import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from seed.gate2.local_campaign import run_ollama_research_suite
from seed.providers.base import ProviderError
from seed.providers.ollama import OllamaProvider


_MANIFEST = {"name": "qwen", "digest": "d" * 64, "size": 1}
_IMPLEMENTATION = {"digest": "i" * 64, "file_count": 0, "files": []}


class Gate2PreflightTests(unittest.TestCase):
    @staticmethod
    def task_file(root: str) -> Path:
        path = Path(root) / "tasks.json"
        path.write_text("{}\n", encoding="utf-8")
        return path

    @staticmethod
    def events(path: Path) -> list[dict]:
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]

    def test_preflight_failure_aborts_before_pair_and_hashes_detail(self):
        with tempfile.TemporaryDirectory() as td:
            task_path = self.task_file(td)
            progress = Path(td) / "progress.jsonl"
            fake_task = SimpleNamespace(task_id="T1")
            with patch("seed.gate2.local_campaign.load_research_tasks", return_value=("suite", [fake_task])), \
                 patch.object(OllamaProvider, "model_manifest", return_value=_MANIFEST), \
                 patch("seed.gate2.local_campaign.implementation_manifest", return_value=_IMPLEMENTATION), \
                 patch.object(OllamaProvider, "gate2_preflight", side_effect=ProviderError("CUDA init failed")) as preflight, \
                 patch("seed.gate2.local_campaign.run_research_pair") as run_pair:
                with self.assertRaises(ProviderError):
                    run_ollama_research_suite(task_path, "qwen", progress_path=progress)
            preflight.assert_called_once_with()
            run_pair.assert_not_called()
            events = self.events(progress)
            self.assertEqual([e["event"] for e in events], ["provider_preflight_failed"])
            self.assertEqual(events[0]["failure_message_sha256"], hashlib.sha256(b"CUDA init failed").hexdigest())
            self.assertNotIn("CUDA init failed", progress.read_text(encoding="utf-8"))

    def test_successful_preflight_precedes_pair_start(self):
        with tempfile.TemporaryDirectory() as td:
            task_path = self.task_file(td)
            progress = Path(td) / "progress.jsonl"
            fake_task = SimpleNamespace(task_id="T1")
            policy = OllamaProvider.gate2_preflight_policy()
            order: list[str] = []

            def preflight():
                order.append("preflight")
                return {"purpose": "gate2_preflight", "prompt_sha256": policy["prompt_sha256"],
                        "response_sha256": "r" * 64, "input_tokens": 3, "output_tokens": 1}

            def stop_pair(*args, **kwargs):
                order.append("pair")
                raise RuntimeError("stop after ordering check")

            with patch("seed.gate2.local_campaign.load_research_tasks", return_value=("suite", [fake_task])), \
                 patch.object(OllamaProvider, "model_manifest", return_value=_MANIFEST), \
                 patch("seed.gate2.local_campaign.implementation_manifest", return_value=_IMPLEMENTATION), \
                 patch.object(OllamaProvider, "gate2_preflight", side_effect=preflight), \
                 patch("seed.gate2.local_campaign.run_research_pair", side_effect=stop_pair):
                with self.assertRaisesRegex(RuntimeError, "ordering check"):
                    run_ollama_research_suite(task_path, "qwen", progress_path=progress)
            self.assertEqual(order, ["preflight", "pair"])
            self.assertEqual([e["event"] for e in self.events(progress)],
                             ["provider_preflight_passed", "pair_started"])

    def test_preflight_policy_is_attested_in_settings(self):
        with tempfile.TemporaryDirectory() as td:
            task_path = self.task_file(td)
            policy = OllamaProvider.gate2_preflight_policy()
            with patch("seed.gate2.local_campaign.load_research_tasks", return_value=("suite", [])), \
                 patch.object(OllamaProvider, "model_manifest", return_value=_MANIFEST), \
                 patch("seed.gate2.local_campaign.implementation_manifest", return_value=_IMPLEMENTATION), \
                 patch.object(OllamaProvider, "gate2_preflight") as preflight:
                result = run_ollama_research_suite(task_path, "qwen")
            preflight.assert_not_called()
            self.assertEqual(result["settings"]["provider_preflight"], policy)
            self.assertEqual(result["settings"]["purpose_num_predict"]["gate2_preflight"], 8)

    def test_completed_resume_skips_preflight(self):
        with tempfile.TemporaryDirectory() as td:
            task_path = self.task_file(td)
            checkpoint = Path(td) / "evidence.json"
            checkpoint.write_text(json.dumps({"pairs": [{"raw": {"task_id": "T1"}, "seed": {"task_id": "T1"}}]}), encoding="utf-8")
            fake_task = SimpleNamespace(task_id="T1")
            with patch("seed.gate2.local_campaign.load_research_tasks", return_value=("suite", [fake_task])), \
                 patch.object(OllamaProvider, "model_manifest", return_value=_MANIFEST), \
                 patch("seed.gate2.local_campaign.implementation_manifest", return_value=_IMPLEMENTATION), \
                 patch("seed.gate2.local_campaign.validate_checkpoint_identity"), \
                 patch.object(OllamaProvider, "gate2_preflight") as preflight, \
                 patch("seed.gate2.local_campaign.run_research_pair") as run_pair:
                run_ollama_research_suite(task_path, "qwen", checkpoint_path=checkpoint)
            preflight.assert_not_called()
            run_pair.assert_not_called()

    def test_invalid_checkpoint_is_rejected_before_preflight(self):
        with tempfile.TemporaryDirectory() as td:
            task_path = self.task_file(td)
            checkpoint = Path(td) / "evidence.json"
            checkpoint.write_text(json.dumps({"pairs": []}), encoding="utf-8")
            fake_task = SimpleNamespace(task_id="T1")
            with patch("seed.gate2.local_campaign.load_research_tasks", return_value=("suite", [fake_task])), \
                 patch.object(OllamaProvider, "model_manifest", return_value=_MANIFEST), \
                 patch("seed.gate2.local_campaign.implementation_manifest", return_value=_IMPLEMENTATION), \
                 patch("seed.gate2.local_campaign.validate_checkpoint_identity", side_effect=ValueError("bad checkpoint")), \
                 patch.object(OllamaProvider, "gate2_preflight") as preflight:
                with self.assertRaisesRegex(ValueError, "bad checkpoint"):
                    run_ollama_research_suite(task_path, "qwen", checkpoint_path=checkpoint)
            preflight.assert_not_called()


    def test_incomplete_resume_preflights_before_next_pair(self):
        with tempfile.TemporaryDirectory() as td:
            task_path = self.task_file(td)
            checkpoint = Path(td) / "evidence.json"
            checkpoint.write_text(json.dumps({"pairs": [{"raw": {"task_id": "T1"}, "seed": {"task_id": "T1"}}]}), encoding="utf-8")
            progress = Path(td) / "progress.jsonl"
            tasks = [SimpleNamespace(task_id="T1"), SimpleNamespace(task_id="T2")]
            policy = OllamaProvider.gate2_preflight_policy()
            preflight_result = {"purpose": "gate2_preflight", "prompt_sha256": policy["prompt_sha256"],
                                "response_sha256": "r" * 64, "input_tokens": 3, "output_tokens": 1}
            with patch("seed.gate2.local_campaign.load_research_tasks", return_value=("suite", tasks)), \
                 patch.object(OllamaProvider, "model_manifest", return_value=_MANIFEST), \
                 patch("seed.gate2.local_campaign.implementation_manifest", return_value=_IMPLEMENTATION), \
                 patch("seed.gate2.local_campaign.validate_checkpoint_identity"), \
                 patch.object(OllamaProvider, "gate2_preflight", return_value=preflight_result) as preflight, \
                 patch("seed.gate2.local_campaign.run_research_pair", side_effect=RuntimeError("stop resumed pair")) as run_pair:
                with self.assertRaisesRegex(RuntimeError, "stop resumed pair"):
                    run_ollama_research_suite(task_path, "qwen", checkpoint_path=checkpoint, progress_path=progress)
            preflight.assert_called_once_with()
            self.assertEqual(run_pair.call_args.args[0].task_id, "T2")
            events = self.events(progress)
            self.assertEqual([e["event"] for e in events], ["provider_preflight_passed", "pair_started"])
            self.assertEqual(events[1]["task_id"], "T2")


if __name__ == "__main__":
    unittest.main()
