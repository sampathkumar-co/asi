from __future__ import annotations

import ast
import json
import subprocess
import sys
from typing import Any

from .registry import ToolResult

_MAX_CODE_CHARS = 4000
_MAX_AST_NODES = 700
_TIMEOUT_SECONDS = 2.0
_ALLOWED_IMPORTS = {
    "collections": {"defaultdict", "deque"},
    "heapq": {"heappush", "heappop"},
    "itertools": {"permutations", "combinations", "product"},
}
_ALLOWED_ATTRIBUTES = {
    "append", "extend", "pop", "popleft", "get", "items", "keys", "values",
    "add", "discard", "remove", "sort", "reverse", "count", "index", "setdefault",
    "join",
}
_FORBIDDEN = (
    ast.Import, ast.ClassDef, ast.With, ast.AsyncWith, ast.Try, ast.Raise,
    ast.Global, ast.Nonlocal, ast.Delete, ast.Await, ast.Yield, ast.YieldFrom,
)

_RUNNER = r'''
import json, sys
from collections import defaultdict, deque
from heapq import heappush, heappop
from itertools import permutations, combinations, product


def dag_longest_path(weights, predecessors, target=None):
    if not isinstance(weights, dict) or not weights:
        raise ValueError("weights must be a non-empty dict")
    if not isinstance(predecessors, dict):
        raise ValueError("predecessors must be a dict")
    nodes = list(weights.keys())
    node_set = set(nodes)
    extra = set(predecessors.keys()) - node_set
    if extra:
        raise ValueError("predecessors contains unknown nodes")
    preds = {}
    for node in nodes:
        raw = predecessors.get(node, [])
        if not isinstance(raw, (list, tuple)):
            raise ValueError("each predecessor list must be a list or tuple")
        values = list(raw)
        if node in values or any(p not in node_set for p in values):
            raise ValueError("invalid predecessor reference")
        preds[node] = values
    successors = {node: [] for node in nodes}
    indegree = {node: len(preds[node]) for node in nodes}
    for node in nodes:
        for pred in preds[node]:
            successors[pred].append(node)
    ready = sorted([node for node in nodes if indegree[node] == 0], key=str)
    topo = []
    while ready:
        node = ready.pop(0)
        topo.append(node)
        for succ in sorted(successors[node], key=str):
            indegree[succ] -= 1
            if indegree[succ] == 0:
                ready.append(succ)
                ready.sort(key=str)
    if len(topo) != len(nodes):
        raise ValueError("graph must be acyclic")
    score = {}
    parent = {}
    for node in topo:
        if preds[node]:
            best = min(preds[node], key=lambda p: (-score[p], str(p)))
            score[node] = score[best] + weights[node]
            parent[node] = best
        else:
            score[node] = weights[node]
            parent[node] = None
    if target is None:
        target = min(nodes, key=lambda n: (-score[n], str(n)))
    if target not in node_set:
        raise ValueError("target must be a graph node")
    path = []
    cursor = target
    while cursor is not None:
        path.append(cursor)
        cursor = parent[cursor]
    path.reverse()
    path_weight = sum(weights[node] for node in path)
    path_edges_valid = all(path[i] in preds[path[i + 1]] for i in range(len(path) - 1))
    recurrence_valid = all(
        score[node] == weights[node] + (max(score[p] for p in preds[node]) if preds[node] else 0)
        for node in topo
    )
    return {
        "weight": score[target],
        "path": path,
        "topological_order": topo,
        "scores": score,
        "checks": {
            "acyclic": len(topo) == len(nodes),
            "target_reached": bool(path) and path[-1] == target,
            "path_edges_valid": path_edges_valid,
            "weight_matches_path": path_weight == score[target],
            "dynamic_program_valid": recurrence_valid,
        },
    }


SAFE = {
    "abs": abs, "all": all, "any": any, "bool": bool, "dict": dict,
    "enumerate": enumerate, "float": float, "int": int, "len": len,
    "list": list, "max": max, "min": min, "range": range,
    "reversed": reversed, "round": round, "set": set, "sorted": sorted,
    "str": str, "sum": sum, "tuple": tuple, "zip": zip,
    "defaultdict": defaultdict, "deque": deque,
    "heappush": heappush, "heappop": heappop,
    "permutations": permutations, "combinations": combinations, "product": product,
    "dag_longest_path": dag_longest_path,
}
payload = json.loads(sys.stdin.read())
ns = {"__builtins__": SAFE}
exec(payload["code"], ns, ns)
if "result" not in ns:
    raise RuntimeError("code must assign a JSON-serializable value to result")
print(json.dumps(ns["result"], ensure_ascii=False, separators=(",", ":")))
'''


class _SafeImportStripper(ast.NodeTransformer):
    def visit_ImportFrom(self, node: ast.ImportFrom):
        allowed = _ALLOWED_IMPORTS.get(node.module or "")
        if node.level != 0 or allowed is None:
            raise ValueError(f"unsupported import: {node.module}")
        for alias in node.names:
            if alias.asname or alias.name not in allowed:
                raise ValueError(f"unsupported import symbol: {alias.name}")
        return None


def _normalize_model_code(code: str) -> str:
    """Repair harmless serialization artifacts without changing program structure."""
    code = code.replace("\r\n", "\n").replace("\r", "\n")
    out: list[str] = []
    for line in code.split("\n"):
        trimmed = line.rstrip()
        trailing = len(trimmed) - len(trimmed.rstrip("\\"))
        if trailing >= 2:
            trimmed = trimmed[:-trailing] + "\\"
        out.append(trimmed if trailing else line)
    return "\n".join(out)


def _sanitize(code: str) -> str:
    code = _normalize_model_code(code)
    if not code or len(code) > _MAX_CODE_CHARS:
        raise ValueError("code must be 1..4000 characters")
    tree = ast.parse(code, mode="exec")
    nodes = list(ast.walk(tree))
    if len(nodes) > _MAX_AST_NODES:
        raise ValueError("code is too complex")
    for node in nodes:
        if isinstance(node, _FORBIDDEN):
            raise ValueError(f"unsupported syntax: {type(node).__name__}")
        if isinstance(node, ast.Attribute):
            if "__" in node.attr or node.attr not in _ALLOWED_ATTRIBUTES:
                raise ValueError(f"unsupported attribute: {node.attr}")
        if isinstance(node, ast.Name) and "__" in node.id:
            raise ValueError("dunder names are forbidden")
        if isinstance(node, ast.FunctionDef):
            if node.decorator_list or "__" in node.name:
                raise ValueError("decorated/dunder functions are forbidden")
    tree = _SafeImportStripper().visit(tree)
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)


def python_compute(payload: dict[str, Any]) -> ToolResult:
    code = str(payload.get("code", ""))
    try:
        safe_code = _sanitize(code)
        proc = subprocess.run(
            [sys.executable, "-I", "-S", "-c", _RUNNER],
            input=json.dumps({"code": safe_code}),
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
