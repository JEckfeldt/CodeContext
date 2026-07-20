import shutil
import tempfile
import zipfile
from pathlib import Path


class RepositoryExtractionError(Exception):
    pass


def extract_zip_archive(archive_path: Path, destination: Path) -> Path:
    if not zipfile.is_zipfile(archive_path):
        raise RepositoryExtractionError("Uploaded file is not a valid ZIP archive.")

    with zipfile.ZipFile(archive_path) as archive:
        archive.extractall(destination)

    return _resolve_repository_root(destination)


def _resolve_repository_root(extracted_dir: Path) -> Path:
    entries = [path for path in extracted_dir.iterdir() if not path.name.startswith("__MACOSX")]
    if len(entries) == 1 and entries[0].is_dir():
        return entries[0]
    return extracted_dir


def create_temp_extraction_dir(base_dir: Path) -> Path:
    base_dir.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix="repo-", dir=base_dir))


def cleanup_directory(path: Path) -> None:
    shutil.rmtree(path, ignore_errors=True)
