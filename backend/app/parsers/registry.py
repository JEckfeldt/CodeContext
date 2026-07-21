from collections.abc import Callable

from app.parsers.base import Parser
from app.parsers.markdown_parser import parse_markdown
from app.parsers.python_parser import parse_python


class _CallableParser:
    def __init__(self, parse_fn: Callable[[str], list]) -> None:
        self._parse_fn = parse_fn

    def parse(self, content: str):
        return self._parse_fn(content)


_REGISTRY: dict[str, Parser] = {
    "python": _CallableParser(parse_python),
    "markdown": _CallableParser(parse_markdown),
}


def get_parser(language: str | None) -> Parser | None:
    if not language:
        return None
    return _REGISTRY.get(language)
