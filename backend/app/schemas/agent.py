"""API schemas for agent runs and structured artifacts."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.agent.structured_output import (
    ArchitectureReport,
    ArtifactCitation,
    ArtifactType,
    Finding,
    FindingsReport,
    RoadmapItem,
    RoadmapReport,
    validate_artifact,
)


class ToolCallTraceRead(BaseModel):
    """Serialized tool invocation from an agent run."""

    tool_name: str
    arguments: dict[str, Any]
    success: bool
    summary: str
    duration_ms: int | None = None


class AgentRunResponse(BaseModel):
    """API response for a completed agent run."""

    project_id: UUID
    answer: str
    steps_taken: int
    tool_calls: list[ToolCallTraceRead] = Field(default_factory=list)
    artifact_type: ArtifactType | None = None
    artifact: ArchitectureReport | FindingsReport | RoadmapReport | None = None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def build_artifact_fields(
        cls,
        *,
        artifact_type: str | None,
        artifact_payload: dict[str, Any] | None,
    ) -> tuple[ArtifactType | None, ArchitectureReport | FindingsReport | RoadmapReport | None]:
        """Validate optional artifact payload for API serialization."""
        if artifact_type is None or artifact_payload is None:
            return None, None

        validated = validate_artifact(artifact_type, artifact_payload)
        return ArtifactType(artifact_type), validated  # type: ignore[return-value]
