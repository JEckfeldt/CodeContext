"use client";

import { DownloadMarkdownButton } from "@/components/agent/DownloadMarkdownButton";
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
    typeof artifact === "object" &&
    "components" in artifact &&
    Array.isArray(artifact.components)
  );
}

function getDownloadFilename(result: AgentRunResponse): string {
  switch (result.artifact_type) {
    case "architecture_report":
      return "architecture-report.md";
    case "findings_report":
      return "findings-report.md";
    case "roadmap_report":
      return "roadmap-report.md";
    default:
      return "agent-report.md";
  }
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

  const markdownContent = result.answer?.trim() ?? "";
  const hasMarkdown = markdownContent.length > 0;

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
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
          <p className="text-sm font-medium text-foreground">Answer</p>
          {hasMarkdown ? (
            <DownloadMarkdownButton
              markdown={markdownContent}
              filename={getDownloadFilename(result)}
            />
          ) : null}
        </div>
        {hasMarkdown ? (
          <MarkdownRenderer markdown={markdownContent} />
        ) : (
          <p className="text-sm text-muted">No answer content was returned.</p>
        )}
      </div>

      <ToolTrace toolCalls={result.tool_calls} />
    </div>
  );
}
