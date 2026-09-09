import tempfile, unittest
from pathlib import Path
from seed.selfmod.policy import FileMutation, PatchPolicy, PatchProposal, sha256_text
from seed.selfmod.descendant import DescendantBuilder
from seed.selfmod.promotion import PromotionEvidence, decide_promotion
from seed.selfmod.sandbox import DockerSandbox

class SelfModTests(unittest.TestCase):
    def proposal(self, path, content="new", expected=None):
        return PatchProposal("p1", "parent", "test", (FileMutation(path, expected, content),))

    def test_policy_allows_agent_code(self):
        self.assertTrue(PatchPolicy().validate(self.proposal("src/seed/agent/x.py")).allowed)

    def test_policy_blocks_evaluator(self):
        decision = PatchPolicy().validate(self.proposal("src/seed/eval/suite.py"))
        self.assertFalse(decision.allowed)
        self.assertTrue(any("forbidden" in x for x in decision.reasons))

    def test_policy_blocks_traversal(self):
        self.assertFalse(PatchPolicy().validate(self.proposal("../escape.py")).allowed)

    def test_descendant_is_copy_not_parent_mutation(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d) / "base"
            f = base / "src/seed/agent/x.py"
            f.parent.mkdir(parents=True)
            f.write_text("old", encoding="utf-8")
            prop = self.proposal("src/seed/agent/x.py", "new", sha256_text("old"))
            child = DescendantBuilder(base).build(prop)
            self.assertEqual(f.read_text(), "old")
            self.assertEqual((child.path / "src/seed/agent/x.py").read_text(), "new")

    def test_stale_mutation_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d) / "base"; f = base / "src/seed/agent/x.py"; f.parent.mkdir(parents=True); f.write_text("old")
            with self.assertRaises(RuntimeError): DescendantBuilder(base).build(self.proposal("src/seed/agent/x.py", "new", "bad"))

    def test_promotion_gate(self):
        yes = decide_promotion(PromotionEvidence(0.70, 0.75, 0.78, True, True))
        no = decide_promotion(PromotionEvidence(0.70, 0.71, 0.90, True, True))
        self.assertTrue(yes.promote); self.assertFalse(no.promote)

    def test_docker_command_disables_network(self):
        cmd = DockerSandbox().command(".")
        self.assertIn("none", cmd)
        self.assertIn("--read-only", cmd)
        self.assertIn("no-new-privileges", cmd)

if __name__ == "__main__": unittest.main()
