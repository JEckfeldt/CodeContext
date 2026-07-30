"use client";

import { MarkdownRenderer } from "@/components/agent/MarkdownRenderer";
import { ToolTrace } from "@/components/agent/ToolTrace";
import { Badge } from "@/components/ui/badge";
import type { AgentRunResponse, ArchitectureReportArtifact } from "@/types";

type AgentRunResultProps = {
  result: AgentRunResponse;
  submittedGoal: string;
};

function isArchitectureReport(
  artifact: AgentRunResponse["artifact"],
): artifact is ArchitectureReportArtifact {
  return (
    artifact !== null &&
    artifact !== undefined &&
    typeof artifact.title === "string" &&
    typeof artifact.summary === "string" &&
    Array.isArray(artifact.components)
  );
}

function ArchitectureReportView({ artifact }: { artifact: ArchitectureReportArtifact }) {
  return (
    <div className="rounded-md border border-border bg-surface px-4 py-4">
      <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        Architecture report
      </p>
      <h3 className="mt-2 text-base font-semibold text-foreground">{artifact.title}</h3>
      <p className="mt-2 text-sm leading-relaxed text-muted">{artifact.summary}</p>
      {artifact.components.length > 0 ? (
        <ul className="mt-4 space-y-3">
          {artifact.components.map((component) => (
            <li
              key={component.name}
              className="rounded-md border border-border-subtle bg-secondary-muted/30 px-3 py-3"
            >
              <p className="text-sm font-medium text-foreground">{component.name}</p>
              <p className="mt-1 text-sm text-muted">{component.description}</p>
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}

export function AgentRunResult({ result, submittedGoal }: AgentRunResultProps) {
  const architectureArtifact =
    result.artifact_type === "architecture_report" && isArchitectureReport(result.artifact)
      ? result.artifact
      : null;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        <p className="text-sm text-muted-foreground">
          Analysis for &ldquo;{submittedGoal}&rdquo;
        </p>
        <Badge variant="secondary">{result.steps_taken} steps</Badge>
      </div>

      {architectureArtifact ? (
        <ArchitectureReportView artifact={architectureArtifact} />
      ) : null}

      <div className="rounded-md border border-border-subtle bg-surface px-4 py-4">
        <p className="mb-3 text-sm font-medium text-foreground">Answer</p>
        <MarkdownRenderer markdown={result.answer} />
      </div>

      <ToolTrace toolCalls={result.tool_calls} />
    </div>
  );
}
