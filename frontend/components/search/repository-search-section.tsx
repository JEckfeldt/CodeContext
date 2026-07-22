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
    <section className="flex min-h-0 flex-1 flex-col" aria-labelledby="repository-search-heading">
      <div className="mb-4">
        <p id="repository-search-heading" className="section-label">
          Search
        </p>
        <p className="mt-1 text-sm text-muted">
          Search your project for relevant files, documents, and code.
        </p>
      </div>

      <div
        className="mb-5 min-h-[8rem] flex-1 space-y-3 overflow-y-auto"
        aria-live="polite"
        aria-busy={status === "loading"}
      >
        {showIntro ? (
          <div className="space-y-2">
            <p className="text-sm font-medium text-foreground">Search your project</p>
            <p className="text-sm leading-relaxed text-muted">
              Search across your indexed project to quickly find relevant files, documents,
              and code snippets.
            </p>
          </div>
        ) : null}

        {status === "loading" ? (
          <div className="status-banner">
            <p className="text-sm text-muted">Searching your project…</p>
          </div>
        ) : null}

        {status === "error" && error ? (
          <div className="status-banner status-banner-error text-sm" role="alert">
            {error}
          </div>
        ) : null}

        {showEmptyResults ? (
          <div className="status-banner">
            <p className="text-sm text-muted">
              No matches for &ldquo;{submittedQuery}&rdquo;. Try different keywords or a
              shorter phrase.
            </p>
          </div>
        ) : null}

        {results.length > 0 ? (
          <div className="space-y-3">
            <p className="text-sm text-muted-foreground">
              {results.length} result{results.length === 1 ? "" : "s"} for &ldquo;
              {submittedQuery}&rdquo;
            </p>
            <ul className="space-y-3">
              {results.map((hit, index) => (
                <li key={`${hit.file_path}-${hit.start_line}-${hit.end_line}-${index}`}>
                  <SearchResultCard hit={hit} />
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </div>

      <form onSubmit={(event) => void handleSearch(event)} className="mt-auto pt-2">
        <div className="composer">
          <label htmlFor="repository-search-query" className="sr-only">
            Search your project
          </label>
          <textarea
            id="repository-search-query"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder={
              disabled
                ? "Upload a project to start searching..."
                : "Search for files, functions, classes, topics, or keywords..."
            }
            disabled={disabled || status === "loading"}
            rows={3}
            className={cn(
              "w-full min-w-0 resize-none border-0 bg-transparent px-0.5 py-1 text-sm leading-relaxed text-foreground outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:text-muted sm:text-[0.9375rem]",
            )}
          />
          <div className="mt-3 flex flex-col gap-2 border-t border-border-subtle pt-3 sm:flex-row sm:justify-end">
            <Button
              type="submit"
              variant="primary"
              className="w-full sm:w-auto"
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
