"""Structured artifact schemas for agent analysis reports."""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Type

from pydantic import BaseModel, ConfigDict, Field


class ArtifactType(StrEnum):
    """Supported structured artifact output formats."""

    ARCHITECTURE_REPORT = "architecture_report"
    FINDINGS_REPORT = "findings_report"
    ROADMAP_REPORT = "roadmap_report"
    IMPLEMENTATION_PLAN = "implementation_plan"


class UnknownArtifactTypeError(KeyError):
    """Raised when an artifact type is not registered."""


class ArtifactCitation(BaseModel):
    """File and line reference supporting an artifact claim."""

    file_path: str = Field(min_length=1)
    start_line: int = Field(ge=1)
    end_line: int = Field(ge=1)
    symbol_name: str | None = None


class ArchitectureComponent(BaseModel):
    """Named module or layer within the repository."""

    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    file_paths: list[str] = Field(default_factory=list)


class ArchitectureReport(BaseModel):
    """Structured architecture analysis report."""

    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    components: list[ArchitectureComponent] = Field(default_factory=list)
    data_flow: str | None = None
    recommendations: list[str] = Field(default_factory=list)
    citations: list[ArtifactCitation] = Field(default_factory=list)


class Finding(BaseModel):
    """Single finding for security, performance, or quality reviews."""

    severity: str = Field(min_length=1)
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    file_path: str | None = None
    line_start: int | None = Field(default=None, ge=1)
    line_end: int | None = Field(default=None, ge=1)


class FindingsReport(BaseModel):
    """Structured findings report with severity-tagged items."""

    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    findings: list[Finding] = Field(default_factory=list)
    citations: list[ArtifactCitation] = Field(default_factory=list)


class RoadmapItem(BaseModel):
    """Prioritized action item in a refactoring or improvement roadmap."""

    priority: str = Field(min_length=1)
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)


class RoadmapReport(BaseModel):
    """Structured roadmap report with ordered improvement items."""

    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    items: list[RoadmapItem] = Field(default_factory=list)


class ImplementationMilestone(BaseModel):
    """Ordered milestone in an implementation plan."""

    title: str = Field(min_length=1)
    objective: str = Field(min_length=1)
    files_to_modify: list[str] = Field(default_factory=list)
    files_to_create: list[str] = Field(default_factory=list)
    implementation_details: str = Field(min_length=1)
    testing_requirements: list[str] = Field(default_factory=list)
    cursor_prompt: str = Field(min_length=1)


class AffectedComponent(BaseModel):
    """Named component affected by an implementation plan."""

    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    file_paths: list[str] = Field(default_factory=list)


class ImplementationPlan(BaseModel):
    """Structured implementation plan for IDE-agent execution."""

    title: str = Field(min_length=1)
    goal: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    existing_system_analysis: str = Field(min_length=1)
    relevant_files: list[str] = Field(default_factory=list)
    affected_components: list[AffectedComponent] = Field(default_factory=list)
    milestones: list[ImplementationMilestone] = Field(min_length=1)
    risks: list[str] = Field(default_factory=list)
    citations: list[ArtifactCitation] = Field(default_factory=list)


ARTIFACT_SCHEMAS: dict[ArtifactType, Type[BaseModel]] = {
    ArtifactType.ARCHITECTURE_REPORT: ArchitectureReport,
    ArtifactType.FINDINGS_REPORT: FindingsReport,
    ArtifactType.ROADMAP_REPORT: RoadmapReport,
    ArtifactType.IMPLEMENTATION_PLAN: ImplementationPlan,
}


def get_artifact_schema(
    artifact_type: str | ArtifactType,
) -> Type[BaseModel]:
    """Return the Pydantic model for a registered artifact type."""
    if isinstance(artifact_type, ArtifactType):
        normalized = artifact_type
    else:
        try:
            normalized = ArtifactType(artifact_type.strip())
        except ValueError as exc:
            known = ", ".join(item.value for item in ArtifactType)
            raise UnknownArtifactTypeError(
                f"Unknown artifact type: {artifact_type!r}. Known types: {known}"
            ) from exc

    schema = ARTIFACT_SCHEMAS.get(normalized)
    if schema is None:
        known = ", ".join(item.value for item in ArtifactType)
        raise UnknownArtifactTypeError(
            f"Unknown artifact type: {artifact_type!r}. Known types: {known}"
        )
    return schema


def validate_artifact(
    artifact_type: str | ArtifactType,
    payload: dict[str, Any],
) -> BaseModel:
    """Validate raw artifact JSON into the typed report model."""
    schema = get_artifact_schema(artifact_type)
    return schema.model_validate(payload)
