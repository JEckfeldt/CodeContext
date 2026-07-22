# CodeContext Project Status

Handoff document for continuing development. **Scope and phased goals** are defined in the [Roadmap](ROADMAP.md). This file describes **what is shipped**, **what works today**, and **what comes next**.

**Summary:** Phases **1–4** are **complete** for MVP. Users can upload a ZIP, browse files, **search by meaning**, and **ask grounded questions** with source citations. **Phase 5 — Advanced Developer Tools** is next.

---

## Phase overview

| Phase | Roadmap goal | Status |
|-------|----------------|--------|
| 1 — Repository Ingestion | Upload and browse discovered source files | **Complete** |
| 2 — Code Indexing | Prepare repositories for semantic search | **Complete** |
| 3 — Semantic Search | Find relevant code with natural language | **Complete** |
| 4 — AI Code Assistant | Grounded answers with file citations | **Complete** |
| 5 — Advanced Developer Tools | Scale and deeper repo insights | **Not started** |

---

## Current state

| Layer | Stack |
|--------|--------|
| Frontend | Next.js — upload, file list, semantic search, **Ask CodeContext** UI |
| Backend | FastAPI, SQLAlchemy async, Alembic, **LLM + RAG orchestration** |
| Database | PostgreSQL 16 + **pgvector** + **HNSW** (cosine) |

**Data flow (today):** ZIP → `files` → `code_chunks` → optional embeddings → vector search → **RAG prompt + chat completion** → answer + **SourceCitation** list in the UI.

---

## Completed work

### Phase 1 — Repository Ingestion

**Roadmap outcome:** User can upload a repository and browse its discovered source files.

| Roadmap feature | Status |
|-----------------|--------|
| Repository upload (ZIP) | Done |
| Project management | Done (create project + upload) |
| Recursive file discovery | Done |
| Supported file filtering and ignores | Done (extensions, `.gitignore`) |
| Persist file metadata and source content | Done |
| Git clone | Deferred (not in MVP) |

### Phase 2 — Code Indexing

**Roadmap outcome:** A repository becomes searchable by meaning, not just filenames.

| Roadmap feature | Status |
|-----------------|--------|
| Language-aware parsing | Done (Python, Markdown; fallback chunker) |
| Code chunking | Done |
| Embedding generation | Done (OpenAI, opt-in via `EMBEDDING_ENABLED`) |
| Vector storage (pgvector) | Done (+ HNSW index, migration `0004`) |

### Phase 3 — Semantic Search

**Roadmap outcome:** User can search the codebase and quickly find relevant files and snippets.

| Roadmap feature | Status |
|-----------------|--------|
| Vector similarity search | Done (`search_similar_chunks`, pgvector `<=>`) |
| Result ranking and filtering | Done (cosine similarity, scoped by `project_id`, top 10) |
| Search API and UI | Done (`POST .../search`, `RepositorySearchSection`) |
| Context retrieval for downstream AI | Done (shared retrieval layer for RAG) |

**Implementation highlights:**

| Deliverable | Location / notes |
|-------------|------------------|
| Retrieval service | `backend/app/retrieval/` |
| Search API | `POST /api/v1/projects/{id}/search` |
| Search UI | `frontend/components/search/` |

### Phase 4 — AI Code Assistant

**Roadmap outcome:** User can ask questions and get **grounded answers linked to real project files**.

| Area | Deliverable |
|------|-------------|
| **Backend — LLM** | `ChatProvider` protocol, `get_chat_provider()`, OpenAI chat completions (`app/llm/`) |
| **Backend — prompts** | RAG system prompt, numbered context blocks, `build_rag_messages()` (`app/prompts/`) |
| **Backend — orchestration** | `assistant_service.ask_question()` — retrieve → prompt → complete → citations |
| **Backend — API** | `POST /api/v1/projects/{id}/ask`, Pydantic `ProjectAskRequest` / `ProjectAskResponse`, `SourceCitation` |
| **Backend — reliability** | `select_rag_context_chunks()` aligns prompt `[n]` labels with API citations; consistent 404/503 mapping |
| **Frontend** | `RepositoryAskSection`, `askProject()` client, Markdown answers, citation cards, friendly error messages |
| **Testing** | Backend **58 passed, 1 skipped** (default); `npm run build` for frontend |

**Implementation highlights:**

| Deliverable | Location / notes |
|-------------|------------------|
| LLM providers | `backend/app/llm/` |
| RAG prompts | `backend/app/prompts/` |
| Orchestration | `backend/app/services/assistant_service.py` |
| Ask API | `backend/app/api/routes/projects.py` |
| Ask UI | `frontend/components/assistant/` |
| API client | `frontend/lib/api.ts` |

---

## Current capabilities

What works end-to-end **today**:

1. Create a project and upload a ZIP archive.
2. Discover and persist source files; browse paths in the UI.
3. Parse and chunk code (structure-aware where supported).
4. Optionally embed chunks on upload (`EMBEDDING_ENABLED` + `OPENAI_API_KEY`).
5. **Search** with natural language (UI or API): path, symbol, lines, snippet, similarity.
6. **Ask** natural-language questions about an indexed repository.
7. Receive **grounded answers** from retrieved code context (RAG).
8. View **source citations** with file paths, line ranges, symbols, and snippet previews.

**HTTP API**

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/v1/projects` | Create project |
| POST | `/api/v1/projects/{id}/upload` | Upload ZIP |
| GET | `/api/v1/projects/{id}/files` | List files |
| POST | `/api/v1/projects/{id}/search` | Semantic search |
| POST | `/api/v1/projects/{id}/ask` | RAG Q&A (see below) |
| GET | `/api/v1/health` | Health check |

**`POST /api/v1/projects/{id}/ask`**

Request:

```json
{
  "question": "How does authentication work?",
  "top_k": 8
}
```

`top_k` is optional (1–20); omit to use the default retrieval limit.

Response:

```json
{
  "project_id": "…",
  "question": "How does authentication work?",
  "answer": "Authentication is handled in … [1]",
  "citations": [
    {
      "index": 1,
      "file_path": "src/auth.py",
      "start_line": 1,
      "end_line": 24,
      "symbol_name": "login",
      "snippet": "…",
      "similarity": 0.89
    }
  ]
}
```

| Status | Meaning |
|--------|---------|
| 200 | Success (empty `citations` possible if nothing retrieved) |
| 404 | Project not found |
| 422 | Invalid body |
| 503 | Postgres/pgvector unavailable, embeddings unavailable, LLM disabled, or provider failure |

Ask requires **PostgreSQL + pgvector**, **`EMBEDDING_ENABLED`**, **`LLM_ENABLED`**, and **`OPENAI_API_KEY`** (see README and `.env.example`).

**Not available yet:** conversation history, streaming responses, authentication, Git clone ingestion, reindex-without-re-upload, background indexing, advanced retrieval (hybrid search, re-ranking), repository maps / dependency graphs.

---

## Not implemented yet

### Phase 5 — Advanced Developer Tools

Per roadmap: repository maps and navigation, dependency and relationship insights, stronger retrieval strategies, background indexing and performance tuning at scale.

### Cross-cutting gaps

- Authentication and multi-tenant projects
- Git clone ingestion
- Project indexing status and reindex without re-upload
- Embedding coverage indicators in the UI
- Shared API error helpers and env-driven RAG context limits

---

## Next recommended step

**Phase 5 — Advanced Developer Tools**, starting with the highest-value foundations:

1. **Operational clarity** — indexing/embedding status in the UI, reindex path, env-driven RAG limits.
2. **Retrieval quality** — optional re-ranking, hybrid signals, or similarity thresholds before RAG.
3. **Scale** — background indexing jobs and HNSW/ops tuning for larger repos.

Defer **conversation history** and **streaming** until core repo-exploration features land, unless product priority shifts to chat-first UX.

---

## Development notes

### Docker

```bash
docker compose up --build
```

Backend entrypoint: `alembic upgrade head` then uvicorn.

### Migrations

`0001` projects/files → `0002` chunks → `0003` symbol + embedding → `0004` HNSW.

Legacy DBs created only via `init_db()`: `alembic stamp 0002_create_code_chunks` then `alembic upgrade head`.

### Environment

See [README.md](../README.md) and `.env.example` — `EMBEDDING_ENABLED`, `LLM_ENABLED`, `OPENAI_API_KEY`, `DATABASE_URL`, `NEXT_PUBLIC_API_URL`.

### Tests

```bash
cd backend && python -m pytest -q    # 58 passed, 1 skipped (default)
cd frontend && npm run build
```

Postgres integration: `CODECONTEXT_INTEGRATION_DATABASE_URL=... pytest -m integration`

### Key paths

| Area | Path |
|------|------|
| Retrieval | `backend/app/retrieval/` |
| LLM | `backend/app/llm/` |
| Prompts | `backend/app/prompts/` |
| Assistant service | `backend/app/services/assistant_service.py` |
| Projects API | `backend/app/api/routes/projects.py` |
| Search UI | `frontend/components/search/` |
| Ask UI | `frontend/components/assistant/` |
| API client | `frontend/lib/api.ts` |

---

*When Phase 5 ships: add **Completed work — Phase 5**, update the phase table, and refresh **Next recommended step**.*
