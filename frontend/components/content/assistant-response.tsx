import { FileReference } from "@/components/content/file-reference";
import { MarkdownContent } from "@/components/content/markdown-content";
import { cn } from "@/lib/cn";
import type { SourceCitation } from "@/types";

type LegacyReference = {
  path: string;
  snippet: string;
};

type AssistantResponseProps = {
  markdown: string;
  /** @deprecated Prefer `citations` from the ask API. */
  references?: LegacyReference[];
  citations?: SourceCitation[];
  className?: string;
};

function citationKey(citation: SourceCitation): string {
  return `${citation.index}-${citation.file_path}-${citation.start_line}-${citation.end_line}`;
}

export function AssistantResponse({
  markdown,
  references,
  citations,
  className,
}: AssistantResponseProps) {
  const showCitations = citations && citations.length > 0;
  const showLegacy = !showCitations && references && references.length > 0;

  return (
    <div className={cn("surface-assistant space-y-5 rounded-lg border border-border p-4 sm:p-5", className)}>
      <MarkdownContent content={markdown} />
      {showCitations ? (
        <div className="space-y-4 border-t border-[color-mix(in_srgb,var(--accent-purple)_14%,var(--border))] pt-4">
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">
            Sources
          </p>
          {citations.map((citation) => (
            <FileReference
              key={citationKey(citation)}
              path={citation.file_path}
              snippet={citation.snippet}
              startLine={citation.start_line}
              endLine={citation.end_line}
              symbolName={citation.symbol_name}
              citationIndex={citation.index}
            />
          ))}
        </div>
      ) : null}
      {showLegacy ? (
        <div className="space-y-4 border-t border-[color-mix(in_srgb,var(--accent-purple)_14%,var(--border))] pt-4">
          {references.map((reference, index) => (
            <FileReference
              key={`${reference.path}-${index}`}
              path={reference.path}
              snippet={reference.snippet}
            />
          ))}
        </div>
      ) : null}
    </div>
  );
}
