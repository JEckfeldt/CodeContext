import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.llm.base import ChatMessage
from app.llm.exceptions import LLMCompletionError, LLMUnavailableError
from app.retrieval.exceptions import QueryEmbeddingError, SemanticSearchUnavailableError
from app.retrieval.types import ChunkSearchResult
from app.prompts.rag_context import select_rag_context_chunks
from app.services import assistant_service
from app.services.assistant_service import ask_question


class MockChatProvider:
    def __init__(self, answer: str = "Answer with [1].") -> None:
        self._answer = answer
        self.messages_calls: list[list[ChatMessage]] = []

    async def complete(
        self,
        messages: list[ChatMessage],
        *,
        max_tokens: int | None = None,
    ) -> str:
        self.messages_calls.append(messages)
        return self._answer


def _chunk(file_path: str, *, similarity: float = 0.9) -> ChunkSearchResult:
    return ChunkSearchResult(
        file_path=file_path,
        content=f"content of {file_path}",
        start_line=1,
        end_line=3,
        symbol_name="sym",
        similarity=similarity,
    )


@pytest.mark.asyncio
async def test_ask_question_orchestrates_search_prompt_and_llm(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_id = uuid.uuid4()
    session = AsyncMock()
    chunks = [_chunk("a.py", similarity=0.95), _chunk("b.py", similarity=0.85)]
    search_mock = AsyncMock(return_value=chunks)
    build_mock = MagicMock(
        return_value=[
            {"role": "system", "content": "system"},
            {"role": "user", "content": "user"},
        ]
    )
    mock_provider = MockChatProvider()

    monkeypatch.setattr(assistant_service, "search_similar_chunks", search_mock)
    monkeypatch.setattr(assistant_service, "build_rag_messages", build_mock)

    result = await ask_question(
        session,
        project_id,
        "  Where is auth?  ",
        limit=4,
        provider=mock_provider,
    )

    search_mock.assert_awaited_once_with(
        session,
        project_id,
        "Where is auth?",
        limit=4,
    )
    build_mock.assert_called_once_with(
        "Where is auth?",
        select_rag_context_chunks(chunks),
    )
    assert mock_provider.messages_calls == [
        [
            {"role": "system", "content": "system"},
            {"role": "user", "content": "user"},
        ]
    ]

    assert result.project_id == project_id
    assert result.question == "Where is auth?"
    assert result.answer == "Answer with [1]."
    assert result.retrieved_chunks == chunks
    assert len(result.citations) == 2
    assert result.citations[0].index == 1
    assert result.citations[0].file_path == "a.py"
    assert result.citations[1].index == 2
    assert result.citations[1].file_path == "b.py"
    assert result.citations[0].similarity == pytest.approx(0.95)


@pytest.mark.asyncio
async def test_ask_question_uses_default_retrieval_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    search_mock = AsyncMock(return_value=[])
    monkeypatch.setattr(assistant_service, "search_similar_chunks", search_mock)
    monkeypatch.setattr(
        assistant_service,
        "build_rag_messages",
        lambda question, chunks: [{"role": "user", "content": question}],
    )
    provider = MockChatProvider("ok")

    await ask_question(AsyncMock(), uuid.uuid4(), "hello", provider=provider)

    assert search_mock.await_args.kwargs["limit"] == assistant_service.DEFAULT_TOP_K


@pytest.mark.asyncio
async def test_ask_question_raises_when_llm_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(assistant_service, "search_similar_chunks", AsyncMock(return_value=[]))
    monkeypatch.setattr(
        assistant_service,
        "build_rag_messages",
        lambda question, chunks: [{"role": "user", "content": question}],
    )
    monkeypatch.setattr(assistant_service, "get_chat_provider", lambda: None)

    with pytest.raises(LLMUnavailableError, match="LLM_ENABLED"):
        await ask_question(AsyncMock(), uuid.uuid4(), "hello")


@pytest.mark.asyncio
async def test_ask_question_propagates_retrieval_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    search_mock = AsyncMock(side_effect=QueryEmbeddingError("embed failed"))
    monkeypatch.setattr(assistant_service, "search_similar_chunks", search_mock)

    with pytest.raises(QueryEmbeddingError):
        await ask_question(AsyncMock(), uuid.uuid4(), "hello", provider=MockChatProvider())

    search_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_ask_question_propagates_semantic_search_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    search_mock = AsyncMock(side_effect=SemanticSearchUnavailableError("no postgres"))
    monkeypatch.setattr(assistant_service, "search_similar_chunks", search_mock)

    with pytest.raises(SemanticSearchUnavailableError):
        await ask_question(AsyncMock(), uuid.uuid4(), "hello", provider=MockChatProvider())


@pytest.mark.asyncio
async def test_ask_question_propagates_llm_completion_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(assistant_service, "search_similar_chunks", AsyncMock(return_value=[]))
    monkeypatch.setattr(
        assistant_service,
        "build_rag_messages",
        lambda question, chunks: [{"role": "user", "content": question}],
    )

    class FailingProvider:
        async def complete(self, messages, *, max_tokens=None) -> str:
            raise LLMCompletionError("api down")

    with pytest.raises(LLMCompletionError):
        await ask_question(AsyncMock(), uuid.uuid4(), "hello", provider=FailingProvider())


@pytest.mark.asyncio
async def test_ask_question_citations_preserve_retrieval_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    chunks = [_chunk("first.py"), _chunk("second.py"), _chunk("third.py")]
    monkeypatch.setattr(assistant_service, "search_similar_chunks", AsyncMock(return_value=chunks))
    monkeypatch.setattr(
        assistant_service,
        "build_rag_messages",
        lambda question, retrieved: [{"role": "user", "content": "x"}],
    )

    result = await ask_question(
        AsyncMock(),
        uuid.uuid4(),
        "order test",
        provider=MockChatProvider("done"),
    )

    assert [citation.index for citation in result.citations] == [1, 2, 3]
    assert [citation.file_path for citation in result.citations] == [
        "first.py",
        "second.py",
        "third.py",
    ]


@pytest.mark.asyncio
async def test_ask_question_citations_match_prompt_context_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import re

    from app.prompts.rag_context import RagContextLimits

    limits = RagContextLimits(
        max_chunks=5,
        max_chunk_lines=100,
        max_chunk_chars=500,
        max_total_context_chars=550,
    )
    monkeypatch.setattr(assistant_service, "DEFAULT_RAG_CONTEXT_LIMITS", limits)
    monkeypatch.setattr(
        "app.prompts.rag_context.DEFAULT_RAG_CONTEXT_LIMITS",
        limits,
    )

    large_chunks = [
        ChunkSearchResult(
            file_path=f"src/file_{index}.py",
            content="x" * 500,
            start_line=1,
            end_line=20,
            symbol_name=f"sym_{index}",
            similarity=0.9 - index * 0.01,
        )
        for index in range(5)
    ]
    monkeypatch.setattr(
        assistant_service,
        "search_similar_chunks",
        AsyncMock(return_value=large_chunks),
    )
    provider = MockChatProvider("See [1].")

    result = await ask_question(
        AsyncMock(),
        uuid.uuid4(),
        "large context test",
        provider=provider,
    )

    user_content = provider.messages_calls[0][1]["content"]
    header_indexes = [int(match) for match in re.findall(r"### \[(\d+)\]", user_content)]

    assert len(result.citations) == len(header_indexes)
    assert len(result.citations) < len(large_chunks)
    assert result.citations[0].index == 1
    assert [citation.index for citation in result.citations] == header_indexes
    assert len(result.retrieved_chunks) == len(large_chunks)
