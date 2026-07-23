from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import PurePosixPath

from pypdf import PdfReader

from app.ingestion.base import BaseImporter, IngestionError
from app.ingestion.models import (
    ExtractedDocument,
    FileImportSource,
    SourceType,
    UploadedFilePayload,
)

SUPPORTED_UPLOAD_EXTENSIONS: dict[str, str] = {
    ".md": "markdown",
    ".markdown": "markdown",
    ".txt": "text",
    ".pdf": "pdf",
}


def is_supported_upload_filename(filename: str) -> bool:
    suffix = PurePosixPath(filename).suffix.lower()
    return suffix in SUPPORTED_UPLOAD_EXTENSIONS


def validate_upload_filename(filename: str) -> str:
    name = PurePosixPath(filename).name
    if not name or name in {".", ".."}:
        raise IngestionError("Each upload must have a valid filename.")
    if not is_supported_upload_filename(name):
        supported = ", ".join(sorted(SUPPORTED_UPLOAD_EXTENSIONS))
        raise IngestionError(f"Unsupported file type. Supported extensions: {supported}.")
    return name


def extract_pdf_text(data: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(data))
    except Exception as exc:
        raise IngestionError("Could not read PDF file.") from exc

    parts: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            parts.append(text.strip())

    content = "\n\n".join(parts).strip()
    if not content:
        raise IngestionError("PDF did not contain extractable text.")
    return content


def extract_uploaded_file(
    payload: UploadedFilePayload,
    *,
    max_file_size_bytes: int,
) -> ExtractedDocument:
    path = validate_upload_filename(payload.filename)
    if len(payload.data) > max_file_size_bytes:
        raise IngestionError(f"File {path} exceeds the maximum allowed size.")

    suffix = PurePosixPath(path).suffix.lower()
    language = SUPPORTED_UPLOAD_EXTENSIONS[suffix]

    if suffix == ".pdf":
        content = extract_pdf_text(payload.data)
    else:
        try:
            content = payload.data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise IngestionError(f"File {path} must be UTF-8 text.") from exc
        if not content.strip():
            raise IngestionError(f"File {path} is empty.")

    return ExtractedDocument.from_filesystem_entry(
        path=path,
        content=content,
        language=language,
        extension=suffix.lstrip("."),
        size=len(payload.data),
        metadata={"source_type": SourceType.FILE.value},
    )


class FileImporter(BaseImporter[FileImportSource, list[ExtractedDocument]]):
    """
    Turns uploaded file payloads into ``ExtractedDocument`` instances.

    Skips ``CodeExtractor``; documents feed directly into the shared ingest path.
    """

    source_type = SourceType.FILE

    def __init__(self, *, max_file_size_bytes: int) -> None:
        self._max_file_size_bytes = max_file_size_bytes

    def import_source(self, source: FileImportSource) -> list[ExtractedDocument]:
        if not source.files:
            raise IngestionError("At least one file is required.")

        documents: list[ExtractedDocument] = []
        for payload in source.files:
            documents.append(
                extract_uploaded_file(
                    payload,
                    max_file_size_bytes=self._max_file_size_bytes,
                )
            )
        documents.sort(key=lambda item: item.path)
        return documents
