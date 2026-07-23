"use client";

import { useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import {
  createProject,
  importGitRepository,
  importProjectFiles,
  listProjectFiles,
  projectNameFromGitUrl,
  projectNameFromUploadedFiles,
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

type ConnectSource = "zip" | "git" | "files";

const INDIVIDUAL_FILE_ACCEPT = ".md,.markdown,.txt,.pdf,text/markdown,text/plain,application/pdf";

type RepositoryUploaderProps = {
  onSuccess: (result: IngestedRepository) => void;
  disabled?: boolean;
};

export function RepositoryUploader({ onSuccess, disabled }: RepositoryUploaderProps) {
  const zipInputRef = useRef<HTMLInputElement>(null);
  const filesInputRef = useRef<HTMLInputElement>(null);
  const [source, setSource] = useState<ConnectSource>("zip");
  const [selectedZip, setSelectedZip] = useState<File | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [gitUrl, setGitUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleZipUpload() {
    if (!selectedZip || loading) return;

    setError(null);
    setLoading(true);

    try {
      const name = projectNameFromZipFilename(selectedZip.name);
      const project = await createProject(name);
      const upload = await uploadRepository(project.id, selectedZip);
      const files = await listProjectFiles(project.id);

      onSuccess({ project, upload, files });
      setSelectedZip(null);
      if (zipInputRef.current) zipInputRef.current.value = "";
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

  async function handleFilesImport() {
    if (selectedFiles.length === 0 || loading) return;

    setError(null);
    setLoading(true);

    try {
      const name = projectNameFromUploadedFiles(selectedFiles);
      const project = await createProject(name);
      const upload = await importProjectFiles(project.id, selectedFiles);
      const files = await listProjectFiles(project.id);

      onSuccess({ project, upload, files });
      setSelectedFiles([]);
      if (filesInputRef.current) filesInputRef.current.value = "";
    } catch (err) {
      setError(err instanceof Error ? err.message : "Import failed.");
    } finally {
      setLoading(false);
    }
  }

  const loadingMessage =
    source === "zip"
      ? "Creating project, uploading archive, and discovering source files…"
      : source === "git"
        ? "Creating project, cloning repository, and discovering source files…"
        : "Creating project, importing files, and indexing content…";

  return (
    <div className="space-y-4">
      <div
        className="flex w-full max-w-xl rounded-lg border border-border bg-secondary-muted/70 p-1"
        role="tablist"
        aria-label="Connect source"
      >
        {(
          [
            ["zip", "Upload ZIP"],
            ["git", "Repository URL"],
            ["files", "Individual Files"],
          ] as const
        ).map(([value, label]) => (
          <button
            key={value}
            type="button"
            role="tab"
            aria-selected={source === value}
            className={cn(
              "flex-1 rounded-md px-2 py-2 text-sm font-medium transition-colors sm:px-3",
              source === value
                ? "bg-surface text-primary shadow-sm"
                : "text-muted hover:text-foreground",
            )}
            disabled={loading || disabled}
            onClick={() => {
              setSource(value);
              setError(null);
            }}
          >
            {label}
          </button>
        ))}
      </div>

      {source === "zip" ? (
        <div
          className={cn(
            "rounded-lg border border-dashed border-border bg-secondary-muted/80 px-4 py-5 sm:px-6",
            selectedZip && "border-primary/35 bg-primary-muted/30",
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
              onClick={() => zipInputRef.current?.click()}
            >
              {selectedZip ? "Change file" : "Choose ZIP file"}
            </Button>
            <input
              ref={zipInputRef}
              type="file"
              accept=".zip,application/zip"
              className="hidden"
              disabled={disabled || loading}
              onChange={(event) => {
                const file = event.target.files?.[0] ?? null;
                setSelectedZip(file);
                setError(null);
              }}
            />
            <Button
              type="button"
              variant="primary"
              className="h-10 w-full sm:w-auto"
              disabled={disabled || loading || !selectedZip}
              onClick={() => void handleZipUpload()}
            >
              {loading ? "Indexing…" : "Upload and ingest"}
            </Button>
          </div>

          {selectedZip && !loading ? (
            <p className="mt-3 break-all font-mono text-xs text-muted sm:text-sm">
              Selected:{" "}
              <span className="text-foreground">{selectedZip.name}</span>
            </p>
          ) : null}
        </div>
      ) : null}

      {source === "git" ? (
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
      ) : null}

      {source === "files" ? (
        <div
          className={cn(
            "rounded-lg border border-dashed border-border bg-secondary-muted/80 px-4 py-5 sm:px-6",
            selectedFiles.length > 0 && "border-primary/35 bg-primary-muted/30",
          )}
        >
          <p className="text-sm font-medium text-foreground">Individual files</p>
          <p className="mt-1 text-sm text-muted">
            Upload Markdown, plain text, or text-based PDF files to index for search.
          </p>

          <div className="mt-4 flex flex-col gap-2 sm:flex-row sm:flex-wrap">
            <Button
              type="button"
              variant="outline"
              className="h-10 w-full sm:w-auto"
              disabled={disabled || loading}
              onClick={() => filesInputRef.current?.click()}
            >
              {selectedFiles.length > 0 ? "Change files" : "Choose files"}
            </Button>
            <input
              ref={filesInputRef}
              type="file"
              multiple
              accept={INDIVIDUAL_FILE_ACCEPT}
              className="hidden"
              disabled={disabled || loading}
              onChange={(event) => {
                const list = event.target.files ? Array.from(event.target.files) : [];
                setSelectedFiles(list);
                setError(null);
              }}
            />
            <Button
              type="button"
              variant="primary"
              className="h-10 w-full sm:w-auto"
              disabled={disabled || loading || selectedFiles.length === 0}
              onClick={() => void handleFilesImport()}
            >
              {loading ? "Importing…" : "Upload files"}
            </Button>
          </div>

          {selectedFiles.length > 0 && !loading ? (
            <ul className="mt-3 space-y-1 font-mono text-xs text-muted sm:text-sm">
              {selectedFiles.map((file) => (
                <li key={`${file.name}-${file.size}`} className="break-all text-foreground">
                  {file.name}
                </li>
              ))}
            </ul>
          ) : null}
        </div>
      ) : null}

      {loading ? <p className="text-sm text-muted">{loadingMessage}</p> : null}

      {error ? (
        <p className="status-banner-error text-sm" role="alert">
          {error}
        </p>
      ) : null}
    </div>
  );
}
