from __future__ import annotations

import random
from typing import Iterable, List

from soe_simulation import Civilization, FAILURE_STABILITY_THRESHOLD, SimulationConfig, TopologyGraph, clamp


PHASE1_DEFAULT_YEARS = 500
PHASE1_DEFAULT_STEP_YEARS = 10


def build_phase1_config(
    *,
    years: int = PHASE1_DEFAULT_YEARS,
    step_years: int = PHASE1_DEFAULT_STEP_YEARS,
    governance_survival_threshold: float = 0.45,
    contagion_penalty: float = 0.08,
) -> SimulationConfig:
    """Build a v2-backed config for the isolated v3 topology phase.

    The existing engine requires topology mode to be enabled before it will
    execute contagion and fragmentation logic, so the adapter keeps a valid
    v2 topology flag internally and swaps in the requested Phase 1 graph later.
    """

    return SimulationConfig(
        years=years,
        step_years=step_years,
        topology="random",
        contagion_penalty=contagion_penalty,
        betrayal_year=None,
        betrayal_fraction=0.0,
        trust_memory_decay=0.0,
        infiltration_year=None,
        infiltration_fraction=0.0,
        infiltration_trust_damage=0.0,
        infiltration_cooperation_damage=0.0,
        enable_local_defense=False,
        governance_survival_threshold=governance_survival_threshold,
    )


def clone_graph(graph: TopologyGraph) -> TopologyGraph:
    copied = TopologyGraph(list(graph.adjacency))
    for source_id, neighbors in graph.adjacency.items():
        for target_id in neighbors:
            if source_id < target_id:
                copied.add_edge(source_id, target_id)
    return copied


def build_phase1_civilization(config: SimulationConfig, seed: int, graph: TopologyGraph) -> Civilization:
    civilization = Civilization(config, random.Random(seed))
    civilization.network = clone_graph(graph)
    civilization.connected_components = civilization.current_component_count()
    civilization.previous_component_count = civilization.connected_components
    civilization.refresh_aggregates()
    return civilization


def apply_initial_failures(civilization: Civilization, node_ids: Iterable[int]) -> List[int]:
    targeted_ids: List[int] = []
    node_lookup = {node.node_id: node for node in civilization.nodes}
    failure_ceiling = max(0.0, FAILURE_STABILITY_THRESHOLD - 0.05)
    for node_id in node_ids:
        node = node_lookup.get(node_id)
        if node is None:
            continue
        node.governance_stability = min(node.governance_stability, failure_ceiling)
        node.cooperation = clamp(node.cooperation - 0.18, 0.0, 1.0)
        node.trust_memory = clamp(node.trust_memory - 0.12, 0.0, 1.0)
        targeted_ids.append(node_id)
    if targeted_ids:
        for node_id in targeted_ids:
            node = node_lookup[node_id]
            for neighbor in civilization.neighbor_nodes(node, node_lookup=node_lookup):
                neighbor.cooperation = clamp(
                    neighbor.cooperation - civilization.config.contagion_penalty,
                    0.0,
                    1.0,
                )
                civilization.exposed_node_ids.add(neighbor.node_id)
        civilization.failed_node_ids.update(targeted_ids)
        civilization.exposed_node_ids.difference_update(civilization.failed_node_ids)
        civilization.initial_failure_count += len(targeted_ids)
        civilization.refresh_aggregates()
    return targeted_ids
