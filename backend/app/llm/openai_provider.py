from typing import Any

import httpx

from app.llm.base import ChatMessage
from app.llm.exceptions import LLMCompletionError
from app.llm.types import ChatCompletionResult, ToolCall


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

        payload = await self._post_chat_completion(
            messages,
            max_tokens=max_tokens,
        )
        result = self._parse_chat_completion(payload, require_content=True)
        assert result.content is not None
        return result.content

    async def complete_with_tools(
        self,
        messages: list[ChatMessage],
        tools: list[dict[str, Any]],
        *,
        tool_choice: str | dict[str, Any] = "auto",
        max_tokens: int | None = None,
    ) -> ChatCompletionResult:
        if not messages:
            raise LLMCompletionError("Chat completion requires at least one message.")
        if not tools:
            raise LLMCompletionError("Tool completion requires at least one tool definition.")

        payload = await self._post_chat_completion(
            messages,
            max_tokens=max_tokens,
            tools=tools,
            tool_choice=tool_choice,
        )
        return self._parse_chat_completion(payload, require_content=False)

    async def _post_chat_completion(
        self,
        messages: list[ChatMessage],
        *,
        max_tokens: int | None = None,
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str | dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        effective_max_tokens = max_tokens if max_tokens is not None else self._max_tokens

        request_json: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "max_tokens": effective_max_tokens,
        }
        if tools is not None:
            request_json["tools"] = tools
            request_json["tool_choice"] = tool_choice if tool_choice is not None else "auto"

        async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
            try:
                response = await client.post(
                    f"{self._api_base}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json",
                    },
                    json=request_json,
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

        if not isinstance(payload, dict):
            raise LLMCompletionError(
                "OpenAI chat completion returned an unexpected response shape."
            )
        return payload

    def _parse_chat_completion(
        self,
        payload: dict[str, Any],
        *,
        require_content: bool,
    ) -> ChatCompletionResult:
        try:
            message = payload["choices"][0]["message"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMCompletionError(
                "OpenAI chat completion returned an unexpected response shape."
            ) from exc

        if not isinstance(message, dict):
            raise LLMCompletionError(
                "OpenAI chat completion returned an unexpected response shape."
            )

        raw_content = message.get("content")
        content = str(raw_content).strip() if raw_content is not None else None
        if content == "":
            content = None

        tool_calls = self._parse_tool_calls(message.get("tool_calls"))

        if require_content:
            if content is None:
                raise LLMCompletionError("OpenAI chat completion returned empty content.")
            return ChatCompletionResult(content=content, tool_calls=[])

        if content is None and not tool_calls:
            raise LLMCompletionError(
                "OpenAI chat completion returned neither content nor tool calls."
            )

        return ChatCompletionResult(content=content, tool_calls=tool_calls)

    def _parse_tool_calls(self, raw_tool_calls: Any) -> list[ToolCall]:
        if raw_tool_calls is None:
            return []
        if not isinstance(raw_tool_calls, list):
            raise LLMCompletionError(
                "OpenAI chat completion returned an unexpected tool_calls shape."
            )

        parsed: list[ToolCall] = []
        for item in raw_tool_calls:
            if not isinstance(item, dict):
                raise LLMCompletionError(
                    "OpenAI chat completion returned an unexpected tool_calls shape."
                )

            call_id = item.get("id")
            function = item.get("function")
            if not isinstance(call_id, str) or not call_id.strip():
                raise LLMCompletionError(
                    "OpenAI chat completion returned a tool call without an id."
                )
            if not isinstance(function, dict):
                raise LLMCompletionError(
                    "OpenAI chat completion returned a tool call without function data."
                )

            name = function.get("name")
            arguments = function.get("arguments")
            if not isinstance(name, str) or not name.strip():
                raise LLMCompletionError(
                    "OpenAI chat completion returned a tool call without a name."
                )
            if not isinstance(arguments, str):
                raise LLMCompletionError(
                    "OpenAI chat completion returned a tool call without arguments."
                )

            parsed.append(
                ToolCall(
                    id=call_id,
                    name=name,
                    arguments=arguments,
                )
            )

        return parsed
