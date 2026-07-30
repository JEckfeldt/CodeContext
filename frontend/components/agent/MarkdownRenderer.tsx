"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { CodeBlock } from "@/components/content/code-block";
import { cn } from "@/lib/cn";

type MarkdownRendererProps = {
  markdown: string;
  className?: string;
};

export function MarkdownRenderer({ markdown, className }: MarkdownRendererProps) {
  if (!markdown.trim()) {
    return null;
  }

  return (
    <div className={cn("agent-markdown", className)}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          pre({ children }) {
            return <>{children}</>;
          },
          code({ className: codeClassName, children, ...props }) {
            const match = /language-([\w-]+)/.exec(codeClassName ?? "");
            const language = match?.[1];
            const code = String(children).replace(/\n$/, "");
            const isBlock = Boolean(match) || code.includes("\n");

            if (isBlock) {
              return <CodeBlock language={language} code={code} />;
            }

            return (
              <code className={codeClassName} {...props}>
                {children}
              </code>
            );
          },
          a({ href, children, ...props }) {
            const isExternal = href?.startsWith("http://") || href?.startsWith("https://");
            return (
              <a
                href={href}
                {...props}
                {...(isExternal
                  ? { target: "_blank", rel: "noopener noreferrer" }
                  : undefined)}
              >
                {children}
              </a>
            );
          },
        }}
      >
        {markdown}
      </ReactMarkdown>
    </div>
  );
}
