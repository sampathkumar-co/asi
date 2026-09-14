import unittest
from pathlib import Path
from unittest.mock import patch

from seed.gate2.local_campaign import _budget, _run_arm
from seed.gate2.schema import load_research_tasks
from seed.providers.base import ProviderError
from seed.providers.budgeted import BudgetedProvider
from seed.providers.scripted import ScriptedProvider


class _FailingProvider:
    def complete(self, messages, *, purpose):
        raise ProviderError("transport unavailable")


class Gate2FailureClassificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1]
        _, tasks = load_research_tasks(root / "configs/gate2_public_calibration_v1.json")
        cls.task = tasks[0]

    @staticmethod
    def meter(inner):
        budget = _budget()
        return BudgetedProvider(inner, budget, provider_id="ollama:qwen3:8b"), budget
    def test_provider_error_is_campaign_infrastructure_failure(self):
        meter, budget = self.meter(_FailingProvider())
        arm = _run_arm(self.task, meter, budget, "raw")
        self.assertEqual(arm.status, "infrastructure_error")
        self.assertEqual(arm.failure_kind, "provider")
        self.assertIn("transport unavailable", arm.failure_message)
        self.assertEqual(arm.usage["model_calls"], 0)

    def test_trusted_runner_value_error_is_runner_failure(self):
        meter, budget = self.meter(ScriptedProvider([]))
        with patch("seed.gate2.local_campaign._attribute_outcomes", return_value={}), \
             patch("seed.gate2.local_campaign._validated_attribution", return_value=()), \
             patch("seed.gate2.local_campaign._canonical_matrices", side_effect=ValueError("trusted runner defect")):
            arm = _run_arm(self.task, meter, budget, "seed")
        self.assertEqual(arm.status, "failed:ValueError")
        self.assertEqual(arm.failure_kind, "runner")
        self.assertIn("trusted runner defect", arm.failure_message)
    def test_invalid_model_output_after_repair_is_model_protocol_failure(self):
        meter, budget = self.meter(ScriptedProvider([]))
        malformed = {"outcome_support": {}}
        with patch("seed.gate2.local_campaign._attribute_outcomes", return_value=malformed), \
             patch("seed.gate2.local_campaign._repair_schema", return_value=malformed) as repair:
            arm = _run_arm(self.task, meter, budget, "seed")
        self.assertEqual(arm.status, "failed:ModelProtocolError")
        self.assertEqual(arm.failure_kind, "model_protocol")
        self.assertIn("attribution must cover", arm.failure_message)
        self.assertEqual(repair.call_count, 2)
        self.assertEqual(len(arm.repair_events), 2)


if __name__ == "__main__":
    unittest.main()
