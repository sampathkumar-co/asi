from __future__ import annotations

from dataclasses import dataclass

from seed.core.budget import BudgetExceeded
from seed.core.models import Goal, RunStatus
from seed.providers.base import Message, ModelProvider


@dataclass(frozen=True)
class RawRun:
    status: RunStatus
    answer: str | None
    error: str | None = None


class RawModelAgent:
    """Minimal raw-model arm for fair Gate-1 comparisons."""

    def __init__(self, provider: ModelProvider) -> None:
        self.provider = provider

    def run(self, goal: Goal) -> RawRun:
        prompt = "\n".join([
            f"Goal: {goal.description}",
            "Success criteria:",
            *[f"- {x}" for x in goal.success_criteria],
            "Constraints:",
            *[f"- {x}" for x in goal.constraints],
            "Return the final answer directly.",
        ])
        try:
            response = self.provider.complete([Message("user", prompt)], purpose="raw_answer")
        except BudgetExceeded as exc:
            return RawRun(RunStatus.BUDGET_EXHAUSTED, None, str(exc))
        except Exception as exc:
            return RawRun(RunStatus.FAILED, None, f"{type(exc).__name__}: {exc}")
        return RawRun(RunStatus.SUCCEEDED, response.text)
