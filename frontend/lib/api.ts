import { getApiBaseUrl } from "@/lib/config";
import type { FileRecord, Project, UploadResult } from "@/types";

async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with status ${response.status}`);
  }
  return response.json() as Promise<T>;
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
