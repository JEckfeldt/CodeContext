"use client";

import { useState } from "react";

import {
  RepositoryUploader,
  type IngestedRepository,
} from "@/components/repository/repository-uploader";
import { FileBrowser } from "@/components/repository/file-browser";
import { RepositoryView } from "@/components/repository/repository-view";
import { RepositoryAskSection } from "@/components/assistant/repository-ask-section";
import { RepositorySearchSection } from "@/components/search/repository-search-section";
import { Button } from "@/components/ui/button";

export function CodeContextApp() {
  const [ingested, setIngested] = useState<IngestedRepository | null>(null);
  const [searchSession, setSearchSession] = useState(0);
  const [askSession, setAskSession] = useState(0);

  function handleIngestSuccess(result: IngestedRepository) {
    setIngested(result);
    setSearchSession((value) => value + 1);
    setAskSession((value) => value + 1);
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
            Upload a repository, browse discovered files, search indexed code by
            meaning, and ask grounded questions with citations.
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

      <RepositorySearchSection
        key={searchSession}
        projectId={ingested?.project.id ?? ""}
        disabled={!repositoryReady}
      />

      <RepositoryAskSection
        key={askSession}
        projectId={ingested?.project.id ?? ""}
        disabled={!repositoryReady}
      />
    </div>
  );
}
