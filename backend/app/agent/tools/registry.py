"""Tool registration and execution."""

from __future__ import annotations

from typing import Any

from app.agent.context import AgentRunContext
from app.agent.exceptions import AgentError, UnknownToolError
from app.agent.schemas import ToolDefinition, ToolResult


class ToolRegistry:
    """Registry of agent tools with OpenAI schema export and dispatch."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        """Register a tool by name."""
        if tool.name in self._tools:
            raise AgentError(f"Tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> ToolDefinition:
        """Return a registered tool definition."""
        tool = self._tools.get(name)
        if tool is None:
            raise UnknownToolError(f"Unknown tool: {name}")
        return tool

    def list_tools(self) -> list[ToolDefinition]:
        """Return all registered tools in registration order."""
        return list(self._tools.values())

    def get_openai_tools(self) -> list[dict[str, Any]]:
        """Return OpenAI-compatible tool schemas for all registered tools."""
        return [tool.to_openai_tool() for tool in self._tools.values()]

    async def execute(
        self,
        name: str,
        context: AgentRunContext,
        arguments: dict[str, Any],
    ) -> ToolResult:
        """Dispatch a tool call to its handler."""
        tool = self.get_tool(name)
        return await tool.handler(context, arguments)
