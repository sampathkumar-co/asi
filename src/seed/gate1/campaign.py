from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json

from seed.eval.statistics import PairedComparison, paired_bootstrap
from .realchat import PairedRealChatEvidence


@dataclass(frozen=True)
class ScoredChatPair:
    pair: PairedRealChatEvidence
    raw_score: float
    seed_score: float

    def validate(self) -> None:
        self.pair.validate()
        if not 0.0 <= float(self.raw_score) <= 1.0:
            raise ValueError("raw_score must be in [0,1]")
        if not 0.0 <= float(self.seed_score) <= 1.0:
            raise ValueError("seed_score must be in [0,1]")


@dataclass(frozen=True)
class Gate1Criterion:
    min_pairs: int = 8
    min_mean_gain: float = 0.05
    min_win_rate: float = 0.60
    require_ci_above_zero: bool = True
    require_certification_ready_pairs: bool = True


@dataclass(frozen=True)
class Gate1CampaignSummary:
    provider_id: str
    model_id: str
    surface_id: str
    pair_count: int
    raw_mean: float
    seed_mean: float
    mean_gain: float
    ci_low: float
    ci_high: float
    win_rate: float
    all_pairs_certification_ready: bool
    passed: bool
    failures: tuple[str, ...]
    content_hash: str


def summarize_campaign(
    records: list[ScoredChatPair] | tuple[ScoredChatPair, ...],
    *,
    criterion: Gate1Criterion | None = None,
    bootstrap_samples: int = 4000,
    seed: int = 0,
) -> Gate1CampaignSummary:
    criterion = criterion or Gate1Criterion()
    if len(records) < 2:
        raise ValueError("Gate-1 campaign summary requires at least two paired tasks")
    for record in records:
        record.validate()

    first = records[0].pair.raw
    identity = (first.provider_id, first.model_id, first.surface_id)
    envelope = first.limits
    task_ids: set[str] = set()
    for record in records:
        run = record.pair.raw
        if (run.provider_id, run.model_id, run.surface_id) != identity:
            raise ValueError("campaign mixes provider/model/surface identities")
        if run.limits != envelope:
            raise ValueError("campaign mixes resource envelopes")
        if run.task_id in task_ids:
            raise ValueError(f"duplicate task_id in campaign: {run.task_id}")
        task_ids.add(run.task_id)

    raw_scores = [float(r.raw_score) for r in records]
    seed_scores = [float(r.seed_score) for r in records]
    comparison: PairedComparison = paired_bootstrap(
        raw_scores,
        seed_scores,
        samples=bootstrap_samples,
        seed=seed,
    )
    all_ready = all(r.pair.certification_ready for r in records)

    failures: list[str] = []
    if len(records) < criterion.min_pairs:
        failures.append(f"needs at least {criterion.min_pairs} paired tasks")
    if comparison.mean_gain < criterion.min_mean_gain:
        failures.append("mean capability gain below threshold")
    if comparison.win_rate < criterion.min_win_rate:
        failures.append("paired-task win rate below threshold")
    if criterion.require_ci_above_zero and comparison.ci_low <= 0.0:
        failures.append("paired bootstrap confidence interval does not clear zero")
    if criterion.require_certification_ready_pairs and not all_ready:
        failures.append("one or more pairs lack attested model/usage + Gate-0 receipt evidence")

    body = {
        "provider_id": identity[0],
        "model_id": identity[1],
        "surface_id": identity[2],
        "pair_count": len(records),
        "raw_mean": comparison.baseline_mean,
        "seed_mean": comparison.candidate_mean,
        "mean_gain": comparison.mean_gain,
        "ci_low": comparison.ci_low,
        "ci_high": comparison.ci_high,
        "win_rate": comparison.win_rate,
        "all_pairs_certification_ready": all_ready,
        "passed": not failures,
        "failures": tuple(failures),
    }
    digest = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    return Gate1CampaignSummary(**body, content_hash=digest)
