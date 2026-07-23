import uuid
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.ingestion.models import UploadedFilePayload
from app.ingestion.service import ingestion_pipeline


class IngestionService:
    async def ingest_zip_upload(
        self,
        session: AsyncSession,
        project_id: uuid.UUID,
        upload_path: Path,
        *,
        user_id: uuid.UUID,
    ) -> dict[str, object]:
        return await ingestion_pipeline.ingest_zip_upload(
            session,
            project_id,
            upload_path,
            user_id=user_id,
        )

    async def ingest_git_url(
        self,
        session: AsyncSession,
        project_id: uuid.UUID,
        url: str,
        *,
        user_id: uuid.UUID,
    ) -> dict[str, object]:
        return await ingestion_pipeline.ingest_git_url(
            session,
            project_id,
            url,
            user_id=user_id,
        )

    async def ingest_uploaded_files(
        self,
        session: AsyncSession,
        project_id: uuid.UUID,
        files: list[UploadedFilePayload],
        *,
        user_id: uuid.UUID,
    ) -> dict[str, object]:
        return await ingestion_pipeline.ingest_uploaded_files(
            session,
            project_id,
            files,
            user_id=user_id,
        )


ingestion_service = IngestionService()
