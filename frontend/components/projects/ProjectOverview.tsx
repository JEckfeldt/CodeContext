import { ProjectStats } from "@/components/projects/ProjectStats";
import { formatRelativeTime } from "@/lib/format-relative-time";
import type { ProjectSnapshot } from "@/lib/project-meta";
import type { Project } from "@/types";

type ProjectOverviewProps = {
  project: Project;
  snapshot: ProjectSnapshot;
};

function formatCount(value: number, singular: string, plural: string): string {
  return `${value.toLocaleString()} ${value === 1 ? singular : plural}`;
}

function formatLastIndexed(lastIndexedAt: string | null): string {
  if (!lastIndexedAt) return "Not indexed yet";
  return formatRelativeTime(lastIndexedAt);
}

function formatEmbeddings(snapshot: ProjectSnapshot): string {
  if (snapshot.chunkCount === 0) return "No chunks indexed";
  if (snapshot.embeddingCount === 0) return "0 embeddings";
  return formatCount(snapshot.embeddingCount, "embedding", "embeddings");
}

export function ProjectOverview({ project, snapshot }: ProjectOverviewProps) {
  const stats = [
    {
      label: "Files",
      value: formatCount(snapshot.fileCount, "file", "files"),
    },
    {
      label: "Chunks",
      value: formatCount(snapshot.chunkCount, "chunk", "chunks"),
    },
    {
      label: "Sources",
      value: formatCount(snapshot.sourceCount, "source", "sources"),
    },
    {
      label: "Last indexed",
      value: formatLastIndexed(snapshot.lastIndexedAt),
      placeholder: !snapshot.lastIndexedAt,
    },
    {
      label: "Embeddings",
      value: formatEmbeddings(snapshot),
      placeholder: snapshot.embeddingCount === 0 && snapshot.chunkCount > 0,
    },
  ];

  return (
    <div className="space-y-4">
      <div>
        <p className="section-label">Overview</p>
        <p className="section-title mt-1">{project.name}</p>
        {snapshot.sourceBadges.length > 0 ? (
          <p className="mt-1 text-sm text-muted">{snapshot.sourceBadges.join(" · ")}</p>
        ) : snapshot.sourceCount > 0 ? (
          <p className="mt-1 text-sm text-muted">
            {formatCount(snapshot.sourceCount, "source", "sources")} indexed
          </p>
        ) : null}
      </div>
      <ProjectStats items={stats} />
    </div>
  );
}
