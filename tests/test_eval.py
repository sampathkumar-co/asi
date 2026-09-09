import tempfile, json, unittest
from pathlib import Path
from seed.eval.cases import EvalCase, exact_match, numeric_match
from seed.eval.metrics import metaproductivity, recursive_amplification
from seed.eval.receipts import write_receipt
from seed.eval.suite import EvalSuite

class EvalTests(unittest.TestCase):
    def test_suite_scores(self):
        suite = EvalSuite("s", [EvalCase("a", "x", exact_match("x")), EvalCase("b", "2", numeric_match(2))])
        out = suite.run("c", lambda p: p)
        self.assertEqual(out.score, 1.0)
        self.assertEqual(len(out.receipt.content_hash), 64)

    def test_receipt_writes(self):
        suite = EvalSuite("s", [EvalCase("a", "x", exact_match("x"))])
        out = suite.run("c", lambda p: p)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "receipt.json"
            write_receipt(out.receipt, p)
            self.assertEqual(json.loads(p.read_text())["content_hash"], out.receipt.content_hash)

    def test_recursive_metrics(self):
        self.assertEqual(metaproductivity(0.2, 2.0), 0.1)
        self.assertAlmostEqual(recursive_amplification(0.1, 0.15), 1.5)
        self.assertIsNone(recursive_amplification(0.0, 0.1))

if __name__ == "__main__": unittest.main()
