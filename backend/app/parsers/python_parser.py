import ast

from app.parsers.base import ParsedBlock


def _slice_lines(lines: list[str], start_line: int, end_line: int) -> str:
    if start_line < 1 or end_line < start_line:
        return ""
    return "".join(lines[start_line - 1 : end_line])


def _definition_end_line(node: ast.AST, line_count: int) -> int:
    end_line = getattr(node, "end_lineno", None)
    if isinstance(end_line, int):
        return min(end_line, line_count)
    return min(getattr(node, "lineno", 1), line_count)


def parse_python(content: str) -> list[ParsedBlock]:
    if not content.strip():
        return []

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return []

    lines = content.splitlines(keepends=True)
    if not lines and content:
        lines = [content]
    line_count = len(lines)

    blocks: list[ParsedBlock] = []

    def add_block(
        start_line: int,
        end_line: int,
        chunk_kind: str,
        symbol_name: str | None,
    ) -> None:
        end_line = min(max(end_line, start_line), line_count)
        text = _slice_lines(lines, start_line, end_line)
        if not text.strip():
            return
        blocks.append(
            ParsedBlock(
                start_line=start_line,
                end_line=end_line,
                content=text,
                chunk_kind=chunk_kind,
                symbol_name=symbol_name,
            )
        )

    first_def_line: int | None = None
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if first_def_line is None:
                first_def_line = node.lineno
            break

    if first_def_line and first_def_line > 1:
        add_block(1, first_def_line - 1, "module", None)

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end_line = _definition_end_line(node, line_count)
            add_block(node.lineno, end_line, "function", node.name)
        elif isinstance(node, ast.ClassDef):
            class_end = _definition_end_line(node, line_count)
            add_block(node.lineno, class_end, "class", node.name)
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    method_end = _definition_end_line(item, line_count)
                    add_block(
                        item.lineno,
                        method_end,
                        "method",
                        f"{node.name}.{item.name}",
                    )

    if not blocks and content.strip():
        add_block(1, line_count, "module", None)

    return blocks
