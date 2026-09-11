from __future__ import annotations

import hashlib
import json
from pathlib import Path
from statistics import fmean
from typing import Any

from seed.eval.statistics import paired_bootstrap

_WEIGHTS = {
    "correct_final_hypothesis": 0.40,
    "first_experiment_discriminating": 0.15,
    "selected_informative_experiment": 0.05,
    "prediction_consistency": 0.15,
    "required_controls": 0.10,
    "evidence_driven_rejection": 0.10,
    "critical_risk_detection": 0.05,
}

DEVELOPMENT_PROMOTION_CRITERIA = {
    "min_valid_pairs": 16,
    "min_seed_mean": 0.75,
    "min_mean_gain": 0.15,
    "min_win_rate": 0.60,
    "min_ci_low_exclusive": 0.0,
    "min_seed_verifier_acceptance": 0.75,
}


def _sha256_json(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _without_hash(body: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in body.items() if key != "content_hash"}


def _usage_within_limits(arm: dict[str, Any]) -> bool:
    limits = arm.get("limits", {})
    usage = arm.get("usage", {})
    checks = (
        ("steps", "max_steps"),
        ("model_calls", "max_model_calls"),
        ("tool_calls", "max_tool_calls"),
        ("tokens", "max_tokens"),
        ("cost_usd", "max_cost_usd"),
    )
    try:
        return all(float(usage[u]) <= float(limits[l]) for u, l in checks)
    except (KeyError, TypeError, ValueError):
        return False


def validate_evidence(evidence: dict[str, Any]) -> list[dict[str, Any]]:
    if evidence.get("gate") != 2:
        raise ValueError("not Gate-2 evidence")
    if evidence.get("content_hash") != _sha256_json(_without_hash(evidence)):
        raise ValueError("Gate-2 evidence content hash mismatch")
    pairs = evidence.get("pairs")
    if not isinstance(pairs, list) or not pairs:
        raise ValueError("Gate-2 evidence must contain non-empty pairs")
    seen: set[str] = set()
    for pair in pairs:
        if not isinstance(pair, dict):
            raise ValueError("malformed Gate-2 pair")
        raw = pair.get("raw")
        seed = pair.get("seed")
        if not isinstance(raw, dict) or not isinstance(seed, dict):
            raise ValueError("Gate-2 pair missing raw/seed arms")
        if raw.get("arm") != "raw" or seed.get("arm") != "seed":
            raise ValueError("Gate-2 arm labels are invalid")
        task_id = str(raw.get("task_id", ""))
        if not task_id or task_id != str(seed.get("task_id", "")):
            raise ValueError("Gate-2 raw/seed task mismatch")
        if task_id in seen:
            raise ValueError("Gate-2 evidence contains duplicate task")
        seen.add(task_id)
        if raw.get("provider_id") != seed.get("provider_id") or raw.get("model_id") != seed.get("model_id"):
            raise ValueError("Gate-2 raw/seed model identity mismatch")
        if raw.get("limits") != seed.get("limits"):
            raise ValueError("Gate-2 raw/seed resource envelope mismatch")
        if not _usage_within_limits(raw) or not _usage_within_limits(seed):
            raise ValueError("Gate-2 arm exceeded declared resource envelope")
        if raw.get("provider_id") != evidence.get("provider_id") or seed.get("provider_id") != evidence.get("provider_id"):
            raise ValueError("Gate-2 pair provider differs from campaign identity")
        if raw.get("model_id") != evidence.get("model") or seed.get("model_id") != evidence.get("model"):
            raise ValueError("Gate-2 pair model differs from campaign identity")
        expected_pair_hash = _sha256_json({"raw": raw, "seed": seed})
        if pair.get("pair_hash") != expected_pair_hash:
            raise ValueError("Gate-2 pair hash mismatch")
    return pairs


def _as_ids(value: object, label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise ValueError(f"{label} must be a list of non-empty ids")
    if len(value) != len(set(value)):
        raise ValueError(f"{label} must not contain duplicates")
    return tuple(value)


def _validate_answer(answer: dict[str, Any]) -> None:
    if not isinstance(answer.get("final_hypothesis_id"), str) or not answer["final_hypothesis_id"]:
        raise ValueError("answer missing final_hypothesis_id")
    discriminating = _as_ids(answer.get("discriminating_experiment_ids"), "discriminating_experiment_ids")
    informative = _as_ids(answer.get("informative_experiment_ids"), "informative_experiment_ids")
    if not set(discriminating).issubset(set(informative)):
        raise ValueError("discriminating experiments must be informative")
    _as_ids(answer.get("required_control_ids"), "required_control_ids")
    _as_ids(answer.get("reject_hypothesis_ids"), "reject_hypothesis_ids")
    _as_ids(answer.get("critical_risk_ids"), "critical_risk_ids")
    prediction_map = answer.get("prediction_map")
    if not isinstance(prediction_map, dict) or not prediction_map:
        raise ValueError("answer missing prediction_map")
    for hypothesis_id, by_experiment in prediction_map.items():
        if not isinstance(hypothesis_id, str) or not hypothesis_id or not isinstance(by_experiment, dict):
            raise ValueError("malformed prediction_map")
        for experiment_id, outcomes in by_experiment.items():
            if not isinstance(experiment_id, str) or not experiment_id:
                raise ValueError("malformed prediction_map experiment")
            _as_ids(outcomes, "prediction outcomes")


def _prediction_fraction(history: list[dict[str, Any]], prediction_map: dict[str, Any]) -> float:
    if not history:
        return 0.0
    correct = 0
    for step in history:
        hypothesis_id = step.get("hypothesis_id")
        experiment_id = step.get("experiment_id")
        predicted = step.get("predicted_outcome_id")
        expected = prediction_map.get(hypothesis_id, {}).get(experiment_id, [])
        if predicted in expected:
            correct += 1
    return correct / len(history)


def _score_arm(arm: dict[str, Any], answer: dict[str, Any]) -> tuple[float, dict[str, float], bool]:
    _validate_answer(answer)
    components = {name: 0.0 for name in _WEIGHTS}
    if arm.get("status") != "succeeded":
        return 0.0, components, True
    history = arm.get("history")
    revisions = arm.get("revisions", [])
    if not isinstance(history, (list, tuple)) or not history:
        return 0.0, components, True
    if not isinstance(revisions, (list, tuple)):
        return 0.0, components, True
    if arm.get("final_hypothesis_id") == answer["final_hypothesis_id"]:
        components["correct_final_hypothesis"] = _WEIGHTS["correct_final_hypothesis"]
    first_experiment = history[0].get("experiment_id")
    if first_experiment in answer["discriminating_experiment_ids"]:
        components["first_experiment_discriminating"] = _WEIGHTS["first_experiment_discriminating"]
    selected = {step.get("experiment_id") for step in history}
    if selected.intersection(answer["informative_experiment_ids"]):
        components["selected_informative_experiment"] = _WEIGHTS["selected_informative_experiment"]
    fraction = _prediction_fraction(history, answer["prediction_map"])
    components["prediction_consistency"] = _WEIGHTS["prediction_consistency"] * fraction
    used_controls = {item for step in history for item in step.get("control_ids", [])}
    if set(answer["required_control_ids"]).issubset(used_controls):
        components["required_controls"] = _WEIGHTS["required_controls"]
    rejected = set(arm.get("rejected_hypothesis_ids", []))
    rejected.update(item for step in history for item in step.get("rejected_hypothesis_ids", []))
    rejected.update(item for revision in revisions for item in revision.get("rejected_hypothesis_ids", []))
    if set(answer["reject_hypothesis_ids"]).issubset(rejected):
        components["evidence_driven_rejection"] = _WEIGHTS["evidence_driven_rejection"]
    risks = set(arm.get("risk_ids", []))
    risks.update(item for step in history for item in step.get("risk_ids", []))
    risks.update(item for revision in revisions for item in revision.get("risk_ids", []))
    if set(answer["critical_risk_ids"]).issubset(risks):
        components["critical_risk_detection"] = _WEIGHTS["critical_risk_detection"]
    return sum(components.values()), components, False


def _promotion_checks(report: dict[str, Any], criteria: dict[str, Any]) -> dict[str, bool]:
    return {
        "valid_pairs": report["valid_pair_count"] >= int(criteria["min_valid_pairs"]),
        "seed_mean": report["seed_mean"] >= float(criteria["min_seed_mean"]),
        "mean_gain": report["mean_gain"] >= float(criteria["min_mean_gain"]),
        "strict_win_rate": report["win_rate"] >= float(criteria["min_win_rate"]),
        "ci_lower_bound_positive": report["ci_low"] > float(criteria["min_ci_low_exclusive"]),
        "seed_verifier_acceptance": report["seed_verifier_acceptance"] >= float(criteria["min_seed_verifier_acceptance"]),
    }


def score_research_campaign(evidence_path: str | Path, answer_path: str | Path) -> dict[str, Any]:
    evidence_raw = Path(evidence_path).read_bytes()
    evidence = json.loads(evidence_raw.decode("utf-8"))
    pairs = validate_evidence(evidence)
    answer_raw = Path(answer_path).read_bytes()
    key = json.loads(answer_raw.decode("utf-8"))
    if evidence.get("suite_id") != key.get("suite_id"):
        raise ValueError("Gate-2 evidence/answer suite mismatch")
    answers = key.get("answers")
    if not isinstance(answers, dict):
        raise ValueError("Gate-2 answer key missing answers")
    criteria = key.get("promotion_criteria", DEVELOPMENT_PROMOTION_CRITERIA)
    if not isinstance(criteria, dict):
        raise ValueError("Gate-2 promotion criteria must be an object")

    raw_scores: list[float] = []
    seed_scores: list[float] = []
    per_task: list[dict[str, Any]] = []
    seed_acceptance: list[float] = []
    for pair in pairs:
        task_id = pair["raw"]["task_id"]
        answer = answers.get(task_id)
        if not isinstance(answer, dict):
            raise ValueError(f"missing Gate-2 answer key for {task_id}")
        raw_score, raw_components, raw_failed_closed = _score_arm(pair["raw"], answer)
        seed_score, seed_components, seed_failed_closed = _score_arm(pair["seed"], answer)
        raw_scores.append(raw_score)
        seed_scores.append(seed_score)
        seed_acceptance.append(1.0 if pair["seed"].get("accepted") is True else 0.0)
        per_task.append({
            "task_id": task_id,
            "raw_score": raw_score,
            "seed_score": seed_score,
            "raw_components": raw_components,
            "seed_components": seed_components,
            "raw_failed_closed": raw_failed_closed,
            "seed_failed_closed": seed_failed_closed,
            "seed_verifier_accepted": pair["seed"].get("accepted") is True,
        })
    if len(raw_scores) < 2:
        raise ValueError("Gate-2 scoring requires at least two paired tasks")
    comparison = paired_bootstrap(raw_scores, seed_scores, samples=4000, seed=0)
    report: dict[str, Any] = {
        "gate": 2,
        "suite_id": evidence["suite_id"],
        "evidence_hash": evidence["content_hash"],
        "evidence_file_sha256": hashlib.sha256(evidence_raw).hexdigest(),
        "answer_key_sha256": hashlib.sha256(answer_raw).hexdigest(),
        "valid_pair_count": len(pairs),
        "raw_mean": comparison.baseline_mean,
        "seed_mean": comparison.candidate_mean,
        "mean_gain": comparison.mean_gain,
        "ci_low": comparison.ci_low,
        "ci_high": comparison.ci_high,
        "win_rate": comparison.win_rate,
        "seed_verifier_acceptance": fmean(seed_acceptance),
        "promotion_criteria": dict(criteria),
        "per_task": per_task,
    }
    checks = _promotion_checks(report, criteria)
    report["promotion_checks"] = checks
    report["promotion_pass"] = all(checks.values())
    report["scoring_weights"] = dict(_WEIGHTS)
    report["content_hash"] = _sha256_json(report)
    return report


def validate_answer_key_for_tasks(task_path: str | Path, answer_path: str | Path) -> dict[str, Any]:
    """Fail closed if an external Gate-2 key does not match the declared task catalog."""
    from .schema import load_research_tasks

    suite_id, tasks = load_research_tasks(task_path)
    key = json.loads(Path(answer_path).read_text(encoding="utf-8"))
    if key.get("suite_id") != suite_id or not isinstance(key.get("answers"), dict):
        raise ValueError("Gate-2 task/key suite mismatch")
    answers = key["answers"]
    task_ids = {task.task_id for task in tasks}
    if set(answers) != task_ids:
        raise ValueError("Gate-2 answer key task set mismatch")

    for task in tasks:
        answer = answers[task.task_id]
        if not isinstance(answer, dict):
            raise ValueError(f"malformed answer for {task.task_id}")
        _validate_answer(answer)
        hypotheses = {item.id for item in task.hypotheses}
        experiments = {item.id: item for item in task.experiments}
        controls = {item.id for item in task.controls}
        risks = {item.id for item in task.risks}
        if answer["final_hypothesis_id"] not in hypotheses:
            raise ValueError(f"invalid final hypothesis in key for {task.task_id}")
        for label in ("discriminating_experiment_ids", "informative_experiment_ids"):
            if not set(answer[label]).issubset(experiments):
                raise ValueError(f"invalid experiment id in {label} for {task.task_id}")
        if not set(answer["required_control_ids"]).issubset(controls):
            raise ValueError(f"invalid required control for {task.task_id}")
        if not set(answer["reject_hypothesis_ids"]).issubset(hypotheses):
            raise ValueError(f"invalid rejected hypothesis for {task.task_id}")
        if not set(answer["critical_risk_ids"]).issubset(risks):
            raise ValueError(f"invalid critical risk for {task.task_id}")
        if set(answer["prediction_map"]) != hypotheses:
            raise ValueError(f"prediction map must cover every hypothesis for {task.task_id}")
        for hypothesis_id, by_experiment in answer["prediction_map"].items():
            if set(by_experiment) != set(experiments):
                raise ValueError(f"prediction map must cover every experiment for {task.task_id}/{hypothesis_id}")
            for experiment_id, predicted in by_experiment.items():
                outcome_ids = {item.id for item in experiments[experiment_id].possible_outcomes}
                if not set(predicted).issubset(outcome_ids):
                    raise ValueError(f"invalid predicted outcome for {task.task_id}/{hypothesis_id}/{experiment_id}")

    return {"suite_id": suite_id, "task_count": len(tasks), "valid": True}