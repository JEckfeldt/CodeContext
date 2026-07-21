from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProjectSearchRequest(BaseModel):
    """Natural-language search query for a project."""

    query: str = Field(min_length=1, max_length=4096)


class ChunkSearchHit(BaseModel):
    """One code chunk match from semantic search."""

    model_config = ConfigDict(from_attributes=True)

    file_path: str
    content: str
    start_line: int
    end_line: int
    symbol_name: str | None
    similarity: float


class ProjectSearchResponse(BaseModel):
    """Search results for a project query."""

    project_id: UUID
    query: str
    results: list[ChunkSearchHit]
