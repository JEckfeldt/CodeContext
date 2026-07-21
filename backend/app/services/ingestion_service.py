import uuid
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.indexing.discovery import discover_files
from app.indexing.extraction import (
    RepositoryExtractionError,
    cleanup_directory,
    create_temp_extraction_dir,
    extract_zip_archive,
)
from app.services import indexing_service, project_service


class IngestionService:
    async def ingest_zip_upload(
        self,
        session: AsyncSession,
        project_id: uuid.UUID,
        upload_path: Path,
    ) -> dict[str, object]:
        await project_service.get_project(session, project_id)
        extraction_dir = create_temp_extraction_dir(Path(settings.data_dir) / "uploads")

        try:
            repository_root = extract_zip_archive(upload_path, extraction_dir)
            discovered = discover_files(
                repository_root,
                max_file_size_bytes=settings.max_ingest_file_bytes,
            )
            files_discovered = await project_service.replace_project_files(
                session,
                project_id,
                discovered,
            )
            chunks_created = await indexing_service.index_project_files(
                session,
                project_id,
            )
            return {
                "project_id": project_id,
                "files_discovered": files_discovered,
                "chunks_created": chunks_created,
                "ingestion_status": "completed",
            }
        except RepositoryExtractionError:
            await session.rollback()
            return {
                "project_id": project_id,
                "files_discovered": 0,
                "chunks_created": 0,
                "ingestion_status": "failed",
            }
        finally:
            cleanup_directory(extraction_dir)
            if upload_path.exists():
                upload_path.unlink(missing_ok=True)


ingestion_service = IngestionService()
