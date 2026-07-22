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
      <p className="text-sm text-muted">No files were discovered in this archive.</p>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-border bg-secondary-muted/50">
      <ul className="max-h-[min(360px,45vh)] divide-y divide-border overflow-y-auto">
        {sorted.map((file) => (
          <li
            key={file.id}
            className="flex flex-col gap-1 px-3 py-2.5 transition-colors hover:bg-surface sm:flex-row sm:items-center sm:justify-between sm:gap-4 sm:px-4"
          >
            <code className="min-w-0 break-all font-mono text-[0.8125rem] leading-5 text-foreground">
              {file.path}
            </code>
            <span className="shrink-0 font-mono text-[11px] text-muted-foreground">
              {file.language ?? file.extension ?? "file"} · {formatSize(file.size)}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
