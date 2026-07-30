import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.agent.context import AgentRunContext
from app.agent.tools.handlers.files import (
    list_project_files_handler,
    read_file_handler,
)
from app.agent.tools.handlers.search import repository_search_handler
from app.agent.tools.handlers.stats import get_project_stats_handler
from app.agent.tools.registry_factory import create_default_registry
from app.retrieval.types import ChunkSearchResult
from app.services import project_service
from app.services import project_stats_service
from app.services.project_service import ProjectFileContent


def _context() -> AgentRunContext:
    return AgentRunContext(
        session=AsyncMock(),
        user_id=uuid.uuid4(),
        project_id=uuid.uuid4(),
    )


@pytest.mark.asyncio
async def test_repository_search_returns_tool_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = _context()
    hit = ChunkSearchResult(
        file_path="src/auth.py",
        content="def login():\n    pass\n",
        start_line=1,
        end_line=2,
        symbol_name="login",
        similarity=0.91,
    )

    monkeypatch.setattr(
        project_service,
        "get_project_for_user",
        AsyncMock(return_value=MagicMock()),
    )
    search_mock = AsyncMock(return_value=[hit])
    monkeypatch.setattr(
        "app.agent.tools.handlers.search.search_similar_chunks",
        search_mock,
    )

    result = await repository_search_handler(context, {"query": "authentication"})

    assert result.success is True
    assert result.data is not None
    assert len(result.data["results"]) == 1
    assert result.data["results"][0]["file_path"] == "src/auth.py"
    assert result.data["results"][0]["symbol_name"] == "login"
    assert result.citations is not None
    assert result.citations[0]["start_line"] == 1
    search_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_project_files_returns_tool_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = _context()
    file = MagicMock()
    file.path = "src/app.py"
    file.filename = "app.py"
    file.language = "python"
    file.extension = "py"

    list_mock = AsyncMock(return_value=[file])
    monkeypatch.setattr(project_service, "list_project_files", list_mock)

    result = await list_project_files_handler(context, {"extension": "py"})

    assert result.success is True
    assert result.data is not None
    assert result.data["count"] == 1
    assert result.data["files"][0]["path"] == "src/app.py"
    list_mock.assert_awaited_once_with(
        context.session,
        context.project_id,
        user_id=context.user_id,
    )


@pytest.mark.asyncio
async def test_get_project_stats_returns_tool_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = _context()
    stats = project_stats_service.ProjectStats(
        file_count=3,
        chunk_count=12,
        source_count=1,
        embedding_count=12,
        last_indexed_at=None,
    )

    monkeypatch.setattr(
        project_service,
        "get_project_for_user",
        AsyncMock(return_value=MagicMock()),
    )
    stats_mock = AsyncMock(return_value=stats)
    monkeypatch.setattr(project_stats_service, "get_project_stats", stats_mock)

    result = await get_project_stats_handler(context, {})

    assert result.success is True
    assert result.data == {
        "file_count": 3,
        "chunk_count": 12,
        "embedding_count": 12,
        "source_count": 1,
        "last_indexed_at": None,
    }


@pytest.mark.asyncio
async def test_read_file_returns_citation_data(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = _context()
    file_content = ProjectFileContent(
        id=uuid.uuid4(),
        project_id=context.project_id,
        path="src/app.py",
        filename="app.py",
        extension="py",
        language="python",
        size=30,
        content="line1\nline2\nline3\n",
        truncated=False,
    )

    read_mock = AsyncMock(return_value=file_content)
    monkeypatch.setattr(project_service, "get_project_file_content", read_mock)

    result = await read_file_handler(
        context,
        {"path": "src/app.py", "start_line": 2, "end_line": 2},
    )

    assert result.success is True
    assert result.data is not None
    assert result.data["content"] == "line2"
    assert result.citations == [
        {
            "file_path": "src/app.py",
            "start_line": 2,
            "end_line": 2,
        }
    ]


def test_registry_factory_returns_all_four_tools() -> None:
    registry = create_default_registry()
    tool_names = {tool.name for tool in registry.list_tools()}

    assert tool_names == {
        "repository_search",
        "list_project_files",
        "get_project_stats",
        "read_file",
    }
    assert len(registry.get_openai_tools()) == 4
