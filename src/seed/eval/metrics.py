from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RunMetrics:
    capability_score: float
    cases: int
    wall_time_s: float
    model_calls: int = 0
    tool_calls: int = 0
    tokens: int = 0
    cost_usd: float = 0.0
    human_interventions: int = 0

    @property
    def efficiency(self) -> float:
        denom = 1.0 + self.cost_usd + self.wall_time_s / 60.0 + self.human_interventions
        return self.capability_score / denom


def metaproductivity(capability_gain: float, compute_cost: float, experiment_cost: float = 0.0, human_cost: float = 0.0) -> float:
    denom = compute_cost + experiment_cost + human_cost
    return capability_gain / denom if denom > 0 else 0.0


def recursive_amplification(previous_metaproductivity: float, current_metaproductivity: float) -> float | None:
    if previous_metaproductivity <= 0:
        return None
    return current_metaproductivity / previous_metaproductivity
