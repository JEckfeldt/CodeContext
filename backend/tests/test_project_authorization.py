import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_new_project_belongs_to_current_user(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    create_response = await client.post(
        "/api/v1/projects",
        json={"name": "Owned Project"},
        headers=auth_headers,
    )
    project_id = create_response.json()["id"]

    list_response = await client.get("/api/v1/projects", headers=auth_headers)
    assert list_response.status_code == 200
    project_ids = {item["id"] for item in list_response.json()}
    assert project_id in project_ids


@pytest.mark.asyncio
async def test_user_cannot_access_another_users_project(client: AsyncClient) -> None:
    owner_register = await client.post(
        "/api/v1/auth/register",
        json={"email": "owner@example.com", "password": "password123"},
    )
    owner_headers = {
        "Authorization": f"Bearer {owner_register.json()['access_token']}",
    }
    project_response = await client.post(
        "/api/v1/projects",
        json={"name": "Private Project"},
        headers=owner_headers,
    )
    project_id = project_response.json()["id"]

    other_register = await client.post(
        "/api/v1/auth/register",
        json={"email": "other@example.com", "password": "password123"},
    )
    other_headers = {
        "Authorization": f"Bearer {other_register.json()['access_token']}",
    }

    response = await client.get(
        f"/api/v1/projects/{project_id}",
        headers=other_headers,
    )
    assert response.status_code == 404

    files_response = await client.get(
        f"/api/v1/projects/{project_id}/files",
        headers=other_headers,
    )
    assert files_response.status_code == 404
