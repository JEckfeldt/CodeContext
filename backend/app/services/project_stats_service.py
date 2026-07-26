import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CodeChunk, File, ProjectSource


@dataclass(frozen=True, slots=True)
class ProjectStats:
    file_count: int
    chunk_count: int
    source_count: int
    embedding_count: int
    last_indexed_at: datetime | None


def empty_project_stats() -> ProjectStats:
    return ProjectStats(
        file_count=0,
        chunk_count=0,
        source_count=0,
        embedding_count=0,
        last_indexed_at=None,
    )


async def get_project_stats(
    session: AsyncSession,
    project_id: uuid.UUID,
) -> ProjectStats:
    stats_map = await get_project_stats_batch(session, [project_id])
    return stats_map.get(project_id, empty_project_stats())


async def get_project_stats_batch(
    session: AsyncSession,
    project_ids: list[uuid.UUID],
) -> dict[uuid.UUID, ProjectStats]:
    if not project_ids:
        return {}

    file_counts = await _count_by_project(session, File, File.project_id, project_ids)
    chunk_counts = await _count_by_project(session, CodeChunk, CodeChunk.project_id, project_ids)
    source_counts = await _count_by_project(
        session, ProjectSource, ProjectSource.project_id, project_ids
    )
    embedding_counts = await _count_embeddings_by_project(session, project_ids)
    last_indexed = await _last_indexed_by_project(session, project_ids)

    return {
        project_id: ProjectStats(
            file_count=file_counts.get(project_id, 0),
            chunk_count=chunk_counts.get(project_id, 0),
            source_count=source_counts.get(project_id, 0),
            embedding_count=embedding_counts.get(project_id, 0),
            last_indexed_at=last_indexed.get(project_id),
        )
        for project_id in project_ids
    }


async def _count_by_project(
    session: AsyncSession,
    model,
    project_column,
    project_ids: list[uuid.UUID],
) -> dict[uuid.UUID, int]:
    result = await session.execute(
        select(project_column, func.count())
        .where(project_column.in_(project_ids))
        .group_by(project_column)
    )
    return {project_id: int(count) for project_id, count in result.all()}


async def _count_embeddings_by_project(
    session: AsyncSession,
    project_ids: list[uuid.UUID],
) -> dict[uuid.UUID, int]:
    result = await session.execute(
        select(CodeChunk.project_id, func.count())
        .where(
            CodeChunk.project_id.in_(project_ids),
            CodeChunk.embedded_at.isnot(None),
        )
        .group_by(CodeChunk.project_id)
    )
    return {project_id: int(count) for project_id, count in result.all()}


async def _last_indexed_by_project(
    session: AsyncSession,
    project_ids: list[uuid.UUID],
) -> dict[uuid.UUID, datetime]:
    source_max = await session.execute(
        select(ProjectSource.project_id, func.max(ProjectSource.created_at))
        .where(ProjectSource.project_id.in_(project_ids))
        .group_by(ProjectSource.project_id)
    )
    chunk_created_max = await session.execute(
        select(CodeChunk.project_id, func.max(CodeChunk.created_at))
        .where(CodeChunk.project_id.in_(project_ids))
        .group_by(CodeChunk.project_id)
    )
    chunk_embedded_max = await session.execute(
        select(CodeChunk.project_id, func.max(CodeChunk.embedded_at))
        .where(
            CodeChunk.project_id.in_(project_ids),
            CodeChunk.embedded_at.isnot(None),
        )
        .group_by(CodeChunk.project_id)
    )

    merged: dict[uuid.UUID, datetime] = {}
    for rows in (source_max.all(), chunk_created_max.all(), chunk_embedded_max.all()):
        for project_id, timestamp in rows:
            if timestamp is None:
                continue
            current = merged.get(project_id)
            if current is None or timestamp > current:
                merged[project_id] = timestamp
    return merged
