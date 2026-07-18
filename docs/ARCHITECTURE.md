# CodeContext Architecture

## Overview

CodeContext is an AI-powered codebase assistant that helps developers understand unfamiliar software projects.

The application analyzes source code repositories, creates a searchable knowledge base using embeddings and vector search, and uses a Large Language Model (LLM) to answer questions about the codebase with relevant file references.

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

The repository pipeline converts source code into searchable knowledge.

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

Responsibilities:
- Store code embeddings
- Perform semantic similarity searches
- Retrieve relevant code sections for AI responses

---

## LLM Layer

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

1. User asks a question

2. System converts the question into an embedding

3. Vector search finds relevant code chunks

4. Retrieved code context is sent to the LLM

5. LLM generates a grounded response

6. Response includes references to relevant files

---

# Design Principles

## Grounded Responses

The AI should answer using information retrieved from the user's codebase rather than relying only on general knowledge.

## Cost Efficiency

Reduce unnecessary LLM usage through:
- Embedding reuse
- Response caching
- Efficient retrieval
- Small context windows

## Modularity

AI providers, embedding models, and retrieval systems should be replaceable without rewriting the application.

## Incremental Development

Build the system in stages:
1. Repository ingestion
2. Code indexing
3. Semantic search
4. AI-powered explanations
5. Advanced developer tools