"""Prompt templates for RAG and assistant responses (Phase 4)."""

from app.prompts.rag_context import (
    DEFAULT_MAX_CHUNK_CHARS,
    DEFAULT_MAX_CHUNK_LINES,
    DEFAULT_MAX_CHUNKS,
    DEFAULT_MAX_TOTAL_CONTEXT_CHARS,
    DEFAULT_RAG_CONTEXT_LIMITS,
    EMPTY_RETRIEVAL_CONTEXT,
    RagContextLimits,
    format_chunk_block,
    format_retrieved_chunks,
    truncate_snippet,
)
from app.prompts.rag_messages import build_rag_messages, build_user_content
from app.prompts.rag_system import RAG_SYSTEM_PROMPT

__all__ = [
    "DEFAULT_MAX_CHUNK_CHARS",
    "DEFAULT_MAX_CHUNK_LINES",
    "DEFAULT_MAX_CHUNKS",
    "DEFAULT_MAX_TOTAL_CONTEXT_CHARS",
    "DEFAULT_RAG_CONTEXT_LIMITS",
    "EMPTY_RETRIEVAL_CONTEXT",
    "RAG_SYSTEM_PROMPT",
    "RagContextLimits",
    "build_rag_messages",
    "build_user_content",
    "format_chunk_block",
    "format_retrieved_chunks",
    "truncate_snippet",
]
