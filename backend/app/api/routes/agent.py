import uuid

from fastapi import APIRouter, HTTPException, status

from app.agent.exceptions import (
    AgentError,
    AgentStepLimitError,
    AgentUnavailableError,
)
from app.core.auth_deps import CurrentUser
from app.core.deps import DbSession
from app.llm.exceptions import LLMCompletionError
from app.schemas.agent import AgentRunRequest, AgentRunResponse
from app.services.agent_service import run_agent
from app.services.project_service import ProjectNotFoundError

router = APIRouter(prefix="/projects", tags=["agent"])


def _project_not_found(exc: ProjectNotFoundError) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=str(exc),
    )


@router.post("/{project_id}/agent/runs", response_model=AgentRunResponse)
async def start_agent_run(
    project_id: uuid.UUID,
    payload: AgentRunRequest,
    session: DbSession,
    current_user: CurrentUser,
) -> AgentRunResponse:
    """Run the read-only analysis agent for a project goal."""
    try:
        result = await run_agent(
            session,
            current_user.id,
            project_id,
            payload.goal,
            task_template=payload.task_template,
        )
    except ProjectNotFoundError as exc:
        raise _project_not_found(exc) from exc
    except AgentUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except AgentStepLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except (LLMCompletionError, AgentError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return AgentRunResponse.from_agent_run_result(project_id, result)
