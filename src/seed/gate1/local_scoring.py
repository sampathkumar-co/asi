from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from collections.abc import Sequence

from seed.eval.statistics import paired_bootstrap

_FINAL_RE = re.compile(r"(?im)^\s*FINAL:\s*(.+?)\s*$")


def _canonical(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"\s*([|=,\-])\s*", r"\1", value)
    return value


def extract_final(output: str | None) -> str | None:
    if not output:
        return None
    matches = _FINAL_RE.findall(output)
    return matches[-1].strip() if matches else None


def score_answer(output: str | None, accepted: str | Sequence[str]) -> float:
    final = extract_final(output)
    if final is None:
        return 0.0
    candidates = (accepted,) if isinstance(accepted, str) else tuple(accepted)
    if not candidates or any(not isinstance(x, str) for x in candidates):
        raise ValueError("accepted answers must be a string or non-empty sequence of strings")
    actual = _canonical(final)
    return 1.0 if any(actual == _canonical(x) for x in candidates) else 0.0


def score_local_campaign(evidence_path: str | Path, answer_path: str | Path) -> dict:
    evidence = json.loads(Path(evidence_path).read_text(encoding="utf-8"))
    answers_raw = Path(answer_path).read_bytes()
    answers = json.loads(answers_raw.decode("utf-8"))
    if evidence["suite_id"] != answers["suite_id"]:
        raise ValueError("evidence/answer suite mismatch")
    expected = answers["answers"]
    raw_scores: list[float] = []
    seed_scores: list[float] = []
    per_task: list[dict] = []
    for item in evidence["pairs"]:
        tid = item["raw"]["task_id"]
        if tid not in expected:
            raise ValueError(f"missing answer key for {tid}")
        raw_score = score_answer(item["raw"].get("answer"), expected[tid])
        seed_score = score_answer(item["seed"].get("answer"), expected[tid])
        raw_scores.append(raw_score)
        seed_scores.append(seed_score)
        per_task.append({"task_id": tid, "raw_score": raw_score, "seed_score": seed_score})
    comparison = paired_bootstrap(raw_scores, seed_scores, samples=4000, seed=0)
    report = {
        "suite_id": evidence["suite_id"],
        "evidence_hash": evidence["content_hash"],
        "answer_key_sha256": hashlib.sha256(answers_raw).hexdigest(),
        "pair_count": len(per_task),
        "raw_mean": comparison.baseline_mean,
        "seed_mean": comparison.candidate_mean,
        "mean_gain": comparison.mean_gain,
        "ci_low": comparison.ci_low,
        "ci_high": comparison.ci_high,
        "win_rate": comparison.win_rate,
        "per_task": per_task,
    }
    encoded = json.dumps(report, sort_keys=True, separators=(",", ":")).encode()
    report["content_hash"] = hashlib.sha256(encoded).hexdigest()
    return report
