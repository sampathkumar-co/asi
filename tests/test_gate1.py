import json
import tempfile
import unittest
from pathlib import Path

from seed.gate1.comparison import ArmEvidence, ComparisonEvidence, within_limits
from seed.gate1.qualification import run_gate1_qualification, write_gate1_certificate


class Gate1Tests(unittest.TestCase):
    def test_gate1_qualification_passes(self):
        cert = run_gate1_qualification()
        self.assertTrue(cert.passed, cert.checks)
        self.assertTrue(all(cert.checks.values()))
        self.assertEqual(len(cert.content_hash), 64)

    def test_gate1_certificate_writes(self):
        cert = run_gate1_qualification()
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "g1.json"
            write_gate1_certificate(cert, path)
            self.assertTrue(json.loads(path.read_text())["passed"])

    def test_comparison_requires_same_envelope(self):
        a = ArmEvidence("raw", "m", 0, "succeeded", {"max_steps": 1, "max_model_calls": 1, "max_tool_calls": 1, "max_tokens": 10, "max_cost_usd": 1}, {"steps":0,"model_calls":1,"tool_calls":0,"tokens":1,"cost_usd":0}, "a")
        b = ArmEvidence("seed", "m", 1, "succeeded", {"max_steps": 2, "max_model_calls": 1, "max_tool_calls": 1, "max_tokens": 10, "max_cost_usd": 1}, {"steps":1,"model_calls":1,"tool_calls":1,"tokens":1,"cost_usd":0}, "b")
        self.assertFalse(ComparisonEvidence(a, b).same_envelope)

    def test_within_limits_rejects_overspend(self):
        a = ArmEvidence("raw", "m", 0, "failed", {"max_steps": 1, "max_model_calls": 1, "max_tool_calls": 0, "max_tokens": 1, "max_cost_usd": 0}, {"steps":0,"model_calls":2,"tool_calls":0,"tokens":1,"cost_usd":0}, "a")
        self.assertFalse(within_limits(a))


if __name__ == "__main__":
    unittest.main()
