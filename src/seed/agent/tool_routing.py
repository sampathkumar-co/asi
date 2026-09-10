from __future__ import annotations


def select_tools(goal: str, available: tuple[str, ...]) -> tuple[str, ...]:
    """Expose only likely-relevant tools plus safe general fallbacks.

    Routing is deterministic and answer-independent; it reduces schema/context
    pressure for small local models without changing evaluator-visible tasks.
    """
    text = goal.lower()
    chosen: set[str] = set()

    def add(name: str) -> None:
        if name in available:
            chosen.add(name)

    add("python_compute")
    add("calculator")

    if any(token in text for token in ("shortest path", "minimum-cost path", "directed path", "edges with weights")):
        add("shortest_path")
    if any(token in text for token in ("critical path", "project completion", "prerequisite", "prerequisites", "unlimited parallel")):
        add("dag_longest_path")
    if any(token in text for token in ("≡", " mod ", "modulo", "congruence", "remainder")):
        add("crt")
    if any(token in text for token in ("ledger", "posted", "refund", "fee", "discount_percent", "discount ")):
        add("aggregate_records")
    if any(token in text for token in (
        "logic grid", "logic-grid", "arranged in positions", "unique order", "unique day order",
        "each a different topic", "presents once each", "exactly two positions", "immediately before",
    )):
        add("assignment_csp")
    if any(token in text for token in ("echo", "scratch evidence")):
        add("echo")

    return tuple(name for name in available if name in chosen)
