"""Result types for semantic retrieval."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ChunkSearchResult:
    """A code chunk matched by vector similarity search."""

    file_path: str
    content: str
    start_line: int
    end_line: int
    symbol_name: str | None
    similarity: float
