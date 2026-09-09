from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import tempfile

from .policy import PatchPolicy, PatchProposal, sha256_text


@dataclass(frozen=True)
class DescendantWorkspace:
    path: Path
    proposal_id: str


class DescendantBuilder:
    """Builds a copy-on-write descendant; never mutates the running parent."""

    def __init__(self, base_repo: str | Path, policy: PatchPolicy | None = None) -> None:
        self.base_repo = Path(base_repo).resolve()
        self.policy = policy or PatchPolicy()

    def build(self, proposal: PatchProposal) -> DescendantWorkspace:
        decision = self.policy.validate(proposal)
        if not decision.allowed:
            raise PermissionError("; ".join(decision.reasons))
        root = Path(tempfile.mkdtemp(prefix="seed-descendant-"))
        target = root / "repo"
        shutil.copytree(self.base_repo, target, ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__", "runs", "artifacts"))
        for mutation in proposal.mutations:
            path = target / mutation.path
            resolved = path.resolve()
            if target.resolve() not in resolved.parents:
                raise PermissionError("Mutation escaped descendant workspace")
            if path.exists() and mutation.expected_sha256 is not None:
                current = sha256_text(path.read_text(encoding="utf-8"))
                if current != mutation.expected_sha256:
                    raise RuntimeError(f"Stale mutation for {mutation.path}")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(mutation.new_content, encoding="utf-8")
        return DescendantWorkspace(target, proposal.proposal_id)
