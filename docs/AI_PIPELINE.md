# CodeContext AI Pipeline

## Overview

The AI pipeline is the core knowledge-building and question-answering workflow in CodeContext. It transforms an uploaded software repository into a searchable knowledge base that a Large Language Model (LLM) can use to answer questions about the project.

Most LLMs do not have access to a user's private codebase. Even when they do, sending an entire repository on every request is impractical due to context limits, latency, and cost. The pipeline solves this by indexing the repository once, storing compact semantic representations of the code, and retrieving only the most relevant sections when a user asks a question.

For the MVP, the pipeline supports:

- Uploading a code repository
- Indexing supported project files
- Searching code semantically
- Asking questions about the codebase
- Receiving grounded answers with file references

The pipeline is designed to produce answers grounded in the user's repository rather than relying on general model knowledge alone.

---

# Pipeline Flow

The end-to-end flow connects repository ingestion, semantic search, and LLM response generation.

Repository Upload
|
v
File Discovery
|
v
File Parsing
|
v
Code Chunking
|
v
Embedding Generation
|
v
Vector Storage
|
v
Semantic Retrieval
|
v
Context Assembly
|
v
LLM Generation
|
v
Response with File References

**Ingestion path (indexing):** When a repository is uploaded, the system discovers supported files, parses their contents, splits them into chunks, generates embeddings, and stores the results in PostgreSQL with pgvector.

**Query path (question answering):** When a user asks a question, the system converts the question into an embedding, retrieves similar code chunks from the vector store, assembles a focused context window, sends that context to the LLM, and returns a response that references the source files used.

These two paths are intentionally separate. Indexing work is performed once per repository (or incrementally when files change), while retrieval and generation run on each user question.

---

# Repository Ingestion

Repository ingestion is the first stage of the pipeline. Its job is to read an uploaded repository and identify the files worth indexing.

## Scanning repositories

After upload, the system walks the repository directory structure and collects candidate files. The scan should respect practical boundaries: skip irrelevant directories (such as dependency folders and build output), avoid binary files, and focus on text-based source and configuration content that can be parsed and searched.

For the MVP, ingestion begins with a user-provided repository upload. The pipeline does not assume integrations with external version control systems or continuous indexing beyond what is needed to process the uploaded project.

## Identifying supported files

Not every file in a repository is useful for code understanding. The initial supported set aligns with the MVP scope:

- Python
- JavaScript
- TypeScript
- Markdown
- JSON
- Configuration files

Files outside this set may be ignored during early phases. Each accepted file should retain metadata such as its relative path, file type, and size, which supports later chunking, retrieval, and source referencing.

## Why source code needs specialized handling

Source code differs from normal documents such as PDFs or articles in several important ways:

- **Structure is semantic.** Meaning comes from syntax, imports, function boundaries, and project layout—not from paragraphs alone.
- **Context is distributed.** Understanding one function often requires knowing related files, configuration, and naming conventions elsewhere in the repository.
- **Precision matters.** Small changes in identifiers, paths, or configuration values can completely change behavior.
- **Noise is costly.** Dependencies, generated artifacts, and large binary assets add little value to retrieval but increase storage and search cost.

Because of this, CodeContext treats repositories as structured technical artifacts rather than flat text documents.

---

# Code Parsing

Parsing converts raw file contents into structured text that can be chunked and indexed reliably.

## Why code should not be chunked like a normal PDF

Generic document chunking—splitting text by fixed token counts or paragraph breaks—works poorly for source code. Arbitrary splits can break functions in half, separate imports from the code that uses them, and destroy the logical units developers actually reason about.

If chunks lack coherent boundaries, semantic search may return fragments that look relevant but are impossible to interpret. The LLM then receives incomplete or misleading context, which reduces answer quality and increases the need for larger, more expensive prompts.

## Future support for language-specific parsing

The MVP can begin with file-type-aware text extraction, but the pipeline is designed to evolve toward language-specific parsing. Different languages expose different natural boundaries:

- Python: modules, classes, functions
- JavaScript / TypeScript: modules, components, exports, functions
- Markdown: sections and headings
- JSON and configuration files: logical key groups or whole-file units

Language-aware parsing improves chunk quality without changing the overall pipeline architecture.

## Extracting meaningful units

The goal of parsing is to identify units that a developer would recognize as meaningful, such as:

- Functions and methods
- Classes and modules
- UI components
- Configuration blocks
- Documentation sections

Extracting these units makes downstream chunking, embedding, and retrieval more accurate. Even when the MVP uses simpler parsing initially, the pipeline should preserve file paths and structural hints so chunks remain traceable back to their source.

---

# Chunking Strategy

Chunking divides parsed content into pieces small enough to embed, store, and retrieve efficiently.

## Why large files need to be split

Embedding models and vector indexes work best on focused passages. Large files—common in application codebases—must be split so that retrieval can return specific sections rather than entire files.

Splitting also keeps query-time context windows small. Sending only the most relevant sections to the LLM reduces cost and helps the model focus on material tied to the user's question.

## The importance of preserving context

Effective chunks balance two needs:

- **Specificity:** Each chunk should represent a coherent unit of meaning.
- **Context:** Each chunk should retain enough surrounding information to remain understandable on its own.

At minimum, chunks should preserve metadata such as:

- Repository-relative file path
- File type or language
- Position within the file (start/end line or structural label, when available)

Without this metadata, retrieved results are harder to rank, explain, and reference in the final response.

## Potential chunking strategies for source code

The MVP can start with pragmatic strategies and refine them over time. Planned approaches include:

- **Structure-aware splitting:** Break files at natural boundaries such as functions, classes, or headings when parsing allows it.
- **Size-bounded fallback:** When a logical unit is still too large, split it into smaller segments while keeping shared metadata and overlapping context if needed.
- **Whole-file chunks for small files:** Short configuration or documentation files may be indexed as a single chunk.
- **Path and type hints in metadata:** Store file path and language with every chunk so retrieval results remain interpretable.

Chunking strategy directly affects search quality and should be treated as a core design decision, not a formatting detail.

---

# Embeddings

Embeddings are numerical representations of text that capture semantic meaning in a vector space.

## What embeddings represent

An embedding converts a code chunk—or a user question—into a fixed-length vector. Chunks with similar meaning tend to produce vectors that are close together, even when the exact wording differs.

For example, a question about "database connection setup" should be near chunks containing database URLs, connection pools, ORM configuration, or environment variable definitions.

## Why embeddings are created

Embeddings make the repository searchable by meaning rather than by exact keyword match alone. This is essential for a codebase assistant because developers often ask questions using different terminology than the code uses.

Instead of searching for precise strings, the system can find conceptually related sections across files and languages.

## How they enable semantic search

During indexing, each chunk embedding is stored alongside its source metadata in PostgreSQL with pgvector. During querying, the user's question is embedded using the same model family, and the system searches for the nearest chunk vectors.

Semantic search is the bridge between free-form developer questions and the indexed contents of a repository.

---

# Vector Retrieval

Vector retrieval selects the code chunks most likely to answer a user's question.

## Converting questions into searches

When a user submits a question, the system embeds the question text using the same embedding approach applied during indexing. That query vector is compared against stored chunk vectors to find the closest matches.

This allows natural-language questions such as:

- "Explain authentication"
- "Where is the database connection configured?"
- "How does this API request flow through the application?"

The retrieval layer maps these questions to concrete locations in the codebase.

## Retrieving relevant code chunks

Retrieval returns a ranked set of chunks based on vector similarity. Each result should include the chunk text plus source metadata, especially file path and location within the file, so the system can show references in the final answer.

For the MVP, semantic retrieval is the primary mechanism for finding relevant context. The number of retrieved chunks should be limited to what fits comfortably in the LLM context window while still covering the question.

## Why retrieval reduces LLM costs

Without retrieval, the system would need to send large portions of the repository—or the entire project—to the LLM for every question. That approach scales poorly in both cost and latency.

Retrieval narrows the input to a small, relevant subset of indexed material. The LLM receives only what it needs to answer the question, which reduces token usage and improves response focus.

---

# LLM Response Generation

Once relevant chunks are retrieved, the LLM generates the user-facing answer.

## Providing retrieved context to the LLM

Context assembly combines the user's question with the selected code chunks and supporting instructions. The assembled prompt should make clear that the model must answer using the supplied repository context.

The LLM layer is responsible for turning retrieved fragments into a coherent explanation, summary, or guided answer. Prompt templates live separately from retrieval logic so providers and instructions can change without rewriting the pipeline.

## Why responses should be grounded in repository information

Grounding is a core design principle of CodeContext. Answers should reflect what is actually present in the uploaded repository rather than generic assumptions about how projects are usually built.

Grounded responses are more trustworthy for developers exploring unfamiliar codebases. They reduce hallucinated file paths, invented functions, and misleading architectural claims.

## Why source references are important

File references connect the answer back to evidence in the repository. For the MVP, responses should cite the files used to produce the answer so users can inspect the source directly.

References serve three purposes:

- **Verification:** Users can confirm the answer against real code.
- **Navigation:** Users can jump to the relevant files to continue exploring.
- **Trust:** Source-linked answers are easier to evaluate than unsupported summaries.

References are part of the MVP product experience, not an optional enhancement.

---

# Cost Optimization

The pipeline is designed with cost efficiency in mind from the start. Several strategies reduce repeated work and unnecessary model usage.

## Reusing embeddings

Embeddings are generated during indexing and stored in the database. Once a file chunk has been embedded, that vector should be reused until the underlying content changes. Re-embedding unchanged code on every query would add avoidable cost and latency.

## Caching responses

Repeated or similar questions may produce similar answers. Caching LLM responses—or caching retrieval results for common queries—can reduce provider calls in development and production use. Cache entries should be scoped to a repository and invalidated when indexed content changes.

## Sending only relevant context

Retrieval and context assembly exist primarily to limit prompt size. The LLM should receive only the top-ranked chunks needed to answer the question, not broad repository excerpts or unrelated files.

## Using smaller models when possible

Not every task requires the largest available model. The architecture supports swapping providers and model sizes so simpler operations can use lower-cost models where appropriate, while more complex explanations can use more capable ones. Model selection is a future optimization lever, but the pipeline should remain provider-agnostic from the start.

---

# Future Improvements

The MVP establishes the core ingestion, indexing, search, and question-answering loop. Several enhancements can improve quality, scale, and flexibility in later phases.

## AST-based parsing

Abstract Syntax Tree (AST) parsing can identify code structure more reliably than line-based splitting. This would improve chunk boundaries for Python, JavaScript, TypeScript, and other supported languages.

## Hybrid search (keyword + vector)

Combining vector similarity with keyword or full-text search may improve retrieval for exact identifiers, function names, environment variables, and file paths that users mention explicitly.

## Repository relationship graphs

A graph of imports, module dependencies, and file relationships could help retrieve not only similar chunks, but structurally related code that vector search alone might miss.

## Background indexing jobs

As repositories grow or change, indexing can move to background workers so uploads and re-indexing do not block the API or frontend. This supports better scalability beyond the initial synchronous MVP flow.

## Multiple LLM providers

The pipeline is intended to remain modular. Supporting multiple LLM providers would allow cost, latency, and capability tradeoffs without changing ingestion or retrieval fundamentals.

These improvements extend the MVP pipeline but are not required for the first end-to-end release.
