"use client";

import { useState } from "react";

import { SearchResultCard } from "@/components/search/search-result-card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/cn";
import { searchProject } from "@/lib/api";
import type { ChunkSearchHit } from "@/types";

type RepositorySearchSectionProps = {
  projectId: string;
  disabled?: boolean;
};

type SearchStatus = "idle" | "loading" | "success" | "error";

export function RepositorySearchSection({
  projectId,
  disabled = false,
}: RepositorySearchSectionProps) {
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState<SearchStatus>("idle");
  const [error, setError] = useState<string | null>(null);
  const [submittedQuery, setSubmittedQuery] = useState<string | null>(null);
  const [results, setResults] = useState<ChunkSearchHit[]>([]);

  async function handleSearch(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = query.trim();
    if (!trimmed || disabled) return;

    setStatus("loading");
    setError(null);
    setSubmittedQuery(trimmed);

    try {
      const response = await searchProject(projectId, trimmed);
      setResults(response.results);
      setStatus("success");
    } catch (err) {
      setResults([]);
      setStatus("error");
      setError(err instanceof Error ? err.message : "Search failed.");
    }
  }

  const showIntro = status === "idle" && results.length === 0 && !error;
  const showEmptyResults =
    status === "success" && submittedQuery !== null && results.length === 0;

  return (
    <section className="flex flex-1 flex-col" aria-labelledby="repository-search-heading">
      <p
        id="repository-search-heading"
        className="mb-4 text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground"
      >
        Search repository
      </p>

      <div
        className="mb-8 min-h-[10rem] space-y-4"
        aria-live="polite"
        aria-busy={status === "loading"}
      >
        {showIntro ? (
          <p className="max-w-[68ch] text-sm leading-7 text-muted">
            Search indexed code with natural language. Results use semantic similarity
            over ingested chunks. Enable{" "}
            <span className="font-mono text-xs text-foreground">EMBEDDING_ENABLED</span>{" "}
            and re-upload so vectors exist for search.
          </p>
        ) : null}

        {status === "loading" ? (
          <div className="rounded-lg border border-border bg-surface px-4 py-3">
            <p className="text-sm leading-7 text-muted">Searching the repository…</p>
          </div>
        ) : null}

        {status === "error" && error ? (
          <div
            className="rounded-lg border border-red-200 bg-red-50 px-4 py-3"
            role="alert"
          >
            <p className="text-sm leading-7 text-red-800">{error}</p>
          </div>
        ) : null}

        {showEmptyResults ? (
          <div className="rounded-lg border border-border bg-surface px-4 py-3">
            <p className="text-sm leading-7 text-muted">
              No matching chunks for &ldquo;{submittedQuery}&rdquo;. Try a different
              phrase, confirm embeddings were created on upload, or broaden your
              question.
            </p>
          </div>
        ) : null}

        {results.length > 0 ? (
          <div className="space-y-4">
            <p className="text-sm text-muted">
              {results.length} result{results.length === 1 ? "" : "s"} for &ldquo;
              {submittedQuery}&rdquo;
            </p>
            <ul className="space-y-4">
              {results.map((hit, index) => (
                <li key={`${hit.file_path}-${hit.start_line}-${hit.end_line}-${index}`}>
                  <SearchResultCard hit={hit} />
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </div>

      <form
        onSubmit={(event) => void handleSearch(event)}
        className="sticky bottom-0 mt-auto border-t border-border bg-background/95 pt-5 backdrop-blur-sm"
      >
        <div className="composer">
          <label htmlFor="repository-search-query" className="sr-only">
            Search the repository
          </label>
          <textarea
            id="repository-search-query"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder={
              disabled
                ? "Load a repository to search..."
                : "Where is authentication implemented?"
            }
            disabled={disabled || status === "loading"}
            rows={3}
            className={cn(
              "w-full resize-none border-0 bg-transparent px-1 py-1 text-[0.9375rem] leading-7 text-foreground outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:text-muted",
            )}
          />
          <div className="mt-3 flex justify-end border-t border-border-subtle pt-3">
            <Button
              type="submit"
              variant="brand"
              disabled={disabled || status === "loading" || !query.trim()}
            >
              {status === "loading" ? "Searching…" : "Search"}
            </Button>
          </div>
        </div>
      </form>
    </section>
  );
}
