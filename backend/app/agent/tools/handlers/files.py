"""Project file listing and read tool handlers."""

from __future__ import annotations

from typing import Any

from app.agent.context import AgentRunContext
from app.agent.schemas import ToolResult
from app.services import project_service
from app.services.project_service import ProjectFileNotFoundError

LIST_TOOL_NAME = "list_project_files"
READ_TOOL_NAME = "read_file"


def _normalize_optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _compact_file_metadata(file) -> dict[str, Any]:
    return {
        "path": file.path,
        "filename": file.filename,
        "language": file.language,
        "extension": file.extension,
    }


def _slice_content_by_lines(
    content: str,
    *,
    start_line: int | None,
    end_line: int | None,
) -> tuple[str, int, int]:
    lines = content.splitlines()
    total_lines = max(len(lines), 1)

    effective_start = start_line if start_line is not None else 1
    effective_end = end_line if end_line is not None else total_lines

    if effective_start < 1:
        effective_start = 1
    if effective_end < effective_start:
        effective_end = effective_start
    if effective_end > total_lines:
        effective_end = total_lines

    start_index = effective_start - 1
    sliced = "\n".join(lines[start_index:effective_end])
    return sliced, effective_start, effective_end


async def list_project_files_handler(
    context: AgentRunContext,
    arguments: dict[str, Any],
) -> ToolResult:
    files = await project_service.list_project_files(
        context.session,
        context.project_id,
        user_id=context.user_id,
    )

    path_prefix = _normalize_optional_str(arguments.get("path_prefix"))
    extension = _normalize_optional_str(arguments.get("extension"))
    if extension is not None:
        extension = extension.lstrip(".").lower()

    filtered = files
    if path_prefix is not None:
        normalized_prefix = path_prefix.lstrip("/")
        filtered = [file for file in filtered if file.path.startswith(normalized_prefix)]
    if extension is not None:
        filtered = [
            file
            for file in filtered
            if (file.extension or "").lower() == extension
        ]

    items = [_compact_file_metadata(file) for file in filtered]

    return ToolResult(
        success=True,
        summary=f"Listed {len(items)} file(s).",
        data={"files": items, "count": len(items)},
    )


async def read_file_handler(
    context: AgentRunContext,
    arguments: dict[str, Any],
) -> ToolResult:
    path = _normalize_optional_str(arguments.get("path"))
    if path is None:
        return ToolResult(
            success=False,
            summary="File path is required.",
            data=None,
        )

    start_line = arguments.get("start_line")
    end_line = arguments.get("end_line")
    parsed_start = int(start_line) if start_line is not None else None
    parsed_end = int(end_line) if end_line is not None else None

    try:
        file_content = await project_service.get_project_file_content(
            context.session,
            context.project_id,
            path,
            user_id=context.user_id,
        )
    except ProjectFileNotFoundError as exc:
        return ToolResult(
            success=False,
            summary=str(exc),
            data=None,
        )

    content, citation_start, citation_end = _slice_content_by_lines(
        file_content.content,
        start_line=parsed_start,
        end_line=parsed_end,
    )

    return ToolResult(
        success=True,
        summary=f"Read {file_content.path} (lines {citation_start}-{citation_end}).",
        data={
            "path": file_content.path,
            "filename": file_content.filename,
            "language": file_content.language,
            "extension": file_content.extension,
            "start_line": citation_start,
            "end_line": citation_end,
            "content": content,
            "truncated": file_content.truncated,
        },
        citations=[
            {
                "file_path": file_content.path,
                "start_line": citation_start,
                "end_line": citation_end,
            }
        ],
    )


LIST_OPENAI_PARAMETERS: dict[str, Any] = {
    "type": "object",
    "properties": {
        "path_prefix": {
            "type": "string",
            "description": "Optional path prefix filter (e.g. backend/app).",
        },
        "extension": {
            "type": "string",
            "description": "Optional file extension filter without dot (e.g. py, md).",
        },
    },
}

READ_OPENAI_PARAMETERS: dict[str, Any] = {
    "type": "object",
    "properties": {
        "path": {
            "type": "string",
            "description": "Project-relative file path to read.",
        },
        "start_line": {
            "type": "integer",
            "description": "Optional 1-based start line (inclusive).",
            "minimum": 1,
        },
        "end_line": {
            "type": "integer",
            "description": "Optional 1-based end line (inclusive).",
            "minimum": 1,
        },
    },
    "required": ["path"],
}
