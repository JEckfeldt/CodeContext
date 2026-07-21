import { FileReference } from "@/components/content/file-reference";
import { MarkdownContent } from "@/components/content/markdown-content";
import { cn } from "@/lib/cn";

type AssistantResponseProps = {
  markdown: string;
  references?: Array<{ path: string; snippet: string }>;
  className?: string;
};

export function AssistantResponse({
  markdown,
  references,
  className,
}: AssistantResponseProps) {
  return (
    <div className={cn("surface-assistant space-y-5", className)}>
      <MarkdownContent content={markdown} />
      {references?.length ? (
        <div className="space-y-4 border-t border-[color-mix(in_srgb,var(--accent-purple)_14%,var(--border))] pt-4">
          {references.map((reference) => (
            <FileReference
              key={reference.path}
              path={reference.path}
              snippet={reference.snippet}
            />
          ))}
        </div>
      ) : null}
    </div>
  );
}
