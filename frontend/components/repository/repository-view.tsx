import { Badge } from "@/components/ui/badge";

type RepositoryViewProps = {
  name: string;
  ingestionStatus: string;
  fileCount: number;
  sourceLabel?: string;
};

function statusLabel(status: string): string {
  if (status === "completed" || status === "indexed") return "Indexed";
  if (status === "failed") return "Failed";
  return status.replace(/_/g, " ");
}

function statusBadgeVariant(status: string): "secondary" | "outline" {
  if (status === "completed" || status === "indexed") return "secondary";
  return "outline";
}

export function RepositoryView({
  name,
  ingestionStatus,
  fileCount,
  sourceLabel = "ZIP upload",
}: RepositoryViewProps) {
  const ready =
    ingestionStatus === "completed" ||
    ingestionStatus === "indexed" ||
    fileCount > 0;

  return (
    <div className="surface-repository">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <p className="section-label">Active project</p>
          <p className="mt-1 truncate font-mono text-sm font-medium text-foreground">
            {name}
          </p>
          <p className="mt-1 text-sm text-muted">
            {sourceLabel} · {fileCount} {fileCount === 1 ? "file" : "files"} ·{" "}
            {ready ? "Ready to search and explain" : statusLabel(ingestionStatus)}
          </p>
        </div>
        <Badge
          variant={statusBadgeVariant(ingestionStatus)}
          className={
            ingestionStatus === "failed"
              ? "border-destructive/30 text-destructive"
              : undefined
          }
        >
          {statusLabel(ingestionStatus)}
        </Badge>
      </div>
    </div>
  );
}
