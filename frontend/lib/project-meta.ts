import type { FileRecord } from "@/types";

export type ImportSourceType = "git" | "zip" | "file";

export type ProjectSnapshot = {
  fileCount: number;
  chunkCount: number | null;
  sourceBadges: string[];
  /** TODO: replace with project_sources API count when available */
  sourceCount: number | null;
  lastIngestStatus: string;
  lastIndexedAt: string | null;
  /** TODO: replace with backend project settings when available */
  embeddingsEnabled: boolean | null;
};

const BADGE_ORDER = ["Git", "ZIP", "PDF", "Markdown", "Text", "Files"] as const;

export function emptyProjectSnapshot(lastIngestStatus = "pending"): ProjectSnapshot {
  return {
    fileCount: 0,
    chunkCount: null,
    sourceBadges: [],
    sourceCount: null,
    lastIngestStatus,
    lastIndexedAt: null,
    embeddingsEnabled: null,
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

export function buildProjectSnapshot(input: {
  files: FileRecord[];
  importTypes: Iterable<ImportSourceType>;
  chunkCount?: number | null;
  lastIngestStatus?: string;
  lastIndexedAt?: string | null;
  embeddingsEnabled?: boolean | null;
}): ProjectSnapshot {
  const sourceBadges = deriveSourceBadges(input.files, input.importTypes);

  return {
    fileCount: input.files.length,
    chunkCount: input.chunkCount ?? null,
    sourceBadges,
    sourceCount: sourceBadges.length > 0 ? sourceBadges.length : null,
    lastIngestStatus: input.lastIngestStatus ?? (input.files.length > 0 ? "indexed" : "pending"),
    lastIndexedAt: input.lastIndexedAt ?? null,
    embeddingsEnabled: input.embeddingsEnabled ?? null,
  };
}
