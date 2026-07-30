import uuid
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.agent.schemas import AgentRunResult, ToolCallResult, ToolResult
from app.agent.structured_output import ArchitectureReport


@pytest.mark.asyncio
async def test_agent_disabled_returns_503(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    create_response = await client.post(
        "/api/v1/projects",
        json={"name": "Agent Disabled"},
        headers=auth_headers,
    )
    project_id = create_response.json()["id"]

    response = await client.post(
        f"/api/v1/projects/{project_id}/agent/runs",
        json={"goal": "Analyze this repository architecture"},
        headers=auth_headers,
    )

    assert response.status_code == 503
    assert "AGENT_ENABLED" in response.json()["detail"]


@pytest.mark.asyncio
async def test_unauthorized_user_cannot_run_agent(
    client: AsyncClient,
) -> None:
    owner_register = await client.post(
        "/api/v1/auth/register",
        json={"email": "agent-owner@example.com", "password": "password123"},
    )
    owner_headers = {
        "Authorization": f"Bearer {owner_register.json()['access_token']}",
    }
    project_response = await client.post(
        "/api/v1/projects",
        json={"name": "Agent Private"},
        headers=owner_headers,
    )
    project_id = project_response.json()["id"]

    unauthenticated = await client.post(
        f"/api/v1/projects/{project_id}/agent/runs",
        json={"goal": "Analyze architecture"},
    )
    assert unauthenticated.status_code == 401

    other_register = await client.post(
        "/api/v1/auth/register",
        json={"email": "agent-other@example.com", "password": "password123"},
    )
    other_headers = {
        "Authorization": f"Bearer {other_register.json()['access_token']}",
    }
    other_user = await client.post(
        f"/api/v1/projects/{project_id}/agent/runs",
        json={"goal": "Analyze architecture"},
        headers=other_headers,
    )
    assert other_user.status_code == 404


@pytest.mark.asyncio
async def test_valid_agent_run_returns_response(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    auth_headers: dict[str, str],
) -> None:
    create_response = await client.post(
        "/api/v1/projects",
        json={"name": "Agent Run"},
        headers=auth_headers,
    )
    project_id = create_response.json()["id"]

    fake_result = AgentRunResult(
        answer="The repository uses a FastAPI backend with a Next.js frontend.",
        steps_taken=2,
        tool_calls=[
            ToolCallResult(
                tool_name="repository_search",
                arguments={"query": "architecture"},
                result=ToolResult(
                    success=True,
                    summary="Found 3 result(s) for query.",
                ),
                duration_ms=12,
            )
        ],
        artifact_type="architecture_report",
        artifact=ArchitectureReport(
            title="Architecture overview",
            summary="Layered FastAPI service.",
            components=[],
            recommendations=[],
            citations=[],
        ),
    )
    run_mock = AsyncMock(return_value=fake_result)
    monkeypatch.setattr("app.api.routes.agent.run_agent", run_mock)

    response = await client.post(
        f"/api/v1/projects/{project_id}/agent/runs",
        json={
            "goal": "Analyze this repository architecture",
            "task_template": "architecture_review",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    run_mock.assert_awaited_once()
    call_args = run_mock.await_args.args
    call_kwargs = run_mock.await_args.kwargs
    assert call_args[2] == uuid.UUID(project_id)
    assert call_args[3] == "Analyze this repository architecture"
    assert call_kwargs["task_template"] == "architecture_review"

    payload = response.json()
    assert payload["project_id"] == project_id
    assert payload["answer"].startswith("The repository uses")
    assert payload["steps_taken"] == 2
    assert len(payload["tool_calls"]) == 1
    assert payload["tool_calls"][0]["tool_name"] == "repository_search"
    assert payload["artifact_type"] == "architecture_report"
    assert payload["artifact"]["title"] == "Architecture overview"


@pytest.mark.asyncio
async def test_unknown_task_template_returns_validation_error(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    create_response = await client.post(
        "/api/v1/projects",
        json={"name": "Bad Template"},
        headers=auth_headers,
    )
    project_id = create_response.json()["id"]

    response = await client.post(
        f"/api/v1/projects/{project_id}/agent/runs",
        json={
            "goal": "Analyze architecture",
            "task_template": "missing_template",
        },
        headers=auth_headers,
    )

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert any("Unknown task template" in str(item) for item in detail)
