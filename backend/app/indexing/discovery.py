from dataclasses import dataclass
from pathlib import Path, PurePosixPath

import pathspec

from app.indexing.constants import DEFAULT_IGNORED_DIR_NAMES, SUPPORTED_EXTENSIONS


@dataclass(frozen=True)
class DiscoveredFile:
    path: str
    filename: str
    extension: str | None
    language: str | None
    size: int
    content: str


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


def _should_skip_directory(name: str) -> bool:
    return name in DEFAULT_IGNORED_DIR_NAMES


def _is_ignored_path(relative_path: str, specs: list[pathspec.PathSpec]) -> bool:
    normalized = PurePosixPath(relative_path).as_posix()
    return any(spec.match_file(normalized) for spec in specs)


def discover_files(
    root: Path,
    *,
    max_file_size_bytes: int,
) -> list[DiscoveredFile]:
    gitignore_specs = _load_gitignore_specs(root)
    discovered: list[DiscoveredFile] = []

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
        discovered.append(
            DiscoveredFile(
                path=relative,
                filename=path.name,
                extension=extension.lstrip(".") if extension else None,
                language=SUPPORTED_EXTENSIONS[extension],
                size=file_size,
                content=content,
            )
        )

    discovered.sort(key=lambda item: item.path)
    return discovered


def should_skip_directory(name: str) -> bool:
    return _should_skip_directory(name)
