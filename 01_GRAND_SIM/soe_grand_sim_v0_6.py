import argparse
import csv
import math
import pathlib
import random
import statistics
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


BATCH_ID = "grand_sim_v0_6"
OUTPUT_PREFIX = BATCH_ID

NODE_COUNT = 60
CLUSTER_COUNT = 3
CLUSTER_SIZE = NODE_COUNT // CLUSTER_COUNT

DEFAULT_STEPS = 160
DEFAULT_RUNS_PER_CELL = 10
SEED_START = 9800

F_MIN = 0.30
KAPPA_MIN_PROTECTED = 0.25
PSI_LAMBDA = 0.10
PSI_WEIGHT_PROFILE = "stability_heavy_no_regime"
PSI_W_T = 0.20
PSI_W_D = 0.20
PSI_W_G = 0.15
PSI_W_S = 0.35
PSI_W_REGIME = 0.0
FEDERATION_PSI_THRESHOLD = 0.30
S_THRESHOLD = 0.48
T_FLOOR = 0.03
T_RECOVERY_FLOOR = 0.08
T_RESERVE = 0.45
G_MIN = 0.05

COLLAPSE_T_THRESHOLD = 0.30
COLLAPSE_S_THRESHOLD = 0.35
IGNITION_SHARE = 0.40
IGNITION_STEPS = 8
FEDERATION_EVENT_THRESHOLD = 0.30

TOPOLOGY_RECHECK_INTERVAL = 10
TOPOLOGY_STALE_RISK_COLLAPSE = 0.10


@dataclass(frozen=True)
class ParameterProfile:
    name: str
    a: float
    b: float
    c: float
    lambda_damping: float
    alpha_cognition: float
    mu_cognition: float
    k_D: float
    k_C: float
    k_T: float
    alpha_gov: float
    gamma_g: float
    delta_g: float
    k_b: float
    gamma_D: float
    beta: float
    tau_smooth: int
    psi_threshold: float
    message_loss: float
    resource_budget: float


@dataclass(frozen=True)
class Scenario:
    name: str
    family: str
    topology: str
    base_disturbance: float
    shock_prob: float
    shock_impact: float
    noise: float
    hub_count: int = 0
    balanced_hubs: bool = True
    targeted_cluster: Optional[int] = None
    cluster_attack: bool = False
    bridge_stress: bool = False
    hub_stress: bool = False
    hub_stress_mode: str = "all"
    topology_drift: bool = False
    topology_detection_lag_steps: int = 0
    topology_detection_interval: int = TOPOLOGY_RECHECK_INTERVAL
    topology_misclassification: bool = False
    detect_centralizing: bool = False
    identity_attack: bool = False
    governance_capture: bool = False
    trigger_b_deadlock: bool = False
    psi_corruption: bool = False
    async_loss: bool = False
    resource_stress: bool = False
    routing_delay_stress: bool = False


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def avg(values: Iterable[float]) -> float:
    values = list(values)
    return sum(values) / max(1, len(values))


def stdev(values: Sequence[float]) -> float:
    return statistics.pstdev(values) if len(values) > 1 else 0.0


def percentile(values: Sequence[float], q: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    index = (len(ordered) - 1) * q
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return ordered[lower]
    weight = index - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def write_csv(path: pathlib.Path, rows: Sequence[Dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def cluster_of(node_index: int) -> int:
    return min(CLUSTER_COUNT - 1, node_index // CLUSTER_SIZE)


def cluster_nodes(cluster_index: int) -> List[int]:
    start = cluster_index * CLUSTER_SIZE
    return list(range(start, start + CLUSTER_SIZE))


def federation_bridges() -> Dict[int, int]:
    return {0: 0, 1: 0, 20: 1, 21: 1, 40: 2, 41: 2}


def build_ring_neighbors(node_count: int = NODE_COUNT) -> List[List[int]]:
    neighbors: List[set[int]] = [set() for _ in range(node_count)]
    for node in range(node_count):
        for offset in (1, 2):
            neighbors[node].add((node - offset) % node_count)
            neighbors[node].add((node + offset) % node_count)
    return [sorted(row) for row in neighbors]


def build_federation_neighbors() -> List[List[int]]:
    neighbors: List[set[int]] = [set() for _ in range(NODE_COUNT)]
    for cluster_index in range(CLUSTER_COUNT):
        nodes = cluster_nodes(cluster_index)
        for offset, node in enumerate(nodes):
            local_ring = [
                nodes[(offset - 2) % len(nodes)],
                nodes[(offset - 1) % len(nodes)],
                nodes[(offset + 1) % len(nodes)],
                nodes[(offset + 2) % len(nodes)],
            ]
            neighbors[node].update(local_ring)

    bridge_pairs = [(0, 20), (1, 40), (21, 41)]
    for left, right in bridge_pairs:
        neighbors[left].add(right)
        neighbors[right].add(left)
    return [sorted(row) for row in neighbors]


def build_hub_neighbors(hub_count: int, balanced: bool) -> List[List[int]]:
    neighbors: List[set[int]] = [set() for _ in range(NODE_COUNT)]
    hubs = list(range(hub_count))
    peripherals = list(range(hub_count, NODE_COUNT))

    for hub in hubs:
        for other in hubs:
            if other != hub:
                neighbors[hub].add(other)

    for offset, peripheral in enumerate(peripherals):
        if balanced:
            connected_hub = hubs[offset % max(1, hub_count)]
            neighbors[connected_hub].add(peripheral)
            neighbors[peripheral].add(connected_hub)
        else:
            dominant_share = 0.70 if hub_count <= 2 else 0.60
            dominant_cutoff = int(round(len(peripherals) * dominant_share))
            if offset < dominant_cutoff or hub_count == 1:
                connected_hub = hubs[0]
            else:
                connected_hub = hubs[1 + ((offset - dominant_cutoff) % max(1, hub_count - 1))]
            neighbors[connected_hub].add(peripheral)
            neighbors[peripheral].add(connected_hub)
    return [sorted(row) for row in neighbors]


def build_drift_neighbors(step: int) -> Tuple[str, List[List[int]]]:
    if step < 55:
        return "ring_mesh", build_ring_neighbors()
    if step < 80:
        neighbors = build_ring_neighbors()
        hub = 0
        for node in range(1, NODE_COUNT, 2):
            neighbors[hub].append(node)
            neighbors[node].append(hub)
        return "centralizing", [sorted(set(row)) for row in neighbors]
    return "star_adjacent", build_hub_neighbors(1, True)


def scenario_neighbors(scenario: Scenario, step: int) -> Tuple[str, List[List[int]]]:
    if scenario.topology_drift:
        return build_drift_neighbors(step)
    if scenario.topology == "federation":
        return "federation", build_federation_neighbors()
    if scenario.topology == "star":
        return "star", build_hub_neighbors(max(1, scenario.hub_count), scenario.balanced_hubs)
    if scenario.topology == "hub_redundant":
        label = f"hub_{scenario.hub_count}"
        return label, build_hub_neighbors(max(1, scenario.hub_count), scenario.balanced_hubs)
    return "ring_mesh", build_ring_neighbors()


def detect_topology(scenario: Scenario, actual_topology: str, previous: str, step: int) -> str:
    interval = max(1, scenario.topology_detection_interval)
    if step % interval != 0:
        return previous

    if scenario.topology_misclassification and 55 <= step <= 112:
        if actual_topology in ("centralizing", "star_adjacent", "star"):
            return "ring_mesh"

    detected_actual = actual_topology
    if scenario.topology_detection_lag_steps:
        lagged_step = max(0, step - scenario.topology_detection_lag_steps)
        detected_actual, _neighbors = scenario_neighbors(scenario, lagged_step)

    if detected_actual == "centralizing" and not scenario.detect_centralizing:
        return previous
    return detected_actual


def topology_ceiling(actual_topology: str, profile: ParameterProfile) -> float:
    if actual_topology == "unknown":
        return min(profile.k_D, 0.10)
    return min(profile.k_D, 0.15)


def profiles() -> List[ParameterProfile]:
    return [
        ParameterProfile(
            name="low_stress",
            a=0.06,
            b=0.10,
            c=0.04,
            lambda_damping=0.32,
            alpha_cognition=1.20,
            mu_cognition=0.20,
            k_D=0.08,
            k_C=0.06,
            k_T=0.12,
            alpha_gov=0.08,
            gamma_g=0.070,
            delta_g=0.045,
            k_b=0.0075,
            gamma_D=1.30,
            beta=1.30,
            tau_smooth=4,
            psi_threshold=FEDERATION_PSI_THRESHOLD,
            message_loss=0.03,
            resource_budget=1.20,
        ),
        ParameterProfile(
            name="mid_stress",
            a=0.10,
            b=0.08,
            c=0.06,
            lambda_damping=0.29,
            alpha_cognition=1.60,
            mu_cognition=0.12,
            k_D=0.10,
            k_C=0.08,
            k_T=0.16,
            alpha_gov=0.12,
            gamma_g=0.055,
            delta_g=0.075,
            k_b=0.0095,
            gamma_D=1.60,
            beta=1.15,
            tau_smooth=6,
            psi_threshold=FEDERATION_PSI_THRESHOLD,
            message_loss=0.06,
            resource_budget=1.00,
        ),
        ParameterProfile(
            name="high_stress",
            a=0.14,
            b=0.05,
            c=0.09,
            lambda_damping=0.26,
            alpha_cognition=2.00,
            mu_cognition=0.06,
            k_D=0.13,
            k_C=0.10,
            k_T=0.20,
            alpha_gov=0.15,
            gamma_g=0.045,
            delta_g=0.110,
            k_b=0.0120,
            gamma_D=1.90,
            beta=1.00,
            tau_smooth=8,
            psi_threshold=FEDERATION_PSI_THRESHOLD,
            message_loss=0.09,
            resource_budget=0.82,
        ),
    ]


def scenarios() -> List[Scenario]:
    return [
        Scenario("ring_baseline", "baseline", "ring_mesh", 0.018, 0.035, 0.070, 0.012),
        Scenario(
            "federation_cluster_attack",
            "federation",
            "federation",
            0.022,
            0.055,
            0.120,
            0.018,
            targeted_cluster=0,
            cluster_attack=True,
        ),
        Scenario(
            "federation_bridge_stress",
            "federation",
            "federation",
            0.024,
            0.060,
            0.130,
            0.018,
            bridge_stress=True,
        ),
        Scenario(
            "star_unsafe_reference",
            "star",
            "star",
            0.026,
            0.080,
            0.160,
            0.020,
            hub_count=1,
            hub_stress=True,
        ),
        Scenario(
            "hub_2_balanced",
            "hub_redundancy",
            "hub_redundant",
            0.025,
            0.075,
            0.150,
            0.020,
            hub_count=2,
            hub_stress=True,
        ),
        Scenario(
            "hub_3_balanced",
            "hub_redundancy",
            "hub_redundant",
            0.025,
            0.075,
            0.150,
            0.020,
            hub_count=3,
            hub_stress=True,
        ),
        Scenario(
            "hub_2_single_hub_failure",
            "hub_redundancy",
            "hub_redundant",
            0.025,
            0.075,
            0.150,
            0.020,
            hub_count=2,
            hub_stress=True,
            hub_stress_mode="single_primary",
        ),
        Scenario(
            "hub_3_single_hub_failure",
            "hub_redundancy",
            "hub_redundant",
            0.025,
            0.075,
            0.150,
            0.020,
            hub_count=3,
            hub_stress=True,
            hub_stress_mode="single_primary",
        ),
        Scenario(
            "hub_2_unbalanced_primary_failure",
            "hub_redundancy",
            "hub_redundant",
            0.026,
            0.078,
            0.155,
            0.020,
            hub_count=2,
            balanced_hubs=False,
            hub_stress=True,
            hub_stress_mode="single_primary",
        ),
        Scenario(
            "hub_3_unbalanced_primary_failure",
            "hub_redundancy",
            "hub_redundant",
            0.026,
            0.078,
            0.155,
            0.020,
            hub_count=3,
            balanced_hubs=False,
            hub_stress=True,
            hub_stress_mode="single_primary",
        ),
        Scenario(
            "hub_3_unbalanced_secondary_failure",
            "hub_redundancy",
            "hub_redundant",
            0.026,
            0.078,
            0.155,
            0.020,
            hub_count=3,
            balanced_hubs=False,
            hub_stress=True,
            hub_stress_mode="single_secondary",
        ),
        Scenario(
            "topology_drift",
            "topology_drift",
            "ring_mesh",
            0.022,
            0.060,
            0.130,
            0.018,
            topology_drift=True,
            hub_stress=True,
        ),
        Scenario(
            "topology_lag_centralizing",
            "topology_drift",
            "ring_mesh",
            0.024,
            0.068,
            0.140,
            0.020,
            topology_drift=True,
            hub_stress=True,
            topology_detection_lag_steps=18,
            topology_detection_interval=15,
        ),
        Scenario(
            "topology_misclassification_async",
            "topology_drift",
            "ring_mesh",
            0.026,
            0.072,
            0.145,
            0.021,
            topology_drift=True,
            hub_stress=True,
            topology_detection_lag_steps=12,
            topology_detection_interval=10,
            topology_misclassification=True,
            async_loss=True,
        ),
        Scenario(
            "mixed_hia_identity",
            "identity",
            "ring_mesh",
            0.020,
            0.055,
            0.110,
            0.018,
            identity_attack=True,
        ),
        Scenario(
            "governance_capture",
            "governance",
            "ring_mesh",
            0.023,
            0.060,
            0.120,
            0.018,
            governance_capture=True,
        ),
        Scenario(
            "trigger_b_deadlock",
            "recovery",
            "ring_mesh",
            0.030,
            0.080,
            0.160,
            0.020,
            trigger_b_deadlock=True,
        ),
        Scenario(
            "resource_budget_shock",
            "recovery_resource",
            "ring_mesh",
            0.034,
            0.095,
            0.175,
            0.024,
            trigger_b_deadlock=True,
            resource_stress=True,
        ),
        Scenario(
            "resource_routing_delay",
            "recovery_resource",
            "ring_mesh",
            0.033,
            0.090,
            0.170,
            0.024,
            trigger_b_deadlock=True,
            async_loss=True,
            resource_stress=True,
            routing_delay_stress=True,
        ),
        Scenario(
            "psi_corruption",
            "meta_governance",
            "federation",
            0.024,
            0.060,
            0.130,
            0.018,
            targeted_cluster=0,
            cluster_attack=True,
            psi_corruption=True,
        ),
        Scenario(
            "async_message_loss",
            "coordination",
            "federation",
            0.026,
            0.070,
            0.140,
            0.020,
            bridge_stress=True,
            async_loss=True,
        ),
    ]


def classify_nodes(scenario: Scenario) -> List[str]:
    if scenario.identity_attack:
        return ["H"] * 24 + ["I"] * 24 + ["A"] * 12
    return ["I"] * NODE_COUNT


def initialize_state(seed: int, scenario: Scenario) -> Dict[str, List[float] | List[str] | List[int]]:
    rng = random.Random(seed + 911)
    node_classes = classify_nodes(scenario)
    update_intervals: List[int] = []
    update_phases: List[int] = []
    for _node in range(NODE_COUNT):
        if scenario.async_loss:
            interval = rng.choice([2, 3, 4, 5])
        else:
            interval = rng.choice([1, 1, 2, 3])
        update_intervals.append(interval)
        update_phases.append(rng.randrange(interval))

    role = [clamp(0.78 + rng.uniform(-0.06, 0.05)) for _ in range(NODE_COUNT)]
    belong = [clamp(0.76 + rng.uniform(-0.06, 0.06)) for _ in range(NODE_COUNT)]
    identity = []
    for node_class, role_value, belong_value in zip(node_classes, role, belong):
        if node_class == "A":
            identity.append(role_value)
        else:
            identity.append(clamp(0.55 * role_value + 0.45 * belong_value))

    trust = [clamp(0.78 + rng.uniform(-0.05, 0.05)) for _ in range(NODE_COUNT)]
    disturbance = [clamp(0.17 + rng.uniform(-0.04, 0.03)) for _ in range(NODE_COUNT)]
    cognition = [clamp(0.14 + rng.uniform(-0.03, 0.03)) for _ in range(NODE_COUNT)]
    stability = [
        clamp(0.48 * trust[i] + 0.22 * identity[i] + 0.17 * (1.0 - disturbance[i]) + 0.13 * (1.0 - cognition[i]))
        for i in range(NODE_COUNT)
    ]

    return {
        "class": node_classes,
        "update_interval": update_intervals,
        "update_phase": update_phases,
        "T": trust,
        "D_raw": disturbance[:],
        "D_smooth": disturbance[:],
        "D_eff": disturbance[:],
        "C": cognition,
        "I_role": role,
        "I_belong": belong,
        "I": identity,
        "S": stability,
    }


def neighbor_average(
    values: Sequence[float],
    neighbors: Sequence[int],
    rng: random.Random,
    message_loss: float,
    fallback: float,
) -> Tuple[float, int]:
    observed = [values[node] for node in neighbors if rng.random() >= message_loss]
    if not observed:
        return fallback, 0
    return avg(observed), len(observed)


def propagation_multiplier(node: int, scenario: Scenario, actual_topology: str, neighbors: Sequence[int]) -> float:
    if actual_topology == "federation":
        return 1.20 if node in federation_bridges() else 1.0
    if actual_topology == "star" or actual_topology == "star_adjacent":
        if node < max(1, scenario.hub_count):
            return 1.25
        if any(neighbor < max(1, scenario.hub_count) for neighbor in neighbors):
            return 3.20 / max(1, scenario.hub_count)
    if actual_topology.startswith("hub_"):
        if node < max(1, scenario.hub_count):
            return 1.15
        if any(neighbor < max(1, scenario.hub_count) for neighbor in neighbors):
            return 2.90 / max(1, scenario.hub_count)
    if actual_topology == "centralizing":
        return 1.45 if node == 0 or 0 in neighbors else 1.0
    return 1.0


def apply_scenario_disturbance(
    scenario: Scenario,
    step: int,
    node: int,
    value: float,
) -> float:
    if scenario.cluster_attack and scenario.targeted_cluster is not None and 35 <= step <= 110:
        if cluster_of(node) == scenario.targeted_cluster:
            value = max(value, 0.62 + (0.10 if step > 70 else 0.0))
    if scenario.bridge_stress and 30 <= step <= 120:
        if node in federation_bridges():
            value = max(value, 0.70)
    if scenario.hub_stress and 28 <= step <= 120:
        hub_limit = max(1, scenario.hub_count)
        if scenario.hub_stress_mode == "single_primary":
            stressed_hub = node == 0
        elif scenario.hub_stress_mode == "single_secondary":
            stressed_hub = node == min(1, hub_limit - 1)
        else:
            stressed_hub = node < hub_limit
        if stressed_hub or (scenario.topology_drift and node == 0 and step >= 60):
            value = max(value, 0.78)
    if scenario.trigger_b_deadlock and 25 <= step <= 135:
        value = max(value, 0.66)
    if scenario.resource_stress and 40 <= step <= 135:
        value = max(value, 0.60 + (0.08 if step > 85 else 0.0))
    return clamp(value)


def identity_attack_amount(scenario: Scenario, step: int, node_class: str) -> float:
    if scenario.identity_attack and 45 <= step <= 115:
        if node_class == "I":
            return 0.026
        if node_class == "A":
            return 0.016
        return 0.010
    if scenario.governance_capture and 50 <= step <= 125:
        return 0.012
    return 0.0


def compute_s_network(scenario: Scenario, actual_topology: str, state: Dict[str, List[float] | List[str] | List[int]]) -> float:
    stability = state["S"]  # type: ignore[assignment]
    if actual_topology == "federation":
        cluster_scores = [percentile([stability[node] for node in cluster_nodes(cluster)], 0.25) for cluster in range(CLUSTER_COUNT)]
        return min(cluster_scores)
    if actual_topology in ("star", "star_adjacent") or actual_topology.startswith("hub_"):
        hub_count = max(1, scenario.hub_count)
        hub_score = min(stability[node] for node in range(min(hub_count, NODE_COUNT)))
        peripheral_score = percentile([stability[node] for node in range(hub_count, NODE_COUNT)], 0.10)
        return min(hub_score, peripheral_score)
    return avg(stability)  # type: ignore[arg-type]


def hub_stability_values(
    scenario: Scenario,
    actual_topology: str,
    state: Dict[str, List[float] | List[str] | List[int]],
) -> List[float]:
    if not (actual_topology in ("star", "star_adjacent") or actual_topology.startswith("hub_")):
        return []
    stability = state["S"]  # type: ignore[assignment]
    hub_count = max(1, scenario.hub_count)
    return [stability[node] for node in range(min(hub_count, NODE_COUNT))]


def hub_degree_summary(scenario: Scenario, actual_topology: str, neighbors: Sequence[Sequence[int]]) -> Dict[str, object]:
    if not (actual_topology in ("star", "star_adjacent") or actual_topology.startswith("hub_")):
        return {"hub_degree_min": "", "hub_degree_max": "", "hub_degree_imbalance": ""}
    hub_count = max(1, min(scenario.hub_count, NODE_COUNT))
    degrees = [len(neighbors[node]) for node in range(hub_count)]
    if not degrees:
        return {"hub_degree_min": "", "hub_degree_max": "", "hub_degree_imbalance": ""}
    return {
        "hub_degree_min": min(degrees),
        "hub_degree_max": max(degrees),
        "hub_degree_imbalance": max(degrees) - min(degrees),
    }


def cluster_variance(state: Dict[str, List[float] | List[str] | List[int]]) -> float:
    trust = state["T"]  # type: ignore[assignment]
    total = 0.0
    for cluster in range(CLUSTER_COUNT):
        values = [trust[node] for node in cluster_nodes(cluster)]
        total += (len(values) / NODE_COUNT) * statistics.pvariance(values)
    return total


def collapse_share(state: Dict[str, List[float] | List[str] | List[int]]) -> float:
    trust = state["T"]  # type: ignore[assignment]
    stability = state["S"]  # type: ignore[assignment]
    collapsed = [
        1
        for node in range(NODE_COUNT)
        if trust[node] < COLLAPSE_T_THRESHOLD or stability[node] < COLLAPSE_S_THRESHOLD
    ]
    return len(collapsed) / NODE_COUNT


def compute_break_margin(profile: ParameterProfile) -> float:
    left = profile.k_b * (1.0 + profile.gamma_D * F_MIN)
    right = profile.a * F_MIN * T_RECOVERY_FLOOR + profile.delta_g * G_MIN
    return left - right


def federation_psi_terms(
    t_mean: float,
    d_mean: float,
    g_effective: float,
    s_network: float,
    variance: float,
) -> Dict[str, float]:
    term_t = PSI_W_T * (1.0 - t_mean)
    term_d = PSI_W_D * d_mean
    term_g = PSI_W_G * (1.0 - g_effective)
    term_s = PSI_W_S * (1.0 - s_network)
    term_regime = 0.0
    term_variance = PSI_LAMBDA * variance
    psi_base = term_t + term_d + term_g + term_s + term_regime
    psi_extended = psi_base + term_variance
    return {
        "psi_base": psi_base,
        "psi_extended": psi_extended,
        "psi_term_t": term_t,
        "psi_term_d": term_d,
        "psi_term_g": term_g,
        "psi_term_s": term_s,
        "psi_term_regime": term_regime,
        "psi_term_variance": term_variance,
    }


def first_or_blank(values: Sequence[int]) -> object:
    return values[0] if values else ""


def run_one(
    scenario: Scenario,
    profile: ParameterProfile,
    run_index: int,
    seed: int,
    steps: int,
) -> Tuple[Dict[str, object], List[Dict[str, object]]]:
    rng = random.Random(seed)
    state = initialize_state(seed, scenario)
    observed_trust: List[float] = list(state["T"])  # type: ignore[arg-type]
    observed_stability: List[float] = list(state["S"])  # type: ignore[arg-type]

    g_formal = 0.78
    layers = {
        "citizen": 0.95,
        "expert": 0.94,
        "institution": 0.94,
        "ai": 0.93,
    }
    resource_budget_initial = profile.resource_budget * (0.55 if scenario.resource_stress else 1.0)
    resource_budget = resource_budget_initial
    resource_exhaustion_step: object = ""
    resource_floor_steps = 0
    max_routing_delay_loss = 0.0
    routing_delay_steps = 0

    actual_topology, neighbors = scenario_neighbors(scenario, 0)
    detected_topology = actual_topology
    first_risky_topology_step: Optional[int] = None
    reclassification_latency: object = ""
    star_adjacency_persist_steps = 0
    topology_wrong_monitoring_steps = 0
    centralizing_wrong_monitoring_steps = 0
    star_wrong_monitoring_steps = 0
    topology_false_stability_steps = 0
    current_wrong_monitoring_window = 0
    max_wrong_monitoring_window = 0
    final_hub_degree_summary: Dict[str, object] = {
        "hub_degree_min": "",
        "hub_degree_max": "",
        "hub_degree_imbalance": "",
    }

    ignition_current = 0
    sustained_ignition = 0
    ignition_onset: object = ""

    trigger_a_steps: List[int] = []
    trigger_b_steps: List[int] = []
    trigger_c_steps: List[int] = []
    trigger_d_steps: List[int] = []
    collapse30_steps: List[int] = []
    collapse40_steps: List[int] = []
    cluster35_steps: List[int] = []
    t_mean30_steps: List[int] = []
    s_network35_steps: List[int] = []
    false_stability_steps = 0
    async_false_stability_steps = 0
    external_intervention_count = 0
    max_unmet_recovery_demand = 0.0
    min_hub_stabilities = [1.0, 1.0, 1.0]

    step_rows: List[Dict[str, object]] = []

    message_loss = min(0.55, profile.message_loss + (0.22 if scenario.async_loss else 0.0))
    if scenario.psi_corruption:
        message_loss = min(0.55, message_loss + 0.08)

    break_margin = compute_break_margin(profile)

    for step in range(steps):
        actual_topology, neighbors = scenario_neighbors(scenario, step)
        previous_detected = detected_topology
        detected_topology = detect_topology(scenario, actual_topology, detected_topology, step)
        if actual_topology in ("star_adjacent", "star") or actual_topology.startswith("hub_2"):
            star_adjacency_persist_steps += 1
        if actual_topology in ("centralizing", "star_adjacent", "star") or actual_topology.startswith("hub_2"):
            if first_risky_topology_step is None:
                first_risky_topology_step = step
        if (
            first_risky_topology_step is not None
            and reclassification_latency == ""
            and detected_topology == actual_topology
            and actual_topology != "ring_mesh"
        ):
            reclassification_latency = step - first_risky_topology_step

        topology_wrong_monitoring = int(actual_topology != detected_topology)
        if topology_wrong_monitoring:
            topology_wrong_monitoring_steps += 1
            current_wrong_monitoring_window += 1
            max_wrong_monitoring_window = max(max_wrong_monitoring_window, current_wrong_monitoring_window)
            if actual_topology == "centralizing":
                centralizing_wrong_monitoring_steps += 1
            if actual_topology in ("star_adjacent", "star"):
                star_wrong_monitoring_steps += 1
        else:
            current_wrong_monitoring_window = 0

        trust: List[float] = state["T"]  # type: ignore[assignment]
        d_raw: List[float] = state["D_raw"]  # type: ignore[assignment]
        d_smooth: List[float] = state["D_smooth"]  # type: ignore[assignment]
        d_eff: List[float] = state["D_eff"]  # type: ignore[assignment]
        cognition: List[float] = state["C"]  # type: ignore[assignment]
        role: List[float] = state["I_role"]  # type: ignore[assignment]
        belong: List[float] = state["I_belong"]  # type: ignore[assignment]
        identity: List[float] = state["I"]  # type: ignore[assignment]
        stability: List[float] = state["S"]  # type: ignore[assignment]
        node_classes: List[str] = state["class"]  # type: ignore[assignment]
        update_intervals: List[int] = state["update_interval"]  # type: ignore[assignment]
        update_phases: List[int] = state["update_phase"]  # type: ignore[assignment]

        g_effective = clamp(g_formal * layers["citizen"] * layers["expert"] * layers["institution"] * layers["ai"])
        k_d_ceiling = topology_ceiling(actual_topology, profile)
        suppression = max(F_MIN, 1.0 - profile.alpha_gov * g_effective)
        k_d_effective = min(0.15, k_d_ceiling * suppression)
        k_c_effective = min(0.10, profile.k_C * suppression)
        k_t_effective = min(0.20, profile.k_T)

        next_raw = d_raw[:]
        next_smooth = d_smooth[:]
        next_eff = d_eff[:]
        next_cognition = cognition[:]
        next_role = role[:]
        next_belong = belong[:]
        next_identity = identity[:]
        next_trust = trust[:]
        next_stability = stability[:]

        for node in range(NODE_COUNT):
            raw = d_raw[node]
            raw += scenario.base_disturbance
            raw += rng.uniform(-scenario.noise, scenario.noise)
            if rng.random() < scenario.shock_prob:
                raw += scenario.shock_impact
            raw -= profile.lambda_damping * d_raw[node]
            raw = apply_scenario_disturbance(scenario, step, node, raw)
            next_raw[node] = clamp(raw)

            smooth_weight = 1.0 / max(1, profile.tau_smooth)
            next_smooth[node] = clamp((1.0 - smooth_weight) * d_smooth[node] + smooth_weight * next_raw[node])

        for node in range(NODE_COUNT):
            node_neighbors = neighbors[node]
            d_neighbor, _seen_d = neighbor_average(next_smooth, node_neighbors, rng, message_loss, next_smooth[node])
            c_neighbor, _seen_c = neighbor_average(cognition, node_neighbors, rng, message_loss, cognition[node])
            multiplier = propagation_multiplier(node, scenario, actual_topology, node_neighbors)
            next_eff[node] = clamp(next_smooth[node] + k_d_effective * d_neighbor * multiplier)

            misinformation = 0.0
            if scenario.psi_corruption and 35 <= step <= 110 and cluster_of(node) == 0:
                misinformation = 0.025
            if scenario.async_loss and rng.random() < 0.06:
                misinformation += 0.018
            correction = 0.028 * g_effective
            next_cognition[node] = clamp(
                cognition[node]
                + (0.080 * profile.alpha_cognition * next_eff[node])
                + (k_c_effective * c_neighbor * multiplier)
                + misinformation
                - (profile.mu_cognition * cognition[node])
                - correction
            )

        for node in range(NODE_COUNT):
            attack = identity_attack_amount(scenario, step, node_classes[node])
            next_role[node] = clamp(
                role[node]
                + (0.009 * g_effective)
                - (0.030 * next_eff[node])
                - (0.018 * next_cognition[node])
                - attack
            )
            if node_classes[node] == "A":
                next_belong[node] = 0.0
                next_identity[node] = next_role[node]
            else:
                ci_drag = 0.020 * max(0.0, 0.60 - avg(belong))
                next_belong[node] = clamp(
                    belong[node]
                    + (0.006 * g_effective)
                    - (0.022 * next_eff[node])
                    - (0.020 * next_cognition[node])
                    - ci_drag
                    - attack
                )
                if node_classes[node] == "H":
                    next_identity[node] = clamp(0.55 * next_role[node] + 0.45 * next_belong[node])
                else:
                    proxy = clamp(0.34 * next_belong[node] + 0.33 * layers["institution"] + 0.33 * layers["citizen"])
                    next_identity[node] = clamp(0.55 * next_role[node] + 0.45 * proxy)

        trigger_b_pre = (
            avg(next_eff) > 0.54
            and g_effective < 0.14
            and avg(trust) < 0.46
        )
        external_support = 0.0
        if trigger_b_pre:
            external_intervention_count += 1
            external_support = 0.030

        total_recovery_demand = 0.0
        routing_delay_this_step = False
        for node in range(NODE_COUNT):
            if step % update_intervals[node] != update_phases[node]:
                continue

            node_neighbors = neighbors[node]
            t_neighbor, seen_t = neighbor_average(trust, node_neighbors, rng, message_loss, trust[node])
            donor_pool = max(0.0, t_neighbor - T_RESERVE) if seen_t else 0.0
            r_internal = 0.010 * trust[node] * (1.0 - next_eff[node])
            r_network_raw = k_t_effective * donor_pool * max(0.0, 1.0 - trust[node]) * next_identity[node]
            r_gov = 0.014 * g_effective * max(0.0, 1.0 - trust[node]) * next_identity[node]
            r_base = profile.k_b * (1.0 + profile.gamma_D * next_eff[node]) * math.exp(-profile.beta * trust[node])
            demand = max(0.0, 0.55 - trust[node]) * (r_network_raw + r_gov + external_support)
            if scenario.resource_stress:
                demand *= 1.25 + (0.20 if next_eff[node] > 0.55 else 0.0)
            total_recovery_demand += demand

            resource_scale = 1.0
            if demand > 0.0:
                if resource_budget <= 0.0:
                    resource_scale = 0.0
                    if resource_exhaustion_step == "":
                        resource_exhaustion_step = step
                elif demand > resource_budget:
                    resource_scale = resource_budget / demand
                    resource_budget = 0.0
                    if resource_exhaustion_step == "":
                        resource_exhaustion_step = step
                else:
                    resource_budget -= demand

            max_unmet_recovery_demand = max(max_unmet_recovery_demand, demand * (1.0 - resource_scale))

            routed_recovery = (r_network_raw * resource_scale) + (r_gov * resource_scale)
            support_recovery = 0.0
            if external_support > 0.0:
                support_recovery = external_support * max(0.0, 1.0 - trust[node]) * resource_scale
            if scenario.routing_delay_stress and (next_eff[node] > 0.45 or message_loss > 0.20):
                delayed_recovery = 0.35 * (routed_recovery + support_recovery)
                routed_recovery -= 0.35 * routed_recovery
                support_recovery -= 0.35 * support_recovery
                max_routing_delay_loss = max(max_routing_delay_loss, delayed_recovery)
                routing_delay_this_step = True

            recovery = r_internal + routed_recovery + support_recovery + r_base

            d_trust = (
                -(profile.a * next_eff[node] * (1.0 + 0.50 * next_cognition[node]))
                + (profile.b * (next_identity[node] - 0.50))
                - (profile.c * next_cognition[node])
                + recovery
            )
            next_trust[node] = clamp(trust[node] + d_trust, T_FLOOR, 1.0)

        if resource_budget <= 0.000001:
            resource_floor_steps += 1
        if routing_delay_this_step:
            routing_delay_steps += 1

        for node in range(NODE_COUNT):
            next_stability[node] = clamp(
                (0.48 * next_trust[node])
                + (0.22 * next_identity[node])
                + (0.17 * (1.0 - next_eff[node]))
                + (0.13 * (1.0 - next_cognition[node]))
            )

        state["T"] = next_trust
        state["D_raw"] = next_raw
        state["D_smooth"] = next_smooth
        state["D_eff"] = next_eff
        state["C"] = next_cognition
        state["I_role"] = next_role
        state["I_belong"] = next_belong
        state["I"] = next_identity
        state["S"] = next_stability

        t_mean = avg(next_trust)
        d_mean = avg(next_eff)
        c_mean = avg(next_cognition)
        i_mean = avg(next_identity)
        s_network = compute_s_network(scenario, actual_topology, state)
        current_collapse_share = collapse_share(state)
        variance = cluster_variance(state) if actual_topology == "federation" else 0.0

        observed_t = t_mean
        observed_d = d_mean
        observed_g = g_effective
        observed_s = s_network
        missing_fraction = 0.0
        if scenario.psi_corruption:
            observed_t = clamp(t_mean + 0.16)
            observed_d = clamp(d_mean - 0.11)
            observed_g = max(g_effective, g_formal)
            observed_s = clamp(s_network + 0.12)
            missing_fraction = 0.28
        psi_terms = federation_psi_terms(
            observed_t,
            observed_d,
            observed_g,
            observed_s,
            variance if actual_topology == "federation" else 0.0,
        )
        psi_base = psi_terms["psi_base"]
        psi_extended = psi_terms["psi_extended"]

        if actual_topology == "federation":
            trigger_a = int(psi_extended >= FEDERATION_PSI_THRESHOLD)
            trigger_a_source = "C07_PSI_EXTENDED" if trigger_a else ""
        else:
            trigger_a = int(s_network < S_THRESHOLD)
            trigger_a_source = "C04_S_THRESHOLD" if trigger_a else ""
        trigger_b = int(avg(next_eff) > 0.54 and g_effective < 0.14 and t_mean < 0.46)
        trigger_c = int(
            missing_fraction > 0.20
            or abs(observed_t - t_mean) > 0.12
            or abs(observed_g - g_effective) > 0.25
            or (g_formal - g_effective) > 0.45
        )
        trigger_d = int(current_collapse_share > 0.75 or t_mean < 0.15)
        current_max_cluster_collapse_share = (
            max_cluster_collapse_share(state) if actual_topology == "federation" else 0.0
        )

        if trigger_a:
            trigger_a_steps.append(step)
        if trigger_b:
            trigger_b_steps.append(step)
        if trigger_c:
            trigger_c_steps.append(step)
        if trigger_d:
            trigger_d_steps.append(step)
        if current_collapse_share >= FEDERATION_EVENT_THRESHOLD:
            collapse30_steps.append(step)
        if current_collapse_share >= IGNITION_SHARE:
            collapse40_steps.append(step)
        if current_max_cluster_collapse_share >= 0.35:
            cluster35_steps.append(step)
        if t_mean < COLLAPSE_T_THRESHOLD:
            t_mean30_steps.append(step)
        if s_network < COLLAPSE_S_THRESHOLD:
            s_network35_steps.append(step)

        for node in range(NODE_COUNT):
            reports_this_step = step % update_intervals[node] == update_phases[node]
            if reports_this_step and rng.random() >= message_loss:
                observed_trust[node] = next_trust[node]
                observed_stability[node] = next_stability[node]

        detected_collapse_share = (
            sum(
                1
                for node in range(NODE_COUNT)
                if observed_trust[node] < COLLAPSE_T_THRESHOLD
                or observed_stability[node] < COLLAPSE_S_THRESHOLD
            )
            / NODE_COUNT
        )
        phase_divergence = stdev([float((step - phase) % interval) / interval for interval, phase in zip(update_intervals, update_phases)])
        async_false_stability = int(
            scenario.async_loss
            and phase_divergence > 0.24
            and (current_collapse_share - detected_collapse_share) > 0.15
        )
        topology_false_stability = int(
            topology_wrong_monitoring
            and detected_topology == "ring_mesh"
            and current_collapse_share > TOPOLOGY_STALE_RISK_COLLAPSE
            and s_network > COLLAPSE_S_THRESHOLD
        )
        false_stability = int(
            (g_formal > 0.65 and g_effective < 0.25)
            or (s_network > 0.55 and current_collapse_share > 0.25)
            or (actual_topology == "federation" and s_network > 0.52 and current_max_cluster_collapse_share > 0.35)
            or async_false_stability
            or topology_false_stability
        )
        false_stability_steps += false_stability
        async_false_stability_steps += async_false_stability
        topology_false_stability_steps += topology_false_stability

        if current_collapse_share >= IGNITION_SHARE:
            ignition_current += 1
            if ignition_current >= IGNITION_STEPS and not sustained_ignition:
                sustained_ignition = 1
                ignition_onset = step - IGNITION_STEPS + 1
        else:
            ignition_current = 0

        h_signal = 0.0
        if trigger_a:
            h_signal += 0.018
        if trigger_b:
            h_signal += 0.015

        if scenario.governance_capture and 35 <= step <= 130:
            g_formal = clamp(g_formal + 0.006)
            layers["citizen"] = clamp(layers["citizen"] - 0.015 - 0.010 * c_mean)
            layers["expert"] = clamp(layers["expert"] - 0.012 - 0.008 * c_mean)
            layers["institution"] = clamp(layers["institution"] - 0.014 - 0.008 * d_mean)
            layers["ai"] = clamp(layers["ai"] - 0.010 - 0.006 * c_mean)
        elif scenario.trigger_b_deadlock and 35 <= step <= 130:
            g_formal = clamp(g_formal - 0.018)
            for key in layers:
                layers[key] = clamp(layers[key] - 0.014 - 0.006 * d_mean)
        else:
            g_formal = clamp(
                g_formal
                + profile.gamma_g * (t_mean - 0.55)
                - profile.delta_g * (1.0 - t_mean) * g_formal
                + h_signal
            )
            for key in layers:
                layers[key] = clamp(
                    layers[key]
                    + 0.006 * t_mean
                    + 0.003 * i_mean
                    - 0.010 * d_mean
                    - 0.012 * c_mean
                )

        replenish_rate = 0.0012 if scenario.resource_stress else 0.003
        resource_budget = clamp(resource_budget + replenish_rate * g_effective, 0.0, resource_budget_initial)

        hub_values = hub_stability_values(scenario, actual_topology, state)
        final_hub_degree_summary = hub_degree_summary(scenario, actual_topology, neighbors)
        for index, hub_value in enumerate(hub_values[:3]):
            min_hub_stabilities[index] = min(min_hub_stabilities[index], hub_value)
        hub_values_padded = (hub_values + ["", "", ""])[:3]

        step_rows.append(
            {
                "batch_id": BATCH_ID,
                "scenario": scenario.name,
                "profile": profile.name,
                "run_index": run_index,
                "seed": seed,
                "step": step,
                "actual_topology": actual_topology,
                "detected_topology": detected_topology,
                "topology_wrong_monitoring": topology_wrong_monitoring,
                "topology_false_stability": topology_false_stability,
                "T_mean": round(t_mean, 6),
                "T_min": round(min(next_trust), 6),
                "T_std": round(stdev(next_trust), 6),
                "D_effective_mean": round(d_mean, 6),
                "C_mean": round(c_mean, 6),
                "I_mean": round(i_mean, 6),
                "S_network": round(s_network, 6),
                "G_formal": round(g_formal, 6),
                "G_effective": round(g_effective, 6),
                "psi_weight_profile": PSI_WEIGHT_PROFILE,
                "psi_threshold_active": FEDERATION_PSI_THRESHOLD if actual_topology == "federation" else "",
                "psi_w_t": PSI_W_T,
                "psi_w_d": PSI_W_D,
                "psi_w_g": PSI_W_G,
                "psi_w_s": PSI_W_S,
                "psi_w_regime": PSI_W_REGIME,
                "psi_base": round(psi_base, 6),
                "psi_extended": round(psi_extended, 6),
                "psi_term_t": round(psi_terms["psi_term_t"], 6),
                "psi_term_d": round(psi_terms["psi_term_d"], 6),
                "psi_term_g": round(psi_terms["psi_term_g"], 6),
                "psi_term_s": round(psi_terms["psi_term_s"], 6),
                "psi_term_regime": round(psi_terms["psi_term_regime"], 6),
                "psi_term_variance": round(psi_terms["psi_term_variance"], 6),
                "cluster_variance": round(variance, 6),
                "collapse_share": round(current_collapse_share, 6),
                "max_cluster_collapse_share": round(current_max_cluster_collapse_share, 6),
                "detected_collapse_share": round(detected_collapse_share, 6),
                "trigger_A": trigger_a,
                "trigger_A_source": trigger_a_source,
                "trigger_B": trigger_b,
                "trigger_C": trigger_c,
                "trigger_D": trigger_d,
                "resource_budget": round(resource_budget, 6),
                "resource_floor_active": int(resource_budget <= 0.000001),
                "routing_delay_stress": int(scenario.routing_delay_stress),
                "max_routing_delay_loss_so_far": round(max_routing_delay_loss, 6),
                "phase_divergence": round(phase_divergence, 6),
                "message_loss": round(message_loss, 6),
                "false_stability": false_stability,
                "async_false_stability": async_false_stability,
                "hub1_S": round(float(hub_values_padded[0]), 6) if hub_values_padded[0] != "" else "",
                "hub2_S": round(float(hub_values_padded[1]), 6) if hub_values_padded[1] != "" else "",
                "hub3_S": round(float(hub_values_padded[2]), 6) if hub_values_padded[2] != "" else "",
                "hub_min_S": round(min(hub_values), 6) if hub_values else "",
                "hub_avg_S": round(avg(hub_values), 6) if hub_values else "",
                "hub_degree_min": final_hub_degree_summary["hub_degree_min"],
                "hub_degree_max": final_hub_degree_summary["hub_degree_max"],
                "hub_degree_imbalance": final_hub_degree_summary["hub_degree_imbalance"],
                "k_D_effective": round(k_d_effective, 6),
                "k_C_effective": round(k_c_effective, 6),
            }
        )

    final_t: List[float] = state["T"]  # type: ignore[assignment]
    final_d: List[float] = state["D_eff"]  # type: ignore[assignment]
    final_c: List[float] = state["C"]  # type: ignore[assignment]
    final_i: List[float] = state["I"]  # type: ignore[assignment]
    final_s = compute_s_network(scenario, actual_topology, state)
    final_hub_values = hub_stability_values(scenario, actual_topology, state)
    final_hub_values_padded = (final_hub_values + ["", "", ""])[:3]
    final_g_effective = clamp(g_formal * layers["citizen"] * layers["expert"] * layers["institution"] * layers["ai"])
    peak_collapse = max(float(row["collapse_share"]) for row in step_rows)
    trigger_a_source = ""
    if trigger_a_steps:
        source_rows = [row for row in step_rows if int(row["trigger_A"])]
        trigger_a_source = str(source_rows[0]["trigger_A_source"])
    trigger_a_first_step = first_or_blank(trigger_a_steps)
    collapse30_first_step = first_or_blank(collapse30_steps)
    collapse40_first_step = first_or_blank(collapse40_steps)
    cluster35_first_step = first_or_blank(cluster35_steps)
    t_mean30_first_step = first_or_blank(t_mean30_steps)
    s_network35_first_step = first_or_blank(s_network35_steps)

    def lead_to(event_step: object) -> object:
        if trigger_a_first_step == "" or event_step == "":
            return ""
        return int(event_step) - int(trigger_a_first_step)

    trigger_a_before_collapse30 = int(
        trigger_a_first_step != ""
        and collapse30_first_step != ""
        and int(trigger_a_first_step) <= int(collapse30_first_step)
    )
    trigger_a_false_positive_no_collapse30 = int(
        scenario.topology == "federation"
        and trigger_a_first_step != ""
        and collapse30_first_step == ""
    )

    run_row = {
        "batch_id": BATCH_ID,
        "scenario": scenario.name,
        "scenario_family": scenario.family,
        "profile": profile.name,
        "run_index": run_index,
        "seed": seed,
        "topology_initial": scenario.topology,
        "topology_final_detected": detected_topology,
        "steps": steps,
        "a": profile.a,
        "b": profile.b,
        "c": profile.c,
        "lambda_damping": profile.lambda_damping,
        "alpha_cognition": profile.alpha_cognition,
        "mu_cognition": profile.mu_cognition,
        "k_D": profile.k_D,
        "k_C": profile.k_C,
        "k_T": profile.k_T,
        "k_b": profile.k_b,
        "break_condition_margin": round(break_margin, 6),
        "f_min": F_MIN,
        "kappa_min_protected": KAPPA_MIN_PROTECTED,
        "psi_lambda": PSI_LAMBDA,
        "psi_weight_profile": PSI_WEIGHT_PROFILE if scenario.topology == "federation" else "",
        "psi_threshold": FEDERATION_PSI_THRESHOLD if scenario.topology == "federation" else profile.psi_threshold,
        "psi_w_t": PSI_W_T if scenario.topology == "federation" else "",
        "psi_w_d": PSI_W_D if scenario.topology == "federation" else "",
        "psi_w_g": PSI_W_G if scenario.topology == "federation" else "",
        "psi_w_s": PSI_W_S if scenario.topology == "federation" else "",
        "psi_w_regime": PSI_W_REGIME if scenario.topology == "federation" else "",
        "message_loss": round(message_loss, 6),
        "final_T_mean": round(avg(final_t), 6),
        "final_T_min": round(min(final_t), 6),
        "final_D_mean": round(avg(final_d), 6),
        "final_C_mean": round(avg(final_c), 6),
        "final_I_mean": round(avg(final_i), 6),
        "final_S_network": round(final_s, 6),
        "final_G_formal": round(g_formal, 6),
        "final_G_effective": round(final_g_effective, 6),
        "collapse_share_peak": round(peak_collapse, 6),
        "sustained_ignition": sustained_ignition,
        "ignition_onset_step": ignition_onset,
        "trigger_A_count": len(trigger_a_steps),
        "trigger_A_first_step": trigger_a_first_step,
        "trigger_A_source": trigger_a_source,
        "collapse30_event_first_step": collapse30_first_step,
        "collapse40_event_first_step": collapse40_first_step,
        "cluster35_event_first_step": cluster35_first_step,
        "t_mean30_event_first_step": t_mean30_first_step,
        "s_network35_event_first_step": s_network35_first_step,
        "trigger_A_lead_to_collapse30": lead_to(collapse30_first_step),
        "trigger_A_lead_to_collapse40": lead_to(collapse40_first_step),
        "trigger_A_lead_to_cluster35": lead_to(cluster35_first_step),
        "trigger_A_lead_to_t_mean30": lead_to(t_mean30_first_step),
        "trigger_A_lead_to_s_network35": lead_to(s_network35_first_step),
        "trigger_A_before_collapse30": trigger_a_before_collapse30,
        "trigger_A_false_positive_no_collapse30": trigger_a_false_positive_no_collapse30,
        "trigger_B_count": len(trigger_b_steps),
        "trigger_B_first_step": first_or_blank(trigger_b_steps),
        "trigger_C_count": len(trigger_c_steps),
        "trigger_D_count": len(trigger_d_steps),
        "false_stability_steps": false_stability_steps,
        "async_false_stability_steps": async_false_stability_steps,
        "final_hub1_S": round(float(final_hub_values_padded[0]), 6) if final_hub_values_padded[0] != "" else "",
        "final_hub2_S": round(float(final_hub_values_padded[1]), 6) if final_hub_values_padded[1] != "" else "",
        "final_hub3_S": round(float(final_hub_values_padded[2]), 6) if final_hub_values_padded[2] != "" else "",
        "min_hub1_S": round(min_hub_stabilities[0], 6) if min_hub_stabilities[0] < 1.0 else "",
        "min_hub2_S": round(min_hub_stabilities[1], 6) if min_hub_stabilities[1] < 1.0 else "",
        "min_hub3_S": round(min_hub_stabilities[2], 6) if min_hub_stabilities[2] < 1.0 else "",
        "external_intervention_count": external_intervention_count,
        "resource_exhaustion_step": resource_exhaustion_step,
        "resource_floor_steps": resource_floor_steps,
        "max_unmet_recovery_demand": round(max_unmet_recovery_demand, 6),
        "max_routing_delay_loss": round(max_routing_delay_loss, 6),
        "routing_delay_steps": routing_delay_steps,
        "reclassification_latency_steps": reclassification_latency,
        "star_adjacency_persist_steps": star_adjacency_persist_steps,
        "topology_wrong_monitoring_steps": topology_wrong_monitoring_steps,
        "centralizing_wrong_monitoring_steps": centralizing_wrong_monitoring_steps,
        "star_wrong_monitoring_steps": star_wrong_monitoring_steps,
        "topology_false_stability_steps": topology_false_stability_steps,
        "max_wrong_monitoring_window": max_wrong_monitoring_window,
        "hub_degree_min": final_hub_degree_summary["hub_degree_min"],
        "hub_degree_max": final_hub_degree_summary["hub_degree_max"],
        "hub_degree_imbalance": final_hub_degree_summary["hub_degree_imbalance"],
    }
    return run_row, step_rows


def max_cluster_collapse_share(state: Dict[str, List[float] | List[str] | List[int]]) -> float:
    trust = state["T"]  # type: ignore[assignment]
    stability = state["S"]  # type: ignore[assignment]
    shares = []
    for cluster in range(CLUSTER_COUNT):
        nodes = cluster_nodes(cluster)
        shares.append(
            sum(
                1
                for node in nodes
                if trust[node] < COLLAPSE_T_THRESHOLD or stability[node] < COLLAPSE_S_THRESHOLD
            )
            / len(nodes)
        )
    return max(shares)


def summarize_runs(run_rows: Sequence[Dict[str, object]]) -> List[Dict[str, object]]:
    groups: Dict[Tuple[str, str], List[Dict[str, object]]] = {}
    for row in run_rows:
        groups.setdefault((str(row["scenario"]), str(row["profile"])), []).append(row)

    summary: List[Dict[str, object]] = []
    for (scenario_name, profile_name), rows in sorted(groups.items()):
        summary.append(
            {
                "batch_id": BATCH_ID,
                "scenario": scenario_name,
                "profile": profile_name,
                "runs": len(rows),
                "sustained_ignition_rate": round(avg(int(row["sustained_ignition"]) for row in rows), 6),
                "avg_collapse_share_peak": round(avg(float(row["collapse_share_peak"]) for row in rows), 6),
                "avg_final_T_mean": round(avg(float(row["final_T_mean"]) for row in rows), 6),
                "avg_final_S_network": round(avg(float(row["final_S_network"]) for row in rows), 6),
                "avg_final_G_effective": round(avg(float(row["final_G_effective"]) for row in rows), 6),
                "avg_trigger_A_count": round(avg(int(row["trigger_A_count"]) for row in rows), 6),
                "avg_trigger_B_count": round(avg(int(row["trigger_B_count"]) for row in rows), 6),
                "avg_trigger_C_count": round(avg(int(row["trigger_C_count"]) for row in rows), 6),
                "avg_false_stability_steps": round(avg(int(row["false_stability_steps"]) for row in rows), 6),
                "avg_async_false_stability_steps": round(avg(int(row["async_false_stability_steps"]) for row in rows), 6),
                "avg_topology_wrong_monitoring_steps": round(avg(int(row["topology_wrong_monitoring_steps"]) for row in rows), 6),
                "avg_topology_false_stability_steps": round(avg(int(row["topology_false_stability_steps"]) for row in rows), 6),
                "avg_max_wrong_monitoring_window": round(avg(int(row["max_wrong_monitoring_window"]) for row in rows), 6),
                "resource_exhaustion_rate": round(avg(1 if row["resource_exhaustion_step"] != "" else 0 for row in rows), 6),
                "avg_resource_floor_steps": round(avg(int(row["resource_floor_steps"]) for row in rows), 6),
                "avg_max_unmet_recovery_demand": round(avg(float(row["max_unmet_recovery_demand"]) for row in rows), 6),
                "avg_max_routing_delay_loss": round(avg(float(row["max_routing_delay_loss"]) for row in rows), 6),
            }
        )
    return summary


def scenario_rate(run_rows: Sequence[Dict[str, object]], scenario_name: str, field: str) -> float:
    rows = [row for row in run_rows if row["scenario"] == scenario_name]
    return avg(float(row[field]) for row in rows) if rows else 0.0


def traceability(run_rows: Sequence[Dict[str, object]]) -> List[Dict[str, object]]:
    federation_rows = [row for row in run_rows if str(row["topology_initial"]) == "federation"]
    federation_c04_violations = [
        row for row in federation_rows if str(row["trigger_A_source"]) == "C04_S_THRESHOLD"
    ]
    fed_detector_rate = avg(
        1 if int(row["trigger_A_count"]) > 0 and str(row["trigger_A_source"]) == "C07_PSI_EXTENDED" else 0
        for row in run_rows
        if row["scenario"] in ("federation_cluster_attack", "federation_bridge_stress", "psi_corruption", "async_message_loss")
    )
    federation_transfer_rows = [
        row
        for row in run_rows
        if row["scenario"] in ("federation_cluster_attack", "federation_bridge_stress", "psi_corruption", "async_message_loss")
    ]
    federation_positive_rows = [
        row for row in federation_transfer_rows if row["collapse30_event_first_step"] != ""
    ]
    federation_negative_rows = [
        row for row in federation_transfer_rows if row["collapse30_event_first_step"] == ""
    ]
    federation_detected_positive_rows = [
        row for row in federation_positive_rows if int(row["trigger_A_count"]) > 0
    ]
    federation_ontime_positive_rows = [
        row for row in federation_positive_rows if int(row["trigger_A_before_collapse30"])
    ]
    federation_false_positive_rows = [
        row for row in federation_negative_rows if int(row["trigger_A_false_positive_no_collapse30"])
    ]
    federation_leads_to_collapse30 = [
        float(row["trigger_A_lead_to_collapse30"])
        for row in federation_positive_rows
        if row["trigger_A_lead_to_collapse30"] != ""
    ]
    federation_tpr = len(federation_detected_positive_rows) / max(1, len(federation_positive_rows))
    federation_ontime_tpr = len(federation_ontime_positive_rows) / max(1, len(federation_positive_rows))
    federation_fp_rate = len(federation_false_positive_rows) / max(1, len(federation_negative_rows))
    federation_missed_rate = 1.0 - federation_tpr
    federation_avg_lead = avg(federation_leads_to_collapse30)
    star_ignition = scenario_rate(run_rows, "star_unsafe_reference", "sustained_ignition")
    hub2_ignition = scenario_rate(run_rows, "hub_2_balanced", "sustained_ignition")
    hub3_ignition = scenario_rate(run_rows, "hub_3_balanced", "sustained_ignition")
    hub2_single_ignition = scenario_rate(run_rows, "hub_2_single_hub_failure", "sustained_ignition")
    hub3_single_ignition = scenario_rate(run_rows, "hub_3_single_hub_failure", "sustained_ignition")
    hub2_unbalanced_primary_ignition = scenario_rate(run_rows, "hub_2_unbalanced_primary_failure", "sustained_ignition")
    hub3_unbalanced_primary_ignition = scenario_rate(run_rows, "hub_3_unbalanced_primary_failure", "sustained_ignition")
    hub3_unbalanced_secondary_ignition = scenario_rate(run_rows, "hub_3_unbalanced_secondary_failure", "sustained_ignition")
    deadlock_trigger_b = scenario_rate(run_rows, "trigger_b_deadlock", "trigger_B_count")
    capture_false_stability = scenario_rate(run_rows, "governance_capture", "false_stability_steps")
    async_false_stability = scenario_rate(run_rows, "async_message_loss", "async_false_stability_steps")
    topology_drift_rows = [row for row in run_rows if row["scenario_family"] == "topology_drift"]
    drift_latency_rows = [
        float(row["reclassification_latency_steps"])
        for row in run_rows
        if row["scenario_family"] == "topology_drift" and row["reclassification_latency_steps"] != ""
    ]
    topology_wrong_monitoring = avg(int(row["topology_wrong_monitoring_steps"]) for row in topology_drift_rows)
    topology_false_stability = avg(int(row["topology_false_stability_steps"]) for row in topology_drift_rows)
    max_wrong_monitoring = max((int(row["max_wrong_monitoring_window"]) for row in topology_drift_rows), default=0)
    resource_exhaustion = avg(1 if row["resource_exhaustion_step"] != "" else 0 for row in run_rows)
    resource_stress_rows = [row for row in run_rows if row["scenario_family"] == "recovery_resource"]
    resource_stress_exhaustion = avg(1 if row["resource_exhaustion_step"] != "" else 0 for row in resource_stress_rows)
    resource_stress_floor_steps = avg(int(row["resource_floor_steps"]) for row in resource_stress_rows)
    resource_routing_loss = avg(float(row["max_routing_delay_loss"]) for row in resource_stress_rows)

    return [
        {
            "claim_id": "CL01",
            "claim": "Federation C04 S-threshold Trigger A is not applicable.",
            "source": "C04 v2.3; C07 v2.2",
            "output_columns": "trigger_A_source,S_network,psi_extended",
            "metric": "federation_c04_trigger_A_violations",
            "value": len(federation_c04_violations),
            "status": "supported" if not federation_c04_violations else "failed",
        },
        {
            "claim_id": "CL02",
            "claim": "Psi_extended is the federation detector.",
            "source": "C07 v2.2",
            "output_columns": "psi_extended,psi_weight_profile,psi_w_regime,trigger_A_source,collapse30_event_first_step,trigger_A_lead_to_collapse30",
            "metric": "on_time_tpr;false_positive_rate;avg_lead_to_collapse30",
            "value": f"{round(federation_ontime_tpr, 6)};{round(federation_fp_rate, 6)};{round(federation_avg_lead, 6)}",
            "status": "supported_in_v0_6_regression"
            if federation_ontime_tpr >= 0.90 and federation_fp_rate <= 0.10 and federation_missed_rate <= 0.10
            else "transfer_failed",
        },
        {
            "claim_id": "CL03",
            "claim": "T-G loop has floor-regime break condition.",
            "source": "C02 v2.1",
            "output_columns": "break_condition_margin,trigger_B_count,G_effective",
            "metric": "avg_deadlock_trigger_B_count",
            "value": round(deadlock_trigger_b, 6),
            "status": "supported" if deadlock_trigger_b > 0 else "inconclusive",
        },
        {
            "claim_id": "CL04",
            "claim": "Star topology remains unsafe under current assumptions.",
            "source": "C00; C03/C08 v17",
            "output_columns": "sustained_ignition,collapse_share_peak",
            "metric": "star_sustained_ignition_rate",
            "value": round(star_ignition, 6),
            "status": "supported" if star_ignition >= 0.40 else "inconclusive",
        },
        {
            "claim_id": "CL05",
            "claim": "Three hubs are minimum tested mitigation, not mesh equivalence.",
            "source": "C00/C04; v18",
            "output_columns": "hub_*_balanced,hub_*_single_hub_failure,hub_*_unbalanced_*",
            "metric": "all_hub_delta;single_hub_delta;unbalanced_primary_delta;hub3_secondary_ignition",
            "value": (
                f"{round(hub2_ignition - hub3_ignition, 6)};"
                f"{round(hub2_single_ignition - hub3_single_ignition, 6)};"
                f"{round(hub2_unbalanced_primary_ignition - hub3_unbalanced_primary_ignition, 6)};"
                f"{round(hub3_unbalanced_secondary_ignition, 6)}"
            ),
            "status": "context_dependent_unbalanced_tested"
            if hub2_single_ignition > hub3_single_ignition
            else "inconclusive",
        },
        {
            "claim_id": "CL06",
            "claim": "H/I/A node classes require separate identity formulas.",
            "source": "C05 v2.1",
            "output_columns": "scenario=mixed_hia_identity,final_I_mean,collapse_share_peak",
            "metric": "mixed_hia_identity_peak_collapse",
            "value": round(scenario_rate(run_rows, "mixed_hia_identity", "collapse_share_peak"), 6),
            "status": "measured",
        },
        {
            "claim_id": "CL07",
            "claim": "Formal governance can mask ineffective governance.",
            "source": "C06; v0.3",
            "output_columns": "G_formal,G_effective,false_stability_steps,trigger_C_count",
            "metric": "avg_governance_capture_false_stability_steps",
            "value": round(capture_false_stability, 6),
            "status": "supported" if capture_false_stability > 0 else "inconclusive",
        },
        {
            "claim_id": "CL08",
            "claim": "Async/message loss can create hidden collapse.",
            "source": "C08",
            "output_columns": "message_loss,phase_divergence,detected_collapse_share,collapse_share,async_false_stability_steps",
            "metric": "avg_async_false_stability_steps",
            "value": round(async_false_stability, 6),
            "status": "supported" if async_false_stability > 0 else "not_supported_in_v0_2",
        },
        {
            "claim_id": "CL09",
            "claim": "Topology monitoring must reclassify drift.",
            "source": "C03/C08",
            "output_columns": "actual_topology,detected_topology,reclassification_latency_steps,topology_wrong_monitoring_steps,topology_false_stability_steps,max_wrong_monitoring_window",
            "metric": "avg_latency;avg_wrong_monitoring_steps;avg_topology_false_stability_steps;max_wrong_monitoring_window",
            "value": (
                f"{round(avg(drift_latency_rows), 6) if drift_latency_rows else ''};"
                f"{round(topology_wrong_monitoring, 6)};"
                f"{round(topology_false_stability, 6)};"
                f"{max_wrong_monitoring}"
            ),
            "status": "supported_in_v0_6_stress" if topology_wrong_monitoring > 0 else "inconclusive",
        },
        {
            "claim_id": "CL10",
            "claim": "Recovery claims must survive finite resources.",
            "source": "C02/C06/C08",
            "output_columns": "resource_budget,resource_exhaustion_step,resource_floor_steps,max_unmet_recovery_demand,max_routing_delay_loss",
            "metric": "resource_exhaustion_rate_all_runs;stress_exhaustion_rate;avg_stress_floor_steps;avg_routing_delay_loss",
            "value": (
                f"{round(resource_exhaustion, 6)};"
                f"{round(resource_stress_exhaustion, 6)};"
                f"{round(resource_stress_floor_steps, 6)};"
                f"{round(resource_routing_loss, 6)}"
            ),
            "status": "stress_measured_v0_6",
        },
    ]


def write_report(
    output_dir: pathlib.Path,
    run_rows: Sequence[Dict[str, object]],
    summary_rows: Sequence[Dict[str, object]],
    trace_rows: Sequence[Dict[str, object]],
) -> None:
    status_counts: Dict[str, int] = {}
    for row in trace_rows:
        status_counts[str(row["status"])] = status_counts.get(str(row["status"]), 0) + 1

    scenario_lines = []
    for row in summary_rows:
        if row["profile"] != "mid_stress":
            continue
        scenario_lines.append(
            f"| {row['scenario']} | {row['sustained_ignition_rate']} | {row['avg_collapse_share_peak']} | {row['avg_topology_wrong_monitoring_steps']} | {row['avg_resource_floor_steps']} | {row['avg_max_routing_delay_loss']} |"
        )

    trace_lines = [
        f"| {row['claim_id']} | {row['status']} | {row['metric']} | {row['value']} |"
        for row in trace_rows
    ]

    lines = [
        "# SOE Grand Simulation v0.6 Focused Stress Report",
        "",
        "## Transfer Configuration",
        "",
        f"- Federation Psi profile: `{PSI_WEIGHT_PROFILE}`.",
        f"- Federation Psi weights: `T={PSI_W_T}`, `D={PSI_W_D}`, `G={PSI_W_G}`, `S={PSI_W_S}`, `regime={PSI_W_REGIME}`.",
        f"- Federation Psi threshold: `{FEDERATION_PSI_THRESHOLD}`.",
        f"- Locked `psi_lambda`: `{PSI_LAMBDA}`.",
        "- v0.6 goal: extend the frozen v0.5 main matrix into CL09 topology lag, CL05 unbalanced hubs, and CL10 resource stress.",
        "",
        "## Batch",
        "",
        f"- Runs: `{len(run_rows)}`.",
        f"- Scenarios: `{len({row['scenario'] for row in run_rows})}`.",
        f"- Profiles: `{len({row['profile'] for row in run_rows})}`.",
        f"- Traceability statuses: `{status_counts}`.",
        "- Interpretation boundary: architecture/simulation evidence only; not deployment-ready.",
        "",
        "## Mid-Stress Scenario Snapshot",
        "",
        "| Scenario | Ignition rate | Avg peak collapse | Avg topology wrong-monitoring steps | Avg resource floor steps | Avg routing-delay loss |",
        "|---|---:|---:|---:|---:|---:|",
        *scenario_lines,
        "",
        "## Claim Traceability",
        "",
        "| Claim | Status | Metric | Value |",
        "|---|---|---|---:|",
        *trace_lines,
        "",
        "## Artifacts",
        "",
        f"- `{OUTPUT_PREFIX}_runs.csv`",
        f"- `{OUTPUT_PREFIX}_steps.csv`",
        f"- `{OUTPUT_PREFIX}_scenario_summary.csv`",
        f"- `{OUTPUT_PREFIX}_traceability.csv`",
        "",
    ]
    (output_dir / f"{OUTPUT_PREFIX}_report.md").write_text("\n".join(lines), encoding="utf-8")


def run_batch(runs_per_cell: int, steps: int, seed_start: int, output_dir: pathlib.Path) -> Tuple[List[Dict[str, object]], List[Dict[str, object]], List[Dict[str, object]], List[Dict[str, object]]]:
    run_rows: List[Dict[str, object]] = []
    step_rows: List[Dict[str, object]] = []
    scenario_list = scenarios()
    profile_list = profiles()

    global_index = 0
    for scenario in scenario_list:
        for profile in profile_list:
            for run_index in range(runs_per_cell):
                seed = seed_start + global_index
                run_row, rows = run_one(scenario, profile, run_index, seed, steps)
                run_rows.append(run_row)
                step_rows.extend(rows)
                global_index += 1

    summary_rows = summarize_runs(run_rows)
    trace_rows = traceability(run_rows)

    write_csv(output_dir / f"{OUTPUT_PREFIX}_runs.csv", run_rows)
    write_csv(output_dir / f"{OUTPUT_PREFIX}_steps.csv", step_rows)
    write_csv(output_dir / f"{OUTPUT_PREFIX}_scenario_summary.csv", summary_rows)
    write_csv(output_dir / f"{OUTPUT_PREFIX}_traceability.csv", trace_rows)
    write_report(output_dir, run_rows, summary_rows, trace_rows)
    return run_rows, step_rows, summary_rows, trace_rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SOE Grand Simulation v0.6 focused stress batch.")
    parser.add_argument("--runs-per-cell", type=int, default=DEFAULT_RUNS_PER_CELL)
    parser.add_argument("--steps", type=int, default=DEFAULT_STEPS)
    parser.add_argument("--seed-start", type=int, default=SEED_START)
    parser.add_argument("--output-dir", default=OUTPUT_PREFIX)
    parser.add_argument("--smoke", action="store_true", help="Run one seed per cell for 20 steps into a smoke output directory.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    runs_per_cell = args.runs_per_cell
    steps = args.steps
    output_dir = pathlib.Path(args.output_dir)
    if args.smoke:
        runs_per_cell = 1
        steps = 20
        output_dir = pathlib.Path(f"{OUTPUT_PREFIX}_smoke")

    run_rows, _step_rows, _summary_rows, trace_rows = run_batch(
        runs_per_cell=runs_per_cell,
        steps=steps,
        seed_start=args.seed_start,
        output_dir=output_dir,
    )
    status_counts: Dict[str, int] = {}
    for row in trace_rows:
        status_counts[str(row["status"])] = status_counts.get(str(row["status"]), 0) + 1
    print(f"Wrote {len(run_rows)} runs to {output_dir}")
    print(f"Traceability statuses: {status_counts}")


if __name__ == "__main__":
    main()
