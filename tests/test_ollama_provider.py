import io
import json
import unittest
from unittest.mock import patch

from seed.providers.base import Message
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
            with self.assertRaises(RuntimeError):
                provider.complete([Message("user", "x")], purpose="raw")

    def test_empty_model_rejected(self):
        with self.assertRaises(ValueError):
            OllamaProvider("  ")


if __name__ == "__main__":
    unittest.main()
