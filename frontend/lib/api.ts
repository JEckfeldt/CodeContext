import { getApiBaseUrl } from "@/lib/config";
import type {
  FileRecord,
  Project,
  ProjectAskRequest,
  ProjectAskResponse,
  ProjectSearchResponse,
  UploadResult,
} from "@/types";

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

export async function importGitRepository(
  projectId: string,
  url: string,
): Promise<UploadResult> {
  const response = await fetch(`${getApiBaseUrl()}/projects/${projectId}/import`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ source_type: "git", url: url.trim() }),
  });
  return parseJson<UploadResult>(response);
}

export async function importProjectFiles(
  projectId: string,
  files: File[],
): Promise<UploadResult> {
  const formData = new FormData();
  for (const file of files) {
    formData.append("files", file);
  }

  const response = await fetch(`${getApiBaseUrl()}/projects/${projectId}/files/import`, {
    method: "POST",
    body: formData,
  });
  return parseJson<UploadResult>(response);
}

export async function listProjectFiles(projectId: string): Promise<FileRecord[]> {
  const response = await fetch(`${getApiBaseUrl()}/projects/${projectId}/files`);
  return parseJson<FileRecord[]>(response);
}

export async function searchProject(
  projectId: string,
  query: string,
): Promise<ProjectSearchResponse> {
  const response = await fetch(`${getApiBaseUrl()}/projects/${projectId}/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
  return parseJson<ProjectSearchResponse>(response);
}

export async function askProject(
  projectId: string,
  request: ProjectAskRequest,
): Promise<ProjectAskResponse> {
  const response = await fetch(`${getApiBaseUrl()}/projects/${projectId}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  return parseJson<ProjectAskResponse>(response);
}

export function projectNameFromZipFilename(filename: string): string {
  return filename.replace(/\.zip$/i, "") || "repository";
}

export function projectNameFromGitUrl(url: string): string {
  const trimmed = url.trim();
  if (!trimmed) return "repository";

  try {
    const parsed = new URL(trimmed);
    const segments = parsed.pathname.split("/").filter(Boolean);
    const repo = segments.at(-1)?.replace(/\.git$/i, "") ?? "repository";
    const owner = segments.length >= 2 ? segments.at(-2) : null;
    return owner ? `${owner}-${repo}` : repo;
  } catch {
    return "repository";
  }
}

export function projectNameFromUploadedFiles(files: File[]): string {
  if (files.length === 0) return "uploaded-files";
  const first = files[0].name.replace(/\.[^.]+$/, "") || "uploaded-files";
  if (files.length === 1) return first;
  return `${first}-and-${files.length - 1}-more`;
}
