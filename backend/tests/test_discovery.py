import io
import zipfile
from pathlib import Path

import pytest

from app.indexing.discovery import discover_files


def _create_repo(root: Path) -> None:
    (root / "src").mkdir()
    (root / "src" / "main.py").write_text("print('hello')\n", encoding="utf-8")
    (root / "README.md").write_text("# Demo", encoding="utf-8")
    (root / "node_modules").mkdir()
    (root / "node_modules" / "ignored.js").write_text("ignored", encoding="utf-8")
    (root / "binary.bin").write_bytes(b"\x00\x01\x02")
    (root / ".gitignore").write_text("ignored.txt\n", encoding="utf-8")
    (root / "ignored.txt").write_text("skip me", encoding="utf-8")


def test_discover_files_skips_unsupported_and_binary(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    _create_repo(repo_root)

    discovered = discover_files(repo_root, max_file_size_bytes=1024 * 1024)
    paths = {item.path for item in discovered}

    assert "src/main.py" in paths
    assert "README.md" in paths
    assert "node_modules/ignored.js" not in paths
    assert "binary.bin" not in paths
    assert "ignored.txt" not in paths


def test_discover_files_respects_max_size(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / "large.py").write_text("x" * 200, encoding="utf-8")

    discovered = discover_files(repo_root, max_file_size_bytes=50)
    assert discovered == []
