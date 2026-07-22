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
    limits: RagContextLimits = DEFAULT_RAG_CONTEXT_LIMITS,
) -> str:
    """Format a single numbered chunk block."""
    snippet = truncate_snippet(
        chunk.content,
        max_lines=limits.max_chunk_lines,
        max_chars=limits.max_chunk_chars,
    )
    header = format_chunk_header(index, chunk)
    return f"{header}\n\n{snippet}"


def format_retrieved_chunks(
    chunks: list[ChunkSearchResult],
    limits: RagContextLimits = DEFAULT_RAG_CONTEXT_LIMITS,
) -> str:
    """Format retrieval hits into numbered context blocks with truncation."""
    if not chunks:
        return EMPTY_RETRIEVAL_CONTEXT

    selected = chunks[: limits.max_chunks]
    blocks: list[str] = []
    total_chars = 0

    for index, chunk in enumerate(selected, start=1):
        block = format_chunk_block(index, chunk, limits)
        separator_len = 2 if blocks else 0
        projected = total_chars + separator_len + len(block)
        if blocks and projected > limits.max_total_context_chars:
            break
        if not blocks and len(block) > limits.max_total_context_chars:
            block = block[: limits.max_total_context_chars].rstrip()
            if not block.endswith("…"):
                block = f"{block}\n…"
        blocks.append(block)
        total_chars += separator_len + len(block)

    return "\n\n".join(blocks)
