from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any

from .registry import ToolResult


def _dec(value: Any) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"invalid decimal value: {value!r}") from exc


def aggregate_records(payload: dict[str, Any]) -> ToolResult:
    try:
        records = payload.get("records")
        if not isinstance(records, list) or not records:
            raise ValueError("records must be a non-empty array")
        include_statuses = payload.get("include_statuses", [])
        if not isinstance(include_statuses, list):
            raise ValueError("include_statuses must be an array")
        include = {str(x) for x in include_statuses}
        totals: dict[str, Decimal] = {}
        included = 0
        for row in records:
            if not isinstance(row, dict):
                raise ValueError("each record must be an object")
            status = str(row.get("status", ""))
            if include and status not in include:
                continue
            group = str(row.get("group", ""))
            if not group:
                raise ValueError("record group is required")
            sign = str(row.get("sign", "add"))
            if sign not in {"add", "subtract"}:
                raise ValueError("sign must be add or subtract")
            if "amount" in row:
                amount = _dec(row["amount"])
            else:
                factors = row.get("factors")
                if not isinstance(factors, list) or not factors:
                    raise ValueError("record needs amount or non-empty factors")
                amount = Decimal(1)
                for factor in factors:
                    amount *= _dec(factor)
                discount = _dec(row.get("discount_percent", 0))
                amount *= Decimal(1) - discount / Decimal(100)
            if sign == "subtract":
                amount = -amount
            totals[group] = totals.get(group, Decimal(0)) + amount
            included += 1

        places = int(payload.get("decimal_places", 2))
        if not 0 <= places <= 8:
            raise ValueError("decimal_places must be 0..8")
        quantum = Decimal(1).scaleb(-places)
        formatted = {
            key: str(value.quantize(quantum, rounding=ROUND_HALF_UP))
            for key, value in totals.items()
        }
        total = sum(totals.values(), Decimal(0))
        formatted_total = str(total.quantize(quantum, rounding=ROUND_HALF_UP))
        template = str(payload.get("answer_template", "FINAL: {TOTAL}"))
        if len(template) > 512 or "{TOTAL}" not in template:
            raise ValueError("answer_template must contain {TOTAL}")
        answer = template.replace("{TOTAL}", formatted_total)
        for key, value in formatted.items():
            answer = answer.replace("{" + key + "}", value)
        unresolved = [part for part in answer.split("{")[1:] if "}" in part]
        if unresolved:
            raise ValueError("answer_template contains unresolved placeholders")
        checks = {
            "records_processed": included > 0,
            "total_matches_groups": total == sum(totals.values(), Decimal(0)),
            "all_finite": all(value.is_finite() for value in totals.values()),
        }
        return ToolResult(True, output={"answer": answer, "checks": checks, "evidence": {"totals": formatted, "total": formatted_total, "included_records": included}})
    except Exception as exc:
        return ToolResult(False, error=str(exc))
