import json, tempfile, unittest
from pathlib import Path
from seed.eval.holdout import load_private_holdout
from seed.eval.repeated import run_repeated
from seed.eval.cases import EvalCase, exact_match
from seed.eval.suite import EvalSuite

class HoldoutTests(unittest.TestCase):
    def test_private_holdout_must_be_outside_repo(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); p = root / "hidden.json"
            p.write_text(json.dumps({"suite_id":"h","cases":[{"id":"1","prompt":"x","type":"exact","expected":"x"}]}))
            with self.assertRaises(PermissionError): load_private_holdout(p, repo_root=root)

    def test_holdout_load_and_manifest(self):
        with tempfile.TemporaryDirectory() as repo, tempfile.TemporaryDirectory() as secret:
            p = Path(secret) / "hidden.json"
            p.write_text(json.dumps({"suite_id":"h","cases":[{"id":"1","prompt":"3","type":"numeric","expected":3}]}))
            suite, manifest = load_private_holdout(p, repo_root=repo)
            self.assertEqual(manifest.case_count, 1)
            self.assertEqual(suite.run("c", lambda x: x).score, 1.0)

    def test_repeated_eval(self):
        suite = EvalSuite("r", [EvalCase("1", "x", exact_match("x"))])
        out = run_repeated(suite, "c", lambda seed: (lambda p: p), runs=3)
        self.assertEqual(out.mean_score, 1.0)
        self.assertEqual(out.stdev_score, 0.0)

if __name__ == "__main__": unittest.main()
