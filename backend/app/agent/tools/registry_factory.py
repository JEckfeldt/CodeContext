"""Factory for the default agent tool registry."""

from app.agent.schemas import ToolDefinition
from app.agent.tools.handlers.files import (
    LIST_OPENAI_PARAMETERS,
    LIST_TOOL_NAME,
    READ_OPENAI_PARAMETERS,
    READ_TOOL_NAME,
    list_project_files_handler,
    read_file_handler,
)
from app.agent.tools.handlers.search import (
    OPENAI_PARAMETERS as SEARCH_OPENAI_PARAMETERS,
    TOOL_NAME as SEARCH_TOOL_NAME,
    repository_search_handler,
)
from app.agent.tools.handlers.stats import (
    OPENAI_PARAMETERS as STATS_OPENAI_PARAMETERS,
    TOOL_NAME as STATS_TOOL_NAME,
    get_project_stats_handler,
)
from app.agent.tools.registry import ToolRegistry


def create_default_registry() -> ToolRegistry:
    """Build a registry with the standard read-only project analysis tools."""
    registry = ToolRegistry()
    registry.register(
        ToolDefinition(
            name=SEARCH_TOOL_NAME,
            description=(
                "Search indexed project content using semantic similarity. "
                "Use for finding relevant code, docs, and snippets."
            ),
            parameters=SEARCH_OPENAI_PARAMETERS,
            handler=repository_search_handler,
        )
    )
    registry.register(
        ToolDefinition(
            name=LIST_TOOL_NAME,
            description=(
                "List files in the project with optional path prefix or extension filters."
            ),
            parameters=LIST_OPENAI_PARAMETERS,
            handler=list_project_files_handler,
        )
    )
    registry.register(
        ToolDefinition(
            name=STATS_TOOL_NAME,
            description=(
                "Get project indexing statistics including files, chunks, sources, "
                "and embeddings."
            ),
            parameters=STATS_OPENAI_PARAMETERS,
            handler=get_project_stats_handler,
        )
    )
    registry.register(
        ToolDefinition(
            name=READ_TOOL_NAME,
            description=(
                "Read bounded content from a project file, optionally limited to a "
                "line range."
            ),
            parameters=READ_OPENAI_PARAMETERS,
            handler=read_file_handler,
        )
    )
    return registry
