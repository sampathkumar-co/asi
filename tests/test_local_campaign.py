import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from seed.gate1.local_campaign import (
    LocalArmEvidence,
    LocalPairEvidence,
    load_local_tasks,
    run_local_pair,
    run_ollama_suite,
)
from seed.providers.scripted import ScriptedProvider


class LocalCampaignTests(unittest.TestCase):
    def test_pair_uses_same_envelope_and_hashes(self):
        task_file = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        json.dump({"suite_id": "s", "tasks": [{"task_id": "T", "prompt": "Return FINAL: 4", "success_criteria": ["answer 4"]}]}, task_file)
        task_file.close()
        _, tasks = load_local_tasks(task_file.name)
        providers = iter([
            ScriptedProvider(['{"analysis":"2+2=4","answer":"FINAL: 4"}']),
            ScriptedProvider([
                '{"description":"compute verified candidate","tool_name":"python_compute","tool_input":{"code":"result={\'answer\':\'FINAL: 4\',\'checks\':{\'arithmetic\':True}}"}}',
                '{"done":true,"confidence":0.95,"reason":"verified candidate present","final_answer":"FINAL: 4"}',
            ]),
        ])
        pair = run_local_pair(tasks[0], lambda: next(providers), provider_id="ollama:test-model")
        self.assertEqual(pair.raw.limits, pair.seed.limits)
        self.assertEqual(pair.raw.answer, "FINAL: 4")
        self.assertEqual(pair.seed.answer, "FINAL: 4")
        self.assertEqual(len(pair.content_hash), 64)
        Path(task_file.name).unlink(missing_ok=True)

    def test_checkpoint_resumes_without_rerunning_completed_pairs(self):
        with tempfile.TemporaryDirectory() as td:
            tasks = Path(td) / "tasks.json"
            checkpoint = Path(td) / "evidence.json"
            tasks.write_text(json.dumps({"suite_id":"s","tasks":[
                {"task_id":"T1","prompt":"one"},{"task_id":"T2","prompt":"two"}
            ]}), encoding="utf-8")

            def fake_pair(task, factory, *, provider_id, progress=None):
                limits = {"max_steps":8,"max_model_calls":12,"max_tool_calls":8,"max_tokens":8000,"max_cost_usd":0.0}
                usage = {"steps":1,"model_calls":1,"tool_calls":0,"tokens":10,"cost_usd":0.0}
                raw = LocalArmEvidence(task.task_id, "raw", provider_id, "m", f"FINAL: {task.task_id}", "succeeded", limits, usage, "a"*64)
                seed = LocalArmEvidence(task.task_id, "seed", provider_id, "m", f"FINAL: {task.task_id}", "succeeded", limits, usage, "b"*64)
                if progress:
                    progress({"event":"fake","task_id":task.task_id})
                return LocalPairEvidence(raw, seed)

            manifest = {"name":"m","digest":"d"*64,"size":1}
            patches = (
                patch("seed.gate1.local_campaign.OllamaProvider.model_manifest", return_value=manifest),
                patch("seed.gate1.local_campaign.run_local_pair", side_effect=fake_pair),
            )
            with patches[0], patches[1] as run:
                first = run_ollama_suite(tasks, "m", checkpoint_path=checkpoint)
                self.assertEqual(run.call_count, 2)
                self.assertEqual(len(first["pairs"]), 2)
                self.assertTrue(checkpoint.exists())
                self.assertTrue(checkpoint.with_suffix(".json.progress.jsonl").exists())

            with patch("seed.gate1.local_campaign.OllamaProvider.model_manifest", return_value=manifest), patch("seed.gate1.local_campaign.run_local_pair", side_effect=fake_pair) as run:
                second = run_ollama_suite(tasks, "m", checkpoint_path=checkpoint)
                self.assertEqual(run.call_count, 0)
                self.assertEqual(first["content_hash"], second["content_hash"])

            tampered = json.loads(checkpoint.read_text(encoding="utf-8"))
            tampered["seed_implementation"]["digest"] = "0" * 64
            checkpoint.write_text(json.dumps(tampered), encoding="utf-8")
            with patch("seed.gate1.local_campaign.OllamaProvider.model_manifest", return_value=manifest):
                with self.assertRaises(ValueError):
                    run_ollama_suite(tasks, "m", checkpoint_path=checkpoint)

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
