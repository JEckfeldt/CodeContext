"""Project statistics tool handler."""

from __future__ import annotations

from typing import Any

from app.agent.context import AgentRunContext
from app.agent.schemas import ToolResult
from app.services import project_service
from app.services import project_stats_service

TOOL_NAME = "get_project_stats"


async def get_project_stats_handler(
    context: AgentRunContext,
    arguments: dict[str, Any],
) -> ToolResult:
    _ = arguments
    await project_service.get_project_for_user(
        context.session,
        context.project_id,
        context.user_id,
    )
    stats = await project_stats_service.get_project_stats(
        context.session,
        context.project_id,
    )

    data = {
        "file_count": stats.file_count,
        "chunk_count": stats.chunk_count,
        "embedding_count": stats.embedding_count,
        "source_count": stats.source_count,
        "last_indexed_at": (
            stats.last_indexed_at.isoformat() if stats.last_indexed_at else None
        ),
    }

    return ToolResult(
        success=True,
        summary=(
            f"Project has {stats.file_count} file(s), "
            f"{stats.chunk_count} chunk(s), "
            f"{stats.source_count} source(s)."
        ),
        data=data,
    )


OPENAI_PARAMETERS: dict[str, Any] = {
    "type": "object",
    "properties": {},
}
