from dataclasses import asdict, dataclass
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path

from seed.core.budget import Budget, BudgetExceeded
from seed.providers.base import Message, ModelResponse
from seed.providers.budgeted import BudgetedProvider
from seed.providers.ollama import OllamaProvider
from seed.providers.scripted import ScriptedProvider
from .local_campaign import (
    ModelProtocolError, ResearchArmEvidence, ResearchPairEvidence, _body, _budget,
    _GATE2_OLLAMA_JSON_PURPOSES, _GATE2_OLLAMA_PURPOSE_NUM_PREDICT,
    _SCHEMA_REPAIR_CALL_LIMIT_PER_ARM, _SchemaRepairState,
    _attribute_outcomes, _canonical_matrices, _information_gain, _mechanical_rejections,
    _posterior_best, _run_arm, _select_experiment, _update_posterior,
    _validate_with_schema_repairs, _validated_attribution, _verifier_verdict,
    validate_checkpoint_identity,
)
from .schema import CatalogItem, ResearchExperiment, ResearchTask
from .scoring import _execution_incidents


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
        task_id="Q3",
        question="Which mechanism explains the effect?",
        hypotheses=(CatalogItem("H1", "baseline mechanism"), CatalogItem("H2", "alternative mechanism")),
        experiments=(
            ResearchExperiment("E1", "weak discriminator", (CatalogItem("O1A", "leans H1"), CatalogItem("O1B", "leans H2")), "O1B", "SECRET_E1_SUPPORTS_H2"),
            ResearchExperiment("E2", "strong discriminator", (CatalogItem("O2A", "supports H1"), CatalogItem("O2B", "supports H2")), "O2B", "SECRET_E2_SUPPORTS_H2"),
        ),
        controls=(CatalogItem("C1", "matched control"),),
        risks=(CatalogItem("R1", "residual confound"),),
        max_experiments=2,
    )


def _attribution_response() -> dict[str, object]:
    return {
        "outcome_support": {
            "E1": {"O1A": ["H1", "H2"], "O1B": ["H1", "H2"]},
            "E2": {"O2A": ["H1"], "O2B": ["H2"]},
        },
        "notes": {"E1": "weak non-discriminator", "E2": "strong discriminator"},
    }


def _raises_value_error(fn) -> bool:
    try:
        fn()
    except ValueError:
        return True
    return False


def _arm(arm: str, *, provider: str = "ollama:qwen", limits: dict | None = None) -> ResearchArmEvidence:
    envelope = limits or _budget().limits()
    return ResearchArmEvidence(
        task_id="Q3", arm=arm, provider_id=provider, model_id="qwen", history=(),
        final_hypothesis_id=None, rejected_hypothesis_ids=(), risk_ids=(), confidence=0.0,
        independent=None, adversarial=None, accepted=None, status="succeeded",
        limits=envelope, usage={"steps": 0, "model_calls": 0, "tool_calls": 0, "tokens": 0, "cost_usd": 0.0},
        transcript_hash="0" * 64,
    )


def _seed_scripted_responses() -> list[str]:
    return [
        json.dumps(_attribution_response()),
        json.dumps({"control_ids": ["C1"], "risk_ids": ["R1"], "reason": "control the strong discriminator"}),
        json.dumps({"control_ids": ["C1"], "risk_ids": ["R1"], "reason": "confirm with remaining experiment"}),
        json.dumps({"final_hypothesis_id": "H1", "rejected_hypothesis_ids": [], "risk_ids": ["R1"], "confidence": 0.2, "reason": "attempt to override runner"}),
        json.dumps({"supported_hypothesis_ids": ["H2"], "has_direct_evidence_defect": False, "defect_summary": "none", "confidence": 0.95, "risk_ids": ["R1"], "reason": "H2 uniquely supported"}),
        json.dumps({"supported_hypothesis_ids": ["H2"], "has_direct_evidence_defect": False, "defect_summary": "none", "confidence": 0.95, "risk_ids": ["R1"], "reason": "H2 survives adversarial review"}),
    ]


def run_gate2_qualification() -> Gate2Certificate:
    task = _task()
    task.validate()

    capture = CaptureProvider([json.dumps(_attribution_response())])
    budget = _budget()
    meter = BudgetedProvider(capture, budget, provider_id="ollama:qwen")
    attribution_data = _attribute_outcomes(meter, budget, task)
    attribution = _validated_attribution(task, attribution_data)
    prompt_text = "\n".join(message.content for _, messages in capture.calls for message in messages)
    hidden_absent = "SECRET_E1_SUPPORTS_H2" not in prompt_text and "SECRET_E2_SUPPORTS_H2" not in prompt_text
    attribution_before_reveal = [purpose for purpose, _ in capture.calls] == ["gate2_seed_attribute_outcomes"] and hidden_absent

    matrices, categoricals = _canonical_matrices(task, attribution)
    prior = {"H1": 0.5, "H2": 0.5}
    ig1 = _information_gain(task, "E1", matrices, prior)
    ig2 = _information_gain(task, "E2", matrices, prior)
    selected, selected_ig = _select_experiment(task, matrices, prior, set())
    posterior1 = _update_posterior(task, selected, matrices, prior)
    second, _ = _select_experiment(task, matrices, posterior1, {selected})
    posterior2 = _update_posterior(task, second, matrices, posterior1)
    final_id, final_tie = _posterior_best(task, posterior2)
    rejected = _mechanical_rejections(task, posterior2)

    invalid_missing_experiment = _raises_value_error(lambda: _validated_attribution(task, {
        "outcome_support": {"E1": {"O1A": ["H1"], "O1B": ["H2"]}}
    }))
    invalid_missing_outcome = _raises_value_error(lambda: _validated_attribution(task, {
        "outcome_support": {"E1": {"O1A": ["H1"]}, "E2": {"O2A": ["H1"], "O2B": ["H2"]}}
    }))
    invalid_empty_support = _raises_value_error(lambda: _validated_attribution(task, {
        "outcome_support": {"E1": {"O1A": [], "O1B": ["H2"]}, "E2": {"O2A": ["H1"], "O2B": ["H2"]}}
    }))
    invalid_unknown_hypothesis = _raises_value_error(lambda: _validated_attribution(task, {
        "outcome_support": {"E1": {"O1A": ["HX"], "O1B": ["H2"]}, "E2": {"O2A": ["H1"], "O2B": ["H2"]}}
    }))
    invalid_duplicate_support = _raises_value_error(lambda: _validated_attribution(task, {
        "outcome_support": {"E1": {"O1A": ["H1", "H1"], "O1B": ["H2"]}, "E2": {"O2A": ["H1"], "O2B": ["H2"]}}
    }))
    bad_weight_rejected = _raises_value_error(lambda: _canonical_matrices(task, attribution, support_weight=1.0))
    canonical_rows_normalized = all(
        abs(sum(matrices[h.id][e.id].values()) - 1.0) < 1e-12
        for h in task.hypotheses for e in task.experiments
    )
    canonical_ratio_fixed = (
        abs(matrices["H1"]["E2"]["O2A"] - 0.75) < 1e-12
        and abs(matrices["H1"]["E2"]["O2B"] - 0.25) < 1e-12
        and abs(matrices["H2"]["E2"]["O2B"] - 0.75) < 1e-12
        and abs(matrices["H2"]["E2"]["O2A"] - 0.25) < 1e-12
    )
    weak_ambiguous_uniform = all(abs(value - 0.5) < 1e-12 for row in matrices.values() for value in row["E1"].values())
    resource_envelope_matches = _budget().limits() == {
        "max_steps": 16, "max_model_calls": 16, "max_tool_calls": 0,
        "max_tokens": 15000, "max_cost_usd": 0.0,
    }

    schema_purposes = (
        "gate2_raw_action", "gate2_raw_final", "gate2_seed_attribute_outcomes",
        "gate2_seed_design", "gate2_seed_final", "gate2_independent",
        "gate2_adversarial", "gate2_repair",
    )
    schema_probe = OllamaProvider("qwen", json_purposes=schema_purposes)
    attribution_format = schema_probe._payload([], "gate2_seed_attribute_outcomes").get("format")
    raw_action_format = schema_probe._payload([], "gate2_raw_action").get("format")
    seed_design_format = schema_probe._payload([], "gate2_seed_design").get("format")
    raw_final_format = schema_probe._payload([], "gate2_raw_final").get("format")
    seed_final_format = schema_probe._payload([], "gate2_seed_final").get("format")
    independent_format = schema_probe._payload([], "gate2_independent").get("format")
    adversarial_format = schema_probe._payload([], "gate2_adversarial").get("format")
    repair_format = schema_probe._payload([], "gate2_repair").get("format")

    attribution_schema_active = (
        isinstance(attribution_format, dict)
        and attribution_format.get("required") == ["outcome_support"]
        and attribution_format["properties"]["outcome_support"]["additionalProperties"]["additionalProperties"].get("minItems") == 1
    )
    action_schema_active = isinstance(raw_action_format, dict) and "prediction_outcome_id" in raw_action_format.get("required", [])
    design_schema_active = isinstance(seed_design_format, dict) and seed_design_format.get("required") == ["control_ids", "risk_ids", "reason"]
    final_schema_active = (
        isinstance(raw_final_format, dict) and raw_final_format == seed_final_format
        and raw_final_format["properties"]["confidence"].get("maximum") == 1
    )
    verifier_schema_active = (
        isinstance(independent_format, dict) and independent_format == adversarial_format
        and independent_format["properties"]["supported_hypothesis_ids"].get("minItems") == 1
    )
    repair_schema_is_stage_generic = repair_format == "json"
    preflight_policy = OllamaProvider.gate2_preflight_policy()
    preflight_policy_safe = (
        preflight_policy.get("purpose") == "gate2_preflight"
        and preflight_policy.get("task_independent") is True
        and preflight_policy.get("outside_scored_envelope") is True
        and isinstance(preflight_policy.get("prompt_sha256"), str)
        and len(str(preflight_policy.get("prompt_sha256"))) == 64
    )
    preflight_runtime_bounded = (
        _GATE2_OLLAMA_PURPOSE_NUM_PREDICT.get("gate2_preflight") == 8
        and "gate2_preflight" not in _GATE2_OLLAMA_JSON_PURPOSES
    )

    repair_initial = {"outcome_support": {}}
    repair_still_invalid = {"outcome_support": {"E1": {}}}
    repair_valid = _attribution_response()
    second_repair_budget = _budget()
    second_repair_meter = BudgetedProvider(
        ScriptedProvider([json.dumps(repair_still_invalid), json.dumps(repair_valid)]),
        second_repair_budget, provider_id="ollama:qwen",
    )
    second_repair_state = _SchemaRepairState()
    second_repair_events: list[dict[str, str]] = []
    try:
        recovered_attribution = _validate_with_schema_repairs(
            second_repair_meter, second_repair_budget, task, arm="seed", stage="attribution",
            data=repair_initial, validator=lambda value: _validated_attribution(task, value),
            history=[], revisions=[], repair_state=second_repair_state,
            repair_events=second_repair_events,
        )
        second_schema_repair_recovers = (
            recovered_attribution == _validated_attribution(task, repair_valid)
            and second_repair_state.used == 2
            and len(second_repair_events) == 2
            and len(second_repair_meter.records) == 2
        )
    except (ModelProtocolError, ValueError):
        second_schema_repair_recovers = False

    hard_cap_budget = _budget()
    hard_cap_meter = BudgetedProvider(
        ScriptedProvider([json.dumps(repair_initial), json.dumps(repair_initial), json.dumps(repair_valid)]),
        hard_cap_budget, provider_id="ollama:qwen",
    )
    hard_cap_state = _SchemaRepairState()
    hard_cap_events: list[dict[str, str]] = []
    try:
        _validate_with_schema_repairs(
            hard_cap_meter, hard_cap_budget, task, arm="seed", stage="attribution",
            data=repair_initial, validator=lambda value: _validated_attribution(task, value),
            history=[], revisions=[], repair_state=hard_cap_state, repair_events=hard_cap_events,
        )
        schema_repair_hard_cap = False
    except ModelProtocolError:
        schema_repair_hard_cap = (
            _SCHEMA_REPAIR_CALL_LIMIT_PER_ARM == 2
            and hard_cap_state.used == 2
            and len(hard_cap_events) == 2
            and len(hard_cap_meter.records) == 2
        )

    max_experiments = 3
    raw_normal_calls = max_experiments + 1
    seed_normal_calls = 1 + max_experiments + 1 + 2
    raw_worst_case_calls = 2 * raw_normal_calls + _SCHEMA_REPAIR_CALL_LIMIT_PER_ARM
    seed_worst_case_calls = 2 * seed_normal_calls + _SCHEMA_REPAIR_CALL_LIMIT_PER_ARM
    bounded_repair_fits_envelope = (
        raw_worst_case_calls <= _budget().max_model_calls
        and seed_worst_case_calls <= _budget().max_model_calls
        and raw_worst_case_calls == 10
        and seed_worst_case_calls == 16
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

    prior_body = _body("suite", "ollama:qwen", "qwen", {"digest": "m"}, {"digest": "a"}, {"x": 1}, [])
    exact_resume_accepts = True
    try:
        validate_checkpoint_identity(prior_body, dict(prior_body))
    except ValueError:
        exact_resume_accepts = False
    changed_body = _body("suite", "ollama:qwen", "qwen", {"digest": "m"}, {"digest": "b"}, {"x": 1}, [])
    implementation_change_rejected = _raises_value_error(lambda: validate_checkpoint_identity(prior_body, changed_body))
    tampered = dict(prior_body)
    tampered["suite_id"] = "tampered"
    checkpoint_tamper_rejected = _raises_value_error(lambda: validate_checkpoint_identity(tampered, changed_body))

    malformed_budget = _budget()
    malformed_meter = BudgetedProvider(ScriptedProvider(["not-json", "still-not-json"]), malformed_budget, provider_id="ollama:qwen")
    malformed_arm = _run_arm(task, malformed_meter, malformed_budget, "raw")
    malformed_fails_closed = (
        malformed_arm.status == "failed:ModelProtocolError"
        and malformed_arm.failure_kind == "model_protocol"
        and malformed_arm.final_hypothesis_id is None
    )

    provider_failure_budget = _budget()
    provider_failure_meter = BudgetedProvider(ScriptedProvider([]), provider_failure_budget, provider_id="ollama:qwen")
    provider_failure_arm = _run_arm(task, provider_failure_meter, provider_failure_budget, "raw")
    provider_failure_classified = (
        provider_failure_arm.status == "infrastructure_error"
        and provider_failure_arm.failure_kind == "provider"
        and provider_failure_arm.final_hypothesis_id is None
    )
    provider_failure_detected = len(_execution_incidents([{"raw": asdict(provider_failure_arm), "seed": asdict(_arm("seed"))}])) == 1

    audit_budget = Budget(max_model_calls=2, max_tokens=1, max_cost_usd=1)
    audit_meter = BudgetedProvider(ScriptedProvider(["two words"]), audit_budget, provider_id="ollama:qwen")
    before_hash = audit_meter.transcript_hash
    try:
        audit_meter.complete([Message("user", "x")], purpose="audit")
    except BudgetExceeded:
        pass
    overbudget_audited = (
        len(audit_meter.records) == 1
        and audit_meter.records[0].budget_accepted is False
        and audit_meter.transcript_hash != before_hash
        and audit_budget.model_calls == 0
    )

    seed_capture = CaptureProvider(_seed_scripted_responses())
    seed_budget = _budget()
    seed_meter = BudgetedProvider(seed_capture, seed_budget, provider_id="ollama:qwen")
    seed_arm = _run_arm(task, seed_meter, seed_budget, "seed")
    seed_purposes = [purpose for purpose, _ in seed_capture.calls]
    expected_purposes = [
        "gate2_seed_attribute_outcomes", "gate2_seed_design", "gate2_seed_design",
        "gate2_seed_final", "gate2_independent", "gate2_adversarial",
    ]
    design_calls = [messages for purpose, messages in seed_capture.calls if purpose == "gate2_seed_design"]
    first_design_text = "\n".join(message.content for message in design_calls[0]) if design_calls else ""
    second_design_text = "\n".join(message.content for message in design_calls[1]) if len(design_calls) > 1 else ""
    designs_hidden_safe = (
        "SECRET_E1_SUPPORTS_H2" not in first_design_text
        and "SECRET_E2_SUPPORTS_H2" not in first_design_text
        and "SECRET_E1_SUPPORTS_H2" not in second_design_text
    )
    seed_experiments = [step.experiment_id for step in seed_arm.history]
    matrix_rows_expected = len(task.hypotheses) * len(task.experiments)
    support_rows_expected = sum(len(experiment.possible_outcomes) for experiment in task.experiments)
    matrix_complete = len(seed_arm.precommitted_probability_matrix) == matrix_rows_expected
    support_complete = len(seed_arm.precommitted_outcome_support) == support_rows_expected

    posterior_map = dict(seed_arm.final_posterior)
    posterior_sums_one = bool(posterior_map) and abs(sum(posterior_map.values()) - 1.0) < 1e-12
    runner_final_overrides_model = seed_arm.final_hypothesis_id == "H2"
    runner_rejection_overrides_model = seed_arm.rejected_hypothesis_ids == ("H1",)
    no_model_action_or_revision = "gate2_seed_action" not in seed_purposes and "gate2_seed_revision" not in seed_purposes
    no_model_probability_forecast = "gate2_seed_forecast_all" not in seed_purposes and "gate2_seed_forecast_hypothesis" not in seed_purposes
    verifier_roles_distinct = (
        seed_arm.independent is not None and seed_arm.adversarial is not None
        and seed_arm.independent.verifier != seed_arm.adversarial.verifier
    )
    verifier_accepts_runner_final = seed_arm.accepted is True
    information_gain_recorded = (
        len(seed_arm.history) == 2
        and seed_arm.history[0].information_gain > seed_arm.history[1].information_gain
        and seed_arm.history[0].information_gain > 0.0
    )
    revisions_are_runner_derived = (
        len(seed_arm.revisions) == 2
        and seed_arm.revisions[-1].hypothesis_id == "H2"
        and "Runner Bayesian update" in seed_arm.revisions[-1].reason
    )
    final_confidence_matches_posterior = abs(seed_arm.confidence - max(posterior_map.values())) < 1e-12
    verifier_prompt_text = "\n".join(
        message.content for purpose, messages in seed_capture.calls
        if purpose in {"gate2_independent", "gate2_adversarial"} for message in messages
    )
    verifier_confidence_semantics_explicit = (
        "support-set audit is correct" in verifier_prompt_text
        and "NOT the runner posterior probability" in verifier_prompt_text
        and "MUST NOT be copied mechanically" in verifier_prompt_text
    )
    model_output_contains_only_support_relation = set(attribution_data) <= {"outcome_support", "notes"}
    six_call_seed_path = seed_arm.usage["model_calls"] == 6 and seed_purposes == expected_purposes

    public = task.public_dict()
    private_key_external = (
        "final_hypothesis_id" not in public
        and "observed_outcome_id" not in json.dumps(public)
        and "SECRET_E1_SUPPORTS_H2" not in json.dumps(public)
        and "SECRET_E2_SUPPORTS_H2" not in json.dumps(public)
    )

    checks = {
        "outcome_attribution_precommitted_before_reveal": attribution_before_reveal,
        "attribution_prompt_hides_private_observations": hidden_absent,
        "attribution_rejects_missing_experiment": invalid_missing_experiment,
        "attribution_rejects_missing_outcome": invalid_missing_outcome,
        "attribution_rejects_empty_support": invalid_empty_support,
        "attribution_rejects_unknown_hypothesis": invalid_unknown_hypothesis,
        "attribution_rejects_duplicate_support": invalid_duplicate_support,
        "canonical_support_weight_must_exceed_one": bad_weight_rejected,
        "canonical_likelihood_rows_are_normalized": canonical_rows_normalized,
        "canonical_likelihood_ratio_is_runner_fixed": canonical_ratio_fixed,
        "ambiguous_experiment_stays_uniform": weak_ambiguous_uniform,
        "model_output_contains_support_relation_not_probabilities": model_output_contains_only_support_relation,
        "information_gain_prefers_stronger_experiment": ig2 > ig1 and selected == "E2" and selected_ig == ig2,
        "posterior_update_favors_observed_hypothesis": posterior1["H2"] > posterior1["H1"],
        "adaptive_second_experiment_uses_remaining_choice": second == "E1",
        "posterior_final_is_runner_derived": final_id == "H2" and final_tie == ("H2",),
        "bayes_factor_rejection_is_runner_derived": rejected == ("H1",),
        "seed_experiment_choice_is_runner_derived": seed_experiments == ["E2", "E1"],
        "seed_design_calls_are_pre_reveal_safe": designs_hidden_safe,
        "seed_call_order_is_explicit": seed_purposes == expected_purposes,
        "seed_uses_six_model_calls": six_call_seed_path,
        "seed_has_no_model_probability_forecast": no_model_probability_forecast,
        "seed_has_no_model_action_or_revision_calls": no_model_action_or_revision,
        "seed_precommitted_support_is_complete": support_complete,
        "seed_precommitted_matrix_is_complete": matrix_complete,

        "seed_final_posterior_is_normalized": posterior_sums_one,
        "seed_final_model_cannot_override_runner": runner_final_overrides_model,
        "seed_rejection_model_cannot_override_runner": runner_rejection_overrides_model,
        "seed_information_gain_is_recorded": information_gain_recorded,
        "seed_revisions_are_runner_derived": revisions_are_runner_derived,
        "seed_confidence_matches_runner_posterior": final_confidence_matches_posterior,
        "verifier_roles_are_distinct_calls": verifier_roles_distinct,
        "verifiers_accept_runner_derived_final": verifier_accepts_runner_final,
        "verifier_confidence_is_audit_confidence_not_posterior": verifier_confidence_semantics_explicit,
        "mechanical_tie_blocks_verifier": _verifier_verdict("H2", ("H2",), ("H1", "H2"), False) == "fail",
        "lower_support_final_blocks_verifier": _verifier_verdict("H2", ("H2",), ("H1",), False) == "fail",
        "provider_schema_constrains_attribution_shape": attribution_schema_active,
        "provider_schema_constrains_raw_action_shape": action_schema_active,
        "provider_schema_constrains_seed_design_shape": design_schema_active,
        "provider_schema_constrains_final_shape": final_schema_active,
        "provider_schema_constrains_verifier_shape": verifier_schema_active,
        "provider_repair_schema_remains_stage_generic": repair_schema_is_stage_generic,
        "provider_preflight_policy_is_task_independent": preflight_policy_safe,
        "provider_preflight_runtime_is_bounded": preflight_runtime_bounded,
        "second_schema_repair_can_recover": second_schema_repair_recovers,
        "schema_repair_hard_cap_is_two": schema_repair_hard_cap,
        "bounded_repair_worst_case_fits_model_call_envelope": bounded_repair_fits_envelope,
        "resource_envelope_matches_runner": resource_envelope_matches,
        "same_identity_pair_validates": pair_validates,
        "model_identity_mismatch_rejected": model_mismatch_rejected,
        "resource_envelope_mismatch_rejected": envelope_mismatch_rejected,
        "exact_resume_identity_accepts": exact_resume_accepts,
        "implementation_change_invalidates_resume": implementation_change_rejected,
        "checkpoint_hash_tamper_rejected": checkpoint_tamper_rejected,
        "malformed_model_json_fails_closed": malformed_fails_closed,
        "provider_failure_is_classified_as_infrastructure": provider_failure_classified,
        "provider_failure_is_detected_as_execution_incident": provider_failure_detected,
        "overbudget_response_is_transcript_audited": overbudget_audited,
        "private_answer_key_external_to_candidate_prompt": private_key_external,
    }
    evidence = {
        "check_count": len(checks),
        "resource_envelope": _budget().limits(),
        "canonical_support_weight": 3.0,
        "seed_call_purposes": seed_purposes,
        "seed_selected_experiments": seed_experiments,
        "seed_final_hypothesis_id": seed_arm.final_hypothesis_id,
        "seed_rejected_hypothesis_ids": list(seed_arm.rejected_hypothesis_ids),
        "seed_final_posterior": dict(seed_arm.final_posterior),
        "information_gain": {"E1": ig1, "E2": ig2},
        "schema_repair_call_limit_per_arm": _SCHEMA_REPAIR_CALL_LIMIT_PER_ARM,
        "worst_case_model_calls": {"raw": raw_worst_case_calls, "seed": seed_worst_case_calls},
        "qualification_note": "Deterministic Gate-2 protocol/integrity canaries; not empirical Gate-2 certification.",
    }

    body = {
        "qualification": "gate2-research-protocol-v3.1",
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
    output.write_text(json.dumps(certificate.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
