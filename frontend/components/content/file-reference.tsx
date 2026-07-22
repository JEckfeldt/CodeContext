import { CodeBlock } from "@/components/content/code-block";

type FileReferenceProps = {
  path: string;
  snippet: string;
  language?: string;
  startLine?: number;
  endLine?: number;
  symbolName?: string | null;
  citationIndex?: number;
};

function formatLineRange(startLine: number, endLine: number): string {
  if (startLine === endLine) {
    return `Line ${startLine}`;
  }
  return `Lines ${startLine}–${endLine}`;
}

export function FileReference({
  path,
  snippet,
  language,
  startLine,
  endLine,
  symbolName,
  citationIndex,
}: FileReferenceProps) {
  const inferredLanguage =
    language ?? path.split(".").pop()?.replace("tsx", "typescript") ?? "code";

  const hasLocation = startLine !== undefined && endLine !== undefined;

  return (
    <div className="rounded-lg border border-border-subtle bg-secondary-muted/40 p-3 sm:p-4">
      <div className="mb-2 space-y-1">
        <p className="text-xs font-medium text-muted-foreground">
          {citationIndex !== undefined
            ? `Source [${citationIndex}]`
            : "Referenced file"}
        </p>
        {hasLocation ? (
          <p className="font-mono text-xs text-muted">
            {formatLineRange(startLine, endLine)}
            {symbolName ? (
              <>
                {" · "}
                <span className="text-foreground">{symbolName}</span>
              </>
            ) : null}
          </p>
        ) : null}
      </div>
      <CodeBlock path={path} language={inferredLanguage} code={snippet} className="my-0" />
    </div>
  );
}
