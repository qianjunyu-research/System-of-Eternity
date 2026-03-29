from __future__ import annotations

import argparse
import csv
import json
import random
import statistics
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import networkx as nx  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    nx = None


NETWORK_TOPOLOGY_NODE_COUNT = 60
FAILURE_STABILITY_THRESHOLD = 0.30
TOPOLOGY_CHOICES = {
    "none",
    "random",
    "scale-free",
    "small-world",
    "federation",
}
HUB_FAILURE_MODES = {
    "remove",
    "stability",
}
SYSTEMIC_SHOCK_TARGETS = {
    "random",
    "hubs",
}


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


class TopologyGraph:
    def __init__(self, nodes: List[int]) -> None:
        self.adjacency: Dict[int, set[int]] = {node_id: set() for node_id in nodes}

    def add_node(self, node_id: int) -> None:
        self.adjacency.setdefault(node_id, set())

    def add_edge(self, source: int, target: int) -> None:
        if source == target:
            return
        self.add_node(source)
        self.add_node(target)
        self.adjacency[source].add(target)
        self.adjacency[target].add(source)

    def remove_node(self, node_id: int) -> None:
        neighbors = list(self.adjacency.get(node_id, ()))
        for neighbor in neighbors:
            self.adjacency[neighbor].discard(node_id)
        self.adjacency.pop(node_id, None)

    def remove_edge(self, source: int, target: int) -> None:
        self.adjacency.get(source, set()).discard(target)
        self.adjacency.get(target, set()).discard(source)

    def neighbors(self, node_id: int) -> List[int]:
        return list(self.adjacency.get(node_id, ()))

    def degree(self, node_id: int) -> int:
        return len(self.adjacency.get(node_id, ()))

    def number_of_nodes(self) -> int:
        return len(self.adjacency)

    def number_of_edges(self) -> int:
        return sum(len(neighbors) for neighbors in self.adjacency.values()) // 2

    def connected_components_count(self) -> int:
        return len(self.connected_components())

    def connected_components(self) -> List[set[int]]:
        components: List[set[int]] = []
        seen: set[int] = set()
        for start in self.adjacency:
            if start in seen:
                continue
            stack = [start]
            component: set[int] = set()
            while stack:
                node_id = stack.pop()
                if node_id in seen:
                    continue
                seen.add(node_id)
                component.add(node_id)
                stack.extend(neighbor for neighbor in self.adjacency[node_id] if neighbor not in seen)
            components.append(component)
        return components


def sample_weighted_unique(
    rng: random.Random,
    candidates: List[int],
    weights: List[float],
    count: int,
) -> List[int]:
    chosen: List[int] = []
    available = list(zip(candidates, weights))
    for _ in range(min(count, len(available))):
        total = sum(weight for _, weight in available)
        if total <= 0:
            chosen.append(available.pop(rng.randrange(len(available)))[0])
            continue
        pick = rng.random() * total
        cursor = 0.0
        for index, (candidate, weight) in enumerate(available):
            cursor += weight
            if pick <= cursor:
                chosen.append(candidate)
                available.pop(index)
                break
    return chosen


def build_random_topology(node_ids: List[int], rng: random.Random) -> TopologyGraph:
    graph = TopologyGraph(node_ids)
    for index, source in enumerate(node_ids):
        for target in node_ids[index + 1 :]:
            if rng.random() < 0.1:
                graph.add_edge(source, target)
    return graph


def build_scale_free_topology(node_ids: List[int], rng: random.Random) -> TopologyGraph:
    graph = TopologyGraph(node_ids)
    if len(node_ids) <= 3:
        for index, source in enumerate(node_ids):
            for target in node_ids[index + 1 :]:
                graph.add_edge(source, target)
        return graph

    seed_nodes = node_ids[:3]
    for index, source in enumerate(seed_nodes):
        for target in seed_nodes[index + 1 :]:
            graph.add_edge(source, target)

    for node_id in node_ids[3:]:
        existing = [candidate for candidate in graph.adjacency if candidate != node_id]
        weights = [graph.degree(candidate) + 1 for candidate in existing]
        targets = sample_weighted_unique(rng, existing, weights, count=2)
        for target in targets:
            graph.add_edge(node_id, target)
    return graph


def build_small_world_topology(node_ids: List[int], rng: random.Random) -> TopologyGraph:
    graph = TopologyGraph(node_ids)
    node_count = len(node_ids)
    half_span = 2
    for index, source in enumerate(node_ids):
        for offset in range(1, half_span + 1):
            target = node_ids[(index + offset) % node_count]
            graph.add_edge(source, target)

    for index, source in enumerate(node_ids):
        for offset in range(1, half_span + 1):
            target = node_ids[(index + offset) % node_count]
            if rng.random() >= 0.1:
                continue
            graph.adjacency[source].discard(target)
            graph.adjacency[target].discard(source)
            forbidden = graph.adjacency[source] | {source}
            candidates = [candidate for candidate in node_ids if candidate not in forbidden]
            if not candidates:
                graph.add_edge(source, target)
                continue
            graph.add_edge(source, rng.choice(candidates))
    return graph


def build_federation_topology(node_ids: List[int], rng: random.Random) -> TopologyGraph:
    graph = TopologyGraph(node_ids)
    blocks = [
        node_ids[0:15],
        node_ids[15:30],
        node_ids[30:45],
        node_ids[45:60],
    ]
    probabilities = [
        [0.30, 0.02, 0.02, 0.02],
        [0.02, 0.30, 0.02, 0.02],
        [0.02, 0.02, 0.30, 0.02],
        [0.02, 0.02, 0.02, 0.30],
    ]
    for block_index, source_block in enumerate(blocks):
        for target_block_index, target_block in enumerate(blocks[block_index:], start=block_index):
            edge_probability = probabilities[block_index][target_block_index]
            for source_position, source in enumerate(source_block):
                target_iterable = (
                    target_block[source_position + 1 :]
                    if block_index == target_block_index
                    else target_block
                )
                for target in target_iterable:
                    if rng.random() < edge_probability:
                        graph.add_edge(source, target)
    return graph


def build_topology_graph(
    topology: str,
    node_ids: List[int],
    rng: random.Random,
) -> TopologyGraph:
    if topology == "random":
        return build_random_topology(node_ids, rng)
    if topology == "scale-free":
        return build_scale_free_topology(node_ids, rng)
    if topology == "small-world":
        return build_small_world_topology(node_ids, rng)
    if topology == "federation":
        return build_federation_topology(node_ids, rng)
    return TopologyGraph(node_ids)


@dataclass(frozen=True)
class SimulationConfig:
    years: int = 1000
    step_years: int = 10
    initial_nodes: int = 50
    initial_population: int = 1_000_000
    initial_tech: float = 1.0
    initial_automation: float = 0.30
    initial_ai: float = 0.20
    initial_protocol_cohesion: float = 0.65
    abundance_threshold: float = 0.70
    ai_superintelligence: float = 3.0
    automation_growth_multiplier: float = 1.0
    ai_growth_multiplier: float = 1.0
    cooperation_multiplier: float = 1.0
    enable_bureaucratic_layer: bool = False
    topology: str = "none"
    contagion_penalty: float = 0.05
    systemic_shock_year: Optional[int] = None
    systemic_shock_count: int = 0
    systemic_shock_stability: float = 0.10
    systemic_shock_target: str = "random"
    hub_failure_year: Optional[int] = None
    hub_failure_mode: str = "remove"
    hub_failure_stability: float = 0.10
    betrayal_year: Optional[int] = None
    betrayal_fraction: float = 0.0
    trust_memory_decay: float = 0.0
    cooperation_collapse_threshold: float = 0.80
    recovery_window_years: int = 100
    infiltration_year: Optional[int] = None
    infiltration_fraction: float = 0.10
    infiltration_trust_damage: float = 0.03
    infiltration_cooperation_damage: float = 0.015
    enable_local_defense: bool = False
    defense_trust_threshold: float = 0.30
    defense_consecutive_steps: int = 10
    enable_trust_repair: bool = False
    reconnect_probability: float = 0.05
    reconnect_cooperation_threshold: float = 0.60
    repair_reinforcement_threshold: float = 0.80
    repair_reinforcement_steps: int = 20
    repair_reinforcement_gain: float = 0.05
    enable_trust_signal_propagation: bool = False
    trust_signal_threshold: float = 0.80
    trust_signal_boost: float = 0.10
    trust_signal_max_distance: int = 2
    enable_group_coordination_boost: bool = False
    group_boost_neighbor_count: int = 3
    group_boost_amount: float = 0.05
    proposal_rate_constant: float = 1.00
    governance_bandwidth_base: float = 0.15
    governance_bandwidth_tech_multiplier: float = 1.20
    critical_backlog_threshold: float = 0.90
    proposal_quota_per_node: float = 0.18
    quota_cooperation_penalty: float = 0.22
    human_control_penalty_per_delegation: float = 0.20
    ai_delegation_beta_multiplier: float = 2.40
    foundational_veto_stability_penalty: float = 0.14
    foundational_veto_tech_pause_cost: float = 0.10
    foundational_veto_freeze_steps: int = 5
    omega_shock_year: Optional[int] = None
    omega_shock_factor: float = 500.0
    governance_survival_threshold: float = 0.50

    def __post_init__(self) -> None:
        if self.years <= 0:
            raise ValueError("years must be positive")
        if self.step_years <= 0:
            raise ValueError("step_years must be positive")
        if self.years % self.step_years != 0:
            raise ValueError("years must be divisible by step_years")
        if self.initial_nodes < 2:
            raise ValueError("initial_nodes must be at least 2")
        if not 0.0 <= self.initial_protocol_cohesion <= 1.0:
            raise ValueError("initial_protocol_cohesion must be between 0 and 1")
        if self.automation_growth_multiplier <= 0:
            raise ValueError("automation_growth_multiplier must be positive")
        if self.ai_growth_multiplier <= 0:
            raise ValueError("ai_growth_multiplier must be positive")
        if self.cooperation_multiplier <= 0:
            raise ValueError("cooperation_multiplier must be positive")
        if self.topology not in TOPOLOGY_CHOICES:
            raise ValueError(f"topology must be one of {sorted(TOPOLOGY_CHOICES)}")
        if self.contagion_penalty < 0:
            raise ValueError("contagion_penalty must be non-negative")
        if self.systemic_shock_year is not None and self.systemic_shock_year < 0:
            raise ValueError("systemic_shock_year must be non-negative")
        if self.systemic_shock_count < 0:
            raise ValueError("systemic_shock_count must be non-negative")
        if not 0.0 <= self.systemic_shock_stability <= 1.0:
            raise ValueError("systemic_shock_stability must be between 0 and 1")
        if self.systemic_shock_target not in SYSTEMIC_SHOCK_TARGETS:
            raise ValueError(
                f"systemic_shock_target must be one of {sorted(SYSTEMIC_SHOCK_TARGETS)}"
            )
        if self.hub_failure_year is not None and self.hub_failure_year < 0:
            raise ValueError("hub_failure_year must be non-negative")
        if self.hub_failure_mode not in HUB_FAILURE_MODES:
            raise ValueError(f"hub_failure_mode must be one of {sorted(HUB_FAILURE_MODES)}")
        if not 0.0 <= self.hub_failure_stability <= 1.0:
            raise ValueError("hub_failure_stability must be between 0 and 1")
        if self.betrayal_year is not None and self.betrayal_year < 0:
            raise ValueError("betrayal_year must be non-negative")
        if not 0.0 <= self.betrayal_fraction <= 1.0:
            raise ValueError("betrayal_fraction must be between 0 and 1")
        if not 0.0 <= self.trust_memory_decay <= 1.0:
            raise ValueError("trust_memory_decay must be between 0 and 1")
        if not 0.0 < self.cooperation_collapse_threshold <= 1.0:
            raise ValueError("cooperation_collapse_threshold must be between 0 and 1")
        if self.recovery_window_years <= 0:
            raise ValueError("recovery_window_years must be positive")
        if self.infiltration_year is not None and self.infiltration_year < 0:
            raise ValueError("infiltration_year must be non-negative")
        if not 0.0 <= self.infiltration_fraction <= 1.0:
            raise ValueError("infiltration_fraction must be between 0 and 1")
        if self.infiltration_trust_damage < 0:
            raise ValueError("infiltration_trust_damage must be non-negative")
        if self.infiltration_cooperation_damage < 0:
            raise ValueError("infiltration_cooperation_damage must be non-negative")
        if not 0.0 < self.defense_trust_threshold < 1.0:
            raise ValueError("defense_trust_threshold must be between 0 and 1")
        if self.defense_consecutive_steps <= 0:
            raise ValueError("defense_consecutive_steps must be positive")
        if not 0.0 <= self.reconnect_probability <= 1.0:
            raise ValueError("reconnect_probability must be between 0 and 1")
        if not 0.0 <= self.reconnect_cooperation_threshold <= 1.0:
            raise ValueError("reconnect_cooperation_threshold must be between 0 and 1")
        if not 0.0 <= self.repair_reinforcement_threshold <= 1.0:
            raise ValueError("repair_reinforcement_threshold must be between 0 and 1")
        if self.repair_reinforcement_steps <= 0:
            raise ValueError("repair_reinforcement_steps must be positive")
        if self.repair_reinforcement_gain < 0:
            raise ValueError("repair_reinforcement_gain must be non-negative")
        if not 0.0 <= self.trust_signal_threshold <= 1.0:
            raise ValueError("trust_signal_threshold must be between 0 and 1")
        if self.trust_signal_boost < 0:
            raise ValueError("trust_signal_boost must be non-negative")
        if self.trust_signal_max_distance <= 0:
            raise ValueError("trust_signal_max_distance must be positive")
        if self.group_boost_neighbor_count <= 0:
            raise ValueError("group_boost_neighbor_count must be positive")
        if self.group_boost_amount < 0:
            raise ValueError("group_boost_amount must be non-negative")
        if self.proposal_rate_constant <= 0:
            raise ValueError("proposal_rate_constant must be positive")
        if self.governance_bandwidth_base <= 0:
            raise ValueError("governance_bandwidth_base must be positive")
        if self.governance_bandwidth_tech_multiplier <= 0:
            raise ValueError("governance_bandwidth_tech_multiplier must be positive")
        if self.critical_backlog_threshold <= 0:
            raise ValueError("critical_backlog_threshold must be positive")
        if self.proposal_quota_per_node <= 0:
            raise ValueError("proposal_quota_per_node must be positive")
        if self.quota_cooperation_penalty < 0:
            raise ValueError("quota_cooperation_penalty must be non-negative")
        if self.human_control_penalty_per_delegation < 0:
            raise ValueError("human_control_penalty_per_delegation must be non-negative")
        if self.ai_delegation_beta_multiplier <= 1:
            raise ValueError("ai_delegation_beta_multiplier must be greater than 1")
        if self.foundational_veto_stability_penalty < 0:
            raise ValueError("foundational_veto_stability_penalty must be non-negative")
        if self.foundational_veto_tech_pause_cost < 0:
            raise ValueError("foundational_veto_tech_pause_cost must be non-negative")
        if self.foundational_veto_freeze_steps <= 0:
            raise ValueError("foundational_veto_freeze_steps must be positive")
        if self.omega_shock_year is not None and self.omega_shock_year < 0:
            raise ValueError("omega_shock_year must be non-negative")
        if self.omega_shock_factor <= 1:
            raise ValueError("omega_shock_factor must be greater than 1")
        if not 0 < self.governance_survival_threshold < 1:
            raise ValueError("governance_survival_threshold must be between 0 and 1")

    @property
    def steps(self) -> int:
        return self.years // self.step_years


@dataclass
class Node:
    population: int
    tech: float
    ideology: float
    governance_stability: float
    cooperation: float = 0.7
    trust_memory: float = 0.7
    defection_drive: float = 0.0
    ai_level: float = 0.0
    proposal_rate: float = 0.0
    is_omega: bool = False
    is_infiltrator: bool = False
    node_id: int = -1

    @classmethod
    def random_initial(cls, rng: random.Random) -> "Node":
        cooperation = rng.uniform(0.55, 0.95)
        return cls(
            population=rng.randint(50_000, 200_000),
            tech=rng.uniform(0.8, 1.2),
            ideology=rng.random(),
            governance_stability=rng.uniform(0.6, 1.0),
            cooperation=cooperation,
            trust_memory=cooperation,
        )


class Civilization:
    def __init__(self, config: SimulationConfig, rng: random.Random) -> None:
        self.config = config
        self.rng = rng
        self.next_node_id = 0
        self.network: Optional[TopologyGraph] = None
        self.connected_components = 1
        self.previous_component_count = 1
        self.fragmentation_count = 0
        self.local_cooperation_mean = config.initial_protocol_cohesion
        self.trust_memory_mean = config.initial_protocol_cohesion
        self.failed_node_ids: set[int] = set()
        self.exposed_node_ids: set[int] = set()
        self.initial_failure_count = 0
        self.secondary_failure_count = 0
        self.systemic_shock_applied = False
        self.hub_failure_applied = False
        self.betrayal_applied = False
        self.infiltration_applied = False
        self.pairwise_trust: Dict[tuple[int, int], float] = {}
        self.low_trust_steps: Dict[tuple[int, int], int] = {}
        self.detected_adversaries: Dict[int, set[int]] = {}
        self.disconnected_neighbors: Dict[int, set[int]] = {}
        self.severed_edge_pairs: set[tuple[int, int]] = set()
        self.restored_edge_pairs: set[tuple[int, int]] = set()
        self.repair_high_cooperation_steps: Dict[tuple[int, int], int] = {}
        self.signal_receivers_ever: set[int] = set()
        self.defense_edge_cuts = 0
        self.reconnection_events = 0
        self.total_infiltrators_injected = 0
        self.infiltrator_isolation_years: Dict[int, int] = {}
        self.nodes = self._create_initial_nodes()
        if self.uses_topology:
            self.network = build_topology_graph(
                self.config.topology,
                [node.node_id for node in self.nodes],
                self.rng,
            )
        if self.uses_local_defense:
            self.initialize_pairwise_trust()
        self.automation = config.initial_automation
        self.ai_capability = config.initial_ai
        self.protocol_cohesion = config.initial_protocol_cohesion
        self.tech_level = config.initial_tech
        self.population = config.initial_population
        self.governance_stability = 0.75
        self.ideology_spread = 0.0
        self.abundance_index = 0.0
        self.abundance_transition_year: Optional[int] = None
        self.ai_superintelligence_year: Optional[int] = None
        self.refresh_aggregates()
        self.previous_component_count = self.connected_components

    @property
    def uses_topology(self) -> bool:
        return self.config.topology != "none"

    @property
    def uses_trust_layer(self) -> bool:
        return self.uses_topology and self.config.betrayal_year is not None

    @property
    def uses_infiltration_layer(self) -> bool:
        return (
            self.uses_topology
            and self.config.infiltration_year is not None
            and self.config.infiltration_fraction > 0
        )

    @property
    def uses_local_defense(self) -> bool:
        return self.uses_topology and self.config.enable_local_defense

    @property
    def uses_trust_repair(self) -> bool:
        return self.uses_local_defense and self.config.enable_trust_repair

    @property
    def uses_trust_signal_propagation(self) -> bool:
        return self.uses_trust_repair and self.config.enable_trust_signal_propagation

    def infiltration_nodes(self) -> List[Node]:
        return [node for node in self.nodes if node.is_infiltrator]

    def organic_nodes(self) -> List[Node]:
        return [node for node in self.nodes if not node.is_infiltrator]

    def cleanup_node_state(self, node_id: int) -> None:
        self.detected_adversaries.pop(node_id, None)
        self.disconnected_neighbors.pop(node_id, None)
        for source_id in list(self.detected_adversaries):
            self.detected_adversaries[source_id].discard(node_id)
            if not self.detected_adversaries[source_id]:
                self.detected_adversaries.pop(source_id, None)
        for source_id in list(self.disconnected_neighbors):
            self.disconnected_neighbors[source_id].discard(node_id)
            if not self.disconnected_neighbors[source_id]:
                self.disconnected_neighbors.pop(source_id, None)
        for key in [key for key in self.pairwise_trust if node_id in key]:
            self.pairwise_trust.pop(key, None)
            self.low_trust_steps.pop(key, None)
        for key in [key for key in self.repair_high_cooperation_steps if node_id in key]:
            self.repair_high_cooperation_steps.pop(key, None)
        self.severed_edge_pairs = {
            key for key in self.severed_edge_pairs if node_id not in key
        }
        self.restored_edge_pairs = {
            key for key in self.restored_edge_pairs if node_id not in key
        }
        self.infiltrator_isolation_years.pop(node_id, None)
        self.signal_receivers_ever.discard(node_id)

    def initialize_pairwise_trust(self) -> None:
        if not self.network:
            return
        node_lookup = {node.node_id: node for node in self.nodes}
        for node in self.nodes:
            self.detected_adversaries.setdefault(node.node_id, set())
            self.disconnected_neighbors.setdefault(node.node_id, set())
        for node in self.nodes:
            for neighbor_id in self.network.neighbors(node.node_id):
                if neighbor_id not in node_lookup:
                    continue
                key = (node.node_id, neighbor_id)
                self.pairwise_trust[key] = node.trust_memory
                self.low_trust_steps.setdefault(key, 0)

    def initialize_pairwise_trust_for_node(self, node: Node) -> None:
        if not self.uses_local_defense or not self.network:
            return
        node_lookup = {candidate.node_id: candidate for candidate in self.nodes}
        self.detected_adversaries.setdefault(node.node_id, set())
        self.disconnected_neighbors.setdefault(node.node_id, set())
        for neighbor_id in self.network.neighbors(node.node_id):
            neighbor = node_lookup.get(neighbor_id)
            if neighbor is None:
                continue
            self.detected_adversaries.setdefault(neighbor_id, set())
            self.disconnected_neighbors.setdefault(neighbor_id, set())
            self.pairwise_trust[(node.node_id, neighbor_id)] = node.trust_memory
            self.pairwise_trust[(neighbor_id, node.node_id)] = neighbor.trust_memory
            self.low_trust_steps[(node.node_id, neighbor_id)] = 0
            self.low_trust_steps[(neighbor_id, node.node_id)] = 0

    def allocate_node_id(self) -> int:
        node_id = self.next_node_id
        self.next_node_id += 1
        return node_id

    def current_component_count(self) -> int:
        if not self.network or self.network.number_of_nodes() == 0:
            return 1
        return self.network.connected_components_count()

    def largest_component_ratio(self) -> float:
        if not self.network or not self.nodes:
            return 1.0
        return self.largest_component_size() / max(1, len(self.nodes))

    def largest_component_size(self) -> int:
        if not self.network or not self.nodes:
            return len(self.nodes)
        return max(
            (len(component) for component in self.network.connected_components()),
            default=0,
        )

    def update_fragmentation_count(self) -> None:
        if not self.uses_topology:
            return
        self.connected_components = self.current_component_count()
        if self.connected_components > self.previous_component_count:
            self.fragmentation_count += self.connected_components - self.previous_component_count
        self.previous_component_count = self.connected_components

    def neighbor_nodes(self, node: Node, node_lookup: Optional[Dict[int, Node]] = None) -> List[Node]:
        if not self.network:
            return []
        if node_lookup is None:
            node_lookup = {candidate.node_id: candidate for candidate in self.nodes}
        return [
            node_lookup[neighbor_id]
            for neighbor_id in self.network.neighbors(node.node_id)
            if neighbor_id in node_lookup
        ]

    def neighbor_average(
        self,
        node: Node,
        attribute: str,
        default: float,
        node_lookup: Optional[Dict[int, Node]] = None,
    ) -> float:
        neighbors = self.neighbor_nodes(node, node_lookup=node_lookup)
        if not neighbors:
            return default
        return statistics.fmean(getattr(neighbor, attribute) for neighbor in neighbors)

    def add_node_to_network(self, node: Node, parent: Optional[Node] = None) -> None:
        if not self.network:
            return
        self.network.add_node(node.node_id)
        existing = [candidate for candidate in self.nodes if candidate.node_id != node.node_id]
        if not existing:
            return
        if parent is None:
            parent = self.rng.choice(existing)
        self.network.add_edge(node.node_id, parent.node_id)
        parent_neighbor_ids = [
            neighbor_id
            for neighbor_id in self.network.neighbors(parent.node_id)
            if neighbor_id != node.node_id
        ]
        extra_links = min(2, len(parent_neighbor_ids))
        if extra_links:
            for neighbor_id in self.rng.sample(parent_neighbor_ids, k=extra_links):
                self.network.add_edge(node.node_id, neighbor_id)
        if self.uses_local_defense:
            self.initialize_pairwise_trust_for_node(node)

    def remove_node(self, node: Node) -> None:
        if node not in self.nodes:
            return
        self.nodes.remove(node)
        if self.network:
            self.network.remove_node(node.node_id)
        self.cleanup_node_state(node.node_id)

    def sever_connection(self, source_id: int, target_id: int) -> None:
        if not self.network:
            return
        self.network.remove_edge(source_id, target_id)
        for key in ((source_id, target_id), (target_id, source_id)):
            self.pairwise_trust.pop(key, None)
            self.low_trust_steps.pop(key, None)
        self.detected_adversaries.get(source_id, set()).add(target_id)
        self.detected_adversaries.get(target_id, set()).add(source_id)
        self.disconnected_neighbors.setdefault(source_id, set()).add(target_id)
        self.disconnected_neighbors.setdefault(target_id, set()).add(source_id)
        undirected_pair = tuple(sorted((source_id, target_id)))
        self.severed_edge_pairs.add(undirected_pair)
        self.repair_high_cooperation_steps.pop(undirected_pair, None)
        self.defense_edge_cuts += 1
        self.update_fragmentation_count()

    def restore_connection(self, source_id: int, target_id: int) -> None:
        if not self.network:
            return
        self.network.add_edge(source_id, target_id)
        for key in ((source_id, target_id), (target_id, source_id)):
            self.pairwise_trust[key] = 0.50
            self.low_trust_steps[key] = 0
        self.detected_adversaries.get(source_id, set()).discard(target_id)
        self.detected_adversaries.get(target_id, set()).discard(source_id)
        self.disconnected_neighbors.get(source_id, set()).discard(target_id)
        self.disconnected_neighbors.get(target_id, set()).discard(source_id)
        undirected_pair = tuple(sorted((source_id, target_id)))
        self.restored_edge_pairs.add(undirected_pair)
        self.repair_high_cooperation_steps[undirected_pair] = 0
        self.reconnection_events += 1
        self.update_fragmentation_count()

    def apply_topology_contagion(self) -> List[str]:
        if not self.uses_topology:
            return []
        events: List[str] = []
        new_failures = [
            node
            for node in self.nodes
            if node.node_id not in self.failed_node_ids
            and node.governance_stability < FAILURE_STABILITY_THRESHOLD
        ]
        if new_failures:
            secondary_failures = sum(
                1 for node in new_failures if node.node_id in self.exposed_node_ids
            )
            self.initial_failure_count += len(new_failures)
            self.secondary_failure_count += secondary_failures
            if secondary_failures:
                events.append("contagion_spread")
            node_lookup = {node.node_id: node for node in self.nodes}
            for failed_node in new_failures:
                for neighbor in self.neighbor_nodes(failed_node, node_lookup=node_lookup):
                    neighbor.cooperation = clamp(
                        neighbor.cooperation - self.config.contagion_penalty,
                        0.0,
                        1.0,
                    )
                    if self.uses_trust_layer:
                        neighbor.trust_memory = clamp(
                            neighbor.trust_memory - 0.50 * self.config.contagion_penalty,
                            0.0,
                            1.0,
                        )
                    if neighbor.node_id not in self.failed_node_ids:
                        self.exposed_node_ids.add(neighbor.node_id)
            self.failed_node_ids.update(node.node_id for node in new_failures)
            self.exposed_node_ids.difference_update(self.failed_node_ids)
            events.append("local_failure")
        self.update_fragmentation_count()
        return events

    def apply_systemic_shock(self, year: int) -> List[str]:
        if (
            not self.uses_topology
            or self.systemic_shock_applied
            or self.config.systemic_shock_year is None
            or year < self.config.systemic_shock_year
            or self.config.systemic_shock_count <= 0
        ):
            return []
        shock_count = min(self.config.systemic_shock_count, len(self.nodes))
        if self.config.systemic_shock_target == "hubs" and self.network:
            shocked_nodes = sorted(
                self.nodes,
                key=lambda node: (
                    self.network.degree(node.node_id),
                    node.population,
                    node.tech,
                ),
                reverse=True,
            )[:shock_count]
        else:
            shocked_nodes = self.rng.sample(self.nodes, k=shock_count)
        node_lookup = {node.node_id: node for node in self.nodes}
        affected_neighbor_ids: set[int] = set()
        for node in shocked_nodes:
            for neighbor in self.neighbor_nodes(node, node_lookup=node_lookup):
                if neighbor.node_id != node.node_id:
                    affected_neighbor_ids.add(neighbor.node_id)
        for neighbor_id in affected_neighbor_ids:
            if neighbor_id in node_lookup:
                node_lookup[neighbor_id].cooperation = clamp(
                    node_lookup[neighbor_id].cooperation - self.config.contagion_penalty,
                    0.0,
                    1.0,
                )
                if neighbor_id not in self.failed_node_ids:
                    self.exposed_node_ids.add(neighbor_id)
        if self.config.hub_failure_mode == "remove":
            for node in list(shocked_nodes):
                if node in self.nodes:
                    self.remove_node(node)
            self.update_fragmentation_count()
            self.systemic_shock_applied = True
            return ["systemic_shock", "shock_removed"]
        for node in shocked_nodes:
            node.governance_stability = self.config.systemic_shock_stability
        self.systemic_shock_applied = True
        return ["systemic_shock"]

    def select_hub_node(self) -> Optional[Node]:
        if not self.network or not self.nodes:
            return None
        return max(
            self.nodes,
            key=lambda node: (
                self.network.degree(node.node_id),
                node.population,
                node.tech,
            ),
        )

    def apply_hub_failure(self, year: int) -> List[str]:
        if (
            not self.uses_topology
            or self.hub_failure_applied
            or self.config.hub_failure_year is None
            or year < self.config.hub_failure_year
        ):
            return []
        hub = self.select_hub_node()
        if hub is None:
            return []
        node_lookup = {node.node_id: node for node in self.nodes}
        neighbors = self.neighbor_nodes(hub, node_lookup=node_lookup)
        for neighbor in neighbors:
            neighbor.cooperation = clamp(
                neighbor.cooperation - self.config.contagion_penalty,
                0.0,
                1.0,
            )
            if self.uses_trust_layer:
                neighbor.trust_memory = clamp(
                    neighbor.trust_memory - 0.50 * self.config.contagion_penalty,
                    0.0,
                    1.0,
                )
            if neighbor.node_id not in self.failed_node_ids:
                self.exposed_node_ids.add(neighbor.node_id)
        self.hub_failure_applied = True
        if self.config.hub_failure_mode == "remove":
            self.remove_node(hub)
            self.update_fragmentation_count()
            return ["hub_failure", "hub_removed"]
        hub.governance_stability = self.config.hub_failure_stability
        return ["hub_failure", "hub_destabilized"]

    def _create_initial_nodes(self) -> List[Node]:
        node_count = (
            NETWORK_TOPOLOGY_NODE_COUNT if self.uses_topology else self.config.initial_nodes
        )
        nodes = [Node.random_initial(self.rng) for _ in range(node_count)]
        raw_total = sum(node.population for node in nodes)
        scale = self.config.initial_population / raw_total
        for node in nodes:
            node.population = max(1_000, int(node.population * scale))
            node.node_id = self.allocate_node_id()
        return nodes

    def select_betrayal_nodes(self) -> List[Node]:
        candidates = self.organic_nodes() or self.nodes
        if self.config.betrayal_fraction > 0:
            betrayal_count = max(1, round(len(candidates) * self.config.betrayal_fraction))
            if self.network:
                return sorted(
                    candidates,
                    key=lambda node: (
                        self.network.degree(node.node_id),
                        node.cooperation,
                        node.population,
                    ),
                    reverse=True,
                )[:betrayal_count]
            return sorted(
                candidates,
                key=lambda node: (node.cooperation, node.population),
                reverse=True,
            )[:betrayal_count]
        if self.network:
            return [
                max(
                    candidates,
                    key=lambda node: (
                        self.network.degree(node.node_id),
                        node.cooperation,
                        node.population,
                    ),
                )
            ]
        return [max(candidates, key=lambda node: (node.cooperation, node.population))]

    def apply_betrayal_event(self, year: int) -> List[str]:
        if (
            not self.uses_trust_layer
            or self.betrayal_applied
            or self.config.betrayal_year is None
            or year < self.config.betrayal_year
        ):
            return []
        betrayed_nodes = self.select_betrayal_nodes()
        if not betrayed_nodes:
            return []
        node_lookup = {node.node_id: node for node in self.nodes}
        for node in betrayed_nodes:
            node.cooperation = clamp(min(node.cooperation, 0.22), 0.0, 1.0)
            node.trust_memory = clamp(min(node.trust_memory, 0.25), 0.0, 1.0)
            node.governance_stability = clamp(node.governance_stability - 0.05, 0.0, 1.0)
            node.defection_drive = 0.70
            for neighbor in self.neighbor_nodes(node, node_lookup=node_lookup):
                neighbor.cooperation = clamp(neighbor.cooperation - 0.06, 0.0, 1.0)
                neighbor.trust_memory = clamp(neighbor.trust_memory - 0.10, 0.0, 1.0)
                neighbor.defection_drive = clamp(neighbor.defection_drive + 0.03, 0.0, 1.0)
        self.betrayal_applied = True
        return ["betrayal_event"]

    def apply_infiltration_event(self, year: int) -> List[str]:
        if (
            not self.uses_infiltration_layer
            or self.infiltration_applied
            or self.config.infiltration_year is None
            or year < self.config.infiltration_year
        ):
            return []
        hosts = self.organic_nodes()
        if not hosts:
            return []
        infiltration_count = max(1, round(len(hosts) * self.config.infiltration_fraction))
        for _ in range(infiltration_count):
            parent = self.rng.choice(hosts)
            infiltrator = Node(
                population=max(1_000, int(parent.population * 0.02)),
                tech=max(0.5, parent.tech * self.rng.uniform(0.85, 1.05)),
                ideology=parent.ideology,
                governance_stability=0.65,
                cooperation=0.0,
                trust_memory=0.0,
                defection_drive=1.0,
                is_infiltrator=True,
            )
            infiltrator.node_id = self.allocate_node_id()
            self.nodes.append(infiltrator)
            self.add_node_to_network(infiltrator, parent=parent)
            self.total_infiltrators_injected += 1
        self.infiltration_applied = True
        return ["infiltration_event"]

    def apply_infiltration_pressure(self) -> List[str]:
        infiltrators = self.infiltration_nodes()
        if not infiltrators:
            return []
        node_lookup = {node.node_id: node for node in self.nodes}
        for infiltrator in infiltrators:
            infiltrator.cooperation = 0.0
            infiltrator.trust_memory = 0.0
            infiltrator.defection_drive = 1.0
            infiltrator.governance_stability = max(infiltrator.governance_stability, 0.65)
            for neighbor in self.neighbor_nodes(infiltrator, node_lookup=node_lookup):
                if neighbor.is_infiltrator:
                    continue
                neighbor.trust_memory = clamp(
                    neighbor.trust_memory - self.config.infiltration_trust_damage,
                    0.0,
                    1.0,
                )
                neighbor.cooperation = clamp(
                    neighbor.cooperation - self.config.infiltration_cooperation_damage,
                    0.0,
                    1.0,
                )
                neighbor.defection_drive = clamp(
                    neighbor.defection_drive + 0.02,
                    0.0,
                    1.0,
                )
        return ["infiltration_pressure"]

    def observed_pairwise_trust(self, observer: Node, neighbor: Node) -> float:
        if neighbor.is_infiltrator:
            return 0.0
        return clamp(
            0.65 * neighbor.cooperation
            + 0.20 * neighbor.trust_memory
            + 0.10 * neighbor.governance_stability
            - 0.15 * neighbor.defection_drive,
            0.0,
            1.0,
        )

    def update_infiltrator_isolation(self, year: int) -> int:
        if not self.network:
            return 0
        new_isolations = 0
        for infiltrator in self.infiltration_nodes():
            if infiltrator.node_id in self.infiltrator_isolation_years:
                continue
            if self.network.degree(infiltrator.node_id) == 0:
                self.infiltrator_isolation_years[infiltrator.node_id] = year
                new_isolations += 1
        return new_isolations

    def apply_local_defense(self, year: int) -> List[str]:
        if not self.uses_local_defense or not self.network:
            return []
        events: List[str] = []
        node_lookup = {node.node_id: node for node in self.nodes}
        edges_to_sever: set[tuple[int, int]] = set()
        for node in self.nodes:
            if node.node_id not in node_lookup:
                continue
            self.detected_adversaries.setdefault(node.node_id, set())
            for neighbor in self.neighbor_nodes(node, node_lookup=node_lookup):
                key = (node.node_id, neighbor.node_id)
                current_trust = self.pairwise_trust.get(key, node.trust_memory)
                observed_trust = self.observed_pairwise_trust(node, neighbor)
                if observed_trust < current_trust:
                    current_trust = clamp(
                        current_trust + 0.60 * (observed_trust - current_trust),
                        0.0,
                        1.0,
                    )
                else:
                    current_trust = clamp(
                        current_trust + self.config.trust_memory_decay * (observed_trust - current_trust),
                        0.0,
                        1.0,
                    )
                self.pairwise_trust[key] = current_trust
                low_steps = self.low_trust_steps.get(key, 0)
                if current_trust < self.config.defense_trust_threshold:
                    low_steps += 1
                else:
                    low_steps = 0
                self.low_trust_steps[key] = low_steps
                if low_steps >= self.config.defense_consecutive_steps:
                    self.detected_adversaries[node.node_id].add(neighbor.node_id)
                    edges_to_sever.add(tuple(sorted((node.node_id, neighbor.node_id))))
        if edges_to_sever:
            events.append("defense_activation")
            for source_id, target_id in sorted(edges_to_sever):
                if target_id in self.network.neighbors(source_id):
                    self.sever_connection(source_id, target_id)
            if edges_to_sever:
                events.append("defense_severed_edge")
        isolated_now = self.update_infiltrator_isolation(year)
        if isolated_now:
            events.append("adversary_isolated")
        return events

    def apply_trust_repair(self) -> List[str]:
        if not self.uses_trust_repair or not self.network:
            return []
        events: List[str] = []
        node_lookup = {node.node_id: node for node in self.nodes}
        reconnect_pairs: List[tuple[int, int]] = []
        for source_id, targets in self.disconnected_neighbors.items():
            source = node_lookup.get(source_id)
            if source is None or source.is_infiltrator:
                continue
            for target_id in list(targets):
                if source_id >= target_id:
                    continue
                target = node_lookup.get(target_id)
                if target is None or target.is_infiltrator:
                    continue
                if target_id in self.network.neighbors(source_id):
                    self.disconnected_neighbors[source_id].discard(target_id)
                    self.disconnected_neighbors.get(target_id, set()).discard(source_id)
                    continue
                if (
                    source.cooperation > self.config.reconnect_cooperation_threshold
                    and target.cooperation > self.config.reconnect_cooperation_threshold
                    and self.rng.random() < self.config.reconnect_probability
                ):
                    reconnect_pairs.append((source_id, target_id))
        for source_id, target_id in reconnect_pairs:
            self.restore_connection(source_id, target_id)
        if reconnect_pairs:
            events.append("trust_repair_reconnect")

        reinforcement_events = 0
        for pair in list(self.restored_edge_pairs):
            source_id, target_id = pair
            source = node_lookup.get(source_id)
            target = node_lookup.get(target_id)
            if source is None or target is None:
                self.repair_high_cooperation_steps.pop(pair, None)
                continue
            if target_id not in self.network.neighbors(source_id):
                self.repair_high_cooperation_steps.pop(pair, None)
                continue
            if source.is_infiltrator or target.is_infiltrator:
                self.repair_high_cooperation_steps[pair] = 0
                continue
            if (
                source.cooperation > self.config.repair_reinforcement_threshold
                and target.cooperation > self.config.repair_reinforcement_threshold
            ):
                steps = self.repair_high_cooperation_steps.get(pair, 0) + 1
                if steps >= self.config.repair_reinforcement_steps:
                    for directed_pair in ((source_id, target_id), (target_id, source_id)):
                        self.pairwise_trust[directed_pair] = clamp(
                            self.pairwise_trust.get(directed_pair, 0.50)
                            + self.config.repair_reinforcement_gain,
                            0.0,
                            1.0,
                        )
                    steps = 0
                    reinforcement_events += 1
                self.repair_high_cooperation_steps[pair] = steps
            else:
                self.repair_high_cooperation_steps[pair] = 0
        if reinforcement_events:
            events.append("trust_repair_reinforcement")
        return events

    def apply_trust_signal_propagation(self) -> List[str]:
        if not self.uses_trust_signal_propagation or not self.network:
            return []
        events: List[str] = []
        node_lookup = {node.node_id: node for node in self.nodes}
        trust_boosts: Dict[tuple[int, int], float] = {}
        node_boosts: Dict[int, float] = {}
        organic_nodes = [node for node in self.nodes if not node.is_infiltrator]
        emitters = [
            node
            for node in organic_nodes
            if node.cooperation > self.config.trust_signal_threshold
            and not any(
                neighbor.is_infiltrator
                for neighbor in self.neighbor_nodes(node, node_lookup=node_lookup)
            )
        ]

        for emitter in emitters:
            frontier: List[tuple[int, int]] = [(emitter.node_id, 0)]
            seen = {emitter.node_id}
            while frontier:
                current_id, distance = frontier.pop(0)
                if distance >= self.config.trust_signal_max_distance:
                    continue
                current = node_lookup.get(current_id)
                if current is None:
                    continue
                for neighbor in self.neighbor_nodes(current, node_lookup=node_lookup):
                    if neighbor.node_id in seen or neighbor.is_infiltrator:
                        continue
                    seen.add(neighbor.node_id)
                    node_boosts[neighbor.node_id] = (
                        node_boosts.get(neighbor.node_id, 0.0) + self.config.trust_signal_boost
                    )
                    for directed_pair in (
                        (current.node_id, neighbor.node_id),
                        (neighbor.node_id, current.node_id),
                    ):
                        trust_boosts[directed_pair] = (
                            trust_boosts.get(directed_pair, 0.0) + self.config.trust_signal_boost
                        )
                    self.signal_receivers_ever.add(neighbor.node_id)
                    frontier.append((neighbor.node_id, distance + 1))

        for node_id, boost in node_boosts.items():
            node = node_lookup.get(node_id)
            if node is None:
                continue
            node.trust_memory = clamp(node.trust_memory + boost, 0.0, 1.0)
        for pair, boost in trust_boosts.items():
            self.pairwise_trust[pair] = clamp(
                self.pairwise_trust.get(pair, 0.50) + boost,
                0.0,
                1.0,
            )
        if node_boosts:
            events.append("trust_signal_propagation")

        if self.config.enable_group_coordination_boost:
            boosted_nodes = 0
            for node in organic_nodes:
                stable_neighbors = [
                    neighbor
                    for neighbor in self.neighbor_nodes(node, node_lookup=node_lookup)
                    if not neighbor.is_infiltrator
                    and neighbor.cooperation > self.config.trust_signal_threshold
                ]
                if len(stable_neighbors) >= self.config.group_boost_neighbor_count:
                    node.cooperation = clamp(
                        node.cooperation + self.config.group_boost_amount,
                        0.0,
                        1.0,
                    )
                    boosted_nodes += 1
            if boosted_nodes:
                events.append("trust_group_boost")
        return events

    def refresh_aggregates(self) -> None:
        self.population = sum(node.population for node in self.nodes)
        self.tech_level = statistics.fmean(node.tech for node in self.nodes)
        self.governance_stability = statistics.fmean(
            node.governance_stability for node in self.nodes
        )
        self.local_cooperation_mean = statistics.fmean(node.cooperation for node in self.nodes)
        self.trust_memory_mean = statistics.fmean(node.trust_memory for node in self.nodes)
        ideologies = [node.ideology for node in self.nodes]
        self.ideology_spread = statistics.pstdev(ideologies) if len(ideologies) > 1 else 0.0
        self.connected_components = self.current_component_count() if self.uses_topology else 1
        self.abundance_index = self._compute_abundance()

    def _compute_abundance(self) -> float:
        per_node_pressure = self.population / max(1, len(self.nodes)) / 25_000
        raw_score = (
            0.24 * self.tech_level
            + 0.42 * self.automation
            + 0.18 * self.ai_capability
            + 0.20 * self.protocol_cohesion
            - 0.18 * per_node_pressure
        )
        return clamp(raw_score / 2.2, 0.0, 1.5)

    def evolve_nodes(self) -> None:
        mean_ideology = statistics.fmean(node.ideology for node in self.nodes)
        node_lookup = {node.node_id: node for node in self.nodes}
        for node in self.nodes:
            if node.is_infiltrator:
                node.cooperation = 0.0
                node.trust_memory = 0.0
                node.defection_drive = 1.0
                node.governance_stability = max(node.governance_stability, 0.65)
                continue
            local_ideology = self.neighbor_average(
                node,
                "ideology",
                mean_ideology,
                node_lookup=node_lookup,
            )
            local_cooperation = self.neighbor_average(
                node,
                "cooperation",
                self.protocol_cohesion,
                node_lookup=node_lookup,
            )
            local_trust_memory = self.neighbor_average(
                node,
                "trust_memory",
                self.protocol_cohesion,
                node_lookup=node_lookup,
            )
            local_defection = self.neighbor_average(
                node,
                "defection_drive",
                0.0,
                node_lookup=node_lookup,
            )
            innovation = self.rng.uniform(0.0, 0.03)
            innovation += 0.010 * local_cooperation
            innovation += 0.006 * min(self.ai_capability, 5.0)
            innovation += 0.004 * self.abundance_index
            innovation -= 0.008 * max(0.0, 0.55 - node.governance_stability)
            node.tech = max(0.2, node.tech + innovation)

            ideology_pull = 0.06 * (local_ideology - node.ideology)
            node.ideology = clamp(
                node.ideology + ideology_pull + self.rng.uniform(-0.03, 0.03),
                0.0,
                1.0,
            )

            base_growth = 0.02 + 0.04 * self.abundance_index
            stability_term = 0.05 * (node.governance_stability - 0.5)
            diversity_term = -0.04 * abs(node.ideology - local_ideology)
            growth_noise = self.rng.uniform(-0.04, 0.04)
            population_growth = clamp(
                base_growth + stability_term + diversity_term + growth_noise,
                -0.20,
                0.18,
            )
            node.population = max(1_000, int(node.population * (1 + population_growth)))

            if self.uses_topology:
                if self.uses_trust_layer:
                    observed_trust = clamp(
                        0.75 * local_cooperation + 0.25 * local_trust_memory - 0.10 * local_defection,
                        0.0,
                        1.0,
                    )
                    trust_delta = observed_trust - node.trust_memory
                    if trust_delta < 0:
                        node.trust_memory = clamp(
                            node.trust_memory + 0.50 * trust_delta,
                            0.0,
                            1.0,
                        )
                    else:
                        node.trust_memory = clamp(
                            node.trust_memory + self.config.trust_memory_decay * trust_delta,
                            0.0,
                            1.0,
                        )
                    defection_delta = 0.12 * max(0.0, 0.40 - node.trust_memory)
                    defection_delta += 0.05 * local_defection
                    defection_delta -= 0.80 * self.config.trust_memory_decay
                    defection_delta += self.rng.uniform(-0.01, 0.01)
                    node.defection_drive = clamp(
                        node.defection_drive + defection_delta,
                        0.0,
                        1.0,
                    )
                cooperation_delta = 0.08 * (local_cooperation - node.cooperation)
                cooperation_delta += 0.05 * (node.governance_stability - 0.5)
                cooperation_delta -= 0.05 * abs(node.ideology - local_ideology)
                if self.uses_trust_layer:
                    cooperation_delta += 0.10 * (node.trust_memory - node.cooperation)
                    cooperation_delta -= 0.12 * node.defection_drive
                cooperation_delta += self.rng.uniform(-0.03, 0.03)
                node.cooperation = clamp(node.cooperation + cooperation_delta, 0.0, 1.0)

            stability_delta = 0.05 * (local_cooperation - 0.5)
            stability_delta += 0.04 * self.abundance_index
            stability_delta -= 0.12 * abs(node.ideology - local_ideology)
            if self.uses_trust_layer:
                stability_delta += 0.03 * (node.trust_memory - 0.5)
                stability_delta -= 0.05 * node.defection_drive
            stability_delta -= 0.03 * max(
                0.0, self.ai_capability - self.config.ai_superintelligence
            )
            stability_delta += self.rng.uniform(-0.04, 0.04)
            node.governance_stability = clamp(
                node.governance_stability + stability_delta,
                0.0,
                1.0,
            )

    def advance_macro(self) -> None:
        cooperation_anchor = (
            self.local_cooperation_mean if self.uses_topology else self.protocol_cohesion
        )
        automation_growth = (
            0.015 * self.tech_level
            + 0.025 * cooperation_anchor
            - 0.010 * self.ideology_spread
        )
        automation_growth *= self.config.automation_growth_multiplier
        if self.abundance_index >= self.config.abundance_threshold:
            automation_growth += 0.015 * self.config.automation_growth_multiplier
        self.automation = clamp(self.automation + automation_growth, 0.0, 4.0)

        ai_growth = 0.012 * self.tech_level + 0.010 * self.automation
        if self.governance_stability < 0.45:
            ai_growth += 0.010
        ai_growth *= self.config.ai_growth_multiplier
        self.ai_capability = max(0.0, self.ai_capability + ai_growth)

        protocol_delta = 0.04 * (self.governance_stability - 0.5)
        protocol_delta += 0.02 * min(self.automation, 1.5)
        if self.uses_topology:
            protocol_delta += 0.03 * (self.local_cooperation_mean - 0.5)
        if self.uses_trust_layer:
            protocol_delta += 0.04 * (self.trust_memory_mean - 0.5)
        protocol_delta -= 0.08 * self.ideology_spread
        protocol_delta *= self.config.cooperation_multiplier
        self.protocol_cohesion = clamp(self.protocol_cohesion + protocol_delta, 0.1, 1.0)
        self.abundance_index = self._compute_abundance()

    def step(self, year: int) -> List[str]:
        self.evolve_nodes()
        self.refresh_aggregates()
        self.advance_macro()
        events = self.apply_structural_events(year)
        events.extend(self.apply_betrayal_event(year))
        events.extend(self.apply_infiltration_event(year))
        events.extend(self.apply_hub_failure(year))
        events.extend(self.apply_systemic_shock(year))
        events.extend(self.apply_infiltration_pressure())
        events.extend(self.apply_local_defense(year))
        events.extend(self.apply_trust_repair())
        events.extend(self.apply_topology_contagion())
        events.extend(self.apply_trust_signal_propagation())
        self.refresh_aggregates()
        return events or ["steady_state"]

    def apply_structural_events(self, year: int) -> List[str]:
        events: List[str] = []
        mean_ideology = statistics.fmean(node.ideology for node in self.nodes)
        cooperation_resilience = max(0.0, self.config.cooperation_multiplier - 1.0)
        organic_nodes = self.organic_nodes() or self.nodes

        if (
            self.abundance_transition_year is None
            and self.abundance_index >= self.config.abundance_threshold
        ):
            self.abundance_transition_year = year
            self.protocol_cohesion = clamp(self.protocol_cohesion + 0.08, 0.1, 1.0)
            for node in organic_nodes:
                node.governance_stability = clamp(
                    node.governance_stability + 0.05,
                    0.0,
                    1.0,
                )
            events.append("abundance_transition")

        if (
            self.ai_superintelligence_year is None
            and self.ai_capability >= self.config.ai_superintelligence
        ):
            self.ai_superintelligence_year = year
            events.append("ai_superintelligence")

        if (
            self.tech_level >= 1.5
            and self.governance_stability >= 0.55
            and self.rng.random() < 0.10
        ):
            self.protocol_cohesion = clamp(
                self.protocol_cohesion + 0.06 * self.config.cooperation_multiplier,
                0.1,
                1.0,
            )
            beneficiaries = self.rng.sample(
                organic_nodes,
                k=max(1, len(organic_nodes) // 6),
            )
            for node in beneficiaries:
                node.governance_stability = clamp(
                    node.governance_stability + 0.05,
                    0.0,
                    1.0,
                )
            events.append("peaceful_upgrade")

        if (
            self.tech_level >= 2.2
            and self.governance_stability < 0.45
            and self.protocol_cohesion >= 0.65
            and self.rng.random() < 0.07
        ):
            self.protocol_cohesion = clamp(
                self.protocol_cohesion + 0.10 * self.config.cooperation_multiplier,
                0.1,
                1.0,
            )
            for node in organic_nodes:
                node.governance_stability = clamp(
                    node.governance_stability + 0.04,
                    0.0,
                    1.0,
                )
            events.append("peaceful_replacement")

        fragmentation_chance = clamp(
            0.03 + 0.02 * self.protocol_cohesion - 0.015 * cooperation_resilience,
            0.0,
            0.20,
        )
        if (
            self.tech_level >= 1.2
            and len(self.nodes) < 250
            and self.rng.random() < fragmentation_chance
        ):
            parent = max(organic_nodes, key=lambda item: item.population)
            if parent.population > 20_000:
                child_population = max(
                    1_000,
                    int(parent.population * self.rng.uniform(0.08, 0.18)),
                )
                parent.population -= child_population
                child = Node(
                    population=child_population,
                    tech=max(0.2, parent.tech * self.rng.uniform(0.9, 1.1)),
                    ideology=clamp(
                        parent.ideology + self.rng.uniform(-0.10, 0.10),
                        0.0,
                        1.0,
                    ),
                    governance_stability=clamp(
                        parent.governance_stability
                        + self.rng.uniform(-0.05, 0.08)
                        + 0.02 * self.protocol_cohesion,
                        0.0,
                        1.0,
                    ),
                )
                child.node_id = self.allocate_node_id()
                self.nodes.append(child)
                self.add_node_to_network(child, parent=parent)
                events.append("node_fragmentation")

        exit_chance = min(
            0.18,
            max(
                0.0,
                0.01 + 0.08 * max(0.0, self.ideology_spread - 0.23) - 0.02 * cooperation_resilience,
            ),
        )
        if len(organic_nodes) > 8 and self.rng.random() < exit_chance:
            exiting = max(
                organic_nodes,
                key=lambda item: abs(item.ideology - mean_ideology)
                + (1.0 - item.governance_stability),
            )
            self.remove_node(exiting)
            self.protocol_cohesion = clamp(self.protocol_cohesion - 0.02, 0.1, 1.0)
            events.append("node_exit")
            organic_nodes = self.organic_nodes() or self.nodes

        collapse_risk = min(
            0.25,
            max(
                0.0,
                0.01
                + 0.08 * max(0.0, 0.50 - self.governance_stability)
                + 0.06 * max(0.0, self.ideology_spread - 0.25)
                - 0.02 * cooperation_resilience,
            ),
        )
        if len(organic_nodes) > 5 and self.rng.random() < collapse_risk:
            victim = min(
                organic_nodes,
                key=lambda item: item.governance_stability + 0.1 * item.tech,
            )
            if victim.population < 15_000 or self.rng.random() < 0.50:
                self.remove_node(victim)
            else:
                victim.population = max(
                    1_000,
                    int(victim.population * self.rng.uniform(0.45, 0.75)),
                )
                victim.tech *= self.rng.uniform(0.75, 0.90)
                victim.governance_stability = clamp(
                    victim.governance_stability * self.rng.uniform(0.40, 0.75),
                    0.0,
                    1.0,
                )
            self.automation *= 0.95
            events.append("regional_collapse")
            organic_nodes = self.organic_nodes() or self.nodes

        scarcity_pressure = max(0.0, 0.85 - self.abundance_index)
        conflict_risk = min(
            0.22,
            max(
                0.0,
                0.02
                + 0.25 * max(0.0, self.ideology_spread - 0.22) * scarcity_pressure
                - 0.03 * cooperation_resilience,
            ),
        )
        if self.rng.random() < conflict_risk:
            affected = self.rng.sample(
                organic_nodes,
                k=max(1, len(organic_nodes) // 5),
            )
            for node in affected:
                node.population = max(1_000, int(node.population * 0.96))
                node.governance_stability = clamp(
                    node.governance_stability * 0.90,
                    0.0,
                    1.0,
                )
            self.protocol_cohesion = clamp(self.protocol_cohesion - 0.05, 0.1, 1.0)
            events.append("ideological_conflict")

        infrastructure_risk = min(
            0.18,
            0.02
            + 0.12 * max(0.0, self.automation - 1.5) * max(0.0, 0.65 - self.governance_stability),
        )
        if self.rng.random() < infrastructure_risk:
            self.automation *= 0.86
            self.protocol_cohesion = clamp(self.protocol_cohesion - 0.03, 0.1, 1.0)
            for node in self.rng.sample(organic_nodes, k=max(1, len(organic_nodes) // 8)):
                node.population = max(1_000, int(node.population * 0.97))
                node.governance_stability = clamp(
                    node.governance_stability * 0.92,
                    0.0,
                    1.0,
                )
            events.append("infrastructure_crisis")

        if self.ai_capability >= self.config.ai_superintelligence:
            emergence_chance = 0.08 + 0.08 * self.protocol_cohesion
            if self.rng.random() < emergence_chance:
                ai_node = Node(
                    population=max(3_000, int(self.population * self.rng.uniform(0.003, 0.010))),
                    tech=max(2.5, self.tech_level * self.rng.uniform(1.4, 1.8)),
                    ideology=clamp(
                        mean_ideology + self.rng.uniform(-0.08, 0.08),
                        0.0,
                        1.0,
                    ),
                    governance_stability=clamp(
                        0.70
                        + 0.10 * self.protocol_cohesion
                        + self.rng.uniform(-0.05, 0.05),
                        0.0,
                        1.0,
                    ),
                )
                ai_node.node_id = self.allocate_node_id()
                self.nodes.append(ai_node)
                self.add_node_to_network(ai_node)
                events.append("ai_governance_node")

            misalignment_risk = min(
                0.18,
                0.02
                + 0.10 * max(0.0, 0.55 - self.governance_stability)
                + 0.04 * max(0.0, 0.65 - self.protocol_cohesion),
            )
            if self.rng.random() < misalignment_risk:
                self.automation *= 0.90
                self.protocol_cohesion = clamp(self.protocol_cohesion - 0.05, 0.1, 1.0)
                for node in self.rng.sample(organic_nodes, k=max(1, len(organic_nodes) // 8)):
                    node.governance_stability = clamp(
                        node.governance_stability * 0.90,
                        0.0,
                        1.0,
                    )
                events.append("ai_coordination_crisis")

        return events

    def snapshot(self, year: int, events: List[str]) -> Dict[str, Any]:
        snapshot = {
            "year": year,
            "nodes": len(self.nodes),
            "population": self.population,
            "tech": round(self.tech_level, 3),
            "automation": round(self.automation, 3),
            "ai_capability": round(self.ai_capability, 3),
            "governance_stability": round(self.governance_stability, 3),
            "abundance": round(self.abundance_index, 3),
            "protocol_cohesion": round(self.protocol_cohesion, 3),
            "cooperation": round(self.local_cooperation_mean, 3),
            "events": events,
        }
        if self.uses_topology:
            containment = (
                self.secondary_failure_count / self.initial_failure_count
                if self.initial_failure_count
                else 0.0
            )
            snapshot.update(
                {
                    "topology": self.config.topology,
                    "connected_components": self.connected_components,
                    "largest_component_size": self.largest_component_size(),
                    "largest_component_ratio": round(self.largest_component_ratio(), 3),
                    "fragmentation_count": self.fragmentation_count,
                    "contagion_initial_failures": self.initial_failure_count,
                    "contagion_secondary_failures": self.secondary_failure_count,
                    "contagion_containment": round(containment, 3),
                }
            )
        if self.uses_trust_layer:
            organic_nodes = self.organic_nodes() or self.nodes
            recovered_node_rate = (
                sum(
                    1
                    for node in organic_nodes
                    if node.cooperation >= self.config.cooperation_collapse_threshold
                )
                / max(1, len(organic_nodes))
            )
            snapshot.update(
                {
                    "trust_memory_mean": round(self.trust_memory_mean, 3),
                    "defection_mean": round(
                        statistics.fmean(node.defection_drive for node in self.nodes),
                        3,
                    ),
                    "recovered_node_rate": round(recovered_node_rate, 3),
                }
            )
        if self.uses_infiltration_layer:
            snapshot["infiltrator_count"] = sum(
                1 for node in self.nodes if node.is_infiltrator
            )
            snapshot["isolated_infiltrator_count"] = len(self.infiltrator_isolation_years)
        if self.uses_local_defense:
            isolation_rate = (
                len(self.infiltrator_isolation_years) / self.total_infiltrators_injected
                if self.total_infiltrators_injected
                else 0.0
            )
            reconnection_rate = (
                len(self.restored_edge_pairs) / len(self.severed_edge_pairs)
                if self.severed_edge_pairs
                else 0.0
            )
            isolation_delays = [
                isolated_year - self.config.infiltration_year
                for isolated_year in self.infiltrator_isolation_years.values()
                if self.config.infiltration_year is not None
            ]
            snapshot.update(
                {
                    "defense_edge_cuts": self.defense_edge_cuts,
                    "adversary_isolation_rate": round(isolation_rate, 3),
                    "reconnection_rate": round(reconnection_rate, 3),
                    "time_to_isolation": (
                        round(statistics.fmean(isolation_delays), 3)
                        if isolation_delays
                        else None
                    ),
                }
            )
        if self.uses_trust_signal_propagation:
            organic_nodes = self.organic_nodes() or self.nodes
            signal_propagation_rate = (
                len(self.signal_receivers_ever) / max(1, len(organic_nodes))
                if organic_nodes
                else 0.0
            )
            snapshot["signal_propagation_rate"] = round(signal_propagation_rate, 3)
        return snapshot


class BureaucraticCivilization(Civilization):
    def __init__(self, config: SimulationConfig, rng: random.Random) -> None:
        super().__init__(config, rng)
        self.governance_bandwidth_beta = config.governance_bandwidth_tech_multiplier
        self.governance_bandwidth = 0.0
        self.civ_total_proposal_rate = 0.0
        self.governance_backlog = 0.0
        self.backlog_ratio = 0.0
        self.human_control_index = 1.0
        self.freeze_steps_remaining = 0
        self.last_defense_action = "none"
        self.defense_action_counts: Dict[str, int] = {}
        self.utilization_history: List[float] = []
        self.cooperation_mean = statistics.fmean(node.cooperation for node in self.nodes)
        self.bureaucratic_ai_total = 0.0
        self.omega_injected = False
        self.omega_proposal_rate = 0.0
        self.distribute_ai_levels(self.proposal_ai_target_total())
        self.refresh_aggregates()
        self.governance_bandwidth = self.compute_governance_bandwidth()
        self.update_proposal_rates(freeze_proposals=False)

    def refresh_aggregates(self) -> None:
        super().refresh_aggregates()
        self.cooperation_mean = statistics.fmean(node.cooperation for node in self.nodes)
        self.bureaucratic_ai_total = sum(node.ai_level for node in self.nodes)

    def proposal_ai_target_total(self) -> float:
        # Proposal pressure should track institutional scale, not explode at the full macro AI rate.
        return 1.05 * self.tech_level + 0.10 * min(self.ai_capability, self.tech_level)

    def distribute_ai_levels(self, target_total: float) -> None:
        if target_total <= 0:
            for node in self.nodes:
                node.ai_level = 0.0
            return

        weights = [
            max(0.01, 0.60 * node.ai_level + 0.25 * node.tech + 0.15 * node.cooperation)
            for node in self.nodes
        ]
        total_weight = sum(weights)
        if total_weight <= 0:
            equal_share = target_total / len(self.nodes)
            for node in self.nodes:
                node.ai_level = equal_share
            return
        for node, weight in zip(self.nodes, weights):
            node.ai_level = target_total * weight / total_weight

    def evolve_nodes(self, freeze_tech: bool = False) -> None:
        mean_ideology = statistics.fmean(node.ideology for node in self.nodes)
        node_lookup = {node.node_id: node for node in self.nodes}
        for node in self.nodes:
            local_ideology = self.neighbor_average(
                node,
                "ideology",
                mean_ideology,
                node_lookup=node_lookup,
            )
            local_cooperation = self.neighbor_average(
                node,
                "cooperation",
                self.protocol_cohesion,
                node_lookup=node_lookup,
            )
            innovation = 0.0 if freeze_tech else self.rng.uniform(0.0, 0.03)
            innovation += 0.010 * local_cooperation
            innovation += 0.004 * self.abundance_index
            innovation -= 0.008 * max(0.0, 0.55 - node.governance_stability)
            node.tech = max(0.2, node.tech + innovation)

            ideology_pull = 0.06 * (local_ideology - node.ideology)
            node.ideology = clamp(
                node.ideology + ideology_pull + self.rng.uniform(-0.03, 0.03),
                0.0,
                1.0,
            )

            base_growth = 0.02 + 0.04 * self.abundance_index
            stability_term = 0.05 * (node.governance_stability - 0.5)
            diversity_term = -0.04 * abs(node.ideology - local_ideology)
            growth_noise = self.rng.uniform(-0.04, 0.04)
            population_growth = clamp(
                base_growth + stability_term + diversity_term + growth_noise,
                -0.20,
                0.18,
            )
            node.population = max(1_000, int(node.population * (1 + population_growth)))

            cooperation_delta = 0.08 * (local_cooperation - node.cooperation)
            cooperation_delta += 0.05 * (node.governance_stability - 0.5)
            cooperation_delta -= 0.05 * abs(node.ideology - local_ideology)
            cooperation_delta += self.rng.uniform(-0.03, 0.03)
            node.cooperation = clamp(node.cooperation + cooperation_delta, 0.0, 1.0)

            stability_delta = 0.05 * (local_cooperation - 0.5)
            stability_delta += 0.04 * self.abundance_index
            stability_delta += 0.05 * (node.cooperation - 0.5)
            stability_delta -= 0.12 * abs(node.ideology - local_ideology)
            stability_delta -= 0.03 * max(
                0.0, self.ai_capability - self.config.ai_superintelligence
            )
            stability_delta += self.rng.uniform(-0.04, 0.04)
            node.governance_stability = clamp(
                node.governance_stability + stability_delta,
                0.0,
                1.0,
            )

    def advance_macro(self, freeze_tech: bool = False) -> None:
        cooperation_anchor = (
            self.cooperation_mean if self.uses_topology else self.protocol_cohesion
        )
        automation_growth = (
            0.015 * self.tech_level
            + 0.025 * cooperation_anchor
            - 0.010 * self.ideology_spread
        )
        automation_growth *= self.config.automation_growth_multiplier
        if self.abundance_index >= self.config.abundance_threshold:
            automation_growth += 0.015 * self.config.automation_growth_multiplier
        self.automation = clamp(self.automation + automation_growth, 0.0, 4.0)

        ai_growth = 0.012 * self.tech_level + 0.010 * self.automation
        if self.governance_stability < 0.45:
            ai_growth += 0.010
        ai_growth *= self.config.ai_growth_multiplier
        self.ai_capability = max(0.0, self.ai_capability + ai_growth)
        self.distribute_ai_levels(self.proposal_ai_target_total())
        self.bureaucratic_ai_total = sum(node.ai_level for node in self.nodes)

        protocol_delta = 0.04 * (self.governance_stability - 0.5)
        protocol_delta += 0.02 * min(self.automation, 1.5)
        protocol_delta += 0.03 * (self.cooperation_mean - 0.5)
        protocol_delta -= 0.08 * self.ideology_spread
        protocol_delta *= self.config.cooperation_multiplier
        self.protocol_cohesion = clamp(self.protocol_cohesion + protocol_delta, 0.1, 1.0)
        self.abundance_index = self._compute_abundance()

    def compute_governance_bandwidth(self) -> float:
        return (
            self.config.governance_bandwidth_base
            + self.governance_bandwidth_beta * self.tech_level
        )

    def update_proposal_rates(self, freeze_proposals: bool, quota_active: bool = False) -> None:
        total = 0.0
        omega_rate = 0.0
        for node in self.nodes:
            proposal_rate = (
                0.0 if freeze_proposals else self.config.proposal_rate_constant * node.ai_level
            )
            if quota_active:
                proposal_rate = min(proposal_rate, self.config.proposal_quota_per_node)
            node.proposal_rate = proposal_rate
            total += proposal_rate
            if node.is_omega:
                omega_rate = proposal_rate
        self.civ_total_proposal_rate = total
        self.omega_proposal_rate = omega_rate

    def projected_gridlock_penalty(self, backlog: float) -> float:
        if backlog <= self.config.critical_backlog_threshold:
            return 0.0
        overload = backlog / self.config.critical_backlog_threshold - 1.0
        return min(0.30, 0.04 + 0.10 * overload)

    def choose_defense_action(self, previous_backlog: float) -> str:
        affected_nodes = [
            node for node in self.nodes if node.proposal_rate > self.config.proposal_quota_per_node
        ]
        capped_total = sum(
            min(node.proposal_rate, self.config.proposal_quota_per_node) for node in self.nodes
        )
        quota_cost = float("inf")
        if affected_nodes:
            quota_cost = (
                self.config.quota_cooperation_penalty
                * len(affected_nodes)
                / len(self.nodes)
                + self.projected_gridlock_penalty(
                    max(0.0, previous_backlog + capped_total - self.governance_bandwidth)
                )
            )

        delegated_bandwidth = (
            self.config.governance_bandwidth_base
            + self.governance_bandwidth_beta
            * self.config.ai_delegation_beta_multiplier
            * self.tech_level
        )
        delegation_cost = (
            self.config.human_control_penalty_per_delegation
            + self.projected_gridlock_penalty(
                max(0.0, previous_backlog + self.civ_total_proposal_rate - delegated_bandwidth)
            )
        )
        veto_cost = (
            self.config.foundational_veto_stability_penalty
            + self.config.foundational_veto_tech_pause_cost
        )
        costs = {
            "proposal_quota": quota_cost,
            "ai_legislative_processors": delegation_cost,
            "foundational_veto": veto_cost,
        }
        return min(costs, key=lambda action: (costs[action], action))

    def apply_proposal_quota(self) -> None:
        affected_count = 0
        for node in self.nodes:
            if node.proposal_rate > self.config.proposal_quota_per_node:
                affected_count += 1
                node.cooperation = clamp(
                    node.cooperation - self.config.quota_cooperation_penalty,
                    0.0,
                    1.0,
                )
        if affected_count:
            cohesion_drop = 0.05 * affected_count / len(self.nodes)
            self.protocol_cohesion = clamp(self.protocol_cohesion - cohesion_drop, 0.1, 1.0)
        self.update_proposal_rates(freeze_proposals=False, quota_active=True)

    def apply_ai_delegation(self) -> None:
        self.governance_bandwidth_beta *= self.config.ai_delegation_beta_multiplier
        self.human_control_index = clamp(
            self.human_control_index - self.config.human_control_penalty_per_delegation,
            0.0,
            1.0,
        )

    def apply_foundational_veto(self) -> None:
        self.governance_backlog = 0.0
        self.backlog_ratio = 0.0
        self.freeze_steps_remaining = max(0, self.config.foundational_veto_freeze_steps - 1)
        self.update_proposal_rates(freeze_proposals=True)
        for node in self.nodes:
            node.governance_stability = clamp(
                node.governance_stability - self.config.foundational_veto_stability_penalty,
                0.0,
                1.0,
            )

    def inject_omega(self) -> None:
        mean_ideology = statistics.fmean(node.ideology for node in self.nodes)
        omega_ai = max(
            0.01,
            self.bureaucratic_ai_total / max(1, len(self.nodes)) * self.config.omega_shock_factor,
        )
        omega = Node(
            population=max(5_000, int(self.population * 0.01)),
            tech=max(1.5, self.tech_level * 1.25),
            ideology=mean_ideology,
            governance_stability=0.72,
            cooperation=0.55,
            ai_level=omega_ai,
            is_omega=True,
        )
        omega.node_id = self.allocate_node_id()
        self.nodes.append(omega)
        self.add_node_to_network(omega)
        self.omega_injected = True

    def apply_bureaucratic_layer(self, year: int, freeze_active: bool) -> List[str]:
        events: List[str] = []
        if (
            self.config.omega_shock_year is not None
            and not self.omega_injected
            and year >= self.config.omega_shock_year
        ):
            self.inject_omega()
            self.refresh_aggregates()
            events.append("omega_injected")

        self.governance_bandwidth = self.compute_governance_bandwidth()
        if freeze_active:
            self.update_proposal_rates(freeze_proposals=True)
            self.governance_backlog = 0.0
            self.backlog_ratio = 0.0
            self.last_defense_action = "foundational_veto"
            self.utilization_history.append(0.0)
            self.freeze_steps_remaining = max(0, self.freeze_steps_remaining - 1)
            return events + ["governance_freeze"]

        previous_backlog = self.governance_backlog
        self.update_proposal_rates(freeze_proposals=False)
        self.governance_backlog = max(
            0.0,
            previous_backlog + self.civ_total_proposal_rate - self.governance_bandwidth,
        )
        self.backlog_ratio = self.governance_backlog / self.config.critical_backlog_threshold
        utilization = self.civ_total_proposal_rate / max(self.governance_bandwidth, 1e-6)
        self.utilization_history.append(utilization)
        self.last_defense_action = "none"

        if self.governance_backlog <= self.config.critical_backlog_threshold:
            return events

        action = self.choose_defense_action(previous_backlog)
        self.last_defense_action = action
        self.defense_action_counts[action] = self.defense_action_counts.get(action, 0) + 1
        events.append(action)

        if action == "proposal_quota":
            self.apply_proposal_quota()
        elif action == "ai_legislative_processors":
            self.apply_ai_delegation()
        else:
            self.apply_foundational_veto()
            self.governance_bandwidth = self.compute_governance_bandwidth()
            return events + ["governance_freeze"]

        self.governance_bandwidth = self.compute_governance_bandwidth()
        self.governance_backlog = max(
            0.0,
            previous_backlog + self.civ_total_proposal_rate - self.governance_bandwidth,
        )
        self.backlog_ratio = self.governance_backlog / self.config.critical_backlog_threshold
        if self.governance_backlog > self.config.critical_backlog_threshold:
            penalty = self.projected_gridlock_penalty(self.governance_backlog)
            for node in self.nodes:
                node.governance_stability = clamp(node.governance_stability - penalty, 0.0, 1.0)
            events.append("governance_gridlock")
        return events

    def step(self, year: int) -> List[str]:
        freeze_active = self.freeze_steps_remaining > 0
        self.evolve_nodes(freeze_tech=freeze_active)
        self.refresh_aggregates()
        self.advance_macro(freeze_tech=freeze_active)
        events = self.apply_structural_events(year)
        events.extend(self.apply_hub_failure(year))
        events.extend(self.apply_systemic_shock(year))
        events.extend(self.apply_topology_contagion())
        self.refresh_aggregates()
        events.extend(self.apply_bureaucratic_layer(year, freeze_active))
        self.refresh_aggregates()
        return events or ["steady_state"]

    def snapshot(self, year: int, events: List[str]) -> Dict[str, Any]:
        snapshot = super().snapshot(year, events)
        snapshot.update(
            {
                "proposal_rate": round(self.civ_total_proposal_rate, 3),
                "governance_bandwidth": round(self.governance_bandwidth, 3),
                "governance_backlog": round(self.governance_backlog, 3),
                "backlog_ratio": round(self.backlog_ratio, 3),
                "human_control_index": round(self.human_control_index, 3),
                "cooperation": round(self.cooperation_mean, 3),
                "utilization": round(
                    self.civ_total_proposal_rate / max(self.governance_bandwidth, 1e-6),
                    3,
                ),
                "defense_action": self.last_defense_action,
                "omega_present": any(node.is_omega for node in self.nodes),
                "omega_proposal_rate": round(self.omega_proposal_rate, 3),
                "freeze_steps_remaining": self.freeze_steps_remaining,
            }
        )
        return snapshot


def run_simulation(config: SimulationConfig, seed: int) -> List[Dict[str, Any]]:
    rng = random.Random(seed)
    civilization: Civilization
    if config.enable_bureaucratic_layer:
        civilization = BureaucraticCivilization(config, rng)
    else:
        civilization = Civilization(config, rng)
    history = [civilization.snapshot(0, ["initial_state"])]
    for step_index in range(1, config.steps + 1):
        year = step_index * config.step_years
        events = civilization.step(year)
        history.append(civilization.snapshot(year, events))
    return history


def serialize_records(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    serialized_records: List[Dict[str, Any]] = []
    for row in records:
        serialized_row: Dict[str, Any] = {}
        for key, value in row.items():
            serialized_row[key] = ";".join(value) if isinstance(value, list) else value
        serialized_records.append(serialized_row)
    return serialized_records


def write_records(records: List[Dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    serialized_records = serialize_records(records)
    if output_path.suffix.lower() == ".csv":
        with output_path.open("w", newline="", encoding="utf-8") as handle:
            fieldnames = list(serialized_records[0].keys()) if serialized_records else []
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for row in serialized_records:
                writer.writerow(row)
        return

    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(serialized_records, handle, indent=2)


def write_history(history: List[Dict[str, Any]], output_path: Path) -> None:
    write_records(history, output_path)


def print_preview(history: List[Dict[str, Any]], preview_rows: int) -> None:
    rows = history[:preview_rows]
    include_governance_flow = bool(rows and "governance_backlog" in rows[0])
    header = (
        f"{'year':>6} {'nodes':>5} {'population':>12} {'tech':>7} "
        f"{'auto':>7} {'ai':>7} {'stability':>10} {'abund':>7}"
    )
    if include_governance_flow:
        header += (
            f" {'prop':>7} {'band':>7} {'backlog':>8} "
            f"{'human':>7} {'action':>14}"
        )
    header += "  events"
    print(header)
    print("-" * len(header))
    for row in rows:
        events = ",".join(row["events"])
        line = (
            f"{row['year']:>6} "
            f"{row['nodes']:>5} "
            f"{row['population']:>12,} "
            f"{row['tech']:>7.3f} "
            f"{row['automation']:>7.3f} "
            f"{row['ai_capability']:>7.3f} "
            f"{row['governance_stability']:>10.3f} "
            f"{row['abundance']:>7.3f}"
        )
        if include_governance_flow:
            line += (
                f" {row['proposal_rate']:>7.3f}"
                f" {row['governance_bandwidth']:>7.3f}"
                f" {row['governance_backlog']:>8.3f}"
                f" {row['human_control_index']:>7.3f}"
                f" {row['defense_action']:>14}"
            )
        line += f"  {events}"
        print(line)


def print_summary(history: List[Dict[str, Any]], config: SimulationConfig) -> None:
    summary = summarize_history(history, config)
    final = summary["final"]
    event_counts = summary["event_counts"]

    print("\nSummary")
    print(f"Final population: {final['population']:,}")
    print(f"Final nodes: {final['nodes']}")
    print(f"Final tech level: {final['tech']:.3f}")
    print(f"Final AI capability: {final['ai_capability']:.3f}")
    print(f"Final governance stability: {final['governance_stability']:.3f}")
    print(f"Final abundance: {final['abundance']:.3f}")
    if summary["abundance_year"] is None:
        print("Abundance transition: not reached")
    else:
        print(f"Abundance transition year: {summary['abundance_year']}")
    if summary["superintelligence_year"] is None:
        print("AI superintelligence threshold: not reached")
    else:
        print(f"AI superintelligence year: {summary['superintelligence_year']}")
    print(
        f"Peak population: "
        f"{summary['peak_population']['population']:,} "
        f"(year {summary['peak_population']['year']})"
    )
    print(
        f"Lowest governance stability: "
        f"{summary['lowest_stability']['governance_stability']:.3f} "
        f"(year {summary['lowest_stability']['year']})"
    )
    if config.topology != "none":
        print(f"Topology: {config.topology}")
        print(f"Final connected components: {summary['final_connected_components']}")
        print(f"Fragmentation count: {summary['fragmentation_count']:.3f}")
        print(f"Contagion containment: {summary['contagion_containment']:.3f}")
    if config.enable_bureaucratic_layer:
        print(
            f"Average governance utilization: "
            f"{summary['average_utilization']:.3f}"
        )
        print(
            f"Peak governance backlog: "
            f"{summary['peak_backlog']['governance_backlog']:.3f} "
            f"(year {summary['peak_backlog']['year']})"
        )
        print(
            f"Minimum human control index: "
            f"{summary['minimum_human_control']['human_control_index']:.3f}"
        )
        if summary["defense_action_counts"]:
            defense_counts = ", ".join(
                f"{name}={count}"
                for name, count in sorted(summary["defense_action_counts"].items())
            )
            print(f"Defense actions used: {defense_counts}")
    if event_counts:
        top_events = sorted(event_counts.items(), key=lambda item: (-item[1], item[0]))[:6]
        formatted = ", ".join(f"{name}={count}" for name, count in top_events)
        print(f"Most common non-steady events: {formatted}")


def summarize_history(
    history: List[Dict[str, Any]],
    config: SimulationConfig,
) -> Dict[str, Any]:
    final = history[-1]
    abundance_year = next(
        (
            row["year"]
            for row in history
            if row["abundance"] >= config.abundance_threshold
        ),
        None,
    )
    superintelligence_year = next(
        (
            row["year"]
            for row in history
            if row["ai_capability"] >= config.ai_superintelligence
        ),
        None,
    )
    peak_population = max(history, key=lambda row: row["population"])
    peak_abundance = max(history, key=lambda row: row["abundance"])
    lowest_stability = min(history, key=lambda row: row["governance_stability"])
    peak_backlog = max(
        history,
        key=lambda row: row.get("governance_backlog", 0.0),
    )
    peak_components = max(
        history,
        key=lambda row: row.get("connected_components", 1),
    )
    minimum_human_control = min(
        history,
        key=lambda row: row.get("human_control_index", 1.0),
    )
    stability_break_year = next(
        (
            row["year"]
            for row in history
            if row["governance_stability"] < config.governance_survival_threshold
        ),
        None,
    )
    survival_checkpoint_year = min(500, final["year"])
    checkpoint_state = next(
        (row for row in history if row["year"] == survival_checkpoint_year),
        history[-1],
    )
    utilization_values = [row.get("utilization") for row in history if "utilization" in row]
    component_values = [row.get("connected_components", 1) for row in history]
    largest_component_values = [row.get("largest_component_ratio", 1.0) for row in history]
    cooperation_values = [row.get("cooperation", row["protocol_cohesion"]) for row in history]
    trust_values = [
        row.get("trust_memory_mean", row.get("cooperation", row["protocol_cohesion"]))
        for row in history
    ]
    event_counts: Dict[str, int] = {}
    defense_action_counts: Dict[str, int] = {}
    for row in history:
        for event in row["events"]:
            if event in ("initial_state", "steady_state"):
                continue
            event_counts[event] = event_counts.get(event, 0) + 1
        action = row.get("defense_action")
        if action and action != "none":
            defense_action_counts[action] = defense_action_counts.get(action, 0) + 1
    fragmentation_events = sum(
        event_counts.get(name, 0)
        for name in ("node_fragmentation", "node_exit", "regional_collapse")
    )
    disruption_events = sum(
        event_counts.get(name, 0)
        for name in ("node_exit", "regional_collapse", "ideological_conflict")
    )
    first_cooperation_collapse_year: Optional[int] = None
    recovery_year: Optional[int] = None
    system_recovery_year: Optional[int] = None
    recovered_within_window = True
    collapsed = False
    time_to_collapse: Optional[int] = None
    time_to_recovery: Optional[int] = None
    recovered_network_size = 0
    post_betrayal_min_cooperation = min(cooperation_values) if cooperation_values else 0.0
    if config.betrayal_year is not None:
        post_betrayal_rows = [
            row for row in history if row["year"] >= config.betrayal_year
        ]
        recovery_deadline = config.betrayal_year + config.recovery_window_years
        recovery_window_rows = [
            row for row in post_betrayal_rows if row["year"] <= recovery_deadline
        ]
        if post_betrayal_rows:
            post_betrayal_min_cooperation = min(
                row.get("cooperation", row["protocol_cohesion"]) for row in post_betrayal_rows
            )
        first_cooperation_collapse_year = next(
            (
                row["year"]
                for row in recovery_window_rows
                if row.get("cooperation", row["protocol_cohesion"])
                < config.cooperation_collapse_threshold
            ),
            None,
        )
        deadline_row = recovery_window_rows[-1] if recovery_window_rows else None
        if deadline_row is not None:
            recovered_within_window = (
                deadline_row.get("cooperation", deadline_row["protocol_cohesion"])
                >= config.cooperation_collapse_threshold
            )
            collapsed = not recovered_within_window
        if first_cooperation_collapse_year is not None and recovered_within_window:
            for index, row in enumerate(recovery_window_rows):
                if row["year"] <= first_cooperation_collapse_year:
                    continue
                if row.get("cooperation", row["protocol_cohesion"]) < config.cooperation_collapse_threshold:
                    continue
                if all(
                    later_row.get("cooperation", later_row["protocol_cohesion"])
                    >= config.cooperation_collapse_threshold
                    for later_row in recovery_window_rows[index:]
                ):
                    recovery_year = row["year"]
                    break
        if collapsed and first_cooperation_collapse_year is not None:
            time_to_collapse = first_cooperation_collapse_year - config.betrayal_year
        for index, row in enumerate(post_betrayal_rows):
            if row.get("cooperation", row["protocol_cohesion"]) < config.cooperation_collapse_threshold:
                continue
            if all(
                later_row.get("cooperation", later_row["protocol_cohesion"])
                >= config.cooperation_collapse_threshold
                for later_row in post_betrayal_rows[index:]
            ):
                system_recovery_year = row["year"]
                time_to_recovery = row["year"] - config.betrayal_year
                recovered_network_size = row.get(
                    "largest_component_size",
                    row.get("nodes", 0),
                )
                break
    return {
        "final": final,
        "abundance_year": abundance_year,
        "superintelligence_year": superintelligence_year,
        "peak_population": peak_population,
        "peak_abundance": peak_abundance,
        "lowest_stability": lowest_stability,
        "peak_backlog": peak_backlog,
        "minimum_human_control": minimum_human_control,
        "stability_break_year": stability_break_year,
        "survival_checkpoint_year": survival_checkpoint_year,
        "survived_500_year_mark": (
            checkpoint_state["governance_stability"] >= config.governance_survival_threshold
        ),
        "survived_final_year": (
            final["governance_stability"] >= config.governance_survival_threshold
        ),
        "final_human_control_index": final.get("human_control_index", 1.0),
        "average_utilization": statistics.fmean(utilization_values) if utilization_values else 0.0,
        "final_connected_components": final.get("connected_components", 1),
        "peak_connected_components": peak_components.get("connected_components", 1),
        "average_connected_components": statistics.fmean(component_values) if component_values else 1.0,
        "largest_component_ratio": final.get("largest_component_ratio", 1.0),
        "minimum_largest_component_ratio": (
            min(largest_component_values) if largest_component_values else 1.0
        ),
        "minimum_cooperation": min(cooperation_values) if cooperation_values else 0.0,
        "final_cooperation": final.get("cooperation", final["protocol_cohesion"]),
        "final_recovered_node_rate": final.get("recovered_node_rate", 0.0),
        "minimum_trust_memory": min(trust_values) if trust_values else 0.0,
        "final_trust_memory": final.get(
            "trust_memory_mean",
            final.get("cooperation", final["protocol_cohesion"]),
        ),
        "final_infiltrator_count": final.get("infiltrator_count", 0),
        "final_isolated_infiltrator_count": final.get("isolated_infiltrator_count", 0),
        "adversary_isolation_rate": final.get("adversary_isolation_rate", 0.0),
        "reconnection_rate": final.get("reconnection_rate", 0.0),
        "signal_propagation_rate": final.get("signal_propagation_rate", 0.0),
        "time_to_isolation": final.get("time_to_isolation"),
        "defense_edge_cuts": final.get("defense_edge_cuts", 0),
        "first_cooperation_collapse_year": first_cooperation_collapse_year,
        "recovery_year": recovery_year,
        "system_recovery_year": system_recovery_year,
        "recovered_within_window": recovered_within_window,
        "collapsed": collapsed,
        "time_to_collapse": time_to_collapse,
        "time_to_recovery": time_to_recovery,
        "recovered_network_size": recovered_network_size,
        "post_betrayal_min_cooperation": post_betrayal_min_cooperation,
        "fragmentation_count": final.get("fragmentation_count", fragmentation_events),
        "contagion_containment": final.get("contagion_containment", 0.0),
        "contagion_initial_failures": final.get("contagion_initial_failures", 0),
        "contagion_secondary_failures": final.get("contagion_secondary_failures", 0),
        "event_counts": event_counts,
        "defense_action_counts": defense_action_counts,
        "fragmentation_events": fragmentation_events,
        "disruption_events": disruption_events,
    }


def build_recommended_experiments(config: SimulationConfig) -> Dict[str, SimulationConfig]:
    return {
        "baseline": config,
        "faster_automation": replace(
            config,
            automation_growth_multiplier=2.40,
        ),
        "slower_ai": replace(
            config,
            ai_growth_multiplier=0.60,
        ),
        "stronger_cooperation": replace(
            config,
            initial_protocol_cohesion=0.82,
            cooperation_multiplier=2.50,
        ),
        "balanced_path": replace(
            config,
            automation_growth_multiplier=1.35,
            ai_growth_multiplier=0.60,
            initial_protocol_cohesion=0.82,
            cooperation_multiplier=2.50,
        ),
    }


def mean_or_none(values: List[Optional[float]]) -> Optional[float]:
    present = [value for value in values if value is not None]
    if not present:
        return None
    return statistics.fmean(present)


def collect_single_run_experiment_results(
    config: SimulationConfig,
    seed: int,
) -> List[Dict[str, Any]]:
    scenarios = build_recommended_experiments(config)
    results: List[Dict[str, Any]] = []
    for name, scenario_config in scenarios.items():
        history = run_simulation(scenario_config, seed=seed)
        summary = summarize_history(history, scenario_config)
        results.append(
            {
                "name": name,
                "seed": seed,
                "abundance_year": summary["abundance_year"],
                "ai_year": summary["superintelligence_year"],
                "peak_abundance": summary["peak_abundance"]["abundance"],
                "final_abundance": summary["final"]["abundance"],
                "stability_break_year": summary["stability_break_year"],
                "final_stability": summary["final"]["governance_stability"],
                "min_stability": summary["lowest_stability"]["governance_stability"],
                "final_nodes": summary["final"]["nodes"],
                "disruption_events": summary["disruption_events"],
            }
        )
    return results


def print_single_run_experiment_report(
    config: SimulationConfig,
    seed: int,
) -> List[Dict[str, Any]]:
    results = collect_single_run_experiment_results(config, seed)
    print(
        f"{'scenario':<24} "
        f"{'abundance':>10} "
        f"{'peak_abund':>10} "
        f"{'ai_year':>8} "
        f"{'stab<0.5':>10} "
        f"{'final_stab':>10} "
        f"{'min_stab':>9} "
        f"{'nodes':>7} "
        f"{'disrupt':>8}"
    )
    print("-" * 108)
    for row in results:
        abundance = "-" if row["abundance_year"] is None else str(row["abundance_year"])
        ai_year = "-" if row["ai_year"] is None else str(row["ai_year"])
        stability_break = (
            "-" if row["stability_break_year"] is None else str(row["stability_break_year"])
        )
        print(
            f"{row['name']:<24} "
            f"{abundance:>10} "
            f"{row['peak_abundance']:>10.3f} "
            f"{ai_year:>8} "
            f"{stability_break:>10} "
            f"{row['final_stability']:>10.3f} "
            f"{row['min_stability']:>9.3f} "
            f"{row['final_nodes']:>7} "
            f"{row['disruption_events']:>8}"
        )
    return results


def collect_multi_run_experiment_results(
    config: SimulationConfig,
    seed: int,
    runs: int,
) -> List[Dict[str, Any]]:
    scenarios = build_recommended_experiments(config)
    results: List[Dict[str, Any]] = []
    for name, scenario_config in scenarios.items():
        summaries = []
        for offset in range(runs):
            history = run_simulation(scenario_config, seed=seed + offset)
            summaries.append(summarize_history(history, scenario_config))

        abundance_years = [summary["abundance_year"] for summary in summaries]
        ai_years = [summary["superintelligence_year"] for summary in summaries]
        abundance_rate = sum(year is not None for year in abundance_years) / runs
        stable_rate = sum(
            summary["stability_break_year"] is None for summary in summaries
        ) / runs
        avg_final_stability = statistics.fmean(
            summary["final"]["governance_stability"] for summary in summaries
        )
        avg_min_stability = statistics.fmean(
            summary["lowest_stability"]["governance_stability"] for summary in summaries
        )
        avg_peak_abundance = statistics.fmean(
            summary["peak_abundance"]["abundance"] for summary in summaries
        )
        avg_disruptions = statistics.fmean(
            summary["disruption_events"] for summary in summaries
        )

        avg_abundance_year = mean_or_none(abundance_years)
        avg_ai_year = mean_or_none(ai_years)
        results.append(
            {
                "name": name,
                "runs": runs,
                "seed_start": seed,
                "abundance_rate": abundance_rate,
                "avg_abundance_year": avg_abundance_year,
                "avg_peak_abundance": avg_peak_abundance,
                "avg_ai_year": avg_ai_year,
                "stable_rate": stable_rate,
                "avg_final_stability": avg_final_stability,
                "avg_min_stability": avg_min_stability,
                "avg_disruptions": avg_disruptions,
            }
        )
    return results


def collect_raw_experiment_results(
    config: SimulationConfig,
    seed: int,
    runs: int,
) -> List[Dict[str, Any]]:
    scenarios = build_recommended_experiments(config)
    results: List[Dict[str, Any]] = []
    for name, scenario_config in scenarios.items():
        for offset in range(runs):
            run_seed = seed + offset
            history = run_simulation(scenario_config, seed=run_seed)
            summary = summarize_history(history, scenario_config)
            results.append(
                {
                    "name": name,
                    "run_index": offset + 1,
                    "seed": run_seed,
                    "abundance_year": summary["abundance_year"],
                    "ai_year": summary["superintelligence_year"],
                    "peak_abundance": summary["peak_abundance"]["abundance"],
                    "final_abundance": summary["final"]["abundance"],
                    "stability_break_year": summary["stability_break_year"],
                    "final_stability": summary["final"]["governance_stability"],
                    "min_stability": summary["lowest_stability"]["governance_stability"],
                    "final_nodes": summary["final"]["nodes"],
                    "disruption_events": summary["disruption_events"],
                }
            )
    return results


def collect_batch_results(
    config: SimulationConfig,
    seed: int,
    runs: int,
) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for offset in range(runs):
        run_seed = seed + offset
        history = run_simulation(config, seed=run_seed)
        summary = summarize_history(history, config)
        defense_counts = summary["defense_action_counts"]
        dominant_action = "none"
        if defense_counts:
            dominant_action = max(
                sorted(defense_counts.items()),
                key=lambda item: item[1],
            )[0]
        results.append(
            {
                "run_index": offset + 1,
                "seed": run_seed,
                "topology": config.topology,
                "survival_checkpoint_year": summary["survival_checkpoint_year"],
                "survived_500_year_mark": summary["survived_500_year_mark"],
                "survived_final_year": summary["survived_final_year"],
                "final_governance_stability": summary["final"]["governance_stability"],
                "final_human_control_index": summary["final_human_control_index"],
                "minimum_human_control_index": summary["minimum_human_control"].get(
                    "human_control_index",
                    1.0,
                ),
                "fragmentation_count": summary["fragmentation_count"],
                "final_connected_components": summary["final_connected_components"],
                "largest_component_ratio": summary["largest_component_ratio"],
                "contagion_containment": summary["contagion_containment"],
                "contagion_initial_failures": summary["contagion_initial_failures"],
                "contagion_secondary_failures": summary["contagion_secondary_failures"],
                "trust_memory_decay": config.trust_memory_decay,
                "final_cooperation": summary["final_cooperation"],
                "final_recovered_node_rate": summary["final_recovered_node_rate"],
                "final_trust_memory": summary["final_trust_memory"],
                "final_infiltrator_count": summary["final_infiltrator_count"],
                "final_isolated_infiltrator_count": summary["final_isolated_infiltrator_count"],
                "adversary_isolation_rate": summary["adversary_isolation_rate"],
                "reconnection_rate": summary["reconnection_rate"],
                "signal_propagation_rate": summary["signal_propagation_rate"],
                "time_to_isolation": summary["time_to_isolation"],
                "defense_edge_cuts": summary["defense_edge_cuts"],
                "minimum_cooperation": summary["minimum_cooperation"],
                "minimum_trust_memory": summary["minimum_trust_memory"],
                "post_betrayal_min_cooperation": summary["post_betrayal_min_cooperation"],
                "first_cooperation_collapse_year": summary["first_cooperation_collapse_year"],
                "time_to_collapse": summary["time_to_collapse"],
                "recovery_year": summary["recovery_year"],
                "time_to_recovery": summary["time_to_recovery"],
                "recovered_network_size": summary["recovered_network_size"],
                "recovered_within_window": summary["recovered_within_window"],
                "collapsed": summary["collapsed"],
                "peak_governance_backlog": summary["peak_backlog"].get(
                    "governance_backlog",
                    0.0,
                ),
                "dominant_defense_action": dominant_action,
                "proposal_quota_count": defense_counts.get("proposal_quota", 0),
                "ai_legislative_processors_count": defense_counts.get(
                    "ai_legislative_processors",
                    0,
                ),
                "foundational_veto_count": defense_counts.get("foundational_veto", 0),
            }
        )
    return results


def print_batch_summary(results: List[Dict[str, Any]]) -> None:
    if not results:
        print("No batch results produced.")
        return

    runs = len(results)
    checkpoint_year = results[0].get("survival_checkpoint_year", 500)
    survival_rate = sum(row["survived_500_year_mark"] for row in results) / runs
    final_survival_rate = sum(row["survived_final_year"] for row in results) / runs
    average_final_human_control = statistics.fmean(
        row["final_human_control_index"] for row in results
    )
    average_final_stability = statistics.fmean(
        row["final_governance_stability"] for row in results
    )
    average_fragmentation = statistics.fmean(row["fragmentation_count"] for row in results)
    average_containment = statistics.fmean(row["contagion_containment"] for row in results)
    average_final_components = statistics.fmean(
        row["final_connected_components"] for row in results
    )
    average_largest_component_ratio = statistics.fmean(
        row["largest_component_ratio"] for row in results
    )
    average_isolation_rate = (
        statistics.fmean(row.get("adversary_isolation_rate", 0.0) for row in results)
        if any("adversary_isolation_rate" in row for row in results)
        else 0.0
    )
    average_reconnection_rate = (
        statistics.fmean(row.get("reconnection_rate", 0.0) for row in results)
        if any("reconnection_rate" in row for row in results)
        else 0.0
    )
    average_signal_propagation_rate = (
        statistics.fmean(row.get("signal_propagation_rate", 0.0) for row in results)
        if any("signal_propagation_rate" in row for row in results)
        else 0.0
    )
    average_recovered_node_rate = (
        statistics.fmean(row.get("final_recovered_node_rate", 0.0) for row in results)
        if any("final_recovered_node_rate" in row for row in results)
        else 0.0
    )
    isolation_times = [
        row["time_to_isolation"]
        for row in results
        if row.get("time_to_isolation") is not None
    ]
    recovery_times = [
        row["time_to_recovery"]
        for row in results
        if row.get("time_to_recovery") is not None
    ]
    recovered_network_sizes = [
        row["recovered_network_size"]
        for row in results
        if row.get("recovered_network_size") is not None
    ]
    collapse_rate = (
        statistics.fmean(float(row.get("collapsed", False)) for row in results)
        if any("collapsed" in row for row in results)
        else 0.0
    )
    recovery_rate = (
        statistics.fmean(float(row.get("recovered_within_window", True)) for row in results)
        if any("recovered_within_window" in row for row in results)
        else 0.0
    )
    collapse_times = [
        row["time_to_collapse"]
        for row in results
        if row.get("time_to_collapse") is not None
    ]
    action_totals = {
        "proposal_quota": sum(row["proposal_quota_count"] for row in results),
        "ai_legislative_processors": sum(
            row["ai_legislative_processors_count"] for row in results
        ),
        "foundational_veto": sum(row["foundational_veto_count"] for row in results),
    }
    dominant_action = "none"
    if any(action_totals.values()):
        dominant_action = max(sorted(action_totals.items()), key=lambda item: item[1])[0]

    print("\nBatch Summary")
    print(f"Runs: {runs}")
    print(f"Survived checkpoint year {checkpoint_year}: {survival_rate:.0%}")
    print(f"Survived final year: {final_survival_rate:.0%}")
    print(f"Average final governance stability: {average_final_stability:.3f}")
    print(f"Average final human control index: {average_final_human_control:.3f}")
    if results[0].get("topology") and results[0]["topology"] != "none":
        print(f"Topology: {results[0]['topology']}")
        print(f"Average fragmentation count: {average_fragmentation:.3f}")
        print(f"Average final connected components: {average_final_components:.3f}")
        print(f"Largest component ratio: {average_largest_component_ratio:.3f}")
        print(f"Contagion containment: {average_containment:.3f}")
    if any("adversary_isolation_rate" in row for row in results):
        print(f"Average adversary isolation rate: {average_isolation_rate:.3f}")
        print(f"Average reconnection rate: {average_reconnection_rate:.3f}")
        print(f"Average signal propagation rate: {average_signal_propagation_rate:.3f}")
        print(f"Average recovered node rate: {average_recovered_node_rate:.3f}")
        if isolation_times:
            print(f"Average time to isolation: {statistics.fmean(isolation_times):.1f}")
        if recovery_times:
            print(f"Average time to recovery: {statistics.fmean(recovery_times):.1f}")
        if recovered_network_sizes:
            print(
                "Average recovered network size: "
                f"{statistics.fmean(recovered_network_sizes):.1f}"
            )
    if any("collapsed" in row for row in results):
        print(f"Collapse rate: {collapse_rate:.0%}")
        print(f"Recovery rate: {recovery_rate:.0%}")
        if collapse_times:
            print(f"Average years to collapse: {statistics.fmean(collapse_times):.1f}")
    print(f"Dominant defensive action: {dominant_action}")
    print(
        "Action totals: "
        f"proposal_quota={action_totals['proposal_quota']}, "
        f"ai_legislative_processors={action_totals['ai_legislative_processors']}, "
        f"foundational_veto={action_totals['foundational_veto']}"
    )


def print_multi_run_experiment_report(
    config: SimulationConfig,
    seed: int,
    runs: int,
) -> List[Dict[str, Any]]:
    results = collect_multi_run_experiment_results(config, seed, runs)
    print(
        f"{'scenario':<24} "
        f"{'abund%':>8} "
        f"{'avg_abund':>10} "
        f"{'avg_peak':>9} "
        f"{'avg_ai':>8} "
        f"{'stable%':>8} "
        f"{'avg_final':>10} "
        f"{'avg_min':>8} "
        f"{'avg_dis':>8}"
    )
    print("-" * 111)
    for row in results:
        abundance_display = (
            "-" if row["avg_abundance_year"] is None else f"{row['avg_abundance_year']:.0f}"
        )
        ai_display = "-" if row["avg_ai_year"] is None else f"{row['avg_ai_year']:.0f}"
        print(
            f"{row['name']:<24} "
            f"{row['abundance_rate']:>7.0%} "
            f"{abundance_display:>10} "
            f"{row['avg_peak_abundance']:>9.3f} "
            f"{ai_display:>8} "
            f"{row['stable_rate']:>7.0%} "
            f"{row['avg_final_stability']:>10.3f} "
            f"{row['avg_min_stability']:>8.3f} "
            f"{row['avg_disruptions']:>8.2f}"
        )
    return results


def print_experiment_report(
    config: SimulationConfig,
    seed: int,
    runs: int,
) -> List[Dict[str, Any]]:
    if runs <= 1:
        return print_single_run_experiment_report(config, seed)
    return print_multi_run_experiment_report(config, seed, runs)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="SOE-inspired civilization simulation over long time horizons."
    )
    parser.add_argument("--years", type=int, default=1000, help="Total simulated years.")
    parser.add_argument(
        "--step-years",
        type=int,
        default=10,
        help="Years advanced per simulation step.",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible runs.")
    parser.add_argument(
        "--runs",
        type=int,
        default=1,
        help="Number of simulation runs to aggregate for batch summaries.",
    )
    parser.add_argument(
        "--initial-protocol-cohesion",
        type=float,
        default=0.65,
        help="Starting civilization-wide protocol cohesion between 0 and 1.",
    )
    parser.add_argument(
        "--automation-growth-multiplier",
        type=float,
        default=1.0,
        help="Multiplier applied to automation growth.",
    )
    parser.add_argument(
        "--ai-growth-multiplier",
        type=float,
        default=1.0,
        help="Multiplier applied to AI capability growth.",
    )
    parser.add_argument(
        "--cooperation-multiplier",
        type=float,
        default=1.0,
        help="Multiplier applied to protocol cohesion growth and anti-fragmentation resilience.",
    )
    parser.add_argument(
        "--bureaucratic-layer",
        action="store_true",
        help="Enable the v1.5 bureaucratic layer with proposal throughput and backlog dynamics.",
    )
    parser.add_argument(
        "--topology",
        choices=sorted(TOPOLOGY_CHOICES),
        default="none",
        help="Optional v2.0 network topology layer. Uses 60 nodes when enabled.",
    )
    parser.add_argument(
        "--contagion-penalty",
        type=float,
        default=0.05,
        help="Cooperation penalty applied to neighbors when a node falls below the failure threshold.",
    )
    parser.add_argument(
        "--systemic-shock-year",
        "--shock-year",
        dest="systemic_shock_year",
        type=int,
        help="Optional year for a simultaneous topology shock affecting multiple nodes.",
    )
    parser.add_argument(
        "--systemic-shock-count",
        type=int,
        default=0,
        help="Number of random nodes forced to the shock stability when the systemic shock fires.",
    )
    parser.add_argument(
        "--systemic-shock-stability",
        type=float,
        default=0.10,
        help="Governance stability assigned to shocked nodes during a systemic shock.",
    )
    parser.add_argument(
        "--systemic-shock-target",
        "--shock-target",
        dest="systemic_shock_target",
        choices=sorted(SYSTEMIC_SHOCK_TARGETS),
        default="random",
        help="Whether a systemic shock targets random nodes or the highest-degree hubs.",
    )
    parser.add_argument(
        "--hub-failure-year",
        type=int,
        help="Optional year for a targeted highest-degree hub failure in topology mode.",
    )
    parser.add_argument(
        "--hub-failure-mode",
        choices=sorted(HUB_FAILURE_MODES),
        default="remove",
        help="Whether the targeted hub is removed from the network or only destabilized.",
    )
    parser.add_argument(
        "--hub-failure-stability",
        type=float,
        default=0.10,
        help="Governance stability assigned to the hub when --hub-failure-mode stability is used.",
    )
    parser.add_argument(
        "--betrayal-year",
        type=int,
        help="Optional year for the CL-NET betrayal event in topology mode.",
    )
    parser.add_argument(
        "--betrayal-fraction",
        type=float,
        default=0.0,
        help="Fraction of nodes affected by the betrayal event. Defaults to a single-node betrayal when 0.",
    )
    parser.add_argument(
        "--trust-memory-decay",
        type=float,
        default=0.0,
        help="Per-step rate at which betrayal damage fades and trust can rebuild.",
    )
    parser.add_argument(
        "--cooperation-collapse-threshold",
        type=float,
        default=0.80,
        help="Cooperation threshold used to classify collapse versus recovery after betrayal.",
    )
    parser.add_argument(
        "--recovery-window-years",
        type=int,
        default=100,
        help="Years allowed for cooperation to recover above the collapse threshold after betrayal.",
    )
    parser.add_argument(
        "--infiltration-year",
        type=int,
        help="Optional year for CL-NET adversarial infiltration node injection.",
    )
    parser.add_argument(
        "--infiltration-fraction",
        type=float,
        default=0.10,
        help="Fraction of current nodes injected as infiltrators when the infiltration event fires.",
    )
    parser.add_argument(
        "--infiltration-trust-damage",
        type=float,
        default=0.03,
        help="Per-step trust-memory damage applied by each infiltrator to its neighbors.",
    )
    parser.add_argument(
        "--infiltration-cooperation-damage",
        type=float,
        default=0.015,
        help="Per-step cooperation damage applied by each infiltrator to its neighbors.",
    )
    parser.add_argument(
        "--local-defense",
        action="store_true",
        help="Enable the CL-NET-3 local trust-based defense layer.",
    )
    parser.add_argument(
        "--defense-trust-threshold",
        type=float,
        default=0.30,
        help="Pairwise trust threshold below which a neighbor accumulates suspicion.",
    )
    parser.add_argument(
        "--defense-consecutive-steps",
        type=int,
        default=10,
        help="Consecutive low-trust steps required before the local defense severs an edge.",
    )
    parser.add_argument(
        "--trust-repair",
        action="store_true",
        help="Enable the CL-NET-4 local trust-reconstruction layer after defense fragmentation.",
    )
    parser.add_argument(
        "--reconnect-probability",
        type=float,
        default=0.05,
        help="Per-step probability that a disconnected non-adversarial pair reconnects when both cooperation scores are high enough.",
    )
    parser.add_argument(
        "--reconnect-cooperation-threshold",
        type=float,
        default=0.60,
        help="Minimum cooperation required for both endpoints before trust repair can reconnect a severed edge.",
    )
    parser.add_argument(
        "--repair-reinforcement-threshold",
        type=float,
        default=0.80,
        help="Cooperation threshold required for sustained post-reconnection trust reinforcement.",
    )
    parser.add_argument(
        "--repair-reinforcement-steps",
        type=int,
        default=20,
        help="Consecutive high-cooperation steps required before a repaired edge receives trust reinforcement.",
    )
    parser.add_argument(
        "--repair-reinforcement-gain",
        type=float,
        default=0.05,
        help="Trust gain applied to a repaired edge after each reinforcement interval.",
    )
    parser.add_argument(
        "--trust-signal-propagation",
        action="store_true",
        help="Enable the CL-NET-5 short-range trust signal layer on top of repair.",
    )
    parser.add_argument(
        "--trust-signal-threshold",
        type=float,
        default=0.80,
        help="Cooperation threshold required before a node emits a trust signal.",
    )
    parser.add_argument(
        "--trust-signal-boost",
        type=float,
        default=0.10,
        help="Per-signal trust boost applied along each local propagation edge.",
    )
    parser.add_argument(
        "--trust-signal-max-distance",
        type=int,
        default=2,
        help="Maximum hop distance for local trust signal propagation.",
    )
    parser.add_argument(
        "--group-coordination-boost",
        action="store_true",
        help="Enable the CL-NET-5 lightweight local group coordination boost.",
    )
    parser.add_argument(
        "--group-boost-neighbor-count",
        type=int,
        default=3,
        help="Stable-neighbor count required before the local group coordination boost fires.",
    )
    parser.add_argument(
        "--group-boost-amount",
        type=float,
        default=0.05,
        help="Cooperation increase applied by the local group coordination boost.",
    )
    parser.add_argument(
        "--proposal-rate-constant",
        type=float,
        default=1.00,
        help="Per-node proposal-rate multiplier k used in the v1.5 bureaucratic layer.",
    )
    parser.add_argument(
        "--governance-bandwidth-base",
        type=float,
        default=0.15,
        help="Base governance bandwidth in the v1.5 bureaucratic layer.",
    )
    parser.add_argument(
        "--governance-bandwidth-tech-multiplier",
        type=float,
        default=1.20,
        help="Tech-to-bandwidth multiplier beta in the v1.5 bureaucratic layer.",
    )
    parser.add_argument(
        "--critical-backlog-threshold",
        type=float,
        default=0.90,
        help="Backlog threshold that triggers defensive actions in the v1.5 bureaucratic layer.",
    )
    parser.add_argument(
        "--proposal-quota-per-node",
        type=float,
        default=0.18,
        help="Per-node proposal cap used by Action A in the v1.5 bureaucratic layer.",
    )
    parser.add_argument(
        "--quota-cooperation-penalty",
        type=float,
        default=0.22,
        help="Per-node cooperation penalty applied when Action A discards proposals.",
    )
    parser.add_argument(
        "--human-control-penalty-per-delegation",
        type=float,
        default=0.20,
        help="Permanent human-control penalty applied by each Action B use.",
    )
    parser.add_argument(
        "--ai-delegation-beta-multiplier",
        type=float,
        default=2.40,
        help="Permanent multiplier applied to governance bandwidth beta by Action B.",
    )
    parser.add_argument(
        "--foundational-veto-stability-penalty",
        type=float,
        default=0.14,
        help="Immediate governance-stability penalty applied by Action C.",
    )
    parser.add_argument(
        "--foundational-veto-tech-pause-cost",
        type=float,
        default=0.10,
        help="Decision cost term used when comparing Action C against other defenses.",
    )
    parser.add_argument(
        "--foundational-veto-freeze-steps",
        type=int,
        default=5,
        help="Number of time steps proposals are frozen after Action C.",
    )
    parser.add_argument(
        "--omega-shock-year",
        type=int,
        help="Optional shock year for injecting Node Omega into the v1.5 bureaucratic layer.",
    )
    parser.add_argument(
        "--omega-shock-factor",
        type=float,
        default=500.0,
        help="AI multiplier applied to Node Omega when the shock is injected.",
    )
    parser.add_argument(
        "--preview-rows",
        type=int,
        default=12,
        help="Number of rows to print to stdout.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional output file path. Use .json or .csv.",
    )
    parser.add_argument(
        "--raw-output",
        type=Path,
        help="Optional output file path for per-run experiment rows. Requires --experiments.",
    )
    parser.add_argument(
        "--experiments",
        action="store_true",
        help="Run the built-in baseline/faster-automation/slower-AI/stronger-cooperation comparison.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.runs <= 0:
        raise ValueError("--runs must be positive")
    if args.raw_output and not args.experiments:
        raise ValueError("--raw-output requires --experiments")
    config = SimulationConfig(
        years=args.years,
        step_years=args.step_years,
        initial_protocol_cohesion=args.initial_protocol_cohesion,
        automation_growth_multiplier=args.automation_growth_multiplier,
        ai_growth_multiplier=args.ai_growth_multiplier,
        cooperation_multiplier=args.cooperation_multiplier,
        enable_bureaucratic_layer=args.bureaucratic_layer,
        topology=args.topology,
        contagion_penalty=args.contagion_penalty,
        systemic_shock_year=args.systemic_shock_year,
        systemic_shock_count=args.systemic_shock_count,
        systemic_shock_stability=args.systemic_shock_stability,
        systemic_shock_target=args.systemic_shock_target,
        hub_failure_year=args.hub_failure_year,
        hub_failure_mode=args.hub_failure_mode,
        hub_failure_stability=args.hub_failure_stability,
        betrayal_year=args.betrayal_year,
        betrayal_fraction=args.betrayal_fraction,
        trust_memory_decay=args.trust_memory_decay,
        cooperation_collapse_threshold=args.cooperation_collapse_threshold,
        recovery_window_years=args.recovery_window_years,
        infiltration_year=args.infiltration_year,
        infiltration_fraction=args.infiltration_fraction,
        infiltration_trust_damage=args.infiltration_trust_damage,
        infiltration_cooperation_damage=args.infiltration_cooperation_damage,
        enable_local_defense=args.local_defense,
        defense_trust_threshold=args.defense_trust_threshold,
        defense_consecutive_steps=args.defense_consecutive_steps,
        enable_trust_repair=args.trust_repair,
        reconnect_probability=args.reconnect_probability,
        reconnect_cooperation_threshold=args.reconnect_cooperation_threshold,
        repair_reinforcement_threshold=args.repair_reinforcement_threshold,
        repair_reinforcement_steps=args.repair_reinforcement_steps,
        repair_reinforcement_gain=args.repair_reinforcement_gain,
        enable_trust_signal_propagation=args.trust_signal_propagation,
        trust_signal_threshold=args.trust_signal_threshold,
        trust_signal_boost=args.trust_signal_boost,
        trust_signal_max_distance=args.trust_signal_max_distance,
        enable_group_coordination_boost=args.group_coordination_boost,
        group_boost_neighbor_count=args.group_boost_neighbor_count,
        group_boost_amount=args.group_boost_amount,
        proposal_rate_constant=args.proposal_rate_constant,
        governance_bandwidth_base=args.governance_bandwidth_base,
        governance_bandwidth_tech_multiplier=args.governance_bandwidth_tech_multiplier,
        critical_backlog_threshold=args.critical_backlog_threshold,
        proposal_quota_per_node=args.proposal_quota_per_node,
        quota_cooperation_penalty=args.quota_cooperation_penalty,
        human_control_penalty_per_delegation=args.human_control_penalty_per_delegation,
        ai_delegation_beta_multiplier=args.ai_delegation_beta_multiplier,
        foundational_veto_stability_penalty=args.foundational_veto_stability_penalty,
        foundational_veto_tech_pause_cost=args.foundational_veto_tech_pause_cost,
        foundational_veto_freeze_steps=args.foundational_veto_freeze_steps,
        omega_shock_year=args.omega_shock_year,
        omega_shock_factor=args.omega_shock_factor,
    )
    if args.experiments:
        experiment_results = print_experiment_report(config, seed=args.seed, runs=args.runs)
        if args.output:
            write_records(experiment_results, args.output)
            print(f"\nSaved experiment results to {args.output}")
        if args.raw_output:
            raw_results = collect_raw_experiment_results(config, seed=args.seed, runs=args.runs)
            write_records(raw_results, args.raw_output)
            print(f"Saved raw experiment results to {args.raw_output}")
        return
    if args.runs > 1:
        batch_results = collect_batch_results(config, seed=args.seed, runs=args.runs)
        print_batch_summary(batch_results)
        if args.output:
            write_records(batch_results, args.output)
            print(f"\nSaved batch results to {args.output}")
        return
    history = run_simulation(config, seed=args.seed)
    print_preview(history, preview_rows=max(1, args.preview_rows))
    print_summary(history, config)
    if args.output:
        write_history(history, args.output)
        print(f"\nSaved full history to {args.output}")


if __name__ == "__main__":
    main()
