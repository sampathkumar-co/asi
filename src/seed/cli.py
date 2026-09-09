from __future__ import annotations

import argparse
import json
from pathlib import Path

from seed.agent.baseline import BaselineAgent
from seed.agent.components import CompletionCritic, QueuePlanner, RegistryExecutor
from seed.core.budget import Budget
from seed.core.events import EventStore
from seed.core.models import Goal, Task
from seed.eval.cases import EvalCase, exact_match, numeric_match
from seed.eval.gate0 import run_gate0_qualification, write_gate0_certificate
from seed.eval.suite import EvalSuite
from seed.gate1.local_campaign import run_ollama_suite
from seed.gate1.local_scoring import score_local_campaign
from seed.gate1.qualification import run_gate1_qualification, write_gate1_certificate
from seed.gate1.realchat import load_pair
from seed.search.architecture import AgentGenome, ArchitectureSearch
from seed.tools.builtin import default_registry


def demo() -> int:
    store = EventStore(":memory:")
    tasks = [Task("Compute 7*8", "calculator", {"expression": "7*8"}), Task("Echo verification marker", "echo", {"text": "verified"})]
    agent = BaselineAgent(QueuePlanner(tasks), RegistryExecutor(default_registry()), CompletionCritic(2), budget=Budget(max_steps=4), events=store)
    state = agent.run(Goal("Demonstrate the bounded Gate-1 loop"))
    print(json.dumps(state.to_dict(), indent=2))
    print("event_chain_valid=", store.verify_chain(state.run_id))
    return 0 if state.status.value == "succeeded" else 1


def eval_demo() -> int:
    suite = EvalSuite("gate0-smoke-v1", [EvalCase("math-1", "2+2", numeric_match(4)), EvalCase("echo-1", "seed", exact_match("seed"))])
    outcome = suite.run("demo-candidate", lambda prompt: 4 if prompt == "2+2" else prompt)
    print(json.dumps({"score": outcome.score, "case_scores": outcome.case_scores, "metrics": outcome.metrics.__dict__, "receipt_hash": outcome.receipt.content_hash}, indent=2))
    return 0


def gate0_certify(repo_root: str, output: str | None) -> int:
    certificate = run_gate0_qualification(repo_root)
    if output:
        write_gate0_certificate(certificate, output)
    print(json.dumps(certificate.to_dict(), indent=2, sort_keys=True))
    return 0 if certificate.passed else 1


def gate1_certify(output: str | None) -> int:
    certificate = run_gate1_qualification()
    if output:
        write_gate1_certificate(certificate, output)
    print(json.dumps(certificate.to_dict(), indent=2, sort_keys=True))
    return 0 if certificate.passed else 1


def gate1_chat_validate(raw_path: str, seed_path: str) -> int:
    pair = load_pair(raw_path, seed_path)
    report = {
        "valid_pair": True,
        "task_id": pair.raw.task_id,
        "provider_id": pair.raw.provider_id,
        "model_id": pair.raw.model_id,
        "surface_id": pair.raw.surface_id,
        "minimum_evidence_level": pair.minimum_evidence_level,
        "certification_ready": pair.certification_ready,
        "content_hash": pair.content_hash,
        "raw_hash": pair.raw.content_hash,
        "seed_hash": pair.seed.content_hash,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


def gate1_local_campaign(task_file: str, model: str, output: str | None) -> int:
    report = run_ollama_suite(task_file, model)
    if output:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


def gate1_local_score(evidence: str, answers: str, output: str | None) -> int:
    report = score_local_campaign(evidence, answers)
    if output:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


def search_demo() -> int:
    def evaluator(g: AgentGenome) -> tuple[float, float]:
        capability = min(1.0, 0.50 + 0.03 * g.verification_passes + 0.01 * min(g.max_steps, 12))
        if g.planner_strategy == "evidence_first":
            capability += 0.05
        cost = g.max_steps / 12 + g.verification_passes / 4
        return min(capability, 1.0), cost
    best = ArchitectureSearch(evaluator, seed=42).search(AgentGenome(), generations=4, population=8)
    print(json.dumps({"candidate_id": best.genome.candidate_id, "genome": best.genome.__dict__, "capability": best.capability, "cost": best.cost, "fitness": best.fitness}, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="seed")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("demo", help="Run the bounded Gate-1 agent demo")
    sub.add_parser("eval-demo", help="Run the Gate-0 evaluation demo")
    gate0 = sub.add_parser("gate0-certify", help="Run the fail-closed Gate-0 infrastructure qualification")
    gate0.add_argument("--repo-root", default=".")
    gate0.add_argument("--output", default=None)
    gate1 = sub.add_parser("gate1-certify", help="Run the fail-closed Gate-1 agent-infrastructure qualification")
    gate1.add_argument("--output", default=None)
    chat = sub.add_parser("gate1-chat-validate", help="Validate a paired real-ChatGPT raw-vs-Seed evidence bundle")
    chat.add_argument("--raw", required=True)
    chat.add_argument("--seed", required=True)
    local = sub.add_parser("gate1-local-campaign", help="Run a paired Raw-vs-Seed campaign against one local Ollama model")
    local.add_argument("--tasks", default="configs/gate1_local_tasks_v1.json")
    local.add_argument("--model", required=True)
    local.add_argument("--output", default=None)
    score = sub.add_parser("gate1-local-score", help="Score local campaign evidence with an external answer key")
    score.add_argument("--evidence", required=True)
    score.add_argument("--answers", required=True)
    score.add_argument("--output", default=None)
    sub.add_parser("search-demo", help="Run the Gate-3 architecture-search demo")
    args = parser.parse_args()
    if args.command == "gate0-certify":
        return gate0_certify(args.repo_root, args.output)
    if args.command == "gate1-certify":
        return gate1_certify(args.output)
    if args.command == "gate1-chat-validate":
        return gate1_chat_validate(args.raw, args.seed)
    if args.command == "gate1-local-campaign":
        return gate1_local_campaign(args.tasks, args.model, args.output)
    if args.command == "gate1-local-score":
        return gate1_local_score(args.evidence, args.answers, args.output)
    return {"demo": demo, "eval-demo": eval_demo, "search-demo": search_demo}[args.command]()


if __name__ == "__main__":
    raise SystemExit(main())
