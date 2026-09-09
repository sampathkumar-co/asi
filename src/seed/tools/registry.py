from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class ToolResult:
    ok: bool
    output: Any = None
    error: str | None = None


ToolFn = Callable[[dict[str, Any]], ToolResult]


class ToolRegistry:
    """Explicit allowlist: an agent can call only tools registered here."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolFn] = {}

    def register(self, name: str, fn: ToolFn) -> None:
        if not name or name in self._tools:
            raise ValueError(f"Invalid or duplicate tool name: {name!r}")
        self._tools[name] = fn

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._tools))

    def call(self, name: str, payload: dict[str, Any]) -> ToolResult:
        fn = self._tools.get(name)
        if fn is None:
            return ToolResult(False, error=f"Tool not allowed: {name}")
        try:
            return fn(payload)
        except Exception as exc:  # tool failures become observations, not process crashes
            return ToolResult(False, error=f"{type(exc).__name__}: {exc}")
