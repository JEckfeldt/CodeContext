from __future__ import annotations

from pathlib import Path

from app.indexing.extraction import (
    RepositoryExtractionError,
    create_temp_extraction_dir,
    extract_zip_archive,
)
from app.ingestion.base import BaseImporter, IngestionError
from app.ingestion.models import ImportedFilesystemTree, SourceType, ZipSource


class ZipImporter(BaseImporter[ZipSource, ImportedFilesystemTree]):
    """
    Expands a ZIP archive into a temporary directory tree.

    GitImporter would follow the same pattern: clone into a temp dir and return
    ``ImportedFilesystemTree`` so ``CodeExtractor`` can reuse discovery rules.
    """

    source_type = SourceType.ZIP

    def __init__(self, *, extraction_base_dir: Path) -> None:
        self._extraction_base_dir = extraction_base_dir

    def import_source(self, source: ZipSource) -> ImportedFilesystemTree:
        extraction_dir = create_temp_extraction_dir(self._extraction_base_dir)
        try:
            root = extract_zip_archive(source.archive_path, extraction_dir)
        except RepositoryExtractionError as exc:
            from app.indexing.extraction import cleanup_directory

            cleanup_directory(extraction_dir)
            raise IngestionError(str(exc)) from exc

        return ImportedFilesystemTree(
            root=root,
            source_type=SourceType.ZIP,
            workspace_dir=extraction_dir,
        )
