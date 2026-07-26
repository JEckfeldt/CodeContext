import { ProjectStats } from "@/components/projects/ProjectStats";
import { formatRelativeTime } from "@/lib/format-relative-time";
import type { ProjectSnapshot } from "@/lib/project-meta";
import type { Project } from "@/types";

type ProjectOverviewProps = {
  project: Project;
  snapshot: ProjectSnapshot;
};

function formatOptionalCount(value: number | null, singular: string, plural: string): string {
  if (value === null) return "—";
  return `${value.toLocaleString()} ${value === 1 ? singular : plural}`;
}

function formatEmbeddingsStatus(enabled: boolean | null): { value: string; placeholder: boolean } {
  if (enabled === null) {
    return { value: "Unknown", placeholder: true };
  }
  return { value: enabled ? "Enabled" : "Disabled", placeholder: false };
}

export function ProjectOverview({ project, snapshot }: ProjectOverviewProps) {
  const lastIndexed = snapshot.lastIndexedAt ?? project.updated_at;
  const embeddings = formatEmbeddingsStatus(snapshot.embeddingsEnabled);

  const stats = [
    {
      label: "Files",
      value: formatOptionalCount(snapshot.fileCount, "file", "files"),
    },
    {
      label: "Chunks",
      value: formatOptionalCount(snapshot.chunkCount, "chunk", "chunks"),
      hint: snapshot.chunkCount === null ? "Available after import or stats API" : undefined,
      placeholder: snapshot.chunkCount === null,
    },
    {
      label: "Sources",
      value:
        snapshot.sourceCount !== null
          ? String(snapshot.sourceCount)
          : snapshot.sourceBadges.length > 0
            ? String(snapshot.sourceBadges.length)
            : "—",
      hint: snapshot.sourceCount === null ? "TODO: project_sources API" : undefined,
      placeholder: snapshot.sourceCount === null && snapshot.sourceBadges.length === 0,
    },
    {
      label: "Last indexed",
      value: snapshot.fileCount > 0 ? formatRelativeTime(lastIndexed) : "Not indexed",
      placeholder: snapshot.fileCount === 0,
    },
    {
      label: "Embeddings",
      value: embeddings.value,
      hint: embeddings.placeholder ? "TODO: backend project settings" : undefined,
      placeholder: embeddings.placeholder,
    },
  ];

  return (
    <div className="space-y-4">
      <div>
        <p className="section-label">Overview</p>
        <p className="section-title mt-1">Project metrics</p>
        {snapshot.sourceBadges.length > 0 ? (
          <p className="mt-1 text-sm text-muted">{snapshot.sourceBadges.join(" · ")}</p>
        ) : null}
      </div>
      <ProjectStats items={stats} />
    </div>
  );
}
