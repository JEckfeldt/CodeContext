import io
import uuid
import zipfile

import pytest
from httpx import AsyncClient

from app.services.indexing_service import count_project_chunks


def _build_repo_zip() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("demo/src/app.py", "def run():\n    return True\n")
        archive.writestr("demo/README.md", "# Demo repo\n")
        archive.writestr("demo/node_modules/pkg/index.js", "module.exports = {}")
    return buffer.getvalue()


@pytest.mark.asyncio
async def test_create_project(client: AsyncClient) -> None:
    response = await client.post("/api/v1/projects", json={"name": "Demo Project"})
    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "Demo Project"
    assert "id" in payload


@pytest.mark.asyncio
async def test_upload_repository_persists_discovered_files(client: AsyncClient) -> None:
    create_response = await client.post("/api/v1/projects", json={"name": "Upload Test"})
    project_id = create_response.json()["id"]

    upload_response = await client.post(
        f"/api/v1/projects/{project_id}/upload",
        files={"archive": ("repo.zip", _build_repo_zip(), "application/zip")},
    )
    assert upload_response.status_code == 200
    upload_payload = upload_response.json()
    assert upload_payload["project_id"] == project_id
    assert upload_payload["files_discovered"] == 2
    assert upload_payload["ingestion_status"] == "completed"

    files_response = await client.get(f"/api/v1/projects/{project_id}/files")
    assert files_response.status_code == 200
    files = files_response.json()
    paths = {item["path"] for item in files}
    assert "src/app.py" in paths
    assert "README.md" in paths
    assert all("content" not in item for item in files)


@pytest.mark.asyncio
async def test_upload_repository_creates_code_chunks(
    client: AsyncClient,
    db_session,
) -> None:
    create_response = await client.post("/api/v1/projects", json={"name": "Chunk Test"})
    project_id = create_response.json()["id"]

    upload_response = await client.post(
        f"/api/v1/projects/{project_id}/upload",
        files={"archive": ("repo.zip", _build_repo_zip(), "application/zip")},
    )
    assert upload_response.status_code == 200
    upload_payload = upload_response.json()
    assert upload_payload["chunks_created"] >= 2

    chunk_count = await count_project_chunks(db_session, uuid.UUID(project_id))
    assert chunk_count == upload_payload["chunks_created"]
    assert chunk_count >= 2


@pytest.mark.asyncio
async def test_upload_rejects_invalid_archive(client: AsyncClient) -> None:
    create_response = await client.post("/api/v1/projects", json={"name": "Bad Upload"})
    project_id = create_response.json()["id"]

    upload_response = await client.post(
        f"/api/v1/projects/{project_id}/upload",
        files={"archive": ("repo.zip", b"not-a-zip", "application/zip")},
    )
    assert upload_response.status_code == 400


@pytest.mark.asyncio
async def test_import_git_rejects_invalid_url(client: AsyncClient) -> None:
    create_response = await client.post("/api/v1/projects", json={"name": "Git Invalid"})
    project_id = create_response.json()["id"]

    response = await client.post(
        f"/api/v1/projects/{project_id}/import",
        json={"source_type": "git", "url": "not-a-valid-url"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_import_git_persists_discovered_files(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from pathlib import Path

    def mock_clone(url: str, destination: Path) -> None:
        destination.mkdir(parents=True)
        (destination / "src" / "app.py").parent.mkdir(parents=True, exist_ok=True)
        (destination / "src" / "app.py").write_text("def run():\n    return True\n", encoding="utf-8")
        (destination / "README.md").write_text("# Git demo\n", encoding="utf-8")

    monkeypatch.setattr(
        "app.ingestion.importers.git_importer.clone_git_repository",
        mock_clone,
    )

    create_response = await client.post("/api/v1/projects", json={"name": "Git Import"})
    project_id = create_response.json()["id"]

    import_response = await client.post(
        f"/api/v1/projects/{project_id}/import",
        json={
            "source_type": "git",
            "url": "https://github.com/user/repository",
        },
    )
    assert import_response.status_code == 200
    payload = import_response.json()
    assert payload["project_id"] == project_id
    assert payload["files_discovered"] == 2
    assert payload["ingestion_status"] == "completed"
    assert payload["chunks_created"] >= 2

    files_response = await client.get(f"/api/v1/projects/{project_id}/files")
    paths = {item["path"] for item in files_response.json()}
    assert "src/app.py" in paths
    assert "README.md" in paths


@pytest.mark.asyncio
async def test_import_files_rejects_unsupported_extension(client: AsyncClient) -> None:
    create_response = await client.post("/api/v1/projects", json={"name": "Bad Files"})
    project_id = create_response.json()["id"]

    response = await client.post(
        f"/api/v1/projects/{project_id}/files/import",
        files={"files": ("notes.zip", b"binary", "application/zip")},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_import_files_persists_markdown_and_text(client: AsyncClient) -> None:
    create_response = await client.post("/api/v1/projects", json={"name": "File Import"})
    project_id = create_response.json()["id"]

    response = await client.post(
        f"/api/v1/projects/{project_id}/files/import",
        files=[
            ("files", ("guide.md", b"# Guide\n\nHello\n", "text/markdown")),
            ("files", ("notes.txt", b"Plain notes\n", "text/plain")),
        ],
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["files_discovered"] == 2
    assert payload["ingestion_status"] == "completed"
    assert payload["chunks_created"] >= 2

    files_response = await client.get(f"/api/v1/projects/{project_id}/files")
    paths = {item["path"] for item in files_response.json()}
    assert paths == {"guide.md", "notes.txt"}


@pytest.mark.asyncio
async def test_import_files_rejects_unsupported_extension(client: AsyncClient) -> None:
    create_response = await client.post("/api/v1/projects", json={"name": "Bad Files"})
    project_id = create_response.json()["id"]

    response = await client.post(
        f"/api/v1/projects/{project_id}/files/import",
        files={"files": ("notes.zip", b"binary", "application/zip")},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_import_files_persists_markdown_and_text(client: AsyncClient) -> None:
    create_response = await client.post("/api/v1/projects", json={"name": "File Import"})
    project_id = create_response.json()["id"]

    response = await client.post(
        f"/api/v1/projects/{project_id}/files/import",
        files=[
            ("files", ("guide.md", b"# Guide\n\nHello\n", "text/markdown")),
            ("files", ("notes.txt", b"Plain notes\n", "text/plain")),
        ],
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["files_discovered"] == 2
    assert payload["ingestion_status"] == "completed"
    assert payload["chunks_created"] >= 2

    files_response = await client.get(f"/api/v1/projects/{project_id}/files")
    paths = {item["path"] for item in files_response.json()}
    assert paths == {"guide.md", "notes.txt"}
