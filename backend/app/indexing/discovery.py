from dataclasses import dataclass

from pathlib import Path

from app.ingestion.extractors.code_extractor import extract_documents_from_directory
from app.ingestion.models import ExtractedDocument


@dataclass(frozen=True)
class DiscoveredFile:
    path: str
    filename: str
    extension: str | None
    language: str | None
    size: int
    content: str


def discovered_file_from_document(document: ExtractedDocument) -> DiscoveredFile:
    return DiscoveredFile(
        path=document.path,
        filename=document.filename,
        extension=document.extension,
        language=document.language,
        size=document.size,
        content=document.content,
    )


def discover_files(
    root: Path,
    *,
    max_file_size_bytes: int,
) -> list[DiscoveredFile]:
    documents = extract_documents_from_directory(
        root,
        max_file_size_bytes=max_file_size_bytes,
    )
    return [discovered_file_from_document(document) for document in documents]
