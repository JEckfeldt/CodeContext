"""Errors raised when calling LLM providers."""


class LLMError(Exception):
    """Base error for LLM failures."""


class LLMUnavailableError(LLMError):
    """The LLM provider is not configured or cannot be used."""


class LLMCompletionError(LLMError):
    """A chat completion request failed or returned an invalid response."""
