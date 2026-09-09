from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Any


_ALLOWED_ARMS = {"raw", "seed"}
_ALLOWED_ROLES = {"system", "user", "assistant", "tool"}
_EVIDENCE_RANK = {"manual_chat": 0, "platform_export": 1, "api_attested": 2}


@dataclass(frozen=True)
class ChatTurn:
    role: str
    content: str

    def validate(self) -> None:
        if self.role not in _ALLOWED_ROLES:
            raise ValueError(f"unsupported chat role: {self.role}")
        if not isinstance(self.content, str) or not self.content.strip():
            raise ValueError("chat turn content must be non-empty")


@dataclass(frozen=True)
class RealChatRun:
    arm: str
    task_id: str
    provider_id: str
    model_id: str
    surface_id: str
    evidence_level: str
    limits: dict[str, int | float]
    usage: dict[str, int | float]
    turns: tuple[ChatTurn, ...]
    final_answer: str
    gate0_receipt_hash: str | None = None
    model_identity_attested: bool = False
    usage_attested: bool = False

    def validate(self) -> None:
        if self.arm not in _ALLOWED_ARMS:
            raise ValueError(f"arm must be one of {_ALLOWED_ARMS}")
        for field_name in ("task_id", "provider_id", "model_id", "surface_id"):
            if not getattr(self, field_name).strip():
                raise ValueError(f"{field_name} must be non-empty")
        if self.evidence_level not in _EVIDENCE_RANK:
            raise ValueError("unknown evidence_level")
        if not self.turns:
            raise ValueError("real-chat evidence requires at least one turn")
        for turn in self.turns:
            turn.validate()
        if not self.final_answer.strip():
            raise ValueError("final_answer must be non-empty")
        for key, value in self.limits.items():
            if float(value) < 0:
                raise ValueError(f"negative limit: {key}")
        for key, value in self.usage.items():
            if float(value) < 0:
                raise ValueError(f"negative usage: {key}")
        if self.gate0_receipt_hash is not None:
            if len(self.gate0_receipt_hash) != 64 or any(c not in "0123456789abcdef" for c in self.gate0_receipt_hash.lower()):
                raise ValueError("gate0_receipt_hash must be a SHA-256 hex digest")

    @property
    def content_hash(self) -> str:
        self.validate()
        payload = asdict(self)
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    @property
    def evidence_rank(self) -> int:
        return _EVIDENCE_RANK[self.evidence_level]

    @property
    def within_declared_limits(self) -> bool:
        mapping = {
            "steps": "max_steps",
            "model_calls": "max_model_calls",
            "tool_calls": "max_tool_calls",
            "tokens": "max_tokens",
            "cost_usd": "max_cost_usd",
        }
        for usage_key, limit_key in mapping.items():
            if limit_key in self.limits and float(self.usage.get(usage_key, 0)) > float(self.limits[limit_key]):
                return False
        return True


@dataclass(frozen=True)
class PairedRealChatEvidence:
    raw: RealChatRun
    seed: RealChatRun

    def validate(self) -> None:
        self.raw.validate()
        self.seed.validate()
        if self.raw.arm != "raw" or self.seed.arm != "seed":
            raise ValueError("pair must contain raw and seed arms")
        if self.raw.task_id != self.seed.task_id:
            raise ValueError("raw and seed task_id differ")
        if self.raw.provider_id != self.seed.provider_id:
            raise ValueError("raw and seed provider_id differ")
        if self.raw.model_id != self.seed.model_id:
            raise ValueError("raw and seed model_id differ")
        if self.raw.surface_id != self.seed.surface_id:
            raise ValueError("raw and seed surface_id differ")
        if self.raw.limits != self.seed.limits:
            raise ValueError("raw and seed resource envelopes differ")
        if not self.raw.within_declared_limits or not self.seed.within_declared_limits:
            raise ValueError("one or both arms exceed the declared resource envelope")

    @property
    def content_hash(self) -> str:
        self.validate()
        payload = {"raw": asdict(self.raw), "seed": asdict(self.seed)}
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    @property
    def minimum_evidence_level(self) -> str:
        rank = min(self.raw.evidence_rank, self.seed.evidence_rank)
        return {v: k for k, v in _EVIDENCE_RANK.items()}[rank]

    @property
    def certification_ready(self) -> bool:
        """True only when key model/usage claims and Gate-0 scoring are externally anchored.

        Normal manually copied ChatGPT conversations are useful pilot evidence but do not
        satisfy this stronger condition by themselves.
        """
        self.validate()
        return (
            min(self.raw.evidence_rank, self.seed.evidence_rank) >= _EVIDENCE_RANK["platform_export"]
            and self.raw.model_identity_attested
            and self.seed.model_identity_attested
            and self.raw.usage_attested
            and self.seed.usage_attested
            and self.raw.gate0_receipt_hash is not None
            and self.seed.gate0_receipt_hash is not None
        )


def _turns(rows: list[dict[str, Any]]) -> tuple[ChatTurn, ...]:
    return tuple(ChatTurn(str(row["role"]), str(row["content"])) for row in rows)


def run_from_dict(payload: dict[str, Any]) -> RealChatRun:
    run = RealChatRun(
        arm=str(payload["arm"]),
        task_id=str(payload["task_id"]),
        provider_id=str(payload["provider_id"]),
        model_id=str(payload["model_id"]),
        surface_id=str(payload["surface_id"]),
        evidence_level=str(payload["evidence_level"]),
        limits=dict(payload["limits"]),
        usage=dict(payload.get("usage", {})),
        turns=_turns(list(payload["turns"])),
        final_answer=str(payload["final_answer"]),
        gate0_receipt_hash=payload.get("gate0_receipt_hash"),
        model_identity_attested=bool(payload.get("model_identity_attested", False)),
        usage_attested=bool(payload.get("usage_attested", False)),
    )
    run.validate()
    return run


def load_pair(raw_path: str | Path, seed_path: str | Path) -> PairedRealChatEvidence:
    raw_payload = json.loads(Path(raw_path).read_text(encoding="utf-8"))
    seed_payload = json.loads(Path(seed_path).read_text(encoding="utf-8"))
    pair = PairedRealChatEvidence(run_from_dict(raw_payload), run_from_dict(seed_payload))
    pair.validate()
    return pair
