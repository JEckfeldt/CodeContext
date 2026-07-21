import { CodeBlock } from "@/components/content/code-block";

type FileReferenceProps = {
  path: string;
  snippet: string;
  language?: string;
};

export function FileReference({ path, snippet, language }: FileReferenceProps) {
  const inferredLanguage =
    language ?? path.split(".").pop()?.replace("tsx", "typescript") ?? "code";

  return (
    <div className="space-y-2">
      <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
        Referenced file
      </p>
      <CodeBlock path={path} language={inferredLanguage} code={snippet} />
    </div>
  );
}
