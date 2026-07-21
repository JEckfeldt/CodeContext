"""Embedding column type and dimension defaults."""

from __future__ import annotations

from sqlalchemy import JSON
from sqlalchemy.types import TypeDecorator

DEFAULT_EMBEDDING_DIMENSIONS = 1536
HNSW_INDEX_NAME = "ix_code_chunks_embedding_hnsw"
VECTOR_COSINE_OPS = "vector_cosine_ops"


class EmbeddingColumn(TypeDecorator):
    """PostgreSQL pgvector column; JSON array fallback for SQLite tests."""

    cache_ok = True
    impl = JSON

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            from pgvector.sqlalchemy import Vector

            return dialect.type_descriptor(Vector(DEFAULT_EMBEDDING_DIMENSIONS))
        return dialect.type_descriptor(JSON())
