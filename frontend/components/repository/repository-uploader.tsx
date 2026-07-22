"use client";

import { useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import {
  createProject,
  listProjectFiles,
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

type RepositoryUploaderProps = {
  onSuccess: (result: IngestedRepository) => void;
  disabled?: boolean;
};

export function RepositoryUploader({ onSuccess, disabled }: RepositoryUploaderProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleUpload() {
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

  return (
    <div className="space-y-4">
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
            onClick={() => void handleUpload()}
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

      {loading ? (
        <p className="text-sm text-muted">
          Creating project, uploading archive, and discovering source files…
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
