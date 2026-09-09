from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json

from seed.core.budget import Budget, BudgetExceeded
from .base import Message, ModelProvider, ModelResponse


@dataclass(frozen=True)
class ModelCallRecord:
    index: int
    provider_id: str
    purpose: str
    request_hash: str
    response_hash: str
    input_tokens: int
    output_tokens: int
    cost_usd: float


class BudgetedProvider:
    """Trusted wrapper that meters model usage and records tamper-evident call metadata."""

    def __init__(self, inner: ModelProvider, budget: Budget, *, provider_id: str) -> None:
        self.inner = inner
        self.budget = budget
        self.provider_id = provider_id
        self.records: list[ModelCallRecord] = []

    @staticmethod
    def _hash(value: object) -> str:
        raw = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
        return hashlib.sha256(raw).hexdigest()

    def complete(self, messages: list[Message], *, purpose: str) -> ModelResponse:
        if not self.budget.can_model_call():
            raise BudgetExceeded("model-call budget exhausted before request")
        request_hash = self._hash([asdict(m) for m in messages])
        response = self.inner.complete(messages, purpose=purpose)
        self.budget.charge_model(response.total_tokens, response.cost_usd)
        self.records.append(
            ModelCallRecord(
                index=len(self.records),
                provider_id=self.provider_id,
                purpose=purpose,
                request_hash=request_hash,
                response_hash=self._hash(response.text),
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                cost_usd=response.cost_usd,
            )
        )
        return response

    @property
    def transcript_hash(self) -> str:
        return self._hash([asdict(r) for r in self.records])
