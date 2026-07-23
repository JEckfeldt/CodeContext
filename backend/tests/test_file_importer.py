import pytest

from app.ingestion.base import IngestionError
from app.ingestion.importers.file_importer import (
    FileImporter,
    validate_upload_filename,
)
from app.ingestion.models import FileImportSource, UploadedFilePayload
from tests.pdf_fixtures import make_text_pdf


@pytest.mark.parametrize(
    "filename",
    ["notes.md", "readme.markdown", "doc.txt"],
)
def test_file_importer_extracts_text_documents(filename: str) -> None:
    content = "# Title\n\nBody text\n" if filename.endswith(".md") or filename.endswith(".markdown") else "Plain text body\n"
    importer = FileImporter(max_file_size_bytes=1024 * 1024)
    documents = importer.import_source(
        FileImportSource(
            files=(
                UploadedFilePayload(
                    filename=filename,
                    data=content.encode("utf-8"),
                ),
            )
        )
    )
    assert len(documents) == 1
    assert documents[0].path == filename
    assert documents[0].content == content
    assert documents[0].language in {"markdown", "text"}


def test_file_importer_extracts_pdf_document() -> None:
    pdf_bytes = make_text_pdf("PDF ingestion test")
    importer = FileImporter(max_file_size_bytes=1024 * 1024)
    documents = importer.import_source(
        FileImportSource(
            files=(
                UploadedFilePayload(filename="paper.pdf", data=pdf_bytes),
            )
        )
    )
    assert len(documents) == 1
    assert documents[0].path == "paper.pdf"
    assert "PDF ingestion test" in documents[0].content
    assert documents[0].language == "pdf"


def test_validate_upload_filename_rejects_unsupported_extension() -> None:
    with pytest.raises(IngestionError, match="Unsupported file type"):
        validate_upload_filename("archive.zip")


def test_file_importer_requires_at_least_one_file() -> None:
    importer = FileImporter(max_file_size_bytes=1024)
    with pytest.raises(IngestionError, match="At least one file"):
        importer.import_source(FileImportSource(files=()))
