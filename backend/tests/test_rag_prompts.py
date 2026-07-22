from app.prompts import (
    DEFAULT_RAG_CONTEXT_LIMITS,
    RagContextLimits,
    build_rag_messages,
    format_retrieved_chunks,
    select_rag_context_chunks,
    truncate_snippet,
)
from app.retrieval.types import ChunkSearchResult


def _sample_chunk(
    *,
    file_path: str = "src/auth.py",
    content: str = "def login():\n    pass",
    start_line: int = 1,
    end_line: int = 2,
    symbol_name: str | None = "login",
    similarity: float = 0.9,
) -> ChunkSearchResult:
    return ChunkSearchResult(
        file_path=file_path,
        content=content,
        start_line=start_line,
        end_line=end_line,
        symbol_name=symbol_name,
        similarity=similarity,
    )


def test_format_retrieved_chunks_numbers_blocks() -> None:
    chunks = [
        _sample_chunk(file_path="a.py", content="alpha", start_line=1, end_line=1),
        _sample_chunk(file_path="b.py", content="beta", start_line=3, end_line=5),
    ]
    context = format_retrieved_chunks(chunks)

    assert "### [1] a.py · line 1" in context
    assert "### [2] b.py · lines 3–5" in context
    assert "alpha" in context
    assert "beta" in context
    assert context.index("[1]") < context.index("[2]")


def test_format_retrieved_chunks_includes_symbol() -> None:
    context = format_retrieved_chunks([_sample_chunk()])
    assert "symbol: login" in context


def test_truncate_snippet_by_lines_and_chars() -> None:
    long_lines = "\n".join(f"line {index}" for index in range(30))
    truncated = truncate_snippet(long_lines, max_lines=3, max_chars=10_000)
    assert truncated.startswith("line 0\nline 1\nline 2")
    assert truncated.endswith("…")

    long_line = "x" * 200
    truncated_chars = truncate_snippet(long_line, max_lines=100, max_chars=50)
    assert len(truncated_chars) <= 52
    assert truncated_chars.endswith("…")


def test_format_retrieved_chunks_respects_total_char_budget() -> None:
    chunks = [
        _sample_chunk(file_path=f"{index}.py", content="x" * 500)
        for index in range(5)
    ]
    limits = RagContextLimits(
        max_chunks=5,
        max_chunk_lines=100,
        max_chunk_chars=500,
        max_total_context_chars=900,
    )
    context = format_retrieved_chunks(chunks, limits)
    included = select_rag_context_chunks(chunks, limits)
    assert len(included) >= 1
    assert "[5]" not in context
    assert context.count("### [") == len(included)


def test_select_rag_context_chunks_aligns_with_prompt_headers() -> None:
    import re

    chunks = [
        _sample_chunk(file_path=f"{index}.py", content="y" * 400)
        for index in range(4)
    ]
    limits = RagContextLimits(max_total_context_chars=1200)
    included = select_rag_context_chunks(chunks, limits)
    context = format_retrieved_chunks(chunks, limits)
    headers = re.findall(r"### \[(\d+)\]", context)
    assert len(included) == len(headers)
    assert headers == [str(index) for index in range(1, len(included) + 1)]


def test_empty_retrieval_context_message() -> None:
    context = format_retrieved_chunks([])
    assert "No code snippets were retrieved" in context


def test_build_rag_messages_structure() -> None:
    messages = build_rag_messages("Where is auth?", [_sample_chunk()])

    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert "ONLY using information" in messages[0]["content"]
    assert "## Question" in messages[1]["content"]
    assert "Where is auth?" in messages[1]["content"]
    assert "## Retrieved code" in messages[1]["content"]
    assert "### [1]" in messages[1]["content"]


def test_build_rag_messages_empty_retrieval() -> None:
    messages = build_rag_messages("Anything?", [])
    user_content = messages[1]["content"]
    assert "No code snippets were retrieved" in user_content


def test_build_rag_messages_is_deterministic() -> None:
    chunks = [
        _sample_chunk(file_path="x.py", content="same"),
        _sample_chunk(file_path="y.py", content="content"),
    ]
    first = build_rag_messages("Explain x", chunks, DEFAULT_RAG_CONTEXT_LIMITS)
    second = build_rag_messages("Explain x", chunks, DEFAULT_RAG_CONTEXT_LIMITS)
    assert first == second
