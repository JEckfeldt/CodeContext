"""Reusable agent task templates for structured repository analysis."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

TASK_TEMPLATE_NAMES = frozenset({"architecture_review", "implementation_planning"})


@dataclass(frozen=True, slots=True)
class TaskTemplate:
    """Pre-defined analysis task with goal and output expectations."""

    name: str
    description: str
    goal_instruction: str
    output_format: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "goal_instruction": self.goal_instruction,
            "output_format": self.output_format,
        }


TASK_TEMPLATES: dict[str, TaskTemplate] = {
    "architecture_review": TaskTemplate(
        name="architecture_review",
        description=(
            "Analyze repository architecture: layers, modules, entry points, and data flow."
        ),
        goal_instruction=(
            "Analyze this repository's architecture. Identify major layers, modules, "
            "entry points, dependencies between components, and how data flows through "
            "the system. Ground every claim in repository evidence with file and line "
            "citations."
        ),
        output_format="architecture_report",
    ),
    "implementation_planning": TaskTemplate(
        name="implementation_planning",
        description=(
            "Create an ordered implementation plan for a requested feature or change."
        ),
        goal_instruction=(
            "Create an implementation plan for the user's feature goal. Before planning, "
            "analyze the existing repository using available tools (get_project_stats, "
            "list_project_files, repository_search, read_file) to understand relevant "
            "files, patterns, and constraints. Ground the plan in verified repository "
            "evidence. Produce milestones that an IDE coding agent can execute one at a time."
        ),
        output_format="implementation_plan",
    ),
}


class UnknownTaskTemplateError(KeyError):
    """Raised when a task template name is not registered."""


def get_task_template(name: str) -> TaskTemplate:
    """Return a registered task template by name."""
    normalized = name.strip()
    template = TASK_TEMPLATES.get(normalized)
    if template is None:
        known = ", ".join(sorted(TASK_TEMPLATES))
        raise UnknownTaskTemplateError(
            f"Unknown task template: {normalized!r}. Known templates: {known}"
        )
    return template
