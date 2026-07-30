"use client";

import { useState } from "react";

import { AgentRunForm } from "@/components/agent/AgentRunForm";
import { AgentRunResult } from "@/components/agent/AgentRunResult";
import { runAgent } from "@/lib/api";
import { formatAssistantErrorMessage } from "@/lib/format-assistant-error";
import type { AgentRunResponse } from "@/types";

type AgentSectionProps = {
  projectId: string;
  disabled?: boolean;
};

export function AgentSection({ projectId, disabled = false }: AgentSectionProps) {
  const [goal, setGoal] = useState("");
  const [taskTemplate, setTaskTemplate] = useState("architecture_review");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AgentRunResponse | null>(null);
  const [submittedGoal, setSubmittedGoal] = useState<string | null>(null);

  async function handleRun() {
    const trimmedGoal = goal.trim();
    if (!trimmedGoal || disabled || loading) return;

    setLoading(true);
    setError(null);
    setSubmittedGoal(trimmedGoal);

    try {
      const response = await runAgent(projectId, {
        goal: trimmedGoal,
        task_template: taskTemplate,
      });
      setResult(response);
    } catch (err) {
      setResult(null);
      setError(
        err instanceof Error
          ? formatAssistantErrorMessage(err.message)
          : "Could not run the analysis agent.",
      );
    } finally {
      setLoading(false);
    }
  }

  const showIntro = !loading && result === null && !error;

  return (
    <section className="flex min-h-0 flex-1 flex-col" aria-labelledby="agent-section-heading">
      <div className="mb-4">
        <p id="agent-section-heading" className="section-label">
          Agent
        </p>
        <p className="mt-1 text-sm text-muted">
          Run a multi-step analysis agent that searches the repository, inspects files, and
          returns a structured report with tool trace details.
        </p>
      </div>

      <div
        className="mb-5 min-h-[8rem] flex-1 space-y-3 overflow-y-auto"
        aria-live="polite"
        aria-busy={loading}
      >
        {showIntro ? (
          <div className="space-y-2">
            <p className="text-sm font-medium text-foreground">Repository analysis agent</p>
            <p className="text-sm leading-relaxed text-muted">
              Choose a task template, describe your goal, and the agent will gather evidence
              from indexed project content before producing an answer.
            </p>
          </div>
        ) : null}

        {loading ? (
          <div className="status-banner">
            <p className="text-sm text-muted">
              Agent is searching and analyzing your repository. This may take a moment…
            </p>
          </div>
        ) : null}

        {error ? (
          <div className="status-banner status-banner-error text-sm" role="alert">
            {error}
          </div>
        ) : null}

        {result && !loading ? (
          <AgentRunResult result={result} submittedGoal={submittedGoal ?? goal.trim()} />
        ) : null}
      </div>

      <AgentRunForm
        goal={goal}
        taskTemplate={taskTemplate}
        loading={loading}
        disabled={disabled}
        onGoalChange={setGoal}
        onTaskTemplateChange={setTaskTemplate}
        onSubmit={() => void handleRun()}
      />
    </section>
  );
}
