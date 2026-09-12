import unittest

from seed.gate2.qualification import run_gate2_qualification


class Gate2QualificationTests(unittest.TestCase):
    def test_all_gate2_protocol_canaries_pass(self):
        certificate = run_gate2_qualification()
        self.assertTrue(certificate.passed)
        self.assertEqual(certificate.evidence["check_count"], 36)
        self.assertTrue(all(certificate.checks.values()))

    def test_qualification_is_deterministic(self):
        first = run_gate2_qualification()
        second = run_gate2_qualification()
        self.assertEqual(first.content_hash, second.content_hash)
        self.assertEqual(first.to_dict(), second.to_dict())


if __name__ == "__main__":
    unittest.main()
