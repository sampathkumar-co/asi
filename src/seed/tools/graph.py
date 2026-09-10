from __future__ import annotations

import heapq
from typing import Any

from .registry import ToolResult


def _number(value: Any) -> int | float:
    if type(value) not in (int, float):
        raise ValueError("weights must contain only finite numbers")
    value = float(value) if isinstance(value, float) else value
    if isinstance(value, float) and (value != value or value in (float("inf"), float("-inf"))):
        raise ValueError("weights must contain only finite numbers")
    return value


def weighted_shortest_path(edges: list[list[Any] | tuple[Any, Any, Any]], source: str, target: str) -> dict[str, Any]:
    if not isinstance(edges, list) or not edges:
        raise ValueError("edges must be a non-empty array")
    source, target = str(source), str(target)
    graph: dict[str, list[tuple[str, int | float]]] = {}
    nodes: set[str] = set()
    clean_edges: list[tuple[str, str, int | float]] = []
    for item in edges:
        if not isinstance(item, (list, tuple)) or len(item) != 3:
            raise ValueError("each edge must be [from, to, weight]")
        u, v, w = str(item[0]), str(item[1]), _number(item[2])
        if w < 0:
            raise ValueError("shortest_path requires non-negative edge weights")
        nodes.update((u, v))
        clean_edges.append((u, v, w))
        graph.setdefault(u, []).append((v, w))
        graph.setdefault(v, [])
    if source not in nodes or target not in nodes:
        raise ValueError("source and target must appear in edges")

    inf = float("inf")
    dist = {node: inf for node in nodes}
    count = {node: 0 for node in nodes}
    parent: dict[str, str | None] = {node: None for node in nodes}
    dist[source], count[source] = 0, 1
    heap: list[tuple[float, str]] = [(0.0, source)]
    while heap:
        d, u = heapq.heappop(heap)
        if d != dist[u]:
            continue
        for v, w in sorted(graph[u], key=lambda x: (str(x[0]), x[1])):
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                count[v] = count[u]
                parent[v] = u
                heapq.heappush(heap, (float(nd), v))
            elif nd == dist[v]:
                count[v] += count[u]
                if parent[v] is None or str(u) < str(parent[v]):
                    parent[v] = u
    if dist[target] == inf:
        raise ValueError("target is unreachable from source")

    path: list[str] = []
    cur: str | None = target
    seen: set[str] = set()
    while cur is not None:
        if cur in seen:
            raise ValueError("path reconstruction cycle")
        seen.add(cur)
        path.append(cur)
        if cur == source:
            break
        cur = parent[cur]
    path.reverse()
    if not path or path[0] != source or path[-1] != target:
        raise ValueError("failed to reconstruct shortest path")
    edge_map = {(u, v): w for u, v, w in clean_edges}
    cost = sum(edge_map[(path[i], path[i + 1])] for i in range(len(path) - 1))
    checks = {
        "source_reached": path[0] == source,
        "target_reached": path[-1] == target,
        "path_edges_valid": all((path[i], path[i + 1]) in edge_map for i in range(len(path) - 1)),
        "cost_matches_path": cost == dist[target],
        "optimality_relaxation": all(dist[v] <= dist[u] + w for u, v, w in clean_edges if dist[u] != inf),
        "unique_shortest_path": count[target] == 1,
    }
    return {"cost": dist[target], "path": path, "distances": dist, "shortest_path_count": count[target], "checks": checks}


def shortest_path_tool(payload: dict[str, Any]) -> ToolResult:
    try:
        edges = payload.get("edges")
        source, target = payload.get("source"), payload.get("target")
        if not isinstance(edges, list) or source is None or target is None:
            raise ValueError("edges, source, and target are required")
        template = str(payload.get("answer_template", "FINAL: {cost} | {path}"))
        separator = str(payload.get("path_separator", "-"))
        if len(template) > 256 or "{cost}" not in template or "{path}" not in template:
            raise ValueError("answer_template must contain {cost} and {path}")
        if len(separator) > 8:
            raise ValueError("path_separator too long")
        data = weighted_shortest_path(edges, str(source), str(target))
        answer = template.replace("{cost}", str(data["cost"])).replace("{path}", separator.join(data["path"]))
        return ToolResult(True, output={"answer": answer, "checks": data["checks"], "evidence": data})
    except Exception as exc:
        return ToolResult(False, error=str(exc))


def weighted_dag_longest_path(
    weights: dict[str, int | float],
    predecessors: dict[str, list[str]],
    target: str | None = None,
) -> dict[str, Any]:
    if not isinstance(weights, dict) or not weights:
        raise ValueError("weights must be a non-empty object")
    if not isinstance(predecessors, dict):
        raise ValueError("predecessors must be an object")

    clean_weights = {str(node): _number(weight) for node, weight in weights.items()}
    nodes = list(clean_weights)
    node_set = set(nodes)
    extra = set(map(str, predecessors)) - node_set
    if extra:
        raise ValueError("predecessors contains unknown nodes")

    preds: dict[str, list[str]] = {}
    for node in nodes:
        raw = predecessors.get(node, [])
        if not isinstance(raw, list):
            raise ValueError("each predecessor list must be an array")
        values = [str(x) for x in raw]
        if len(values) != len(set(values)):
            raise ValueError("duplicate predecessor")
        if node in values or any(p not in node_set for p in values):
            raise ValueError("invalid predecessor reference")
        preds[node] = values

    successors = {node: [] for node in nodes}
    indegree = {node: len(preds[node]) for node in nodes}
    for node in nodes:
        for pred in preds[node]:
            successors[pred].append(node)

    ready = sorted((node for node in nodes if indegree[node] == 0), key=str)
    topo: list[str] = []
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

    score: dict[str, int | float] = {}
    parent: dict[str, str | None] = {}
    for node in topo:
        if preds[node]:
            best = min(preds[node], key=lambda p: (-score[p], str(p)))
            score[node] = score[best] + clean_weights[node]
            parent[node] = best
        else:
            score[node] = clean_weights[node]
            parent[node] = None

    chosen = str(target) if target is not None else min(nodes, key=lambda n: (-score[n], str(n)))
    if chosen not in node_set:
        raise ValueError("target must be a graph node")

    path: list[str] = []
    cursor: str | None = chosen
    while cursor is not None:
        path.append(cursor)
        cursor = parent[cursor]
    path.reverse()

    path_weight = sum(clean_weights[node] for node in path)
    checks = {
        "acyclic": len(topo) == len(nodes),
        "target_reached": bool(path) and path[-1] == chosen,
        "path_edges_valid": all(path[i] in preds[path[i + 1]] for i in range(len(path) - 1)),
        "weight_matches_path": path_weight == score[chosen],
        "dynamic_program_valid": all(score[node] == clean_weights[node] + (max(score[p] for p in preds[node]) if preds[node] else 0) for node in topo),
    }
    return {"weight": score[chosen], "path": path, "scores": score, "topological_order": topo, "checks": checks}


def dag_longest_path_tool(payload: dict[str, Any]) -> ToolResult:
    try:
        weights = payload.get("weights")
        predecessors = payload.get("predecessors")
        if not isinstance(weights, dict) or not isinstance(predecessors, dict):
            raise ValueError("weights and predecessors are required objects")
        target = payload.get("target")
        template = str(payload.get("answer_template", "FINAL: {weight} | {path}"))
        separator = str(payload.get("path_separator", "-"))
        if len(template) > 256 or "{weight}" not in template or "{path}" not in template:
            raise ValueError("answer_template must be <=256 chars and contain {weight} and {path}")
        if len(separator) > 8:
            raise ValueError("path_separator too long")
        graph = weighted_dag_longest_path(weights, predecessors, None if target is None else str(target))
        answer = template.replace("{weight}", str(graph["weight"])).replace("{path}", separator.join(graph["path"]))
        return ToolResult(True, output={"answer": answer, "checks": graph["checks"], "evidence": {"weight": graph["weight"], "path": graph["path"], "scores": graph["scores"], "topological_order": graph["topological_order"]}})
    except Exception as exc:
        return ToolResult(False, error=str(exc))
