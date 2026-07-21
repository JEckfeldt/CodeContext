"use client";

import { useState } from "react";

import { AssistantResponse } from "@/components/content/assistant-response";
import {
  RepositoryUploader,
  type IngestedRepository,
} from "@/components/repository/repository-uploader";
import { FileBrowser } from "@/components/repository/file-browser";
import { RepositoryView } from "@/components/repository/repository-view";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/cn";

type Message =
  | { id: string; role: "user"; content: string }
  | {
      id: string;
      role: "assistant";
      markdown: string;
      references?: Array<{ path: string; snippet: string }>;
    };

function buildMockAnswer(question: string) {
  return {
    markdown: `## Authentication overview

For your question — **“${question}”** — authentication in this repository is enforced in middleware before route handlers run.

### Request flow

1. Read the bearer token from the \`Authorization\` header
2. Verify the JWT signature and expiry
3. Attach the authenticated user to the request context

> Token issuer and audience values are loaded from environment-backed auth settings at startup.

The main entry point is \`verifyAccessToken()\`, which delegates validation to shared auth utilities.

\`\`\`typescript
export async function verifyAccessToken(token: string) {
  const payload = await jwt.verify(token, getJwtSecret());
  return payload.sub;
}
\`\`\`
`,
    references: [
      {
        path: "src/middleware/auth.ts",
        snippet: `export async function authMiddleware(req, res, next) {
  const token = parseBearerToken(req.headers.authorization);
  req.user = await verifyAccessToken(token);
  next();
}`,
      },
      {
        path: "src/config/auth.ts",
        snippet: `export const authConfig = {
  jwtIssuer: process.env.JWT_ISSUER,
  jwtAudience: process.env.JWT_AUDIENCE,
};`,
      },
    ],
  };
}

export function CodeContextApp() {
  const [ingested, setIngested] = useState<IngestedRepository | null>(null);
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);

  function handleIngestSuccess(result: IngestedRepository) {
    setIngested(result);
    setMessages([]);
  }

  function handleAskQuestion(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = query.trim();
    if (!trimmed || !ingested) return;

    const answer = buildMockAnswer(trimmed);
    setMessages((current) => [
      ...current,
      { id: `user-${Date.now()}`, role: "user", content: trimmed },
      {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        markdown: answer.markdown,
        references: answer.references,
      },
    ]);
    setQuery("");
  }

  const repositoryReady = ingested !== null;

  return (
    <div className="mx-auto flex min-h-screen w-full max-w-3xl flex-col px-5 py-10 sm:px-6 sm:py-14">
      <header className="mb-10 space-y-5 border-b border-border pb-8">
        <div className="flex items-center gap-3">
          <div className="brand-mark flex h-9 w-9 items-center justify-center rounded-lg text-xs font-semibold">
            CC
          </div>
          <div>
            <p className="brand-wordmark text-base font-semibold tracking-tight">
              CodeContext
            </p>
            <p className="text-xs text-muted-foreground">AI codebase workspace</p>
          </div>
        </div>
        <div className="space-y-2">
          <h1 className="text-[1.75rem] font-semibold tracking-tight text-foreground sm:text-3xl">
            Understand any codebase with AI
          </h1>
          <p className="max-w-2xl text-[0.9375rem] leading-7 text-muted">
            Documentation-style answers grounded in your repository, with readable
            explanations and referenced source files.
          </p>
        </div>
      </header>

      <section className="mb-10 space-y-4">
        <p className="text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">
          Connect repository
        </p>
        <div className="flex flex-col gap-2 sm:flex-row">
          <Button
            type="button"
            variant="secondary"
            className="h-10 flex-1"
            disabled
            title="Git clone ingestion is not available in Phase 1"
          >
            Connect GitHub repository
          </Button>
        </div>
        <p className="text-xs text-muted">
          GitHub connection is planned for a later phase. Upload a ZIP archive to
          ingest a repository today.
        </p>

        <RepositoryUploader onSuccess={handleIngestSuccess} />

        {!repositoryReady ? (
          <p className="text-sm leading-7 text-muted">
            No repository loaded yet. Select a ZIP file and run upload to index the
            codebase.
          </p>
        ) : (
          <div className="space-y-6">
            <RepositoryView
              name={ingested.project.name}
              ingestionStatus={ingested.upload.ingestion_status}
              fileCount={ingested.files.length}
            />
            <div className="space-y-3">
              <p className="text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">
                Discovered files
              </p>
              <FileBrowser files={ingested.files} />
            </div>
          </div>
        )}
      </section>

      <section className="flex flex-1 flex-col">
        <p className="mb-4 text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">
          Ask CodeContext
        </p>

        <div className="mb-8 space-y-8">
          {messages.length === 0 ? (
            <p className="text-sm leading-7 text-muted">
              Ask a question to generate a markdown explanation with code
              references from the indexed repository. Answers are preview-only until
              the AI assistant phase ships.
            </p>
          ) : null}

          {messages.map((message) => (
            <article key={message.id} className="space-y-3">
              <p
                className={cn(
                  "text-xs font-semibold uppercase",
                  message.role === "user" ? "label-user" : "label-assistant",
                )}
              >
                {message.role === "user" ? "You" : "CodeContext AI"}
              </p>

              {message.role === "user" ? (
                <div className="surface-user">
                  <p className="max-w-[68ch] text-[0.9375rem] leading-7 text-foreground">
                    {message.content}
                  </p>
                </div>
              ) : (
                <AssistantResponse
                  markdown={message.markdown}
                  references={message.references}
                />
              )}
            </article>
          ))}
        </div>

        <form
          onSubmit={handleAskQuestion}
          className="sticky bottom-0 mt-auto border-t border-border bg-background/95 pt-5 backdrop-blur-sm"
        >
          <div className="composer">
            <label htmlFor="codebase-question" className="sr-only">
              Ask a question about the repository
            </label>
            <textarea
              id="codebase-question"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder={
                repositoryReady
                  ? "How does authentication work in this project?"
                  : "Load a repository to ask questions..."
              }
              disabled={!repositoryReady}
              rows={3}
              className={cn(
                "w-full resize-none border-0 bg-transparent px-1 py-1 text-[0.9375rem] leading-7 text-foreground outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:text-muted",
              )}
            />
            <div className="mt-3 flex justify-end border-t border-border-subtle pt-3">
              <Button
                type="submit"
                variant="brand"
                disabled={!repositoryReady || !query.trim()}
              >
                Ask CodeContext
              </Button>
            </div>
          </div>
        </form>
      </section>
    </div>
  );
}
