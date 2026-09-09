from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
import hashlib


@dataclass(frozen=True)
class FileMutation:
    path: str
    expected_sha256: str | None
    new_content: str


@dataclass(frozen=True)
class PatchProposal:
    proposal_id: str
    parent_id: str
    rationale: str
    mutations: tuple[FileMutation, ...]


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reasons: tuple[str, ...]


class PatchPolicy:
    """Immutable Gate-4 policy for candidate workspaces.

    The policy intentionally excludes evaluator, security, CI, provider credentials,
    and self-modification policy code from mutation.
    """

    allowed_prefixes = (
        "src/seed/agent/",
        "src/seed/search/",
        "configs/agent/",
    )
    forbidden_prefixes = (
        ".git/",
        ".github/",
        "src/seed/eval/",
        "src/seed/selfmod/",
        "src/seed/providers/",
        "docs/security",
    )

    def __init__(self, *, max_files: int = 8, max_total_bytes: int = 128_000) -> None:
        self.max_files = max_files
        self.max_total_bytes = max_total_bytes

    def validate(self, proposal: PatchProposal) -> PolicyDecision:
        reasons: list[str] = []
        if not proposal.mutations:
            reasons.append("proposal has no mutations")
        if len(proposal.mutations) > self.max_files:
            reasons.append("too many files")
        total = 0
        seen: set[str] = set()
        for mutation in proposal.mutations:
            normalized = str(PurePosixPath(mutation.path))
            if normalized.startswith("../") or normalized.startswith("/") or ".." in PurePosixPath(normalized).parts:
                reasons.append(f"path traversal rejected: {mutation.path}")
                continue
            if normalized in seen:
                reasons.append(f"duplicate mutation: {normalized}")
            seen.add(normalized)
            if any(normalized.startswith(p) for p in self.forbidden_prefixes):
                reasons.append(f"forbidden path: {normalized}")
            elif not any(normalized.startswith(p) for p in self.allowed_prefixes):
                reasons.append(f"path outside allowlist: {normalized}")
            total += len(mutation.new_content.encode("utf-8"))
        if total > self.max_total_bytes:
            reasons.append("proposal exceeds byte budget")
        return PolicyDecision(not reasons, tuple(reasons))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
