import { PageContainer } from "@/components/layout/page-container";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const settingsSections = [
  {
    title: "Workspace",
    description: "General preferences for the CodeContext developer workspace.",
    items: ["Default project view", "File tree density", "Language display"],
  },
  {
    title: "Integrations",
    description: "Future connections for repositories, models, and deployment environments.",
    items: ["Repository providers", "Embedding provider", "LLM provider"],
  },
  {
    title: "Privacy",
    description: "Controls for stored repository content and conversation history.",
    items: ["Data retention", "Upload storage", "Conversation history"],
  },
];

export default function SettingsPage() {
  return (
    <PageContainer
      title="Settings"
      description="Configure workspace preferences and prepare integrations for upcoming CodeContext features."
    >
      <div className="space-y-4">
        {settingsSections.map((section) => (
          <Card key={section.title}>
            <CardHeader>
              <div className="flex items-center justify-between gap-3">
                <div>
                  <CardTitle>{section.title}</CardTitle>
                  <CardDescription>{section.description}</CardDescription>
                </div>
                <Badge variant="outline">Coming soon</Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              {section.items.map((item) => (
                <div
                  key={item}
                  className="flex items-center justify-between rounded-lg border border-border-subtle bg-background px-4 py-3"
                >
                  <span className="text-sm text-foreground">{item}</span>
                  <span className="text-xs text-muted-foreground">Placeholder</span>
                </div>
              ))}
            </CardContent>
          </Card>
        ))}
      </div>
    </PageContainer>
  );
}
