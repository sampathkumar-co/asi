import unittest
from dataclasses import replace

from seed.gate1.campaign import Gate1Criterion, ScoredChatPair, summarize_campaign
from seed.gate1.realchat import ChatTurn, PairedRealChatEvidence, RealChatRun


LIMITS = {"max_steps": 8, "max_model_calls": 12, "max_tool_calls": 8, "max_tokens": 8000, "max_cost_usd": 0.0}


def run(arm: str, task_id: str, *, ready: bool = True) -> RealChatRun:
    digest = "b" * 64 if ready else None
    return RealChatRun(
        arm=arm,
        task_id=task_id,
        provider_id="openai-chatgpt",
        model_id="gpt-5.6-sol",
        surface_id="chatgpt-web",
        evidence_level="platform_export" if ready else "manual_chat",
        limits=dict(LIMITS),
        usage={"steps": 1, "model_calls": 1, "tool_calls": 0, "tokens": 100, "cost_usd": 0.0},
        turns=(ChatTurn("user", "task"), ChatTurn("assistant", "answer")),
        final_answer="answer",
        gate0_receipt_hash=digest,
        model_identity_attested=ready,
        usage_attested=ready,
    )


def pair(i: int, raw_score: float, seed_score: float, *, ready: bool = True) -> ScoredChatPair:
    evidence = PairedRealChatEvidence(run("raw", f"task-{i}", ready=ready), run("seed", f"task-{i}", ready=ready))
    return ScoredChatPair(evidence, raw_score, seed_score)


class Gate1CampaignTests(unittest.TestCase):
    def test_strong_attested_campaign_passes(self):
        records = [pair(i, 0.25, 0.85) for i in range(10)]
        summary = summarize_campaign(records, seed=7)
        self.assertTrue(summary.passed)
        self.assertGreater(summary.ci_low, 0.0)
        self.assertEqual(summary.pair_count, 10)
        self.assertEqual(len(summary.content_hash), 64)

    def test_manual_chat_campaign_cannot_full_certify(self):
        records = [pair(i, 0.2, 0.9, ready=False) for i in range(8)]
        summary = summarize_campaign(records, seed=1)
        self.assertFalse(summary.passed)
        self.assertTrue(any("attested" in failure for failure in summary.failures))

    def test_small_campaign_fails_min_pairs(self):
        records = [pair(i, 0.1, 0.9) for i in range(3)]
        summary = summarize_campaign(records, criterion=Gate1Criterion(min_pairs=8), seed=2)
        self.assertFalse(summary.passed)
        self.assertTrue(any("8 paired" in failure for failure in summary.failures))

    def test_mixed_model_campaign_rejected(self):
        records = [pair(0, 0.1, 0.9), pair(1, 0.1, 0.9)]
        changed_seed = replace(records[1].pair.seed, model_id="other")
        records[1] = ScoredChatPair(PairedRealChatEvidence(records[1].pair.raw, changed_seed), 0.1, 0.9)
        with self.assertRaises(ValueError):
            summarize_campaign(records)

    def test_duplicate_task_rejected(self):
        records = [pair(0, 0.1, 0.9), pair(0, 0.2, 0.8)]
        with self.assertRaises(ValueError):
            summarize_campaign(records)


if __name__ == "__main__":
    unittest.main()
