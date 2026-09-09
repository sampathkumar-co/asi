from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Callable

from seed.agent.baseline import BaselineAgent
from seed.agent.components import RegistryExecutor
from seed.agent.llm import JSONCritic, JSONPlanner
from seed.core.budget import Budget
from seed.core.models import Goal
from seed.providers.base import Message, ModelProvider
from seed.providers.budgeted import BudgetedProvider
from seed.providers.ollama import OllamaProvider
from seed.tools.builtin import default_registry


@dataclass(frozen=True)
class LocalTask:
    task_id: str
    prompt: str
    success_criteria: tuple[str, ...]


@dataclass(frozen=True)
class LocalArmEvidence:
    task_id: str
    arm: str
    provider_id: str
    model_id: str
    answer: str | None
    status: str
    limits: dict[str, int | float]
    usage: dict[str, int | float]
    transcript_hash: str

    @property
    def content_hash(self) -> str:
        raw = json.dumps(asdict(self), sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class LocalPairEvidence:
    raw: LocalArmEvidence
    seed: LocalArmEvidence

    def validate(self) -> None:
        if self.raw.task_id != self.seed.task_id:
            raise ValueError("raw/seed task mismatch")
        if self.raw.provider_id != self.seed.provider_id or self.raw.model_id != self.seed.model_id:
            raise ValueError("raw/seed provider or model mismatch")
        if self.raw.limits != self.seed.limits:
            raise ValueError("raw/seed resource envelope mismatch")

    @property
    def content_hash(self) -> str:
        self.validate()
        raw = json.dumps({"raw": asdict(self.raw), "seed": asdict(self.seed)}, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(raw).hexdigest()


def load_local_tasks(path: str | Path) -> tuple[str, tuple[LocalTask, ...]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    suite_id = str(data["suite_id"])
    tasks = tuple(LocalTask(str(x["task_id"]), str(x["prompt"]), tuple(map(str, x.get("success_criteria", [])))) for x in data["tasks"])
    if not tasks or len({t.task_id for t in tasks}) != len(tasks):
        raise ValueError("local task suite must contain unique tasks")
    return suite_id, tasks


def _budget() -> Budget:
    return Budget(max_steps=8, max_model_calls=12, max_tool_calls=8, max_tokens=8000, max_cost_usd=0.0)


def _arm(task: LocalTask, arm: str, provider: BudgetedProvider, budget: Budget, answer: str | None, status: str) -> LocalArmEvidence:
    return LocalArmEvidence(task.task_id, arm, provider.provider_id, provider.provider_id.removeprefix("ollama:"), answer, status, budget.limits(), budget.usage(), provider.transcript_hash)


def run_local_pair(task: LocalTask, provider_factory: Callable[[], ModelProvider], *, provider_id: str) -> LocalPairEvidence:
    raw_budget = _budget()
    raw_meter = BudgetedProvider(provider_factory(), raw_budget, provider_id=provider_id)
    raw_system = "Solve directly without Seed orchestration or tools. Reason privately. Return the requested FINAL answer."
    try:
        response = raw_meter.complete([Message("system", raw_system), Message("user", task.prompt)], purpose="raw")
        raw_answer, raw_status = response.text.strip(), "succeeded"
    except Exception as exc:
        raw_answer, raw_status = None, f"failed:{type(exc).__name__}"
    raw = _arm(task, "raw", raw_meter, raw_budget, raw_answer, raw_status)

    seed_budget = _budget()
    seed_meter = BudgetedProvider(provider_factory(), seed_budget, provider_id=provider_id)
    tools = default_registry()
    planner = JSONPlanner(seed_meter, tools.names())
    critic = JSONCritic(seed_meter, finish_threshold=0.85)
    state = BaselineAgent(planner, RegistryExecutor(tools), critic, budget=seed_budget).run(
        Goal(task.prompt, success_criteria=task.success_criteria)
    )
    seed = _arm(task, "seed", seed_meter, seed_budget, state.final_answer, state.status.value)
    pair = LocalPairEvidence(raw, seed)
    pair.validate()
    return pair


def run_ollama_suite(task_path: str | Path, model: str, *, num_ctx: int = 4096, num_predict: int = 2048) -> dict:
    suite_id, tasks = load_local_tasks(task_path)
    provider_id = f"ollama:{model}"
    probe = OllamaProvider(model, temperature=0.0, num_ctx=num_ctx, num_predict=num_predict, think=False)
    manifest = probe.model_manifest()
    factory = lambda: OllamaProvider(model, temperature=0.0, num_ctx=num_ctx, num_predict=num_predict, think=False)
    pairs = [run_local_pair(task, factory, provider_id=provider_id) for task in tasks]
    body = {
        "suite_id": suite_id,
        "provider_id": provider_id,
        "model": model,
        "model_manifest": manifest,
        "settings": {"temperature": 0.0, "think": False, "num_ctx": num_ctx, "num_predict": num_predict},
        "pairs": [{"raw": asdict(p.raw), "seed": asdict(p.seed), "pair_hash": p.content_hash} for p in pairs],
    }
    body["content_hash"] = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return body
