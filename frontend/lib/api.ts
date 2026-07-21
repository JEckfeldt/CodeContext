import { getApiBaseUrl } from "@/lib/config";
import type { FileRecord, Project, UploadResult } from "@/types";

function formatApiError(status: number, body: unknown, fallbackText: string): string {
  if (body && typeof body === "object" && "detail" in body) {
    const detail = (body as { detail: unknown }).detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      return detail
        .map((item) =>
          typeof item === "object" && item && "msg" in item
            ? String((item as { msg: unknown }).msg)
            : String(item),
        )
        .join("; ");
    }
  }
  if (fallbackText) return fallbackText;
  return `Request failed with status ${status}`;
}

async function parseJson<T>(response: Response): Promise<T> {
  const text = await response.text();
  if (!response.ok) {
    let body: unknown;
    try {
      body = text ? JSON.parse(text) : undefined;
    } catch {
      body = undefined;
    }
    throw new Error(formatApiError(response.status, body, text));
  }
  return (text ? JSON.parse(text) : {}) as T;
}

export async function createProject(name: string): Promise<Project> {
  const response = await fetch(`${getApiBaseUrl()}/projects`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  return parseJson<Project>(response);
}

export async function uploadRepository(
  projectId: string,
  file: File,
): Promise<UploadResult> {
  const formData = new FormData();
  formData.append("archive", file);

  const response = await fetch(`${getApiBaseUrl()}/projects/${projectId}/upload`, {
    method: "POST",
    body: formData,
  });
  return parseJson<UploadResult>(response);
}

export async function listProjectFiles(projectId: string): Promise<FileRecord[]> {
  const response = await fetch(`${getApiBaseUrl()}/projects/${projectId}/files`);
  return parseJson<FileRecord[]>(response);
}

export function projectNameFromZipFilename(filename: string): string {
  return filename.replace(/\.zip$/i, "") || "repository";
}
