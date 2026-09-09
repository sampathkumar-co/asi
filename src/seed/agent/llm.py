from __future__ import annotations

import json
from typing import Mapping

from seed.core.models import AgentState, Task
from seed.providers.base import Message, ModelProvider
from .interfaces import Critique


_DEFAULT_TOOL_SCHEMAS: dict[str, dict[str, object]] = {
    "calculator": {
        "required": ["expression"],
        "properties": {"expression": "string arithmetic expression, maximum 200 characters"},
    },
    "echo": {
        "required": ["text"],
        "properties": {"text": "string containing useful scratch evidence or a candidate answer"},
    },
}


class JSONPlanner:
    """Provider-neutral planner requiring a strict compact JSON action schema."""

    def __init__(
        self,
        provider: ModelProvider,
        allowed_tools: tuple[str, ...],
        *,
        tool_schemas: Mapping[str, Mapping[str, object]] | None = None,
    ) -> None:
        self.provider = provider
        self.allowed_tools = allowed_tools
        supplied = dict(tool_schemas or {})
        self.tool_schemas: dict[str, dict[str, object]] = {
            name: dict(supplied.get(name, _DEFAULT_TOOL_SCHEMAS.get(name, {"required": [], "properties": {}})))
            for name in allowed_tools
        }

    def next_task(self, state: AgentState) -> Task:
        prompt = {
            "goal": state.goal.description,
            "constraints": list(state.goal.constraints),
            "step": state.step,
            "recent_observations": [o.__dict__ for o in state.observations[-6:]],
            "allowed_tools": list(self.allowed_tools),
            "tool_input_schemas": self.tool_schemas,
            "schema": {
                "description": "concise string, <=160 chars",
                "tool_name": "exactly one allowed tool",
                "tool_input": "object matching the selected tool_input_schema exactly",
            },
        }
        system = (
            "Return exactly one compact JSON object matching the supplied schema. "
            "Do not emit markdown or analysis outside JSON. Keep description concise. "
            "tool_input MUST use the exact required keys shown for the selected tool; "
            "never invent aliases such as message when the schema requires text."
        )
        response = self.provider.complete(
            [Message("system", system), Message("user", json.dumps(prompt, default=str))],
            purpose="plan",
        )
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise ValueError("Planner returned invalid JSON") from exc
        if not isinstance(data, dict):
            raise ValueError("Planner output must be a JSON object")
        tool = data.get("tool_name")
        if tool not in self.allowed_tools:
            raise PermissionError(f"Planner requested non-allowlisted tool: {tool}")
        desc = data.get("description")
        payload = data.get("tool_input", {})
        if not isinstance(desc, str) or not isinstance(payload, dict):
            raise ValueError("Planner output schema invalid")
        required = self.tool_schemas.get(str(tool), {}).get("required", [])
        if isinstance(required, list) and any(key not in payload for key in required):
            raise ValueError(f"Planner tool_input missing required key for {tool}")
        return Task(desc[:160], str(tool), payload)


class JSONCritic:
    """Evidence-only critic with a strict bounded-confidence schema."""

    def __init__(self, provider: ModelProvider, *, finish_threshold: float = 0.85) -> None:
        self.provider = provider
        self.finish_threshold = finish_threshold

    def review(self, state: AgentState) -> Critique:
        prompt = {
            "goal": state.goal.description,
            "success_criteria": list(state.goal.success_criteria),
            "observations": [o.__dict__ for o in state.observations[-10:]],
            "schema": {
                "done": "boolean",
                "confidence": "number 0..1",
                "reason": "concise string, <=240 chars",
                "final_answer": "string|null",
            },
        }
        system = (
            "Return exactly one compact JSON object and no markdown. Judge ONLY the supplied observations; "
            "do not solve the goal from scratch inside the critic. Set done=true only when observations contain "
            "a complete candidate answer with enough evidence to satisfy the success criteria. If evidence is "
            "incomplete, set done=false, confidence<=0.5, and final_answer=null. Keep reason under 240 characters."
        )
        response = self.provider.complete(
            [Message("system", system), Message("user", json.dumps(prompt, default=str))],
            purpose="critic",
        )
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise ValueError("Critic returned invalid JSON") from exc
        if not isinstance(data, dict):
            raise ValueError("Critic output must be a JSON object")
        confidence = float(data.get("confidence", 0.0))
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("Critic confidence out of range")
        done = bool(data.get("done", False)) and confidence >= self.finish_threshold
        reason = str(data.get("reason", ""))[:240]
        final_answer = data.get("final_answer") if done else None
        return Critique(done, confidence, reason, None if final_answer is None else str(final_answer))
