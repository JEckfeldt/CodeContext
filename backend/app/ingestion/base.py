from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from app.ingestion.models import ExtractedDocument, ImportedFilesystemTree, SourceType

TSource = TypeVar("TSource")
TImported = TypeVar("TImported")


class IngestionError(Exception):
    """Base error for the ingestion pipeline (invalid source, extraction failure)."""


class BaseImporter(ABC, Generic[TSource, TImported]):
    """
    Imports raw input into a normalized intermediate form.

    Register new importers in ``app.ingestion.service.get_importer`` (e.g.
    GitImporter → ImportedFilesystemTree, PdfImporter → future document bundle).
    """

    source_type: SourceType

    @abstractmethod
    def import_source(self, source: TSource) -> TImported:
        raise NotImplementedError


class BaseExtractor(ABC):
    """
    Turns importer output into ``ExtractedDocument`` instances.

    Tree importers typically pair with ``CodeExtractor``; single-file importers
    can add dedicated extractors (PdfImporter + PdfExtractor) without changing
    chunking or persistence.
    """

    @abstractmethod
    def extract_documents(
        self,
        imported: ImportedFilesystemTree,
        *,
        max_file_size_bytes: int,
    ) -> list[ExtractedDocument]:
        raise NotImplementedError
