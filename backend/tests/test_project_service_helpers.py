import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models import File, Project, ProjectSource, User
from app.services import project_service
from app.services.project_service import ProjectFileNotFoundError, ProjectNotFoundError
from app.services import project_source_service


async def _seed_project_with_file_and_source(
    session: AsyncSession,
    *,
    owner_id: uuid.UUID,
) -> tuple[Project, File, ProjectSource]:
    project = Project(name="Agent Helpers Test", user_id=owner_id)
    session.add(project)
    await session.flush()

    file = File(
        project_id=project.id,
        path="src/app.py",
        filename="app.py",
        extension="py",
        language="python",
        size=18,
        content='print("hello")\n',
    )
    session.add(file)

    source = ProjectSource(
        project_id=project.id,
        source_type="zip",
        source_name="repo.zip",
        source_url=None,
    )
    session.add(source)
    await session.commit()
    await session.refresh(project)
    await session.refresh(file)
    await session.refresh(source)
    return project, file, source


async def _create_user(session: AsyncSession, email: str) -> User:
    user = User(email=email, password_hash=hash_password("password123"))
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest.mark.asyncio
async def test_authorized_user_can_read_project_file_content(
    db_session: AsyncSession,
) -> None:
    owner = await _create_user(db_session, "owner-read@example.com")
    project, file, _ = await _seed_project_with_file_and_source(
        db_session,
        owner_id=owner.id,
    )

    result = await project_service.get_project_file_content(
        db_session,
        project.id,
        "src/app.py",
        user_id=owner.id,
    )

    assert result.id == file.id
    assert result.path == "src/app.py"
    assert result.content == 'print("hello")\n'
    assert result.truncated is False


@pytest.mark.asyncio
async def test_unauthorized_user_cannot_read_project_file_content(
    db_session: AsyncSession,
) -> None:
    owner = await _create_user(db_session, "owner-deny-read@example.com")
    other = await _create_user(db_session, "other-read@example.com")
    project, _, _ = await _seed_project_with_file_and_source(
        db_session,
        owner_id=owner.id,
    )

    with pytest.raises(ProjectNotFoundError):
        await project_service.get_project_file_content(
            db_session,
            project.id,
            "src/app.py",
            user_id=other.id,
        )


@pytest.mark.asyncio
async def test_missing_file_returns_expected_error(db_session: AsyncSession) -> None:
    owner = await _create_user(db_session, "owner-missing@example.com")
    project, _, _ = await _seed_project_with_file_and_source(
        db_session,
        owner_id=owner.id,
    )

    with pytest.raises(ProjectFileNotFoundError, match="missing.py"):
        await project_service.get_project_file_content(
            db_session,
            project.id,
            "missing.py",
            user_id=owner.id,
        )


@pytest.mark.asyncio
async def test_authorized_user_can_list_project_sources(
    db_session: AsyncSession,
) -> None:
    owner = await _create_user(db_session, "owner-sources@example.com")
    project, _, source = await _seed_project_with_file_and_source(
        db_session,
        owner_id=owner.id,
    )

    sources = await project_source_service.list_project_sources(
        db_session,
        project.id,
        user_id=owner.id,
    )

    assert len(sources) == 1
    assert sources[0].id == source.id
    assert sources[0].source_type == "zip"
    assert sources[0].source_name == "repo.zip"
    assert sources[0].project_id == project.id


@pytest.mark.asyncio
async def test_unauthorized_user_cannot_list_project_sources(
    db_session: AsyncSession,
) -> None:
    owner = await _create_user(db_session, "owner-deny-sources@example.com")
    other = await _create_user(db_session, "other-sources@example.com")
    project, _, _ = await _seed_project_with_file_and_source(
        db_session,
        owner_id=owner.id,
    )

    with pytest.raises(ProjectNotFoundError):
        await project_source_service.list_project_sources(
            db_session,
            project.id,
            user_id=other.id,
        )


@pytest.mark.asyncio
async def test_get_project_file_content_truncates_large_files(
    db_session: AsyncSession,
) -> None:
    owner = await _create_user(db_session, "owner-truncate@example.com")
    project = Project(name="Truncate Test", user_id=owner.id)
    db_session.add(project)
    await db_session.flush()

    db_session.add(
        File(
            project_id=project.id,
            path="large.txt",
            filename="large.txt",
            extension="txt",
            language="text",
            size=100,
            content="x" * 100,
        )
    )
    await db_session.commit()

    result = await project_service.get_project_file_content(
        db_session,
        project.id,
        "large.txt",
        user_id=owner.id,
        max_content_chars=50,
    )

    assert result.truncated is True
    assert len(result.content) > 50
    assert result.content.endswith("… [truncated]")
