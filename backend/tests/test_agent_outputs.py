import pytest
from pydantic import ValidationError

from app.agent.schemas import AgentRunResult, ToolCallResult, ToolResult
from app.agent.structured_output import (
    ArchitectureReport,
    ArtifactType,
    Finding,
    FindingsReport,
    RoadmapItem,
    RoadmapReport,
    UnknownArtifactTypeError,
    get_artifact_schema,
    validate_artifact,
)


def test_architecture_report_validates() -> None:
    report = ArchitectureReport(
        title="Backend architecture",
        summary="FastAPI service with PostgreSQL and pgvector.",
        components=[
            {
                "name": "API layer",
                "description": "FastAPI routes under app/api.",
                "file_paths": ["backend/app/api"],
            }
        ],
        data_flow="Requests flow from API routes into services and the database.",
        recommendations=["Document module boundaries in README."],
        citations=[
            {
                "file_path": "backend/app/main.py",
                "start_line": 1,
                "end_line": 20,
            }
        ],
    )

    assert report.title == "Backend architecture"
    assert len(report.components) == 1
    assert report.components[0].name == "API layer"
    assert report.citations[0].start_line == 1


def test_findings_report_validates() -> None:
    report = FindingsReport(
        title="Security review",
        summary="Two medium-severity findings in authentication handling.",
        findings=[
            Finding(
                severity="medium",
                title="Missing rate limiting",
                description="Login endpoint has no throttling.",
                file_path="backend/app/api/routes/auth.py",
                line_start=12,
                line_end=40,
            )
        ],
        citations=[
            {
                "file_path": "backend/app/api/routes/auth.py",
                "start_line": 12,
                "end_line": 40,
            }
        ],
    )

    assert report.findings[0].severity == "medium"
    assert report.findings[0].line_start == 12


def test_roadmap_report_validates() -> None:
    report = RoadmapReport(
        title="Refactoring roadmap",
        summary="Prioritized cleanup for the agent layer.",
        items=[
            RoadmapItem(
                priority="high",
                title="Add structured artifact parsing",
                description="Validate final LLM JSON into typed report models.",
            )
        ],
    )

    assert report.items[0].priority == "high"
    assert report.items[0].title.startswith("Add structured")


def test_artifact_type_lookup_works() -> None:
    assert get_artifact_schema(ArtifactType.ARCHITECTURE_REPORT) is ArchitectureReport
    assert get_artifact_schema("findings_report") is FindingsReport
    assert get_artifact_schema("roadmap_report") is RoadmapReport

    validated = validate_artifact(
        "architecture_report",
        {
            "title": "Overview",
            "summary": "Simple service layout.",
            "components": [],
            "recommendations": [],
            "citations": [],
        },
    )
    assert isinstance(validated, ArchitectureReport)


def test_unknown_artifact_type_errors() -> None:
    with pytest.raises(UnknownArtifactTypeError, match="Unknown artifact type: 'missing'"):
        get_artifact_schema("missing")

    with pytest.raises(UnknownArtifactTypeError):
        validate_artifact("missing", {"title": "x", "summary": "y"})


def test_architecture_report_requires_title_and_summary() -> None:
    with pytest.raises(ValidationError):
        ArchitectureReport(title="", summary="Missing title.")


def test_agent_run_result_backward_compatible_without_artifact() -> None:
    result = AgentRunResult(
        answer="Done.",
        steps_taken=1,
        tool_calls=[
            ToolCallResult(
                tool_name="repository_search",
                arguments={"query": "auth"},
                result=ToolResult(success=True, summary="Found results."),
            )
        ],
    )

    assert result.answer == "Done."
    assert result.artifact_type is None
    assert result.artifact is None
