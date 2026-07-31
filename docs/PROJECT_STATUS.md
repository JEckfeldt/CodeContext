# CodeContext Project Status

## Overview

CodeContext is a multi-user workspace for importing, indexing, and querying software repositories. Users authenticate, create owned projects, import sources (Git, ZIP, or files), then use **Search**, **Explain**, or **Agent** over indexed project content.

Local MVP runs via Docker Compose (Next.js frontend, FastAPI backend, PostgreSQL + pgvector). OpenAI powers embeddings, RAG answers, and the read-only analysis agent.

---

## Implemented Features

**Platform**

- JWT auth: register, login, `/auth/me`; bcrypt password hashing
- Project ownership (`projects.user_id`); cross-user access blocked
- Project CRUD with embedded stats (files, chunks, sources, embeddings, `last_indexed_at`)
- `project_sources` audit rows for Git, ZIP, and file imports

**Ingestion & indexing**

- Git URL (public HTTP(S)), ZIP upload, individual file import (`.md`, `.txt`, text-based PDF)
- Source-agnostic pipeline: importers → extractors → chunking → optional embeddings
- File discovery with ignore rules; parsers for Python and Markdown
- pgvector storage with HNSW index (migration `0004`)
- Alembic migrations through `0005` (users, ownership, project sources)

**Search & Explain**

- Semantic search: `POST /api/v1/projects/{id}/search`
- Single-turn RAG explain: `POST /api/v1/projects/{id}/ask` with citations
- Frontend tabs for Search and Explain in the selected-project workspace

**Analysis agent**

- Read-only ReAct loop: `POST /api/v1/projects/{id}/agent/runs` (`AGENT_ENABLED`)
- Four tools: `repository_search`, `list_project_files`, `read_file`, `get_project_stats`
- Task templates (backend + UI): `architecture_review`, `implementation_planning`
- Structured artifacts: `architecture_report`, `implementation_plan` (Pydantic validation + parser)
- Frontend Agent tab: task template selector, goal input, tool trace, structured result views
- Architecture report card UI; implementation plan UI with milestone cards
- Per-milestone **Copy Cursor Prompt** (clipboard)
- Raw answer markdown rendering; download as `.md` (raw `answer` field)
- Placeholder (disabled) templates in UI: security review, explain auth, refactoring roadmap

**Frontend workspace**

- `/register`, `/login`; project dashboard with card grid
- Selected-project view: overview stats, import tabs, file browser, Search / Explain / Agent tabs

**Quality**

- Backend: **148 passed, 1 skipped** (default pytest)
- Frontend: `npm run build` passes

---

## Current Limitations

**Agent**

- Default **`AGENT_MAX_STEPS=10`**. Implementation planning on larger repos often needs more tool calls before producing the final JSON plan; runs fail with `AgentStepLimitError` (HTTP 503) when the step cap is hit before completion.
- Stateless runs — no DB persistence or run history
- No streaming; synchronous request/response only
- Read-only tools only — no writes, shell, git ops, or dependency graph
- `findings_report` and `roadmap_report` schemas exist but have no active templates or UI
- Download exports raw LLM `answer`, not artifact-derived markdown for implementation plans

**Search & Explain**

- Single-shot search and single-turn RAG — no conversation history
- No streaming responses
- Requires `EMBEDDING_ENABLED` (+ OpenAI key, pgvector); Explain also requires `LLM_ENABLED`

**Ingestion & platform**

- Public Git only — no private repo credentials or SSH
- No re-index without re-import; indexing is synchronous (no background workers)
- PDF: text extraction only (no OCR)
- No OAuth, password reset, email verification, teams, or shared projects
- No production deployment guide in-repo
- Legacy projects with `user_id` NULL are inaccessible via API
- Project card source badges inferred client-side, not from a dedicated sources API

---

## Architecture

```text
User (JWT)
  └── Project
        ├── ProjectSource[]  (git | zip | file)
        ├── File[]
        └── CodeChunk[] → optional embeddings (pgvector)
              ├── Search     (vector retrieval)
              ├── Explain    (retrieve once → RAG completion)
              └── Agent      (multi-step tool loop → structured artifact)
```

| Layer | Stack |
|-------|--------|
| Frontend | Next.js (App Router), TypeScript, Tailwind |
| Backend | FastAPI, SQLAlchemy async, Alembic, Pydantic |
| Database | PostgreSQL 16 + pgvector (HNSW) |
| AI | OpenAI embeddings + chat completions; native tool calling for agent (no LangChain) |

**Key backend paths**

- Ingestion: `backend/app/ingestion/`
- Indexing: `backend/app/indexing/`
- Retrieval / RAG: `backend/app/retrieval/`, `backend/app/services/assistant_service.py`
- Agent: `backend/app/agent/runner.py`, `backend/app/services/agent_service.py`, `backend/app/agent/tools/`
- Artifacts: `backend/app/agent/structured_output.py`, `artifact_parser.py`
- Templates: `backend/app/prompts/agent_task_templates.py`, `agent_system.py`

**Key frontend paths**

- Shell: `frontend/components/code-context-app.tsx`
- Agent: `frontend/components/agent/`
- API client: `frontend/lib/api.ts`

---

## Future Work

### Agent reliability & capability

- Raise or make step limits configurable per template (especially `implementation_planning`)
- Graceful handling when step limit is reached mid-run (partial results, clearer UI error)
- Additional task templates: security review, findings report, refactoring roadmap
- New read-only tools: symbol lookup, dependency/change-impact analysis
- Agent run persistence and history
- Artifact-driven markdown export for implementation plans

### Search, Explain & retrieval

- Streaming responses for Explain and Agent
- Multi-turn conversation / thread history
- Hybrid retrieval, re-ranking, retrieval tuning
- Search UX: query highlighting, richer previews, click-to-open source file
- Explain UX: citation line numbers, copy answer

### Ingestion & scalability

- Re-index / re-embed workflow without full re-import
- Background workers for large projects
- Private Git credentials (tokens / SSH)
- Import progress and re-index status in UI
- Broader parser coverage; import/symbol graph

### Platform & operations

- Production deployment path (env, secrets, migrations, `JWT_SECRET_KEY`)
- Password reset, OAuth (optional)
- Teams, shared projects, roles
- Repository map / dependency visualization

### Developer workflow & UX

- Project dashboard: search/filter, favorites, recent activity
- Index health indicators (embedding coverage, config visibility in stats)
- Dedicated sources list API for accurate project card badges

---

## Current Status

**What works today:** End-to-end local MVP — auth, owned projects, multi-source import, indexing, semantic search, RAG explain, and a read-only analysis agent with architecture review and implementation planning. Structured results render in the Agent tab; implementation plan milestones include copy-to-clipboard Cursor prompts.

**MVP state:** Multi-user local/demo system. Not production-hardened. Feature flags (`EMBEDDING_ENABLED`, `LLM_ENABLED`, `AGENT_ENABLED`) gate AI capabilities.

**Main remaining development:** Agent step-limit reliability for implementation planning on non-trivial repos, platform hardening (deploy, re-index, private Git), and UX/scale improvements (streaming, history, background indexing, additional agent templates and tools).

---

## Local development

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000 (`/api/v1/health`)
- Copy `.env.example` → `.env`; set `JWT_SECRET_KEY`, `OPENAI_API_KEY`, and enable flags as needed
- Run migrations: `alembic upgrade head` (includes `0005`)

```bash
cd backend && python -m pytest -q    # 148 passed, 1 skipped
cd frontend && npm run build
```
