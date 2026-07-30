"""Execution context passed to every agent tool handler."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession


@dataclass(frozen=True, slots=True)
class AgentRunContext:
    """Scoped context for a single agent run within an owned project."""

    session: AsyncSession
    user_id: uuid.UUID
    project_id: uuid.UUID
