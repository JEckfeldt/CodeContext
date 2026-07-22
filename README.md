# CodeContext

Understand unfamiliar codebases: **upload a ZIP**, browse files, **find** relevant code, and **get AI explanations** with links back to real source files.

## MVP today

- **Upload** a repository (ZIP)
- **Browse** discovered source files
- **Find Code** — search by meaning over indexed snippets
- **Explain Code** — grounded AI answers with **source citations**

## How it works (UI)

```text
Upload repository → Code workspace → Results
                      ├─ Find Code    (search)
                      └─ Explain Code (AI + citations)
```

In the app, pick **Find Code** or **Explain Code** in one workspace panel, enter a query, then review full-width results below.

Details, API reference, and limitations: [Project Status](docs/PROJECT_STATUS.md) · [Roadmap](docs/ROADMAP.md)

## Find Code

Locates files, functions, classes, and snippets that match your question.

**API:** `POST /api/v1/projects/{project_id}/search`

```json
{ "query": "Where is authentication handled?" }
```

Requires indexed embeddings (`EMBEDDING_ENABLED`, OpenAI key, PostgreSQL + pgvector).

## Explain Code

Uses retrieved code as context, then returns a Markdown explanation plus citations (path, lines, symbol, snippet).

**API:** `POST /api/v1/projects/{project_id}/ask`

```json
{ "question": "How does auth work?", "top_k": 8 }
```

Requires embeddings **and** LLM enabled (`LLM_ENABLED`, same OpenAI key).

## Environment

Copy [`.env.example`](.env.example) to `.env`. Key variables:

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | PostgreSQL (async) |
| `NEXT_PUBLIC_API_URL` | Frontend → API |
| `CORS_ORIGINS` | Browser origin |
| `EMBEDDING_ENABLED` | Index + search / retrieve |
| `LLM_ENABLED` | Explain Code completions |
| `OPENAI_API_KEY` | Embeddings + LLM when enabled |

## Run locally

```bash
docker compose up --build
```

- App: http://localhost:3000  
- API: http://localhost:8000 (`/api/v1/health`)

## Screenshots

<!-- TODO: screenshot — repository upload and file list -->
<!-- TODO: screenshot — Find Code results -->
<!-- TODO: screenshot — Explain Code answer with citations -->

## Tests

```bash
cd backend && python -m pytest -q    # 58 passed, 1 skipped (default)
cd frontend && npm run build
```

Optional: `CODECONTEXT_INTEGRATION_DATABASE_URL=... pytest -m integration`

## License

See [LICENSE](LICENSE).
