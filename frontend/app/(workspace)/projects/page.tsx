import { PageContainer } from "@/components/layout/page-container";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";

export default function ProjectsPage() {
  return (
    <PageContainer
      title="Projects"
      description="Manage uploaded repositories and prepare them for indexing, search, and AI-assisted exploration."
      actions={
        <Button variant="primary" disabled>
          Create project
        </Button>
      }
    >
      <Card>
        <CardHeader>
          <CardTitle>Repository projects</CardTitle>
          <CardDescription>
            Each project represents one codebase you want CodeContext to understand.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <EmptyState
            title="No projects created"
            description="Project creation and repository upload will be available in the next implementation milestone."
            icon={
              <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" aria-hidden>
                <path
                  d="M12 5v14M5 12h14"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                />
              </svg>
            }
            actionLabel="Learn about ingestion"
          />
        </CardContent>
      </Card>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {["Auth service", "Payments API", "Design system"].map((name) => (
          <Card key={name} className="opacity-70">
            <CardContent className="space-y-4 py-5">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="font-medium text-foreground">{name}</p>
                  <p className="font-mono text-xs text-muted-foreground">
                    placeholder/project
                  </p>
                </div>
                <span className="rounded-md bg-border-subtle px-2 py-1 text-xs text-muted">
                  Preview
                </span>
              </div>
              <p className="text-sm leading-6 text-muted">
                Placeholder card showing how indexed repositories will appear in the workspace.
              </p>
              <Button variant="outline" size="sm" disabled>
                Open project
              </Button>
            </CardContent>
          </Card>
        ))}
      </section>
    </PageContainer>
  );
}
