from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Budget:
    max_steps: int = 12
    max_model_calls: int = 24
    max_tool_calls: int = 24
    max_tokens: int = 20_000
    max_cost_usd: float = 2.0

    steps: int = 0
    model_calls: int = 0
    tool_calls: int = 0
    tokens: int = 0
    cost_usd: float = 0.0

    def can_step(self) -> bool:
        return (
            self.steps < self.max_steps
            and self.model_calls <= self.max_model_calls
            and self.tool_calls <= self.max_tool_calls
            and self.tokens <= self.max_tokens
            and self.cost_usd <= self.max_cost_usd
        )

    def charge_step(self) -> None:
        self.steps += 1

    def charge_model(self, tokens: int = 0, cost_usd: float = 0.0) -> None:
        self.model_calls += 1
        self.tokens += max(tokens, 0)
        self.cost_usd += max(cost_usd, 0.0)

    def charge_tool(self) -> None:
        self.tool_calls += 1
