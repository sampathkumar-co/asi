from __future__ import annotations

from math import gcd
from typing import Any

from .registry import ToolResult


def _combine(a: int, m: int, b: int, n: int) -> tuple[int, int]:
    g = gcd(m, n)
    delta = b - a
    if delta % g:
        raise ValueError("congruences are inconsistent")
    m1, n1 = m // g, n // g
    k = ((delta // g) * pow(m1, -1, n1)) % n1
    modulus = m * n1
    return (a + m * k) % modulus, modulus


def chinese_remainder(congruences: list[list[int] | tuple[int, int]]) -> dict[str, Any]:
    if not isinstance(congruences, list) or not congruences:
        raise ValueError("congruences must be a non-empty array")
    first = congruences[0]
    if not isinstance(first, (list, tuple)) or len(first) != 2:
        raise ValueError("each congruence must be [remainder, modulus]")
    a, m = int(first[0]), int(first[1])
    if m <= 0:
        raise ValueError("moduli must be positive")
    a %= m
    normalized = [[a, m]]
    for item in congruences[1:]:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise ValueError("each congruence must be [remainder, modulus]")
        b, n = int(item[0]), int(item[1])
        if n <= 0:
            raise ValueError("moduli must be positive")
        b %= n
        normalized.append([b, n])
        a, m = _combine(a, m, b, n)
    smallest_positive = a if a > 0 else m
    checks = {
        "all_congruences_hold": all(smallest_positive % mod == rem for rem, mod in normalized),
        "positive": smallest_positive > 0,
        "minimal_residue": 0 < smallest_positive <= m,
    }
    return {
        "solution": smallest_positive,
        "modulus": m,
        "normalized": normalized,
        "checks": checks,
    }


def crt_tool(payload: dict[str, Any]) -> ToolResult:
    try:
        congruences = payload.get("congruences")
        if not isinstance(congruences, list):
            raise ValueError("congruences is required")
        template = str(payload.get("answer_template", "FINAL: {solution}"))
        if len(template) > 256 or "{solution}" not in template:
            raise ValueError("answer_template must contain {solution}")
        data = chinese_remainder(congruences)
        answer = template.replace("{solution}", str(data["solution"]))
        return ToolResult(True, output={"answer": answer, "checks": data["checks"], "evidence": data})
    except Exception as exc:
        return ToolResult(False, error=str(exc))
