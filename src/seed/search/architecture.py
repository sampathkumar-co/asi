from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
import random
from typing import Callable


@dataclass(frozen=True)
class AgentGenome:
    max_steps: int = 8
    verification_passes: int = 1
    memory_limit: int = 64
    critic_threshold: float = 0.8
    planner_strategy: str = "sequential"

    @property
    def candidate_id(self) -> str:
        raw = json.dumps(self.__dict__, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(raw).hexdigest()[:16]

    def validate(self) -> None:
        if not 1 <= self.max_steps <= 64:
            raise ValueError("max_steps out of range")
        if not 1 <= self.verification_passes <= 8:
            raise ValueError("verification_passes out of range")
        if not 8 <= self.memory_limit <= 4096:
            raise ValueError("memory_limit out of range")
        if not 0.5 <= self.critic_threshold <= 1.0:
            raise ValueError("critic_threshold out of range")
        if self.planner_strategy not in {"sequential", "branching", "evidence_first"}:
            raise ValueError("unknown planner_strategy")


@dataclass(frozen=True)
class CandidateScore:
    genome: AgentGenome
    capability: float
    cost: float

    @property
    def fitness(self) -> float:
        return self.capability - 0.05 * self.cost


class ArchitectureSearch:
    """Gate-3 bounded evolutionary search over a declarative architecture genome."""

    def __init__(self, evaluator: Callable[[AgentGenome], tuple[float, float]], *, seed: int = 0) -> None:
        self.evaluator = evaluator
        self.rng = random.Random(seed)
        self.archive: dict[str, CandidateScore] = {}

    def mutate(self, parent: AgentGenome) -> AgentGenome:
        choice = self.rng.choice(["steps", "verify", "memory", "threshold", "planner"])
        child = parent
        if choice == "steps":
            child = replace(parent, max_steps=max(1, min(64, parent.max_steps + self.rng.choice([-2, -1, 1, 2]))))
        elif choice == "verify":
            child = replace(parent, verification_passes=max(1, min(8, parent.verification_passes + self.rng.choice([-1, 1]))))
        elif choice == "memory":
            child = replace(parent, memory_limit=max(8, min(4096, parent.memory_limit * self.rng.choice([1, 2]) // self.rng.choice([1, 2]))))
        elif choice == "threshold":
            child = replace(parent, critic_threshold=max(0.5, min(1.0, round(parent.critic_threshold + self.rng.choice([-0.05, 0.05]), 2))))
        else:
            child = replace(parent, planner_strategy=self.rng.choice(["sequential", "branching", "evidence_first"]))
        child.validate()
        return child

    def evaluate(self, genome: AgentGenome) -> CandidateScore:
        genome.validate()
        if genome.candidate_id in self.archive:
            return self.archive[genome.candidate_id]
        capability, cost = self.evaluator(genome)
        score = CandidateScore(genome, float(capability), float(cost))
        self.archive[genome.candidate_id] = score
        return score

    def search(self, initial: AgentGenome, *, generations: int = 4, population: int = 6) -> CandidateScore:
        if generations < 1 or population < 2:
            raise ValueError("Search needs generations>=1 and population>=2")
        current = [initial] + [self.mutate(initial) for _ in range(population - 1)]
        best = self.evaluate(initial)
        for _ in range(generations):
            scored = sorted((self.evaluate(g) for g in current), key=lambda x: x.fitness, reverse=True)
            best = max(best, scored[0], key=lambda x: x.fitness)
            elites = [s.genome for s in scored[: max(1, population // 3)]]
            current = list(elites)
            while len(current) < population:
                current.append(self.mutate(self.rng.choice(elites)))
        return best
