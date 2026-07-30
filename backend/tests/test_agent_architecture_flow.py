import uuid
from unittest.mock import AsyncMock

import pytest

from app.agent.context import AgentRunContext
from app.agent.runner import AgentRunner
from app.agent.schemas import ToolDefinition, ToolResult
from app.agent.structured_output import ArchitectureReport
from app.agent.tools.registry import ToolRegistry
from app.llm.types import ChatCompletionResult, ToolCall
from tests.test_agent_runner import FakeChatProvider


async def _search_handler(_context: AgentRunContext, arguments: dict) -> ToolResult:
    query = arguments.get("query", "")
    return ToolResult(
        success=True,
        summary=f"Found results for {query!r}.",
        data={
            "query": query,
            "results": [
                {
                    "file_path": "backend/app/database/session.py",
                    "start_line": 1,
                    "end_line": 20,
                    "symbol_name": "get_db",
                    "snippet": "async def get_db(): ...",
                    "similarity": 0.89,
                }
            ],
        },
        citations=[
            {
                "file_path": "backend/app/database/session.py",
                "start_line": 1,
                "end_line": 20,
            }
        ],
    )


async def _list_files_handler(_context: AgentRunContext, _arguments: dict) -> ToolResult:
    return ToolResult(
        success=True,
        summary="Listed 4 project files.",
        data={
            "count": 4,
            "files": [
                {"path": "backend/app/main.py", "filename": "main.py", "language": "python", "extension": "py"},
                {"path": "backend/app/api/router.py", "filename": "router.py", "language": "python", "extension": "py"},
            ],
        },
    )


def _architecture_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(
        ToolDefinition(
            name="repository_search",
            description="Search indexed project content.",
            parameters={
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
            handler=_search_handler,
        )
    )
    registry.register(
        ToolDefinition(
            name="list_project_files",
            description="List project files.",
            parameters={"type": "object", "properties": {}},
            handler=_list_files_handler,
        )
    )
    return registry


def _context() -> AgentRunContext:
    return AgentRunContext(
        session=AsyncMock(),
        user_id=uuid.uuid4(),
        project_id=uuid.uuid4(),
    )


FINAL_ARCHITECTURE_RESPONSE = """```json
{
  "title": "Architecture Overview",
  "summary": "FastAPI backend with PostgreSQL",
  "components": [
    {
      "name": "Backend API",
      "description": "Handles REST endpoints"
    }
  ]
}
```"""


@pytest.mark.asyncio
async def test_architecture_review_flow_parses_structured_artifact() -> None:
    provider = FakeChatProvider(
        [
            ChatCompletionResult(
                content=None,
                tool_calls=[
                    ToolCall(
                        id="call_search",
                        name="repository_search",
                        arguments='{"query": "database authentication architecture"}',
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
            ChatCompletionResult(content=FINAL_ARCHITECTURE_RESPONSE, tool_calls=[]),
        ]
    )
    runner = AgentRunner(provider, _architecture_registry(), max_steps=8)

    result = await runner.run(
        _context(),
        goal="Analyze this repository architecture",
        task_template="architecture_review",
    )

    assert result.steps_taken == 3
    assert [call.tool_name for call in result.tool_calls] == [
        "repository_search",
        "list_project_files",
    ]
    assert result.tool_calls[0].arguments == {
        "query": "database authentication architecture",
    }
    assert result.tool_calls[0].result.success is True
    assert result.tool_calls[1].result.success is True

    assert result.artifact_type == "architecture_report"
    assert isinstance(result.artifact, ArchitectureReport)
    assert result.artifact.title == "Architecture Overview"
    assert result.artifact.summary == "FastAPI backend with PostgreSQL"
    assert result.artifact.components[0].name == "Backend API"
    assert FINAL_ARCHITECTURE_RESPONSE in result.answer

    system_prompt = provider.calls[0][0]["content"]
    assert "Active task template: architecture_review" in system_prompt
    assert "Expected output format: architecture_report" in system_prompt


@pytest.mark.asyncio
async def test_architecture_flow_keeps_markdown_when_artifact_parsing_fails() -> None:
    provider = FakeChatProvider(
        [
            ChatCompletionResult(
                content="## Architecture Summary\n\nThe backend uses FastAPI and PostgreSQL.",
                tool_calls=[],
            )
        ]
    )
    runner = AgentRunner(provider, _architecture_registry(), max_steps=5)

    result = await runner.run(
        _context(),
        goal="Analyze this repository architecture",
        task_template="architecture_review",
    )

    assert result.answer.startswith("## Architecture Summary")
    assert result.artifact_type is None
    assert result.artifact is None
