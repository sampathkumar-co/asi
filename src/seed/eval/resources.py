from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ResourceUsage:
    wall_time_s: float = 0.0
    model_calls: int = 0
    tool_calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    human_interventions: int = 0
    compute_seconds: float = 0.0

    def validate(self) -> None:
        values = (
            self.wall_time_s, self.model_calls, self.tool_calls, self.input_tokens,
            self.output_tokens, self.cost_usd, self.human_interventions, self.compute_seconds,
        )
        if any(float(v) < 0 for v in values):
            raise ValueError("Resource usage cannot be negative")

    @property
    def tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    def normalized_cost(self, *, dollar_weight: float = 1.0, minute_weight: float = 0.02, human_weight: float = 1.0) -> float:
        self.validate()
        return dollar_weight * self.cost_usd + minute_weight * (self.wall_time_s / 60.0) + human_weight * self.human_interventions


@dataclass(frozen=True)
class MeasuredOutput:
    """Candidate output plus externally measured resource usage for one case."""
    output: Any
    usage: ResourceUsage


class ResourceAccumulator:
    def __init__(self) -> None:
        self.model_calls = 0
        self.tool_calls = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self.cost_usd = 0.0
        self.human_interventions = 0
        self.compute_seconds = 0.0

    def add(self, usage: ResourceUsage) -> None:
        usage.validate()
        self.model_calls += usage.model_calls
        self.tool_calls += usage.tool_calls
        self.input_tokens += usage.input_tokens
        self.output_tokens += usage.output_tokens
        self.cost_usd += usage.cost_usd
        self.human_interventions += usage.human_interventions
        self.compute_seconds += usage.compute_seconds

    def snapshot(self, *, wall_time_s: float) -> ResourceUsage:
        return ResourceUsage(
            wall_time_s=wall_time_s,
            model_calls=self.model_calls,
            tool_calls=self.tool_calls,
            input_tokens=self.input_tokens,
            output_tokens=self.output_tokens,
            cost_usd=self.cost_usd,
            human_interventions=self.human_interventions,
            compute_seconds=self.compute_seconds,
        )
