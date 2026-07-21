from dataclasses import dataclass

from app.parsers.base import ParsedBlock

DEFAULT_CHUNK_MAX_CHARS = 2000
TEXT_BLOCK_KIND = "text_block"


@dataclass(frozen=True)
class ChunkDraft:
    chunk_index: int
    start_line: int
    end_line: int
    content: str
    language: str | None
    chunk_kind: str = TEXT_BLOCK_KIND


def chunk_file_content(
    content: str,
    language: str | None,
    *,
    max_chars: int = DEFAULT_CHUNK_MAX_CHARS,
) -> list[ChunkDraft]:
    if not content:
        return []

    lines = content.splitlines(keepends=True)
    if not lines:
        lines = [content]

    drafts: list[ChunkDraft] = []
    chunk_index = 0
    buffer: list[str] = []
    buffer_len = 0
    start_line = 1

    def emit(end_line: int) -> None:
        nonlocal chunk_index, buffer, buffer_len, start_line
        if not buffer:
            return
        drafts.append(
            ChunkDraft(
                chunk_index=chunk_index,
                start_line=start_line,
                end_line=end_line,
                content="".join(buffer),
                language=language,
            )
        )
        chunk_index += 1
        buffer = []
        buffer_len = 0

    for line_number, line in enumerate(lines, start=1):
        line_len = len(line)

        if line_len > max_chars:
            if buffer:
                emit(line_number - 1)
            for offset in range(0, line_len, max_chars):
                segment = line[offset : offset + max_chars]
                drafts.append(
                    ChunkDraft(
                        chunk_index=chunk_index,
                        start_line=line_number,
                        end_line=line_number,
                        content=segment,
                        language=language,
                    )
                )
                chunk_index += 1
            start_line = line_number + 1
            continue

        if buffer_len + line_len > max_chars and buffer:
            emit(line_number - 1)
            start_line = line_number

        if not buffer:
            start_line = line_number

        buffer.append(line)
        buffer_len += line_len

    if buffer:
        emit(start_line + len(buffer) - 1)

    return drafts


def chunk_parsed_blocks(
    blocks: list[ParsedBlock],
    language: str | None,
    *,
    max_chars: int = DEFAULT_CHUNK_MAX_CHARS,
) -> list[ChunkDraft]:
    drafts: list[ChunkDraft] = []
    chunk_index = 0

    for block in blocks:
        if len(block.content) <= max_chars:
            drafts.append(
                ChunkDraft(
                    chunk_index=chunk_index,
                    start_line=block.start_line,
                    end_line=block.end_line,
                    content=block.content,
                    language=language,
                    chunk_kind=block.chunk_kind,
                )
            )
            chunk_index += 1
            continue

        line_offset = block.start_line - 1
        sub_chunks = chunk_file_content(
            block.content,
            language,
            max_chars=max_chars,
        )
        for sub_index, sub in enumerate(sub_chunks):
            drafts.append(
                ChunkDraft(
                    chunk_index=chunk_index,
                    start_line=sub.start_line + line_offset,
                    end_line=sub.end_line + line_offset,
                    content=sub.content,
                    language=language,
                    chunk_kind=block.chunk_kind
                    if sub_index == 0
                    else TEXT_BLOCK_KIND,
                )
            )
            chunk_index += 1

    return drafts
