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

export type AgentArtifactType =
  | "architecture_report"
  | "findings_report"
  | "roadmap_report"
  | "implementation_plan";

export type ArtifactCitation = {
  file_path: string;
  start_line: number;
  end_line: number;
  symbol_name?: string | null;
};

export type ArchitectureComponent = {
  name: string;
  description: string;
  file_paths?: string[];
};

export type ArchitectureReportArtifact = {
  title: string;
  summary: string;
  components: ArchitectureComponent[];
  data_flow?: string | null;
  recommendations?: string[];
  citations?: ArtifactCitation[];
};

export type ImplementationMilestone = {
  title: string;
  objective: string;
  files_to_modify: string[];
  files_to_create: string[];
  implementation_details: string;
  testing_requirements: string[];
  cursor_prompt: string;
};

export type AffectedComponent = {
  name: string;
  description: string;
  file_paths: string[];
};

export type ImplementationPlanArtifact = {
  title: string;
  goal: string;
  summary: string;
  existing_system_analysis: string;
  relevant_files: string[];
  affected_components: AffectedComponent[];
  milestones: ImplementationMilestone[];
  risks: string[];
  citations: ArtifactCitation[];
};

export type AgentStructuredArtifact =
  | ArchitectureReportArtifact
  | ImplementationPlanArtifact;

type AgentRunResponseCore = {
  project_id: string;
  answer: string;
  steps_taken: number;
  tool_calls: ToolCallTrace[];
};

type AgentRunResponseWithoutArtifact = AgentRunResponseCore & {
  artifact_type?: null;
  artifact?: null;
};

type AgentRunResponseWithArchitectureArtifact = AgentRunResponseCore & {
  artifact_type: "architecture_report";
  artifact: ArchitectureReportArtifact;
};

type AgentRunResponseWithImplementationPlanArtifact = AgentRunResponseCore & {
  artifact_type: "implementation_plan";
  artifact: ImplementationPlanArtifact;
};

type AgentRunResponseWithOtherArtifact = AgentRunResponseCore & {
  artifact_type: "findings_report" | "roadmap_report";
  artifact: Record<string, unknown> | null;
};

export type AgentRunResponse =
  | AgentRunResponseWithoutArtifact
  | AgentRunResponseWithArchitectureArtifact
  | AgentRunResponseWithImplementationPlanArtifact
  | AgentRunResponseWithOtherArtifact;
