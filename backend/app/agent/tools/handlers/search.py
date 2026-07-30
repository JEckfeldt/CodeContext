"""Semantic search tool handler."""

from __future__ import annotations

from typing import Any

from app.agent.context import AgentRunContext
from app.agent.schemas import ToolResult
from app.prompts.rag_context import truncate_snippet
from app.retrieval.retrieval_service import DEFAULT_TOP_K, search_similar_chunks
from app.retrieval.types import ChunkSearchResult
from app.services import project_service

TOOL_NAME = "repository_search"
MAX_SNIPPET_LINES = 14
MAX_SNIPPET_CHARS = 400


def _compact_search_hit(hit: ChunkSearchResult) -> dict[str, Any]:
    return {
        "file_path": hit.file_path,
        "start_line": hit.start_line,
        "end_line": hit.end_line,
        "symbol_name": hit.symbol_name,
        "snippet": truncate_snippet(
            hit.content,
            max_lines=MAX_SNIPPET_LINES,
            max_chars=MAX_SNIPPET_CHARS,
        ),
        "similarity": hit.similarity,
    }


async def repository_search_handler(
    context: AgentRunContext,
    arguments: dict[str, Any],
) -> ToolResult:
    query = str(arguments.get("query", "")).strip()
    if not query:
        return ToolResult(
            success=False,
            summary="Search query must not be empty.",
            data={"results": []},
        )

    await project_service.get_project_for_user(
        context.session,
        context.project_id,
        context.user_id,
    )

    raw_limit = arguments.get("limit")
    limit = DEFAULT_TOP_K
    if raw_limit is not None:
        limit = max(1, min(int(raw_limit), 20))

    hits = await search_similar_chunks(
        context.session,
        context.project_id,
        query,
        limit=limit,
    )
    results = [_compact_search_hit(hit) for hit in hits]

    return ToolResult(
        success=True,
        summary=f"Found {len(results)} result(s) for query.",
        data={"query": query, "results": results},
        citations=[
            {
                "file_path": item["file_path"],
                "start_line": item["start_line"],
                "end_line": item["end_line"],
                "symbol_name": item["symbol_name"],
            }
            for item in results
        ],
    )


OPENAI_PARAMETERS: dict[str, Any] = {
    "type": "object",
    "properties": {
        "query": {
            "type": "string",
            "description": "Natural-language search query over indexed project content.",
        },
        "limit": {
            "type": "integer",
            "description": "Maximum number of results to return (1-20).",
            "minimum": 1,
            "maximum": 20,
        },
    },
    "required": ["query"],
}
