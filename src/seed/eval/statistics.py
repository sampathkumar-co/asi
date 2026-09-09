from __future__ import annotations

from dataclasses import dataclass
from statistics import NormalDist, fmean, stdev
import math
import random


@dataclass(frozen=True)
class ScoreSummary:
    n: int
    mean: float
    stdev: float
    ci_low: float
    ci_high: float


def summarize_scores(scores: list[float] | tuple[float, ...], *, confidence: float = 0.95) -> ScoreSummary:
    if len(scores) < 2:
        raise ValueError("At least two scores are required")
    if not 0.5 < confidence < 1.0:
        raise ValueError("confidence must be between 0.5 and 1")
    bounded = [min(1.0, max(0.0, float(x))) for x in scores]
    mean = fmean(bounded)
    sd = stdev(bounded)
    z = NormalDist().inv_cdf(0.5 + confidence / 2.0)
    margin = z * sd / math.sqrt(len(bounded))
    return ScoreSummary(len(bounded), mean, sd, max(0.0, mean - margin), min(1.0, mean + margin))


@dataclass(frozen=True)
class PairedComparison:
    n: int
    baseline_mean: float
    candidate_mean: float
    mean_gain: float
    ci_low: float
    ci_high: float
    win_rate: float


def paired_bootstrap(
    baseline: list[float] | tuple[float, ...],
    candidate: list[float] | tuple[float, ...],
    *,
    confidence: float = 0.95,
    samples: int = 4000,
    seed: int = 0,
) -> PairedComparison:
    if len(baseline) != len(candidate) or len(baseline) < 2:
        raise ValueError("Paired comparison requires equal-length vectors with n>=2")
    if samples < 200:
        raise ValueError("Use at least 200 bootstrap samples")
    diffs = [float(c) - float(b) for b, c in zip(baseline, candidate)]
    n = len(diffs)
    rng = random.Random(seed)
    boot = sorted(fmean(rng.choice(diffs) for _ in range(n)) for _ in range(samples))
    alpha = (1.0 - confidence) / 2.0
    lo_i = max(0, min(samples - 1, int(alpha * samples)))
    hi_i = max(0, min(samples - 1, int((1.0 - alpha) * samples) - 1))
    return PairedComparison(
        n=n,
        baseline_mean=fmean(float(x) for x in baseline),
        candidate_mean=fmean(float(x) for x in candidate),
        mean_gain=fmean(diffs),
        ci_low=boot[lo_i],
        ci_high=boot[hi_i],
        win_rate=sum(1 for d in diffs if d > 0) / n,
    )
