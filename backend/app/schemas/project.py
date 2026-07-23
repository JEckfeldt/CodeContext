from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class ProjectImportSourceType(str, Enum):
    git = "git"


class ProjectImportRequest(BaseModel):
    source_type: ProjectImportSourceType
    url: str = Field(min_length=1)


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime


class ProjectUploadResponse(BaseModel):
    project_id: UUID
    files_discovered: int
    chunks_created: int
    embeddings_created: int
    ingestion_status: str


class FileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    path: str
    filename: str
    extension: str | None
    language: str | None
    size: int
    created_at: datetime
