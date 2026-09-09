import json
import tempfile
import unittest
from pathlib import Path

from seed.gate1.local_campaign import load_local_tasks, run_local_pair
from seed.providers.scripted import ScriptedProvider


class LocalCampaignTests(unittest.TestCase):
    def test_pair_uses_same_envelope_and_hashes(self):
        task_file = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        json.dump({"suite_id": "s", "tasks": [{"task_id": "T", "prompt": "Return FINAL: 4", "success_criteria": ["answer 4"]}]}, task_file)
        task_file.close()
        _, tasks = load_local_tasks(task_file.name)
        providers = iter([
            ScriptedProvider(["FINAL: 4"]),
            ScriptedProvider([
                '{"description":"candidate","tool_name":"echo","tool_input":{"text":"FINAL: 4"}}',
                '{"done":true,"confidence":0.95,"reason":"candidate present","final_answer":"FINAL: 4"}',
            ]),
        ])
        pair = run_local_pair(tasks[0], lambda: next(providers), provider_id="ollama:test-model")
        self.assertEqual(pair.raw.limits, pair.seed.limits)
        self.assertEqual(pair.raw.answer, "FINAL: 4")
        self.assertEqual(pair.seed.answer, "FINAL: 4")
        self.assertEqual(len(pair.content_hash), 64)
        Path(task_file.name).unlink(missing_ok=True)

    def test_duplicate_tasks_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "tasks.json"
            path.write_text(json.dumps({"suite_id":"s","tasks":[
                {"task_id":"T","prompt":"a"},{"task_id":"T","prompt":"b"}
            ]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_local_tasks(path)


if __name__ == "__main__":
    unittest.main()
