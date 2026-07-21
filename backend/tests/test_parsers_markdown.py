from app.parsers.markdown_parser import parse_markdown


def test_parse_markdown_splits_by_headings() -> None:
    content = "# Title\n\nIntro line.\n\n## Details\n\nMore text.\n"
    blocks = parse_markdown(content)

    assert len(blocks) == 2
    assert blocks[0].chunk_kind == "markdown_section"
    assert blocks[0].symbol_name == "Title"
    assert blocks[0].start_line == 1
    assert "Intro line." in blocks[0].content
    assert blocks[1].symbol_name == "Details"
    assert "## Details" in blocks[1].content
    assert "More text." in blocks[1].content


def test_parse_markdown_single_section_without_headings() -> None:
    content = "Plain notes without headings.\n"
    blocks = parse_markdown(content)

    assert len(blocks) == 1
    assert blocks[0].chunk_kind == "markdown_section"
    assert blocks[0].symbol_name is None
    assert blocks[0].start_line == 1
    assert blocks[0].end_line == 1
