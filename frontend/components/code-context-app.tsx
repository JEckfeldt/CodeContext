"use client";

import { useState } from "react";

import { RepositoryAskSection } from "@/components/assistant/repository-ask-section";
import {
  RepositoryUploader,
  type IngestedRepository,
} from "@/components/repository/repository-uploader";
import { FileBrowser } from "@/components/repository/file-browser";
import { RepositoryView } from "@/components/repository/repository-view";
import { RepositorySearchSection } from "@/components/search/repository-search-section";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/cn";

type WorkspaceMode = "search" | "ask";

export function CodeContextApp() {
  const [ingested, setIngested] = useState<IngestedRepository | null>(null);
  const [searchSession, setSearchSession] = useState(0);
  const [askSession, setAskSession] = useState(0);
  const [workspaceMode, setWorkspaceMode] = useState<WorkspaceMode>("search");

  function handleIngestSuccess(result: IngestedRepository) {
    setIngested(result);
    setSearchSession((value) => value + 1);
    setAskSession((value) => value + 1);
  }

  const repositoryReady = ingested !== null;

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-20 border-b border-border bg-surface/90 backdrop-blur-md">
        <div className="mx-auto flex w-full max-w-6xl items-center gap-3 px-4 py-3 sm:px-6 lg:px-8">
          <div className="brand-mark flex h-8 w-8 shrink-0 items-center justify-center rounded-md text-[11px] font-semibold">
            CC
          </div>
          <div className="min-w-0">
            <p className="brand-wordmark truncate text-sm">CodeContext</p>
            <p className="truncate text-xs text-muted-foreground">
              Understand projects with search and AI
            </p>
          </div>
        </div>
      </header>

      <main className="mx-auto w-full max-w-6xl px-4 py-8 sm:px-6 sm:py-10 lg:px-8">
        <div className="mb-8 max-w-2xl">
          <h1 className="text-2xl font-semibold tracking-tight text-foreground sm:text-[1.75rem]">
            AI workspace for your project
          </h1>
          <p className="mt-2 text-sm leading-relaxed text-muted sm:text-[0.9375rem]">
            Upload content, browse files, then search and explain in one workspace.
          </p>
        </div>

        <section aria-labelledby="connect-heading" className="panel p-5 sm:p-6 lg:p-7">
          <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <p id="connect-heading" className="section-label">
                Repository
              </p>
              <p className="section-title mt-1">Connect a project</p>
              <p className="mt-1 max-w-xl text-sm text-muted">
                ZIP upload today. Git and additional formats are planned for later phases.
              </p>
            </div>
            <Button
              type="button"
              variant="secondary"
              size="sm"
              className="w-full shrink-0 sm:w-auto"
              disabled
              title="Git clone ingestion is not available yet"
            >
              Connect GitHub
            </Button>
          </div>

          <RepositoryUploader onSuccess={handleIngestSuccess} />

          {!repositoryReady ? (
            <div className="status-banner mt-5">
              <p className="text-sm text-muted">
                No project loaded. Select a ZIP archive and upload to index content for
                search and explanations.
              </p>
            </div>
          ) : (
            <div className="mt-6 space-y-5 border-t border-border-subtle pt-6">
              <RepositoryView
                name={ingested.project.name}
                ingestionStatus={ingested.upload.ingestion_status}
                fileCount={ingested.files.length}
              />
              <div>
                <p className="section-label mb-3">Discovered files</p>
                <FileBrowser files={ingested.files} />
              </div>
            </div>
          )}
        </section>

        <section
          aria-labelledby="workspace-heading"
          className="panel mt-8 flex min-h-[32rem] flex-col p-5 sm:mt-10 sm:p-6 lg:p-7"
        >
          <div className="mb-6 border-b border-border-subtle pb-5">
            <p id="workspace-heading" className="section-label">
              Project workspace
            </p>
            <p className="section-title mt-1">Search or explain</p>
            <div
              className="mt-4 flex w-full max-w-md rounded-lg border border-border bg-secondary-muted/70 p-1"
              role="tablist"
              aria-label="Workspace mode"
            >
              <button
                type="button"
                role="tab"
                id="workspace-tab-search"
                aria-selected={workspaceMode === "search"}
                aria-controls="workspace-panel-search"
                className={cn(
                  "flex-1 rounded-md px-3 py-2 text-sm font-medium transition-colors sm:px-4",
                  workspaceMode === "search"
                    ? "bg-surface text-primary shadow-sm"
                    : "text-muted hover:text-foreground",
                )}
                onClick={() => setWorkspaceMode("search")}
              >
                🔍 Search
              </button>
              <button
                type="button"
                role="tab"
                id="workspace-tab-ask"
                aria-selected={workspaceMode === "ask"}
                aria-controls="workspace-panel-ask"
                className={cn(
                  "flex-1 rounded-md px-3 py-2 text-sm font-medium transition-colors sm:px-4",
                  workspaceMode === "ask"
                    ? "bg-surface text-primary shadow-sm"
                    : "text-muted hover:text-foreground",
                )}
                onClick={() => setWorkspaceMode("ask")}
              >
                🤖 Explain
              </button>
            </div>
          </div>

          <div className="flex min-h-0 flex-1 flex-col">
            <div
              id="workspace-panel-search"
              role="tabpanel"
              aria-labelledby="workspace-tab-search"
              hidden={workspaceMode !== "search"}
              className={cn(
                "flex min-h-[26rem] flex-1 flex-col",
                workspaceMode !== "search" && "hidden",
              )}
            >
              <RepositorySearchSection
                key={`search-${searchSession}`}
                projectId={ingested?.project.id ?? ""}
                disabled={!repositoryReady}
              />
            </div>

            <div
              id="workspace-panel-ask"
              role="tabpanel"
              aria-labelledby="workspace-tab-ask"
              hidden={workspaceMode !== "ask"}
              className={cn(
                "flex min-h-[26rem] flex-1 flex-col",
                workspaceMode !== "ask" && "hidden",
              )}
            >
              <RepositoryAskSection
                key={`ask-${askSession}`}
                projectId={ingested?.project.id ?? ""}
                disabled={!repositoryReady}
              />
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
