# CodeContext Architecture

## Overview

CodeContext ingests source repositories, builds a searchable knowledge base with embeddings and vector search, and uses an LLM to answer questions with file references.

**Related documentation:** [AI Pipeline](AI_PIPELINE.md#overview) · [Database Schema](DATABASE_SCHEMA.md#overview) · [Roadmap](ROADMAP.md#codecontext-roadmap) · [Project Status](PROJECT_STATUS.md#project-status)

---

# System Architecture

## High-Level Flow

```
User → Frontend (Next.js) → Backend API (FastAPI)
                                    ↓
              Repository Pipeline ← → AI Services
                                    ↓
                         PostgreSQL + pgvector
                                    ↓
                         Retrieved Context → LLM Response → User
```

---

# Core Components

## Frontend

**Stack:** Next.js, TypeScript, Tailwind CSS

**Responsibilities:** Upload repositories, display project info, chat UI, AI responses, referenced files

## Backend API

**Stack:** FastAPI, Python

**Responsibilities:** Handle requests, manage ingestion, coordinate AI workflows, communicate with the database

## Repository Processing Pipeline

The [repository ingestion pipeline](AI_PIPELINE.md#repository-ingestion) converts source code into searchable knowledge: read uploads, filter supported files, extract content, chunk, embed, and store indexed data.

**Supported files (initial):** Python, JavaScript, TypeScript, Markdown, JSON, configuration files

## Vector Database

**Stack:** PostgreSQL, pgvector — see [Database Technology](DATABASE_SCHEMA.md#database-technology)

**Responsibilities:** Store embeddings, run semantic similarity search, retrieve code sections for AI responses

## LLM Layer

See [LLM Response Generation](AI_PIPELINE.md#llm-response-generation) and [Conversation entities](DATABASE_SCHEMA.md#conversation).

**Responsibilities:** Interpret retrieved context, generate explanations, answer project questions

**Example questions:**
- "Explain authentication"
- "Where is the database connection configured?"
- "How does this API request flow through the application?"

---

# AI Pipeline

Full design: [AI Pipeline](AI_PIPELINE.md#pipeline-flow)

1. User asks a question
2. Question → [embedding](AI_PIPELINE.md#embeddings)
3. [Vector search](AI_PIPELINE.md#vector-retrieval) finds [code chunks](DATABASE_SCHEMA.md#code-chunk)
4. Retrieved context → LLM
5. LLM generates a [grounded response](AI_PIPELINE.md#llm-response-generation) with [file references](AI_PIPELINE.md#llm-response-generation)

---

# Design Principles

## Grounded Responses

Answer from retrieved codebase content, not general knowledge alone. See [LLM Response Generation](AI_PIPELINE.md#llm-response-generation).

## Cost Efficiency

Apply [Cost Optimization](AI_PIPELINE.md#cost-optimization): embedding reuse, response caching, efficient retrieval, small context windows.

## Modularity

Swap AI providers, embedding models, and retrieval systems without rewriting the application.

## Incremental Development

Build in [Roadmap](ROADMAP.md#codecontext-roadmap) phases:

1. [Repository ingestion](ROADMAP.md#phase-1-repository-ingestion)
2. [Code indexing](ROADMAP.md#phase-2-code-indexing)
3. [Semantic search](ROADMAP.md#phase-3-semantic-search)
4. [AI-powered explanations](ROADMAP.md#phase-4-ai-powered-explanations)
5. [Advanced developer tools](ROADMAP.md#phase-5-advanced-developer-tools)
