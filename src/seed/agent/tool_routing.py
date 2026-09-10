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

    graph_terms = ("path", "route", "network", "edge", "edges", "arc", "arcs")
    shortest_terms = ("shortest", "minimum-cost", "minimum cost", "least-cost", "least cost", "lowest-cost", "lowest cost")
    weighted_terms = ("weighted", "weight", "cost", "=", "->")
    if (any(term in text for term in shortest_terms) and any(term in text for term in graph_terms) and any(term in text for term in weighted_terms)) or "edges with weights" in text:
        add("shortest_path")
    if any(token in text for token in ("critical path", "project completion", "prerequisite", "prerequisites", "unlimited parallel")):
        add("dag_longest_path")
    if any(token in text for token in ("≡", " mod ", "modulo", "congruence", "remainder")):
        add("crt")
    if any(token in text for token in ("ledger", "transaction", "reconcile", "reconciliation", "approved", "cleared", "credit", "debit", "refund", "fee", "discount_percent", "discount ")):
        add("transaction_ledger")
    elif any(token in text for token in ("grouped sum", "aggregate records")):
        add("aggregate_records")
    if any(token in text for token in (
        "logic grid", "logic-grid", "arranged in positions", "unique order", "unique day order",
        "each a different topic", "presents once each", "exactly two positions", "immediately before",
    )):
        add("assignment_csp")
    if "print(" in text and any(token in text for token in ("def ", "for ", "while ", "python", "trace")):
        add("python_trace")
    if any(token in text for token in ("capacity", "maximum total value", "max total value", "weight <=", "weight ?", "subset")) and any(token in text for token in ("item", "items", "value")):
        add("subset_optimize")
    if any(token in text for token in ("echo", "scratch evidence")):
        add("echo")

    return tuple(name for name in available if name in chosen)
