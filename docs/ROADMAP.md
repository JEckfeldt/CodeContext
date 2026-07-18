# CodeContext Roadmap

**Related documentation:** [Architecture Overview](ARCHITECTURE.md#overview) · [AI Pipeline](AI_PIPELINE.md#overview) · [Database Schema](DATABASE_SCHEMA.md#overview) · [Project Status](PROJECT_STATUS.md#project-status)

## Phase 1 — Repository Ingestion

- Define repository upload and storage workflow
- Implement [file discovery and supported file filtering](AI_PIPELINE.md#repository-ingestion)
- Establish [backend project and API scaffolding](ARCHITECTURE.md#backend-api)
- Persist indexed repositories as [Project](DATABASE_SCHEMA.md#project) and [File](DATABASE_SCHEMA.md#file) records

## Phase 2 — Code Indexing

- [Parse supported source files into chunks](AI_PIPELINE.md#code-parsing)
- [Generate and store embeddings](AI_PIPELINE.md#embeddings)
- Persist indexed metadata as [Code Chunk](DATABASE_SCHEMA.md#code-chunk) and [Embedding](DATABASE_SCHEMA.md#embedding) records in [PostgreSQL](DATABASE_SCHEMA.md#postgresql)

## Phase 3 — Semantic Search

- Enable [vector similarity search with pgvector](AI_PIPELINE.md#vector-retrieval)
- Return relevant code chunks for user queries
- Expose search endpoints to the [frontend](ARCHITECTURE.md#frontend)

## Phase 4 — AI-Powered Explanations

- Integrate [LLM provider](ARCHITECTURE.md#llm-layer)
- Build [prompt templates for grounded responses](AI_PIPELINE.md#llm-response-generation)
- Persist chat history as [Conversation](DATABASE_SCHEMA.md#conversation) and [Message](DATABASE_SCHEMA.md#message) records
- Return answers with [file references](AI_PIPELINE.md#llm-response-generation)

## Phase 5 — Advanced Developer Tools

- Improve retrieval quality and context selection
- Add richer project exploration features
- Optimize cost and performance via [Cost Optimization](AI_PIPELINE.md#cost-optimization) strategies
- Explore [Future Improvements](AI_PIPELINE.md#future-improvements) and [Future Considerations](DATABASE_SCHEMA.md#future-considerations)
