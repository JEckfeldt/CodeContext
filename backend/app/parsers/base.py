from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ParsedBlock:
    start_line: int
    end_line: int
    content: str
    chunk_kind: str
    symbol_name: str | None = None


class Parser(Protocol):
    def parse(self, content: str) -> list[ParsedBlock]: ...
