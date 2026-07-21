import { cn } from "@/lib/cn";

type CodeBlockProps = {
  path?: string;
  language?: string;
  code: string;
  className?: string;
};

export function CodeBlock({ path, language, code, className }: CodeBlockProps) {
  return (
    <div
      className={cn(
        "my-4 overflow-hidden rounded-lg border border-[#334155] bg-code-bg",
        className,
      )}
    >
      {path ? (
        <div className="flex items-center justify-between gap-3 border-b border-[#334155] bg-code-header px-3 py-2">
          <p className="truncate font-mono text-xs text-code-text">
            <span className="text-[#93c5fd]">{path}</span>
          </p>
          {language ? (
            <span className="shrink-0 rounded bg-[#334155] px-2 py-0.5 font-mono text-[10px] uppercase tracking-wide text-slate-300">
              {language}
            </span>
          ) : null}
        </div>
      ) : null}
      <pre className="overflow-x-auto px-4 py-3 font-mono text-[0.8125rem] leading-6 text-code-text">
        <code>{code.trimEnd()}</code>
      </pre>
    </div>
  );
}
