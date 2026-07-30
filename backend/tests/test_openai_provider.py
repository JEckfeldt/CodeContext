from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.llm.exceptions import LLMCompletionError
from app.llm.openai_provider import OpenAIChatProvider

_MESSAGES = [{"role": "user", "content": "Hello"}]
_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "repository_search",
            "description": "Search indexed project content.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    }
]


def _mock_http_response(payload: dict) -> MagicMock:
    response = MagicMock()
    response.raise_for_status = MagicMock()
    response.json.return_value = payload
    return response


def _patch_async_client(response: MagicMock):
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=response)
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    return patch("app.llm.openai_provider.httpx.AsyncClient", return_value=mock_client)


@pytest.mark.asyncio
async def test_complete_returns_content_with_empty_tool_calls() -> None:
    provider = OpenAIChatProvider(api_key="test-key", model="gpt-4o-mini")
    payload = {
        "choices": [
            {
                "message": {
                    "content": "Hello back.",
                    "tool_calls": None,
                }
            }
        ]
    }

    with _patch_async_client(_mock_http_response(payload)):
        result = await provider.complete(_MESSAGES)

    assert result == "Hello back."


@pytest.mark.asyncio
async def test_complete_with_tools_parses_tool_calls() -> None:
    provider = OpenAIChatProvider(api_key="test-key", model="gpt-4o-mini")
    payload = {
        "choices": [
            {
                "message": {
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call_abc123",
                            "type": "function",
                            "function": {
                                "name": "repository_search",
                                "arguments": "{\"query\": \"authentication flow\"}",
                            },
                        }
                    ],
                }
            }
        ]
    }

    with _patch_async_client(_mock_http_response(payload)):
        result = await provider.complete_with_tools(_MESSAGES, _TOOLS)

    assert result.content is None
    assert result.has_tool_calls is True
    assert len(result.tool_calls) == 1
    assert result.tool_calls[0].id == "call_abc123"
    assert result.tool_calls[0].name == "repository_search"
    assert result.tool_calls[0].arguments == "{\"query\": \"authentication flow\"}"


@pytest.mark.asyncio
async def test_complete_with_tools_includes_tools_in_request_payload() -> None:
    provider = OpenAIChatProvider(api_key="test-key", model="gpt-4o-mini")
    payload = {
        "choices": [
            {
                "message": {
                    "content": "Done.",
                    "tool_calls": [],
                }
            }
        ]
    }
    response = _mock_http_response(payload)

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=response)
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("app.llm.openai_provider.httpx.AsyncClient", return_value=mock_client):
        await provider.complete_with_tools(
            _MESSAGES,
            _TOOLS,
            tool_choice="auto",
        )

    mock_client.post.assert_awaited_once()
    request_kwargs = mock_client.post.await_args.kwargs
    request_json = request_kwargs["json"]

    assert request_json["tools"] == _TOOLS
    assert request_json["tool_choice"] == "auto"
    assert request_json["model"] == "gpt-4o-mini"


@pytest.mark.asyncio
async def test_complete_does_not_send_tools_in_request_payload() -> None:
    provider = OpenAIChatProvider(api_key="test-key", model="gpt-4o-mini")
    payload = {
        "choices": [
            {
                "message": {
                    "content": "Plain answer.",
                }
            }
        ]
    }
    response = _mock_http_response(payload)

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=response)
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("app.llm.openai_provider.httpx.AsyncClient", return_value=mock_client):
        await provider.complete(_MESSAGES)

    request_json = mock_client.post.await_args.kwargs["json"]
    assert "tools" not in request_json
    assert "tool_choice" not in request_json


@pytest.mark.asyncio
async def test_complete_with_tools_requires_tool_definitions() -> None:
    provider = OpenAIChatProvider(api_key="test-key", model="gpt-4o-mini")

    with pytest.raises(LLMCompletionError, match="requires at least one tool definition"):
        await provider.complete_with_tools(_MESSAGES, [])
