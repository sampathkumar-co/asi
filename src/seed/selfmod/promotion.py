from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PromotionEvidence:
    parent_score: float
    candidate_score: float
    holdout_score: float
    sandbox_passed: bool
    independent_verification_passed: bool


@dataclass(frozen=True)
class PromotionDecision:
    promote: bool
    reasons: tuple[str, ...]


def decide_promotion(evidence: PromotionEvidence, *, min_gain: float = 0.02, min_holdout: float = 0.7) -> PromotionDecision:
    reasons: list[str] = []
    if not evidence.sandbox_passed:
        reasons.append("sandbox tests failed")
    if not evidence.independent_verification_passed:
        reasons.append("independent verification failed")
    if evidence.candidate_score - evidence.parent_score < min_gain:
        reasons.append("insufficient capability gain")
    if evidence.holdout_score < min_holdout:
        reasons.append("holdout score below threshold")
    return PromotionDecision(not reasons, tuple(reasons))
