import uuid
from typing import Any
from unittest.mock import AsyncMock

import pytest

from app.agent.context import AgentRunContext
from app.agent.exceptions import AgentStepLimitError
from app.agent.runner import AgentRunner
from app.agent.schemas import ToolDefinition, ToolResult
from app.agent.tools.registry import ToolRegistry
from app.llm.types import ChatCompletionResult, ToolCall


class FakeChatProvider:
    """Test double that returns a scripted sequence of completions."""

    def __init__(self, responses: list[ChatCompletionResult]) -> None:
        self._responses = list(responses)
        self.calls: list[list[dict[str, Any]]] = []

    async def complete_with_tools(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        *,
        tool_choice: str | dict[str, Any] = "auto",
        max_tokens: int | None = None,
    ) -> ChatCompletionResult:
        del tools, tool_choice, max_tokens
        self.calls.append(messages)
        if not self._responses:
            raise RuntimeError("FakeChatProvider has no remaining responses.")
        return self._responses.pop(0)


async def _search_handler(_context: AgentRunContext, arguments: dict) -> ToolResult:
    query = arguments.get("query", "")
    return ToolResult(
        success=True,
        summary=f"Found results for {query!r}.",
        data={"query": query, "results": [{"file_path": "src/auth.py"}]},
        citations=[{"file_path": "src/auth.py", "start_line": 1, "end_line": 10}],
    )


def _search_tool() -> ToolDefinition:
    return ToolDefinition(
        name="repository_search",
        description="Search indexed project content.",
        parameters={
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
        handler=_search_handler,
    )


def _list_tool() -> ToolDefinition:
    async def handler(_context: AgentRunContext, _arguments: dict) -> ToolResult:
        return ToolResult(
            success=True,
            summary="Listed project files.",
            data={"files": [{"path": "src/auth.py"}]},
        )

    return ToolDefinition(
        name="list_project_files",
        description="List project files.",
        parameters={"type": "object", "properties": {}},
        handler=handler,
    )


def _registry(*tools: ToolDefinition) -> ToolRegistry:
    registry = ToolRegistry()
    for tool in tools:
        registry.register(tool)
    return registry


def _context() -> AgentRunContext:
    return AgentRunContext(
        session=AsyncMock(),
        user_id=uuid.uuid4(),
        project_id=uuid.uuid4(),
    )


@pytest.mark.asyncio
async def test_runner_returns_immediate_answer() -> None:
    provider = FakeChatProvider(
        [ChatCompletionResult(content="The project uses FastAPI.", tool_calls=[])]
    )
    runner = AgentRunner(provider, _registry(_search_tool()), max_steps=5)

    result = await runner.run(_context(), goal="What framework is used?")

    assert result.answer == "The project uses FastAPI."
    assert result.steps_taken == 1
    assert result.tool_calls == []
    assert len(provider.calls) == 1
    assert provider.calls[0][0]["role"] == "system"
    assert provider.calls[0][1]["content"] == "What framework is used?"


@pytest.mark.asyncio
async def test_runner_handles_single_tool_call() -> None:
    provider = FakeChatProvider(
        [
            ChatCompletionResult(
                content=None,
                tool_calls=[
                    ToolCall(
                        id="call_search",
                        name="repository_search",
                        arguments='{"query": "authentication"}',
                    )
                ],
            ),
            ChatCompletionResult(content="Auth lives in src/auth.py.", tool_calls=[]),
        ]
    )
    runner = AgentRunner(provider, _registry(_search_tool()), max_steps=5)

    result = await runner.run(_context(), goal="Explain authentication.")

    assert result.answer == "Auth lives in src/auth.py."
    assert result.steps_taken == 2
    assert len(result.tool_calls) == 1
    assert result.tool_calls[0].tool_name == "repository_search"
    assert result.tool_calls[0].arguments == {"query": "authentication"}
    assert result.tool_calls[0].result.success is True

    second_call_messages = provider.calls[1]
    assert second_call_messages[-2]["role"] == "assistant"
    assert second_call_messages[-2]["tool_calls"][0]["id"] == "call_search"
    assert second_call_messages[-1]["role"] == "tool"
    assert second_call_messages[-1]["tool_call_id"] == "call_search"
    assert "authentication" in second_call_messages[-1]["content"]


@pytest.mark.asyncio
async def test_runner_handles_multiple_tool_steps() -> None:
    provider = FakeChatProvider(
        [
            ChatCompletionResult(
                content=None,
                tool_calls=[
                    ToolCall(
                        id="call_search",
                        name="repository_search",
                        arguments='{"query": "routes"}',
                    )
                ],
            ),
            ChatCompletionResult(
                content=None,
                tool_calls=[
                    ToolCall(
                        id="call_list",
                        name="list_project_files",
                        arguments="{}",
                    )
                ],
            ),
            ChatCompletionResult(content="Routes are defined under src/api.", tool_calls=[]),
        ]
    )
    runner = AgentRunner(
        provider,
        _registry(_search_tool(), _list_tool()),
        max_steps=5,
    )

    result = await runner.run(_context(), goal="Map API routes.")

    assert result.answer == "Routes are defined under src/api."
    assert result.steps_taken == 3
    assert [call.tool_name for call in result.tool_calls] == [
        "repository_search",
        "list_project_files",
    ]
    assert len(provider.calls) == 3


@pytest.mark.asyncio
async def test_runner_raises_when_step_limit_exceeded() -> None:
    endless_tool_call = ChatCompletionResult(
        content=None,
        tool_calls=[
            ToolCall(
                id="call_loop",
                name="repository_search",
                arguments='{"query": "keep going"}',
            )
        ],
    )
    provider = FakeChatProvider([endless_tool_call, endless_tool_call, endless_tool_call])
    runner = AgentRunner(provider, _registry(_search_tool()), max_steps=2)

    with pytest.raises(AgentStepLimitError, match="exceeded the maximum of 2"):
        await runner.run(_context(), goal="Never finish.")

    assert len(provider.calls) == 2
