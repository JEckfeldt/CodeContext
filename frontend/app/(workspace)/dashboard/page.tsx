import { PageContainer } from "@/components/layout/page-container";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";

const overviewItems = [
  { label: "Repositories", value: "0" },
  { label: "Indexed files", value: "0" },
  { label: "Recent searches", value: "0" },
  { label: "Conversations", value: "0" },
];

export default function DashboardPage() {
  return (
    <PageContainer
      title="Dashboard"
      description="A calm overview of your repositories, indexing activity, and upcoming AI workflows."
    >
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {overviewItems.map((item) => (
          <Card key={item.label}>
            <CardContent className="space-y-2 py-5">
              <p className="text-sm text-muted">{item.label}</p>
              <p className="text-3xl font-semibold tracking-tight text-foreground">
                {item.value}
              </p>
            </CardContent>
          </Card>
        ))}
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(0,1.4fr)_minmax(0,1fr)]">
        <Card>
          <CardHeader>
            <CardTitle>Recent repositories</CardTitle>
            <CardDescription>
              Uploaded projects will appear here once ingestion is connected.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <EmptyState
              title="No repositories yet"
              description="Create a project and upload a repository to start exploring source files with CodeContext."
              icon={
                <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" aria-hidden>
                  <path
                    d="M4 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7Z"
                    stroke="currentColor"
                    strokeWidth="1.8"
                  />
                </svg>
              }
              actionLabel="Go to Projects"
              actionHref="/projects"
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Workspace status</CardTitle>
            <CardDescription>
              Foundation UI is ready for upcoming ingestion and search features.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="rounded-xl border border-border-subtle bg-background px-4 py-4">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm font-medium text-foreground">Design system</p>
                  <p className="text-sm text-muted">Shell, components, and page layouts</p>
                </div>
                <Badge variant="primary">Ready</Badge>
              </div>
            </div>
            <div className="rounded-xl border border-border-subtle bg-background px-4 py-4">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm font-medium text-foreground">Repository ingestion</p>
                  <p className="text-sm text-muted">Upload and file discovery workflows</p>
                </div>
                <Badge variant="outline">Planned</Badge>
              </div>
            </div>
            <div className="rounded-xl border border-border-subtle bg-background px-4 py-4">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm font-medium text-foreground">Semantic search</p>
                  <p className="text-sm text-muted">Natural-language code retrieval</p>
                </div>
                <Badge variant="outline">Planned</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </section>
    </PageContainer>
  );
}
