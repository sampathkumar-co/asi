import tempfile
import unittest
from pathlib import Path

from seed.gate1.attestation import implementation_manifest


class Gate1AttestationTests(unittest.TestCase):
    def test_manifest_is_stable_and_content_addressed(self):
        first = implementation_manifest()
        second = implementation_manifest()
        self.assertEqual(first, second)
        self.assertEqual(len(first["digest"]), 64)
        self.assertGreater(first["file_count"], 5)
        self.assertEqual(first["file_count"], len(first["files"]))

    def test_manifest_changes_when_attested_file_changes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for relative in (
                "src/seed/agent/x.py",
                "src/seed/tools/x.py",
                "src/seed/core/budget.py",
                "src/seed/core/events.py",
                "src/seed/core/models.py",
                "src/seed/providers/base.py",
                "src/seed/providers/budgeted.py",
                "src/seed/providers/ollama.py",
                "src/seed/gate1/attestation.py",
                "src/seed/gate1/local_campaign.py",
            ):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("x=1\n", encoding="utf-8")
            before = implementation_manifest(root)["digest"]
            (root / "src/seed/agent/x.py").write_text("x=2\n", encoding="utf-8")
            after = implementation_manifest(root)["digest"]
            self.assertNotEqual(before, after)


if __name__ == "__main__":
    unittest.main()
