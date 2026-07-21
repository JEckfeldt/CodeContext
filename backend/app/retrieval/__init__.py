"""Semantic retrieval over code chunk embeddings (Phase 3)."""

from app.retrieval.exceptions import (
    QueryEmbeddingError,
    RetrievalError,
    SemanticSearchUnavailableError,
)
from app.retrieval.retrieval_service import DEFAULT_TOP_K, search_similar_chunks
from app.retrieval.types import ChunkSearchResult

__all__ = [
    "ChunkSearchResult",
    "DEFAULT_TOP_K",
    "QueryEmbeddingError",
    "RetrievalError",
    "SemanticSearchUnavailableError",
    "search_similar_chunks",
]
