"""Agent run orchestration loop."""

from __future__ import annotations

import json
import time
from typing import Any

from app.agent.context import AgentRunContext
from app.agent.exceptions import AgentError, AgentStepLimitError
from app.agent.schemas import AgentRunResult, ToolCallResult, ToolResult
from app.agent.tools.registry import ToolRegistry
from app.llm.base import ChatProvider
from app.llm.types import ChatCompletionResult, ToolCall
from app.prompts.agent_system import build_agent_system_prompt


def _build_initial_messages(
    goal: str,
    task_template: str | None,
) -> list[dict[str, Any]]:
    system_prompt = build_agent_system_prompt(task_template)
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": goal},
    ]


def _assistant_message(completion: ChatCompletionResult) -> dict[str, Any]:
    message: dict[str, Any] = {
        "role": "assistant",
        "content": completion.content,
    }
    if completion.tool_calls:
        message["tool_calls"] = [
            {
                "id": tool_call.id,
                "type": "function",
                "function": {
                    "name": tool_call.name,
                    "arguments": tool_call.arguments,
                },
            }
            for tool_call in completion.tool_calls
        ]
    return message


def _parse_tool_arguments(raw_arguments: str) -> dict[str, Any]:
    try:
        parsed = json.loads(raw_arguments)
    except json.JSONDecodeError as exc:
        raise AgentError(f"Tool arguments are not valid JSON: {exc}") from exc

    if not isinstance(parsed, dict):
        raise AgentError("Tool arguments must be a JSON object.")
    return parsed


def _format_tool_result_content(result: ToolResult) -> str:
    payload: dict[str, Any] = {
        "success": result.success,
        "summary": result.summary,
    }
    if result.data is not None:
        payload["data"] = result.data
    if result.citations is not None:
        payload["citations"] = result.citations
    return json.dumps(payload, ensure_ascii=False)


class AgentRunner:
    """ReAct-style loop connecting prompts, tool calling, and tool handlers."""

    def __init__(
        self,
        chat_provider: ChatProvider,
        tool_registry: ToolRegistry,
        max_steps: int,
    ) -> None:
        if max_steps < 1:
            raise ValueError("max_steps must be at least 1")
        self._chat_provider = chat_provider
        self._tool_registry = tool_registry
        self._max_steps = max_steps

    async def run(
        self,
        context: AgentRunContext,
        goal: str,
        task_template: str | None = None,
    ) -> AgentRunResult:
        trimmed_goal = goal.strip()
        if not trimmed_goal:
            raise AgentError("Agent run goal must not be empty.")

        messages = _build_initial_messages(trimmed_goal, task_template)
        tool_trace: list[ToolCallResult] = []
        steps_taken = 0

        while steps_taken < self._max_steps:
            steps_taken += 1
            completion = await self._chat_provider.complete_with_tools(
                messages,  # type: ignore[arg-type]
                self._tool_registry.get_openai_tools(),
            )

            if completion.has_tool_calls:
                messages.append(_assistant_message(completion))
                for tool_call in completion.tool_calls:
                    trace_entry = await self._execute_tool_call(
                        context,
                        tool_call,
                        messages,
                    )
                    tool_trace.append(trace_entry)
                continue

            if completion.content is not None:
                return AgentRunResult(
                    answer=completion.content,
                    steps_taken=steps_taken,
                    tool_calls=tool_trace,
                )

            raise AgentError("LLM returned an empty completion with no tool calls.")

        raise AgentStepLimitError(
            f"Agent run exceeded the maximum of {self._max_steps} step(s)."
        )

    async def _execute_tool_call(
        self,
        context: AgentRunContext,
        tool_call: ToolCall,
        messages: list[dict[str, Any]],
    ) -> ToolCallResult:
        started = time.perf_counter()
        arguments: dict[str, Any] = {}

        try:
            arguments = _parse_tool_arguments(tool_call.arguments)
            result = await self._tool_registry.execute(
                tool_call.name,
                context,
                arguments,
            )
        except AgentError as exc:
            result = ToolResult(
                success=False,
                summary=str(exc),
            )
        except Exception as exc:
            result = ToolResult(
                success=False,
                summary=f"Tool {tool_call.name!r} failed: {exc}",
            )

        duration_ms = int((time.perf_counter() - started) * 1000)
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": _format_tool_result_content(result),
            }
        )
        return ToolCallResult(
            tool_name=tool_call.name,
            arguments=arguments,
            result=result,
            duration_ms=duration_ms,
        )
