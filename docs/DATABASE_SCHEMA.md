# CodeContext Database Schema

## Overview

The database is the persistent foundation for CodeContext. It stores everything the application needs to transform uploaded repositories into searchable knowledge and to support question-and-answer interactions over that knowledge.

CodeContext uses the database for three primary responsibilities:

1. **Repository indexing** — Track uploaded projects, discovered files, parsed chunks, and generated embeddings.
2. **Semantic search** — Store vector representations and retrieve relevant code sections when users ask questions.
3. **Conversations** — Persist chat history so users can review prior questions and AI responses within the context of a project.

The schema is designed around the MVP workflow: upload a repository, index supported files, search semantically, ask questions, and receive grounded answers with file references. It intentionally avoids premature complexity such as user accounts, repository versioning, or background job orchestration, while leaving room for those additions later.

**Related documentation:** [Architecture Overview](ARCHITECTURE.md#overview) · [AI Pipeline](AI_PIPELINE.md#overview) · [Roadmap](ROADMAP.md#codecontext-roadmap)

---

# Database Technology

## PostgreSQL

PostgreSQL is the primary relational database for CodeContext. It provides durable storage, structured relationships, transactional integrity, and mature tooling for application development.

CodeContext needs more than vector search alone. The system must persist hierarchical repository data (projects, files, chunks), conversation history, indexing status, and metadata used for source references. A relational database fits this model naturally and supports consistent queries across ingestion, retrieval, and chat features.

## pgvector

pgvector extends PostgreSQL with vector similarity search. CodeContext uses it to store embeddings and perform nearest-neighbor retrieval over code chunks.

Semantic search is central to the MVP. When a user asks a question, the system embeds the question and compares it against stored chunk embeddings to find the most relevant source material. pgvector allows this workflow to run in the same database as the rest of the application data. See [Vector Retrieval](AI_PIPELINE.md#vector-retrieval) and the [Vector Database component](ARCHITECTURE.md#vector-database).

## Why relational metadata and vectors belong together

Keeping embeddings alongside relational metadata offers several advantages:

- **Traceability:** Every retrieved vector can be joined directly to its chunk, file, and project without cross-system lookups.
- **Scoped search:** Queries can be limited to a single project or file set while performing vector similarity ranking.
- **Source references:** File paths, chunk locations, and project context needed for grounded LLM responses remain accessible in the same query path as retrieval.
- **Operational simplicity:** One database reduces infrastructure complexity during MVP development and early deployment.
- **Consistency:** Indexing status, chunk content, and embeddings can be updated within shared transactional boundaries.

Separating vectors into a standalone vector database may become useful at larger scale, but colocating vectors with metadata is the right starting point for the MVP.

---

# Core Entities

The MVP schema centers on six entities grouped into two domains: indexed repository data and project conversations.

---

## Project

Represents an indexed repository uploaded to CodeContext.

### Purpose

A Project is the top-level container for everything derived from one repository upload. It anchors [file discovery](AI_PIPELINE.md#repository-ingestion), [chunking](AI_PIPELINE.md#chunking-strategy), [embedding storage](AI_PIPELINE.md#embeddings), [semantic search](AI_PIPELINE.md#vector-retrieval), and [chat sessions](AI_PIPELINE.md#llm-response-generation) related to that codebase.

### Important fields

Conceptual fields for a Project include:

- **Identity:** Unique identifier
- **Name:** Human-readable project name, often derived from the repository
- **Description:** Optional summary shown in the UI
- **Source information:** How the repository was provided (for the MVP, an uploaded archive or directory)
- **Indexing status:** Whether ingestion is pending, in progress, completed, or failed
- **Timestamps:** Created and last indexed times
- **Summary metadata:** Optional high-level stats such as file count or supported file count

The MVP does not require user ownership fields. Projects exist as standalone indexed repositories.

### Relationships

- One Project has many Files
- One Project has many Conversations

---

## File

Represents a single file discovered inside a repository.

### Purpose

A File records metadata about source material included in indexing. It connects repository structure to searchable chunks and supports file references in AI responses.

### Metadata stored

Conceptual metadata for a File includes:

- **Relative path:** Location within the repository (for example, `backend/app/main.py`)
- **File type / language:** Such as Python, TypeScript, Markdown, JSON, or configuration
- **Size:** File size in bytes
- **Content hash:** Optional fingerprint used to detect unchanged files during re-indexing
- **Indexing status:** Whether the file was parsed, skipped, or failed processing
- **Timestamps:** When the file was first indexed and last updated

The raw file content may be stored on disk or in object storage depending on implementation, but the database should retain enough metadata to locate and reference the file reliably.

### Relationship to Project

Each File belongs to exactly one Project. Files do not span projects. Deleting or re-indexing a Project implies replacing its associated file records and downstream chunks.

---

## Code Chunk

Represents a searchable section of a file.

### Purpose

A Code Chunk is the unit of retrieval in CodeContext. It holds the text segment produced by parsing and chunking, along with metadata needed for semantic search and source referencing.

Chunks are what the system embeds, retrieves, and sends to the LLM as context.

### Why chunks exist

Entire files are often too large to embed efficiently or fit into an LLM context window. Splitting files into focused sections allows:

- More precise semantic search results
- Lower retrieval and generation cost
- Better alignment between user questions and specific functions, classes, configuration blocks, or documentation sections

As described in the [AI pipeline chunking strategy](AI_PIPELINE.md#chunking-strategy), chunks should preserve enough context to remain understandable while staying small enough to retrieve selectively.

### Conceptual fields

- **Chunk text:** The indexed content segment
- **Position metadata:** Start/end line numbers or structural label when available
- **Chunk index:** Order of the chunk within its file
- **Token or character count:** Useful for context window planning
- **Optional structural hint:** Such as function, class, section, or configuration block

### Relationship to File

Each Code Chunk belongs to exactly one File. A File may produce one or many chunks depending on its size and structure. Chunks are not shared across files.

---

## Embedding

Represents the vector representation of a code chunk used for semantic search.

### Purpose

An Embedding stores the numerical vector generated from a chunk's text. It enables nearest-neighbor search when a user question is converted into a query vector.

Embeddings are created during [indexing](AI_PIPELINE.md#embeddings) and reused until the underlying chunk content changes.

### Conceptual fields

- **Vector values:** The embedding produced by the chosen model
- **Model identifier:** Which embedding model generated the vector
- **Dimensions:** Vector size, determined by the model
- **Created timestamp:** When the embedding was generated

Query-time question embeddings do not need to be persisted for the MVP. The database primarily stores embeddings for indexed chunks.

### Relationship to Code Chunk

Each Embedding corresponds to one Code Chunk. For the MVP, this is effectively a one-to-one relationship: one searchable chunk, one stored vector.

Separating Embedding as its own entity keeps vector-specific concerns distinct from chunk text and metadata, and allows future support for re-embedding with different models without losing the underlying chunk record.

---

## Conversation

Represents a user's interaction session with a specific project.

### Purpose

A Conversation groups related questions and answers about one indexed repository. It supports the [frontend chat experience](ARCHITECTURE.md#frontend) and preserves context across multiple turns in the same session.

For the MVP, a Conversation is scoped to a single Project. Users can start a new conversation when exploring a different line of inquiry about the same codebase.

### Conceptual fields

- **Title:** Optional label, possibly derived from the first user message
- **Timestamps:** Created and last activity times
- **Status:** Active or archived, if needed for UI organization

The MVP does not require user identity on conversations.

### Relationship to Project

Each Conversation belongs to exactly one Project. Conversations do not span multiple repositories.

---

## Message

Represents an individual user question or AI response within a conversation.

### Purpose

Messages persist the chat history that powers the CodeContext Q&A experience. They record what the user asked, what the system answered, and enough metadata to support grounded responses with file references.

### Conceptual fields

- **Role:** User or assistant
- **Content:** The message text
- **Timestamps:** When the message was created
- **Source references:** For assistant messages, the files or chunks used to produce the answer
- **Optional retrieval metadata:** Which chunks were selected during context assembly, if stored for transparency or debugging

User messages contain questions about the repository. Assistant messages contain generated explanations grounded in retrieved code context. See [LLM Response Generation](AI_PIPELINE.md#llm-response-generation).

### Relationship to Conversation

Each Message belongs to exactly one Conversation. Messages are ordered within a conversation to preserve chat history.

---

# Entity Relationships

The schema separates repository indexing data from conversational data. Both branches connect through Project.

## Indexing and search path

Project
|
+-- File
    |
    +-- Code Chunk
        |
        +-- Embedding

**Reading the hierarchy:**

- A **Project** represents one uploaded repository.
- Each **File** in that repository is tracked as a child of the Project.
- Each **Code Chunk** is a searchable segment of a File.
- Each **Embedding** is the vector form of a Code Chunk used for semantic retrieval.

This chain supports the [ingestion pipeline](AI_PIPELINE.md#pipeline-flow) from repository upload through vector storage, and the query pipeline from [semantic search](AI_PIPELINE.md#vector-retrieval) back to [file references](AI_PIPELINE.md#llm-response-generation).

## Conversation path

Project
|
+-- Conversation
    |
    +-- Message

**Reading the hierarchy:**

- A **Project** is the scope for all chat activity about that repository.
- Each **Conversation** groups a sequence of related interactions.
- Each **Message** records one user question or one AI response.

Assistant messages may reference Files and Code Chunks retrieved during response generation, linking the conversation domain back to the indexing domain without merging the two hierarchies.

## How the paths connect at runtime

When a user asks a question:

1. The system identifies the [Project](#project) and [Conversation](#conversation)
2. The question is embedded and compared against [Embeddings](#embedding) scoped to that Project
3. Relevant [Code Chunks](#code-chunk) and their parent [Files](#file) are retrieved
4. The LLM generates a [Message](#message) using that context
5. The assistant Message stores file references pointing back to indexed repository data

See the full [query path](AI_PIPELINE.md#pipeline-flow) in the AI pipeline design.

This design keeps indexing data stable and reusable while conversations remain a separate, append-only history.

---

# Future Considerations

The MVP schema is intentionally focused. Several extensions may be added as the product matures.

## Users and authentication

Future versions may introduce User accounts so projects, conversations, and uploads are owned, private, and accessible only to authorized people. This would add ownership fields to Project and Conversation and likely require access control across all entities.

## Repository versions

The MVP treats a Project as a snapshot of one uploaded repository. Later, CodeContext may support multiple versions of the same repository over time, allowing comparisons between indexed states and historical Q&A against specific versions.

## File change tracking

Incremental indexing could track which Files changed between uploads or syncs using content hashes and update only affected Chunks and Embeddings. This would reduce re-indexing cost and keep search results current. See [Reusing embeddings](AI_PIPELINE.md#reusing-embeddings).

## Indexing jobs

Background workers and job records could manage long-running ingestion tasks, retries, progress reporting, and failure recovery. Job entities would complement Project indexing status fields for larger repositories. See [Background indexing jobs](AI_PIPELINE.md#background-indexing-jobs).

## Permissions

Multi-user deployments may require project-level roles, shared access, read-only viewers, and audit trails. Permissions would extend the schema beyond the single-user MVP assumption.

These additions should build on the current entity model rather than replace it. The Project → File → Code Chunk → Embedding chain and the Project → Conversation → Message chain provide a stable foundation for future growth.
