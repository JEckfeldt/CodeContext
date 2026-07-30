"""Agent-layer errors."""


class AgentError(Exception):
    """Base error for agent orchestration and tool execution."""


class UnknownToolError(AgentError):
    """Raised when the registry has no tool with the requested name."""


class AgentStepLimitError(AgentError):
    """Raised when an agent run exceeds the configured maximum step count."""


class AgentUnavailableError(AgentError):
    """Raised when the agent feature or its LLM provider is not configured."""
