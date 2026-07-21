"""Semantic search over indexed code chunks using pgvector."""

from __future__ import annotations

import uuid
from typing import Any, Mapping

from pgvector.sqlalchemy import Vector
from sqlalchemy import bindparam, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.vector import DEFAULT_EMBEDDING_DIMENSIONS
from app.embeddings.base import EmbeddingProvider
from app.retrieval.exceptions import QueryEmbeddingError, SemanticSearchUnavailableError
from app.retrieval.query_embedding import embed_search_query
from app.retrieval.types import ChunkSearchResult
from app.services import project_service

DEFAULT_TOP_K = 10

_SIMILARITY_SEARCH_SQL = text(
    """
    SELECT
        f.path AS file_path,
        c.content AS content,
        c.start_line AS start_line,
        c.end_line AS end_line,
        c.symbol_name AS symbol_name,
        (1 - (c.embedding <=> :query_embedding)) AS similarity
    FROM code_chunks c
    INNER JOIN files f ON f.id = c.file_id
    WHERE c.project_id = :project_id
      AND c.embedding IS NOT NULL
    ORDER BY c.embedding <=> :query_embedding
    LIMIT :result_limit
    """
).bindparams(bindparam("query_embedding", type_=Vector(DEFAULT_EMBEDDING_DIMENSIONS)))


async def _require_postgresql(session: AsyncSession) -> None:
    """Ensure the session is backed by PostgreSQL (pgvector search)."""
    connection = await session.connection()
    if connection.dialect.name != "postgresql":
        raise SemanticSearchUnavailableError(
            "Semantic search requires PostgreSQL with pgvector."
        )


async def search_similar_chunks(
    session: AsyncSession,
    project_id: uuid.UUID,
    query: str,
    *,
    limit: int = DEFAULT_TOP_K,
    provider: EmbeddingProvider | None = None,
) -> list[ChunkSearchResult]:
    """Find the most similar indexed chunks to a natural-language query.

    Embeds the query with the same embedding provider used at index time, then
    ranks ``code_chunks`` by cosine distance (pgvector ``<=>``) scoped to
    ``project_id``.

    Args:
        session: Async database session.
        project_id: Project whose embedded chunks to search.
        query: Natural-language search text.
        limit: Maximum number of hits (default 10).
        provider: Optional embedding provider override (tests).

    Returns:
        Up to ``limit`` results ordered by descending similarity.

    Raises:
        ProjectNotFoundError: If the project does not exist.
        QueryEmbeddingError: If the query cannot be embedded.
        SemanticSearchUnavailableError: If the database is not PostgreSQL.
        ValueError: If ``limit`` is less than 1.
    """
    if limit < 1:
        raise ValueError("limit must be at least 1")

    await project_service.get_project(session, project_id)
    await _require_postgresql(session)

    query_embedding = await embed_search_query(query, provider=provider)

    result = await session.execute(
        _SIMILARITY_SEARCH_SQL,
        {
            "project_id": project_id,
            "query_embedding": query_embedding,
            "result_limit": limit,
        },
    )
    rows = result.mappings().all()

    return [_mapping_row_to_result(row) for row in rows]


def _mapping_row_to_result(row: Mapping[str, Any]) -> ChunkSearchResult:
    """Convert a SQLAlchemy row mapping to a ``ChunkSearchResult``."""
    return ChunkSearchResult(
        file_path=row["file_path"],
        content=row["content"],
        start_line=row["start_line"],
        end_line=row["end_line"],
        symbol_name=row["symbol_name"],
        similarity=float(row["similarity"]),
    )
