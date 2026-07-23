import uuid
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.ingestion.service import ingestion_pipeline


class IngestionService:
    async def ingest_zip_upload(
        self,
        session: AsyncSession,
        project_id: uuid.UUID,
        upload_path: Path,
    ) -> dict[str, object]:
        return await ingestion_pipeline.ingest_zip_upload(
            session,
            project_id,
            upload_path,
        )

    async def ingest_git_url(
        self,
        session: AsyncSession,
        project_id: uuid.UUID,
        url: str,
    ) -> dict[str, object]:
        return await ingestion_pipeline.ingest_git_url(
            session,
            project_id,
            url,
        )


ingestion_service = IngestionService()
