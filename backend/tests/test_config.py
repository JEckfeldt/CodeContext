import pytest

from app.core.config import Settings


def test_agent_settings_defaults() -> None:
    settings = Settings()

    assert settings.agent_enabled is False
    assert settings.agent_max_steps == 10
    assert settings.agent_model == settings.llm_model
    assert settings.agent_model == "gpt-4o-mini"


def test_agent_settings_env_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGENT_ENABLED", "true")
    monkeypatch.setenv("AGENT_MAX_STEPS", "15")
    monkeypatch.setenv("AGENT_MODEL", "gpt-4o")
    monkeypatch.setenv("LLM_MODEL", "gpt-4o-mini")

    settings = Settings()

    assert settings.agent_enabled is True
    assert settings.agent_max_steps == 15
    assert settings.agent_model == "gpt-4o"
    assert settings.llm_model == "gpt-4o-mini"


def test_agent_model_defaults_to_llm_model_when_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("AGENT_MODEL", raising=False)
    monkeypatch.setenv("LLM_MODEL", "custom-llm")

    settings = Settings()

    assert settings.agent_model == "custom-llm"
    assert settings.llm_model == "custom-llm"
