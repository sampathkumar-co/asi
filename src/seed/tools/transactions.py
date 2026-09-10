from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import re
from typing import Any

from .registry import ToolResult

_ADD_KINDS = {"sale", "credit"}
_SUBTRACT_KINDS = {"refund", "fee", "debit"}

_KEY_ALIASES = {
    "qty": "quantity", "unit": "unit_price", "unitprice": "unit_price",
    "price": "unit_price", "discount": "discount_percent", "type": "kind",
}

def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for raw_key, value in row.items():
        key = str(raw_key).strip().lower().rstrip(",:;").replace(" ", "_").replace("-", "_")
        key = _KEY_ALIASES.get(key, key)
        if key in normalized and normalized[key] != value:
            raise ValueError(f"conflicting values for {key}")
        normalized[key] = value
    return normalized

def _dec(value: Any) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"invalid decimal value: {value!r}") from exc

def _record_amount(row: dict[str, Any]) -> Decimal:
    kind = str(row.get("kind", "")).lower()
    if kind not in _ADD_KINDS | _SUBTRACT_KINDS:
        raise ValueError("kind must be sale, credit, refund, fee, or debit")
    has_amount = "amount" in row
    has_parts = "quantity" in row or "unit_price" in row
    if kind == "sale":
        if has_amount == has_parts:
            raise ValueError("sale requires exactly one of amount OR quantity+unit_price")
        if has_parts:
            if "quantity" not in row or "unit_price" not in row:
                raise ValueError("sale quantity and unit_price must be supplied together")
            amount = _dec(row["quantity"]) * _dec(row["unit_price"])
        else:
            amount = _dec(row["amount"])
        discount = _dec(row.get("discount_percent", 0))
        if not Decimal(0) <= discount <= Decimal(100):
            raise ValueError("discount_percent must be 0..100")
        amount *= Decimal(1) - discount / Decimal(100)
    else:
        if not has_amount or has_parts:
            raise ValueError(f"{kind} requires amount and no quantity/unit_price")
        amount = _dec(row["amount"])
    return amount if kind in _ADD_KINDS else -amount

def _parse_records_text(text: str) -> list[dict[str, Any]]:
    source = text.split("Return exactly", 1)[0].split("Return:", 1)[0]
    records: list[dict[str, Any]] = []
    pattern = re.compile(r"([A-Za-z][A-Za-z0-9_-]*)\s+(sale|credit|refund|fee|debit)\s+(.+?)\s+([A-Z][A-Z0-9_-]*)\s*$", re.IGNORECASE)
    for segment in source.split(";"):
        clean = segment.strip().rstrip(".").strip()
        match = pattern.search(clean)
        if not match:
            continue
        group, kind, body, status = match.groups()
        kind = kind.lower(); row: dict[str, Any] = {"group": group, "kind": kind, "status": status.upper()}
        if kind == "sale":
            product = re.search(r"(-?\d+(?:\.\d+)?)\s*\*\s*(-?\d+(?:\.\d+)?)", body)
            if product:
                row["quantity"] = product.group(1); row["unit_price"] = product.group(2)
            else:
                amount = re.search(r"-?\d+(?:\.\d+)?", body)
                if not amount: raise ValueError("sale text missing amount or quantity*unit_price")
                row["amount"] = amount.group(0)
            discount = re.search(r"(-?\d+(?:\.\d+)?)\s*%\s*discount", body, re.IGNORECASE)
            if discount: row["discount_percent"] = discount.group(1)
        else:
            amount = re.search(r"-?\d+(?:\.\d+)?", body)
            if not amount: raise ValueError(f"{kind} text missing amount")
            row["amount"] = amount.group(0)
        records.append(row)
    if not records:
        raise ValueError("records_text contained no recognizable transactions")
    return records

def transaction_ledger(payload: dict[str, Any]) -> ToolResult:
    try:
        records_text = payload.get("records_text")
        records = _parse_records_text(str(records_text)) if records_text else payload.get("records")
        statuses = payload.get("include_statuses", [])
        if not isinstance(records, list) or not records:
            raise ValueError("records or records_text must provide transactions")
        if not isinstance(statuses, list):
            raise ValueError("include_statuses must be an array")
        include = {str(x) for x in statuses}
        totals: dict[str, Decimal] = {}
        included = 0
        for row in records:
            if not isinstance(row, dict):
                raise ValueError("each record must be an object")
            row = _normalize_row(row)
            status = str(row.get("status", ""))
            if include and status not in include:
                continue
            group = str(row.get("group", ""))
            if not group:
                raise ValueError("record group is required")
            totals[group] = totals.get(group, Decimal(0)) + _record_amount(row)
            included += 1
        places = int(payload.get("decimal_places", 2))
        if not 0 <= places <= 8:
            raise ValueError("decimal_places must be 0..8")
        quantum = Decimal(1).scaleb(-places)
        rendered = {k: str(v.quantize(quantum, rounding=ROUND_HALF_UP)) for k,v in totals.items()}
        total = sum(totals.values(), Decimal(0))
        total_s = str(total.quantize(quantum, rounding=ROUND_HALF_UP))
        template = str(payload.get("answer_template", "FINAL: {TOTAL}"))
        if "{TOTAL}" not in template or len(template) > 512:
            raise ValueError("answer_template must contain {TOTAL}")
        answer = template.replace("{TOTAL}", total_s)
        for key,value in rendered.items():
            answer = answer.replace("{"+key+"}", value)
        if "{" in answer or "}" in answer:
            raise ValueError("answer_template contains unresolved placeholders")
        if not answer.lstrip().upper().startswith("FINAL:"):
            answer = "FINAL: " + answer.strip()
        checks = {"records_processed": included > 0, "semantic_kinds_valid": True, "total_matches_groups": total == sum(totals.values(), Decimal(0))}
        return ToolResult(True, output={"answer":answer,"checks":checks,"evidence":{"totals":rendered,"total":total_s,"included_records":included}})
    except Exception as exc:
        return ToolResult(False, error=str(exc))
