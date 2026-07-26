import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

type ProjectDashboardEmptyStateProps = {
  onCreateProject: () => void;
};

export function ProjectDashboardEmptyState({
  onCreateProject,
}: ProjectDashboardEmptyStateProps) {
  return (
    <div className="flex justify-center py-6 sm:py-10">
      <Card className="w-full max-w-lg border-dashed shadow-sm">
        <CardContent className="flex flex-col items-center px-6 py-10 text-center sm:px-10 sm:py-12">
          <span
            aria-hidden
            className="brand-mark flex h-12 w-12 items-center justify-center rounded-xl text-lg"
          >
            📁
          </span>
          <h2 className="mt-5 text-lg font-semibold tracking-tight text-foreground sm:text-xl">
            No projects yet
          </h2>
          <p className="mt-2 max-w-sm text-sm leading-relaxed text-muted sm:text-[0.9375rem]">
            Projects are AI workspaces for your code and documents. Create one to import sources,
            index content, and run Search or Explain.
          </p>
          <Button
            type="button"
            variant="primary"
            className="mt-6 h-10 w-full sm:w-auto"
            onClick={onCreateProject}
          >
            + Create project
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
