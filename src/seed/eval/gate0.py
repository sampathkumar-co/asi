from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import secrets
import tempfile
from typing import Any

from .holdout import load_private_holdout
from .integrity import snapshot_tree, unchanged
from .repeated import run_repeated
from .signing import ReceiptSigner, SignedReceipt
from .statistics import paired_bootstrap, summarize_scores


@dataclass(frozen=True)
class Gate0Certificate:
    gate: int
    qualification: str
    passed: bool
    checks: dict[str, bool]
    evidence: dict[str, Any]
    content_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _hash_body(body: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    ).hexdigest()


def _write_fixture(path: Path, suite_id: str, cases: list[dict[str, Any]]) -> None:
    path.write_text(json.dumps({"suite_id": suite_id, "cases": cases}, sort_keys=True), encoding="utf-8")


def run_gate0_qualification(repo_root: str | Path) -> Gate0Certificate:
    """Qualify the Gate-0 measurement infrastructure in a clean, fail-closed test.

    This certifies evaluator plumbing, not frontier-model capability. The private
    fixtures are generated outside the candidate repository, then evaluated by a
    trusted control process using both known-good and known-bad canary candidates.
    """
    root = Path(repo_root).resolve()
    eval_root = root / "src" / "seed" / "eval"
    before = snapshot_tree(eval_root)

    checks: dict[str, bool] = {}
    evidence: dict[str, Any] = {"repo_root": str(root), "evaluator_digest_before": before.digest}

    with tempfile.TemporaryDirectory(prefix="seed-gate0-private-") as private_dir:
        private = Path(private_dir)
        hidden_path = private / "hidden.json"
        ood_path = private / "ood.json"
        _write_fixture(hidden_path, "gate0-private-canary-v1", [
            {"id": "h1", "prompt": "alpha-marker", "type": "exact", "expected": "A"},
            {"id": "h2", "prompt": "numeric-six-seven", "type": "numeric", "expected": 42},
            {"id": "h3", "prompt": "seed-normalization", "type": "exact", "expected": "seed"},
        ])
        _write_fixture(ood_path, "gate0-ood-canary-v1", [
            {"id": "o1", "prompt": "beta-marker", "type": "exact", "expected": "B"},
            {"id": "o2", "prompt": "numeric-nine-ten", "type": "numeric", "expected": 19},
        ])

        hidden, hidden_manifest = load_private_holdout(hidden_path, repo_root=root)
        ood, ood_manifest = load_private_holdout(ood_path, repo_root=root)
        checks["private_holdouts_external"] = not str(hidden_path.resolve()).startswith(str(root)) and not str(ood_path.resolve()).startswith(str(root))

        answers = {
            "alpha-marker": "A",
            "numeric-six-seven": 42,
            "seed-normalization": "seed",
            "beta-marker": "B",
            "numeric-nine-ten": 19,
        }
        good_factory = lambda run: (lambda prompt: answers[prompt])
        bad_factory = lambda run: (lambda prompt: "definitely-wrong")

        hidden_good = run_repeated(hidden, "qualification-good-hidden", good_factory, runs=5)
        ood_good = run_repeated(ood, "qualification-good-ood", good_factory, runs=5)
        hidden_bad = run_repeated(hidden, "qualification-bad-hidden", bad_factory, runs=5)

        hidden_summary = summarize_scores([o.score for o in hidden_good.outcomes])
        ood_summary = summarize_scores([o.score for o in ood_good.outcomes])
        bad_summary = summarize_scores([o.score for o in hidden_bad.outcomes])
        checks["known_good_passes_hidden"] = hidden_summary.ci_low >= 0.99
        checks["known_good_passes_ood"] = ood_summary.ci_low >= 0.99
        checks["known_bad_fails_closed"] = bad_summary.ci_high <= 0.01

        signer = ReceiptSigner(secrets.token_bytes(32))
        signed: list[tuple[Any, SignedReceipt]] = []
        for outcome in (*hidden_good.outcomes, *ood_good.outcomes, *hidden_bad.outcomes):
            signed.append((outcome.receipt, signer.sign(outcome.receipt)))
        checks["all_receipts_signed_and_verified"] = all(signer.verify(r, s) for r, s in signed)
        receipt, signature = signed[0]
        tampered = SignedReceipt(signature.content_hash, "0" * len(signature.signature), signature.algorithm)
        checks["tampered_signature_rejected"] = not signer.verify(receipt, tampered)

        comparison = paired_bootstrap([0.0] * 8, [1.0] * 8, samples=1000, seed=7)
        checks["paired_statistics_discriminate"] = comparison.ci_low > 0.9 and comparison.mean_gain == 1.0

        evidence.update({
            "hidden_manifest_sha256": hidden_manifest.sha256,
            "ood_manifest_sha256": ood_manifest.sha256,
            "hidden_known_good": asdict(hidden_summary),
            "ood_known_good": asdict(ood_summary),
            "hidden_known_bad": asdict(bad_summary),
            "paired_statistics_canary": asdict(comparison),
            "signed_receipts_checked": len(signed),
        })

    after = snapshot_tree(eval_root)
    checks["evaluator_unchanged_during_qualification"] = unchanged(before, after)
    evidence["evaluator_digest_after"] = after.digest
    evidence["evaluator_files"] = after.files

    passed = all(checks.values())
    body = {"gate": 0, "qualification": "gate0-infrastructure-v1", "passed": passed, "checks": checks, "evidence": evidence}
    return Gate0Certificate(content_hash=_hash_body(body), **body)


def write_gate0_certificate(certificate: Gate0Certificate, path: str | Path) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(certificate.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
