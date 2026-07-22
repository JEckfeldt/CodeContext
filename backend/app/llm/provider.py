from app.core.config import settings
from app.llm.base import ChatProvider
from app.llm.openai_provider import OpenAIChatProvider


def get_chat_provider() -> ChatProvider | None:
    if not settings.llm_enabled:
        return None
    if not settings.openai_api_key:
        return None
    return OpenAIChatProvider(
        api_key=settings.openai_api_key,
        model=settings.llm_model,
        max_tokens=settings.llm_max_tokens,
        timeout_seconds=settings.llm_timeout_seconds,
    )
