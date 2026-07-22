import { CodeBlock } from "@/components/content/code-block";
import { Badge } from "@/components/ui/badge";
import { isSnippetTruncated, truncateCodeSnippet } from "@/lib/truncate-snippet";
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
  const displayContent = truncateCodeSnippet(hit.content);
  const truncated = isSnippetTruncated(hit.content);

  return (
    <article className="surface-assistant space-y-3 p-4 sm:p-5">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between sm:gap-3">
        <div className="min-w-0 flex-1 space-y-1">
          <p
            className="break-all font-mono text-sm font-medium text-foreground sm:truncate"
            title={hit.file_path}
          >
            {hit.file_path}
          </p>
          <p className="text-xs leading-5 text-muted-foreground">
            {formatLineRange(hit.start_line, hit.end_line)}
            {hit.symbol_name ? (
              <>
                {" · "}
                <span className="font-mono text-foreground">{hit.symbol_name}</span>
              </>
            ) : null}
          </p>
        </div>
        <Badge variant="primary" className="w-fit shrink-0">
          {formatSimilarity(hit.similarity)}
        </Badge>
      </div>
      <CodeBlock code={displayContent} className="my-0 max-h-[min(280px,40vh)]" />
      {truncated ? (
        <p className="text-[11px] text-muted-foreground">Snippet truncated for display.</p>
      ) : null}
    </article>
  );
}
