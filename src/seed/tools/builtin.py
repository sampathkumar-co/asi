from __future__ import annotations

import ast
import operator
from typing import Any

from .aggregate import aggregate_records
from .assignment import assignment_csp_tool
from .csp import finite_csp_tool
from .graph import dag_longest_path_tool, shortest_path_tool
from .math_exact import crt_tool
from .python_compute import python_compute
from .registry import ToolRegistry, ToolResult


_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _eval(node: ast.AST) -> float | int:
    if isinstance(node, ast.Expression):
        return _eval(node.body)
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _BINOPS:
        left, right = _eval(node.left), _eval(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 20:
            raise ValueError("Exponent too large")
        return _BINOPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY:
        return _UNARY[type(node.op)](_eval(node.operand))
    raise ValueError("Expression contains unsupported syntax")


def calculator(payload: dict[str, Any]) -> ToolResult:
    expr = str(payload.get("expression", ""))
    if len(expr) > 200:
        return ToolResult(False, error="Expression too long")
    try:
        tree = ast.parse(expr, mode="eval")
        value = _eval(tree)
    except Exception as exc:
        return ToolResult(False, error=str(exc))
    return ToolResult(True, output=value)


def echo(payload: dict[str, Any]) -> ToolResult:
    return ToolResult(True, output=payload.get("text", ""))


def default_registry() -> ToolRegistry:
    reg = ToolRegistry()
    reg.register("aggregate_records", aggregate_records)
    reg.register("assignment_csp", assignment_csp_tool)
    reg.register("calculator", calculator)
    reg.register("crt", crt_tool)
    reg.register("dag_longest_path", dag_longest_path_tool)
    reg.register("finite_csp", finite_csp_tool)
    reg.register("shortest_path", shortest_path_tool)
    reg.register("python_compute", python_compute)
    reg.register("echo", echo)
    return reg
