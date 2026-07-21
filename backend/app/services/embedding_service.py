import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.embeddings.base import EmbeddingProvider
from app.embeddings.input_text import build_embedding_input_text
from app.embeddings.provider import get_embedding_provider
from app.models import CodeChunk, File
from app.services import project_service


async def embed_project_chunks(
    session: AsyncSession,
    project_id: uuid.UUID,
    *,
    provider: EmbeddingProvider | None = None,
) -> int:
    if not settings.embedding_enabled:
        return 0

    await project_service.get_project(session, project_id)
    embedding_provider = provider or get_embedding_provider()
    if embedding_provider is None:
        return 0

    result = await session.execute(
        select(CodeChunk, File.path)
        .join(File, File.id == CodeChunk.file_id)
        .where(
            CodeChunk.project_id == project_id,
            CodeChunk.embedded_at.is_(None),
        )
        .order_by(CodeChunk.id.asc())
    )
    pending = list(result.all())
    if not pending:
        return 0

    embedded_count = 0
    batch_size = max(1, settings.embedding_batch_size)
    embedded_at = datetime.now(timezone.utc)

    for start in range(0, len(pending), batch_size):
        batch = pending[start : start + batch_size]
        texts = [
            build_embedding_input_text(
                file_path=file_path,
                language=chunk.language,
                symbol_name=chunk.symbol_name,
                content=chunk.content,
            )
            for chunk, file_path in batch
        ]
        vectors = await embedding_provider.embed_texts(texts)
        if len(vectors) != len(batch):
            raise RuntimeError("Embedding provider returned an unexpected vector count.")

        for (chunk, _), vector in zip(batch, vectors, strict=True):
            chunk.embedding = vector
            chunk.embedding_model = settings.embedding_model
            chunk.embedded_at = embedded_at
            embedded_count += 1

    await session.commit()
    return embedded_count
