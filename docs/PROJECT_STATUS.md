# CodeContext Project Status

Living progress tracker for the CodeContext monorepo. Update this file as milestones move forward.

For planned phases and scope, see the [Roadmap](ROADMAP.md).

## Current milestone

**Phase 1 — Repository Ingestion**

Backend ingestion is largely in place. Current focus is completing the end-to-end experience: project creation, ZIP upload, and browsing ingested files from the frontend workspace.

## Completed

- [x] Repository structure and core documentation
- [x] Frontend application shell and design system
- [x] Backend FastAPI foundation
- [x] PostgreSQL + pgvector configuration
- [x] Project and File database models
- [x] Repository ZIP ingestion API
- [x] File discovery (supported types, ignores, `.gitignore`)
- [x] Ingestion tests (API + discovery)
- [x] Docker Compose dev environment
- [x] Improved frontend hot reload in Docker

## In Progress

- [ ] Connect Projects UI to ingestion API
- [ ] End-to-end Phase 1 demo (upload → browse files in UI)

## Upcoming

- [ ] Git clone ingestion (optional Phase 1 extension)
- [ ] Phase 2 — Code indexing (parsing, chunking, embeddings)
- [ ] Phase 3 — Semantic search
- [ ] Phase 4 — AI code assistant

## Current Notes

- **Stack:** Next.js frontend, FastAPI backend, PostgreSQL with pgvector for future vector search.
- **Backend:** `POST /api/v1/projects`, `POST /api/v1/projects/{id}/upload`, and `GET /api/v1/projects/{id}/files` are implemented. File contents are stored in PostgreSQL for discovered source files.
- **Frontend:** Dashboard, Projects, and Settings use the workspace UI. Ingestion is not wired in the UI yet.
- **Out of scope for now:** embeddings, semantic search, LLM features, authentication.
- **Run locally:** `docker compose up --build` — frontend on port 3000, backend on port 8000, health check at `/api/v1/health`.
