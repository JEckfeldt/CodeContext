"use client";

import { useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import {
  createProject,
  listProjectFiles,
  projectNameFromZipFilename,
  uploadRepository,
} from "@/lib/api";
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
    <div className="space-y-3">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
        <Button
          type="button"
          variant="outline"
          className="h-10 flex-1 sm:flex-none"
          disabled={disabled || loading}
          onClick={() => fileInputRef.current?.click()}
        >
          {selectedFile ? "Change ZIP file" : "Select ZIP file"}
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
          variant="secondary"
          className="h-10 flex-1 sm:flex-none"
          disabled={disabled || loading || !selectedFile}
          onClick={() => void handleUpload()}
        >
          {loading ? "Indexing repository…" : "Upload and ingest"}
        </Button>
      </div>

      {selectedFile && !loading ? (
        <p className="font-mono text-sm text-muted">
          Selected: <span className="text-foreground">{selectedFile.name}</span>
        </p>
      ) : null}

      {loading ? (
        <p className="text-sm leading-7 text-muted">
          Creating project, uploading archive, and discovering source files…
        </p>
      ) : null}

      {error ? (
        <p className="text-sm leading-7 text-destructive" role="alert">
          {error}
        </p>
      ) : null}
    </div>
  );
}
