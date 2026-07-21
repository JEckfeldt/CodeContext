import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { CodeBlock } from "@/components/content/code-block";
import { cn } from "@/lib/cn";

type MarkdownContentProps = {
  content: string;
  className?: string;
};

export function MarkdownContent({ content, className }: MarkdownContentProps) {
  return (
    <div className={cn("markdown-content", className)}>
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
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
