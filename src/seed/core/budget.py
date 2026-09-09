from __future__ import annotations

from dataclasses import asdict, dataclass


class BudgetExceeded(RuntimeError):
    pass


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

    def __post_init__(self) -> None:
        limits = (self.max_steps, self.max_model_calls, self.max_tool_calls, self.max_tokens)
        if any(v < 0 for v in limits) or self.max_cost_usd < 0:
            raise ValueError("Budget limits must be non-negative")

    def can_step(self) -> bool:
        return self.steps < self.max_steps

    def can_model_call(self) -> bool:
        return self.model_calls < self.max_model_calls and self.tokens <= self.max_tokens and self.cost_usd <= self.max_cost_usd

    def can_tool_call(self) -> bool:
        return self.tool_calls < self.max_tool_calls

    def charge_step(self) -> None:
        if self.steps + 1 > self.max_steps:
            raise BudgetExceeded("step budget exceeded")
        self.steps += 1

    def charge_model(self, tokens: int = 0, cost_usd: float = 0.0) -> None:
        tokens = max(int(tokens), 0)
        cost_usd = max(float(cost_usd), 0.0)
        if self.model_calls + 1 > self.max_model_calls:
            raise BudgetExceeded("model-call budget exceeded")
        if self.tokens + tokens > self.max_tokens:
            raise BudgetExceeded("token budget exceeded")
        if self.cost_usd + cost_usd > self.max_cost_usd:
            raise BudgetExceeded("cost budget exceeded")
        self.model_calls += 1
        self.tokens += tokens
        self.cost_usd += cost_usd

    def charge_tool(self) -> None:
        if self.tool_calls + 1 > self.max_tool_calls:
            raise BudgetExceeded("tool-call budget exceeded")
        self.tool_calls += 1

    def limits(self) -> dict[str, int | float]:
        return {
            "max_steps": self.max_steps,
            "max_model_calls": self.max_model_calls,
            "max_tool_calls": self.max_tool_calls,
            "max_tokens": self.max_tokens,
            "max_cost_usd": self.max_cost_usd,
        }

    def usage(self) -> dict[str, int | float]:
        return {
            "steps": self.steps,
            "model_calls": self.model_calls,
            "tool_calls": self.tool_calls,
            "tokens": self.tokens,
            "cost_usd": self.cost_usd,
        }
