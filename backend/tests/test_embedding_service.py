import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, settings
from app.database.vector import DEFAULT_EMBEDDING_DIMENSIONS
from app.embeddings.input_text import build_embedding_input_text
from app.models import CodeChunk, File, Project
from app.services.embedding_service import embed_project_chunks


@pytest.fixture
def enabled_embedding_settings(monkeypatch: pytest.MonkeyPatch) -> Settings:
    updated = settings.model_copy(
        update={
            "embedding_enabled": True,
            "openai_api_key": "test-key",
        }
    )
    monkeypatch.setattr("app.core.config.settings", updated)
    monkeypatch.setattr("app.services.embedding_service.settings", updated)
    monkeypatch.setattr("app.embeddings.provider.settings", updated)
    return updated


class MockEmbeddingProvider:
    def __init__(self) -> None:
        self.calls: list[list[str]] = []

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        self.calls.append(texts)
        return [[0.1] * DEFAULT_EMBEDDING_DIMENSIONS for _ in texts]


async def _seed_chunk(session: AsyncSession) -> tuple[Project, CodeChunk]:
    project = Project(name="Embed Test")
    session.add(project)
    await session.flush()

    file = File(
        project_id=project.id,
        path="src/auth.py",
        filename="auth.py",
        extension="py",
        language="python",
        size=20,
        content="def login():\n    pass\n",
    )
    session.add(file)
    await session.flush()

    chunk = CodeChunk(
        file_id=file.id,
        project_id=project.id,
        chunk_index=0,
        start_line=1,
        end_line=2,
        content="def login():\n    pass\n",
        language="python",
        chunk_kind="function",
        symbol_name="login",
    )
    session.add(chunk)
    await session.commit()
    await session.refresh(chunk)
    return project, chunk


@pytest.mark.asyncio
async def test_build_embedding_input_text_includes_metadata() -> None:
    text = build_embedding_input_text(
        file_path="src/auth.py",
        language="python",
        symbol_name="login",
        content="def login():\n    pass\n",
    )
    assert "file: src/auth.py" in text
    assert "language: python" in text
    assert "symbol: login" in text
    assert "def login():" in text


@pytest.mark.asyncio
async def test_embed_project_chunks_updates_chunks(
    db_session: AsyncSession,
    enabled_embedding_settings: Settings,
) -> None:
    project, chunk = await _seed_chunk(db_session)
    provider = MockEmbeddingProvider()

    embedded = await embed_project_chunks(
        db_session,
        project.id,
        provider=provider,
    )
    assert embedded == 1
    assert len(provider.calls) == 1

    await db_session.refresh(chunk)
    assert chunk.embedding is not None
    assert len(chunk.embedding) == DEFAULT_EMBEDDING_DIMENSIONS
    assert chunk.embedding_model == enabled_embedding_settings.embedding_model
    assert chunk.embedded_at is not None
    assert chunk.content == "def login():\n    pass\n"


@pytest.mark.asyncio
async def test_embed_project_chunks_skips_already_embedded(
    db_session: AsyncSession,
    enabled_embedding_settings: Settings,
) -> None:
    project, _chunk = await _seed_chunk(db_session)
    provider = MockEmbeddingProvider()

    first = await embed_project_chunks(db_session, project.id, provider=provider)
    second = await embed_project_chunks(db_session, project.id, provider=provider)

    assert first == 1
    assert second == 0
    assert len(provider.calls) == 1


@pytest.mark.asyncio
async def test_embed_project_chunks_disabled_by_default(
    db_session: AsyncSession,
) -> None:
    project, _chunk = await _seed_chunk(db_session)
    provider = MockEmbeddingProvider()

    embedded = await embed_project_chunks(
        db_session,
        project.id,
        provider=provider,
    )
    assert embedded == 0
    assert provider.calls == []
