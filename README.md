# Ana Flow

Ana Flow is an intelligent multi-agent workflow system built with LangChain and LangGraph. It orchestrates specialized AI agents to answer complex questions, perform research, conduct data analysis, and generate forecasts through a collaborative workflow.

## Features

- 🤖 **Multi-Agent Architecture**: Coordinated team of specialized agents (researcher, planner, coder, reporter, etc.)
- 🔍 **Background Investigation**: Automatic web search and information gathering before task execution
- 📊 **Data Analysis & Forecasting**: Built-in tools for data processing, statistical analysis, and time series forecasting
- 🌐 **Web Search Integration**: Tavily search integration for real-time information retrieval
- 💻 **Python Code Execution**: Safe Python REPL for data analysis and computations
- 🌍 **Bilingual Support**: Interactive interface available in both English and Chinese
- 🔌 **Flexible LLM Backends**: Support for OpenAI, DeepSeek, and Ollama providers
- ⚡ **Async Workflow**: Efficient asynchronous execution for improved performance
- 🎨 **Web Interface**: Modern web UI for interactive chat-based interactions

## Architecture

Ana Flow uses a graph-based state machine (LangGraph) where different specialized agents work together:

- **Coordinator**: Routes tasks to appropriate agents
- **Planner**: Creates execution plans for complex tasks
- **Researcher**: Performs web searches and information gathering
- **Coder**: Executes Python code for data analysis
- **Loader**: Loads and processes data from various sources
- **Reporter**: Generates formatted reports and outputs
- **Conclusion**: Provides final reasoning and summaries
- **Background Investigator**: Pre-emptively gathers context before planning

## Installation

### Prerequisites

- Python >= 3.12
- Node.js (for Tavily MCP server)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd ana-flow
```

2. Install dependencies using `uv` (recommended) or `pip`:
```bash
# Using uv
uv sync

# Or using pip
pip install -e .
```

3. Configure your LLM settings in `config.yaml`:
```yaml
BASIC_MODEL:
  base_url: https://api.openai.com/v1
  model: gpt-4
  api_key: your-api-key
  max_tokens: 8192

REASONING_MODEL:
  base_url: https://api.openai.com/v1
  model: gpt-4
  api_key: your-api-key
  max_tokens: 8192

MODEL_PROVIDER:
  provider: "openai"  # or "deepseek" or "ollama"
```

4. Set up environment variables (optional):
```bash
export TAVILY_API_KEY=your-tavily-api-key
```

## Usage

### Interactive Mode

Run Ana Flow in interactive mode with a built-in question selector:

```bash
python -m ana_flow.main --interactive
```

### Command Line Mode

Ask questions directly from the command line:

```bash
python -m ana_flow.main "Your question here"
```

### Command Line Options

```bash
python -m ana_flow.main [query] [options]

Options:
  --interactive              Run in interactive mode
  --max-plan-iterations N    Maximum number of plan iterations (default: 1)
  --max-step-num N          Maximum number of steps in a plan (default: 3)
  --debug                    Enable debug logging
  --no-background-investigation  Disable background investigation
```

### Programmatic Usage

```python
from ana_flow.workflow import run_agent_workflow_async
import asyncio

async def main():
    await run_agent_workflow_async(
        user_input="Forecast sales for product X over the next 6 months",
        debug=False,
        max_plan_iterations=1,
        max_step_num=3,
        enable_background_investigation=True
    )

asyncio.run(main())
```

## Configuration

### LLM Providers

Ana Flow supports three LLM providers:

1. **OpenAI**: Set `provider: "openai"` and configure with OpenAI-compatible API
2. **DeepSeek**: Set `provider: "deepseek"` and use DeepSeek API endpoints
3. **Ollama**: Set `provider: "ollama"` for local Ollama instances

### Environment Variables

You can override configuration using environment variables:

```bash
# Format: {LLM_TYPE}_MODEL__{KEY}
export BASIC_MODEL__api_key=your-key
export BASIC_MODEL__base_url=https://api.example.com
export REASONING_MODEL__api_key=your-key
```

## Project Structure

```
ana-flow/
├── src/
│   └── ana_flow/
│       ├── main.py              # Entry point
│       ├── workflow.py          # Workflow orchestration
│       ├── graph/               # LangGraph state machine
│       ├── config/              # Configuration management
│       ├── llms/                # LLM provider abstractions
│       ├── tools/               # Agent tools (search, code execution, etc.)
│       ├── prompts/             # Prompt templates
│       ├── server/              # Web server endpoints
│       └── rag/                 # Retrieval-Augmented Generation
├── web/                         # Web interface
├── config.yaml                  # Main configuration file
├── pyproject.toml               # Project dependencies
└── README.md
```

## Examples

### Sales Forecasting

```bash
python -m ana_flow.main "Forecast sales of Geely Galaxy E5 in the Chinese market for the next five months from June to November"
```

### Custom Analysis

```bash
python -m ana_flow.main --interactive
# Then select "[Ask my own question]" and enter your query
```

## Development

### Running Tests

```bash
pytest
```

### Debugging

Enable debug logging for detailed execution information:

```bash
python -m ana_flow.main "your question" --debug
```

Debug logs are saved to `ana_flow/logs/agent_workflow.log`.

## Dependencies

Key dependencies include:
- `langchain` & `langgraph`: Core framework
- `langchain-openai`, `langchain-deepseek`, `langchain-ollama`: LLM providers
- `pandas`, `numpy`: Data processing
- `matplotlib`, `seaborn`: Visualization
- `prophet`, `statsmodels`: Time series forecasting
- `fastapi`: Web server
- `inquirerpy`: Interactive CLI

See `pyproject.toml` for the complete list.

## License

MIT License (SPDX-License-Identifier: MIT)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on the project repository.

