"""Structured types for chat completions and tool calling."""

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ToolCall:
    """A single function tool call requested by the assistant."""

    id: str
    name: str
    arguments: str


@dataclass(frozen=True, slots=True)
class ChatCompletionResult:
    """Result of a chat completion that may include text and/or tool calls."""

    content: str | None
    tool_calls: list[ToolCall] = field(default_factory=list)

    @property
    def has_tool_calls(self) -> bool:
        return len(self.tool_calls) > 0
