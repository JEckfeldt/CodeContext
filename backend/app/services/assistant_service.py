"""Orchestrate retrieval, RAG prompts, and LLM completion for project Q&A."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.llm.base import ChatMessage, ChatProvider
from app.llm.exceptions import LLMUnavailableError
from app.llm.provider import get_chat_provider
from app.prompts.rag_context import (
    DEFAULT_RAG_CONTEXT_LIMITS,
    RagContextLimits,
    select_rag_context_chunks,
    snippet_preview_for_chunk,
)
from app.prompts.rag_messages import build_rag_messages
from app.retrieval.retrieval_service import DEFAULT_TOP_K, search_similar_chunks
from app.retrieval.types import ChunkSearchResult


@dataclass(frozen=True)
class SourceCitation:
    """Structured source reference aligned with prompt block indices."""

    index: int
    file_path: str
    start_line: int
    end_line: int
    symbol_name: str | None
    snippet: str
    similarity: float


@dataclass(frozen=True)
class AssistantResult:
    """Result of a single grounded assistant turn."""

    project_id: uuid.UUID
    question: str
    answer: str
    citations: list[SourceCitation]
    retrieved_chunks: list[ChunkSearchResult]


def _build_citations(
    context_chunks: list[ChunkSearchResult],
    limits: RagContextLimits | None = None,
) -> list[SourceCitation]:
    """Build citations for chunks actually included in the LLM prompt."""
    effective_limits = limits or DEFAULT_RAG_CONTEXT_LIMITS
    return [
        SourceCitation(
            index=index,
            file_path=chunk.file_path,
            start_line=chunk.start_line,
            end_line=chunk.end_line,
            symbol_name=chunk.symbol_name,
            snippet=snippet_preview_for_chunk(chunk, effective_limits),
            similarity=chunk.similarity,
        )
        for index, chunk in enumerate(context_chunks, start=1)
    ]


async def ask_question(
    session: AsyncSession,
    project_id: uuid.UUID,
    question: str,
    *,
    history: list[ChatMessage] | None = None,
    limit: int | None = None,
    provider: ChatProvider | None = None,
) -> AssistantResult:
    """Answer a question using retrieval-augmented generation.

    Args:
        session: Async database session.
        project_id: Project to search and answer for.
        question: Natural-language question.
        history: Reserved for multi-turn conversations (not used yet).
        limit: Maximum chunks to retrieve (defaults to retrieval ``DEFAULT_TOP_K``).
        provider: Optional chat provider override (tests).

    Raises:
        ProjectNotFoundError: Propagated from retrieval when the project is missing.
        QueryEmbeddingError: Propagated when the query cannot be embedded.
        SemanticSearchUnavailableError: Propagated when vector search is unavailable.
        LLMUnavailableError: When no chat provider is configured.
        LLMCompletionError: Propagated when the LLM request fails.
    """
    trimmed_question = question.strip()
    effective_limit = limit if limit is not None else DEFAULT_TOP_K

    retrieved_chunks = await search_similar_chunks(
        session,
        project_id,
        trimmed_question,
        limit=effective_limit,
    )

    context_chunks = select_rag_context_chunks(retrieved_chunks)
    messages = build_rag_messages(trimmed_question, context_chunks)

    if history:
        # Multi-turn support will prepend/append turns without changing retrieval.
        pass

    chat_provider = provider if provider is not None else get_chat_provider()
    if chat_provider is None:
        raise LLMUnavailableError(
            "LLM provider is not configured. Set LLM_ENABLED=true and OPENAI_API_KEY."
        )

    answer = await chat_provider.complete(messages)

    return AssistantResult(
        project_id=project_id,
        question=trimmed_question,
        answer=answer,
        citations=_build_citations(context_chunks),
        retrieved_chunks=retrieved_chunks,
    )
