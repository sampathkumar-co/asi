import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from seed.gate1.realchat import ChatTurn, PairedRealChatEvidence, RealChatRun, load_pair


LIMITS = {"max_steps": 8, "max_model_calls": 12, "max_tool_calls": 8, "max_tokens": 8000, "max_cost_usd": 0.0}


def make_run(arm: str, **overrides):
    base = RealChatRun(
        arm=arm,
        task_id="task-001",
        provider_id="openai-chatgpt",
        model_id="gpt-5.6-sol",
        surface_id="chatgpt-web",
        evidence_level="manual_chat",
        limits=dict(LIMITS),
        usage={"steps": 1, "model_calls": 1, "tool_calls": 0, "tokens": 0, "cost_usd": 0.0},
        turns=(ChatTurn("user", "Solve the task."), ChatTurn("assistant", "Answer")),
        final_answer="Answer",
    )
    return replace(base, **overrides)


class RealChatTests(unittest.TestCase):
    def test_valid_manual_pair_is_pilot_not_certification(self):
        pair = PairedRealChatEvidence(make_run("raw"), make_run("seed"))
        pair.validate()
        self.assertEqual(pair.minimum_evidence_level, "manual_chat")
        self.assertFalse(pair.certification_ready)
        self.assertEqual(len(pair.content_hash), 64)

    def test_mismatched_model_rejected(self):
        raw = make_run("raw")
        seed = make_run("seed", model_id="different-model")
        with self.assertRaises(ValueError):
            PairedRealChatEvidence(raw, seed).validate()

    def test_mismatched_envelope_rejected(self):
        raw = make_run("raw")
        seed = make_run("seed", limits={**LIMITS, "max_tokens": 9000})
        with self.assertRaises(ValueError):
            PairedRealChatEvidence(raw, seed).validate()

    def test_overspend_rejected(self):
        raw = make_run("raw")
        seed = make_run("seed", usage={"steps": 1, "model_calls": 1, "tool_calls": 0, "tokens": 9000, "cost_usd": 0.0})
        with self.assertRaises(ValueError):
            PairedRealChatEvidence(raw, seed).validate()

    def test_attested_pair_with_gate0_receipts_can_be_certification_ready(self):
        digest = "a" * 64
        raw = make_run("raw", evidence_level="platform_export", gate0_receipt_hash=digest, model_identity_attested=True, usage_attested=True)
        seed = make_run("seed", evidence_level="platform_export", gate0_receipt_hash=digest, model_identity_attested=True, usage_attested=True)
        pair = PairedRealChatEvidence(raw, seed)
        self.assertTrue(pair.certification_ready)

    def test_load_pair_and_hash_tamper_signal(self):
        with tempfile.TemporaryDirectory() as d:
            raw = make_run("raw")
            seed = make_run("seed")
            rp = Path(d) / "raw.json"
            sp = Path(d) / "seed.json"
            rp.write_text(json.dumps({**raw.__dict__, "turns": [t.__dict__ for t in raw.turns]}), encoding="utf-8")
            sp.write_text(json.dumps({**seed.__dict__, "turns": [t.__dict__ for t in seed.turns]}), encoding="utf-8")
            before = load_pair(rp, sp).content_hash
            data = json.loads(sp.read_text())
            data["final_answer"] = "tampered"
            sp.write_text(json.dumps(data), encoding="utf-8")
            after = load_pair(rp, sp).content_hash
            self.assertNotEqual(before, after)


if __name__ == "__main__":
    unittest.main()
