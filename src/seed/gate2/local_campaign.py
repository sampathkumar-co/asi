from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import time
from typing import Callable

from seed.core.budget import Budget, BudgetExceeded
from seed.providers.base import Message, ModelProvider
from seed.providers.budgeted import BudgetedProvider, ModelCallRecord
from seed.providers.ollama import OllamaProvider
from .attestation import implementation_manifest
from .schema import ResearchTask, load_research_tasks


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
    hypothesis_probabilities: tuple[tuple[str, tuple[tuple[str, int], ...]], ...] = ()


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
            raise
        repair = {"stage": purpose, "validation_error": str(exc)[:240], "invalid_output": response.text[:3000]}
        budget.charge_step()
        response = provider.complete([Message("system", "Return only one corrected JSON object. Fix syntax only; preserve all substantive choices and add no evidence."), Message("user", json.dumps(repair))], purpose="gate2_repair")
        data = json.loads(response.text)
    if not isinstance(data, dict):
        raise ValueError("model output must be a JSON object")
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
    public = task.public_dict()
    public["history"] = [asdict(x) for x in history]
    public["revisions"] = [asdict(x) for x in (revisions or [])]
    public["schema"] = {
        "hypothesis_id": "one hypothesis id",
        "experiment_id": "one unused experiment id, or null after at least one experiment",
        "prediction_outcome_id": "one declared outcome id expected if hypothesis_id is true; commit before reveal; or null when stopping",
        "control_ids": "list of control ids",
        "rejected_hypothesis_ids": "list of hypothesis ids contradicted by already revealed history only",
        "risk_ids": "list of risk/confound ids currently relevant",
        "reason": "concise rationale",
    }
    if arm == "seed":
        public["schema"].pop("prediction_outcome_id", None)
        system = (
            "Act as a falsifiable scientific investigator. Return JSON only. Choose the hypothesis currently best supported and the unused experiment that most discriminates plausible hypotheses. "
            "Choose relevant controls; reject only hypotheses contradicted by already revealed observations; track material risks/confounds. "
            "Do NOT forecast experiment outcomes in this call: separate blind pre-reveal forecast stages will do that. Do not invent ids or claim unrevealed evidence."
        )
        purpose = "gate2_seed_action"
    else:
        system = (
            "Investigate the problem directly and return JSON only using the supplied schema. Choose your best current hypothesis "
            "and next experiment from the available ids. prediction_outcome_id must be the outcome you expect if hypothesis_id is true, before reveal. Do not use Seed's scientific-method scaffold or verifier protocol."
        )
        purpose = "gate2_raw_action"
    return _json_call(provider, budget, [Message("system", system), Message("user", json.dumps(public))], purpose)


def _validated_action_choice(task: ResearchTask, data: dict, history: list[ResearchStep]) -> dict | None:
    hypothesis_id = str(data.get("hypothesis_id", ""))
    if hypothesis_id not in _ids(task.hypotheses): raise ValueError("invalid hypothesis id")
    experiment_id = data.get("experiment_id")
    if experiment_id is None:
        if not history: raise ValueError("at least one experiment is required")
        return None
    if not isinstance(experiment_id, str) or experiment_id not in _ids(task.experiments): raise ValueError("invalid experiment id")
    if experiment_id in {x.experiment_id for x in history}: raise ValueError("experiment cannot be repeated")
    controls, rejected, risks = _strings(data.get("control_ids", [])), _strings(data.get("rejected_hypothesis_ids", [])), _strings(data.get("risk_ids", []))
    if not set(controls).issubset(_ids(task.controls)): raise ValueError("invalid control id")
    if not set(rejected).issubset(_ids(task.hypotheses)): raise ValueError("invalid rejected hypothesis id")
    if not set(risks).issubset(_ids(task.risks)): raise ValueError("invalid risk id")
    return {"hypothesis_id": hypothesis_id, "experiment_id": experiment_id, "control_ids": controls, "rejected_hypothesis_ids": rejected, "risk_ids": risks}


def _forecast_one(provider: BudgetedProvider, budget: Budget, task: ResearchTask, experiment_id: str, hypothesis_id: str) -> dict:
    experiment = task.experiment(experiment_id)
    hypothesis = next(x for x in task.hypotheses if x.id == hypothesis_id)
    payload = {"question": task.question, "hypothesis": asdict(hypothesis), "experiment": {"id": experiment.id, "description": experiment.description, "possible_outcomes": [asdict(x) for x in experiment.possible_outcomes]}, "schema": {"outcome_probabilities": "map every declared outcome id to an integer probability 0..100 summing exactly 100", "reason": "brief causal rationale"}}
    system = ("No experiment result is available. You are given ONE hypothesis and one experiment with declared outcomes. "
              "Assume the hypothesis is the sole true explanation and assign a predictive probability distribution across ALL declared outcomes. "
              "Probabilities must be integer percentages summing exactly 100. Use the outcome text literally and reserve substantial probability for instability/noise outcomes when the hypothesis itself is stochastic or unstable. Return JSON only.")
    return _json_call(provider, budget, [Message("system", system), Message("user", json.dumps(payload))], "gate2_seed_forecast_hypothesis")


def _validated_forecast_one(task: ResearchTask, experiment_id: str, hypothesis_id: str, data: dict) -> tuple[str, str, tuple[tuple[str, int], ...]]:
    if hypothesis_id not in _ids(task.hypotheses): raise ValueError("invalid forecast hypothesis id")
    experiment = task.experiment(experiment_id)
    outcome_ids = [x.id for x in experiment.possible_outcomes]
    raw = data.get("outcome_probabilities")
    if not isinstance(raw, dict) or not set(raw).issubset(set(outcome_ids)):
        raise ValueError("forecast probabilities may contain only declared outcome ids")
    supplied: dict[str, int] = {}
    for oid, value in raw.items():
        if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 100:
            raise ValueError("forecast probabilities must be integer percentages 0..100")
        supplied[oid] = value
    if sum(supplied.values()) != 100:
        raise ValueError("forecast probabilities must sum exactly to 100 before zero-fill")
    probs = {oid: supplied.get(oid, 0) for oid in outcome_ids}
    categorical = max(outcome_ids, key=lambda oid: probs[oid])
    return hypothesis_id, categorical, tuple((oid, probs[oid]) for oid in outcome_ids)


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
    hypothesis_probabilities: tuple[tuple[str, tuple[tuple[str, int], ...]], ...] = ()
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


def _revision(provider: BudgetedProvider, budget: Budget, task: ResearchTask, history: list[ResearchStep], revisions: list[ResearchRevision]) -> dict:
    if not history:
        raise ValueError("revision requires revealed evidence")
    payload = {
        "task": task.public_dict(),
        "history": [asdict(x) for x in history],
        "prior_revisions": [asdict(x) for x in revisions],
        "latest_experiment_id": history[-1].experiment_id,
        "latest_precommitted_hypothesis_predictions": dict(history[-1].hypothesis_predictions),
        "latest_precommitted_hypothesis_probabilities": {hid: dict(probs) for hid, probs in history[-1].hypothesis_probabilities},
        "latest_observed_outcome_probabilities": {hid: dict(probs)[history[-1].observed_outcome_id] for hid, probs in history[-1].hypothesis_probabilities},
        "cumulative_likelihood_products": _mechanical_support(task, history)[0],
        "schema": {
            "hypothesis_id": "best-supported hypothesis after the newly revealed evidence",
            "rejected_hypothesis_ids": "hypothesis ids contradicted by revealed evidence",
            "risk_ids": "material risk/confound ids after reviewing the evidence",
            "confidence": "number 0..1",
            "reason": "concise evidence-based revision rationale",
        },
    }
    system = (
        "A selected experiment result has now been revealed. Return JSON only. The probability distributions were frozen before reveal. "
        "A hypothesis receives stronger evidence when it assigned higher probability to the actually observed outcome; cumulative_likelihood_products multiplies those frozen observed-outcome probabilities across experiments. "
        "Use that direction of evidence, combine it with the revealed record, explicitly reject contradicted hypotheses, update material risks/confounds, and select the hypothesis now best supported. "
        "Do not choose another experiment in this call. Do not invent ids or use evidence that has not been revealed."
    )
    return _json_call(provider, budget, [Message("system", system), Message("user", json.dumps(payload))], "gate2_seed_revision")


def _validated_revision(task: ResearchTask, history: list[ResearchStep], data: dict) -> ResearchRevision:
    if not history:
        raise ValueError("revision requires revealed evidence")
    hypothesis_id = str(data.get("hypothesis_id", ""))
    if hypothesis_id not in _ids(task.hypotheses):
        raise ValueError("invalid revised hypothesis id")
    rejected = _strings(data.get("rejected_hypothesis_ids", []))
    risks = _strings(data.get("risk_ids", []))
    if not set(rejected).issubset(_ids(task.hypotheses)):
        raise ValueError("invalid revised rejected-hypothesis id")
    if hypothesis_id in rejected:
        raise ValueError("revised hypothesis cannot also be rejected")
    if not set(risks).issubset(_ids(task.risks)):
        raise ValueError("invalid revised risk id")
    confidence = float(data.get("confidence", 0.0))
    if not 0.0 <= confidence <= 1.0:
        raise ValueError("revision confidence out of range")
    return ResearchRevision(
        after_experiment_id=history[-1].experiment_id,
        hypothesis_id=hypothesis_id,
        rejected_hypothesis_ids=rejected,
        risk_ids=risks,
        confidence=confidence,
        reason=str(data.get("reason", ""))[:320],
    )


def _final_report(provider: BudgetedProvider, budget: Budget, task: ResearchTask, history: list[ResearchStep], arm: str, revisions: list[ResearchRevision] | None = None) -> dict:
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
        system = "Conclude from the observed evidence only. Return JSON only. Revise if evidence falsified the initial hypothesis; separate evidence from assumptions and list material risks."
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


def _mechanical_support(task: ResearchTask, history: list[ResearchStep]) -> tuple[dict[str, int], tuple[str, ...]]:
    hypothesis_ids = tuple(x.id for x in task.hypotheses)
    products = {hid: 1 for hid in hypothesis_ids}
    if not history:
        raise ValueError("verifier requires revealed history")
    for step in history:
        distributions = {hid: dict(probs) for hid, probs in step.hypothesis_probabilities}
        if set(distributions) != set(hypothesis_ids):
            raise ValueError("verifier requires complete frozen hypothesis probability forecasts")
        for hid in hypothesis_ids:
            if step.observed_outcome_id not in distributions[hid]:
                raise ValueError("observed outcome missing from frozen probability forecast")
            products[hid] *= int(distributions[hid][step.observed_outcome_id])
    best_score = max(products.values())
    best = tuple(hid for hid in hypothesis_ids if products[hid] == best_score)
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
        _, mechanical_best = _mechanical_support(task, history)
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
        return validate(repaired)


def _arm_evidence(task: ResearchTask, arm: str, meter: BudgetedProvider, budget: Budget, history: list[ResearchStep], final: tuple | None, status: str, independent=None, adversarial=None, revisions: list[ResearchRevision] | None = None, repair_events: list[dict[str, str]] | None = None) -> ResearchArmEvidence:
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
    )


def _run_arm(task: ResearchTask, provider: BudgetedProvider, budget: Budget, arm: str) -> ResearchArmEvidence:
    history: list[ResearchStep] = []
    revisions: list[ResearchRevision] = []
    repair_events: list[dict[str, str]] = []
    final = None
    independent = adversarial = None
    try:
        def validate_or_repair(stage: str, data: dict, validator):
            try:
                return validator(data)
            except ValueError as exc:
                repair_events.append({"stage": stage, "error": str(exc)[:240], "invalid_output_sha256": hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()})
                repaired = _repair_schema(provider, budget, task, arm=arm, stage=stage, invalid_output=data, error=exc, history=history, revisions=revisions)
                return validator(repaired)
        for _ in range(task.max_experiments):
            action = _action(provider, budget, task, history, arm, revisions)
            if arm == "seed":
                choice = validate_or_repair("action", action, lambda value: _validated_action_choice(task, value, history))
                if choice is None: break
                categorical: dict[str, str] = {}
                distributions: dict[str, tuple[tuple[str, int], ...]] = {}
                for hypothesis in task.hypotheses:
                    forecast_data = _forecast_one(provider, budget, task, choice["experiment_id"], hypothesis.id)
                    hid, outcome_id, probabilities = validate_or_repair("forecast_hypothesis", forecast_data, lambda value, hid=hypothesis.id: _validated_forecast_one(task, choice["experiment_id"], hid, value))
                    categorical[hid] = outcome_id
                    distributions[hid] = probabilities
                forecasts = tuple((h.id, categorical[h.id]) for h in task.hypotheses)
                probability_rows = tuple((h.id, distributions[h.id]) for h in task.hypotheses)
                experiment = task.experiment(choice["experiment_id"])
                prediction = categorical[choice["hypothesis_id"]]
                step = ResearchStep(
                    choice["hypothesis_id"], experiment.id, prediction, choice["control_ids"],
                    choice["rejected_hypothesis_ids"], choice["risk_ids"], experiment.observed_outcome_id,
                    experiment.observation, forecasts, probability_rows,
                )
            else:
                step = validate_or_repair("action", action, lambda value: _validated_step(task, value, history))
                if step is None: break
            history.append(step)
            if arm == "seed":
                revision_data = _revision(provider, budget, task, history, revisions)
                revisions.append(validate_or_repair("revision", revision_data, lambda value: _validated_revision(task, history, value)))
        final_data = _final_report(provider, budget, task, history, arm, revisions)
        final = validate_or_repair("final", final_data, lambda value: _validated_final(task, value))
        if arm == "seed":
            independent = _verify(provider, budget, task, history, final_data, "independent", revisions)
            adversarial = _verify(provider, budget, task, history, final_data, "adversarial", revisions)
        status = "succeeded"
    except BudgetExceeded:
        status = "budget_exhausted"
    except Exception as exc:
        status = f"failed:{type(exc).__name__}"
    return _arm_evidence(task, arm, provider, budget, history, final, status, independent, adversarial, revisions, repair_events)


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
        "gate2_raw_action", "gate2_raw_final", "gate2_seed_action", "gate2_seed_forecast_hypothesis", "gate2_seed_revision", "gate2_seed_final",
        "gate2_independent", "gate2_adversarial", "gate2_repair",
    )
    caps = {
        "gate2_raw_action": 640, "gate2_seed_action": 640, "gate2_seed_forecast_hypothesis": 192, "gate2_seed_revision": 384,
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
        "seed_protocol": "falsifiable action -> isolated blind per-hypothesis probability forecasts -> reveal -> cumulative frozen-likelihood comparison -> revision -> trusted likelihood support gate + independent/adversarial verification",
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
