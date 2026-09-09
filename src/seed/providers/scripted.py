from __future__ import annotations

from collections import deque

from .base import Message, ModelResponse


class ScriptedProvider:
    """Deterministic provider for tests and reproducible demos."""

    def __init__(self, responses: list[str]) -> None:
        self._responses = deque(responses)

    def complete(self, messages: list[Message], *, purpose: str) -> ModelResponse:
        if not self._responses:
            raise RuntimeError(f"No scripted response left for purpose={purpose}")
        text = self._responses.popleft()
        return ModelResponse(text=text, input_tokens=sum(len(m.content.split()) for m in messages), output_tokens=len(text.split()))
