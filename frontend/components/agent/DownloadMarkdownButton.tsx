"use client";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/cn";

type DownloadMarkdownButtonProps = {
  markdown: string;
  filename: string;
  disabled?: boolean;
  className?: string;
};

function sanitizeFilename(filename: string): string {
  const trimmed = filename.trim();
  const baseName = trimmed || "agent-report";
  const withExtension = baseName.toLowerCase().endsWith(".md") ? baseName : `${baseName}.md`;

  return withExtension
    .replace(/[^a-zA-Z0-9._-]+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");
}

export function DownloadMarkdownButton({
  markdown,
  filename,
  disabled = false,
  className,
}: DownloadMarkdownButtonProps) {
  const hasContent = markdown.trim().length > 0;

  function handleDownload() {
    const content = markdown.trim();
    if (!content) return;

    const safeFilename = sanitizeFilename(filename);
    const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
    const objectUrl = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = objectUrl;
    link.download = safeFilename;
    link.rel = "noopener";
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(objectUrl);
  }

  return (
    <Button
      type="button"
      variant="outline"
      size="sm"
      className={cn("shrink-0", className)}
      disabled={disabled || !hasContent}
      onClick={handleDownload}
      aria-label={`Download ${sanitizeFilename(filename)}`}
    >
      Download Markdown
    </Button>
  );
}
