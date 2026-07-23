from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path, PurePosixPath
from typing import Any

from app.models import File


class SourceType(str, Enum):
    """Identifies how project content enters the ingestion pipeline."""

    ZIP = "zip"
    GIT = "git"
    FILE = "file"
    PDF = "pdf"
    MARKDOWN = "markdown"
    TEXT = "text"


@dataclass(frozen=True)
class ExtractedDocument:
    """
    Normalized unit of indexed project content.

    Chunking and embedding operate on these objects rather than on ZIP-specific
    file records so future importers (Git, PDF, single files) share one path.
    """

    path: str
    content: str
    language: str | None = None
    title: str | None = None
    filename: str = ""
    extension: str | None = None
    size: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_filesystem_entry(
        cls,
        *,
        path: str,
        content: str,
        language: str | None,
        extension: str | None,
        size: int,
        metadata: dict[str, Any] | None = None,
    ) -> ExtractedDocument:
        posix = PurePosixPath(path)
        return cls(
            path=path,
            title=path,
            content=content,
            language=language,
            filename=posix.name,
            extension=extension,
            size=size,
            metadata=metadata or {},
        )

    @classmethod
    def from_persisted_file(cls, file: File) -> ExtractedDocument:
        return cls(
            path=file.path,
            title=file.path,
            content=file.content,
            language=file.language,
            filename=file.filename,
            extension=file.extension,
            size=file.size,
            metadata={"file_id": str(file.id)},
        )


@dataclass(frozen=True)
class ZipSource:
    source_type: SourceType = SourceType.ZIP
    archive_path: Path = field(default_factory=Path)


@dataclass(frozen=True)
class ImportedFilesystemTree:
    """
    Result of importers that materialize content as a directory tree (ZIP, Git).

    Tree-based extractors (e.g. CodeExtractor) walk ``root`` and emit documents.
    ``workspace_dir`` is the temporary directory owned by the importer (for cleanup).
    """

    root: Path
    source_type: SourceType
    workspace_dir: Path
