from __future__ import annotations

import json
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .base import Message, ModelResponse


class OllamaProvider:
    """Local Ollama adapter for real Gate-1 experiments.

    The adapter is intentionally dependency-free and reports Ollama's own
    prompt/evaluation token counters. Structured JSON mode is enabled only for
    planner/critic calls, where Seed's protocol requires machine-readable JSON.
    """

    def __init__(
        self,
        model: str,
        *,
        base_url: str = "http://127.0.0.1:11434",
        timeout_s: float = 180.0,
        temperature: float = 0.0,
        num_ctx: int = 4096,
        num_predict: int = 256,
        think: bool = False,
        json_purposes: Iterable[str] = ("plan", "critic"),
    ) -> None:
        if not model.strip():
            raise ValueError("Ollama model name must be non-empty")
        if timeout_s <= 0 or num_ctx <= 0 or num_predict <= 0:
            raise ValueError("Ollama timeout/context/output limits must be positive")
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_s = float(timeout_s)
        self.temperature = float(temperature)
        self.num_ctx = int(num_ctx)
        self.num_predict = int(num_predict)
        self.think = bool(think)
        self.json_purposes = frozenset(json_purposes)

    @property
    def provider_id(self) -> str:
        return f"ollama:{self.model}"

    def _payload(self, messages: list[Message], purpose: str) -> dict:
        payload: dict = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": False,
            "think": self.think,
            "options": {
                "temperature": self.temperature,
                "num_ctx": self.num_ctx,
                "num_predict": self.num_predict,
            },
        }
        if purpose in self.json_purposes:
            payload["format"] = "json"
        return payload

    def complete(self, messages: list[Message], *, purpose: str) -> ModelResponse:
        request = Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(self._payload(messages, purpose)).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout_s) as response:
                data = json.load(response)
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            raise RuntimeError(f"Ollama request failed: {exc}") from exc

        message = data.get("message")
        text = message.get("content") if isinstance(message, dict) else None
        if not isinstance(text, str):
            raise RuntimeError("Ollama response missing message.content")

        def _count(name: str) -> int:
            value = data.get(name, 0)
            return max(int(value), 0) if isinstance(value, (int, float)) else 0

        metadata = {
            "model": str(data.get("model", self.model)),
            "purpose": purpose,
            "done_reason": str(data.get("done_reason", "")),
            "total_duration_ns": str(data.get("total_duration", 0)),
            "load_duration_ns": str(data.get("load_duration", 0)),
        }
        return ModelResponse(
            text=text,
            input_tokens=_count("prompt_eval_count"),
            output_tokens=_count("eval_count"),
            cost_usd=0.0,
            metadata=metadata,
        )
