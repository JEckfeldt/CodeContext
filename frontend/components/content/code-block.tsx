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
        "my-4 overflow-hidden rounded-md border border-slate-700/80 bg-code-bg shadow-sm",
        className,
      )}
    >
      {path ? (
        <div className="flex items-center justify-between gap-3 border-b border-slate-700/80 bg-code-header px-3 py-2">
          <p className="min-w-0 truncate font-mono text-xs text-code-text">
            <span className="text-blue-300">{path}</span>
          </p>
          {language ? (
            <span className="shrink-0 rounded bg-slate-700 px-2 py-0.5 font-mono text-[10px] uppercase tracking-wide text-slate-300">
              {language}
            </span>
          ) : null}
        </div>
      ) : null}
      <pre className="max-h-[inherit] overflow-x-auto overflow-y-auto px-3 py-3 font-mono text-[0.8125rem] leading-6 text-code-text sm:px-4">
        <code>{code.trimEnd()}</code>
      </pre>
    </div>
  );
}
