import type { FileRecord } from "@/types";

type FileBrowserProps = {
  files: FileRecord[];
};

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function FileBrowser({ files }: FileBrowserProps) {
  const sorted = [...files].sort((a, b) => a.path.localeCompare(b.path));

  if (sorted.length === 0) {
    return (
      <p className="text-sm leading-7 text-muted">No source files were discovered in this archive.</p>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-border bg-[#0f172a]">
      <ul className="max-h-[min(420px,50vh)] divide-y divide-white/10 overflow-y-auto">
        {sorted.map((file) => (
          <li
            key={file.id}
            className="flex flex-col gap-0.5 px-3 py-2.5 sm:flex-row sm:items-center sm:justify-between sm:gap-4"
          >
            <code className="min-w-0 break-all font-mono text-[0.8125rem] leading-5 text-slate-100">
              {file.path}
            </code>
            <span className="shrink-0 font-mono text-[11px] text-slate-400">
              {file.language ?? file.extension ?? "file"} · {formatSize(file.size)}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
