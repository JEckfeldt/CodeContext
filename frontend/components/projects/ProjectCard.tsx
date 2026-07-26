import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { formatRelativeTime } from "@/lib/format-relative-time";
import type { ProjectSnapshot } from "@/lib/project-meta";
import { cn } from "@/lib/cn";
import type { Project } from "@/types";

type ProjectCardProps = {
  project: Project;
  snapshot: ProjectSnapshot;
  selected: boolean;
  onSelect: (project: Project) => void;
};

function formatCount(value: number | null, label: string): string {
  if (value === null) return `— ${label}`;
  return `${value.toLocaleString()} ${label}`;
}

export function ProjectCard({ project, snapshot, selected, onSelect }: ProjectCardProps) {
  const updatedLabel = formatRelativeTime(project.updated_at);
  const badgeLine =
    snapshot.sourceBadges.length > 0 ? snapshot.sourceBadges.join(" • ") : "No sources yet";

  return (
    <button
      type="button"
      onClick={() => onSelect(project)}
      aria-pressed={selected}
      className="group w-full text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:ring-offset-2 focus-visible:ring-offset-background"
    >
      <Card
        className={cn(
          "h-full transition-all duration-150",
          "hover:border-primary/35 hover:shadow-md",
          selected
            ? "border-primary ring-2 ring-primary/20 shadow-md"
            : "border-border",
        )}
      >
        <CardContent className="flex h-full flex-col gap-4 p-4 sm:p-5">
          <div className="flex items-start gap-3">
            <span
              aria-hidden
              className={cn(
                "flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-base",
                selected ? "bg-primary-muted text-primary" : "bg-secondary-muted text-muted",
              )}
            >
              📁
            </span>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-semibold text-foreground">{project.name}</p>
              <p className="mt-1 line-clamp-2 text-xs text-muted">{badgeLine}</p>
            </div>
          </div>

          <div className="flex flex-wrap gap-1.5">
            {snapshot.sourceBadges.length > 0 ? (
              snapshot.sourceBadges.map((badge) => (
                <Badge key={badge} variant={selected ? "primary" : "outline"}>
                  {badge}
                </Badge>
              ))
            ) : (
              <Badge variant="outline">Empty</Badge>
            )}
          </div>

          <div className="mt-auto space-y-1 border-t border-border-subtle pt-3 text-xs text-muted">
            <p>{formatCount(snapshot.fileCount, snapshot.fileCount === 1 ? "File" : "Files")}</p>
            <p>{formatCount(snapshot.chunkCount, snapshot.chunkCount === 1 ? "Chunk" : "Chunks")}</p>
            <p className="text-muted-foreground">Updated {updatedLabel}</p>
          </div>
        </CardContent>
      </Card>
    </button>
  );
}
