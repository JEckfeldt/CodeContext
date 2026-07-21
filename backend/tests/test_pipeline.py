from app.indexing.chunking import TEXT_BLOCK_KIND
from app.indexing.pipeline import build_file_chunks


def test_build_file_chunks_fallback_for_unknown_language() -> None:
    content = "console.log('hello');\n"
    drafts = build_file_chunks(content, "javascript")

    assert len(drafts) == 1
    assert drafts[0].chunk_kind == TEXT_BLOCK_KIND


def test_build_file_chunks_uses_python_parser() -> None:
    content = "def run():\n    return 1\n"
    drafts = build_file_chunks(content, "python")

    assert len(drafts) == 1
    assert drafts[0].chunk_kind == "function"
    assert drafts[0].start_line == 1


def test_build_file_chunks_uses_markdown_parser() -> None:
    content = "# Hello\n\nBody text.\n"
    drafts = build_file_chunks(content, "markdown")

    assert len(drafts) == 1
    assert drafts[0].chunk_kind == "markdown_section"
