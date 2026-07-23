import { getApiBaseUrl } from "@/lib/config";
import { authHeaders } from "@/lib/auth-token";
import type {
  AuthResponse,
  FileRecord,
  Project,
  ProjectAskRequest,
  ProjectAskResponse,
  ProjectSearchResponse,
  UploadResult,
  User,
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

function jsonHeaders(): HeadersInit {
  return {
    "Content-Type": "application/json",
    ...authHeaders(),
  };
}

export async function registerUser(email: string, password: string): Promise<AuthResponse> {
  const response = await fetch(`${getApiBaseUrl()}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  return parseJson<AuthResponse>(response);
}

export async function loginUser(email: string, password: string): Promise<AuthResponse> {
  const response = await fetch(`${getApiBaseUrl()}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  return parseJson<AuthResponse>(response);
}

export async function fetchCurrentUser(): Promise<User> {
  const response = await fetch(`${getApiBaseUrl()}/auth/me`, {
    headers: authHeaders(),
  });
  return parseJson<User>(response);
}

export async function listProjects(): Promise<Project[]> {
  const response = await fetch(`${getApiBaseUrl()}/projects`, {
    headers: authHeaders(),
  });
  return parseJson<Project[]>(response);
}

export async function createProject(name: string): Promise<Project> {
  const response = await fetch(`${getApiBaseUrl()}/projects`, {
    method: "POST",
    headers: jsonHeaders(),
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
    headers: authHeaders(),
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
    headers: jsonHeaders(),
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
    headers: authHeaders(),
    body: formData,
  });
  return parseJson<UploadResult>(response);
}

export async function listProjectFiles(projectId: string): Promise<FileRecord[]> {
  const response = await fetch(`${getApiBaseUrl()}/projects/${projectId}/files`, {
    headers: authHeaders(),
  });
  return parseJson<FileRecord[]>(response);
}

export async function searchProject(
  projectId: string,
  query: string,
): Promise<ProjectSearchResponse> {
  const response = await fetch(`${getApiBaseUrl()}/projects/${projectId}/search`, {
    method: "POST",
    headers: jsonHeaders(),
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
    headers: jsonHeaders(),
    body: JSON.stringify(request),
  });
  return parseJson<ProjectAskResponse>(response);
}
