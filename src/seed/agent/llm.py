from __future__ import annotations

import json
from typing import Mapping

from seed.core.models import AgentState, Observation, Task
from seed.providers.base import Message, ModelProvider
from .interfaces import Critique


_DEFAULT_TOOL_SCHEMAS: dict[str, dict[str, object]] = {
    "aggregate_records": {
        "required": ["records", "include_statuses", "answer_template"],
        "properties": {
            "records": "array of {group,status,sign:add|subtract, amount OR factors:[...], optional discount_percent}",
            "include_statuses": "array of statuses that count",
            "decimal_places": "optional integer 0..8, default 2",
            "answer_template": "string containing {TOTAL} and any group placeholders such as {A}",
        },
    },
    "calculator": {
        "required": ["expression"],
        "properties": {"expression": "string arithmetic expression, maximum 200 characters"},
    },
    "crt": {
        "required": ["congruences", "answer_template"],
        "properties": {
            "congruences": "array of [remainder, positive_modulus] pairs",
            "answer_template": "string containing {solution}, e.g. FINAL: {solution}",
        },
    },
    "dag_longest_path": {
        "required": ["weights", "predecessors", "answer_template"],
        "properties": {
            "weights": "object node->numeric weight/duration",
            "predecessors": "object node->array of prerequisite nodes",
            "target": "optional target node",
            "answer_template": "string containing {weight} and {path}",
            "path_separator": "optional separator, default '-'",
        },
    },
    "finite_csp": {
        "required": ["domains", "all_different", "constraints", "sequences", "answer_template"],
        "properties": {
            "domains": "object variable->small array of allowed values; for ordering puzzles use positions such as [1,2,3,4]",
            "all_different": "array of variable-name arrays that must all take distinct values",
            "constraints": "array using ops eq, ne, lt, gt, offset_eq, abs_diff, not_in. For a literal constant use value, not right. For 'X immediately before Y', use offset_eq with left=Y,right=X,value=1; plain lt is only 'before'.",
            "sequences": "array of {name,variables,order,optional labels,optional separator}; labels should be an object variable->exact output token when aliases/abbreviations are required",
            "answer_template": "string using sequence placeholders such as FINAL: {people} | {topics}",
        },
    },
    "shortest_path": {
        "required": ["edges", "source", "target", "answer_template"],
        "properties": {
            "edges": "array of [from,to,nonnegative_weight] directed edges",
            "source": "source node",
            "target": "target node",
            "answer_template": "string containing {cost} and {path}",
            "path_separator": "optional separator, default '-'",
        },
    },
    "python_compute": {
        "required": ["code"],
        "properties": {
            "code": "compact safe Python code, preferably <=1600 chars; avoid backslash line continuations; end with result={'answer':'FINAL: ...','checks':{...},'evidence':optional}"
        },
    },
    "echo": {
        "required": ["text"],
        "properties": {"text": "string containing useful scratch evidence or a candidate answer"},
    },
}


def _observation_view(obs: Observation) -> dict[str, object]:
    return {"ok": obs.ok, "output": obs.output, "error": obs.error}


def _recent_action_view(state: AgentState) -> list[dict[str, object]]:
    count = min(4, len(state.tasks), len(state.observations))
    if count == 0:
        return []
    tasks = state.tasks[-count:]
    observations = state.observations[-count:]
    return [
        {"description": task.description, "tool_name": task.tool_name, "outcome": _observation_view(obs)}
        for task, obs in zip(tasks, observations)
    ]


def _verified_answers(state: AgentState) -> tuple[str, ...]:
    answers: list[str] = []
    for obs in state.observations:
        if not obs.ok or not isinstance(obs.output, dict):
            continue
        answer = obs.output.get("answer")
        checks = obs.output.get("checks")
        if not isinstance(answer, str) or not answer.strip().startswith("FINAL:"):
            continue
        if not isinstance(checks, dict) or not checks:
            continue
        if not all(value is True for value in checks.values()):
            continue
        answers.append(answer.strip())
    return tuple(answers)


def _normalize_tool_name(tool: object, allowed_tools: tuple[str, ...]) -> str:
    value = str(tool)
    if value == "python" and "python_compute" in allowed_tools:
        return "python_compute"
    return value


def _normalize_tool_input(tool: str, payload: dict) -> dict:
    normalized = dict(payload)
    nested_tool = normalized.get("tool_name")
    nested_input = normalized.get("tool_input")
    if nested_tool in (tool, "python" if tool == "python_compute" else tool) and isinstance(nested_input, dict):
        normalized = dict(nested_input)
    if tool == "echo" and "text" not in normalized and isinstance(normalized.get("message"), str):
        normalized["text"] = normalized.pop("message")
    if tool == "calculator" and "expression" not in normalized and isinstance(normalized.get("expr"), str):
        normalized["expression"] = normalized.pop("expr")
    if tool == "python_compute" and "code" not in normalized and isinstance(normalized.get("python"), str):
        normalized["code"] = normalized.pop("python")
    return normalized


class JSONPlanner:
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
            "success_criteria": list(state.goal.success_criteria),
            "constraints": list(state.goal.constraints),
            "step": state.step,
            "recent_actions": _recent_action_view(state),
            "recent_observations": [_observation_view(o) for o in state.observations[-6:]],
            "recent_critic_notes": list(state.notes[-4:]),
            "allowed_tools": list(self.allowed_tools),
            "tool_input_schemas": self.tool_schemas,
            "verified_compute_contract": {
                "answer": "exact requested FINAL: ... string",
                "checks": "non-empty object of meaningful booleans, all true",
                "evidence": "optional compact supporting data",
            },
            "schema": {
                "description": "concise string <=160 chars",
                "tool_name": "exactly one allowed tool",
                "tool_input": "object matching selected tool schema exactly",
            },
        }
        system = (
            "Return exactly one compact JSON object matching the supplied schema; no markdown or outside analysis. "
            "Choose the smallest action that creates checkable evidence. When a specialized exact tool is allowed, prefer it over writing Python: "
            "shortest_path for nonnegative weighted directed shortest paths; dag_longest_path for precedence/project critical paths; crt for systems "
            "of congruences; aggregate_records for filtered grouped sums/ledger arithmetic; finite_csp for logic grids, permutations, schedules, and "
            "small finite-domain ordering constraints. For finite_csp, model each entity/topic as a variable whose value is its position/day and put "
            "each same-kind set in all_different. A fixed literal uses value (for example eq left=X value=4); right always names another variable. "
            "Translate exact adjacency faithfully: 'X immediately before Y' means Y=X+1, so use offset_eq left=Y right=X value=1, never plain lt. "
            "Use sequences to render variables in position order. If the task requires exact aliases, abbreviations, or output tokens, either name the "
            "variables with those exact tokens or provide sequence.labels as a variable->exact-output-token object; do not emit longer internal names. "
            "Translate task data faithfully and preserve exact FINAL formatting via answer_template. Use python_compute only as the general fallback for "
            "computations not covered by an exact tool. Use calculator only for one simple expression. For python_compute, derive the candidate from task "
            "data, avoid backslash line continuations, and finish with one result object containing exact FINAL answer plus non-empty meaningful boolean "
            "checks computed against the selected candidate. Never hard-code an unchecked guess. Pay attention to relation direction, filtering/status "
            "rules, signs, percentages, required abbreviations, and output format. Use recent critic feedback and materially change failed/repeated "
            "approaches. tool_input MUST use the exact required keys."
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
        tool = _normalize_tool_name(data.get("tool_name"), self.allowed_tools)
        if tool not in self.allowed_tools:
            raise PermissionError(f"Planner requested non-allowlisted tool: {tool}")
        desc = data.get("description")
        payload = data.get("tool_input", {})
        if not isinstance(desc, str) or not isinstance(payload, dict):
            raise ValueError("Planner output schema invalid")
        payload = _normalize_tool_input(tool, payload)
        required = self.tool_schemas.get(tool, {}).get("required", [])
        if isinstance(required, list) and any(key not in payload for key in required):
            raise ValueError(f"Planner tool_input missing required key for {tool}")
        return Task(desc[:160], tool, payload)


class JSONCritic:
    def __init__(
        self,
        provider: ModelProvider,
        *,
        finish_threshold: float = 0.85,
        require_verified_answer: bool = False,
    ) -> None:
        self.provider = provider
        self.finish_threshold = finish_threshold
        self.require_verified_answer = bool(require_verified_answer)

    def review(self, state: AgentState) -> Critique:
        verified = _verified_answers(state) if self.require_verified_answer else ()
        prompt = {
            "goal": state.goal.description,
            "success_criteria": list(state.goal.success_criteria),
            "observations": [_observation_view(o) for o in state.observations[-10:]],
            "verified_candidate_answers": list(verified),
            "schema": {
                "done": "boolean",
                "confidence": "number 0..1",
                "reason": "concise string <=240 chars",
                "final_answer": "string|null",
            },
        }
        system = (
            "Return exactly one compact JSON object and no markdown. Judge ONLY supplied observations; do not solve from scratch. Treat failed tool "
            "observations as no evidence. If verified_candidate_answers is present, set done=true only by copying one exactly; never construct or "
            "repair a different final answer. Otherwise set done=true only when successful observations contain complete checkable evidence. If "
            "evidence is incomplete or inconsistent, set done=false, confidence<=0.5, final_answer=null."
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
        if self.require_verified_answer and done:
            candidate = None if final_answer is None else str(final_answer).strip()
            if candidate not in verified:
                done = False
                final_answer = None
                confidence = min(confidence, 0.5)
                reason = "no verified evidence answer: checks must be non-empty booleans all true"
        return Critique(done, confidence, reason, None if final_answer is None else str(final_answer).strip())
