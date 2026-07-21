"""Errors raised during semantic retrieval."""


class RetrievalError(Exception):
    """Base error for retrieval failures."""


class QueryEmbeddingError(RetrievalError):
    """The query could not be embedded (missing provider or provider failure)."""


class SemanticSearchUnavailableError(RetrievalError):
    """Vector search cannot run in the current environment (e.g. non-PostgreSQL)."""
