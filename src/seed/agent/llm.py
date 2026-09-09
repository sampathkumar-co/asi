from __future__ import annotations

import json

from seed.core.models import AgentState, Task
from seed.providers.base import Message, ModelProvider
from .interfaces import Critique


class JSONPlanner:
    """Provider-neutral planner requiring a strict JSON action schema."""

    def __init__(self, provider: ModelProvider, allowed_tools: tuple[str, ...]) -> None:
        self.provider = provider
        self.allowed_tools = allowed_tools

    def next_task(self, state: AgentState) -> Task:
        prompt = {
            "goal": state.goal.description,
            "constraints": list(state.goal.constraints),
            "step": state.step,
            "recent_observations": [o.__dict__ for o in state.observations[-6:]],
            "allowed_tools": list(self.allowed_tools),
            "schema": {"description": "string", "tool_name": "one allowed tool", "tool_input": "object"},
        }
        response = self.provider.complete(
            [Message("system", "Return only a JSON object matching the supplied schema."), Message("user", json.dumps(prompt, default=str))],
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
        return Task(desc, tool, payload)


class JSONCritic:
    """Provider-neutral critic with a strict bounded-confidence schema."""

    def __init__(self, provider: ModelProvider, *, finish_threshold: float = 0.85) -> None:
        self.provider = provider
        self.finish_threshold = finish_threshold

    def review(self, state: AgentState) -> Critique:
        prompt = {
            "goal": state.goal.description,
            "success_criteria": list(state.goal.success_criteria),
            "observations": [o.__dict__ for o in state.observations[-10:]],
            "schema": {"done": "boolean", "confidence": "0..1", "reason": "string", "final_answer": "string|null"},
        }
        response = self.provider.complete(
            [Message("system", "Critique evidence conservatively. Return only JSON."), Message("user", json.dumps(prompt, default=str))],
            purpose="critic",
        )
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise ValueError("Critic returned invalid JSON") from exc
        confidence = float(data.get("confidence", 0.0))
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("Critic confidence out of range")
        done = bool(data.get("done", False)) and confidence >= self.finish_threshold
        reason = str(data.get("reason", ""))
        final_answer = data.get("final_answer") if done else None
        return Critique(done, confidence, reason, None if final_answer is None else str(final_answer))
