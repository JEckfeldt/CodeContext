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
    select_rag_context_chunks,
    snippet_preview_for_chunk,
    truncate_snippet,
)
from app.prompts.agent_system import build_agent_system_prompt
from app.prompts.agent_task_templates import (
    TASK_TEMPLATES,
    TaskTemplate,
    UnknownTaskTemplateError,
    get_task_template,
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
    "TASK_TEMPLATES",
    "RagContextLimits",
    "TaskTemplate",
    "UnknownTaskTemplateError",
    "build_agent_system_prompt",
    "build_rag_messages",
    "get_task_template",
    "build_user_content",
    "format_chunk_block",
    "format_retrieved_chunks",
    "select_rag_context_chunks",
    "snippet_preview_for_chunk",
    "truncate_snippet",
]
