export type User = {
  id: string;
  email: string;
  created_at: string;
};

export type AuthResponse = {
  access_token: string;
  token_type: string;
  user: User;
};

export type ProjectStats = {
  file_count: number;
  chunk_count: number;
  source_count: number;
  embedding_count: number;
  last_indexed_at: string | null;
};

export type Project = {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
  stats: ProjectStats;
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

export type SourceCitation = {
  index: number;
  file_path: string;
  start_line: number;
  end_line: number;
  symbol_name: string | null;
  snippet: string;
  similarity: number;
};

export type ProjectAskRequest = {
  question: string;
  top_k?: number;
};

export type ProjectAskResponse = {
  project_id: string;
  question: string;
  answer: string;
  citations: SourceCitation[];
};

export type AgentRunRequest = {
  goal: string;
  task_template?: string | null;
};

export type ToolCallTrace = {
  tool_name: string;
  arguments: Record<string, unknown>;
  success: boolean;
  summary: string;
  duration_ms: number | null;
};

export type ArchitectureReportArtifact = {
  title: string;
  summary: string;
  components: Array<{
    name: string;
    description: string;
    file_paths?: string[];
  }>;
  data_flow?: string | null;
  recommendations?: string[];
  citations?: Array<{
    file_path: string;
    start_line: number;
    end_line: number;
    symbol_name?: string | null;
  }>;
};

export type AgentRunResponse = {
  project_id: string;
  answer: string;
  steps_taken: number;
  tool_calls: ToolCallTrace[];
  artifact_type?: "architecture_report" | "findings_report" | "roadmap_report" | null;
  artifact?: ArchitectureReportArtifact | null;
};
