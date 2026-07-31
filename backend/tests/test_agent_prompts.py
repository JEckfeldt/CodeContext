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
    assert "Implementation plan output requirements" not in prompt


def test_implementation_planning_template_exists() -> None:
    template = get_task_template("implementation_planning")

    assert template.name == "implementation_planning"
    assert template.output_format == "implementation_plan"
    assert "implementation plan" in template.description.lower()
    assert "repository" in template.goal_instruction.lower()
    assert "implementation_planning" in TASK_TEMPLATES


def test_implementation_planning_prompt_includes_planning_instructions() -> None:
    prompt = build_agent_system_prompt(task_template="implementation_planning")

    assert "Active task template: implementation_planning" in prompt
    assert "Expected output format: implementation_plan" in prompt
    assert "Implementation plan output requirements" in prompt
    assert "existing_system_analysis" in prompt
    assert "cursor_prompt" in prompt
    assert "Output ONLY valid JSON" in prompt
    assert "Prefer 3–5 ordered milestones" in prompt
    assert "Do not invent files" in prompt
    assert "get_project_stats" in prompt


def test_architecture_review_template_unchanged() -> None:
    template = get_task_template("architecture_review")

    assert template.output_format == "architecture_report"
    assert template.description == (
        "Analyze repository architecture: layers, modules, entry points, and data flow."
    )
    assert "entry points" in template.goal_instruction
    assert "Ground every claim" in template.goal_instruction

    prompt = build_agent_system_prompt(task_template="architecture_review")
    assert "architecture_report" in prompt
    assert "implementation_plan" not in prompt
    assert "Output ONLY valid JSON" not in prompt
