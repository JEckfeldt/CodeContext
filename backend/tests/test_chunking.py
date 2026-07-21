import pytest

from app.indexing.chunking import (
    DEFAULT_CHUNK_MAX_CHARS,
    TEXT_BLOCK_KIND,
    chunk_file_content,
)


def test_chunk_file_content_empty() -> None:
    assert chunk_file_content("", "python") == []


def test_chunk_file_content_single_small_line() -> None:
    drafts = chunk_file_content("print('hi')\n", "python")
    assert len(drafts) == 1
    assert drafts[0].chunk_index == 0
    assert drafts[0].start_line == 1
    assert drafts[0].end_line == 1
    assert drafts[0].language == "python"
    assert drafts[0].chunk_kind == TEXT_BLOCK_KIND
    assert "print('hi')" in drafts[0].content


def test_chunk_file_content_preserves_line_numbers_across_chunks() -> None:
    lines = [f"line {index}\n" for index in range(1, 6)]
    content = "".join(lines)
    drafts = chunk_file_content(content, "python", max_chars=12)

    assert len(drafts) >= 2
    assert drafts[0].start_line == 1
    assert drafts[0].end_line >= 1
    assert drafts[-1].end_line == 5
    for index, draft in enumerate(drafts):
        assert draft.chunk_index == index
        assert len(draft.content) <= 12


def test_chunk_file_content_splits_long_line() -> None:
    long_line = "x" * 50 + "\n"
    drafts = chunk_file_content(long_line, None, max_chars=20)

    assert len(drafts) == 3
    assert all(draft.start_line == 1 and draft.end_line == 1 for draft in drafts)
    assert sum(len(draft.content) for draft in drafts) == len(long_line)


def test_chunk_file_content_respects_default_max_size() -> None:
    content = "a" * (DEFAULT_CHUNK_MAX_CHARS + 1)
    drafts = chunk_file_content(content, "markdown")

    assert len(drafts) == 2
    assert len(drafts[0].content) == DEFAULT_CHUNK_MAX_CHARS
    assert len(drafts[1].content) == 1
