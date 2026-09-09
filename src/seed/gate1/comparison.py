from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json


@dataclass(frozen=True)
class ArmEvidence:
    arm: str
    provider_id: str
    score: float
    status: str
    limits: dict[str, int | float]
    usage: dict[str, int | float]
    transcript_hash: str


@dataclass(frozen=True)
class ComparisonEvidence:
    raw: ArmEvidence
    seed: ArmEvidence

    @property
    def same_provider(self) -> bool:
        return self.raw.provider_id == self.seed.provider_id

    @property
    def same_envelope(self) -> bool:
        return self.raw.limits == self.seed.limits

    @property
    def capability_gain(self) -> float:
        return self.seed.score - self.raw.score

    @property
    def content_hash(self) -> str:
        raw = json.dumps(asdict(self), sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(raw).hexdigest()


def within_limits(evidence: ArmEvidence) -> bool:
    mapping = {
        "steps": "max_steps",
        "model_calls": "max_model_calls",
        "tool_calls": "max_tool_calls",
        "tokens": "max_tokens",
        "cost_usd": "max_cost_usd",
    }
    return all(float(evidence.usage.get(u, 0)) <= float(evidence.limits[l]) for u, l in mapping.items())
