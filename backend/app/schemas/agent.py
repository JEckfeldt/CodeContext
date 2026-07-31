"""API schemas for agent runs and structured artifacts."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.agent.structured_output import (
    ArchitectureReport,
    ArtifactType,
    FindingsReport,
    ImplementationPlan,
    RoadmapReport,
    validate_artifact,
)
from app.prompts.agent_task_templates import UnknownTaskTemplateError, get_task_template

if TYPE_CHECKING:
    from app.agent.schemas import AgentRunResult


class AgentRunRequest(BaseModel):
    """Start an agent analysis run for a project."""

    goal: str = Field(min_length=1, max_length=4096)
    task_template: str | None = Field(default=None, min_length=1, max_length=64)

    @field_validator("task_template")
    @classmethod
    def validate_task_template(cls, value: str | None) -> str | None:
        if value is None:
            return None
        try:
            get_task_template(value)
        except UnknownTaskTemplateError as exc:
            raise ValueError(str(exc)) from exc
        return value


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
    artifact: ArchitectureReport | FindingsReport | RoadmapReport | ImplementationPlan | None = None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_agent_run_result(
        cls,
        project_id: UUID,
        result: AgentRunResult,
    ) -> AgentRunResponse:
        """Build API response from an internal agent run result."""
        tool_calls = [
            ToolCallTraceRead(
                tool_name=call.tool_name,
                arguments=call.arguments,
                success=call.result.success,
                summary=call.result.summary,
                duration_ms=call.duration_ms,
            )
            for call in result.tool_calls
        ]

        artifact_type: ArtifactType | None = None
        artifact: ArchitectureReport | FindingsReport | RoadmapReport | ImplementationPlan | None = None
        if result.artifact_type is not None and result.artifact is not None:
            artifact_type = ArtifactType(result.artifact_type)
            if isinstance(result.artifact, BaseModel):
                artifact = result.artifact  # type: ignore[assignment]
            else:
                artifact = validate_artifact(result.artifact_type, result.artifact)  # type: ignore[assignment]

        return cls(
            project_id=project_id,
            answer=result.answer,
            steps_taken=result.steps_taken,
            tool_calls=tool_calls,
            artifact_type=artifact_type,
            artifact=artifact,
        )
