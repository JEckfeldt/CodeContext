# CodeContext Architecture

## Overview

CodeContext is an AI-powered codebase assistant that helps developers understand unfamiliar software projects.

The application analyzes source code repositories, creates a searchable knowledge base using embeddings and vector search, and uses a Large Language Model (LLM) to answer questions about the codebase with relevant file references.

**Related documentation:** [AI Pipeline](AI_PIPELINE.md#overview) · [Database Schema](DATABASE_SCHEMA.md#overview) · [Roadmap](ROADMAP.md#codecontext-roadmap) · [Project Status](PROJECT_STATUS.md#project-status)

---

# System Architecture

## High-Level Flow

User
|
v
Frontend (Next.js)
|
v
Backend API (FastAPI)
|
+----------------------+
|                      |
v                      v
Repository Pipeline    AI Services
|                      |
v                      |
PostgreSQL + pgvector  |
|
v
Retrieved Context
|
v
LLM Response
|
v
User

---

# Core Components

## Frontend

Technology:
- Next.js
- TypeScript
- Tailwind CSS

Responsibilities:
- Upload repositories
- Display project information
- Provide chat interface
- Display AI responses
- Show referenced files

---

## Backend API

Technology:
- FastAPI
- Python

Responsibilities:
- Handle frontend requests
- Manage repository ingestion
- Coordinate AI workflows
- Communicate with database services

---

## Repository Processing Pipeline

The [repository ingestion pipeline](AI_PIPELINE.md#repository-ingestion) converts source code into searchable knowledge.

Responsibilities:
- Read uploaded repositories
- Identify supported file types
- Extract source code content
- Split files into meaningful chunks
- Generate embeddings
- Store indexed information

Supported files initially:
- Python
- JavaScript
- TypeScript
- Markdown
- JSON
- Configuration files

---

## Vector Database

Technology:
- PostgreSQL
- pgvector

See [Database Technology](DATABASE_SCHEMA.md#database-technology) for why relational metadata and vectors are stored together.

Responsibilities:
- Store code embeddings
- Perform semantic similarity searches
- Retrieve relevant code sections for AI responses

---

## LLM Layer

See [LLM Response Generation](AI_PIPELINE.md#llm-response-generation) and [Conversation entities](DATABASE_SCHEMA.md#conversation) for how responses and chat history are handled.

Responsibilities:
- Understand retrieved code context
- Generate explanations
- Answer questions about the project
- Create documentation and learning materials

Examples:
- "Explain authentication"
- "Where is the database connection configured?"
- "How does this API request flow through the application?"

---

# AI Pipeline

See [AI Pipeline](AI_PIPELINE.md#pipeline-flow) for the full system design.

1. User asks a question

2. System converts the question into an [embedding](AI_PIPELINE.md#embeddings)

3. [Vector search](AI_PIPELINE.md#vector-retrieval) finds relevant [code chunks](DATABASE_SCHEMA.md#code-chunk)

4. Retrieved code context is sent to the LLM

5. LLM generates a [grounded response](AI_PIPELINE.md#llm-response-generation)

6. Response includes [references to relevant files](AI_PIPELINE.md#llm-response-generation)

---

# Design Principles

## Grounded Responses

The AI should answer using information retrieved from the user's codebase rather than relying only on general knowledge. See [LLM Response Generation](AI_PIPELINE.md#llm-response-generation).

## Cost Efficiency

Reduce unnecessary LLM usage through strategies described in [Cost Optimization](AI_PIPELINE.md#cost-optimization):
- Embedding reuse
- Response caching
- Efficient retrieval
- Small context windows

## Modularity

AI providers, embedding models, and retrieval systems should be replaceable without rewriting the application.

## Incremental Development

Build the system in stages defined in the [Roadmap](ROADMAP.md#codecontext-roadmap):
1. [Repository ingestion](ROADMAP.md#phase-1-repository-ingestion)
2. [Code indexing](ROADMAP.md#phase-2-code-indexing)
3. [Semantic search](ROADMAP.md#phase-3-semantic-search)
4. [AI-powered explanations](ROADMAP.md#phase-4-ai-powered-explanations)
5. [Advanced developer tools](ROADMAP.md#phase-5-advanced-developer-tools)