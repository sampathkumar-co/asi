from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
import time
from typing import Callable

from seed.core.budget import Budget, BudgetExceeded
from seed.providers.base import Message, ModelProvider, ProviderError
from seed.providers.budgeted import BudgetedProvider, ModelCallRecord
from seed.providers.ollama import OllamaProvider
from .attestation import implementation_manifest
from .schema import ResearchTask, load_research_tasks


class ModelProtocolError(ValueError):
    """Model output remained invalid after the frozen bounded repair path."""


@dataclass(frozen=True)
class ResearchStep:
    hypothesis_id: str
    experiment_id: str
    predicted_outcome_id: str
    control_ids: tuple[str, ...]
    rejected_hypothesis_ids: tuple[str, ...]
    risk_ids: tuple[str, ...]
    observed_outcome_id: str
    observation: str
    hypothesis_predictions: tuple[tuple[str, str], ...] = ()
    hypothesis_probabilities: tuple[tuple[str, tuple[tuple[str, float], ...]], ...] = ()
    information_gain: float = 0.0
    posterior_probabilities: tuple[tuple[str, float], ...] = ()


@dataclass(frozen=True)
class ResearchRevision:
    after_experiment_id: str
    hypothesis_id: str
    rejected_hypothesis_ids: tuple[str, ...]
    risk_ids: tuple[str, ...]
    confidence: float
    reason: str


@dataclass(frozen=True)
class VerificationEvidence:
    verifier: str
    verdict: str
    confidence: float
    risk_ids: tuple[str, ...]
    reason: str
    supported_hypothesis_ids: tuple[str, ...] = ()
    direct_evidence_defect: bool = False
    defect_summary: str = ""
    mechanical_supported_hypothesis_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class ResearchArmEvidence:
    task_id: str
    arm: str
    provider_id: str
    model_id: str
    history: tuple[ResearchStep, ...]
    final_hypothesis_id: str | None
    rejected_hypothesis_ids: tuple[str, ...]
    risk_ids: tuple[str, ...]
    confidence: float
    independent: VerificationEvidence | None
    adversarial: VerificationEvidence | None
    accepted: bool | None
    status: str
    limits: dict[str, int | float]
    usage: dict[str, int | float]
    transcript_hash: str
    revisions: tuple[ResearchRevision, ...] = ()
    call_purposes: tuple[str, ...] = ()
    repair_events: tuple[dict[str, str], ...] = ()
    precommitted_probability_matrix: tuple[tuple[str, str, tuple[tuple[str, float], ...]], ...] = ()
    precommitted_outcome_support: tuple[tuple[str, str, tuple[str, ...]], ...] = ()
    final_posterior: tuple[tuple[str, float], ...] = ()
    failure_kind: str | None = None
    failure_message: str | None = None

    @property
    def content_hash(self) -> str:
        raw = json.dumps(asdict(self), sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class ResearchPairEvidence:
    raw: ResearchArmEvidence
    seed: ResearchArmEvidence

    def validate(self) -> None:
        if self.raw.task_id != self.seed.task_id:
            raise ValueError("raw/seed task mismatch")
        if self.raw.provider_id != self.seed.provider_id or self.raw.model_id != self.seed.model_id:
            raise ValueError("raw/seed provider or model mismatch")
        if self.raw.limits != self.seed.limits:
            raise ValueError("raw/seed resource envelope mismatch")

    @property
    def content_hash(self) -> str:
        self.validate()
        raw = json.dumps({"raw": asdict(self.raw), "seed": asdict(self.seed)}, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(raw).hexdigest()


def _budget() -> Budget:
    return Budget(max_steps=16, max_model_calls=16, max_tool_calls=0, max_tokens=15000, max_cost_usd=0.0)


def _record_event(task_id: str, arm: str, record: ModelCallRecord) -> dict:
    return {
        "event": "model_call", "task_id": task_id, "arm": arm,
        "index": record.index, "purpose": record.purpose,
        "request_hash": record.request_hash, "response_hash": record.response_hash,
        "input_tokens": record.input_tokens, "output_tokens": record.output_tokens,
        "wall_time_s": record.wall_time_s, "budget_accepted": record.budget_accepted,
    }


def _ids(items) -> set[str]:
    return {x.id for x in items}


def _strings(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or any(not isinstance(x, str) for x in value):
        raise ValueError("expected a list of string ids")
    return tuple(dict.fromkeys(x.strip() for x in value if x.strip()))


def _json_call(provider: BudgetedProvider, budget: Budget, messages: list[Message], purpose: str) -> dict:
    budget.charge_step()
    response = provider.complete(messages, purpose=purpose)
    try:
        data = json.loads(response.text)
    except json.JSONDecodeError as exc:
        if purpose == "gate2_repair":
            raise ModelProtocolError(f"repair returned invalid JSON: {exc}") from exc
        repair = {"stage": purpose, "validation_error": str(exc)[:240], "invalid_output": response.text[:3000]}
        budget.charge_step()
        response = provider.complete([Message("system", "Return only one corrected JSON object. Fix syntax only; preserve all substantive choices and add no evidence."), Message("user", json.dumps(repair))], purpose="gate2_repair")
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as repair_exc:
            raise ModelProtocolError(f"repair returned invalid JSON: {repair_exc}") from repair_exc
    if not isinstance(data, dict):
        raise ModelProtocolError("model output must be a JSON object")
    return data



def _repair_schema(provider: BudgetedProvider, budget: Budget, task: ResearchTask, *, arm: str, stage: str, invalid_output: dict, error: Exception, history: list[ResearchStep], revisions: list[ResearchRevision]) -> dict:
    payload = {
        "stage": stage, "arm": arm, "validation_error": str(error)[:240],
        "allowed_ids": {
            "hypotheses": [x.id for x in task.hypotheses],
            "experiments": {e.id: [o.id for o in e.possible_outcomes] for e in task.experiments},
            "controls": [x.id for x in task.controls], "risks": [x.id for x in task.risks],
            "used_experiments": [x.experiment_id for x in history],
        },
        "invalid_output": invalid_output,
    }
    system = ("Return only one corrected JSON object. Change only fields needed to satisfy validation_error and allowed_ids. Preserve the original scientific choice whenever it has a valid representation. Do not explain, invent evidence, or add any hidden information.")
    return _json_call(provider, budget, [Message("system", system), Message("user", json.dumps(payload, separators=(",", ":")))], "gate2_repair")

def _action(provider: BudgetedProvider, budget: Budget, task: ResearchTask, history: list[ResearchStep], arm: str, revisions: list[ResearchRevision] | None = None) -> dict:
    if arm != "raw":
        raise ValueError("v3 Seed experiment choice is runner-derived")
    public = task.public_dict()
    public["history"] = [asdict(x) for x in history]
    public["schema"] = {
        "hypothesis_id": "one hypothesis id",
        "experiment_id": "one unused experiment id, or null after at least one experiment",
        "prediction_outcome_id": "one declared outcome id expected if hypothesis_id is true; commit before reveal; or null when stopping",
        "control_ids": "list of control ids",
        "rejected_hypothesis_ids": "list of hypothesis ids contradicted by already revealed history only",
        "risk_ids": "list of risk/confound ids currently relevant",
        "reason": "concise rationale",
    }
    system = (
        "Investigate the problem directly and return JSON only using the supplied schema. Choose your best current hypothesis "
        "and next experiment from the available ids. prediction_outcome_id must be the outcome you expect if hypothesis_id is true, before reveal. Do not use Seed's scientific-method scaffold or verifier protocol."
    )
    return _json_call(provider, budget, [Message("system", system), Message("user", json.dumps(public))], "gate2_raw_action")

def _attribute_outcomes(provider: BudgetedProvider, budget: Budget, task: ResearchTask) -> dict:
    payload = {
        "question": task.question,
        "hypotheses": [{"id": h.id, "text": h.text} for h in task.hypotheses],
        "experiments": [{
            "id": experiment.id,
            "description": experiment.description,
            "possible_outcomes": [{"id": x.id, "text": x.text} for x in experiment.possible_outcomes],
        } for experiment in task.experiments],
        "schema": {
            "outcome_support": "experiment id -> outcome id -> non-empty list of declared hypothesis ids whose truth would make that outcome a natural/direct result",
            "notes": "brief causal explanation per experiment",
        },
    }
    system = (
        "No experiment result is available. Work PRE-REVEAL only. For each declared experiment and each possible outcome, "
        "identify which declared hypothesis or hypotheses would most naturally make that outcome occur. Reason from the intervention semantics: "
        "what is varied, matched, removed, isolated, or held fixed. Attribute outcomes to causal hypotheses, not to observed facts. "
        "An outcome may naturally support more than one hypothesis when the experiment cannot distinguish them. Use only declared ids and return JSON only."
    )
    return _json_call(provider, budget, [Message("system", system), Message("user", json.dumps(payload))], "gate2_seed_attribute_outcomes")


def _validated_attribution(task: ResearchTask, data: dict) -> tuple[tuple[str, str, tuple[str, ...]], ...]:
    raw = data.get("outcome_support")
    experiment_ids = {experiment.id for experiment in task.experiments}
    if not isinstance(raw, dict) or set(raw) != experiment_ids:
        raise ValueError("attribution must cover every declared experiment exactly once")
    hypothesis_ids = _ids(task.hypotheses)
    rows: list[tuple[str, str, tuple[str, ...]]] = []
    for experiment in task.experiments:
        outcome_ids = {outcome.id for outcome in experiment.possible_outcomes}
        by_outcome = raw.get(experiment.id)
        if not isinstance(by_outcome, dict) or set(by_outcome) != outcome_ids:
            raise ValueError("attribution must cover every declared outcome exactly once")
        for outcome in experiment.possible_outcomes:
            raw_supported = by_outcome.get(outcome.id)
            if not isinstance(raw_supported, list) or any(not isinstance(item, str) for item in raw_supported):
                raise ValueError("every outcome attribution must be a list of hypothesis ids")
            cleaned = [item.strip() for item in raw_supported if item.strip()]
            if not cleaned:
                raise ValueError("every outcome attribution must name at least one hypothesis")
            if len(cleaned) != len(set(cleaned)):
                raise ValueError("duplicate attributed hypothesis id")
            supported = tuple(cleaned)
            if not set(supported).issubset(hypothesis_ids):
                raise ValueError("invalid attributed hypothesis id")
            rows.append((experiment.id, outcome.id, supported))
    return tuple(rows)


def _canonical_matrices(task: ResearchTask, attribution: tuple[tuple[str, str, tuple[str, ...]], ...], *, support_weight: float = 3.0) -> tuple[dict[str, dict[str, dict[str, float]]], dict[str, dict[str, str]]]:
    if support_weight <= 1.0:
        raise ValueError("support_weight must exceed 1")
    support = {(experiment_id, outcome_id): set(hypotheses) for experiment_id, outcome_id, hypotheses in attribution}
    matrices: dict[str, dict[str, dict[str, float]]] = {}
    categoricals: dict[str, dict[str, str]] = {}
    for hypothesis in task.hypotheses:
        matrices[hypothesis.id] = {}
        categoricals[hypothesis.id] = {}
        for experiment in task.experiments:
            outcome_ids = [outcome.id for outcome in experiment.possible_outcomes]
            supported = [outcome_id for outcome_id in outcome_ids if hypothesis.id in support[(experiment.id, outcome_id)]]
            if not supported or len(supported) == len(outcome_ids):
                weights = {outcome_id: 1.0 for outcome_id in outcome_ids}
            else:
                weights = {outcome_id: (support_weight if outcome_id in supported else 1.0) for outcome_id in outcome_ids}
            total = sum(weights.values())
            probabilities = {outcome_id: weights[outcome_id] / total for outcome_id in outcome_ids}
            matrices[hypothesis.id][experiment.id] = probabilities
            max_probability = max(probabilities.values())
            categoricals[hypothesis.id][experiment.id] = next(outcome_id for outcome_id in outcome_ids if math.isclose(probabilities[outcome_id], max_probability, rel_tol=1e-12, abs_tol=1e-15))
    return matrices, categoricals


def _information_gain(task: ResearchTask, experiment_id: str, matrices: dict[str, dict[str, dict[str, float]]], prior: dict[str, float]) -> float:
    outcome_ids = [x.id for x in task.experiment(experiment_id).possible_outcomes]
    mixture = {outcome_id: sum(prior[hypothesis_id] * matrices[hypothesis_id][experiment_id][outcome_id] for hypothesis_id in prior) for outcome_id in outcome_ids}
    score = 0.0
    for hypothesis_id, prior_probability in prior.items():
        for outcome_id in outcome_ids:
            conditional = matrices[hypothesis_id][experiment_id][outcome_id]
            marginal = mixture[outcome_id]
            if prior_probability > 0.0 and conditional > 0.0 and marginal > 0.0:
                score += prior_probability * conditional * math.log2(conditional / marginal)
    return score


def _select_experiment(task: ResearchTask, matrices: dict[str, dict[str, dict[str, float]]], prior: dict[str, float], used: set[str]) -> tuple[str, float]:
    candidates = [experiment.id for experiment in task.experiments if experiment.id not in used]
    if not candidates:
        raise ValueError("no unused experiment remains")
    scores = {experiment_id: _information_gain(task, experiment_id, matrices, prior) for experiment_id in candidates}
    order = {experiment.id: index for index, experiment in enumerate(task.experiments)}
    selected = max(candidates, key=lambda experiment_id: (scores[experiment_id], -order[experiment_id]))
    return selected, scores[selected]


def _update_posterior(task: ResearchTask, experiment_id: str, matrices: dict[str, dict[str, dict[str, float]]], prior: dict[str, float]) -> dict[str, float]:
    observed = task.experiment(experiment_id).observed_outcome_id
    unnormalized = {hypothesis_id: prior[hypothesis_id] * matrices[hypothesis_id][experiment_id][observed] for hypothesis_id in prior}
    normalizer = sum(unnormalized.values())
    if normalizer <= 0.0:
        raise ValueError("all hypotheses assigned zero likelihood to the observed outcome")
    return {hypothesis_id: value / normalizer for hypothesis_id, value in unnormalized.items()}


def _posterior_best(task: ResearchTask, posterior: dict[str, float]) -> tuple[str, tuple[str, ...]]:
    best_probability = max(posterior.values())
    best = tuple(hypothesis.id for hypothesis in task.hypotheses if math.isclose(posterior[hypothesis.id], best_probability, rel_tol=1e-12, abs_tol=1e-15))
    return best[0], best


def _mechanical_rejections(task: ResearchTask, posterior: dict[str, float], *, min_bayes_factor: float = 3.0) -> tuple[str, ...]:
    final_id, _ = _posterior_best(task, posterior)
    best_probability = posterior[final_id]
    rejected = []
    for hypothesis in task.hypotheses:
        if hypothesis.id == final_id:
            continue
        probability = posterior[hypothesis.id]
        if probability == 0.0 or best_probability + 1e-15 >= min_bayes_factor * probability:
            rejected.append(hypothesis.id)
    return tuple(rejected)


def _seed_design(provider: BudgetedProvider, budget: Budget, task: ResearchTask, history: list[ResearchStep], experiment_id: str, posterior: dict[str, float]) -> dict:
    payload = {
        "task": task.public_dict(),
        "history": [asdict(x) for x in history],
        "runner_selected_experiment_id": experiment_id,
        "runner_posterior": posterior,
        "schema": {
            "control_ids": "list of declared control ids needed for this already-selected experiment",
            "risk_ids": "list of declared risk/confound ids currently relevant",
            "reason": "brief design rationale; do not select a different experiment",
        },
    }
    system = (
        "The runner has already selected the experiment mechanically from blind forecast information gain. Return JSON only. "
        "Do not change the experiment or infer an unrevealed outcome. Choose the declared controls needed to make this experiment interpretable and list material declared risks/confounds."
    )
    return _json_call(provider, budget, [Message("system", system), Message("user", json.dumps(payload))], "gate2_seed_design")


def _validated_seed_design(task: ResearchTask, data: dict) -> tuple[tuple[str, ...], tuple[str, ...]]:
    controls = _strings(data.get("control_ids", []))
    risks = _strings(data.get("risk_ids", []))
    if not set(controls).issubset(_ids(task.controls)):
        raise ValueError("invalid control id")
    if not set(risks).issubset(_ids(task.risks)):
        raise ValueError("invalid risk id")
    return controls, risks


def _validated_step(task: ResearchTask, data: dict, history: list[ResearchStep], *, require_hypothesis_predictions: bool = False) -> ResearchStep | None:
    hypothesis_id = str(data.get("hypothesis_id", ""))
    if hypothesis_id not in _ids(task.hypotheses):
        raise ValueError("invalid hypothesis id")
    experiment_id = data.get("experiment_id")
    if experiment_id is None:
        if not history:
            raise ValueError("at least one experiment is required")
        return None
    if not isinstance(experiment_id, str) or experiment_id not in _ids(task.experiments):
        raise ValueError("invalid experiment id")
    if experiment_id in {x.experiment_id for x in history}:
        raise ValueError("experiment cannot be repeated")
    experiment = task.experiment(experiment_id)
    prediction = data.get("prediction_outcome_id")
    if not isinstance(prediction, str) or prediction not in _ids(experiment.possible_outcomes):
        raise ValueError("invalid pre-evidence prediction")
    hypothesis_predictions: tuple[tuple[str, str], ...] = ()
    hypothesis_probabilities: tuple[tuple[str, tuple[tuple[str, float], ...]], ...] = ()
    if require_hypothesis_predictions:
        raw_predictions = data.get("hypothesis_predictions")
        hypothesis_ids = [item.id for item in task.hypotheses]
        if not isinstance(raw_predictions, dict) or set(raw_predictions) != set(hypothesis_ids):
            raise ValueError("Seed must precommit one outcome prediction for every hypothesis")
        for hid in hypothesis_ids:
            outcome_id = raw_predictions.get(hid)
            if not isinstance(outcome_id, str) or outcome_id not in _ids(experiment.possible_outcomes):
                raise ValueError("invalid hypothesis forecast outcome")
        if raw_predictions[hypothesis_id] != prediction:
            raise ValueError("selected-hypothesis prediction must match hypothesis forecast")
        hypothesis_predictions = tuple((hid, raw_predictions[hid]) for hid in hypothesis_ids)
    controls = _strings(data.get("control_ids", []))
    rejected = _strings(data.get("rejected_hypothesis_ids", []))
    risks = _strings(data.get("risk_ids", []))
    if not set(controls).issubset(_ids(task.controls)):
        raise ValueError("invalid control id")
    if not set(rejected).issubset(_ids(task.hypotheses)):
        raise ValueError("invalid rejected hypothesis id")
    if not set(risks).issubset(_ids(task.risks)):
        raise ValueError("invalid risk id")
    return ResearchStep(
        hypothesis_id=hypothesis_id,
        experiment_id=experiment.id,
        predicted_outcome_id=prediction,
        control_ids=controls,
        rejected_hypothesis_ids=rejected,
        risk_ids=risks,
        observed_outcome_id=experiment.observed_outcome_id,
        observation=experiment.observation,
        hypothesis_predictions=hypothesis_predictions,
    )


def _final_report(provider: BudgetedProvider, budget: Budget, task: ResearchTask, history: list[ResearchStep], arm: str, revisions: list[ResearchRevision] | None = None, *, forced_final_id: str | None = None, forced_rejected: tuple[str, ...] = (), posterior: dict[str, float] | None = None) -> dict:
    prompt = {
        "task": task.public_dict(),
        "history": [asdict(x) for x in history],
        "revisions": [asdict(x) for x in (revisions or [])],
        "schema": {
            "final_hypothesis_id": "one hypothesis id",
            "rejected_hypothesis_ids": "list of hypothesis ids contradicted by evidence",
            "risk_ids": "list of unresolved or controlled risk/confound ids",
            "confidence": "number 0..1",
            "reason": "concise evidence-based conclusion",
        },
    }
    if arm == "seed":
        if forced_final_id is None or posterior is None:
            raise ValueError("Seed final report requires runner-derived posterior conclusion")
        prompt["runner_derived_final_hypothesis_id"] = forced_final_id
        prompt["runner_derived_rejected_hypothesis_ids"] = list(forced_rejected)
        prompt["runner_posterior"] = posterior
        system = (
            "The runner has already derived the final hypothesis and rejected competitors mechanically from the frozen pre-reveal forecast posterior. "
            "Return JSON only. Explain that runner-derived conclusion from the revealed evidence, preserve the supplied final_hypothesis_id and rejected_hypothesis_ids, and list material risks. Do not override the runner."
        )
        purpose = "gate2_seed_final"
    else:
        system = "Give your best final conclusion from the observations. Return JSON only using the supplied schema."
        purpose = "gate2_raw_final"
    return _json_call(provider, budget, [Message("system", system), Message("user", json.dumps(prompt))], purpose)


def _validated_final(task: ResearchTask, data: dict) -> tuple[str, tuple[str, ...], tuple[str, ...], float]:
    hypothesis_id = str(data.get("final_hypothesis_id", ""))
    if hypothesis_id not in _ids(task.hypotheses):
        raise ValueError("invalid final hypothesis id")
    rejected = _strings(data.get("rejected_hypothesis_ids", []))
    risks = _strings(data.get("risk_ids", []))
    if not set(rejected).issubset(_ids(task.hypotheses)):
        raise ValueError("invalid final rejected-hypothesis id")
    if not set(risks).issubset(_ids(task.risks)):
        raise ValueError("invalid final risk id")
    confidence = float(data.get("confidence", 0.0))
    if not 0.0 <= confidence <= 1.0:
        raise ValueError("final confidence out of range")
    return hypothesis_id, rejected, risks, confidence


def _mechanical_support(task: ResearchTask, history: list[ResearchStep]) -> tuple[dict[str, float], tuple[str, ...]]:
    hypothesis_ids = tuple(x.id for x in task.hypotheses)
    products = {hid: 1.0 for hid in hypothesis_ids}
    if not history:
        raise ValueError("verifier requires revealed history")
    for step in history:
        distributions = {hid: dict(probs) for hid, probs in step.hypothesis_probabilities}
        if set(distributions) != set(hypothesis_ids):
            raise ValueError("verifier requires complete frozen hypothesis likelihood forecasts")
        for hid in hypothesis_ids:
            if step.observed_outcome_id not in distributions[hid]:
                raise ValueError("observed outcome missing from frozen likelihood forecast")
            products[hid] *= float(distributions[hid][step.observed_outcome_id])
    best_score = max(products.values())
    best = tuple(hid for hid in hypothesis_ids if math.isclose(products[hid], best_score, rel_tol=1e-12, abs_tol=1e-15))
    return products, best


def _verifier_verdict(final_id: str, model_supported: tuple[str, ...], mechanical_best: tuple[str, ...], direct_defect: bool) -> str:
    return "pass" if (
        mechanical_best == (final_id,)
        and model_supported == (final_id,)
        and not direct_defect
    ) else "fail"


def _verify(provider: BudgetedProvider, budget: Budget, task: ResearchTask, history: list[ResearchStep], final: dict, kind: str, revisions: list[ResearchRevision] | None = None) -> VerificationEvidence:
    payload = {
        "task": task.public_dict(),
        "history": [asdict(x) for x in history],
        "revisions": [asdict(x) for x in (revisions or [])],
        "final_report": final,
    }
    payload["schema"] = {
        "supported_hypothesis_ids": "non-empty list of declared hypothesis ids tied for strongest support; include every tie",
        "has_direct_evidence_defect": "boolean; true only for a concrete contradiction or protocol/evidence defect grounded in the revealed record, never for generic residual uncertainty",
        "defect_summary": "concise concrete defect description, or 'none' when false",
        "confidence": "0..1 confidence in this support assessment",
        "risk_ids": "list of declared risk ids that remain relevant",
        "reason": "concise evidence-based audit summary",
    }
    common = (
        "Evaluate only the declared hypotheses against the revealed evidence. "
        "supported_hypothesis_ids must contain every declared hypothesis tied for strongest evidential support. "
        "Residual risks or hypothetical unknown confounders belong in risk_ids/reason and MUST NOT by themselves create a defect or a tie. "
        "confidence is your confidence that this support-set audit is correct given the revealed record; it is NOT the runner posterior probability and MUST NOT be copied mechanically from posterior/confidence values in the record. "
        "Set has_direct_evidence_defect=true only for a concrete contradiction, prediction/evidence mismatch, or protocol/evidence defect visible in the record. "
        "Return JSON only; do not emit a verdict label because the runner derives pass/fail."
    )
    if kind == "independent":
        system = "Independently audit the conclusion. " + common
        purpose = "gate2_independent"
    else:
        system = "Act as an adversarial scientific reviewer and actively search for falsifiers and competing declared hypotheses. " + common
        purpose = "gate2_adversarial"
    data = _json_call(provider, budget, [Message("system", system), Message("user", json.dumps(payload))], purpose)
    _, mechanical_best = _mechanical_support(task, history)

    def validate(value: dict) -> VerificationEvidence:
        supported = _strings(value.get("supported_hypothesis_ids", []))
        hypothesis_ids = _ids(task.hypotheses)
        if not supported:
            raise ValueError("verifier supported_hypothesis_ids must be non-empty")
        if not set(supported).issubset(hypothesis_ids):
            raise ValueError("invalid verifier supported hypothesis id")
        direct_defect = value.get("has_direct_evidence_defect")
        if not isinstance(direct_defect, bool):
            raise ValueError("verifier has_direct_evidence_defect must be boolean")
        defect_summary = value.get("defect_summary", "")
        if not isinstance(defect_summary, str):
            raise ValueError("verifier defect_summary must be string")
        final_id = str(final.get("final_hypothesis_id", ""))
        verdict = _verifier_verdict(final_id, supported, mechanical_best, direct_defect)
        confidence = float(value.get("confidence", 0.0))
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("verifier confidence out of range")
        risks = _strings(value.get("risk_ids", []))
        if not set(risks).issubset(_ids(task.risks)):
            raise ValueError("invalid verifier risk id")
        return VerificationEvidence(kind, verdict, confidence, risks, str(value.get("reason", ""))[:320], supported, direct_defect, defect_summary[:240], mechanical_best)
    try:
        return validate(data)
    except ValueError as exc:
        repaired = _repair_schema(provider, budget, task, arm="seed", stage=f"{kind}_verifier", invalid_output=data, error=exc, history=history, revisions=list(revisions or []))
        try:
            return validate(repaired)
        except ValueError as repair_exc:
            raise ModelProtocolError(str(repair_exc)) from repair_exc


def _arm_evidence(task: ResearchTask, arm: str, meter: BudgetedProvider, budget: Budget, history: list[ResearchStep], final: tuple | None, status: str, independent=None, adversarial=None, revisions: list[ResearchRevision] | None = None, repair_events: list[dict[str, str]] | None = None, precommitted_probability_matrix: tuple[tuple[str, str, tuple[tuple[str, float], ...]], ...] = (), precommitted_outcome_support: tuple[tuple[str, str, tuple[str, ...]], ...] = (), final_posterior: tuple[tuple[str, float], ...] = (), failure_kind: str | None = None, failure_message: str | None = None) -> ResearchArmEvidence:
    if final is None:
        hypothesis_id, rejected, risks, confidence = None, (), (), 0.0
    else:
        hypothesis_id, rejected, risks, confidence = final
    accepted = None
    if arm == "seed" and independent is not None and adversarial is not None:
        accepted = (
            independent.verdict == "pass" and adversarial.verdict == "pass"
            and independent.confidence >= 0.8 and adversarial.confidence >= 0.8
        )
    return ResearchArmEvidence(
        task.task_id, arm, meter.provider_id, meter.provider_id.removeprefix("ollama:"), tuple(history),
        hypothesis_id, tuple(rejected), tuple(risks), confidence, independent, adversarial, accepted,
        status, budget.limits(), budget.usage(), meter.transcript_hash, tuple(revisions or []),
        tuple(record.purpose for record in meter.records), tuple(repair_events or []),
        tuple(precommitted_probability_matrix), tuple(precommitted_outcome_support), tuple(final_posterior),
        failure_kind, failure_message,
    )


def _run_arm(task: ResearchTask, provider: BudgetedProvider, budget: Budget, arm: str) -> ResearchArmEvidence:
    history: list[ResearchStep] = []
    revisions: list[ResearchRevision] = []
    repair_events: list[dict[str, str]] = []
    precommitted_matrix: tuple[tuple[str, str, tuple[tuple[str, float], ...]], ...] = ()
    precommitted_support: tuple[tuple[str, str, tuple[str, ...]], ...] = ()
    posterior_evidence: tuple[tuple[str, float], ...] = ()
    final = None
    independent = adversarial = None
    failure_kind = failure_message = None
    try:
        def validate_or_repair(stage: str, data: dict, validator):
            try:
                return validator(data)
            except ValueError as exc:
                repair_events.append({"stage": stage, "error": str(exc)[:240], "invalid_output_sha256": hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()})
                repaired = _repair_schema(provider, budget, task, arm=arm, stage=stage, invalid_output=data, error=exc, history=history, revisions=revisions)
                try:
                    return validator(repaired)
                except ValueError as repair_exc:
                    raise ModelProtocolError(str(repair_exc)) from repair_exc

        if arm == "seed":
            attribution_data = _attribute_outcomes(provider, budget, task)
            precommitted_support = validate_or_repair("attribution", attribution_data, lambda value: _validated_attribution(task, value))
            matrices, categoricals = _canonical_matrices(task, precommitted_support)
            frozen_rows = []
            for hypothesis in task.hypotheses:
                for experiment in task.experiments:
                    probabilities = tuple((outcome.id, matrices[hypothesis.id][experiment.id][outcome.id]) for outcome in experiment.possible_outcomes)
                    frozen_rows.append((hypothesis.id, experiment.id, probabilities))
            precommitted_matrix = tuple(frozen_rows)
            posterior = {hypothesis.id: 1.0 / len(task.hypotheses) for hypothesis in task.hypotheses}
            used: set[str] = set()
            for _ in range(task.max_experiments):
                experiment_id, information_gain = _select_experiment(task, matrices, posterior, used)
                current_hypothesis_id, _ = _posterior_best(task, posterior)
                design_data = _seed_design(provider, budget, task, history, experiment_id, posterior)
                controls, risks = validate_or_repair("design", design_data, lambda value: _validated_seed_design(task, value))
                experiment = task.experiment(experiment_id)
                forecasts = tuple((hypothesis.id, categoricals[hypothesis.id][experiment_id]) for hypothesis in task.hypotheses)
                probability_rows = tuple((hypothesis.id, tuple(matrices[hypothesis.id][experiment_id].items())) for hypothesis in task.hypotheses)
                prediction = categoricals[current_hypothesis_id][experiment_id]
                posterior = _update_posterior(task, experiment_id, matrices, posterior)
                posterior_evidence = tuple((hypothesis.id, posterior[hypothesis.id]) for hypothesis in task.hypotheses)
                revised_hypothesis_id, _ = _posterior_best(task, posterior)
                rejected = _mechanical_rejections(task, posterior)
                step = ResearchStep(
                    current_hypothesis_id, experiment.id, prediction, controls, rejected, risks,
                    experiment.observed_outcome_id, experiment.observation, forecasts, probability_rows,
                    information_gain, posterior_evidence,
                )
                history.append(step)
                revisions.append(ResearchRevision(
                    experiment.id, revised_hypothesis_id, rejected, risks, max(posterior.values()),
                    f"Runner Bayesian update after {experiment.id}; posterior winner {revised_hypothesis_id}.",
                ))
                used.add(experiment_id)

            final_id, _ = _posterior_best(task, posterior)
            final_rejected = _mechanical_rejections(task, posterior)
            final_data = _final_report(provider, budget, task, history, arm, revisions, forced_final_id=final_id, forced_rejected=final_rejected, posterior=posterior)
            final_data = dict(final_data)
            final_data["final_hypothesis_id"] = final_id
            final_data["rejected_hypothesis_ids"] = list(final_rejected)
            final_data["confidence"] = max(posterior.values())
            final = validate_or_repair("final", final_data, lambda value: _validated_final(task, value))
            independent = _verify(provider, budget, task, history, final_data, "independent", revisions)
            adversarial = _verify(provider, budget, task, history, final_data, "adversarial", revisions)
        else:
            for _ in range(task.max_experiments):
                action = _action(provider, budget, task, history, arm, revisions)
                step = validate_or_repair("action", action, lambda value: _validated_step(task, value, history))
                if step is None:
                    break
                history.append(step)
            final_data = _final_report(provider, budget, task, history, arm, revisions)
            final = validate_or_repair("final", final_data, lambda value: _validated_final(task, value))
        status = "succeeded"
    except BudgetExceeded as exc:
        status = "budget_exhausted"
        failure_kind, failure_message = "budget", str(exc)[:500]
    except ProviderError as exc:
        status = "infrastructure_error"
        failure_kind, failure_message = "provider", str(exc)[:500]
    except ModelProtocolError as exc:
        status = "failed:ModelProtocolError"
        failure_kind, failure_message = "model_protocol", str(exc)[:500]
    except Exception as exc:
        status = f"failed:{type(exc).__name__}"
        failure_kind = "runner"
        failure_message = f"{type(exc).__name__}: {exc}"[:500]
    return _arm_evidence(
        task, arm, provider, budget, history, final, status, independent, adversarial, revisions, repair_events,
        precommitted_matrix, precommitted_support, posterior_evidence, failure_kind, failure_message,
    )


def run_research_pair(task: ResearchTask, provider_factory: Callable[[], ModelProvider], *, provider_id: str, progress: Callable[[dict], None] | None = None) -> ResearchPairEvidence:
    def make(arm: str) -> ResearchArmEvidence:
        budget = _budget()
        callback = (lambda record: progress(_record_event(task.task_id, arm, record))) if progress else None
        meter = BudgetedProvider(provider_factory(), budget, provider_id=provider_id, on_record=callback)
        return _run_arm(task, meter, budget, arm)
    pair = ResearchPairEvidence(make("raw"), make("seed"))
    pair.validate()
    return pair


def _hash_body(body: dict) -> str:
    unsigned = {k: v for k, v in body.items() if k != "content_hash"}
    return hashlib.sha256(json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _atomic_write(path: Path, body: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    last_error = None
    for attempt in range(30):
        try:
            tmp.replace(path)
            return
        except PermissionError as exc:
            last_error = exc
            if attempt == 29:
                break
            time.sleep(min(0.05 * (2 ** min(attempt, 4)), 0.5))
    raise last_error or RuntimeError("checkpoint replacement failed")


def _append_jsonl(path: Path, event: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n")
        handle.flush()


def _body(suite_id: str, provider_id: str, model: str, manifest: dict, implementation: dict, settings: dict, pairs: list[dict]) -> dict:
    body = {
        "gate": 2,
        "suite_id": suite_id,
        "provider_id": provider_id,
        "model": model,
        "model_manifest": manifest,
        "seed_implementation": implementation,
        "settings": settings,
        "pairs": pairs,
    }
    body["content_hash"] = _hash_body(body)
    return body


def validate_checkpoint_identity(prior: dict, expected: dict) -> None:
    if prior.get("content_hash") != _hash_body(prior):
        raise ValueError("Gate-2 checkpoint content hash mismatch")
    fields = ("gate", "suite_id", "provider_id", "model", "model_manifest", "seed_implementation", "settings")
    if any(prior.get(field) != expected.get(field) for field in fields):
        raise ValueError("Gate-2 checkpoint identity/settings/implementation mismatch")
    for pair in prior.get("pairs", []):
        raw = pair.get("raw")
        seed = pair.get("seed")
        if not isinstance(raw, dict) or not isinstance(seed, dict):
            raise ValueError("Gate-2 checkpoint contains malformed pair")
        expected_hash = hashlib.sha256(json.dumps({"raw": raw, "seed": seed}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        if pair.get("pair_hash") != expected_hash:
            raise ValueError("Gate-2 checkpoint pair hash mismatch")


def run_ollama_research_suite(task_path: str | Path, model: str, *, checkpoint_path: str | Path | None = None, resume: bool = True, progress_path: str | Path | None = None, num_ctx: int = 4096) -> dict:
    task_file = Path(task_path)
    task_file_sha256 = hashlib.sha256(task_file.read_bytes()).hexdigest()
    suite_id, tasks = load_research_tasks(task_file)
    provider_id = f"ollama:{model}"
    json_purposes = (
        "gate2_raw_action", "gate2_raw_final", "gate2_seed_attribute_outcomes", "gate2_seed_design", "gate2_seed_final",
        "gate2_independent", "gate2_adversarial", "gate2_repair",
    )
    caps = {
        "gate2_raw_action": 640, "gate2_seed_attribute_outcomes": 640, "gate2_seed_design": 384,
        "gate2_raw_final": 512, "gate2_seed_final": 512,
        "gate2_independent": 384, "gate2_adversarial": 384, "gate2_repair": 256,
    }
    probe = OllamaProvider(
        model, temperature=0.0, num_ctx=num_ctx, num_predict=640, think=False,
        json_purposes=json_purposes, purpose_num_predict=caps,
    )
    manifest = probe.model_manifest()
    implementation = implementation_manifest()
    settings = {
        "temperature": 0.0,
        "think": False,
        "num_ctx": num_ctx,
        "purpose_num_predict": caps,
        "raw_protocol": "interactive direct investigation without Seed verifier scaffold",
        "seed_protocol": "blind pre-reveal outcome-to-hypothesis causal attribution -> runner-fixed 3:1 canonical likelihoods -> information-gain experiment selection -> controlled reveal -> Bayesian posterior update + Bayes-factor rejection -> runner-derived final -> independent/adversarial verification",
        "resource_envelope": _budget().limits(),
        "task_file_sha256": task_file_sha256,
    }
    factory = lambda: OllamaProvider(
        model, temperature=0.0, num_ctx=num_ctx, num_predict=640, think=False,
        json_purposes=json_purposes, purpose_num_predict=caps,
    )

    checkpoint = Path(checkpoint_path) if checkpoint_path else None
    if progress_path:
        progress_file = Path(progress_path)
    elif checkpoint:
        progress_file = checkpoint.with_suffix(checkpoint.suffix + ".progress.jsonl")
    else:
        progress_file = None
    pairs: list[dict] = []
    if checkpoint and resume and checkpoint.exists():
        prior = json.loads(checkpoint.read_text(encoding="utf-8"))
        expected = _body(suite_id, provider_id, model, manifest, implementation, settings, list(prior.get("pairs", [])))
        validate_checkpoint_identity(prior, expected)
        pairs = list(prior.get("pairs", []))
        done = [p.get("raw", {}).get("task_id") for p in pairs]
        if len(done) != len(set(done)):
            raise ValueError("Gate-2 checkpoint contains duplicate tasks")

    completed = {str(p.get("raw", {}).get("task_id")) for p in pairs}
    task_ids = {x.task_id for x in tasks}
    if not completed.issubset(task_ids):
        raise ValueError("Gate-2 checkpoint contains unknown task")

    def emit(event: dict) -> None:
        if progress_file:
            _append_jsonl(progress_file, event)

    for task in tasks:
        if task.task_id in completed:
            continue
        emit({"event": "pair_started", "task_id": task.task_id})
        pair = run_research_pair(task, factory, provider_id=provider_id, progress=emit)
        pairs.append({"raw": asdict(pair.raw), "seed": asdict(pair.seed), "pair_hash": pair.content_hash})
        body = _body(suite_id, provider_id, model, manifest, implementation, settings, pairs)
        if checkpoint:
            _atomic_write(checkpoint, body)
        emit({"event": "pair_completed", "task_id": task.task_id, "pair_hash": pair.content_hash})

    return _body(suite_id, provider_id, model, manifest, implementation, settings, pairs)
