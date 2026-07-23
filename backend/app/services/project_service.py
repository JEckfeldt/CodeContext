import uuid
from datetime import datetime, timezone

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.indexing.discovery import DiscoveredFile
from app.models import File, Project
from app.schemas import ProjectCreate


class ProjectNotFoundError(Exception):
    pass


async def create_project(
    session: AsyncSession,
    payload: ProjectCreate,
    *,
    user_id: uuid.UUID,
) -> Project:
    project = Project(name=payload.name.strip(), user_id=user_id)
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return project


async def list_projects_for_user(
    session: AsyncSession,
    user_id: uuid.UUID,
) -> list[Project]:
    result = await session.scalars(
        select(Project)
        .where(Project.user_id == user_id)
        .order_by(Project.updated_at.desc())
    )
    return list(result.all())


async def get_project(session: AsyncSession, project_id: uuid.UUID) -> Project:
    project = await session.get(Project, project_id)
    if project is None:
        raise ProjectNotFoundError(f"Project {project_id} was not found.")
    return project


async def get_project_for_user(
    session: AsyncSession,
    project_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Project:
    project = await session.get(Project, project_id)
    if project is None or project.user_id != user_id:
        raise ProjectNotFoundError(f"Project {project_id} was not found.")
    return project


async def list_project_files(
    session: AsyncSession,
    project_id: uuid.UUID,
    *,
    user_id: uuid.UUID,
) -> list[File]:
    await get_project_for_user(session, project_id, user_id)
    result = await session.scalars(
        select(File)
        .where(File.project_id == project_id)
        .order_by(File.path.asc())
    )
    return list(result.all())


async def replace_project_files(
    session: AsyncSession,
    project_id: uuid.UUID,
    discovered_files: list[DiscoveredFile],
    *,
    user_id: uuid.UUID,
) -> int:
    await get_project_for_user(session, project_id, user_id)
    await session.execute(delete(File).where(File.project_id == project_id))

    for discovered in discovered_files:
        session.add(
            File(
                project_id=project_id,
                path=discovered.path,
                filename=discovered.filename,
                extension=discovered.extension,
                language=discovered.language,
                size=discovered.size,
                content=discovered.content,
            )
        )

    await session.execute(
        update(Project)
        .where(Project.id == project_id)
        .values(updated_at=datetime.now(timezone.utc))
    )
    await session.commit()
    return len(discovered_files)


async def upsert_project_files(
    session: AsyncSession,
    project_id: uuid.UUID,
    discovered_files: list[DiscoveredFile],
    *,
    user_id: uuid.UUID,
) -> int:
    await get_project_for_user(session, project_id, user_id)

    for discovered in discovered_files:
        existing = await session.scalar(
            select(File).where(
                File.project_id == project_id,
                File.path == discovered.path,
            )
        )
        if existing is None:
            session.add(
                File(
                    project_id=project_id,
                    path=discovered.path,
                    filename=discovered.filename,
                    extension=discovered.extension,
                    language=discovered.language,
                    size=discovered.size,
                    content=discovered.content,
                )
            )
            continue

        existing.filename = discovered.filename
        existing.extension = discovered.extension
        existing.language = discovered.language
        existing.size = discovered.size
        existing.content = discovered.content

    await session.execute(
        update(Project)
        .where(Project.id == project_id)
        .values(updated_at=datetime.now(timezone.utc))
    )
    await session.commit()
    return len(discovered_files)
