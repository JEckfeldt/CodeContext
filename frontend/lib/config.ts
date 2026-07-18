const DEFAULT_API_URL = "http://localhost:8000";

export function getApiUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL ?? DEFAULT_API_URL;
}

export function getApiBaseUrl(): string {
  return `${getApiUrl()}/api/v1`;
}
