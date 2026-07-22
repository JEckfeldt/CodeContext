# CodeContext Project Status

Handoff document for continuing development. **Scope and phased goals** are defined in the [Roadmap](ROADMAP.md). This file describes **what is shipped**, **what works today**, **what is missing**, and **recommended next steps**.

---

## Development summary

| | |
|--|--|
| **Current phase** | Post–Phase 4 MVP (Phases 1–4 complete; Phase 5 not started) |
| **Completed phases** | 1 Repository Ingestion · 2 Code Indexing · 3 Semantic Search · 4 AI Code Assistant |
| **Recommended next milestone** | Production foundations: **authentication**, **Git ingestion**, **re-index workflow**, and **deployment** |
| **Approximate MVP maturity** | **Strong local/demo MVP** — full ingest → find → explain path works with Docker, Postgres, and OpenAI; not production-hardened (no auth, no hosted deploy story, no streaming/history) |

---

## Summary

Phases **1–4** are **complete**. CodeContext is a single-page app where users **upload a ZIP**, **browse files**, and use one **code workspace** with two modes:

- **Find Code** — natural-language search over indexed snippets (semantic / vector search)
- **Explain Code** — RAG assistant that answers from retrieved context with **source citations**

The frontend has been refactored for a **unified, responsive workspace** (light theme, tabbed modes, full-width results). Backend tests: **58 passed, 1 skipped** (default). Frontend: **`npm run build`** verified.

**Phase 5** (advanced developer tools) and several **cross-cutting** features (auth, Git clone, streaming, etc.) are **not** implemented.

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
| Frontend | Next.js — upload, file list, **Find Code** / **Explain Code** workspace |
| Backend | FastAPI, SQLAlchemy async, Alembic, retrieval, LLM + RAG |
| Database | PostgreSQL 16 + **pgvector** + **HNSW** (cosine) |

**Backend data flow:** ZIP → `files` → `code_chunks` → optional embeddings → vector search → (Explain mode) RAG prompt + chat completion → answer + citations.

---

## UI workflow (today)

```text
Upload repository (ZIP)
        ↓
Browse discovered files + active repo summary
        ↓
Code workspace (one panel, tabbed)
   ┌─────────────┬──────────────┐
   │ Find Code   │ Explain Code │  ← only one mode visible at a time
   └─────────────┴──────────────┘
        ↓
   Query input + primary action (Search / Explain)
        ↓
   Results (scrollable, full width)
```

### Find Code (UI label)

**Purpose:** Help users **locate** relevant files, functions, classes, and snippets in the indexed repository.

**Backend:** `POST /api/v1/projects/{id}/search` → vector similarity over embedded chunks.

**Results:** Ranked hits with path, line range, symbol (if any), snippet, similarity score.

### Explain Code (UI label)

**Purpose:** Help users **understand** how the codebase works via AI explanations tied to real source.

**Backend:** `POST /api/v1/projects/{id}/ask` → retrieve chunks → RAG prompt → LLM → Markdown answer + **SourceCitation** list (aligned with prompt context).

**Results:** Markdown answer and expandable source cards (path, lines, symbol, snippet).

Component filenames (`RepositorySearchSection`, `RepositoryAskSection`) are unchanged; only user-facing copy uses Find / Explain.

---

## Current MVP capabilities

Everything below works **today** when run via Docker (or equivalent) with PostgreSQL + pgvector and OpenAI configured as documented.

**Ingestion & browsing**

- Create project and **ZIP upload**
- File discovery with extension / ignore rules and `.gitignore` respect
- Persist file metadata and content
- **Browse** discovered files in the UI

**Indexing & search (backend)**

- **Code chunking** (Python / Markdown parsers; line-based fallback)
- Optional **embeddings** on upload (`EMBEDDING_ENABLED`, OpenAI)
- **pgvector** storage and **HNSW** cosine index
- **Semantic search** API and Find Code UI

**AI assistant (backend + UI)**

- LLM provider abstraction + OpenAI chat completions (`LLM_ENABLED`)
- RAG **prompts**, **assistant_service** orchestration
- **Explain Code** UI: Markdown answers, **source citations**, user-friendly errors
- Citation list matches chunks sent to the model (`select_rag_context_chunks`)

**Frontend / UX**

- **Responsive** layout (mobile / tablet / desktop)
- **Unified workspace** with tabbed Find Code / Explain Code (state preserved when switching tabs)
- Light, developer-tool-style UI (panels, composers, code blocks)

**Quality**

- Backend unit/API tests; optional Postgres integration test (skipped by default)
- Frontend production build passes

---

## HTTP API (reference)

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/v1/projects` | Create project |
| POST | `/api/v1/projects/{id}/upload` | Upload ZIP |
| GET | `/api/v1/projects/{id}/files` | List files |
| POST | `/api/v1/projects/{id}/search` | Find Code (semantic search) |
| POST | `/api/v1/projects/{id}/ask` | Explain Code (RAG) |
| GET | `/api/v1/health` | Health check |

**Ask request:** `{ "question": "…", "top_k": 8 }` (`top_k` optional, 1–20).

**Ask response:** `{ "project_id", "question", "answer", "citations": [{ "index", "file_path", "start_line", "end_line", "symbol_name", "snippet", "similarity" }] }`.

Search/ask require **PostgreSQL + pgvector**, **`EMBEDDING_ENABLED`**, and for ask also **`LLM_ENABLED`** + **`OPENAI_API_KEY`**. See [README.md](../README.md) and `.env.example`.

---

## Completed work (by phase)

### Phase 1 — Repository Ingestion

ZIP upload, project create, discovery, filters, persist files. Git clone **not** implemented.

### Phase 2 — Code Indexing

Chunks, parsers, optional embeddings, pgvector + migration `0004` HNSW.

### Phase 3 — Semantic Search

`search_similar_chunks`, search API, Find Code UI (`frontend/components/search/`).

### Phase 4 — AI Code Assistant

`app/llm/`, `app/prompts/`, `assistant_service`, ask API/schemas, Explain Code UI (`frontend/components/assistant/`), citation alignment hardening.

| Area | Path |
|------|------|
| Retrieval | `backend/app/retrieval/` |
| LLM | `backend/app/llm/` |
| Prompts | `backend/app/prompts/` |
| Orchestration | `backend/app/services/assistant_service.py` |
| Routes | `backend/app/api/routes/projects.py` |
| Shell / workspace | `frontend/components/code-context-app.tsx` |
| API client | `frontend/lib/api.ts` |

---

## Current limitations

Features that **do not exist** today (do not assume they work):

**Product & access**

- **Authentication** / login
- **Multi-user** or multi-tenant projects
- **Deployment** guide or production hosting setup in-repo (Docker Compose is for local/dev)

**Ingestion & indexing**

- **Git clone** / GitHub connect (UI button is disabled placeholder)
- **Re-index** or refresh index **without** re-uploading the ZIP
- **Background indexing** workers (upload is synchronous from the user’s perspective)
- UI **embedding coverage** indicators (empty search vs missing vectors)

**Assistant UX**

- **Streaming** AI responses
- **Conversation history** / multi-turn threads

**Advanced search & platform**

- Hybrid retrieval, **re-ranking**, repository **maps**, **dependency graphs**
- **Usage analytics** / billing
- Public chunk listing API

---

## Recommended next priorities

### High priority

- **Authentication** — secure projects and API before any shared deployment
- **Git repository ingestion** — clone or connect remotes instead of ZIP-only
- **Re-index workflow** — re-chunk / re-embed without full re-upload; surface status in UI
- **Deployment** — documented path to staging/production (env, migrations, secrets)

### Medium priority

- **Streaming** Explain Code responses
- **Conversation history** for follow-up questions
- **Retrieval improvements** — thresholds, optional re-rank before RAG
- **Embedding / indexing status** in UI after upload

### Future (Phase 5+)

- Repository maps and navigation
- Dependency / relationship insights
- Background workers for large repos
- Hybrid retrieval and re-ranking at scale
- Multi-repository or org-wide chat (depends on auth)

---

## Development notes

### Run locally

```bash
docker compose up --build
```

- Frontend: http://localhost:3000  
- Backend: http://localhost:8000 (`/api/v1/health`)  
- Backend entrypoint: `alembic upgrade head` then uvicorn

### Migrations

`0001` projects/files → `0002` chunks → `0003` symbol + embedding → `0004` HNSW.

Legacy DBs from `init_db()` only: `alembic stamp 0002_create_code_chunks` then `alembic upgrade head`.

### Tests

```bash
cd backend && python -m pytest -q    # 58 passed, 1 skipped (default)
cd frontend && npm run build
```

Postgres integration: `CODECONTEXT_INTEGRATION_DATABASE_URL=... pytest -m integration`

---

*When Phase 5 or major platform work ships, update **Phase overview**, **Completed work**, **Current MVP capabilities**, and **Recommended next priorities**.*
