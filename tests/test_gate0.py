import tempfile
import unittest
from pathlib import Path

from seed.eval.gate0 import run_gate0_qualification, write_gate0_certificate


class Gate0QualificationTests(unittest.TestCase):
    def test_full_gate0_qualification_passes(self):
        repo = Path(__file__).resolve().parents[1]
        cert = run_gate0_qualification(repo)
        self.assertTrue(cert.passed, cert.checks)
        self.assertTrue(all(cert.checks.values()))
        self.assertEqual(cert.qualification, "gate0-infrastructure-v1")
        self.assertEqual(len(cert.content_hash), 64)

    def test_certificate_writes(self):
        repo = Path(__file__).resolve().parents[1]
        cert = run_gate0_qualification(repo)
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "gate0.json"
            write_gate0_certificate(cert, path)
            self.assertIn('"passed": true', path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
