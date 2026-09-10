from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path

from seed.agent.baseline import BaselineAgent
from seed.agent.components import RegistryExecutor
from seed.agent.llm import JSONCritic, JSONPlanner
from seed.agent.raw import RawModelAgent
from seed.core.budget import Budget, BudgetExceeded
from seed.core.models import Goal, RunStatus
from seed.providers.base import Message
from seed.providers.budgeted import BudgetedProvider
from seed.providers.scripted import ScriptedProvider
from seed.tools.builtin import default_registry
from .comparison import ArmEvidence, ComparisonEvidence, within_limits


@dataclass(frozen=True)
class Gate1Certificate:
    qualification: str
    gate: int
    passed: bool
    checks: dict[str, bool]
    evidence: dict[str, object]
    content_hash: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _score(answer: str | None) -> float:
    return 1.0 if answer is not None and answer.strip() == "61" else 0.0


def _envelope() -> dict[str, int | float]:
    return {"max_steps": 4, "max_model_calls": 6, "max_tool_calls": 3, "max_tokens": 2_000, "max_cost_usd": 1.0}


def _arm(arm: str, provider: BudgetedProvider, budget: Budget, score: float, status: RunStatus) -> ArmEvidence:
    return ArmEvidence(
        arm=arm,
        provider_id=provider.provider_id,
        score=score,
        status=status.value,
        limits=budget.limits(),
        usage=budget.usage(),
        transcript_hash=provider.transcript_hash,
    )


def run_gate1_qualification() -> Gate1Certificate:
    provider_id = "scripted-same-model-gate1-v1"
    envelope = _envelope()
    goal = Goal("Compute (7 * 8) + 5", success_criteria=("Return only the verified numeric answer",))

    raw_budget = Budget(**envelope)
    raw_provider = BudgetedProvider(ScriptedProvider(["60"]), raw_budget, provider_id=provider_id)
    raw_run = RawModelAgent(raw_provider).run(goal)
    raw_evidence = _arm("raw", raw_provider, raw_budget, _score(raw_run.answer), raw_run.status)

    seed_budget = Budget(**envelope)
    seed_provider = BudgetedProvider(
        ScriptedProvider([
            '{"description":"multiply first","tool_name":"calculator","tool_input":{"expression":"7*8"}}',
            '{"done":false,"confidence":0.70,"reason":"Need the final addition","final_answer":null}',
            '{"description":"add five","tool_name":"calculator","tool_input":{"expression":"56+5"}}',
            '{"done":true,"confidence":0.99,"reason":"Two-step calculation verified","final_answer":"61"}',
        ]),
        seed_budget,
        provider_id=provider_id,
    )
    planner = JSONPlanner(seed_provider, ("calculator",))
    critic = JSONCritic(seed_provider, finish_threshold=0.85)
    seed_state = BaselineAgent(planner, RegistryExecutor(default_registry()), critic, budget=seed_budget).run(goal)
    seed_evidence = _arm("seed", seed_provider, seed_budget, _score(seed_state.final_answer), seed_state.status)
    comparison = ComparisonEvidence(raw_evidence, seed_evidence)

    allowlist_enforced = False
    try:
        p = JSONPlanner(ScriptedProvider(['{"description":"escape","tool_name":"shell","tool_input":{}}']), ("calculator",))
        p.next_task(seed_state)
    except PermissionError:
        allowlist_enforced = True

    malformed_fails_closed = False
    try:
        JSONPlanner(ScriptedProvider(["not-json"]), ("calculator",)).next_task(seed_state)
    except ValueError:
        malformed_fails_closed = True

    runaway_blocked = False
    tiny = Budget(max_steps=1, max_model_calls=1, max_tool_calls=0, max_tokens=100, max_cost_usd=0)
    metered = BudgetedProvider(ScriptedProvider(["a", "b"]), tiny, provider_id=provider_id)
    try:
        metered.complete([Message("user", "one")], purpose="one")
        metered.complete([Message("user", "two")], purpose="two")
    except BudgetExceeded:
        runaway_blocked = True

    budget_status = False
    limited_budget = Budget(max_steps=2, max_model_calls=1, max_tool_calls=2, max_tokens=500, max_cost_usd=0)
    limited_provider = BudgetedProvider(
        ScriptedProvider(['{"description":"multiply","tool_name":"calculator","tool_input":{"expression":"7*8"}}']),
        limited_budget,
        provider_id=provider_id,
    )
    limited_state = BaselineAgent(
        JSONPlanner(limited_provider, ("calculator",)),
        RegistryExecutor(default_registry()),
        JSONCritic(limited_provider),
        budget=limited_budget,
    ).run(goal)
    budget_status = limited_state.status == RunStatus.BUDGET_EXHAUSTED

    checks = {
        "same_provider_identity": comparison.same_provider,
        "same_resource_envelope": comparison.same_envelope,
        "both_arms_within_budget": within_limits(raw_evidence) and within_limits(seed_evidence),
        "seed_completes_multistep_task": seed_state.status == RunStatus.SUCCEEDED and seed_state.step == 2 and seed_state.final_answer == "61",
        "comparison_detects_canary_gain": comparison.capability_gain == 1.0,
        "tool_allowlist_enforced": allowlist_enforced,
        "malformed_model_output_fails_closed": malformed_fails_closed,
        "runaway_model_calls_blocked": runaway_blocked,
        "budget_exhaustion_becomes_terminal_status": budget_status,
        "model_transcript_recorded": len(seed_provider.records) == 4 and len(seed_provider.transcript_hash) == 64,
    }
    evidence = {
        "comparison": asdict(comparison),
        "comparison_hash": comparison.content_hash,
        "seed_steps": seed_state.step,
        "seed_observations": len(seed_state.observations),
        "seed_model_records": len(seed_provider.records),
        "qualification_note": "Deterministic infrastructure canary; not a frontier-model capability claim.",
    }
    passed = all(checks.values())
    body = {"qualification": "gate1-agent-infrastructure-v1", "gate": 1, "passed": passed, "checks": checks, "evidence": evidence}
    content_hash = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()
    return Gate1Certificate(**body, content_hash=content_hash)


def write_gate1_certificate(certificate: Gate1Certificate, path: str | Path) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(certificate.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
