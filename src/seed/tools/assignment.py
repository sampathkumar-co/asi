from __future__ import annotations

import re
from typing import Any

from .csp import solve_finite_csp
from .registry import ToolResult

_CALL_RE = re.compile(r"^\s*([a-z_]+)\s*\((.*)\)\s*$")
_LIST_CALL_RE = re.compile(r"^\s*(not_same_any|not_in_topics)\s*\(\s*([^,]+)\s*,\s*\[(.*)\]\s*\)\s*$")


def _atom(text: str) -> Any:
    value = text.strip().strip('"\'')
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?\d+(?:\.\d+)", value):
        return float(value)
    return value


def _normalize_constraint(raw: Any, entities: set[str]) -> list[dict[str, Any]]:
    """Accept documented objects plus compact function-call strings."""
    if isinstance(raw, dict):
        data = dict(raw)
        if data.get("op") in {"not_same_any", "not_in_topics"}:
            entity = str(data.get("entity", data.get("left", "")))
            others = data.get("others", data.get("values", []))
            if entity not in entities or not isinstance(others, list):
                raise ValueError("not_same_any requires a known entity and an array of entities")
            return [{"op": "not_same", "left": entity, "right": str(other)} for other in others]
    elif isinstance(raw, str):
        list_match = _LIST_CALL_RE.fullmatch(raw)
        if list_match:
            entity = str(_atom(list_match.group(2)))
            others = [str(_atom(part)) for part in list_match.group(3).split(",") if part.strip()]
            if entity not in entities or not others or any(other not in entities for other in others):
                raise ValueError("not_same_any requires known entities")
            return [{"op": "not_same", "left": entity, "right": other} for other in others]

        match = _CALL_RE.fullmatch(raw)
        if not match:
            raise ValueError("constraint string must look like op(arg, ...)")
        op = match.group(1)
        args = [_atom(part) for part in match.group(2).split(",") if part.strip()]
        if op == "position_eq" and len(args) == 2:
            if str(args[1]) in entities:
                data = {"op": "same_position", "left": str(args[0]), "right": str(args[1])}
            else:
                data = {"op": op, "entity": str(args[0]), "position": args[1]}
        elif op == "not_in_positions" and len(args) >= 2:
            data = {"op": op, "entity": str(args[0]), "positions": list(args[1:])}
        elif op == "distance" and len(args) == 3:
            data = {"op": op, "left": str(args[0]), "right": str(args[1]), "value": args[2]}
        elif op in {"before", "after", "immediately_before", "immediately_after", "same_position", "not_same"} and len(args) == 2:
            data = {"op": op, "left": str(args[0]), "right": str(args[1])}
        else:
            raise ValueError(f"invalid compact assignment constraint: {raw}")
    else:
        raise ValueError("constraints must be objects or compact function-call strings")

    if data.get("op") == "position_eq" and str(data.get("position")) in entities:
        data = {"op": "same_position", "left": str(data.get("entity", "")), "right": str(data["position"])}
    return [data]


def _translate_constraint(raw: dict[str, Any], entities: set[str]) -> dict[str, Any]:
    op = str(raw.get("op", ""))
    if op == "position_eq":
        entity = str(raw.get("entity", ""))
        if entity not in entities:
            raise ValueError("position_eq entity must be known")
        return {"op": "eq", "left": entity, "value": raw.get("position")}
    if op == "not_in_positions":
        entity = str(raw.get("entity", ""))
        values = raw.get("positions")
        if entity not in entities or not isinstance(values, list):
            raise ValueError("not_in_positions requires known entity and positions")
        return {"op": "not_in", "var": entity, "values": values}

    left, right = str(raw.get("left", "")), str(raw.get("right", ""))
    if left not in entities or right not in entities:
        raise ValueError(f"{op} requires known left/right entities")
    if op == "same_position":
        return {"op": "eq", "left": left, "right": right}
    if op == "not_same":
        return {"op": "ne", "left": left, "right": right}
    if op == "before":
        return {"op": "lt", "left": left, "right": right}
    if op == "after":
        return {"op": "gt", "left": left, "right": right}
    if op == "immediately_before":
        return {"op": "offset_eq", "left": right, "right": left, "value": 1}
    if op == "immediately_after":
        return {"op": "offset_eq", "left": left, "right": right, "value": 1}
    if op == "distance":
        return {"op": "abs_diff", "left": left, "right": right, "value": raw.get("value")}
    raise ValueError(f"unsupported assignment constraint op: {op}")


def assignment_csp_tool(payload: dict[str, Any]) -> ToolResult:
    try:
        groups = payload.get("groups")
        positions = payload.get("positions")
        constraints = payload.get("constraints", [])
        render_groups = payload.get("render_groups")
        labels = payload.get("labels", {})
        template = str(payload.get("answer_template", "FINAL: {assignment}"))
        if not isinstance(groups, dict) or not groups or not isinstance(positions, list) or not positions:
            raise ValueError("groups and positions are required")
        if not isinstance(constraints, list) or not isinstance(render_groups, list) or not isinstance(labels, dict):
            raise ValueError("constraints/render_groups/labels have invalid types")
        if len(template) > 512:
            raise ValueError("answer_template too long")

        clean_groups: dict[str, list[str]] = {}
        entities: set[str] = set()
        for raw_name, raw_entities in groups.items():
            name = str(raw_name)
            if not name or not isinstance(raw_entities, list) or len(raw_entities) != len(positions):
                raise ValueError("each group must contain exactly one entity per position")
            values = [str(x) for x in raw_entities]
            if len(values) != len(set(values)) or any(v in entities for v in values):
                raise ValueError("entity names must be unique across groups")
            entities.update(values)
            clean_groups[name] = values

        domains = {entity: list(positions) for entity in entities}
        all_different = list(clean_groups.values())
        normalized_constraints: list[dict[str, Any]] = []
        for raw in constraints:
            normalized_constraints.extend(_normalize_constraint(raw, entities))
        low_constraints = [_translate_constraint(raw, entities) for raw in normalized_constraints]
        solved = solve_finite_csp(domains, all_different, low_constraints)
        solution = solved["solution"]
        if solution is None:
            raise ValueError("assignment CSP has no solution")
        if not solved["unique"]:
            raise ValueError("assignment CSP solution is not unique")

        rendered: dict[str, str] = {}
        for spec in render_groups:
            if not isinstance(spec, dict):
                raise ValueError("render_groups entries must be objects")
            name = str(spec.get("name", ""))
            raw_group = spec.get("group", "")
            if isinstance(raw_group, list) and name in clean_groups:
                group = name
            else:
                group = str(raw_group)
            if not name or group not in clean_groups:
                raise ValueError("render group name/group invalid")
            ordered = sorted(clean_groups[group], key=lambda entity: positions.index(solution[entity]))
            rendered_values = [str(labels.get(entity, entity)) for entity in ordered]
            default_separator = "" if rendered_values and all(len(value) == 1 for value in rendered_values) else "-"
            separator = str(spec.get("separator", default_separator))
            rendered[name] = separator.join(rendered_values)

        answer = template
        for name, value in rendered.items():
            answer = answer.replace("{" + name + "}", value)
        if "{" in answer or "}" in answer:
            raise ValueError("answer_template contains unresolved placeholders")
        checks = {
            "solution_found": True,
            "unique_solution": solved["unique"],
            "all_constraints_hold": True,
            "all_groups_rendered": len(rendered) == len(render_groups),
        }
        return ToolResult(True, output={"answer": answer, "checks": checks, "evidence": {"solution": solution, "search_nodes": solved["search_nodes"], "rendered": rendered}})
    except Exception as exc:
        return ToolResult(False, error=str(exc))
