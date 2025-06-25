# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from ana_flow.config.tools import SELECTED_RAG_PROVIDER, RAGProvider
from ana_flow.rag.ragflow import RAGFlowProvider
from ana_flow.rag.retriever import Retriever


def build_retriever() -> Retriever | None:
    if SELECTED_RAG_PROVIDER == RAGProvider.RAGFLOW.value:
        return RAGFlowProvider()
    elif SELECTED_RAG_PROVIDER:
        raise ValueError(f"Unsupported RAG provider: {SELECTED_RAG_PROVIDER}")
    return None
