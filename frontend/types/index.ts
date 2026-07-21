export type Project = {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
};

export type UploadResult = {
  project_id: string;
  files_discovered: number;
  chunks_created: number;
  embeddings_created: number;
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

export type ChunkSearchHit = {
  file_path: string;
  content: string;
  start_line: number;
  end_line: number;
  symbol_name: string | null;
  similarity: number;
};

export type ProjectSearchResponse = {
  project_id: string;
  query: string;
  results: ChunkSearchHit[];
};
