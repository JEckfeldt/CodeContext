"""Assemble OpenAI-style chat messages for repository RAG."""

from app.llm.base import ChatMessage
from app.prompts.rag_context import (
    DEFAULT_RAG_CONTEXT_LIMITS,
    RagContextLimits,
    format_retrieved_chunks,
)
from app.prompts.rag_system import RAG_SYSTEM_PROMPT
from app.retrieval.types import ChunkSearchResult

USER_QUESTION_HEADING = "## Question"
USER_CONTEXT_HEADING = "## Retrieved code"


def build_user_content(
    question: str,
    chunks: list[ChunkSearchResult],
    limits: RagContextLimits = DEFAULT_RAG_CONTEXT_LIMITS,
) -> str:
    """Build the user message body (question + retrieved context)."""
    trimmed_question = question.strip()
    context = format_retrieved_chunks(chunks, limits)
    return (
        f"{USER_QUESTION_HEADING}\n\n"
        f"{trimmed_question}\n\n"
        f"{USER_CONTEXT_HEADING}\n\n"
        f"{context}"
    )


def build_rag_messages(
    question: str,
    chunks: list[ChunkSearchResult],
    limits: RagContextLimits = DEFAULT_RAG_CONTEXT_LIMITS,
) -> list[ChatMessage]:
    """Return system + user messages for a single-turn RAG request."""
    return [
        {"role": "system", "content": RAG_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": build_user_content(question, chunks, limits),
        },
    ]
