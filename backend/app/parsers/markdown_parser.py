import re

from app.parsers.base import ParsedBlock

_HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def _heading_level(line: str) -> int | None:
    match = _HEADING_PATTERN.match(line.rstrip("\r\n"))
    if not match:
        return None
    return len(match.group(1))


def _heading_title(line: str) -> str:
    match = _HEADING_PATTERN.match(line.rstrip("\r\n"))
    if not match:
        return line.strip()
    return match.group(2).strip()


def parse_markdown(content: str) -> list[ParsedBlock]:
    if not content:
        return []

    lines = content.splitlines(keepends=True)
    if not lines and content:
        lines = [content]

    heading_lines: list[tuple[int, str]] = []
    for index, line in enumerate(lines, start=1):
        if _heading_level(line) is not None:
            heading_lines.append((index, line))

    if not heading_lines:
        text = "".join(lines)
        if not text.strip():
            return []
        return [
            ParsedBlock(
                start_line=1,
                end_line=len(lines),
                content=text,
                chunk_kind="markdown_section",
                symbol_name=None,
            )
        ]

    blocks: list[ParsedBlock] = []
    first_heading_line = heading_lines[0][0]
    if first_heading_line > 1:
        preamble = "".join(lines[: first_heading_line - 1])
        if preamble.strip():
            blocks.append(
                ParsedBlock(
                    start_line=1,
                    end_line=first_heading_line - 1,
                    content=preamble,
                    chunk_kind="markdown_section",
                    symbol_name=None,
                )
            )

    for heading_index, (start_line, _heading_line) in enumerate(heading_lines):
        end_line = (
            heading_lines[heading_index + 1][0] - 1
            if heading_index + 1 < len(heading_lines)
            else len(lines)
        )
        section_text = "".join(lines[start_line - 1 : end_line])
        if not section_text.strip():
            continue
        blocks.append(
            ParsedBlock(
                start_line=start_line,
                end_line=end_line,
                content=section_text,
                chunk_kind="markdown_section",
                symbol_name=_heading_title(_heading_line),
            )
        )

    return blocks
