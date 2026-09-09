import json
import tempfile
import unittest
from pathlib import Path

from seed.gate1.local_scoring import extract_final, score_answer, score_local_campaign


class LocalScoringTests(unittest.TestCase):
    def test_extracts_last_final(self):
        self.assertEqual(extract_final("x\nFINAL: wrong\ny\nFINAL: 20 | A-C-E-G-I"), "20 | A-C-E-G-I")

    def test_semantic_delimiter_spacing_is_normalized(self):
        self.assertEqual(score_answer("FINAL: A = 83.00, B = 238.50", ["A=83.00,B=238.50"]), 1.0)

    def test_campaign_scores_with_external_key(self):
        with tempfile.TemporaryDirectory() as td:
            evidence = Path(td) / "evidence.json"
            answers = Path(td) / "answers.json"
            evidence.write_text(json.dumps({
                "suite_id":"s","content_hash":"abc","pairs":[
                    {"raw":{"task_id":"T1","answer":"FINAL: no"},"seed":{"task_id":"T1","answer":"FINAL: yes"}},
                    {"raw":{"task_id":"T2","answer":"FINAL: ok"},"seed":{"task_id":"T2","answer":"FINAL: ok"}}
                ]}), encoding="utf-8")
            answers.write_text(json.dumps({"suite_id":"s","answers":{"T1":["yes"],"T2":["ok"]}}), encoding="utf-8")
            report = score_local_campaign(evidence, answers)
            self.assertEqual(report["raw_mean"], 0.5)
            self.assertEqual(report["seed_mean"], 1.0)
            self.assertEqual(len(report["content_hash"]), 64)


if __name__ == "__main__":
    unittest.main()
