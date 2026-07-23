import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ProjectSource


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
