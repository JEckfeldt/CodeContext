from __future__ import annotations

import uuid
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.indexing.extraction import cleanup_directory
from app.ingestion.adapters import discovered_files_from_documents
from app.ingestion.base import IngestionError
from app.ingestion.extractors.code_extractor import CodeExtractor
from app.ingestion.importers.git_importer import GitImporter
from app.ingestion.importers.zip_importer import ZipImporter
from app.ingestion.models import GitSource, ImportedFilesystemTree, SourceType, ZipSource
from app.services import embedding_service, indexing_service, project_service


class IngestionPipeline:
    """
    Source-agnostic ingestion orchestration.

    Flow: Source → Importer → Extractor → Documents → persist → Chunker → Embeddings

    New source types plug in by:
    1. Adding a ``SourceType`` and source dataclass in ``models.py``
    2. Implementing ``BaseImporter`` (e.g. ``GitImporter``, ``PdfImporter``)
    3. Choosing an extractor (``CodeExtractor`` for trees, or a dedicated extractor)
    4. Calling ``_ingest_imported_tree`` from a new ``run_*`` entry point
    """

    def __init__(self) -> None:
        upload_base = Path(settings.data_dir) / "uploads"
        self._zip_importer = ZipImporter(extraction_base_dir=upload_base)
        self._git_importer = GitImporter(workspace_base_dir=upload_base)
        self._code_extractor = CodeExtractor()

    async def ingest_zip_upload(
        self,
        session: AsyncSession,
        project_id: uuid.UUID,
        upload_path: Path,
    ) -> dict[str, object]:
        """ZIP upload entry point used by the existing REST API."""
        return await self.run_zip_ingestion(session, project_id, upload_path)

    async def ingest_git_url(
        self,
        session: AsyncSession,
        project_id: uuid.UUID,
        url: str,
    ) -> dict[str, object]:
        """Git URL entry point used by ``POST /projects/{id}/import``."""
        return await self.run_git_ingestion(session, project_id, url)

    async def run_zip_ingestion(
        self,
        session: AsyncSession,
        project_id: uuid.UUID,
        archive_path: Path,
    ) -> dict[str, object]:
        source = ZipSource(source_type=SourceType.ZIP, archive_path=archive_path)
        workspace_dir: Path | None = None

        try:
            imported = self._zip_importer.import_source(source)
            workspace_dir = imported.workspace_dir
            return await self._ingest_imported_tree(session, project_id, imported)
        except IngestionError:
            await session.rollback()
            return self._failed_result(project_id)
        finally:
            if workspace_dir is not None:
                cleanup_directory(workspace_dir)
            if archive_path.exists():
                archive_path.unlink(missing_ok=True)

    async def run_git_ingestion(
        self,
        session: AsyncSession,
        project_id: uuid.UUID,
        url: str,
    ) -> dict[str, object]:
        source = GitSource(source_type=SourceType.GIT, url=url)
        workspace_dir: Path | None = None

        try:
            imported = self._git_importer.import_source(source)
            workspace_dir = imported.workspace_dir
            return await self._ingest_imported_tree(session, project_id, imported)
        except IngestionError:
            await session.rollback()
            return self._failed_result(project_id)
        finally:
            if workspace_dir is not None:
                cleanup_directory(workspace_dir)

    async def _ingest_imported_tree(
        self,
        session: AsyncSession,
        project_id: uuid.UUID,
        imported: ImportedFilesystemTree,
    ) -> dict[str, object]:
        await project_service.get_project(session, project_id)
        documents = self._code_extractor.extract_documents(
            imported,
            max_file_size_bytes=settings.max_ingest_file_bytes,
        )
        discovered = discovered_files_from_documents(documents)
        files_discovered = await project_service.replace_project_files(
            session,
            project_id,
            discovered,
        )
        chunks_created = await indexing_service.index_project_files(
            session,
            project_id,
        )
        embeddings_created = await embedding_service.embed_project_chunks(
            session,
            project_id,
        )
        return {
            "project_id": project_id,
            "files_discovered": files_discovered,
            "chunks_created": chunks_created,
            "embeddings_created": embeddings_created,
            "ingestion_status": "completed",
        }

    @staticmethod
    def _failed_result(project_id: uuid.UUID) -> dict[str, object]:
        return {
            "project_id": project_id,
            "files_discovered": 0,
            "chunks_created": 0,
            "embeddings_created": 0,
            "ingestion_status": "failed",
        }


ingestion_pipeline = IngestionPipeline()
