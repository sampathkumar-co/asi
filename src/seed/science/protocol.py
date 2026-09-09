from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol
import uuid


class Verdict(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    INCONCLUSIVE = "inconclusive"


@dataclass(frozen=True)
class Hypothesis:
    claim: str
    rationale: str
    falsifiers: tuple[str, ...]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass(frozen=True)
class ExperimentPlan:
    hypothesis_id: str
    method: str
    predicted_result: str
    success_metric: str
    controls: tuple[str, ...] = ()
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass(frozen=True)
class ExperimentResult:
    plan_id: str
    observations: dict[str, Any]
    artifact_refs: tuple[str, ...] = ()
    reproducible: bool = False


@dataclass(frozen=True)
class VerificationReport:
    verifier: str
    verdict: Verdict
    confidence: float
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class ResearchRecord:
    hypothesis: Hypothesis
    plan: ExperimentPlan
    result: ExperimentResult
    independent: VerificationReport
    adversarial: VerificationReport

    @property
    def accepted(self) -> bool:
        return (
            self.result.reproducible
            and self.independent.verdict == Verdict.PASS
            and self.adversarial.verdict == Verdict.PASS
            and self.independent.confidence >= 0.8
            and self.adversarial.confidence >= 0.8
        )


class ExperimentRunner(Protocol):
    def run(self, plan: ExperimentPlan) -> ExperimentResult: ...


class Verifier(Protocol):
    name: str
    def verify(self, hypothesis: Hypothesis, plan: ExperimentPlan, result: ExperimentResult) -> VerificationReport: ...


class ResearchCycle:
    """Gate-2 scientific method: proposer and verifiers are separate components."""

    def __init__(self, runner: ExperimentRunner, independent: Verifier, adversarial: Verifier) -> None:
        if independent.name == adversarial.name:
            raise ValueError("Independent and adversarial verifiers must be distinct")
        self.runner = runner
        self.independent = independent
        self.adversarial = adversarial

    def execute(self, hypothesis: Hypothesis, plan: ExperimentPlan) -> ResearchRecord:
        if plan.hypothesis_id != hypothesis.id:
            raise ValueError("Experiment plan does not target the supplied hypothesis")
        result = self.runner.run(plan)
        first = self.independent.verify(hypothesis, plan, result)
        second = self.adversarial.verify(hypothesis, plan, result)
        return ResearchRecord(hypothesis, plan, result, first, second)
