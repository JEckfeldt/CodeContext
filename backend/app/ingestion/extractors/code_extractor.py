from __future__ import annotations

from pathlib import Path, PurePosixPath

import pathspec

from app.indexing.constants import DEFAULT_IGNORED_DIR_NAMES, SUPPORTED_EXTENSIONS
from app.ingestion.base import BaseExtractor
from app.ingestion.models import ExtractedDocument, ImportedFilesystemTree


class CodeExtractor(BaseExtractor):
    """
    Walks a filesystem tree and emits text/source documents.

    Used after ZIP and Git imports. Future ``MarkdownImporter`` / ``TextImporter``
    may bypass this extractor and yield ``ExtractedDocument`` directly from the
    importer stage when no directory walk is required.
    """

    def extract_documents(
        self,
        imported: ImportedFilesystemTree,
        *,
        max_file_size_bytes: int,
    ) -> list[ExtractedDocument]:
        return extract_documents_from_directory(
            imported.root,
            max_file_size_bytes=max_file_size_bytes,
        )


def extract_documents_from_directory(
    root: Path,
    *,
    max_file_size_bytes: int,
) -> list[ExtractedDocument]:
    gitignore_specs = _load_gitignore_specs(root)
    documents: list[ExtractedDocument] = []

    for path in root.rglob("*"):
        if not path.is_file():
            continue

        relative = path.relative_to(root).as_posix()
        if any(part in DEFAULT_IGNORED_DIR_NAMES for part in path.parts):
            continue
        if _is_ignored_path(relative, gitignore_specs):
            continue

        extension = path.suffix.lower() or None
        if extension not in SUPPORTED_EXTENSIONS:
            continue

        file_size = path.stat().st_size
        if file_size > max_file_size_bytes:
            continue

        raw = path.read_bytes()
        if _is_binary(raw):
            continue

        content = raw.decode("utf-8")
        documents.append(
            ExtractedDocument.from_filesystem_entry(
                path=relative,
                content=content,
                language=SUPPORTED_EXTENSIONS[extension],
                extension=extension.lstrip(".") if extension else None,
                size=file_size,
                metadata={"source_root": str(root)},
            )
        )

    documents.sort(key=lambda item: item.path)
    return documents


def _load_gitignore_specs(root: Path) -> list[pathspec.PathSpec]:
    specs: list[pathspec.PathSpec] = []
    for gitignore_path in root.rglob(".gitignore"):
        if any(part in DEFAULT_IGNORED_DIR_NAMES for part in gitignore_path.parts):
            continue
        try:
            patterns = gitignore_path.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        specs.append(pathspec.GitIgnoreSpec.from_lines(patterns))
    return specs


def _is_binary(data: bytes) -> bool:
    if b"\x00" in data:
        return True
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return True
    return False


def _is_ignored_path(relative_path: str, specs: list[pathspec.PathSpec]) -> bool:
    normalized = PurePosixPath(relative_path).as_posix()
    return any(spec.match_file(normalized) for spec in specs)
