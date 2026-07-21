import { CodeBlock } from "@/components/content/code-block";
import { Badge } from "@/components/ui/badge";
import type { ChunkSearchHit } from "@/types";

type SearchResultCardProps = {
  hit: ChunkSearchHit;
};

function formatLineRange(startLine: number, endLine: number): string {
  if (startLine === endLine) {
    return `Line ${startLine}`;
  }
  return `Lines ${startLine}–${endLine}`;
}

function formatSimilarity(score: number): string {
  return `${(score * 100).toFixed(1)}% match`;
}

export function SearchResultCard({ hit }: SearchResultCardProps) {
  return (
    <article className="surface-assistant space-y-3 rounded-lg border border-border p-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0 space-y-1">
          <p className="truncate font-mono text-sm font-medium text-foreground">
            {hit.file_path}
          </p>
          <p className="text-xs text-muted">
            {formatLineRange(hit.start_line, hit.end_line)}
            {hit.symbol_name ? (
              <>
                {" "}
                · <span className="font-mono text-foreground">{hit.symbol_name}</span>
              </>
            ) : null}
          </p>
        </div>
        <Badge variant="secondary">{formatSimilarity(hit.similarity)}</Badge>
      </div>
      <CodeBlock path={hit.file_path} code={hit.content} className="my-0" />
    </article>
  );
}
