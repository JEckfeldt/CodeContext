import io
import zipfile

import pytest
from httpx import AsyncClient


def _build_repo_zip() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("demo/src/app.py", "def run():\n    return True\n")
        archive.writestr("demo/README.md", "# Demo repo\n")
    return buffer.getvalue()


def _assert_empty_stats(stats: dict) -> None:
    assert stats["file_count"] == 0
    assert stats["chunk_count"] == 0
    assert stats["source_count"] == 0
    assert stats["embedding_count"] == 0
    assert stats["last_indexed_at"] is None


@pytest.mark.asyncio
async def test_create_project_returns_empty_stats(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    response = await client.post(
        "/api/v1/projects",
        json={"name": "Stats Empty"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    payload = response.json()
    assert "stats" in payload
    _assert_empty_stats(payload["stats"])


@pytest.mark.asyncio
async def test_list_projects_includes_stats(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    create_response = await client.post(
        "/api/v1/projects",
        json={"name": "Listed Stats"},
        headers=auth_headers,
    )
    project_id = create_response.json()["id"]

    list_response = await client.get("/api/v1/projects", headers=auth_headers)
    assert list_response.status_code == 200
    project = next(item for item in list_response.json() if item["id"] == project_id)
    assert "stats" in project
    _assert_empty_stats(project["stats"])


@pytest.mark.asyncio
async def test_get_project_returns_stats(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    create_response = await client.post(
        "/api/v1/projects",
        json={"name": "Get Stats"},
        headers=auth_headers,
    )
    project_id = create_response.json()["id"]

    get_response = await client.get(
        f"/api/v1/projects/{project_id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 200
    payload = get_response.json()
    assert "stats" in payload
    _assert_empty_stats(payload["stats"])


@pytest.mark.asyncio
async def test_project_stats_after_zip_import(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    create_response = await client.post(
        "/api/v1/projects",
        json={"name": "Imported Stats"},
        headers=auth_headers,
    )
    project_id = create_response.json()["id"]

    upload_response = await client.post(
        f"/api/v1/projects/{project_id}/upload",
        files={"archive": ("repo.zip", _build_repo_zip(), "application/zip")},
        headers=auth_headers,
    )
    assert upload_response.status_code == 200
    upload_payload = upload_response.json()

    get_response = await client.get(
        f"/api/v1/projects/{project_id}",
        headers=auth_headers,
    )
    stats = get_response.json()["stats"]
    assert stats["file_count"] == upload_payload["files_discovered"]
    assert stats["chunk_count"] == upload_payload["chunks_created"]
    assert stats["source_count"] == 1
    assert stats["embedding_count"] == 0
    assert stats["last_indexed_at"] is not None


@pytest.mark.asyncio
async def test_user_cannot_access_another_users_project_stats(
    client: AsyncClient,
) -> None:
    owner_register = await client.post(
        "/api/v1/auth/register",
        json={"email": "stats-owner@example.com", "password": "password123"},
    )
    owner_headers = {
        "Authorization": f"Bearer {owner_register.json()['access_token']}",
    }
    project_response = await client.post(
        "/api/v1/projects",
        json={"name": "Private Stats Project"},
        headers=owner_headers,
    )
    project_id = project_response.json()["id"]

    other_register = await client.post(
        "/api/v1/auth/register",
        json={"email": "stats-other@example.com", "password": "password123"},
    )
    other_headers = {
        "Authorization": f"Bearer {other_register.json()['access_token']}",
    }

    response = await client.get(
        f"/api/v1/projects/{project_id}",
        headers=other_headers,
    )
    assert response.status_code == 404
