from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any
import uuid


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class RunStatus(str, Enum):
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    BUDGET_EXHAUSTED = "budget_exhausted"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class Goal:
    description: str
    success_criteria: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class Task:
    description: str
    tool_name: str | None = None
    tool_input: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class Observation:
    task_id: str
    ok: bool
    output: Any = None
    error: str | None = None
    created_at: str = field(default_factory=utc_now)


@dataclass
class AgentState:
    goal: Goal
    status: RunStatus = RunStatus.RUNNING
    step: int = 0
    tasks: list[Task] = field(default_factory=list)
    observations: list[Observation] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    confidence: float = 0.0
    final_answer: str | None = None
    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data
