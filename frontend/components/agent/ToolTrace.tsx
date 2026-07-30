"use client";

import { cn } from "@/lib/cn";
import type { ToolCallTrace } from "@/types";

type ToolTraceProps = {
  toolCalls: ToolCallTrace[];
  className?: string;
};

function formatArgumentValue(value: unknown): string {
  if (typeof value === "string") {
    return `"${value}"`;
  }
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

export function ToolTrace({ toolCalls, className }: ToolTraceProps) {
  if (toolCalls.length === 0) {
    return null;
  }

  return (
    <div className={cn("space-y-3", className)}>
      <p className="text-sm font-medium text-foreground">Tool trace</p>
      <ol className="space-y-3">
        {toolCalls.map((call, index) => (
          <li
            key={`${call.tool_name}-${index}`}
            className="rounded-md border border-border-subtle bg-secondary-muted/40 px-3 py-3"
          >
            <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Step {index + 1}
            </p>
            <p className="mt-1 font-mono text-sm text-foreground">{call.tool_name}</p>
            {Object.keys(call.arguments).length > 0 ? (
              <dl className="mt-2 space-y-1">
                {Object.entries(call.arguments).map(([key, value]) => (
                  <div key={key}>
                    <dt className="text-xs text-muted-foreground">{key}:</dt>
                    <dd className="whitespace-pre-wrap font-mono text-xs text-foreground">
                      {formatArgumentValue(value)}
                    </dd>
                  </div>
                ))}
              </dl>
            ) : null}
            <p
              className={cn(
                "mt-2 text-xs",
                call.success ? "text-muted-foreground" : "text-destructive",
              )}
            >
              {call.summary}
            </p>
          </li>
        ))}
      </ol>
    </div>
  );
}
