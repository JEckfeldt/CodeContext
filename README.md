# CodeContext

AI-powered codebase assistant: ingest ZIP archives, index code into semantic chunks, search by meaning, and **ask grounded questions** with citations via RAG.

## MVP today

- Upload a code repository (ZIP)
- Browse discovered source files
- **Search the codebase by meaning** (semantic similarity)
- **Ask questions** and receive **grounded AI answers** with **source citations**

## Documentation

- [Roadmap](docs/ROADMAP.md) — phased plan and scope
- [Project Status](docs/PROJECT_STATUS.md) — handoff and current capabilities

## Semantic search

CodeContext embeds **chunks** and ranks them with **cosine similarity** in PostgreSQL (pgvector + HNSW).

**`POST /api/v1/projects/{project_id}/search`** — body `{ "query": "…" }` → ranked `results` with snippets.

Requires **`EMBEDDING_ENABLED=true`**, **`OPENAI_API_KEY`**, and Postgres with pgvector. See [Project Status](docs/PROJECT_STATUS.md) for details.

## AI Code Assistant (RAG)

1. **Retrieve** — same vector search as semantic search (optional `top_k` on ask).
2. **Prompt** — numbered code context blocks + grounding rules.
3. **Complete** — OpenAI chat model (`LLM_ENABLED`).
4. **Respond** — Markdown `answer` + structured `citations` (path, lines, symbol, snippet).

**`POST /api/v1/projects/{project_id}/ask`**

```json
{ "question": "How does auth work?", "top_k": 8 }
```

```json
{
  "project_id": "…",
  "question": "…",
  "answer": "…",
  "citations": [{ "index": 1, "file_path": "…", "start_line": 1, "end_line": 10, "symbol_name": null, "snippet": "…", "similarity": 0.9 }]
}
```

Ask requires **embeddings + LLM** enabled and the same Postgres stack as search.

### Required environment variables

Copy [`.env.example`](.env.example) to `.env`.

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | Backend → PostgreSQL (async) |
| `NEXT_PUBLIC_API_URL` | Frontend → backend API |
| `CORS_ORIGINS` | Browser origin for API |
| `EMBEDDING_ENABLED` | Embed chunks on upload and search/ask queries |
| `LLM_ENABLED` | Enable chat completions for `/ask` |
| `OPENAI_API_KEY` | Required when embeddings or LLM are enabled |
| `EMBEDDING_MODEL` / `LLM_MODEL` | OpenAI model names |
| `EMBEDDING_BATCH_SIZE` | Chunk embedding batch size |
| `LLM_MAX_TOKENS` | Completion token cap |

## Run locally

```bash
docker compose up --build
```

- Frontend: http://localhost:3000  
- Backend: http://localhost:8000 (`/api/v1/health`)

## Screenshots

<!-- TODO: add screenshot — repository upload and file list -->
<!-- TODO: add screenshot — semantic search results -->
<!-- TODO: add screenshot — Ask CodeContext answer with citations -->

## Tests

```bash
cd backend && python -m pytest -q    # 58 passed, 1 skipped (default)
cd frontend && npm run build
```

Optional Postgres integration: `CODECONTEXT_INTEGRATION_DATABASE_URL=... pytest -m integration`

## License

See [LICENSE](LICENSE).
