from pathlib import Path

import pytest

from app.ingestion.base import IngestionError
from app.ingestion.extractors.code_extractor import CodeExtractor
from app.ingestion.importers.git_importer import (
    GitImporter,
    validate_git_remote_url,
)
from app.ingestion.models import GitSource
from app.indexing.extraction import cleanup_directory


@pytest.mark.parametrize(
    ("url", "message"),
    [
        ("", "Git URL is required."),
        ("ftp://github.com/user/repo", "http or https"),
        ("https://github.com", "repository path"),
        ("not-a-url", "http or https"),
    ],
)
def test_validate_git_remote_url_rejects_invalid(url: str, message: str) -> None:
    with pytest.raises(IngestionError, match=message):
        validate_git_remote_url(url)


def test_validate_git_remote_url_accepts_https_repo() -> None:
    normalized = validate_git_remote_url("https://github.com/user/repository.git/")
    assert normalized == "https://github.com/user/repository.git"


def test_git_importer_produces_extracted_documents(tmp_path: Path) -> None:
    def mock_clone(url: str, destination: Path) -> None:
        assert url == "https://github.com/user/repo"
        destination.mkdir(parents=True)
        (destination / "src" / "app.py").parent.mkdir(parents=True, exist_ok=True)
        (destination / "src" / "app.py").write_text("def main():\n    pass\n", encoding="utf-8")
        (destination / "README.md").write_text("# Demo\n", encoding="utf-8")

    importer = GitImporter(workspace_base_dir=tmp_path, clone_fn=mock_clone)
    imported = importer.import_source(
        GitSource(url="https://github.com/user/repo"),
    )

    try:
        documents = CodeExtractor().extract_documents(
            imported,
            max_file_size_bytes=1024 * 1024,
        )
        paths = {document.path for document in documents}
        assert paths == {"README.md", "src/app.py"}
    finally:
        cleanup_directory(imported.workspace_dir)
