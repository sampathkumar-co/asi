from dataclasses import asdict
import json
import tempfile
import unittest
from pathlib import Path

from seed.gate2.local_campaign import (
    ResearchArmEvidence, ResearchPairEvidence, ResearchStep, VerificationEvidence, _body
)
from seed.gate2.scoring import (
    _score_arm, score_research_campaign, validate_answer_key_for_tasks, validate_evidence
)


LIMITS = {
    "max_steps": 8, "max_model_calls": 12, "max_tool_calls": 0,
    "max_tokens": 8000, "max_cost_usd": 0.0,
}
USAGE = {"steps": 4, "model_calls": 4, "tool_calls": 0, "tokens": 100, "cost_usd": 0.0}


def answer():
    return {
        "final_hypothesis_id": "H2",
        "discriminating_experiment_ids": ["E1"],
        "informative_experiment_ids": ["E1", "E2"],
        "prediction_map": {"H1": {"E1": ["O1"]}, "H2": {"E2": ["O2"]}},
        "required_control_ids": ["C1"],
        "reject_hypothesis_ids": ["H1"],
        "critical_risk_ids": ["K1"],
    }


def arm(arm_name: str, *, perfect: bool, status: str = "succeeded") -> ResearchArmEvidence:
    if perfect:
        steps = (
            ResearchStep("H1", "E1", "O1", ("C1",), (), ("K1",), "O2", "evidence"),
            ResearchStep("H2", "E2", "O2", ("C1",), ("H1",), ("K1",), "O2", "evidence2"),
        )
        final, rejected, risks = "H2", ("H1",), ("K1",)
    else:
        steps = (ResearchStep("H1", "E2", "O9", (), (), (), "O2", "evidence"),)
        final, rejected, risks = "H1", (), ()
    independent = VerificationEvidence("independent", "pass", 0.9, ("K1",), "ok") if arm_name == "seed" else None
    adversarial = VerificationEvidence("adversarial", "pass", 0.9, ("K1",), "ok") if arm_name == "seed" else None
    return ResearchArmEvidence(
        "R1", arm_name, "ollama:qwen", "qwen", steps,
        final, rejected, risks, 0.9, independent, adversarial,
        True if arm_name == "seed" else None, status, LIMITS, USAGE, "a" * 64,
    )


def evidence_for_two_pairs():
    pairs = []
    for task_id in ("R1", "R2"):
        raw = arm("raw", perfect=False)
        seed = arm("seed", perfect=True)
        raw = ResearchArmEvidence(task_id, *asdict(raw).values().__iter__()) if False else raw
        raw_dict = asdict(raw); raw_dict["task_id"] = task_id
        seed_dict = asdict(seed); seed_dict["task_id"] = task_id
        pair_hash = ResearchPairEvidence(
            ResearchArmEvidence(**raw_dict), ResearchArmEvidence(**seed_dict)
        ).content_hash
        pairs.append({"raw": raw_dict, "seed": seed_dict, "pair_hash": pair_hash})
    return _body("suite", "ollama:qwen", "qwen", {"digest": "m"}, {"digest": "i"}, {"x": 1}, pairs)


class Gate2ScoringTests(unittest.TestCase):
    def test_perfect_arm_scores_one(self):
        score, components, failed_closed = _score_arm(asdict(arm("seed", perfect=True)), answer())
        self.assertAlmostEqual(score, 1.0)
        self.assertFalse(failed_closed)
        self.assertAlmostEqual(sum(components.values()), 1.0)

    def test_failed_arm_scores_zero(self):
        score, components, failed_closed = _score_arm(
            asdict(arm("raw", perfect=True, status="budget_exhausted")), answer()
        )
        self.assertEqual(score, 0.0)
        self.assertTrue(failed_closed)
        self.assertEqual(sum(components.values()), 0.0)

    def test_evidence_hash_tamper_is_rejected(self):
        evidence = evidence_for_two_pairs()
        evidence["suite_id"] = "tampered"
        with self.assertRaises(ValueError):
            validate_evidence(evidence)

    def test_pair_hash_tamper_is_rejected(self):
        evidence = evidence_for_two_pairs()
        evidence["pairs"][0]["pair_hash"] = "0" * 64
        evidence["content_hash"] = __import__("hashlib").sha256(
            json.dumps({k: v for k, v in evidence.items() if k != "content_hash"}, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        with self.assertRaises(ValueError):
            validate_evidence(evidence)

    def test_external_campaign_scoring_uses_separate_key(self):
        evidence = evidence_for_two_pairs()
        key = {"suite_id": "suite", "answers": {"R1": answer(), "R2": answer()}}
        with tempfile.TemporaryDirectory() as td:
            evidence_path = Path(td) / "evidence.json"
            key_path = Path(td) / "answers.json"
            evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
            key_path.write_text(json.dumps(key), encoding="utf-8")
            report = score_research_campaign(evidence_path, key_path)
        self.assertEqual(report["valid_pair_count"], 2)
        self.assertAlmostEqual(report["seed_mean"], 1.0)
        self.assertGreater(report["seed_mean"], report["raw_mean"])
        self.assertAlmostEqual(report["seed_verifier_acceptance"], 1.0)
        self.assertFalse(report["promotion_pass"])
        self.assertEqual(len(report["content_hash"]), 64)

    def test_resource_overage_is_rejected(self):
        evidence = evidence_for_two_pairs()
        evidence["pairs"][0]["raw"]["usage"]["steps"] = 99
        pair = evidence["pairs"][0]
        pair["pair_hash"] = __import__("hashlib").sha256(
            json.dumps({"raw": pair["raw"], "seed": pair["seed"]}, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        evidence["content_hash"] = __import__("hashlib").sha256(
            json.dumps({k: v for k, v in evidence.items() if k != "content_hash"}, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        with self.assertRaises(ValueError):
            validate_evidence(evidence)

    def test_public_calibration_task_key_pair_validates(self):
        root = Path(__file__).resolve().parents[1]
        report = validate_answer_key_for_tasks(
            root / "configs/gate2_public_calibration_v1.json",
            root / "configs/gate2_public_calibration_v1_answers.json",
        )
        self.assertTrue(report["valid"])
        self.assertEqual(report["task_count"], 8)


if __name__ == "__main__":
    unittest.main()
