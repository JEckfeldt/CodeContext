/**
 * Map backend ask/search error details to short user-facing messages.
 */
export function formatAssistantErrorMessage(rawMessage: string): string {
  const message = rawMessage.trim();
  if (!message) {
    return "Could not get an answer. Please try again.";
  }

  if (message.includes("LLM_ENABLED") || message.includes("LLM provider is not configured")) {
    return "AI answers are disabled. Set LLM_ENABLED=true and OPENAI_API_KEY, then restart the backend.";
  }

  if (
    message.includes("EMBEDDING_ENABLED") ||
    message.includes("Embedding provider is not configured")
  ) {
    return "Semantic retrieval is unavailable. Set EMBEDDING_ENABLED=true and OPENAI_API_KEY, re-upload the repository, then try again.";
  }

  if (message.includes("PostgreSQL") || message.includes("pgvector")) {
    return "Semantic search requires PostgreSQL with pgvector. Use the Docker stack or point the backend at a Postgres database.";
  }

  if (message.includes("OpenAI chat completion failed") || message.includes("chat completion")) {
    return "The AI service failed to generate an answer. Check your API key and try again in a moment.";
  }

  if (message.includes("Project") && message.includes("not found")) {
    return "This project could not be found. Upload the repository again.";
  }

  return message;
}
