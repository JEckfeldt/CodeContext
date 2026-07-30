import uuid
from unittest.mock import AsyncMock

import pytest

from app.agent.context import AgentRunContext
from app.agent.exceptions import UnknownToolError
from app.agent.schemas import ToolDefinition, ToolResult
from app.agent.tools.registry import ToolRegistry


async def _fake_echo_handler(_context: AgentRunContext, arguments: dict) -> ToolResult:
    message = arguments.get("message", "")
    return ToolResult(
        success=True,
        summary=f"Echoed: {message}",
        data={"message": message},
    )


def _echo_tool() -> ToolDefinition:
    return ToolDefinition(
        name="echo",
        description="Echo a message back for testing.",
        parameters={
            "type": "object",
            "properties": {
                "message": {"type": "string"},
            },
            "required": ["message"],
        },
        handler=_fake_echo_handler,
    )


def _context() -> AgentRunContext:
    return AgentRunContext(
        session=AsyncMock(),
        user_id=uuid.uuid4(),
        project_id=uuid.uuid4(),
    )


def test_register_and_get_tool() -> None:
    registry = ToolRegistry()
    tool = _echo_tool()

    registry.register(tool)

    assert registry.get_tool("echo") is tool
    assert len(registry.list_tools()) == 1


def test_get_openai_tools_schema() -> None:
    registry = ToolRegistry()
    registry.register(_echo_tool())

    schemas = registry.get_openai_tools()

    assert len(schemas) == 1
    assert schemas[0] == {
        "type": "function",
        "function": {
            "name": "echo",
            "description": "Echo a message back for testing.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                },
                "required": ["message"],
            },
        },
    }


@pytest.mark.asyncio
async def test_execute_fake_tool_successfully() -> None:
    registry = ToolRegistry()
    registry.register(_echo_tool())
    context = _context()

    result = await registry.execute(
        "echo",
        context,
        {"message": "hello agent"},
    )

    assert result.success is True
    assert result.summary == "Echoed: hello agent"
    assert result.data == {"message": "hello agent"}
    assert result.citations is None


def test_unknown_tool_raises() -> None:
    registry = ToolRegistry()

    with pytest.raises(UnknownToolError, match="Unknown tool: missing"):
        registry.get_tool("missing")


@pytest.mark.asyncio
async def test_execute_unknown_tool_raises() -> None:
    registry = ToolRegistry()

    with pytest.raises(UnknownToolError, match="Unknown tool: missing"):
        await registry.execute("missing", _context(), {})
