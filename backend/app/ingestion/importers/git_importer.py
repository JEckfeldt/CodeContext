from __future__ import annotations

import subprocess
from pathlib import Path
from urllib.parse import urlparse

from collections.abc import Callable

from app.indexing.extraction import cleanup_directory, create_temp_extraction_dir
from app.ingestion.base import BaseImporter, IngestionError
from app.ingestion.models import GitSource, ImportedFilesystemTree, SourceType


def validate_git_remote_url(url: str) -> str:
    """Validate a public HTTP(S) Git remote URL."""
    normalized = url.strip()
    if not normalized:
        raise IngestionError("Git URL is required.")

    parsed = urlparse(normalized)
    if parsed.scheme not in {"http", "https"}:
        raise IngestionError("Git URL must use http or https.")
    if not parsed.netloc:
        raise IngestionError("Git URL is missing a host.")
    if not parsed.path or parsed.path in {"/", ""}:
        raise IngestionError("Git URL must include a repository path.")

    return normalized.rstrip("/")


def clone_git_repository(url: str, destination: Path) -> None:
    """Shallow-clone a remote repository into ``destination``."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        ["git", "clone", "--depth", "1", url, str(destination)],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        message = (completed.stderr or completed.stdout or "git clone failed.").strip()
        raise IngestionError(message)


class GitImporter(BaseImporter[GitSource, ImportedFilesystemTree]):
    """
    Clones a public Git remote into a temporary directory tree.

    Output is consumed by ``CodeExtractor`` using the same rules as ZIP imports.
    """

    source_type = SourceType.GIT

    def __init__(
        self,
        *,
        workspace_base_dir: Path,
        clone_fn: Callable[[str, Path], None] | None = None,
    ) -> None:
        self._workspace_base_dir = workspace_base_dir
        self._clone_fn = clone_fn

    def import_source(self, source: GitSource) -> ImportedFilesystemTree:
        validated_url = validate_git_remote_url(source.url)
        workspace_dir = create_temp_extraction_dir(self._workspace_base_dir)
        clone_root = workspace_dir / "repo"
        clone = self._clone_fn if self._clone_fn is not None else clone_git_repository

        try:
            clone(validated_url, clone_root)
        except IngestionError:
            cleanup_directory(workspace_dir)
            raise

        if not clone_root.is_dir():
            cleanup_directory(workspace_dir)
            raise IngestionError("Git clone did not produce a repository directory.")

        return ImportedFilesystemTree(
            root=clone_root,
            source_type=SourceType.GIT,
            workspace_dir=workspace_dir,
        )
