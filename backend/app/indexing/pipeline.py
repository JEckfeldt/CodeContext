from app.indexing.chunking import (
    DEFAULT_CHUNK_MAX_CHARS,
    ChunkDraft,
    chunk_file_content,
    chunk_parsed_blocks,
)
from app.parsers import get_parser


def build_file_chunks(
    content: str,
    language: str | None,
    *,
    max_chars: int | None = None,
) -> list[ChunkDraft]:
    limit = max_chars if max_chars is not None else DEFAULT_CHUNK_MAX_CHARS
    parser = get_parser(language)
    if parser is not None:
        blocks = parser.parse(content)
        if blocks:
            return chunk_parsed_blocks(blocks, language, max_chars=limit)

    return chunk_file_content(content, language, max_chars=limit)
