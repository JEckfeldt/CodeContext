"use client";

import { useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import {
  createProject,
  importGitRepository,
  listProjectFiles,
  projectNameFromGitUrl,
  projectNameFromZipFilename,
  uploadRepository,
} from "@/lib/api";
import { cn } from "@/lib/cn";
import type { FileRecord, Project, UploadResult } from "@/types";

export type IngestedRepository = {
  project: Project;
  upload: UploadResult;
  files: FileRecord[];
};

type ConnectSource = "zip" | "git";

type RepositoryUploaderProps = {
  onSuccess: (result: IngestedRepository) => void;
  disabled?: boolean;
};

export function RepositoryUploader({ onSuccess, disabled }: RepositoryUploaderProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [source, setSource] = useState<ConnectSource>("zip");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [gitUrl, setGitUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleZipUpload() {
    if (!selectedFile || loading) return;

    setError(null);
    setLoading(true);

    try {
      const name = projectNameFromZipFilename(selectedFile.name);
      const project = await createProject(name);
      const upload = await uploadRepository(project.id, selectedFile);
      const files = await listProjectFiles(project.id);

      onSuccess({ project, upload, files });
      setSelectedFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
    } finally {
      setLoading(false);
    }
  }

  async function handleGitImport() {
    const url = gitUrl.trim();
    if (!url || loading) return;

    setError(null);
    setLoading(true);

    try {
      const name = projectNameFromGitUrl(url);
      const project = await createProject(name);
      const upload = await importGitRepository(project.id, url);
      const files = await listProjectFiles(project.id);

      onSuccess({ project, upload, files });
      setGitUrl("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Import failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <div
        className="flex w-full max-w-md rounded-lg border border-border bg-secondary-muted/70 p-1"
        role="tablist"
        aria-label="Connect source"
      >
        <button
          type="button"
          role="tab"
          aria-selected={source === "zip"}
          className={cn(
            "flex-1 rounded-md px-3 py-2 text-sm font-medium transition-colors sm:px-4",
            source === "zip"
              ? "bg-surface text-primary shadow-sm"
              : "text-muted hover:text-foreground",
          )}
          disabled={loading || disabled}
          onClick={() => {
            setSource("zip");
            setError(null);
          }}
        >
          Upload ZIP
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={source === "git"}
          className={cn(
            "flex-1 rounded-md px-3 py-2 text-sm font-medium transition-colors sm:px-4",
            source === "git"
              ? "bg-surface text-primary shadow-sm"
              : "text-muted hover:text-foreground",
          )}
          disabled={loading || disabled}
          onClick={() => {
            setSource("git");
            setError(null);
          }}
        >
          Repository URL
        </button>
      </div>

      {source === "zip" ? (
        <div
          className={cn(
            "rounded-lg border border-dashed border-border bg-secondary-muted/80 px-4 py-5 sm:px-6",
            selectedFile && "border-primary/35 bg-primary-muted/30",
          )}
        >
          <p className="text-sm font-medium text-foreground">Upload ZIP archive</p>
          <p className="mt-1 text-sm text-muted">
            Select a project archive to ingest and index for search.
          </p>

          <div className="mt-4 flex flex-col gap-2 sm:flex-row sm:flex-wrap">
            <Button
              type="button"
              variant="outline"
              className="h-10 w-full sm:w-auto"
              disabled={disabled || loading}
              onClick={() => fileInputRef.current?.click()}
            >
              {selectedFile ? "Change file" : "Choose ZIP file"}
            </Button>
            <input
              ref={fileInputRef}
              type="file"
              accept=".zip,application/zip"
              className="hidden"
              disabled={disabled || loading}
              onChange={(event) => {
                const file = event.target.files?.[0] ?? null;
                setSelectedFile(file);
                setError(null);
              }}
            />
            <Button
              type="button"
              variant="primary"
              className="h-10 w-full sm:w-auto"
              disabled={disabled || loading || !selectedFile}
              onClick={() => void handleZipUpload()}
            >
              {loading ? "Indexing…" : "Upload and ingest"}
            </Button>
          </div>

          {selectedFile && !loading ? (
            <p className="mt-3 break-all font-mono text-xs text-muted sm:text-sm">
              Selected:{" "}
              <span className="text-foreground">{selectedFile.name}</span>
            </p>
          ) : null}
        </div>
      ) : (
        <div className="rounded-lg border border-dashed border-border bg-secondary-muted/80 px-4 py-5 sm:px-6">
          <label htmlFor="git-repository-url" className="text-sm font-medium text-foreground">
            Repository URL
          </label>
          <p className="mt-1 text-sm text-muted">
            Import a public Git repository to ingest and index for search.
          </p>

          <input
            id="git-repository-url"
            type="url"
            value={gitUrl}
            disabled={disabled || loading}
            placeholder="https://github.com/user/repository"
            className="mt-4 w-full rounded-md border border-border bg-surface px-3 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
            onChange={(event) => {
              setGitUrl(event.target.value);
              setError(null);
            }}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                event.preventDefault();
                void handleGitImport();
              }
            }}
          />

          <div className="mt-4">
            <Button
              type="button"
              variant="primary"
              className="h-10 w-full sm:w-auto"
              disabled={disabled || loading || !gitUrl.trim()}
              onClick={() => void handleGitImport()}
            >
              {loading ? "Importing…" : "Import Repository"}
            </Button>
          </div>
        </div>
      )}

      {loading ? (
        <p className="text-sm text-muted">
          {source === "zip"
            ? "Creating project, uploading archive, and discovering source files…"
            : "Creating project, cloning repository, and discovering source files…"}
        </p>
      ) : null}

      {error ? (
        <p className="status-banner-error text-sm" role="alert">
          {error}
        </p>
      ) : null}
    </div>
  );
}
