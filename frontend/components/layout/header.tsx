import { Badge } from "@/components/ui/badge";

export function Header() {
  return (
    <header className="flex h-16 items-center justify-between border-b border-border bg-surface/80 px-6 backdrop-blur-sm">
      <div className="min-w-0">
        <p className="text-xs font-medium uppercase tracking-[0.18em] text-muted-foreground">
          Workspace
        </p>
        <p className="truncate text-sm text-muted">
          Explore repositories, search code, and ask grounded questions.
        </p>
      </div>

      <div className="flex items-center gap-3">
        <Badge variant="primary">Foundation preview</Badge>
      </div>
    </header>
  );
}
