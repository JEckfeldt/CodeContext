import pytest

from app.prompts.agent_system import build_agent_system_prompt
from app.prompts.agent_task_templates import (
    TASK_TEMPLATES,
    UnknownTaskTemplateError,
    get_task_template,
)


def test_system_prompt_contains_identity_rules() -> None:
    prompt = build_agent_system_prompt()

    assert "CodeContext analysis agent" in prompt
    assert "read-only" in prompt.lower()
    assert "Use tools to gather evidence" in prompt
    assert "Do not invent files" in prompt
    assert "Never modify code" in prompt


def test_system_prompt_contains_tool_guidance() -> None:
    prompt = build_agent_system_prompt()

    assert "repository_search" in prompt
    assert "list_project_files" in prompt
    assert "read_file" in prompt
    assert "get_project_stats" in prompt


def test_architecture_review_template_exists() -> None:
    template = get_task_template("architecture_review")

    assert template.name == "architecture_review"
    assert template.output_format == "architecture_report"
    assert "architecture" in template.description.lower()
    assert "entry points" in template.goal_instruction.lower()
    assert "architecture_review" in TASK_TEMPLATES


def test_unknown_template_raises_expected_error() -> None:
    with pytest.raises(UnknownTaskTemplateError, match="Unknown task template: 'missing'"):
        get_task_template("missing")

    with pytest.raises(UnknownTaskTemplateError):
        build_agent_system_prompt(task_template="missing")


def test_system_prompt_includes_task_template_section() -> None:
    prompt = build_agent_system_prompt(task_template="architecture_review")

    assert "Active task template: architecture_review" in prompt
    assert "Expected output format: architecture_report" in prompt
    assert "data flows through the system" in prompt
