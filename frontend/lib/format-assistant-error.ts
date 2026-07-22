/**
 * Map backend ask/search error details to short user-facing messages.
 */
export function formatAssistantErrorMessage(rawMessage: string): string {
  const message = rawMessage.trim();
  if (!message) {
    return "Could not get an explanation. Please try again.";
  }

  if (message.includes("LLM_ENABLED") || message.includes("LLM provider is not configured")) {
    return "AI explanations are turned off on the server. Ask your administrator to enable the AI service, then try again.";
  }

  if (
    message.includes("EMBEDDING_ENABLED") ||
    message.includes("Embedding provider is not configured")
  ) {
    return "Search is not set up on the server yet. Re-upload your project after indexing is enabled, then try again.";
  }

  if (message.includes("PostgreSQL") || message.includes("pgvector")) {
    return "The app could not reach the database used for search. Check that the backend is running with the full Docker setup.";
  }

  if (message.includes("OpenAI chat completion failed") || message.includes("chat completion")) {
    return "The AI service could not finish your request. Wait a moment and try again.";
  }

  if (message.includes("Project") && message.includes("not found")) {
    return "This project could not be found. Upload your content again.";
  }

  return message;
}
