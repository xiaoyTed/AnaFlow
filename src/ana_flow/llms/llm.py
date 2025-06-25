# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from pathlib import Path
from typing import Any, Dict

from langchain_openai import ChatOpenAI
from langchain_ollama.llms import OllamaLLM
from langchain_deepseek import ChatDeepSeek
from typing import get_args

from ana_flow.config import load_yaml_config
from ana_flow.config.agents import LLMType

# Cache for LLM instances
_llm_cache: dict[LLMType, ChatOpenAI] = {}

def _get_config_file_path() -> str:
    """Get the path to the configuration file."""
    return str((Path(__file__).parent.parent.parent / "conf.yaml").resolve())


def _get_llm_type_config_keys() -> dict[str, str]:
    """Get mapping of LLM types to their configuration keys."""
    return {
        "reasoning": "REASONING_MODEL",
        "basic": "BASIC_MODEL",
        "vision": "VISION_MODEL",
    }


def _get_env_llm_conf(llm_type: str) -> Dict[str, Any]:
    """
    Get LLM configuration from environment variables.
    Environment variables should follow the format: {LLM_TYPE}__{KEY}
    e.g., BASIC_MODEL__api_key, BASIC_MODEL__base_url
    """
    prefix = f"{llm_type.upper()}_MODEL__"
    conf = {}
    for key, value in os.environ.items():
        if key.startswith(prefix):
            conf_key = key[len(prefix) :].lower()
            conf[conf_key] = value
    return conf


def _create_llm_use_conf(llm_type: LLMType, conf: Dict[str, Any]) -> ChatOpenAI:
    llm_type_map = {
        "reasoning": conf.get("REASONING_MODEL"),
        "basic": conf.get("BASIC_MODEL"),
        "vision": conf.get("VISION_MODEL"),
    }
    llm_conf = llm_type_map.get(llm_type)
    if not llm_conf:
        raise ValueError(f"Unknown LLM type: {llm_type}")
    if not isinstance(llm_conf, dict):
        raise ValueError(f"Invalid LLM Conf: {llm_type}")

    llm_provider = conf.get("MODEL_PROVIDER")
    
    if llm_provider["provider"] == "ollama":
        return OllamaLLM(**llm_conf)
    elif llm_provider["provider"] == "openai":
        return ChatOpenAI(**llm_conf)


def get_llm_by_type(
    llm_type: LLMType,
) -> ChatOpenAI:
    """
    Get LLM instance by type. Returns cached instance if available.
    """
    if llm_type in _llm_cache:
        return _llm_cache[llm_type]

    conf = load_yaml_config(
        str((Path(__file__).parent.parent.parent.parent / "conf.yaml").resolve())
    )
    llm = _create_llm_use_conf(llm_type, conf)
    _llm_cache[llm_type] = llm
    return llm


# In the future, we will use reasoning_llm and vl_llm for different purposes
# reasoning_llm = get_llm_by_type("reasoning")
# vl_llm = get_llm_by_type("vision")

def get_configured_llm_models() -> dict[str, list[str]]:
    """
    Get all configured LLM models grouped by type.

    Returns:
        Dictionary mapping LLM type to list of configured model names.
    """
    try:
        conf = load_yaml_config(_get_config_file_path())
        llm_type_config_keys = _get_llm_type_config_keys()

        configured_models: dict[str, list[str]] = {}

        for llm_type in get_args(LLMType):
            # Get configuration from YAML file
            config_key = llm_type_config_keys.get(llm_type, "")
            yaml_conf = conf.get(config_key, {}) if config_key else {}

            # Get configuration from environment variables
            env_conf = _get_env_llm_conf(llm_type)

            # Merge configurations, with environment variables taking precedence
            merged_conf = {**yaml_conf, **env_conf}

            # Check if model is configured
            model_name = merged_conf.get("model")
            if model_name:
                configured_models.setdefault(llm_type, []).append(model_name)

        return configured_models

    except Exception as e:
        # Log error and return empty dict to avoid breaking the application
        print(f"Warning: Failed to load LLM configuration: {e}")
        return {}



if __name__ == "__main__":
    # Initialize LLMs for different purposes - now these will be cached
    basic_llm = get_llm_by_type("basic")
    print(basic_llm.invoke("Hello"))
