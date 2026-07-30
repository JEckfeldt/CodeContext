"""Orchestrate agent runs for owned projects."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.context import AgentRunContext
from app.agent.exceptions import AgentUnavailableError
from app.agent.runner import AgentRunner
from app.agent.schemas import AgentRunResult
from app.agent.tools.registry_factory import create_default_registry
from app.core.config import settings
from app.llm.base import ChatProvider
from app.llm.provider import get_agent_chat_provider
from app.prompts.agent_task_templates import get_task_template
from app.services import project_service


class AgentService:
    """Run the analysis agent against an owned project."""

    async def run_agent(
        self,
        session: AsyncSession,
        user_id: uuid.UUID,
        project_id: uuid.UUID,
        goal: str,
        task_template: str | None = None,
        *,
        chat_provider: ChatProvider | None = None,
    ) -> AgentRunResult:
        await project_service.get_project_for_user(session, project_id, user_id)

        if not settings.agent_enabled:
            raise AgentUnavailableError(
                "Agent is not enabled. Set AGENT_ENABLED=true to use the analysis agent."
            )

        if task_template is not None:
            get_task_template(task_template)

        provider = (
            chat_provider
            if chat_provider is not None
            else get_agent_chat_provider()
        )
        if provider is None:
            raise AgentUnavailableError(
                "Agent LLM provider is not configured. "
                "Set LLM_ENABLED=true and OPENAI_API_KEY."
            )

        context = AgentRunContext(
            session=session,
            user_id=user_id,
            project_id=project_id,
        )
        registry = create_default_registry()
        runner = AgentRunner(
            chat_provider=provider,
            tool_registry=registry,
            max_steps=settings.agent_max_steps,
        )
        return await runner.run(
            context,
            goal,
            task_template=task_template,
        )


agent_service = AgentService()


async def run_agent(
    session: AsyncSession,
    user_id: uuid.UUID,
    project_id: uuid.UUID,
    goal: str,
    task_template: str | None = None,
    *,
    chat_provider: ChatProvider | None = None,
) -> AgentRunResult:
    """Convenience wrapper around the default ``AgentService`` instance."""
    return await agent_service.run_agent(
        session,
        user_id,
        project_id,
        goal,
        task_template=task_template,
        chat_provider=chat_provider,
    )
