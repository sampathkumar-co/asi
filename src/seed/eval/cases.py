from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


ScoreFn = Callable[[Any], float]


@dataclass(frozen=True)
class EvalCase:
    case_id: str
    prompt: str
    scorer: ScoreFn
    metadata: dict[str, Any] = field(default_factory=dict)


def exact_match(expected: str) -> ScoreFn:
    def score(value: Any) -> float:
        return 1.0 if str(value).strip() == expected.strip() else 0.0
    return score


def numeric_match(expected: float, tolerance: float = 1e-9) -> ScoreFn:
    def score(value: Any) -> float:
        try:
            return 1.0 if abs(float(value) - expected) <= tolerance else 0.0
        except (TypeError, ValueError):
            return 0.0
    return score
