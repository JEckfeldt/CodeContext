const DEFAULT_MAX_LINES = 14;
const DEFAULT_MAX_CHARS = 1200;

/** Truncate long code snippets for display while keeping readable previews. */
export function truncateCodeSnippet(
  content: string,
  maxLines: number = DEFAULT_MAX_LINES,
  maxChars: number = DEFAULT_MAX_CHARS,
): string {
  const normalized = content.replace(/\r\n/g, "\n");
  const lines = normalized.split("\n");
  let snippet = lines.slice(0, maxLines).join("\n");

  if (lines.length > maxLines) {
    snippet = `${snippet}\n…`;
  }

  if (snippet.length > maxChars) {
    snippet = `${snippet.slice(0, maxChars).trimEnd()}…`;
  }

  return snippet;
}

export function isSnippetTruncated(content: string): boolean {
  return truncateCodeSnippet(content) !== content.replace(/\r\n/g, "\n");
}
