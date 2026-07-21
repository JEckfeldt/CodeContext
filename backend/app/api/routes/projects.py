import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core.config import settings
from app.core.deps import DbSession
from app.retrieval import search_similar_chunks
from app.retrieval.exceptions import QueryEmbeddingError, SemanticSearchUnavailableError
from app.schemas import (
    ChunkSearchHit,
    FileRead,
    ProjectCreate,
    ProjectRead,
    ProjectSearchRequest,
    ProjectSearchResponse,
    ProjectUploadResponse,
)
from app.services import project_service
from app.services.ingestion_service import ingestion_service
from app.services.project_service import ProjectNotFoundError

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    session: DbSession,
) -> ProjectRead:
    project = await project_service.create_project(session, payload)
    return ProjectRead.model_validate(project)


@router.post("/{project_id}/upload", response_model=ProjectUploadResponse)
async def upload_repository(
    project_id: uuid.UUID,
    session: DbSession,
    archive: UploadFile = File(...),
) -> ProjectUploadResponse:
    if not archive.filename or not archive.filename.lower().endswith(".zip"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Repository upload must be a ZIP archive.",
        )

    try:
        await project_service.get_project(session, project_id)
    except ProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    upload_dir = Path(settings.data_dir) / "uploads" / "incoming"
    upload_dir.mkdir(parents=True, exist_ok=True)
    upload_path = upload_dir / f"{project_id}.zip"

    upload_path.write_bytes(await archive.read())

    result = await ingestion_service.ingest_zip_upload(
        session,
        project_id,
        upload_path,
    )

    if result["ingestion_status"] == "failed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to extract repository archive.",
        )

    return ProjectUploadResponse.model_validate(result)


@router.get("/{project_id}/files", response_model=list[FileRead])
async def list_project_files(
    project_id: uuid.UUID,
    session: DbSession,
) -> list[FileRead]:
    try:
        files = await project_service.list_project_files(session, project_id)
    except ProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return [FileRead.model_validate(file) for file in files]


@router.post("/{project_id}/search", response_model=ProjectSearchResponse)
async def search_project(
    project_id: uuid.UUID,
    payload: ProjectSearchRequest,
    session: DbSession,
) -> ProjectSearchResponse:
    """Run semantic search over embedded chunks in a project."""
    try:
        results = await search_similar_chunks(session, project_id, payload.query)
    except ProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except (SemanticSearchUnavailableError, QueryEmbeddingError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return ProjectSearchResponse(
        project_id=project_id,
        query=payload.query,
        results=[ChunkSearchHit.model_validate(hit) for hit in results],
    )
