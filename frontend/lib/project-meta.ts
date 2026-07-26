import type { FileRecord, Project } from "@/types";

export type ImportSourceType = "git" | "zip" | "file";

export type ProjectSnapshot = {
  fileCount: number;
  chunkCount: number;
  sourceCount: number;
  embeddingCount: number;
  sourceBadges: string[];
  lastIngestStatus: string;
  lastIndexedAt: string | null;
};

const BADGE_ORDER = ["Git", "ZIP", "PDF", "Markdown", "Text", "Files"] as const;

export function emptyProjectSnapshot(lastIngestStatus = "pending"): ProjectSnapshot {
  return {
    fileCount: 0,
    chunkCount: 0,
    sourceCount: 0,
    embeddingCount: 0,
    sourceBadges: [],
    lastIngestStatus,
    lastIndexedAt: null,
  };
}

export function deriveSourceBadges(
  files: FileRecord[],
  importTypes: Iterable<ImportSourceType>,
): string[] {
  const badges = new Set<string>();

  for (const importType of importTypes) {
    if (importType === "git") badges.add("Git");
    if (importType === "zip") badges.add("ZIP");
    if (importType === "file") badges.add("Files");
  }

  for (const file of files) {
    const extension = (file.extension ?? "").toLowerCase();
    if (extension === "pdf") badges.add("PDF");
    else if (extension === "md" || extension === "markdown") badges.add("Markdown");
    else if (extension === "txt") badges.add("Text");
  }

  return BADGE_ORDER.filter((badge) => badges.has(badge));
}

export function snapshotFromProject(
  project: Project,
  options?: {
    files?: FileRecord[];
    importTypes?: Iterable<ImportSourceType>;
    lastIngestStatus?: string;
  },
): ProjectSnapshot {
  const files = options?.files ?? [];
  const importTypes = options?.importTypes ?? [];

  return {
    fileCount: project.stats.file_count,
    chunkCount: project.stats.chunk_count,
    sourceCount: project.stats.source_count,
    embeddingCount: project.stats.embedding_count,
    sourceBadges: deriveSourceBadges(files, importTypes),
    lastIngestStatus:
      options?.lastIngestStatus ??
      (project.stats.file_count > 0 ? "indexed" : "pending"),
    lastIndexedAt: project.stats.last_indexed_at,
  };
}
