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
from seed.search.architecture import AgentGenome, ArchitectureSearch
from seed.tools.builtin import default_registry


def demo() -> int:
    store = EventStore(":memory:")
    tasks = [
        Task("Compute 7*8", "calculator", {"expression": "7*8"}),
        Task("Echo verification marker", "echo", {"text": "verified"}),
    ]
    agent = BaselineAgent(QueuePlanner(tasks), RegistryExecutor(default_registry()), CompletionCritic(2), budget=Budget(max_steps=4), events=store)
    state = agent.run(Goal("Demonstrate the bounded Gate-1 loop"))
    print(json.dumps(state.to_dict(), indent=2))
    print("event_chain_valid=", store.verify_chain(state.run_id))
    return 0 if state.status.value == "succeeded" else 1


def eval_demo() -> int:
    suite = EvalSuite("gate0-smoke-v1", [
        EvalCase("math-1", "2+2", numeric_match(4)),
        EvalCase("echo-1", "seed", exact_match("seed")),
    ])

    def candidate(prompt: str):
        return 4 if prompt == "2+2" else prompt

    outcome = suite.run("demo-candidate", candidate)
    print(json.dumps({
        "score": outcome.score,
        "case_scores": outcome.case_scores,
        "metrics": outcome.metrics.__dict__,
        "receipt_hash": outcome.receipt.content_hash,
    }, indent=2))
    return 0


def gate0_certify(repo_root: str, output: str | None) -> int:
    certificate = run_gate0_qualification(repo_root)
    if output:
        write_gate0_certificate(certificate, output)
    print(json.dumps(certificate.to_dict(), indent=2, sort_keys=True))
    return 0 if certificate.passed else 1


def search_demo() -> int:
    def evaluator(g: AgentGenome) -> tuple[float, float]:
        capability = min(1.0, 0.50 + 0.03 * g.verification_passes + 0.01 * min(g.max_steps, 12))
        if g.planner_strategy == "evidence_first":
            capability += 0.05
        cost = g.max_steps / 12 + g.verification_passes / 4
        return min(capability, 1.0), cost

    search = ArchitectureSearch(evaluator, seed=42)
    best = search.search(AgentGenome(), generations=4, population=8)
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
    sub.add_parser("search-demo", help="Run the Gate-3 architecture-search demo")
    args = parser.parse_args()
    if args.command == "gate0-certify":
        return gate0_certify(args.repo_root, args.output)
    return {"demo": demo, "eval-demo": eval_demo, "search-demo": search_demo}[args.command]()


if __name__ == "__main__":
    raise SystemExit(main())
