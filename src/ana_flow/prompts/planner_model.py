# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class StepType(str, Enum):
    RESEARCH = "research"
    PROCESSING = "processing"
    LOADING = "loading"
    PREDICTION = "prediction"


class Step(BaseModel):
    need_web_search: bool = Field(
        ..., description="Must be explicitly set for each step"
    )
    title: str
    description: str = Field(..., description="Specify exactly what data to collect")
    step_type: StepType = Field(..., description="Indicates the nature of the step")
    execution_res: Optional[str] = Field(
        default=None, description="The Step execution result"
    )


class Plan(BaseModel):
    locale: str = Field(
        ..., description="e.g. 'en-US' or 'zh-CN', based on the user's language"
    )
    has_enough_context: bool
    thought: str
    title: str
    steps: List[Step] = Field(
        default_factory=list,
        description="Research & Processing steps to get more context",
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "has_enough_context": False,
                    "thought": (
                        "To understand the current market trends in AI, we need to gather comprehensive information."
                    ),
                    "title": "AI Market Research Plan",
                    "steps": [
                        {
                            "need_web_search": False,
                            "title": "Load Local Market Data",
                            "description": (
                                "Load and analyze local CSV files containing market data to understand the available data structure and key metrics."
                            ),
                            "step_type": "loading",
                        },
                        {
                            "need_web_search": True,
                            "title": "Current AI Market Analysis",
                            "description": (
                                "Collect data on market size, growth rates, major players, and investment trends in AI sector."
                            ),
                            "step_type": "research",
                        },
                        {
                            "need_web_search": False,
                            "title": "Data Processing and Analysis",
                            "description": (
                                "Process the collected data to derive key insights about market trends and patterns."
                            ),
                            "step_type": "processing",
                        },
                        {
                            "need_web_search": False,
                            "title": "Conclusion and Summary",
                            "description": (
                                "Synthesize all findings into a comprehensive conclusion with key insights, recommendations, and actionable outcomes."
                            ),
                            "step_type": "conclusion",
                        },
                    ],
                }
            ]
        }
