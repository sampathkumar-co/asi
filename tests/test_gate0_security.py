import tempfile
import unittest
from pathlib import Path

from seed.eval.integrity import snapshot_tree, unchanged
from seed.eval.receipts import make_receipt
from seed.eval.resources import ResourceUsage
from seed.eval.signing import ReceiptSigner, SignedReceipt
from seed.eval.statistics import paired_bootstrap, summarize_scores


class Gate0SecurityTests(unittest.TestCase):
    def test_receipt_signature_and_tamper_detection(self):
        receipt = make_receipt("s", "c", 1.0, {"x": 1.0}, {})
        signer = ReceiptSigner(b"s" * 32)
        signed = signer.sign(receipt)
        self.assertTrue(signer.verify(receipt, signed))
        forged = SignedReceipt(signed.content_hash, "0" * 64)
        self.assertFalse(signer.verify(receipt, forged))

    def test_short_signing_key_rejected(self):
        with self.assertRaises(ValueError):
            ReceiptSigner(b"short")

    def test_tree_snapshot_detects_mutation(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); f = root / "a.txt"; f.write_text("a")
            before = snapshot_tree(root)
            f.write_text("b")
            after = snapshot_tree(root)
            self.assertFalse(unchanged(before, after))

    def test_score_confidence_summary(self):
        summary = summarize_scores([1.0, 1.0, 1.0, 1.0, 1.0])
        self.assertEqual(summary.ci_low, 1.0)
        self.assertEqual(summary.ci_high, 1.0)

    def test_paired_bootstrap(self):
        result = paired_bootstrap([0, 0, 0, 0], [1, 1, 1, 1], samples=500, seed=1)
        self.assertEqual(result.mean_gain, 1.0)
        self.assertEqual(result.ci_low, 1.0)

    def test_resource_accounting_rejects_negative(self):
        with self.assertRaises(ValueError):
            ResourceUsage(cost_usd=-1).validate()

    def test_resource_accounting_is_explicit(self):
        usage = ResourceUsage(wall_time_s=60, cost_usd=2, human_interventions=1)
        self.assertAlmostEqual(usage.normalized_cost(), 3.02)


if __name__ == "__main__":
    unittest.main()
