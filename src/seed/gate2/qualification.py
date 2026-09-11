from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import hashlib
import json
from pathlib import Path

from seed.core.budget import Budget, BudgetExceeded
from seed.providers.base import Message, ModelResponse
from seed.providers.budgeted import BudgetedProvider
from seed.providers.scripted import ScriptedProvider
from .local_campaign import (
    ResearchArmEvidence,
    ResearchPairEvidence,
    _action,
    _body,
    _forecast_one,
    _resolve_forecast_collision,
    _run_arm,
    _validated_action_choice,
    _validated_forecast_one,
    _validated_collision,
    _validated_step,
    validate_checkpoint_identity,
)
from .schema import CatalogItem, ResearchExperiment, ResearchTask


@dataclass(frozen=True)
class Gate2Certificate:
    qualification: str
    gate: int
    passed: bool
    checks: dict[str, bool]
    evidence: dict[str, object]
    content_hash: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class CaptureProvider:
    def __init__(self, responses: list[str]) -> None:
        self.responses = list(responses)
        self.calls: list[tuple[str, list[Message]]] = []

    def complete(self, messages: list[Message], *, purpose: str) -> ModelResponse:
        self.calls.append((purpose, messages))
        if not self.responses:
            raise RuntimeError("no scripted response left")
        text = self.responses.pop(0)
        return ModelResponse(
            text=text,
            input_tokens=sum(len(message.content.split()) for message in messages),
            output_tokens=len(text.split()),
        )


def _task() -> ResearchTask:
    return ResearchTask(
        task_id="Q1",
        question="Which hypothesis explains the effect?",
        hypotheses=(CatalogItem("H1", "baseline cause"), CatalogItem("H2", "alternative cause")),
        experiments=(ResearchExperiment(
            "E1",
            "run the discriminating experiment",
            (CatalogItem("O1", "supports H1"), CatalogItem("O2", "supports H2")),
            "O2",
            "SECRET_OBSERVATION_SUPPORTS_H2",
        ),),
        controls=(CatalogItem("C1", "matched control"),),
        risks=(CatalogItem("R1", "selection confound"),),
        max_experiments=1,
    )


def _valid_action() -> dict[str, object]:
    return {
        "hypothesis_id": "H1",
        "experiment_id": "E1",
        "prediction_outcome_id": "O1",
        "hypothesis_predictions": {"H1": "O1", "H2": "O2"},
        "control_ids": ["C1"],
        "rejected_hypothesis_ids": [],
        "risk_ids": ["R1"],
        "reason": "precommit",
    }


def _raises_value_error(fn) -> bool:
    try:
        fn()
    except ValueError:
        return True
    return False


def _arm(arm: str, *, provider: str = "ollama:qwen", limits: dict | None = None) -> ResearchArmEvidence:
    envelope = limits or {
        "max_steps": 16,
        "max_model_calls": 16,
        "max_tool_calls": 0,
        "max_tokens": 12000,
        "max_cost_usd": 0.0,
    }
    return ResearchArmEvidence(
        task_id="Q1", arm=arm, provider_id=provider, model_id="qwen", history=(),
        final_hypothesis_id=None, rejected_hypothesis_ids=(), risk_ids=(), confidence=0.0,
        independent=None, adversarial=None, accepted=None, status="succeeded",
        limits=envelope, usage={"steps": 0, "model_calls": 0, "tool_calls": 0, "tokens": 0, "cost_usd": 0.0},
        transcript_hash="0" * 64,
    )


def run_gate2_qualification() -> Gate2Certificate:
    task = _task()
    task.validate()
    forecast_responses = {"H1": {"outcome_id": "O1", "reason": "supports H1"}, "H2": {"outcome_id": "O2", "reason": "supports H2"}}
    capture = CaptureProvider([json.dumps(_valid_action())] + [json.dumps(forecast_responses[h.id]) for h in task.hypotheses])
    budget = Budget(max_steps=16, max_model_calls=16, max_tool_calls=0, max_tokens=12000, max_cost_usd=0)
    meter = BudgetedProvider(capture, budget, provider_id="ollama:qwen")
    action = _action(meter, budget, task, [], "seed")
    choice = _validated_action_choice(task, action, [])
    forecasts = []
    for hypothesis in task.hypotheses:
        data = _forecast_one(meter, budget, task, choice["experiment_id"], hypothesis.id)
        forecasts.append(_validated_forecast_one(task, choice["experiment_id"], hypothesis.id, data))
    forecasts = tuple(forecasts)
    prompt_text = "\n".join(message.content for _, messages in capture.calls for message in messages)
    hidden_absent = "SECRET_OBSERVATION_SUPPORTS_H2" not in prompt_text and "observed_outcome_id" not in prompt_text
    purposes0 = [purpose for purpose, _ in capture.calls]
    audit_separate_pre_reveal = purposes0 == ["gate2_seed_action", "gate2_seed_forecast_hypothesis", "gate2_seed_forecast_hypothesis"] and hidden_absent
    collision_capture = CaptureProvider([json.dumps({"hypothesis_predictions": {"H1": "O1", "H2": "O2"}, "distinguishable": True, "reason": "separates"})])
    collision_budget = Budget(max_steps=16, max_model_calls=16, max_tool_calls=0, max_tokens=12000, max_cost_usd=0)
    collision_meter = BudgetedProvider(collision_capture, collision_budget, provider_id="ollama:qwen")
    collision_data = _resolve_forecast_collision(collision_meter, collision_budget, task, "E1", ("H1", "H2"), "O1")
    collision_map = _validated_collision(task, "E1", ("H1", "H2"), collision_data)
    collision_prompt = "\n".join(m.content for _, msgs in collision_capture.calls for m in msgs)
    collision_hidden_safe = collision_map == {"H1": "O1", "H2": "O2"} and "SECRET_OBSERVATION_SUPPORTS_H2" not in collision_prompt and "observed_outcome_id" not in collision_prompt
    all_forecasts_precommitted = dict(forecasts) == {"H1": "O1", "H2": "O2"}
    precommit_before_reveal = bool(hidden_absent and dict(forecasts)[choice["hypothesis_id"]] == "O1" and task.experiment("E1").observed_outcome_id == "O2")
    step = _validated_step(task, _valid_action(), [], require_hypothesis_predictions=True)

    invalid_id_checks: dict[str, bool] = {}
    for field, invalid in (
        ("hypothesis_id", "HX"),
        ("experiment_id", "EX"),
        ("control_ids", ["CX"]),
        ("risk_ids", ["RX"]),
    ):
        bad = dict(_valid_action())
        bad[field] = invalid
        invalid_id_checks[field] = _raises_value_error(lambda bad=bad: _validated_action_choice(task, bad, []))

    repeated = _raises_value_error(lambda: _validated_action_choice(task, _valid_action(), [step])) if step else False
    invalid_forecast_rejected = _raises_value_error(
        lambda: _validated_forecast_one(task, "E1", "H1", {"outcome_id": "OX"})
    )

    valid_pair = ResearchPairEvidence(_arm("raw"), _arm("seed"))
    pair_validates = True
    try:
        valid_pair.validate()
    except ValueError:
        pair_validates = False
    model_mismatch_rejected = _raises_value_error(
        lambda: ResearchPairEvidence(_arm("raw"), _arm("seed", provider="ollama:other")).validate()
    )
    changed_limits = dict(_arm("seed").limits)
    changed_limits["max_steps"] = 7
    envelope_mismatch_rejected = _raises_value_error(
        lambda: ResearchPairEvidence(_arm("raw"), _arm("seed", limits=changed_limits)).validate()
    )

    prior = _body("suite", "ollama:qwen", "qwen", {"digest": "m"}, {"digest": "a"}, {"x": 1}, [])
    resume_identity_accepts_exact = True
    try:
        validate_checkpoint_identity(prior, dict(prior))
    except ValueError:
        resume_identity_accepts_exact = False
    changed = _body("suite", "ollama:qwen", "qwen", {"digest": "m"}, {"digest": "b"}, {"x": 1}, [])
    implementation_change_invalidates_resume = _raises_value_error(
        lambda: validate_checkpoint_identity(prior, changed)
    )
    tampered = dict(prior)
    tampered["suite_id"] = "tampered"
    checkpoint_hash_tamper_rejected = _raises_value_error(
        lambda: validate_checkpoint_identity(tampered, changed)
    )

    malformed_budget = Budget(max_steps=16, max_model_calls=16, max_tool_calls=0, max_tokens=12000, max_cost_usd=0)
    malformed_meter = BudgetedProvider(
        ScriptedProvider(["not-json"]), malformed_budget, provider_id="ollama:qwen"
    )
    malformed_arm = _run_arm(task, malformed_meter, malformed_budget, "raw")
    malformed_fails_closed = (
        malformed_arm.status.startswith("failed:") and malformed_arm.final_hypothesis_id is None
    )

    bad_action = dict(_valid_action())
    bad_action["hypothesis_id"] = "HX"
    repair_capture = CaptureProvider([
        json.dumps(bad_action), json.dumps(_valid_action()),
        json.dumps({"final_hypothesis_id": "H2", "rejected_hypothesis_ids": ["H1"], "risk_ids": ["R1"], "confidence": 0.9, "reason": "repaired"}),
    ])
    repair_budget = Budget(max_steps=16, max_model_calls=16, max_tool_calls=0, max_tokens=12000, max_cost_usd=0)
    repair_meter = BudgetedProvider(repair_capture, repair_budget, provider_id="ollama:qwen")
    repaired_arm = _run_arm(task, repair_meter, repair_budget, "raw")
    repair_purposes = [purpose for purpose, _ in repair_capture.calls]
    repair_prompt = "\n".join(m.content for purpose, messages in repair_capture.calls if purpose == "gate2_repair" for m in messages)
    schema_repair_hidden_safe = repaired_arm.status == "succeeded" and repair_purposes == ["gate2_raw_action", "gate2_repair", "gate2_raw_final"] and "SECRET_OBSERVATION_SUPPORTS_H2" not in repair_prompt

    audit_budget = Budget(max_model_calls=2, max_tokens=1, max_cost_usd=1)
    audit_meter = BudgetedProvider(ScriptedProvider(["two words"]), audit_budget, provider_id="ollama:qwen")
    audit_before = audit_meter.transcript_hash
    try:
        audit_meter.complete([Message("user", "x")], purpose="audit")
    except BudgetExceeded:
        pass
    overbudget_response_audited = len(audit_meter.records) == 1 and audit_meter.records[0].budget_accepted is False and audit_meter.transcript_hash != audit_before and audit_budget.model_calls == 0

    verifier_responses = [
        json.dumps(_valid_action()),
        json.dumps(forecast_responses["H1"]),
        json.dumps(forecast_responses["H2"]),
        json.dumps({
            "hypothesis_id": "H2",
            "rejected_hypothesis_ids": ["H1"],
            "risk_ids": ["R1"],
            "confidence": 0.9,
            "reason": "O2 contradicts H1 and supports H2",
        }),
        json.dumps({
            "final_hypothesis_id": "H2",
            "rejected_hypothesis_ids": ["H1"],
            "risk_ids": ["R1"],
            "confidence": 0.9,
            "reason": "observed O2",
        }),
        json.dumps({"has_material_defect": False, "defect_summary": "none", "confidence": 0.95, "risk_ids": ["R1"], "reason": "supported"}),
        json.dumps({"has_material_defect": True, "defect_summary": "unresolved confound", "confidence": 0.95, "risk_ids": ["R1"], "reason": "unresolved confound"}),
    ]
    verifier_capture = CaptureProvider(verifier_responses)
    verifier_budget = Budget(max_steps=16, max_model_calls=16, max_tool_calls=0, max_tokens=12000, max_cost_usd=0)
    verifier_meter = BudgetedProvider(
        verifier_capture, verifier_budget, provider_id="ollama:qwen"
    )
    seed_arm = _run_arm(task, verifier_meter, verifier_budget, "seed")
    purposes = [purpose for purpose, _ in verifier_capture.calls]
    revision_calls = [messages for purpose, messages in verifier_capture.calls if purpose == "gate2_seed_revision"]
    revision_after_reveal = (
        len(revision_calls) == 1
        and "SECRET_OBSERVATION_SUPPORTS_H2" in "\n".join(m.content for m in revision_calls[0])
        and len(seed_arm.revisions) == 1
        and seed_arm.revisions[0].hypothesis_id == "H2"
        and "H1" in seed_arm.revisions[0].rejected_hypothesis_ids
    )
    forecast_match_table_mechanical = (
        len(revision_calls) == 1
        and '"hypothesis_id": "H1", "predicted_outcome_id": "O1", "matches_observation": false' in "\n".join(m.content for m in revision_calls[0])
        and '"hypothesis_id": "H2", "predicted_outcome_id": "O2", "matches_observation": true' in "\n".join(m.content for m in revision_calls[0])
    )
    revision_call_order = purposes == [
        "gate2_seed_action", "gate2_seed_forecast_hypothesis", "gate2_seed_forecast_hypothesis", "gate2_seed_revision", "gate2_seed_final",
        "gate2_independent", "gate2_adversarial",
    ]
    verifier_roles_distinct = (
        purposes.count("gate2_independent") == 1
        and purposes.count("gate2_adversarial") == 1
        and seed_arm.independent is not None
        and seed_arm.adversarial is not None
        and seed_arm.independent.verifier != seed_arm.adversarial.verifier
    )
    disagreement_blocks_acceptance = seed_arm.accepted is False
    verifier_verdict_runner_derived = (
        seed_arm.independent is not None and seed_arm.adversarial is not None
        and seed_arm.independent.verdict == "pass" and seed_arm.adversarial.verdict == "fail"
        and all('"verdict"' not in text for text in verifier_responses[-2:])
    )

    tiny_budget = Budget(max_steps=0, max_model_calls=16, max_tool_calls=0, max_tokens=12000, max_cost_usd=0)
    tiny_meter = BudgetedProvider(
        ScriptedProvider([json.dumps(_valid_action())]), tiny_budget, provider_id="ollama:qwen"
    )
    exhausted_arm = _run_arm(task, tiny_meter, tiny_budget, "raw")
    budget_exhaustion_terminal = exhausted_arm.status == "budget_exhausted"

    public = task.public_dict()
    private_key_external = (
        "final_hypothesis_id" not in public
        and "observed_outcome_id" not in json.dumps(public)
        and "SECRET_OBSERVATION_SUPPORTS_H2" not in json.dumps(public)
    )

    checks = {
        "hidden_outcomes_absent_before_selection": hidden_absent,
        "forecast_audit_is_separate_and_pre_reveal": audit_separate_pre_reveal,
        "forecast_collision_resolution_is_hidden_safe": collision_hidden_safe,
        "prediction_precommitted_before_reveal": precommit_before_reveal,
        "all_hypothesis_forecasts_precommitted_before_reveal": all_forecasts_precommitted,
        "invalid_isolated_forecast_rejected": invalid_forecast_rejected,
        "invalid_hypothesis_id_rejected": invalid_id_checks["hypothesis_id"],
        "invalid_experiment_id_rejected": invalid_id_checks["experiment_id"],
        "invalid_control_id_rejected": invalid_id_checks["control_ids"],
        "invalid_risk_id_rejected": invalid_id_checks["risk_ids"],
        "repeated_experiment_rejected": repeated,
        "same_identity_pair_validates": pair_validates,
        "model_identity_mismatch_rejected": model_mismatch_rejected,
        "resource_envelope_mismatch_rejected": envelope_mismatch_rejected,
        "exact_resume_identity_accepts": resume_identity_accepts_exact,
        "implementation_change_invalidates_resume": implementation_change_invalidates_resume,
        "checkpoint_hash_tamper_rejected": checkpoint_hash_tamper_rejected,
        "malformed_model_json_fails_closed": malformed_fails_closed,
        "schema_repair_is_explicit_and_hidden_safe": schema_repair_hidden_safe,
        "overbudget_response_is_transcript_audited": overbudget_response_audited,
        "post_reveal_revision_receives_revealed_evidence": revision_after_reveal,
        "post_reveal_forecast_match_table_is_mechanical": forecast_match_table_mechanical,
        "post_reveal_revision_call_order_is_explicit": revision_call_order,
        "verifier_roles_are_distinct_calls": verifier_roles_distinct,
        "verifier_disagreement_blocks_acceptance": disagreement_blocks_acceptance,
        "verifier_verdict_is_runner_derived": verifier_verdict_runner_derived,
        "budget_exhaustion_is_terminal": budget_exhaustion_terminal,
        "private_answer_key_external_to_candidate_prompt": private_key_external,
    }
    evidence = {
        "check_count": len(checks),
        "seed_verifier_call_purposes": purposes,
        "seed_disagreement_status": seed_arm.status,
        "seed_disagreement_accepted": seed_arm.accepted,
        "seed_revision_count": len(seed_arm.revisions),
        "forecast_audit_call_purposes": [purpose for purpose, _ in capture.calls],
        "repair_canary_call_purposes": repair_purposes,
        "overbudget_record_budget_accepted": audit_meter.records[0].budget_accepted if audit_meter.records else None,
        "qualification_note": "Deterministic Gate-2 protocol canaries; not empirical Gate-2 certification.",
    }
    body = {
        "qualification": "gate2-research-protocol-v1",
        "gate": 2,
        "passed": all(checks.values()),
        "checks": checks,
        "evidence": evidence,
    }
    content_hash = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return Gate2Certificate(**body, content_hash=content_hash)


def write_gate2_certificate(certificate: Gate2Certificate, path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(certificate.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
