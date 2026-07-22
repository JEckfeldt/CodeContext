from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from app.services.assistant_service import AssistantResult


class ProjectAskRequest(BaseModel):
    """Natural-language question for the project assistant."""

    question: str = Field(min_length=1, max_length=4096)
    top_k: int | None = Field(default=None, ge=1, le=20)


class SourceCitation(BaseModel):
    """Grounded source reference for an assistant answer."""

    model_config = ConfigDict(from_attributes=True)

    index: int
    file_path: str
    start_line: int
    end_line: int
    symbol_name: str | None
    snippet: str
    similarity: float


class ProjectAskResponse(BaseModel):
    """Assistant answer with structured citations."""

    project_id: UUID
    question: str
    answer: str
    citations: list[SourceCitation]

    @classmethod
    def from_assistant_result(cls, result: AssistantResult) -> ProjectAskResponse:
        """Build API response from ``AssistantResult``."""
        return cls(
            project_id=result.project_id,
            question=result.question,
            answer=result.answer,
            citations=[SourceCitation.model_validate(citation) for citation in result.citations],
        )
