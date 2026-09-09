import unittest
from seed.science.protocol import *

class Runner:
    def run(self, plan):
        return ExperimentResult(plan.id, {"delta": 0.12}, reproducible=True)

class GoodVerifier:
    def __init__(self, name): self.name = name
    def verify(self, hypothesis, plan, result):
        return VerificationReport(self.name, Verdict.PASS, 0.9, ("replicated",))

class BadVerifier(GoodVerifier):
    def verify(self, hypothesis, plan, result):
        return VerificationReport(self.name, Verdict.FAIL, 0.95, ("confound",))

class ScienceTests(unittest.TestCase):
    def setUp(self):
        self.h = Hypothesis("X helps", "prior", ("no gain",))
        self.p = ExperimentPlan(self.h.id, "A/B", "+10%", "delta", ("same seed",))

    def test_accept_requires_two_verifiers(self):
        rec = ResearchCycle(Runner(), GoodVerifier("independent"), GoodVerifier("adversarial")).execute(self.h, self.p)
        self.assertTrue(rec.accepted)

    def test_adversarial_failure_blocks(self):
        rec = ResearchCycle(Runner(), GoodVerifier("independent"), BadVerifier("adversarial")).execute(self.h, self.p)
        self.assertFalse(rec.accepted)

    def test_verifiers_must_be_distinct(self):
        with self.assertRaises(ValueError): ResearchCycle(Runner(), GoodVerifier("same"), GoodVerifier("same"))

if __name__ == "__main__": unittest.main()
