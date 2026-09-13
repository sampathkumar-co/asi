import io
import json
import unittest
from unittest.mock import patch

from seed.providers.base import Message, ProviderError
from seed.providers.ollama import OllamaProvider


class OllamaProviderTests(unittest.TestCase):
    @staticmethod
    def _response(content: str = '{"ok":true}') -> io.BytesIO:
        body = {
            "model": "qwen-local",
            "message": {"role": "assistant", "content": content},
            "prompt_eval_count": 17,
            "eval_count": 9,
            "done_reason": "stop",
            "total_duration": 123,
            "load_duration": 7,
        }
        return io.BytesIO(json.dumps(body).encode("utf-8"))

    def test_plan_uses_bounded_json_schema_and_reports_usage(self):
        provider = OllamaProvider("qwen-local", temperature=0, num_ctx=2048, num_predict=128)
        with patch("seed.providers.ollama.urlopen", return_value=self._response()) as mocked:
            result = provider.complete([Message("user", "plan")], purpose="plan")
        request = mocked.call_args.args[0]
        payload = json.loads(request.data)
        self.assertIsInstance(payload["format"], dict)
        self.assertEqual(payload["format"]["type"], "object")
        self.assertEqual(payload["format"]["properties"]["description"]["maxLength"], 160)
        self.assertFalse(payload["think"])
        self.assertEqual(payload["options"]["temperature"], 0.0)
        self.assertEqual(result.total_tokens, 26)
        self.assertEqual(result.cost_usd, 0.0)
        self.assertEqual(result.metadata["model"], "qwen-local")

    def test_purpose_specific_output_limit_overrides_default(self):
        provider = OllamaProvider("qwen-local", num_predict=768, purpose_num_predict={"critic": 128})
        with patch("seed.providers.ollama.urlopen", return_value=self._response()) as mocked:
            provider.complete([Message("user", "critic")], purpose="critic")
        payload = json.loads(mocked.call_args.args[0].data)
        self.assertEqual(payload["options"]["num_predict"], 128)

    def test_critic_schema_bounds_reason(self):
        provider = OllamaProvider("qwen-local")
        with patch("seed.providers.ollama.urlopen", return_value=self._response()) as mocked:
            provider.complete([Message("user", "critic")], purpose="critic")
        payload = json.loads(mocked.call_args.args[0].data)
        self.assertEqual(payload["format"]["properties"]["reason"]["maxLength"], 240)
        self.assertEqual(payload["format"]["properties"]["confidence"]["maximum"], 1)

    def test_raw_eval_allows_bounded_scratch_and_answer(self):
        provider = OllamaProvider("qwen-local")
        content = '{"analysis":"checked constraints","answer":"FINAL: x"}'
        with patch("seed.providers.ollama.urlopen", return_value=self._response(content)) as mocked:
            result = provider.complete([Message("user", "solve")], purpose="raw_eval")
        payload = json.loads(mocked.call_args.args[0].data)
        self.assertEqual(payload["format"]["required"], ["analysis", "answer"])
        self.assertEqual(payload["format"]["properties"]["analysis"]["maxLength"], 6000)
        self.assertEqual(payload["format"]["properties"]["answer"]["maxLength"], 512)
        self.assertEqual(result.text, content)

    def test_raw_call_does_not_force_json(self):
        provider = OllamaProvider("qwen-local")
        with patch("seed.providers.ollama.urlopen", return_value=self._response("FINAL: x")) as mocked:
            result = provider.complete([Message("user", "solve")], purpose="raw")
        payload = json.loads(mocked.call_args.args[0].data)
        self.assertNotIn("format", payload)
        self.assertEqual(result.text, "FINAL: x")

    def test_missing_content_fails_closed(self):
        provider = OllamaProvider("qwen-local")
        bad = io.BytesIO(json.dumps({"model": "qwen-local", "message": {}}).encode("utf-8"))
        with patch("seed.providers.ollama.urlopen", return_value=bad):
            with self.assertRaises(ProviderError):
                provider.complete([Message("user", "x")], purpose="raw")

    def test_transport_failure_is_provider_error(self):
        provider = OllamaProvider("qwen-local")
        with patch("seed.providers.ollama.urlopen", side_effect=OSError("connection reset")):
            with self.assertRaises(ProviderError) as caught:
                provider.complete([Message("user", "x")], purpose="raw")
        self.assertIn("Ollama request failed", str(caught.exception))

    def _gate2_payload(self, purpose: str) -> dict:
        purposes = {
            "gate2_raw_action", "gate2_raw_final", "gate2_seed_attribute_outcomes",
            "gate2_seed_design", "gate2_seed_final", "gate2_independent",
            "gate2_adversarial", "gate2_repair",
        }
        provider = OllamaProvider("qwen-local", json_purposes=purposes)
        return provider._payload([Message("user", "x")], purpose)

    def test_gate2_attribution_uses_nested_support_schema(self):
        fmt = self._gate2_payload("gate2_seed_attribute_outcomes")["format"]
        self.assertEqual(fmt["required"], ["outcome_support"])
        support = fmt["properties"]["outcome_support"]["additionalProperties"]["additionalProperties"]
        self.assertEqual(support["type"], "array")
        self.assertEqual(support["minItems"], 1)
        self.assertTrue(support["uniqueItems"])

    def test_gate2_action_and_design_schemas_are_explicit(self):
        action = self._gate2_payload("gate2_raw_action")["format"]
        self.assertIn("prediction_outcome_id", action["required"])
        self.assertEqual(action["properties"]["experiment_id"]["anyOf"][1]["type"], "null")
        design = self._gate2_payload("gate2_seed_design")["format"]
        self.assertEqual(design["required"], ["control_ids", "risk_ids", "reason"])

    def test_gate2_final_schema_bounds_confidence(self):
        raw = self._gate2_payload("gate2_raw_final")["format"]
        seed = self._gate2_payload("gate2_seed_final")["format"]
        self.assertEqual(raw, seed)
        self.assertEqual(raw["properties"]["confidence"]["minimum"], 0)
        self.assertEqual(raw["properties"]["confidence"]["maximum"], 1)

    def test_gate2_verifier_schema_requires_support_and_audit_fields(self):
        independent = self._gate2_payload("gate2_independent")["format"]
        adversarial = self._gate2_payload("gate2_adversarial")["format"]
        self.assertEqual(independent, adversarial)
        self.assertIn("supported_hypothesis_ids", independent["required"])
        self.assertEqual(independent["properties"]["supported_hypothesis_ids"]["minItems"], 1)
        self.assertEqual(independent["properties"]["confidence"]["maximum"], 1)

    def test_gate2_repair_stays_generic_for_stage_specific_shape(self):
        payload = self._gate2_payload("gate2_repair")
        self.assertEqual(payload["format"], "json")

    def test_gate2_preflight_is_task_independent_bounded_plain_text(self):
        provider = OllamaProvider("qwen-local", purpose_num_predict={"gate2_preflight": 8})
        with patch("seed.providers.ollama.urlopen", return_value=self._response("READY")) as mocked:
            result = provider.gate2_preflight()
        payload = json.loads(mocked.call_args.args[0].data)
        self.assertEqual(payload["options"]["num_predict"], 8)
        self.assertNotIn("format", payload)
        self.assertEqual(payload["messages"], [
            {"role": "system", "content": "Provider readiness probe. Reply with READY and no task reasoning."},
            {"role": "user", "content": "READY"},
        ])
        policy = provider.gate2_preflight_policy()
        self.assertTrue(policy["task_independent"])
        self.assertTrue(policy["outside_scored_envelope"])
        self.assertEqual(result["prompt_sha256"], policy["prompt_sha256"])
        self.assertEqual(result["output_tokens"], 9)

    def test_gate2_preflight_rejects_empty_content(self):
        provider = OllamaProvider("qwen-local", purpose_num_predict={"gate2_preflight": 8})
        with patch("seed.providers.ollama.urlopen", return_value=self._response("   ")):
            with self.assertRaises(ProviderError):
                provider.gate2_preflight()

    def test_empty_model_rejected(self):
        with self.assertRaises(ValueError):
            OllamaProvider("  ")

    def test_invalid_purpose_output_limit_rejected(self):
        with self.assertRaises(ValueError):
            OllamaProvider("qwen-local", purpose_num_predict={"critic": 0})


if __name__ == "__main__":
    unittest.main()
