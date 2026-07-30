"""Parse structured artifacts from final agent LLM responses."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel

from app.agent.structured_output import validate_artifact

_JSON_FENCE_PATTERN = re.compile(
    r"```(?:json)?\s*\n?(.*?)\n?```",
    re.DOTALL | re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class ArtifactParseResult:
    """Outcome of attempting to parse a structured artifact from LLM text."""

    artifact_type: str | None
    artifact: BaseModel | None


def extract_json_payload(content: str) -> dict[str, Any] | None:
    """Extract a JSON object from raw text or fenced code blocks."""
    trimmed = content.strip()
    if not trimmed:
        return None

    try:
        parsed = json.loads(trimmed)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    for match in _JSON_FENCE_PATTERN.finditer(trimmed):
        block = match.group(1).strip()
        if not block:
            continue
        try:
            parsed = json.loads(block)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            continue

    return None


def parse_artifact_from_response(
    content: str,
    output_format: str,
) -> ArtifactParseResult:
    """Validate structured artifact JSON embedded in a final LLM response."""
    try:
        payload = extract_json_payload(content)
        if payload is None:
            return ArtifactParseResult(None, None)

        artifact = validate_artifact(output_format, payload)
        return ArtifactParseResult(output_format, artifact)
    except Exception:
        return ArtifactParseResult(None, None)
