import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ProjectSource
from app.services import project_service


async def record_project_source(
    session: AsyncSession,
    project_id: uuid.UUID,
    *,
    source_type: str,
    source_name: str,
    source_url: str | None = None,
) -> ProjectSource:
    source = ProjectSource(
        project_id=project_id,
        source_type=source_type,
        source_name=source_name,
        source_url=source_url,
    )
    session.add(source)
    await session.commit()
    await session.refresh(source)
    return source


async def list_project_sources(
    session: AsyncSession,
    project_id: uuid.UUID,
    *,
    user_id: uuid.UUID,
) -> list[ProjectSource]:
    """List import sources for an owned project."""
    await project_service.get_project_for_user(session, project_id, user_id)
    result = await session.scalars(
        select(ProjectSource)
        .where(ProjectSource.project_id == project_id)
        .order_by(ProjectSource.created_at.asc())
    )
    return list(result.all())
