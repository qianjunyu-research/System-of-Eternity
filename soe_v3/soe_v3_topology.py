from __future__ import annotations

import random
from typing import Iterable, List, Sequence

from soe_simulation import TopologyGraph


PHASE1_TOPOLOGIES = (
    "fully-connected",
    "chain",
    "star",
    "random-sparse",
)


def build_fully_connected_topology(node_ids: Sequence[int]) -> TopologyGraph:
    graph = TopologyGraph(list(node_ids))
    for index, source in enumerate(node_ids):
        for target in node_ids[index + 1 :]:
            graph.add_edge(source, target)
    return graph


def build_chain_topology(node_ids: Sequence[int]) -> TopologyGraph:
    graph = TopologyGraph(list(node_ids))
    for source, target in zip(node_ids, node_ids[1:]):
        graph.add_edge(source, target)
    return graph


def build_star_topology(node_ids: Sequence[int], center_id: int | None = None) -> TopologyGraph:
    graph = TopologyGraph(list(node_ids))
    if not node_ids:
        return graph
    center = node_ids[0] if center_id is None else center_id
    for node_id in node_ids:
        if node_id != center:
            graph.add_edge(center, node_id)
    return graph


def build_random_sparse_topology(
    node_ids: Sequence[int],
    rng: random.Random,
    *,
    extra_edge_probability: float = 0.06,
) -> TopologyGraph:
    # Start with a chain backbone so Phase 1 comparisons begin from a connected
    # graph instead of mixing propagation with random initial disconnection.
    graph = build_chain_topology(node_ids)
    for index, source in enumerate(node_ids):
        for target in node_ids[index + 2 :]:
            if target in graph.adjacency[source]:
                continue
            if rng.random() < extra_edge_probability:
                graph.add_edge(source, target)
    return graph


def build_phase1_topology(
    topology: str,
    node_ids: Sequence[int],
    rng: random.Random,
    *,
    random_edge_probability: float = 0.06,
) -> TopologyGraph:
    if topology == "fully-connected":
        return build_fully_connected_topology(node_ids)
    if topology == "chain":
        return build_chain_topology(node_ids)
    if topology == "star":
        return build_star_topology(node_ids)
    if topology == "random-sparse":
        return build_random_sparse_topology(
            node_ids,
            rng,
            extra_edge_probability=random_edge_probability,
        )
    raise ValueError(f"Unsupported Phase 1 topology: {topology}")


def topology_degrees(graph: TopologyGraph) -> List[int]:
    return sorted((graph.degree(node_id) for node_id in graph.adjacency), reverse=True)
