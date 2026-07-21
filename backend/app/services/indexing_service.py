import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.indexing.chunking import chunk_file_content
from app.models import CodeChunk, File
from app.services import project_service


async def index_project_files(session: AsyncSession, project_id: uuid.UUID) -> int:
    await project_service.get_project(session, project_id)
    files = await project_service.list_project_files(session, project_id)

    await session.execute(delete(CodeChunk).where(CodeChunk.project_id == project_id))

    chunks_created = 0
    for file in files:
        chunks_created += await _index_file(session, file)

    await session.commit()
    return chunks_created


async def _index_file(session: AsyncSession, file: File) -> int:
    drafts = chunk_file_content(file.content, file.language)
    for draft in drafts:
        session.add(
            CodeChunk(
                file_id=file.id,
                project_id=file.project_id,
                chunk_index=draft.chunk_index,
                start_line=draft.start_line,
                end_line=draft.end_line,
                content=draft.content,
                language=draft.language,
                chunk_kind=draft.chunk_kind,
            )
        )
    return len(drafts)


async def count_project_chunks(session: AsyncSession, project_id: uuid.UUID) -> int:
    result = await session.scalars(
        select(CodeChunk.id).where(CodeChunk.project_id == project_id)
    )
    return len(result.all())
