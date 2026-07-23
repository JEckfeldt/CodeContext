import uuid

import pytest
from httpx import AsyncClient

from app.retrieval.types import ChunkSearchResult


@pytest.mark.asyncio
async def test_search_project_returns_results(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    auth_headers: dict[str, str],
) -> None:
    create_response = await client.post(
        "/api/v1/projects",
        json={"name": "Search Test"},
        headers=auth_headers,
    )
    project_id = create_response.json()["id"]

    async def fake_search(session, pid, query, **kwargs):
        assert pid == uuid.UUID(project_id)
        assert query == "Where is authentication implemented?"
        return [
            ChunkSearchResult(
                file_path="src/auth.py",
                content="def login(): pass",
                start_line=1,
                end_line=1,
                symbol_name="login",
                similarity=0.88,
            )
        ]

    monkeypatch.setattr("app.api.routes.projects.search_similar_chunks", fake_search)

    response = await client.post(
        f"/api/v1/projects/{project_id}/search",
        json={"query": "Where is authentication implemented?"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["project_id"] == project_id
    assert payload["query"] == "Where is authentication implemented?"
    assert len(payload["results"]) == 1
    assert payload["results"][0]["file_path"] == "src/auth.py"
    assert payload["results"][0]["similarity"] == pytest.approx(0.88)


@pytest.mark.asyncio
async def test_search_project_not_found(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    missing_id = uuid.uuid4()
    response = await client.post(
        f"/api/v1/projects/{missing_id}/search",
        json={"query": "auth flow"},
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_search_semantic_search_unavailable(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    create_response = await client.post(
        "/api/v1/projects",
        json={"name": "SQLite Search"},
        headers=auth_headers,
    )
    project_id = create_response.json()["id"]

    response = await client.post(
        f"/api/v1/projects/{project_id}/search",
        json={"query": "auth flow"},
        headers=auth_headers,
    )
    assert response.status_code == 503
    assert "PostgreSQL" in response.json()["detail"]


@pytest.mark.asyncio
async def test_search_rejects_invalid_body(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    create_response = await client.post(
        "/api/v1/projects",
        json={"name": "Invalid Search"},
        headers=auth_headers,
    )
    project_id = create_response.json()["id"]

    response = await client.post(
        f"/api/v1/projects/{project_id}/search",
        json={"query": ""},
        headers=auth_headers,
    )
    assert response.status_code == 422

    missing_query = await client.post(
        f"/api/v1/projects/{project_id}/search",
        json={},
        headers=auth_headers,
    )
    assert missing_query.status_code == 422
