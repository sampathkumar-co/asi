from __future__ import annotations

import json
from typing import Any

from .registry import ToolResult

_MAX_VARIABLES = 16
_MAX_DOMAIN = 16
_MAX_SEARCH_NODES = 250_000


def _coerce_literal(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    try:
        return json.loads(value)
    except Exception:
        return value


def _normalize_constraint(c: dict[str, Any], variables: set[str]) -> dict[str, Any]:
    out = dict(c)
    op = str(out.get("op", ""))
    if "value" in out:
        out["value"] = _coerce_literal(out["value"])
    if op in {"eq", "ne"} and "right" in out and str(out["right"]) not in variables and "value" not in out:
        out["value"] = _coerce_literal(out.pop("right"))
    if op == "not_in" and isinstance(out.get("values"), list):
        out["values"] = [_coerce_literal(v) for v in out["values"]]
    return out


def _validate_constraint(c: dict[str, Any], variables: set[str]) -> None:
    op = str(c.get("op", ""))
    supported = {"eq", "ne", "lt", "gt", "offset_eq", "abs_diff", "not_in"}
    if op not in supported:
        raise ValueError(f"unsupported constraint op: {op}")
    if op == "not_in":
        var = str(c.get("var", ""))
        if var not in variables or not isinstance(c.get("values"), list):
            raise ValueError("not_in requires var and values")
        return
    left = str(c.get("left", ""))
    if left not in variables:
        raise ValueError("constraint left must be a variable")
    has_right = "right" in c
    has_value = "value" in c
    if op in {"lt", "gt", "offset_eq", "abs_diff"} and not has_right:
        raise ValueError(f"{op} requires right variable")
    if has_right and str(c["right"]) not in variables:
        raise ValueError("constraint right must be a variable")
    if op in {"eq", "ne"} and not (has_right or has_value):
        raise ValueError(f"{op} requires right or value")
    if op in {"offset_eq", "abs_diff"}:
        if not has_value or type(c["value"]) not in (int, float):
            raise ValueError(f"{op} requires numeric value")


def _constraint_ok(c: dict[str, Any], assignment: dict[str, Any]) -> bool | None:
    op = str(c["op"])
    if op == "not_in":
        var = str(c["var"])
        if var not in assignment:
            return None
        return assignment[var] not in c["values"]
    left = str(c["left"])
    if left not in assignment:
        return None
    lv = assignment[left]
    if "right" in c:
        right = str(c["right"])
        if right not in assignment:
            return None
        rv = assignment[right]
    else:
        rv = c.get("value")
    if op == "eq":
        return lv == rv
    if op == "ne":
        return lv != rv
    if op == "lt":
        return lv < rv
    if op == "gt":
        return lv > rv
    if op == "offset_eq":
        return lv == rv + c["value"]
    if op == "abs_diff":
        return abs(lv - rv) == c["value"]
    raise ValueError(f"unsupported constraint op: {op}")


def solve_finite_csp(
    domains: dict[str, list[Any]],
    all_different: list[list[str]],
    constraints: list[dict[str, Any]],
) -> dict[str, Any]:
    if not isinstance(domains, dict) or not domains or len(domains) > _MAX_VARIABLES:
        raise ValueError("domains must contain 1..16 variables")
    clean: dict[str, list[Any]] = {}
    for raw_name, raw_domain in domains.items():
        name = str(raw_name)
        if not name or not isinstance(raw_domain, list) or not raw_domain or len(raw_domain) > _MAX_DOMAIN:
            raise ValueError("each domain must contain 1..16 values")
        values = [_coerce_literal(v) for v in raw_domain]
        if len(values) != len({repr(v) for v in values}):
            raise ValueError("domain values must be unique")
        clean[name] = values
    variables = set(clean)

    if not isinstance(all_different, list) or not isinstance(constraints, list):
        raise ValueError("all_different and constraints must be arrays")
    groups: list[list[str]] = []
    for group in all_different:
        if not isinstance(group, list) or len(group) < 2:
            raise ValueError("all_different groups must contain at least two variables")
        names = [str(x) for x in group]
        if len(names) != len(set(names)) or any(name not in variables for name in names):
            raise ValueError("invalid all_different group")
        groups.append(names)

    normalized: list[dict[str, Any]] = []
    for raw in constraints:
        if not isinstance(raw, dict):
            raise ValueError("constraints must be objects")
        c = _normalize_constraint(raw, variables)
        _validate_constraint(c, variables)
        normalized.append(c)
    constraints = normalized

    occurrences = {name: 0 for name in clean}
    for group in groups:
        for name in group:
            occurrences[name] += 1
    for c in constraints:
        for key in ("left", "right", "var"):
            if key in c and str(c[key]) in occurrences:
                occurrences[str(c[key])] += 1
    order = sorted(clean, key=lambda n: (len(clean[n]), -occurrences[n], n))
    assignment: dict[str, Any] = {}
    solutions: list[dict[str, Any]] = []
    nodes = 0

    def partial_ok() -> bool:
        for group in groups:
            vals = [assignment[name] for name in group if name in assignment]
            if len(vals) != len({repr(v) for v in vals}):
                return False
        for c in constraints:
            result = _constraint_ok(c, assignment)
            if result is False:
                return False
        return True

    def search(index: int) -> None:
        nonlocal nodes
        if len(solutions) >= 2:
            return
        if nodes >= _MAX_SEARCH_NODES:
            raise RuntimeError("finite CSP search node limit exceeded")
        nodes += 1
        if index == len(order):
            solutions.append(dict(assignment))
            return
        name = order[index]
        for value in clean[name]:
            assignment[name] = value
            if partial_ok():
                search(index + 1)
            assignment.pop(name, None)
            if len(solutions) >= 2:
                return

    search(0)
    return {
        "solution": solutions[0] if solutions else None,
        "solution_count_capped": len(solutions),
        "unique": len(solutions) == 1,
        "search_nodes": nodes,
        "constraints": constraints,
    }


def finite_csp_tool(payload: dict[str, Any]) -> ToolResult:
    try:
        domains = payload.get("domains")
        all_different = payload.get("all_different", [])
        constraints = payload.get("constraints", [])
        sequences = payload.get("sequences", [])
        template = str(payload.get("answer_template", "FINAL: {assignment}"))
        if not isinstance(domains, dict) or not isinstance(sequences, list):
            raise ValueError("domains and sequences are required")
        if len(template) > 512:
            raise ValueError("answer_template too long")
        solved = solve_finite_csp(domains, all_different, constraints)
        solution = solved["solution"]
        if solution is None:
            raise ValueError("CSP has no solution")
        if not solved["unique"]:
            raise ValueError("CSP solution is not unique")

        rendered: dict[str, str] = {}
        for spec in sequences:
            if not isinstance(spec, dict):
                raise ValueError("sequence specs must be objects")
            name = str(spec.get("name", ""))
            variables = spec.get("variables")
            order_values = spec.get("order")
            if not name or not isinstance(variables, list) or not isinstance(order_values, list):
                raise ValueError("sequence requires name, variables, and order")
            variables = [str(v) for v in variables]
            labels = spec.get("labels", {})
            if isinstance(labels, list):
                if len(labels) != len(variables):
                    raise ValueError("parallel sequence labels must match variables length")
                labels = {var: labels[i] for i, var in enumerate(variables)}
            if not isinstance(labels, dict):
                raise ValueError("sequence labels must be an object or parallel array")
            separator = str(spec.get("separator", "-"))
            parts: list[str] = []
            for expected in [_coerce_literal(v) for v in order_values]:
                matches = [var for var in variables if var in solution and solution[var] == expected]
                if len(matches) != 1:
                    raise ValueError("sequence order does not map to exactly one variable")
                var = matches[0]
                parts.append(str(labels.get(var, var)))
            rendered[name] = separator.join(parts)

        answer = template
        for name, value in rendered.items():
            answer = answer.replace("{" + name + "}", value)
        if "{assignment}" in answer:
            answer = answer.replace("{assignment}", str(solution))
        if "{" in answer or "}" in answer:
            raise ValueError("answer_template contains unresolved placeholders")

        normalized_constraints = solved["constraints"]
        assignment_check = all(_constraint_ok(c, solution) is True for c in normalized_constraints)
        all_diff_check = all(
            len([solution[name] for name in group]) == len({repr(solution[name]) for name in group})
            for group in all_different
        )
        checks = {
            "solution_found": solution is not None,
            "unique_solution": solved["unique"],
            "constraints_hold": assignment_check,
            "all_different_hold": all_diff_check,
            "sequences_rendered": len(rendered) == len(sequences),
        }
        evidence = {k: v for k, v in solved.items() if k != "constraints"}
        evidence["sequences"] = rendered
        return ToolResult(True, output={"answer": answer, "checks": checks, "evidence": evidence})
    except Exception as exc:
        return ToolResult(False, error=str(exc))
