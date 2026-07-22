import uuid
from unittest.mock import ANY, AsyncMock

import pytest
from httpx import AsyncClient

from app.llm.exceptions import LLMCompletionError, LLMUnavailableError
from app.retrieval.exceptions import QueryEmbeddingError, SemanticSearchUnavailableError
from app.services.assistant_service import AssistantResult, SourceCitation


@pytest.mark.asyncio
async def test_ask_project_returns_answer(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    create_response = await client.post("/api/v1/projects", json={"name": "Ask Test"})
    project_id = create_response.json()["id"]

    fake_result = AssistantResult(
        project_id=uuid.UUID(project_id),
        question="How does auth work?",
        answer="Authentication is handled in [1].",
        citations=[
            SourceCitation(
                index=1,
                file_path="src/auth.py",
                start_line=1,
                end_line=10,
                symbol_name="login",
                snippet="def login(): pass",
                similarity=0.91,
            )
        ],
        retrieved_chunks=[],
    )
    ask_mock = AsyncMock(return_value=fake_result)
    monkeypatch.setattr("app.api.routes.projects.ask_question", ask_mock)

    response = await client.post(
        f"/api/v1/projects/{project_id}/ask",
        json={"question": "How does auth work?", "top_k": 5},
    )

    assert response.status_code == 200
    ask_mock.assert_awaited_once_with(
        ANY,
        uuid.UUID(project_id),
        "How does auth work?",
        limit=5,
    )
    payload = response.json()
    assert payload["project_id"] == project_id
    assert payload["question"] == "How does auth work?"
    assert payload["answer"] == "Authentication is handled in [1]."
    assert len(payload["citations"]) == 1
    assert payload["citations"][0]["file_path"] == "src/auth.py"
    assert payload["citations"][0]["similarity"] == pytest.approx(0.91)


@pytest.mark.asyncio
async def test_ask_project_not_found(client: AsyncClient) -> None:
    missing_id = uuid.uuid4()
    response = await client.post(
        f"/api/v1/projects/{missing_id}/ask",
        json={"question": "What is this project?"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_ask_project_rejects_invalid_body(client: AsyncClient) -> None:
    create_response = await client.post("/api/v1/projects", json={"name": "Invalid Ask"})
    project_id = create_response.json()["id"]

    empty_question = await client.post(
        f"/api/v1/projects/{project_id}/ask",
        json={"question": ""},
    )
    assert empty_question.status_code == 422

    invalid_top_k = await client.post(
        f"/api/v1/projects/{project_id}/ask",
        json={"question": "valid?", "top_k": 0},
    )
    assert invalid_top_k.status_code == 422

    missing_question = await client.post(
        f"/api/v1/projects/{project_id}/ask",
        json={},
    )
    assert missing_question.status_code == 422


@pytest.mark.asyncio
async def test_ask_project_llm_unavailable(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    create_response = await client.post("/api/v1/projects", json={"name": "LLM Off"})
    project_id = create_response.json()["id"]

    ask_mock = AsyncMock(
        side_effect=LLMUnavailableError(
            "LLM provider is not configured. Set LLM_ENABLED=true and OPENAI_API_KEY."
        )
    )
    monkeypatch.setattr("app.api.routes.projects.ask_question", ask_mock)

    response = await client.post(
        f"/api/v1/projects/{project_id}/ask",
        json={"question": "Explain the app"},
    )
    assert response.status_code == 503
    assert "LLM_ENABLED" in response.json()["detail"]
    ask_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_ask_project_retrieval_failure(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    create_response = await client.post("/api/v1/projects", json={"name": "Retrieval Fail"})
    project_id = create_response.json()["id"]

    ask_mock = AsyncMock(side_effect=QueryEmbeddingError("Embedding provider is not configured."))
    monkeypatch.setattr("app.api.routes.projects.ask_question", ask_mock)

    response = await client.post(
        f"/api/v1/projects/{project_id}/ask",
        json={"question": "Where is auth?"},
    )
    assert response.status_code == 503
    ask_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_ask_project_semantic_search_unavailable(client: AsyncClient) -> None:
    create_response = await client.post("/api/v1/projects", json={"name": "SQLite Ask"})
    project_id = create_response.json()["id"]

    response = await client.post(
        f"/api/v1/projects/{project_id}/ask",
        json={"question": "Where is auth?"},
    )
    assert response.status_code == 503
    assert "PostgreSQL" in response.json()["detail"]


@pytest.mark.asyncio
async def test_ask_project_provider_failure(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    create_response = await client.post("/api/v1/projects", json={"name": "LLM Fail"})
    project_id = create_response.json()["id"]

    ask_mock = AsyncMock(side_effect=LLMCompletionError("OpenAI chat completion failed"))
    monkeypatch.setattr("app.api.routes.projects.ask_question", ask_mock)

    response = await client.post(
        f"/api/v1/projects/{project_id}/ask",
        json={"question": "Summarize the repo"},
    )
    assert response.status_code == 503
    assert "OpenAI chat completion failed" in response.json()["detail"]
    ask_mock.assert_awaited_once()
