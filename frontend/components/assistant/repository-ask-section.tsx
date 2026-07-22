"use client";

import { useState } from "react";

import { AssistantResponse } from "@/components/content/assistant-response";
import { Button } from "@/components/ui/button";
import { askProject } from "@/lib/api";
import { cn } from "@/lib/cn";
import type { SourceCitation } from "@/types";

type RepositoryAskSectionProps = {
  projectId: string;
  disabled?: boolean;
};

export function RepositoryAskSection({
  projectId,
  disabled = false,
}: RepositoryAskSectionProps) {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [citations, setCitations] = useState<SourceCitation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submittedQuestion, setSubmittedQuestion] = useState<string | null>(null);

  async function handleAsk(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = question.trim();
    if (!trimmed || disabled || loading) return;

    setLoading(true);
    setError(null);
    setSubmittedQuestion(trimmed);

    try {
      const response = await askProject(projectId, { question: trimmed });
      setAnswer(response.answer);
      setCitations(response.citations);
    } catch (err) {
      setAnswer(null);
      setCitations([]);
      setError(err instanceof Error ? err.message : "Could not get an answer.");
    } finally {
      setLoading(false);
    }
  }

  const showIntro = !loading && answer === null && !error;

  return (
    <section
      className="mt-12 border-t border-border pt-10"
      aria-labelledby="repository-ask-heading"
    >
      <p
        id="repository-ask-heading"
        className="mb-4 text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground"
      >
        Ask CodeContext
      </p>

      <div
        className="mb-8 min-h-[8rem] space-y-4"
        aria-live="polite"
        aria-busy={loading}
      >
        {showIntro ? (
          <p className="max-w-[68ch] text-sm leading-7 text-muted">
            Ask a question about the loaded repository. Answers use retrieved code
            snippets and citations. Requires{" "}
            <span className="font-mono text-xs text-foreground">EMBEDDING_ENABLED</span>,{" "}
            <span className="font-mono text-xs text-foreground">LLM_ENABLED</span>, and{" "}
            <span className="font-mono text-xs text-foreground">OPENAI_API_KEY</span>.
          </p>
        ) : null}

        {loading ? (
          <div className="rounded-lg border border-border bg-surface px-4 py-3">
            <p className="text-sm leading-7 text-muted">Generating an answer…</p>
          </div>
        ) : null}

        {error ? (
          <div
            className="rounded-lg border border-red-200 bg-red-50 px-4 py-3"
            role="alert"
          >
            <p className="text-sm leading-7 text-red-800">{error}</p>
          </div>
        ) : null}

        {answer !== null && !loading ? (
          <div className="space-y-3">
            {submittedQuestion ? (
              <p className="text-sm text-muted">
                Answer for &ldquo;{submittedQuestion}&rdquo;
              </p>
            ) : null}
            <AssistantResponse markdown={answer} citations={citations} />
          </div>
        ) : null}
      </div>

      <form onSubmit={(event) => void handleAsk(event)}>
        <div className="composer">
          <label htmlFor="repository-ask-question" className="sr-only">
            Ask a question about the repository
          </label>
          <textarea
            id="repository-ask-question"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder={
              disabled
                ? "Load a repository to ask questions..."
                : "How does authentication work in this project?"
            }
            disabled={disabled || loading}
            rows={3}
            className={cn(
              "w-full resize-none border-0 bg-transparent px-1 py-1 text-[0.9375rem] leading-7 text-foreground outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:text-muted",
            )}
          />
          <div className="mt-3 flex justify-end border-t border-border-subtle pt-3">
            <Button
              type="submit"
              variant="brand"
              disabled={disabled || loading || !question.trim()}
            >
              {loading ? "Asking…" : "Ask"}
            </Button>
          </div>
        </div>
      </form>
    </section>
  );
}
