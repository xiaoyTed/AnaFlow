# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import json
import logging
import os
from typing import Annotated, Literal
import time
import pandas as pd

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langgraph.types import Command, interrupt
from langchain_mcp_adapters.client import MultiServerMCPClient

from langgraph.prebuilt import create_react_agent
from ana_flow.tools.search import LoggedTavilySearch
from ana_flow.tools import (
    crawl_tool,
    get_web_search_tool,
    python_repl_tool,
    csv_loader_tool,
)

from ana_flow.config.agents import AGENT_LLM_MAP
from ana_flow.config.configuration import Configuration
from ana_flow.llms.llm import get_llm_by_type
from ana_flow.prompts.planner_model import Plan, StepType
from ana_flow.prompts.loader_model import LoaderOutput
from ana_flow.prompts.template import apply_prompt_template
from ana_flow.utils.json_utils import repair_json_output

from ana_flow.graph.types import State
from ana_flow.config import SELECTED_SEARCH_ENGINE, SearchEngine

from dotenv import load_dotenv
#load env variable
load_dotenv()
PG_USER_NAME = os.getenv("PG_USER_NAME")
PG_PASSWORD = os.getenv("PG_PASSWORD")

logger = logging.getLogger(__name__)


@tool
def handoff_to_planner(
    task_title: Annotated[str, "The title of the market analysis task to be handed off."],
    locale: Annotated[str, "The user's detected language locale (e.g., en-US, zh-CN)."],
):
    """Handoff to planner agent to create market analysis plan."""
    # This tool is not returning anything: we're just using it
    # as a way for LLM to signal that it needs to hand off to planner agent
    return


def background_investigation_node(
    state: State, config: RunnableConfig
) -> Command[Literal["planner"]]:
    logger.info("Market background investigation node is running.")
    configurable = Configuration.from_runnable_config(config)
    query = state["messages"][-1].content
    if SELECTED_SEARCH_ENGINE == SearchEngine.TAVILY:
        searched_content = LoggedTavilySearch(
            max_results=configurable.max_search_results
        ).invoke({"query": query})
        background_investigation_results = None
        if isinstance(searched_content, list):
            background_investigation_results = [
                {"title": elem["title"], "content": elem["content"]}
                for elem in searched_content
            ]
        else:
            logger.error(
                f"Tavily search returned malformed response: {searched_content}"
            )
    else:
        background_investigation_results = get_web_search_tool(
            configurable.max_search_results
        ).invoke(query)
    return Command(
        update={
            "background_investigation_results": json.dumps(
                background_investigation_results, ensure_ascii=False
            )
        },
        goto="planner",
    )


def planner_node(
    state: State, config: RunnableConfig
) -> Command[Literal["human_feedback", "reporter"]]:
    """Planner node that generates the market analysis plan."""
    logger.info("Planner generating market analysis plan")
    configurable = Configuration.from_runnable_config(config)
    plan_iterations = state["plan_iterations"] if state.get("plan_iterations", 0) else 0
    messages = apply_prompt_template("planner", state, configurable)

    if (
        plan_iterations == 0
        and state.get("enable_background_investigation")
        and state.get("background_investigation_results")
    ):
        messages += [
            {
                "role": "user",
                "content": (
                    "Market background investigation results of user query:\n"
                    + state["background_investigation_results"]
                    + "\n"
                ),
            }
        ]

    if AGENT_LLM_MAP["planner"] == "basic":
        llm = get_llm_by_type(AGENT_LLM_MAP["planner"]).with_structured_output(
            Plan,
            method="json_mode",
        )
    else:
        llm = get_llm_by_type(AGENT_LLM_MAP["planner"])

    # if the plan iterations is greater than the max plan iterations, return the reporter node
    if plan_iterations >= configurable.max_plan_iterations:
        return Command(goto="reporter")

    full_response = ""
    if AGENT_LLM_MAP["planner"] == "basic":
        response = llm.invoke(messages)
        full_response = response.model_dump_json(indent=4, exclude_none=True)
    else:
        response = llm.stream(messages)
        #print the response for debugging
        for chunk in response:
            full_response += chunk.content
            print(chunk.content)

    try:
        curr_plan = json.loads(repair_json_output(full_response))
    except json.JSONDecodeError:
        logger.warning("Planner response is not a valid JSON")
        if plan_iterations > 0:
            return Command(goto="reporter")
        else:
            return Command(goto="__end__")
        
    logger.debug(f"Current state messages: {state['messages']}")
    logger.info(f"Planner response: {full_response}")
    
    if curr_plan.get("has_enough_context"):
        logger.info("Planner response has enough market context.")
        new_plan = Plan.model_validate(curr_plan)
        return Command(
            update={
                "messages": [AIMessage(content=json.dumps(curr_plan, indent=4, ensure_ascii=False), name="planner")],
                "current_plan": new_plan,
            },
            goto="reporter",
        )
    return Command(
        update={
            "messages": [AIMessage(content=json.dumps(curr_plan, indent=4, ensure_ascii=False), name="planner")],
            "current_plan": json.dumps(curr_plan, indent=4, ensure_ascii=False),
        },
        goto="human_feedback",
    )


def human_feedback_node(
    state,
) -> Command[Literal["planner", "research_team", "reporter", "__end__"]]:
    current_plan = state.get("current_plan", "")
    
    # Write plan to file for user review
    try:
        with open("plan_review.txt", "w", encoding="utf-8") as f:
            f.write(current_plan)
    except Exception as e:
        logger.error(f"Error writing plan to file: {e}")
        return Command(goto="research_team")

    logger.info("Plan written to plan_review.txt for review")
    
    # Check if file was modified
    if os.path.exists("plan_review.txt"):
        # User edited the file
        with open("plan_review.txt", "r") as f:
            feedback = f.read()
        os.remove("plan_review.txt")

    logger.info("Plan accepted by user")

    # Update current plan based on user feedback
    if feedback :
        current_plan = feedback
    plan_iterations = state["plan_iterations"] if state.get("plan_iterations", 0) else 0
    goto = "research_team"
    try:
        current_plan = repair_json_output(current_plan)
        # increment the plan iterations
        plan_iterations += 1
        # parse the plan
        new_plan = json.loads(current_plan)
        if new_plan["has_enough_context"]:
            goto = "reporter"
    except json.JSONDecodeError:
        logger.warning("Planner response is not a valid JSON")
        return Command(goto="__end__")

    return Command(
        update={
            "current_plan": Plan.model_validate(new_plan),
            "plan_iterations": plan_iterations,
            "locale": new_plan["locale"],
        },
        goto=goto,
    )


def coordinator_node(
    state: State,
) -> Command[Literal["planner", "background_investigator", "__end__"]]:
    """Coordinator node that communicates with customers about market analysis."""
    logger.info("Market analysis coordinator talking.")
    messages = apply_prompt_template("coordinator", state)
    response = (
        get_llm_by_type(AGENT_LLM_MAP["coordinator"])
        .bind_tools([handoff_to_planner])
        .invoke(messages)
    )
    logger.debug(f"Current state messages: {state['messages']}")

    goto = "__end__"
    locale = state.get("locale", "en-US")  # Default locale if not specified

    if len(response.tool_calls) > 0:
        goto = "planner"
        # if state.get("enable_background_investigation"):
        #     # if the search_before_planning is True, add the web search tool to the planner agent
        #     goto = "background_investigator"
        try:
            for tool_call in response.tool_calls:
                if tool_call.get("name", "") != "handoff_to_planner":
                    continue
                if tool_locale := tool_call.get("args", {}).get("locale"):
                    locale = tool_locale
                    break
        except Exception as e:
            logger.error(f"Error processing tool calls: {e}")
    else:
        logger.warning(
            "Coordinator response contains no tool calls. Terminating workflow execution."
        )
        logger.debug(f"Coordinator response: {response}")

    return Command(
        update={
            "messages": [
                AIMessage(content=response.content, name="coordinator"),
            ],
            "locale": locale,
        },
        goto=goto,
    )


def reporter_node(state: State):
    """Reporter node that write a final report."""
    logger.info("Reporter write final report")
    current_plan = state.get("current_plan")
    input_ = {
        "messages": [
            HumanMessage(
                f"# Research Requirements\n\n## Task\n\n{current_plan.title}\n\n## Description\n\n{current_plan.thought}"
            )
        ],
        "locale": state.get("locale", "en-US"),
    }
    invoke_messages = apply_prompt_template("reporter", input_)
    observations = state.get("observations", [])

    # Add a reminder about the new report format, citation style, and table usage
    invoke_messages.append(
        HumanMessage(
            content="IMPORTANT: Structure your report according to the format in the prompt. Remember to include:\n\n1. Title - A concise title for the market analysis report\n2. Key Market Insights - 4-6 bulleted points of the most important findings\n3. Market Overview - Brief introduction and context (1-2 paragraphs)\n4. Detailed Market Analysis - Organized into logical sections with clear headings\n5. Market Survey Note (optional) - For more comprehensive reports\n\nWhen presenting market data:\n- Include relevant market visualizations from previous steps\n- Present facts and sales data accurately and impartially\n- Organize information logically with clear section headings\n- Highlight key market trends and sales insights\n- Use clear and concise language\n- Rely strictly on provided market data\n- Never fabricate or assume market information\n- Clearly distinguish between market facts and analysis\n\nPRIORITIZE USING MARKDOWN TABLES for market data presentation and comparison. Structure tables with clear headers and aligned columns. Example table format:\n\n| Market Metric | Value | YoY Change | Notes |\n|--------------|-------|------------|-------|\n| Metric 1 | Value 1 | Change 1 | Notes 1 |\n| Metric 2 | Value 2 | Change 2 | Notes 2 |",
            name="system",
        )
    )

    for observation in observations:
        invoke_messages.append(
            HumanMessage(
                content=f"Below are some observations for the research task:\n\n{observation}",
                name="observation",
            )
        )
    logger.debug(f"Current invoke messages: {invoke_messages}")
    response = get_llm_by_type(AGENT_LLM_MAP["reporter"]).invoke(invoke_messages)
    response_content = response.content
    logger.info(f"reporter response: {response_content}")

    return {"final_report": response_content}


def research_team_node(
    state: State,
) -> Command[Literal["planner", "researcher", "coder", "loader"]]:
    """Research team node that coordinates market analysis tasks."""
    logger.info("Market analysis research team coordinating tasks")
    current_plan = state.get("current_plan", "")
    if not current_plan:
        return Command(goto="planner")
    if all(step.execution_res for step in current_plan.steps):
        return Command(goto="planner")
    for step in current_plan.steps:
        if not step.execution_res:
            break
    if step.step_type and step.step_type == StepType.RESEARCH:
        return Command(goto="researcher")
    if step.step_type and step.step_type == StepType.LOADING:
        return Command(goto="loader")
    if step.step_type and step.step_type == StepType.PROCESSING:
        return Command(goto="coder")
    if step.step_type and step.step_type == StepType.PREDICTION:
        return Command(goto="conclusion")
    return Command(goto="planner")


def human_edit_node(
    state: State, config: RunnableConfig
) -> Command[Literal["research_team"]]:
    """Human edit node that simulates human review/edit before research step."""
    logger.info("Human edit node: waiting for human input before passing to researcher node.")

    try:
        # Save state content to json file
        with open("state.txt", "w") as f:
            observations = state.get("observations", [])
            for observation in observations:
                f.write(observation)
                f.write("\n\n")
        logger.info("State written to state.txt for review")
    except:
        logger.error("Error writing state to file")
        return Command(goto="research_team")

    with open("state.txt", "r") as f:
        feedback = f.read()
    os.remove("state.txt")
    
    # Update state with the edited observation
    if feedback:
        # Add the edited feedback as a new observation
        updated_observations = [feedback]
    else:
        updated_observations = observations
    
    return Command(
        update={"observations": updated_observations}, 
        goto="research_team"
    )


async def researcher_node(
    state: State, config: RunnableConfig
) -> Command[Literal["research_team"]]:
    """Researcher node that do research"""
    logger.info("Researcher node is researching.")

    agent_type = "researcher"

    current_plan = state.get("current_plan")
    observations = state.get("observations", [])
    language = state.get("locale", "zh-CN")

    configurable = {"servers": {
                        "tavily-mcp": {
                            "transport": "stdio",
                            "command": "npx",
                            "args": ["-y", "tavily-mcp@0.1.3"],
                            "env": {
                                "TAVILY_API_KEY": os.getenv("TAVILY_API_KEY"),
                            },
                            "enabled_tools": ["tavily_search_results_json"],
                            "add_to_agents": ["researcher"],
                        }
                    }
                    }
    loaded_tools = []
    mcp_servers = {}
    for server_name, server_config in configurable["servers"].items():
        if (
            server_config["enabled_tools"]
            and agent_type in server_config["add_to_agents"]
        ):
            mcp_servers[server_name] = {
                k: v
                for k, v in server_config.items()
                if k in ("transport", "command", "args", "url", "env")
            }
        # Create and execute agent with MCP tools if available
    if mcp_servers:
        client = MultiServerMCPClient(mcp_servers)
        try:
            mcp_tools = await client.get_tools()
            for tool in mcp_tools:
                loaded_tools.append(tool)
        finally:
            # Assuming MultiServerMCPClient might have an aclose method for cleanup,
            # similar to other Langchain clients. If not, this can be removed.
            # Based on common patterns, it's good practice to close clients.
            # If client.aclose() doesn't exist or is not needed, this block can be simplified/removed.
            if hasattr(client, "aclose"):
                await client.aclose()
            elif hasattr(client, "close") and callable(client.close): # type: ignore
                client.close() # type: ignore

        #config llm output with structured output
    llm = get_llm_by_type(AGENT_LLM_MAP[agent_type])

    prompt = lambda state: apply_prompt_template(agent_type, state)

    agent = create_react_agent(
        name=agent_type, 
        model=llm, 
        tools=loaded_tools, 
        prompt=prompt)

    model_input = set_model_input(current_plan, agent_type, language)

    response_content = await _execute_agent_step(model_input, agent, agent_type)

    current_plan = update_current_plan(current_plan, response_content, agent_type)

    return Command(
        update={
            "observations": observations + [response_content],
        },
        goto="research_team",
    )


async def coder_node(
    state: State, config: RunnableConfig
) -> Command[Literal["research_team"]]:
    """Coder node that do code analysis."""
    logger.info("Coder node is coding.")
    current_plan = state.get("current_plan")
    observations = state.get("observations", [])
    language = state.get("locale", "zh-CN")
    agent_type = "coder"

    loaded_tools = [python_repl_tool]

    llm = get_llm_by_type(AGENT_LLM_MAP[agent_type])
    prompt = lambda state: apply_prompt_template(agent_type, state)

    agent = create_react_agent(
        name=agent_type, 
        model=llm, 
        tools=loaded_tools, 
        prompt=prompt)

    model_input = set_model_input(current_plan, agent_type, language)
    response_content = await _execute_agent_step(model_input, agent, agent_type)

    current_plan = update_current_plan(current_plan, response_content, agent_type)

    return Command(
        update={
            "observations": observations + [response_content],
        },
        goto="research_team",
    )


async def loader_node(
    state: State, config: RunnableConfig
) -> Command[Literal["init_forcast_node"]]:
    """Loader node that handles loading and processing local data files."""
    logger.info("Loader node is loading and processing local data files.")

    current_plan = state.get("current_plan")
    language = state.get("locale", "zh-CN")
    agent_type = "loader"

    pg_database_url = f"postgresql://{PG_USER_NAME}:{PG_PASSWORD}@10.36.21.200:5432/dqdb?sslmode=disable"
    mcp_servers = {
        "postgres-mcp": {
            "transport": "stdio",
            "command": "uv",
            "args": ["tool", "run", "postgres-mcp", "--access-mode=unrestricted"],
            "env": {
                "DATABASE_URI": pg_database_url
            }
        }
    }
    client = MultiServerMCPClient(mcp_servers)
    try:
        mcp_tools = await client.get_tools()
    finally:
        if hasattr(client, "aclose"):
            await client.aclose()
        elif hasattr(client, "close") and callable(client.close): # type: ignore
            client.close() # type: ignore

    loaded_tools = []
    for tool in mcp_tools:
        loaded_tools.append(tool)

    #config llm output with structured output
    llm = get_llm_by_type(AGENT_LLM_MAP[agent_type])

    prompt = lambda state: apply_prompt_template(agent_type, state)

    agent = create_react_agent(
            name=agent_type, 
            model=llm, 
            tools=loaded_tools, 
            prompt=prompt)

    agent_input = set_model_input(current_plan, agent_type, language)
    response_content= await _execute_agent_step(agent_input, agent, agent_type)

    response_content = repair_json_output(response_content)
    loader_output = json.loads(response_content)

    #create a pandas dataframe from the loader_output
    df = pd.DataFrame(loader_output["sale_data"])
    df.columns = ["period", "quantity"]
    #convert the period to datetime
    df['period'] = pd.to_datetime(df['period'], format='%Y%m')

    # Set date as index
    df = df.set_index('period')

    save_fold = "src/ana_flow/temp_data"
    df.to_csv(os.path.join(save_fold, "sales_data.csv"))

    return Command(
        goto="init_forcast_node",
    )

async def init_forcast_node(state: State) -> Command[Literal["research_team"]]:
    """to do the first step forcest use arima or vector arima model to forecast the sales data"""
    logger.info("Init forcast node is forecasting the sales data as the first step.")
    observations = state.get("observations", [])
    current_plan = state.get("current_plan")
    
    agent_type = "init_forcast"
    
    mcp_servers = {
        "market-forecaster": {
            "transport": "stdio",
            "command": "uv",
            "args": ["tool", "run", "market-forecaster"],
        }
    }

    client = MultiServerMCPClient(mcp_servers)
    try:
        mcp_tools = await client.get_tools()
    finally:
        if hasattr(client, "aclose"):
            await client.aclose()
        elif hasattr(client, "close") and callable(client.close): # type: ignore
            client.close() # type: ignore

    loaded_tools = []
    for tool in mcp_tools:
        loaded_tools.append(tool)

    llm = get_llm_by_type(AGENT_LLM_MAP[agent_type])

    prompt = lambda state: apply_prompt_template(agent_type, state)

    agent = create_react_agent(
        name=agent_type, 
        model=llm, 
        tools=loaded_tools, 
        prompt=prompt)

    title = "use arima model to forecast the sales data"
    description = "use Time Series Analysis Tool, use arima model to forecast the sales data, and please load csv data from src/ana_flow/temp_data/sales_data.csv"
    language = "zh-CN"
    agent_input = {
        "messages": [
            HumanMessage(
                content=f"# Current Task\n\n## Title\n\n{title}\n\n## Description\n\n{description}\n\n## Locale\n\n{language}"
            )

        ]
    }

    response_content = await _execute_agent_step(agent_input, agent, agent_type)

    current_plan = update_current_plan(current_plan, response_content, agent_type)

    return Command(
        update={
            "messages": [
                HumanMessage(content=response_content, name="init_forcast"),
            ],
            "observations": observations + [response_content],
        },
        goto="research_team",
    )

def conclusion_node(state: State) -> Command[Literal["research_team"]]:
    """Conclusion node that makes final predictions based on model results and adjusts them according to text information."""
    logger.info("Conclusion node making final predictions")
    current_plan = state.get("current_plan")
    observations = state.get("observations", [])
    language = state.get("locale", "zh-CN")

    # Prepare input for the conclusion node
    input_ = {
        "messages": [
            HumanMessage(
                f"# Research Requirements\n\n## Task\n\n{current_plan.title}\n\n## Description\n\n{current_plan.thought}"
            )
        ],
        "locale": language,
    }
    invoke_messages = apply_prompt_template("conclusion", input_)
    
    # Add all observations as context for the conclusion
    for observation in observations:
        invoke_messages.append(
            HumanMessage(
                content=f"Below are some observations for the research task:\n\n{observation}",
                name="observation",
            )
        )
    
    # Add specific instruction for conclusion node
    invoke_messages.append(
        HumanMessage(
            content="IMPORTANT: You are the final conclusion node. Your task is to:\n\n1. Review all the prediction model results from previous steps\n2. Analyze all the text information and market insights gathered\n3. Make final sales predictions by adjusting the model predictions based on qualitative factors\n4. Provide a comprehensive conclusion that combines quantitative model outputs with qualitative market analysis\n5. Include confidence levels and reasoning for your final predictions\n6. Focus on actionable insights and clear recommendations\n\nDo NOT perform any web research or code execution. Base your conclusions ONLY on the provided information.",
            name="system",
        )
    )
    
    logger.debug(f"Current invoke messages: {invoke_messages}")
    response = get_llm_by_type(AGENT_LLM_MAP["conclusion"]).invoke(invoke_messages)
    response_content = response.content
    logger.info(f"conclusion response: {response_content}")

    #updata execution_res
    current_plan = update_current_plan(current_plan, response_content, "conclusion")

    return Command(
        update={
            "messages": [
                HumanMessage(content=response_content, name="conclusion"),
            ],
            "observations": observations + [response_content],
        },
        goto="research_team",
    )

async def _execute_agent_step(agent_input, agent, agent_type: str) -> str:
    # Invoke the agent
    default_recursion_limit = 25
    try:
        env_value_str = os.getenv("AGENT_RECURSION_LIMIT", str(default_recursion_limit))
        parsed_limit = int(env_value_str)

        if parsed_limit > 0:
            recursion_limit = parsed_limit
            logger.info(f"Recursion limit set to: {recursion_limit}")
        else:
            logger.warning(
                f"AGENT_RECURSION_LIMIT value '{env_value_str}' (parsed as {parsed_limit}) is not positive. "
                f"Using default value {default_recursion_limit}."
            )
            recursion_limit = default_recursion_limit
    except ValueError:
        raw_env_value = os.getenv("AGENT_RECURSION_LIMIT")
        logger.warning(
            f"Invalid AGENT_RECURSION_LIMIT value: '{raw_env_value}'. "
            f"Using default value {default_recursion_limit}."
        )
        recursion_limit = default_recursion_limit

    try:
        result = await agent.ainvoke(
            input=agent_input, config={"recursion_limit": recursion_limit}
        )
    except Exception as e:
        logger.error(f"Error invoking agent: {e}")
        # return Command(goto="research_team")

    # Process the result
    response_content = result["messages"][-1].content
    logger.debug(f"{agent_type.capitalize()} full response: {response_content}")

    return response_content

def set_model_input(current_plan: Plan, agent_name: str, language: str) -> dict:
    current_step = None
    completed_steps = []
    for step in current_plan.steps:
        if not step.execution_res:
            current_step = step
            break
        else:
            completed_steps.append(step)

    if not current_step:
        logger.warning("No unexecuted step found")
        return Command(goto="research_team")

    logger.info(f"Executing step: {current_step.title}")

    # Format completed steps information
    completed_steps_info = ""
    if completed_steps:
        completed_steps_info = "# Existing Research Findings\n\n"
        for i, step in enumerate(completed_steps):
            completed_steps_info += f"## Existing Finding {i+1}: {step.title}\n\n"
            completed_steps_info += f"<finding>\n{step.execution_res}\n</finding>\n\n"

    # Prepare the input for the agent with completed steps info
    agent_input = {
        "messages": [
            HumanMessage(
                content=f"{completed_steps_info}# Current Task\n\n## Title\n\n{current_step.title}\n\n## Description\n\n{current_step.description}\n\n## Locale\n\n{language}"
            )

        ]
    }

    # Add citation reminder for researcher agent
    if agent_name == "researcher":
        agent_input["messages"].append(
            HumanMessage(
                content="IMPORTANT: DO NOT include inline citations in the text. Instead, track all sources and include a References section at the end using link reference format. Include an empty line between each citation for better readability. Use this format for each reference:\n- [Source Title](URL)\n\n- [Another Source](URL)",
                name="system",
            )
        )
    return agent_input

def update_current_plan(current_plan: Plan, response_content: str, agent_type: str) -> Plan:
    for step in current_plan.steps:
        if not step.execution_res:
            current_step_index = current_plan.steps.index(step)
            current_plan.steps[current_step_index].execution_res = response_content
            break
    logger.info(f"Step '{current_plan.steps[current_step_index].title}' execution completed by {agent_type}")
    return current_plan