import { Badge } from "@/components/ui/badge";

type RepositoryBarProps = {
  name: string;
  sourceLabel: string;
  fileCount: number;
  languages: string[];
};

export function RepositoryBar({
  name,
  sourceLabel,
  fileCount,
  languages,
}: RepositoryBarProps) {
  return (
    <div className="surface-repository space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="min-w-0">
          <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-primary">
            Active repository
          </p>
          <p className="mt-1 truncate font-mono text-sm font-medium text-foreground">
            {name}
          </p>
          <p className="mt-1 text-sm text-muted">
            {sourceLabel} · {fileCount} files · Ready for questions
          </p>
        </div>
        <Badge variant="secondary">Indexed</Badge>
      </div>
      <div className="flex flex-wrap gap-2">
        {languages.map((language) => (
          <Badge key={language} variant="outline">
            {language}
          </Badge>
        ))}
      </div>
    </div>
  );
}
