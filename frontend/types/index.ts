export type Project = {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
};

export type UploadResult = {
  project_id: string;
  files_discovered: number;
  ingestion_status: string;
};

export type FileRecord = {
  id: string;
  project_id: string;
  path: string;
  filename: string;
  extension: string | null;
  language: string | null;
  size: number;
  created_at: string;
};

export type HealthResponse = {
  status: string;
};
