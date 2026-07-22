import httpx

from app.llm.base import ChatMessage
from app.llm.exceptions import LLMCompletionError


class OpenAIChatProvider:
    def __init__(
        self,
        api_key: str,
        model: str,
        *,
        max_tokens: int = 2048,
        api_base: str = "https://api.openai.com/v1",
        timeout_seconds: float = 120.0,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._max_tokens = max_tokens
        self._api_base = api_base.rstrip("/")
        self._timeout_seconds = timeout_seconds

    async def complete(
        self,
        messages: list[ChatMessage],
        *,
        max_tokens: int | None = None,
    ) -> str:
        if not messages:
            raise LLMCompletionError("Chat completion requires at least one message.")

        effective_max_tokens = max_tokens if max_tokens is not None else self._max_tokens

        async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
            try:
                response = await client.post(
                    f"{self._api_base}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self._model,
                        "messages": messages,
                        "max_tokens": effective_max_tokens,
                    },
                )
                response.raise_for_status()
                payload = response.json()
            except httpx.HTTPStatusError as exc:
                detail = exc.response.text.strip() or str(exc)
                raise LLMCompletionError(
                    f"OpenAI chat completion failed: {detail}"
                ) from exc
            except httpx.HTTPError as exc:
                raise LLMCompletionError(
                    f"OpenAI chat completion request failed: {exc}"
                ) from exc

        try:
            content = payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMCompletionError(
                "OpenAI chat completion returned an unexpected response shape."
            ) from exc

        if content is None:
            raise LLMCompletionError("OpenAI chat completion returned empty content.")

        return str(content).strip()
