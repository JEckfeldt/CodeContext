"""Embed natural-language search queries using the shared embedding provider."""

from app.embeddings.base import EmbeddingProvider
from app.embeddings.provider import get_embedding_provider
from app.retrieval.exceptions import QueryEmbeddingError


async def embed_search_query(
    query: str,
    *,
    provider: EmbeddingProvider | None = None,
) -> list[float]:
    """Return a vector for ``query`` using the configured embedding provider.

    Args:
        query: User search text.
        provider: Optional provider override (used in tests).

    Raises:
        QueryEmbeddingError: If the query is empty or embedding is unavailable.
    """
    trimmed = query.strip()
    if not trimmed:
        raise QueryEmbeddingError("Search query must not be empty.")

    embedding_provider = provider or get_embedding_provider()
    if embedding_provider is None:
        raise QueryEmbeddingError(
            "Embedding provider is not configured. "
            "Set EMBEDDING_ENABLED=true and OPENAI_API_KEY."
        )

    vectors = await embedding_provider.embed_texts([trimmed])
    if not vectors:
        raise QueryEmbeddingError("Embedding provider returned no vectors.")

    return vectors[0]
