from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime


class IngestionStatus(BaseModel):
    status: str
    files_discovered: int


class ProjectUploadResponse(BaseModel):
    project_id: UUID
    files_discovered: int
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
