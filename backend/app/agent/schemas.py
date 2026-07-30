"""Agent tool definitions and execution results."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from app.agent.context import AgentRunContext

ToolHandler = Callable[[AgentRunContext, dict[str, Any]], Awaitable["ToolResult"]]


@dataclass(frozen=True, slots=True)
class ToolDefinition:
    """Registered tool with OpenAI schema and handler."""

    name: str
    description: str
    parameters: dict[str, Any]
    handler: ToolHandler

    def to_openai_tool(self) -> dict[str, Any]:
        """Convert to OpenAI Chat Completions tool schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


@dataclass(frozen=True, slots=True)
class ToolResult:
    """Outcome returned by a tool handler."""

    success: bool
    summary: str
    data: dict[str, Any] | list[Any] | None = None
    citations: list[dict[str, Any]] | None = None


@dataclass(frozen=True, slots=True)
class ToolCallResult:
    """Record of a single tool invocation for run tracing."""

    tool_name: str
    arguments: dict[str, Any]
    result: ToolResult
    duration_ms: int | None = None
