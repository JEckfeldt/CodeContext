import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.retrieval.exceptions import QueryEmbeddingError, SemanticSearchUnavailableError
from app.retrieval.query_embedding import embed_search_query
from app.retrieval.retrieval_service import search_similar_chunks
from app.retrieval.types import ChunkSearchResult


class MockEmbeddingProvider:
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [[0.0] * 1536 for _ in texts]


@pytest.mark.asyncio
async def test_embed_search_query_rejects_empty_string() -> None:
    with pytest.raises(QueryEmbeddingError):
        await embed_search_query("   ", provider=MockEmbeddingProvider())


@pytest.mark.asyncio
async def test_embed_search_query_uses_provider() -> None:
    provider = MockEmbeddingProvider()
    vector = await embed_search_query("auth middleware", provider=provider)
    assert len(vector) == 1536


@pytest.mark.asyncio
async def test_search_similar_chunks_maps_rows(db_session: AsyncSession) -> None:
    project_id = uuid.uuid4()
    mock_result = MagicMock()
    mock_result.mappings.return_value.all.return_value = [
        {
            "file_path": "src/auth.py",
            "content": "def login(): pass",
            "start_line": 1,
            "end_line": 1,
            "symbol_name": "login",
            "similarity": 0.91,
        }
    ]

    connection = AsyncMock()
    connection.dialect.name = "postgresql"
    db_session.connection = AsyncMock(return_value=connection)
    db_session.execute = AsyncMock(return_value=mock_result)

    async def fake_get_project(session, pid):
        return MagicMock()

    import app.services.project_service as project_service_module

    original = project_service_module.get_project
    project_service_module.get_project = fake_get_project
    try:
        hits = await search_similar_chunks(
            db_session,
            project_id,
            "how does login work",
            provider=MockEmbeddingProvider(),
        )
    finally:
        project_service_module.get_project = original

    assert len(hits) == 1
    assert hits[0] == ChunkSearchResult(
        file_path="src/auth.py",
        content="def login(): pass",
        start_line=1,
        end_line=1,
        symbol_name="login",
        similarity=0.91,
    )


@pytest.mark.asyncio
async def test_search_similar_chunks_requires_postgresql(db_session: AsyncSession) -> None:
    connection = AsyncMock()
    connection.dialect.name = "sqlite"
    db_session.connection = AsyncMock(return_value=connection)

    import app.services.project_service as project_service_module

    original = project_service_module.get_project
    project_service_module.get_project = AsyncMock(return_value=MagicMock())
    try:
        with pytest.raises(SemanticSearchUnavailableError):
            await search_similar_chunks(
                db_session,
                uuid.uuid4(),
                "query",
                provider=MockEmbeddingProvider(),
            )
    finally:
        project_service_module.get_project = original
