from typing import Any, Literal, Protocol, TypedDict

from app.llm.types import ChatCompletionResult


class ChatMessage(TypedDict):
    """OpenAI-compatible chat message."""

    role: Literal["system", "user", "assistant"]
    content: str


class ChatProvider(Protocol):
    async def complete(
        self,
        messages: list[ChatMessage],
        *,
        max_tokens: int | None = None,
    ) -> str: ...

    async def complete_with_tools(
        self,
        messages: list[ChatMessage],
        tools: list[dict[str, Any]],
        *,
        tool_choice: str | dict[str, Any] = "auto",
        max_tokens: int | None = None,
    ) -> ChatCompletionResult: ...
