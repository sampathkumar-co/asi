from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from seed.core.models import AgentState, Task


@dataclass(frozen=True)
class Critique:
    done: bool
    confidence: float
    reason: str
    final_answer: str | None = None


class Planner(Protocol):
    def next_task(self, state: AgentState) -> Task: ...


class Executor(Protocol):
    def execute(self, task: Task): ...


class Critic(Protocol):
    def review(self, state: AgentState) -> Critique: ...
