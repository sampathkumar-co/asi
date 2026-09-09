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
from seed.core.events import EventStore
from seed.core.models import Goal
from seed.providers.base import Message, ModelProvider
from seed.providers.budgeted import BudgetedProvider, ModelCallRecord
from seed.providers.ollama import OllamaProvider
from seed.tools.builtin import default_registry
from .attestation import implementation_manifest


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


def _record_event(task_id: str, arm: str, record: ModelCallRecord) -> dict:
    return {
        "event": "model_call",
        "task_id": task_id,
        "arm": arm,
        "index": record.index,
        "purpose": record.purpose,
        "request_hash": record.request_hash,
        "response_hash": record.response_hash,
        "input_tokens": record.input_tokens,
        "output_tokens": record.output_tokens,
        "wall_time_s": record.wall_time_s,
    }


def run_local_pair(
    task: LocalTask,
    provider_factory: Callable[[], ModelProvider],
    *,
    provider_id: str,
    progress: Callable[[dict], None] | None = None,
) -> LocalPairEvidence:
    raw_budget = _budget()
    raw_cb = (lambda record: progress(_record_event(task.task_id, "raw", record))) if progress else None
    raw_meter = BudgetedProvider(provider_factory(), raw_budget, provider_id=provider_id, on_record=raw_cb)
    raw_system = (
        "Solve directly without Seed orchestration or tools. Use the bounded analysis field as scratch reasoning. "
        "Return only a JSON object with fields analysis and answer; answer must be the requested FINAL: ... string."
    )
    try:
        response = raw_meter.complete([Message("system", raw_system), Message("user", task.prompt)], purpose="raw_eval")
        data = json.loads(response.text)
        answer = data.get("answer") if isinstance(data, dict) else None
        if not isinstance(answer, str) or not answer.strip():
            raise ValueError("raw evaluation response missing answer")
        raw_answer, raw_status = answer.strip(), "succeeded"
    except Exception as exc:
        raw_answer, raw_status = None, f"failed:{type(exc).__name__}"
    raw = _arm(task, "raw", raw_meter, raw_budget, raw_answer, raw_status)

    seed_budget = _budget()
    seed_cb = (lambda record: progress(_record_event(task.task_id, "seed", record))) if progress else None
    seed_meter = BudgetedProvider(provider_factory(), seed_budget, provider_id=provider_id, on_record=seed_cb)
    tools = default_registry()
    planner = JSONPlanner(seed_meter, tools.names())
    critic = JSONCritic(seed_meter, finish_threshold=0.85, require_verified_answer=True)
    with EventStore(":memory:") as events:
        state = BaselineAgent(planner, RegistryExecutor(tools), critic, budget=seed_budget, events=events).run(
            Goal(task.prompt, success_criteria=task.success_criteria)
        )
    seed = _arm(task, "seed", seed_meter, seed_budget, state.final_answer, state.status.value)
    pair = LocalPairEvidence(raw, seed)
    pair.validate()
    return pair


def _hash_body(body: dict) -> str:
    unsigned = {k: v for k, v in body.items() if k != "content_hash"}
    return hashlib.sha256(json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _atomic_write(path: Path, body: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def _append_jsonl(path: Path, event: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n")
        handle.flush()


def _body(
    suite_id: str,
    provider_id: str,
    model: str,
    manifest: dict,
    implementation: dict,
    settings: dict,
    pairs: list[dict],
) -> dict:
    body = {
        "suite_id": suite_id,
        "provider_id": provider_id,
        "model": model,
        "model_manifest": manifest,
        "seed_implementation": implementation,
        "settings": settings,
        "pairs": pairs,
    }
    body["content_hash"] = _hash_body(body)
    return body


def run_ollama_suite(
    task_path: str | Path,
    model: str,
    *,
    num_ctx: int = 4096,
    num_predict: int = 768,
    checkpoint_path: str | Path | None = None,
    resume: bool = True,
    progress_path: str | Path | None = None,
) -> dict:
    suite_id, tasks = load_local_tasks(task_path)
    provider_id = f"ollama:{model}"
    purpose_caps = {
        "raw_eval": int(num_predict),
        "plan": min(640, int(num_predict)),
        "critic": min(128, int(num_predict)),
    }
    probe = OllamaProvider(
        model,
        temperature=0.0,
        num_ctx=num_ctx,
        num_predict=num_predict,
        think=False,
        purpose_num_predict=purpose_caps,
    )
    manifest = probe.model_manifest()
    implementation = implementation_manifest()
    settings = {
        "temperature": 0.0,
        "think": False,
        "num_ctx": num_ctx,
        "purpose_num_predict": purpose_caps,
        "raw_protocol": "one bounded analysis+answer call; no tools",
        "seed_protocol": "bounded planner/tool/critic with machine-checked answer contract",
    }
    factory = lambda: OllamaProvider(
        model,
        temperature=0.0,
        num_ctx=num_ctx,
        num_predict=num_predict,
        think=False,
        purpose_num_predict=purpose_caps,
    )

    pairs: list[dict] = []
    checkpoint = Path(checkpoint_path) if checkpoint_path else None
    if progress_path:
        progress_file = Path(progress_path)
    elif checkpoint:
        progress_file = checkpoint.with_suffix(checkpoint.suffix + ".progress.jsonl")
    else:
        progress_file = None
    if checkpoint and resume and checkpoint.exists():
        prior = json.loads(checkpoint.read_text(encoding="utf-8"))
        identity = (
            prior.get("suite_id"),
            prior.get("provider_id"),
            prior.get("model"),
            prior.get("model_manifest"),
            prior.get("seed_implementation"),
            prior.get("settings"),
        )
        expected = (suite_id, provider_id, model, manifest, implementation, settings)
        if identity != expected:
            raise ValueError("checkpoint identity/settings/implementation do not match requested campaign")
        pairs = list(prior.get("pairs", []))
        if len({p.get("raw", {}).get("task_id") for p in pairs}) != len(pairs):
            raise ValueError("checkpoint contains duplicate task evidence")

    completed = {str(p.get("raw", {}).get("task_id")) for p in pairs}
    task_ids = {t.task_id for t in tasks}
    if not completed.issubset(task_ids):
        raise ValueError("checkpoint contains task not present in requested suite")

    def emit(event: dict) -> None:
        if progress_file:
            _append_jsonl(progress_file, event)

    for task in tasks:
        if task.task_id in completed:
            continue
        emit({"event": "pair_started", "task_id": task.task_id})
        pair = run_local_pair(task, factory, provider_id=provider_id, progress=emit)
        pairs.append({"raw": asdict(pair.raw), "seed": asdict(pair.seed), "pair_hash": pair.content_hash})
        body = _body(suite_id, provider_id, model, manifest, implementation, settings, pairs)
        if checkpoint:
            _atomic_write(checkpoint, body)
        emit({"event": "pair_completed", "task_id": task.task_id, "pair_hash": pair.content_hash})

    return _body(suite_id, provider_id, model, manifest, implementation, settings, pairs)
