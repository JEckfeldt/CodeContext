from typing import Literal, Protocol, TypedDict


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
