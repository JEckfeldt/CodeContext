"""Format retrieved chunks into numbered context blocks for RAG prompts."""

from __future__ import annotations

from dataclasses import dataclass

from app.retrieval.types import ChunkSearchResult

DEFAULT_MAX_CHUNKS = 10
DEFAULT_MAX_CHUNK_LINES = 14
DEFAULT_MAX_CHUNK_CHARS = 1200
DEFAULT_MAX_TOTAL_CONTEXT_CHARS = 12_000

EMPTY_RETRIEVAL_CONTEXT = (
    "(No code snippets were retrieved for this question. "
    "Say you cannot answer from repository context.)"
)


@dataclass(frozen=True)
class RagContextLimits:
    """Bounds for prompt context size (override in tests or from settings later)."""

    max_chunks: int = DEFAULT_MAX_CHUNKS
    max_chunk_lines: int = DEFAULT_MAX_CHUNK_LINES
    max_chunk_chars: int = DEFAULT_MAX_CHUNK_CHARS
    max_total_context_chars: int = DEFAULT_MAX_TOTAL_CONTEXT_CHARS


DEFAULT_RAG_CONTEXT_LIMITS = RagContextLimits()


def truncate_snippet(
    content: str,
    *,
    max_lines: int,
    max_chars: int,
) -> str:
    """Truncate code text by line count and character count."""
    normalized = content.replace("\r\n", "\n")
    lines = normalized.split("\n")
    snippet = "\n".join(lines[:max_lines])

    if len(lines) > max_lines:
        snippet = f"{snippet}\n…"

    if len(snippet) > max_chars:
        snippet = f"{snippet[:max_chars].rstrip()}\n…"

    return snippet


def snippet_preview_for_chunk(
    chunk: ChunkSearchResult,
    limits: RagContextLimits | None = None,
) -> str:
    """Snippet text used in prompt blocks and API citations."""
    effective_limits = limits or DEFAULT_RAG_CONTEXT_LIMITS
    return truncate_snippet(
        chunk.content,
        max_lines=effective_limits.max_chunk_lines,
        max_chars=effective_limits.max_chunk_chars,
    )


def format_line_range(start_line: int, end_line: int) -> str:
    if start_line == end_line:
        return f"line {start_line}"
    return f"lines {start_line}–{end_line}"


def format_chunk_header(index: int, chunk: ChunkSearchResult) -> str:
    line_range = format_line_range(chunk.start_line, chunk.end_line)
    header = f"### [{index}] {chunk.file_path} · {line_range}"
    if chunk.symbol_name:
        header = f"{header} · symbol: {chunk.symbol_name}"
    return header


def format_chunk_block(
    index: int,
    chunk: ChunkSearchResult,
    limits: RagContextLimits | None = None,
) -> str:
    """Format a single numbered chunk block."""
    effective_limits = limits or DEFAULT_RAG_CONTEXT_LIMITS
    snippet = snippet_preview_for_chunk(chunk, effective_limits)
    header = format_chunk_header(index, chunk)
    return f"{header}\n\n{snippet}"


def select_rag_context_chunks(
    chunks: list[ChunkSearchResult],
    limits: RagContextLimits | None = None,
) -> list[ChunkSearchResult]:
    """Return chunks that are included in the RAG prompt (same order as [1], [2], …)."""
    effective_limits = limits or DEFAULT_RAG_CONTEXT_LIMITS
    if not chunks:
        return []

    candidates = chunks[: effective_limits.max_chunks]
    included: list[ChunkSearchResult] = []
    total_chars = 0

    for index, chunk in enumerate(candidates, start=1):
        block = format_chunk_block(index, chunk, effective_limits)
        separator_len = 2 if included else 0
        projected = total_chars + separator_len + len(block)
        if included and projected > effective_limits.max_total_context_chars:
            break

        included.append(chunk)

        if len(included) == 1 and len(block) > effective_limits.max_total_context_chars:
            break

        total_chars += separator_len + len(block)

    return included


def format_retrieved_chunks(
    chunks: list[ChunkSearchResult],
    limits: RagContextLimits | None = None,
) -> str:
    """Format retrieval hits into numbered context blocks with truncation."""
    effective_limits = limits or DEFAULT_RAG_CONTEXT_LIMITS
    if not chunks:
        return EMPTY_RETRIEVAL_CONTEXT

    included = select_rag_context_chunks(chunks, effective_limits)
    if not included:
        return EMPTY_RETRIEVAL_CONTEXT

    blocks: list[str] = []
    for index, chunk in enumerate(included, start=1):
        block = format_chunk_block(index, chunk, effective_limits)
        if not blocks and len(block) > effective_limits.max_total_context_chars:
            block = block[: effective_limits.max_total_context_chars].rstrip()
            if not block.endswith("…"):
                block = f"{block}\n…"
        blocks.append(block)

    return "\n\n".join(blocks)
