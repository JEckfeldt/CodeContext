import uuid

import pytest
from pydantic import ValidationError

from app.agent.artifact_parser import parse_artifact_from_response
from app.agent.schemas import AgentRunResult, ToolCallResult, ToolResult
from app.agent.structured_output import (
    ArchitectureReport,
    ArtifactType,
    ImplementationPlan,
    get_artifact_schema,
    validate_artifact,
)
from app.schemas.agent import AgentRunResponse


def _valid_implementation_plan_payload() -> dict:
    return {
        "title": "Authentication Implementation Plan",
        "goal": "Implement authentication",
        "summary": "Add JWT auth aligned with existing CodeContext patterns.",
        "existing_system_analysis": (
            "Authentication already exists in backend/app/services/auth_service.py "
            "with JWT helpers in backend/app/core/security.py."
        ),
        "relevant_files": [
            "backend/app/services/auth_service.py",
            "backend/app/core/security.py",
        ],
        "affected_components": [
            {
                "name": "Auth service",
                "description": "Handles register/login and token issuance.",
                "file_paths": ["backend/app/services/auth_service.py"],
            }
        ],
        "milestones": [
            {
                "title": "Extend auth models",
                "objective": "Ensure user model supports required auth fields.",
                "files_to_modify": ["backend/app/models/user.py"],
                "files_to_create": [],
                "implementation_details": "Add any missing columns and migration.",
                "testing_requirements": ["Model tests pass", "Migration applies cleanly"],
                "cursor_prompt": (
                    "Implement Milestone 1 of the authentication plan. "
                    "Update user models only; match CodeContext conventions."
                ),
            }
        ],
        "risks": ["Existing sessions may require migration planning."],
        "citations": [
            {
                "file_path": "backend/app/services/auth_service.py",
                "start_line": 1,
                "end_line": 40,
            }
        ],
    }


def test_implementation_plan_validates() -> None:
    plan = validate_artifact("implementation_plan", _valid_implementation_plan_payload())

    assert isinstance(plan, ImplementationPlan)
    assert plan.title == "Authentication Implementation Plan"
    assert plan.goal == "Implement authentication"
    assert len(plan.milestones) == 1
    assert plan.milestones[0].cursor_prompt.startswith("Implement Milestone 1")
    assert plan.affected_components[0].name == "Auth service"


def test_implementation_plan_rejects_invalid_payload() -> None:
    payload = _valid_implementation_plan_payload()
    payload.pop("milestones")

    with pytest.raises(ValidationError):
        validate_artifact("implementation_plan", payload)

    with pytest.raises(ValidationError):
        validate_artifact(
            "implementation_plan",
            {**_valid_implementation_plan_payload(), "goal": ""},
        )


def test_implementation_plan_artifact_type_lookup() -> None:
    assert get_artifact_schema(ArtifactType.IMPLEMENTATION_PLAN) is ImplementationPlan
    assert get_artifact_schema("implementation_plan") is ImplementationPlan


def test_parse_implementation_plan_from_raw_json() -> None:
    import json

    content = json.dumps(_valid_implementation_plan_payload())
    parsed = parse_artifact_from_response(content, "implementation_plan")

    assert parsed.artifact_type == "implementation_plan"
    assert isinstance(parsed.artifact, ImplementationPlan)
    assert parsed.artifact.milestones[0].title == "Extend auth models"


def test_parse_implementation_plan_from_fenced_json() -> None:
    import json

    fenced = (
        "Here is the implementation plan:\n```json\n"
        f"{json.dumps(_valid_implementation_plan_payload(), indent=2)}\n```"
    )
    parsed = parse_artifact_from_response(fenced, "implementation_plan")

    assert parsed.artifact_type == "implementation_plan"
    assert isinstance(parsed.artifact, ImplementationPlan)
    assert parsed.artifact.relevant_files[0].endswith("auth_service.py")


def test_parse_implementation_plan_malformed_json_gracefully_falls_back() -> None:
    parsed = parse_artifact_from_response(
        "## Plan\n\nUse JWT auth.\n```json\n{not valid json}\n```",
        "implementation_plan",
    )

    assert parsed.artifact_type is None
    assert parsed.artifact is None


def test_parse_implementation_plan_invalid_schema_gracefully_falls_back() -> None:
    parsed = parse_artifact_from_response(
        '{"title": "Incomplete", "summary": "Missing required fields"}',
        "implementation_plan",
    )

    assert parsed.artifact_type is None
    assert parsed.artifact is None


def test_artifact_parser_does_not_break_architecture_report() -> None:
    architecture_payload = {
        "title": "Architecture Overview",
        "summary": "FastAPI backend with PostgreSQL",
        "components": [
            {
                "name": "Backend API",
                "description": "Handles REST endpoints",
            }
        ],
    }

    raw = parse_artifact_from_response(
        __import__("json").dumps(architecture_payload),
        "architecture_report",
    )
    fenced = parse_artifact_from_response(
        f"```json\n{__import__('json').dumps(architecture_payload)}\n```",
        "architecture_report",
    )

    assert isinstance(raw.artifact, ArchitectureReport)
    assert isinstance(fenced.artifact, ArchitectureReport)
    assert raw.artifact.components[0].name == "Backend API"


def test_agent_run_response_supports_implementation_plan_artifact() -> None:
    plan = validate_artifact("implementation_plan", _valid_implementation_plan_payload())
    result = AgentRunResult(
        answer="Plan attached as JSON.",
        steps_taken=2,
        tool_calls=[],
        artifact_type="implementation_plan",
        artifact=plan,
    )

    response = AgentRunResponse.from_agent_run_result(uuid.uuid4(), result)

    assert response.artifact_type == ArtifactType.IMPLEMENTATION_PLAN
    assert isinstance(response.artifact, ImplementationPlan)
    assert response.artifact.milestones[0].testing_requirements[0] == "Model tests pass"
