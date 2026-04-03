from __future__ import annotations

from collections import deque
from typing import Iterable, List, Sequence

from soe_simulation import TopologyGraph


def compute_failure_rate(initial_node_count: int, failed_node_ids: Iterable[int]) -> float:
    failed_count = len(set(failed_node_ids))
    if initial_node_count <= 0:
        return 0.0
    return failed_count / initial_node_count


def compute_time_to_collapse(
    step_records: Sequence[dict],
    *,
    stability_threshold: float,
) -> int | None:
    for row in step_records:
        if row["avg_stability"] < stability_threshold:
            return int(row["year"])
    return None


def compute_survival_clusters(graph: TopologyGraph, stable_node_ids: Iterable[int]) -> List[int]:
    stable_nodes = set(stable_node_ids)
    remaining = set(stable_nodes)
    cluster_sizes: List[int] = []
    while remaining:
        start = remaining.pop()
        queue = [start]
        size = 0
        while queue:
            node_id = queue.pop()
            if node_id not in stable_nodes:
                continue
            stable_nodes.remove(node_id)
            size += 1
            for neighbor_id in graph.neighbors(node_id):
                if neighbor_id in stable_nodes:
                    queue.append(neighbor_id)
        cluster_sizes.append(size)
        remaining = set(stable_nodes)
    return sorted(cluster_sizes, reverse=True)


def compute_cascade_depth(
    graph: TopologyGraph,
    origin_ids: Iterable[int],
    failed_node_ids: Iterable[int],
) -> int:
    origins = set(origin_ids)
    failures = set(failed_node_ids)
    if not origins or not failures:
        return 0

    queue = deque((origin, 0) for origin in origins if origin in graph.adjacency)
    seen = {origin for origin, _ in queue}
    max_depth = 0
    while queue:
        node_id, depth = queue.popleft()
        if node_id in failures:
            max_depth = max(max_depth, depth)
        for neighbor_id in graph.neighbors(node_id):
            if neighbor_id in seen:
                continue
            seen.add(neighbor_id)
            queue.append((neighbor_id, depth + 1))
    return max_depth


def compute_resource_exhaustion_map() -> List[int]:
    # Phase 1 is topology-only, so this metric is intentionally empty until the
    # resource layer lands in Phase 3.
    return []


def compute_critical_node_index(baseline_final_stability: float, stressed_final_stability: float) -> float:
    return max(0.0, baseline_final_stability - stressed_final_stability)
