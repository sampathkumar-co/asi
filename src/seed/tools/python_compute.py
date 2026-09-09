from __future__ import annotations

import ast
import json
import subprocess
import sys
from typing import Any

from .registry import ToolResult

_MAX_CODE_CHARS = 4000
_MAX_AST_NODES = 600
_TIMEOUT_SECONDS = 2.0

_FORBIDDEN = (
    ast.Import, ast.ImportFrom, ast.Attribute, ast.ClassDef, ast.With, ast.AsyncWith,
    ast.Try, ast.Raise, ast.Global, ast.Nonlocal, ast.Delete, ast.Await,
    ast.Yield, ast.YieldFrom,
)

_RUNNER = r'''
import json, sys
from itertools import permutations, combinations, product
SAFE = {
    "abs": abs, "all": all, "any": any, "bool": bool, "dict": dict,
    "enumerate": enumerate, "float": float, "int": int, "len": len,
    "list": list, "max": max, "min": min, "range": range,
    "reversed": reversed, "round": round, "set": set, "sorted": sorted,
    "str": str, "sum": sum, "tuple": tuple, "zip": zip,
    "permutations": permutations, "combinations": combinations, "product": product,
}
payload = json.loads(sys.stdin.read())
ns = {"__builtins__": SAFE}
exec(payload["code"], ns, ns)
if "result" not in ns:
    raise RuntimeError("code must assign a JSON-serializable value to result")
print(json.dumps(ns["result"], ensure_ascii=False, separators=(",", ":")))
'''


def _validate(code: str) -> None:
    if not code or len(code) > _MAX_CODE_CHARS:
        raise ValueError("code must be 1..4000 characters")
    tree = ast.parse(code, mode="exec")
    nodes = list(ast.walk(tree))
    if len(nodes) > _MAX_AST_NODES:
        raise ValueError("code is too complex")
    for node in nodes:
        if isinstance(node, _FORBIDDEN):
            raise ValueError(f"unsupported syntax: {type(node).__name__}")
        if isinstance(node, ast.Name) and "__" in node.id:
            raise ValueError("dunder names are forbidden")
        if isinstance(node, ast.FunctionDef):
            if node.decorator_list or "__" in node.name:
                raise ValueError("decorated/dunder functions are forbidden")


def python_compute(payload: dict[str, Any]) -> ToolResult:
    code = str(payload.get("code", ""))
    try:
        _validate(code)
        proc = subprocess.run(
            [sys.executable, "-I", "-S", "-c", _RUNNER],
            input=json.dumps({"code": code}),
            capture_output=True,
            text=True,
            timeout=_TIMEOUT_SECONDS,
            check=False,
        )
        if proc.returncode != 0:
            error = (proc.stderr or proc.stdout or "python_compute failed").strip()
            return ToolResult(False, error=error[-1000:])
        value = json.loads(proc.stdout)
        return ToolResult(True, output=value)
    except subprocess.TimeoutExpired:
        return ToolResult(False, error="python_compute timed out")
    except Exception as exc:
        return ToolResult(False, error=str(exc))
