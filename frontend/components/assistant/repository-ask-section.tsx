"use client";

import { useState } from "react";

import { AssistantResponse } from "@/components/content/assistant-response";
import { Button } from "@/components/ui/button";
import { askProject } from "@/lib/api";
import { formatAssistantErrorMessage } from "@/lib/format-assistant-error";
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
      setError(
        err instanceof Error
          ? formatAssistantErrorMessage(err.message)
          : "Could not get an explanation.",
      );
    } finally {
      setLoading(false);
    }
  }

  const showIntro = !loading && answer === null && !error;

  return (
    <section className="flex min-h-0 flex-1 flex-col" aria-labelledby="repository-ask-heading">
      <div className="mb-4">
        <p id="repository-ask-heading" className="section-label">
          Explain
        </p>
        <p className="mt-1 text-sm text-muted">
          Ask AI to explain your project using the indexed content and provide grounded
          answers with citations.
        </p>
      </div>

      <div
        className="mb-5 min-h-[8rem] flex-1 space-y-3 overflow-y-auto"
        aria-live="polite"
        aria-busy={loading}
      >
        {showIntro ? (
          <div className="space-y-2">
            <p className="text-sm font-medium text-foreground">Understand your project</p>
            <p className="text-sm leading-relaxed text-muted">
              Ask questions about your project and receive AI explanations backed by source
              citations.
            </p>
          </div>
        ) : null}

        {loading ? (
          <div className="status-banner">
            <p className="text-sm text-muted">Preparing your explanation…</p>
          </div>
        ) : null}

        {error ? (
          <div className="status-banner status-banner-error text-sm" role="alert">
            {error}
          </div>
        ) : null}

        {answer !== null && !loading ? (
          <div className="space-y-3">
            {submittedQuestion ? (
              <p className="text-sm text-muted-foreground">
                Explanation for &ldquo;{submittedQuestion}&rdquo;
              </p>
            ) : null}
            <AssistantResponse markdown={answer} citations={citations} />
            {citations.length === 0 ? (
              <p className="text-sm text-muted">
                No matching sources were found for this question. The explanation may note
                that it could not find enough context in your project.
              </p>
            ) : null}
          </div>
        ) : null}
      </div>

      <form onSubmit={(event) => void handleAsk(event)} className="mt-auto pt-2">
        <div className="composer">
          <label htmlFor="repository-ask-question" className="sr-only">
            Ask for an explanation about your project
          </label>
          <textarea
            id="repository-ask-question"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder={
              disabled
                ? "Upload a project to ask questions..."
                : "Ask how something works, summarize a document, trace a feature, or understand the architecture..."
            }
            disabled={disabled || loading}
            rows={3}
            className={cn(
              "w-full min-w-0 resize-none border-0 bg-transparent px-0.5 py-1 text-sm leading-relaxed text-foreground outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:text-muted sm:text-[0.9375rem]",
            )}
          />
          <div className="mt-3 flex flex-col gap-2 border-t border-border-subtle pt-3 sm:flex-row sm:justify-end">
            <Button
              type="submit"
              variant="brand"
              className="w-full sm:w-auto"
              disabled={disabled || loading || !question.trim()}
            >
              {loading ? "Explaining…" : "Explain"}
            </Button>
          </div>
        </div>
      </form>
    </section>
  );
}
