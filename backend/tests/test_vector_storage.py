import os
from pathlib import Path

import pytest
from sqlalchemy import inspect, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.vector import DEFAULT_EMBEDDING_DIMENSIONS
from app.models import CodeChunk, File, Project


@pytest.mark.asyncio
async def test_sqlite_embedding_column_uses_json(async_engine) -> None:
    async with async_engine.connect() as connection:

        def read_column_type(sync_connection):
            inspector = inspect(sync_connection)
            columns = inspector.get_columns("code_chunks")
            embedding_column = next(
                column for column in columns if column["name"] == "embedding"
            )
            return type(embedding_column["type"]).__name__

        column_type = await connection.run_sync(read_column_type)

    assert column_type == "JSON"


@pytest.mark.asyncio
async def test_sqlite_embedding_roundtrip_as_list(
    db_session: AsyncSession,
) -> None:
    project = Project(name="Vector SQLite")
    db_session.add(project)
    await db_session.flush()

    file = File(
        project_id=project.id,
        path="main.py",
        filename="main.py",
        extension="py",
        language="python",
        size=10,
        content="print(1)\n",
    )
    db_session.add(file)
    await db_session.flush()

    vector = [0.25] * DEFAULT_EMBEDDING_DIMENSIONS
    chunk = CodeChunk(
        file_id=file.id,
        project_id=project.id,
        chunk_index=0,
        start_line=1,
        end_line=1,
        content="print(1)\n",
        language="python",
        chunk_kind="text_block",
        embedding=vector,
        embedding_model="test-model",
    )
    db_session.add(chunk)
    await db_session.commit()

    result = await db_session.scalar(
        select(CodeChunk).where(CodeChunk.project_id == project.id)
    )
    assert result is not None
    assert isinstance(result.embedding, list)
    assert len(result.embedding) == DEFAULT_EMBEDDING_DIMENSIONS
    assert result.embedding[0] == pytest.approx(0.25)


INTEGRATION_DATABASE_URL = os.getenv("CODECONTEXT_INTEGRATION_DATABASE_URL")


@pytest.mark.integration
@pytest.mark.skipif(
    not INTEGRATION_DATABASE_URL,
    reason="Set CODECONTEXT_INTEGRATION_DATABASE_URL to a PostgreSQL pgvector URL",
)
def test_postgres_hnsw_index_and_cosine_storage(monkeypatch: pytest.MonkeyPatch) -> None:
    from alembic import command
    from alembic.config import Config
    from pgvector.psycopg import register_vector
    import psycopg

    import app.core.config as config_module

    async_url = INTEGRATION_DATABASE_URL
    sync_url = async_url.replace("postgresql+asyncpg://", "postgresql://").replace(
        "postgresql+psycopg://",
        "postgresql://",
    )
    monkeypatch.setenv("DATABASE_URL", async_url)
    monkeypatch.setattr(config_module, "settings", config_module.Settings())

    backend_root = Path(__file__).resolve().parents[1]
    alembic_cfg = Config(str(backend_root / "alembic.ini"))
    command.upgrade(alembic_cfg, "head")

    with psycopg.connect(sync_url) as connection:
        register_vector(connection)
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT indexname
                FROM pg_indexes
                WHERE tablename = 'code_chunks'
                  AND indexname = 'ix_code_chunks_embedding_hnsw'
                """
            )
            assert cursor.fetchone() is not None

            cursor.execute(
                """
                SELECT extname
                FROM pg_extension
                WHERE extname = 'vector'
                """
            )
            assert cursor.fetchone() is not None

            cursor.execute(
                """
                INSERT INTO projects (id, name, created_at, updated_at)
                VALUES (
                    '11111111-1111-1111-1111-111111111111',
                    'Vector Integration',
                    NOW(),
                    NOW()
                )
                ON CONFLICT (id) DO NOTHING
                """
            )
            cursor.execute(
                """
                INSERT INTO files (
                    id, project_id, path, filename, extension, language, size, content, created_at
                )
                VALUES (
                    '22222222-2222-2222-2222-222222222222',
                    '11111111-1111-1111-1111-111111111111',
                    'src/a.py',
                    'a.py',
                    'py',
                    'python',
                    12,
                    'print(1)',
                    NOW()
                )
                ON CONFLICT (id) DO NOTHING
                """
            )

            near = [1.0] + [0.0] * (DEFAULT_EMBEDDING_DIMENSIONS - 1)
            far = [0.0] * (DEFAULT_EMBEDDING_DIMENSIONS - 1) + [1.0]

            cursor.execute(
                """
                INSERT INTO code_chunks (
                    id, file_id, project_id, chunk_index, start_line, end_line,
                    content, language, chunk_kind, embedding, embedding_model, embedded_at, created_at
                )
                VALUES
                (
                    '33333333-3333-3333-3333-333333333333',
                    '22222222-2222-2222-2222-222222222222',
                    '11111111-1111-1111-1111-111111111111',
                    0, 1, 1, 'near', 'python', 'text_block', %s, 'test', NOW(), NOW()
                ),
                (
                    '44444444-4444-4444-4444-444444444444',
                    '22222222-2222-2222-2222-222222222222',
                    '11111111-1111-1111-1111-111111111111',
                    1, 2, 2, 'far', 'python', 'text_block', %s, 'test', NOW(), NOW()
                )
                ON CONFLICT (id) DO NOTHING
                """,
                (near, far),
            )

            cursor.execute(
                """
                SELECT content
                FROM code_chunks
                WHERE project_id = '11111111-1111-1111-1111-111111111111'
                  AND embedding IS NOT NULL
                ORDER BY embedding <=> %s::vector
                LIMIT 1
                """,
                (near,),
            )
            row = cursor.fetchone()
            assert row is not None
            assert row[0] == "near"

        connection.rollback()
