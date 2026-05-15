from __future__ import annotations

import argparse
import csv
import math
import random
import statistics
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

from .claude_brief_suite import ParameterSet, clamp, quantile


BASELINE_PARAMS = ParameterSet(
    a=0.2887,
    b=0.1042,
    c=0.1826,
    lam=0.2770,
    alpha=0.2039,
    mu=0.2319,
)

COLLAPSE_D_THRESHOLD = 0.44
COLLAPSE_T_THRESHOLD = 0.25


@dataclass(frozen=True)
class CampaignConfig:
    seed: int = 42
    monte_carlo_runs: int = 320
    regime_runs: int = 12
    network_runs: int = 12
    adversarial_runs: int = 20
    single_steps: int = 60
    network_steps: int = 36


@dataclass
class SingleRunResult:
    run_id: int
    regime: str
    final_trust: float
    final_disturbance: float
    final_cognition: float
    min_trust: float
    max_disturbance: float
    max_cognition: float
    collapse_band_hits: int
    collapse_time: int
    survived: int
    recovered_after_shock: int
    trajectory_mean_t: float
    trajectory_var_t: float
    trajectory_mean_d: float
    trajectory_var_d: float
    trajectory_mean_c: float
    trajectory_var_c: float


@dataclass
class NetworkRunSummary:
    topology: str
    node_count: int
    regime_name: str
    k_d: float
    k_c: float
    k_t: float
    run_index: int
    systemic_collapse: int
    cascade_probability: float
    fragmented: int
    time_to_systemic_collapse: int
    healthy_cluster_ratio: float
    failed_node_share: float
    mean_final_trust: float


@dataclass
class DualFailureSupportConfig:
    name: str
    temporary_trust_boost: float
    coordination_assist: float
    staged_reentry_bonus: float


@dataclass
class HeroGateOption:
    name: str
    duration_hours: int
    fast_trigger: bool = False


def write_csv(path: Path, rows: Sequence[Dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    fieldnames: List[str] = []
    for row in rows:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def collapse_margin(params: ParameterSet, identity: float, recovery: float, disturbance: float, cognition: float) -> float:
    return (params.b * identity + recovery) - (params.a * disturbance + params.c * cognition)


def classify_single_run(
    trust_history: Sequence[float],
    disturbance_history: Sequence[float],
    cognition_history: Sequence[float],
    collapse_time: int | None,
) -> str:
    if collapse_time is not None:
        return "collapse"

    last_ten_trust = trust_history[-10:]
    last_ten_disturbance = disturbance_history[-10:]
    trust_span = max(last_ten_trust) - min(last_ten_trust)
    disturbance_span = max(last_ten_disturbance) - min(last_ten_disturbance)
    if min(last_ten_trust) >= 0.55 and max(last_ten_disturbance) < 0.35 and trust_span < 0.12 and disturbance_span < 0.10:
        return "stable"
    return "metastable"


def simulate_single_trajectory(
    params: ParameterSet,
    *,
    steps: int,
    rng: random.Random,
    base_identity: float,
    disturbance_scale: float,
    recovery_scale: float,
    alpha_scale: float,
    control_scale: float,
    initial_trust: float,
    initial_disturbance: float,
    initial_cognition: float,
    burst_pattern: str,
    recovery_noise_scale: float,
    parameter_perturbation: float,
) -> Dict[str, object]:
    a = params.a * (1.0 + rng.uniform(-parameter_perturbation, parameter_perturbation))
    b = params.b * (1.0 + rng.uniform(-parameter_perturbation, parameter_perturbation))
    c = params.c * (1.0 + rng.uniform(-parameter_perturbation, parameter_perturbation))
    lam = params.lam * control_scale * (1.0 + rng.uniform(-parameter_perturbation, parameter_perturbation))
    alpha = params.alpha * alpha_scale * (1.0 + rng.uniform(-parameter_perturbation, parameter_perturbation))
    mu = params.mu * control_scale * (1.0 + rng.uniform(-parameter_perturbation, parameter_perturbation))

    trust = initial_trust
    disturbance = initial_disturbance
    cognition = initial_cognition
    identity = base_identity
    propagation = 0.025 + (0.03 * disturbance_scale)
    shock_step = steps // 3
    collapse_time: int | None = None
    shock_recovered = False
    consecutive_collapse = 0
    collapse_band_hits = 0
    trust_history: List[float] = []
    disturbance_history: List[float] = []
    cognition_history: List[float] = []
    recovery_history: List[float] = []

    for step in range(steps):
        burst = 0.0
        if burst_pattern == "quiet":
            burst = 0.0
        elif burst_pattern == "bursty" and step in (shock_step - 1, shock_step, shock_step + 1):
            burst = 0.10 * disturbance_scale
        elif burst_pattern == "clustered" and step in range(shock_step, min(steps, shock_step + 5)):
            burst = 0.06 * disturbance_scale
        elif burst_pattern == "periodic" and step % 12 == 0:
            burst = 0.08 * disturbance_scale

        if step == shock_step:
            burst += 0.18 * disturbance_scale

        external = (0.018 + rng.uniform(0.0, 0.020)) * disturbance_scale + burst
        recovery = max(0.0, (0.020 + rng.uniform(-recovery_noise_scale, recovery_noise_scale)) * recovery_scale)
        if trust < 0.55:
            recovery += 0.038 * recovery_scale
        if trust < 0.40:
            recovery += 0.018 * recovery_scale

        disturbance = max(0.0, disturbance + external + (propagation * disturbance) - (lam * disturbance))
        cognition = max(0.0, cognition + (alpha * disturbance) - (mu * cognition) + rng.uniform(-0.01, 0.01))
        trust = clamp(trust - (a * disturbance) + (b * identity) - (c * cognition) + recovery)

        trust_history.append(trust)
        disturbance_history.append(disturbance)
        cognition_history.append(cognition)
        recovery_history.append(recovery)

        if disturbance >= COLLAPSE_D_THRESHOLD:
            collapse_band_hits += 1

        in_collapse = trust < COLLAPSE_T_THRESHOLD or (disturbance >= COLLAPSE_D_THRESHOLD and collapse_margin(params, identity, recovery, disturbance, cognition) < 0.0)
        if in_collapse:
            consecutive_collapse += 1
        else:
            consecutive_collapse = 0

        if consecutive_collapse >= 3 and collapse_time is None:
            collapse_time = step

        if step > shock_step and shock_recovered is False:
            if trust > 0.58 and disturbance < 0.34 and cognition < 0.28:
                shock_recovered = True

    regime = classify_single_run(trust_history, disturbance_history, cognition_history, collapse_time)
    return {
        "regime": regime,
        "final_trust": trust_history[-1],
        "final_disturbance": disturbance_history[-1],
        "final_cognition": cognition_history[-1],
        "min_trust": min(trust_history),
        "max_disturbance": max(disturbance_history),
        "max_cognition": max(cognition_history),
        "collapse_band_hits": collapse_band_hits,
        "collapse_time": -1 if collapse_time is None else collapse_time,
        "survived": int(collapse_time is None),
        "recovered_after_shock": int(shock_recovered and collapse_time is None),
        "trajectory_mean_t": statistics.fmean(trust_history),
        "trajectory_var_t": statistics.pvariance(trust_history),
        "trajectory_mean_d": statistics.fmean(disturbance_history),
        "trajectory_var_d": statistics.pvariance(disturbance_history),
        "trajectory_mean_c": statistics.fmean(cognition_history),
        "trajectory_var_c": statistics.pvariance(cognition_history),
        "trust_history": trust_history,
        "disturbance_history": disturbance_history,
        "cognition_history": cognition_history,
    }


def run_monte_carlo_phase(config: CampaignConfig, seed: int) -> tuple[List[Dict[str, object]], Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    collapse_times: List[int] = []
    final_trusts: List[float] = []
    final_disturbances: List[float] = []
    final_cognitions: List[float] = []
    regimes = {"stable": 0, "metastable": 0, "collapse": 0}

    for run_index in range(config.monte_carlo_runs):
        rng = random.Random(seed + run_index)
        row = simulate_single_trajectory(
            BASELINE_PARAMS,
            steps=config.single_steps,
            rng=rng,
            base_identity=clamp(0.76 + rng.uniform(-0.10, 0.08)),
            disturbance_scale=rng.uniform(0.80, 1.45),
            recovery_scale=rng.uniform(0.80, 1.25),
            alpha_scale=rng.uniform(0.85, 1.20),
            control_scale=rng.uniform(0.85, 1.20),
            initial_trust=clamp(0.74 + rng.uniform(-0.16, 0.10)),
            initial_disturbance=max(0.0, 0.16 + rng.uniform(-0.08, 0.16)),
            initial_cognition=max(0.0, 0.14 + rng.uniform(-0.08, 0.12)),
            burst_pattern=rng.choice(["quiet", "bursty", "clustered", "periodic"]),
            recovery_noise_scale=rng.uniform(0.005, 0.020),
            parameter_perturbation=rng.uniform(0.10, 0.20),
        )
        regimes[str(row["regime"])] += 1
        if int(row["collapse_time"]) >= 0:
            collapse_times.append(int(row["collapse_time"]))
        final_trusts.append(float(row["final_trust"]))
        final_disturbances.append(float(row["final_disturbance"]))
        final_cognitions.append(float(row["final_cognition"]))
        rows.append({"run_index": run_index, **{key: value for key, value in row.items() if not key.endswith("_history")}})

    summary = {
        "runs": config.monte_carlo_runs,
        "survival_rate": round((regimes["stable"] + regimes["metastable"]) / config.monte_carlo_runs, 4),
        "stable_rate": round(regimes["stable"] / config.monte_carlo_runs, 4),
        "metastable_rate": round(regimes["metastable"] / config.monte_carlo_runs, 4),
        "collapse_rate": round(regimes["collapse"] / config.monte_carlo_runs, 4),
        "collapse_time_p10": -1 if not collapse_times else round(quantile(collapse_times, 0.10), 2),
        "collapse_time_p50": -1 if not collapse_times else round(quantile(collapse_times, 0.50), 2),
        "collapse_time_p90": -1 if not collapse_times else round(quantile(collapse_times, 0.90), 2),
        "mean_final_trust": round(statistics.fmean(final_trusts), 4),
        "var_final_trust": round(statistics.pvariance(final_trusts), 4),
        "mean_final_disturbance": round(statistics.fmean(final_disturbances), 4),
        "var_final_disturbance": round(statistics.pvariance(final_disturbances), 4),
        "mean_final_cognition": round(statistics.fmean(final_cognitions), 4),
        "var_final_cognition": round(statistics.pvariance(final_cognitions), 4),
        "collapse_band_entry_rate": round(sum(int(row["collapse_band_hits"]) > 0 for row in rows) / config.monte_carlo_runs, 4),
        "recovery_success_rate_after_shock": round(sum(int(row["recovered_after_shock"]) for row in rows) / config.monte_carlo_runs, 4),
    }
    return rows, summary


def classify_regime_from_runs(rows: Sequence[Dict[str, object]]) -> str:
    collapse_rate = sum(int(row["regime"] == "collapse") for row in rows) / len(rows)
    metastable_rate = sum(int(row["regime"] == "metastable") for row in rows) / len(rows)
    if collapse_rate >= 0.50:
        return "collapse"
    if metastable_rate >= 0.35 or collapse_rate >= 0.10:
        return "metastable"
    return "stable"


def run_regime_mapping_phase(config: CampaignConfig, seed: int) -> tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    disturbance_levels = [0.80, 1.00, 1.20, 1.35, 1.50]
    recovery_levels = [0.80, 1.00, 1.15, 1.30]
    control_levels = [0.85, 1.00, 1.15]
    alpha_levels = [0.85, 1.00, 1.15, 1.30]

    grid_rows: List[Dict[str, object]] = []
    boundary_rows: List[Dict[str, object]] = []

    for disturbance_scale in disturbance_levels:
        for recovery_scale in recovery_levels:
            for control_scale in control_levels:
                for alpha_scale in alpha_levels:
                    cell_runs: List[Dict[str, object]] = []
                    for run_index in range(config.regime_runs):
                        rng = random.Random(seed + int(disturbance_scale * 1000) + int(recovery_scale * 3000) + int(alpha_scale * 5000) + int(control_scale * 7000) + run_index)
                        result = simulate_single_trajectory(
                            BASELINE_PARAMS,
                            steps=config.single_steps,
                            rng=rng,
                            base_identity=0.76,
                            disturbance_scale=disturbance_scale,
                            recovery_scale=recovery_scale,
                            alpha_scale=alpha_scale,
                            control_scale=control_scale,
                            initial_trust=0.76,
                            initial_disturbance=0.18,
                            initial_cognition=0.16,
                            burst_pattern="clustered",
                            recovery_noise_scale=0.010,
                            parameter_perturbation=0.08,
                        )
                        cell_runs.append(result)

                    regime_class = classify_regime_from_runs(cell_runs)
                    collapse_rate = sum(int(run["regime"] == "collapse") for run in cell_runs) / len(cell_runs)
                    metastable_rate = sum(int(run["regime"] == "metastable") for run in cell_runs) / len(cell_runs)
                    grid_rows.append(
                        {
                            "disturbance_scale": disturbance_scale,
                            "recovery_scale": recovery_scale,
                            "control_scale": control_scale,
                            "alpha_scale": alpha_scale,
                            "regime": regime_class,
                            "collapse_rate": round(collapse_rate, 4),
                            "metastable_rate": round(metastable_rate, 4),
                            "mean_final_trust": round(statistics.fmean(float(run["final_trust"]) for run in cell_runs), 4),
                            "mean_final_disturbance": round(statistics.fmean(float(run["final_disturbance"]) for run in cell_runs), 4),
                            "mean_final_cognition": round(statistics.fmean(float(run["final_cognition"]) for run in cell_runs), 4),
                        }
                    )

    for recovery_scale in recovery_levels:
        for control_scale in control_levels:
            for alpha_scale in alpha_levels:
                matching_rows = [
                    row for row in grid_rows
                    if row["recovery_scale"] == recovery_scale and row["control_scale"] == control_scale and row["alpha_scale"] == alpha_scale
                ]
                stable_limit = next((row["disturbance_scale"] for row in matching_rows if row["regime"] != "stable"), None)
                collapse_limit = next((row["disturbance_scale"] for row in matching_rows if row["regime"] == "collapse"), None)
                boundary_rows.append(
                    {
                        "recovery_scale": recovery_scale,
                        "control_scale": control_scale,
                        "alpha_scale": alpha_scale,
                        "stable_to_metastable_disturbance_threshold": stable_limit if stable_limit is not None else "not_reached",
                        "metastable_to_collapse_disturbance_threshold": collapse_limit if collapse_limit is not None else "not_reached",
                    }
                )
    return grid_rows, boundary_rows


def build_topology(node_count: int, topology: str, rng: random.Random) -> List[List[int]]:
    neighbors = {node_id: set() for node_id in range(node_count)}

    def add_edge(left: int, right: int) -> None:
        if left == right:
            return
        neighbors[left].add(right)
        neighbors[right].add(left)

    if topology == "fully_connected":
        for left in range(node_count):
            for right in range(left + 1, node_count):
                add_edge(left, right)
    elif topology == "random":
        for node_id in range(node_count - 1):
            add_edge(node_id, node_id + 1)
        probability = min(0.10, 8.0 / max(1.0, float(node_count)))
        for left in range(node_count):
            for right in range(left + 2, node_count):
                if rng.random() < probability:
                    add_edge(left, right)
    elif topology == "clustered":
        cluster_size = max(5, node_count // 4)
        clusters = [list(range(start, min(node_count, start + cluster_size))) for start in range(0, node_count, cluster_size)]
        for cluster in clusters:
            for left_index, left in enumerate(cluster):
                for right in cluster[left_index + 1:]:
                    add_edge(left, right)
        for cluster_index in range(len(clusters) - 1):
            add_edge(clusters[cluster_index][0], clusters[cluster_index + 1][0])
    else:
        raise ValueError(f"Unknown topology: {topology}")

    return [sorted(neighbors[node_id]) for node_id in range(node_count)]


def healthy_components(neighbors: Sequence[Sequence[int]], healthy_nodes: Iterable[int]) -> List[int]:
    healthy = set(healthy_nodes)
    visited: set[int] = set()
    sizes: List[int] = []
    for node_id in healthy:
        if node_id in visited:
            continue
        stack = [node_id]
        visited.add(node_id)
        size = 0
        while stack:
            current = stack.pop()
            size += 1
            for neighbor in neighbors[current]:
                if neighbor in healthy and neighbor not in visited:
                    visited.add(neighbor)
                    stack.append(neighbor)
        sizes.append(size)
    return sorted(sizes, reverse=True)


def run_network_scenario(
    params: ParameterSet,
    *,
    topology: str,
    node_count: int,
    k_d: float,
    k_c: float,
    k_t: float,
    steps: int,
    run_seed: int,
    adversarial_profile: str | None = None,
) -> Dict[str, object]:
    rng = random.Random(run_seed)
    neighbors = build_topology(node_count, topology, rng)
    trust = [clamp(0.76 + rng.uniform(-0.06, 0.06)) for _ in range(node_count)]
    disturbance = [max(0.0, 0.16 + rng.uniform(-0.04, 0.04)) for _ in range(node_count)]
    cognition = [max(0.0, 0.14 + rng.uniform(-0.04, 0.04)) for _ in range(node_count)]
    identity = [clamp(0.76 + rng.uniform(-0.08, 0.06)) for _ in range(node_count)]
    consecutive_failure = [0 for _ in range(node_count)]
    failed = [False for _ in range(node_count)]
    systemic_collapse_time: int | None = None
    peak_failed_share = 0.0
    peak_divergence = 0.0

    for step in range(steps):
        attack_nodes = [0]
        if adversarial_profile == "coordinated_spikes" and step in (8, 9, 10):
            attack_nodes = list(range(min(4, node_count)))
        elif adversarial_profile == "trust_targeted" and step in (10, 11, 12):
            attack_nodes = [0, 1]
        elif adversarial_profile == "timing_attack" and step in (7, 8, 9):
            attack_nodes = [0, 1, 2]
        elif adversarial_profile == "cognitive_amp" and step in (8, 9, 10, 11):
            attack_nodes = list(range(min(3, node_count)))

        next_trust: List[float] = []
        next_disturbance: List[float] = []
        next_cognition: List[float] = []
        next_identity: List[float] = []

        for node_id in range(node_count):
            local_neighbors = neighbors[node_id]
            avg_neighbor_disturbance = statistics.fmean(disturbance[neighbor] for neighbor in local_neighbors)
            avg_neighbor_cognition = statistics.fmean(cognition[neighbor] for neighbor in local_neighbors)
            avg_neighbor_trust = statistics.fmean(trust[neighbor] for neighbor in local_neighbors)
            avg_neighbor_identity = statistics.fmean(identity[neighbor] for neighbor in local_neighbors)

            external = 0.022 + rng.uniform(0.0, 0.018)
            if step == 8 and node_id == 0:
                external += 0.28
            if node_id in attack_nodes:
                if adversarial_profile == "coordinated_spikes":
                    external += 0.16
                elif adversarial_profile == "cognitive_amp":
                    external += 0.06
                elif adversarial_profile == "trust_targeted":
                    external += 0.08
                elif adversarial_profile == "timing_attack":
                    external += 0.12

            recovery = 0.02
            if trust[node_id] < 0.55:
                recovery += 0.04
            if trust[node_id] < 0.40:
                recovery += 0.02
            if adversarial_profile == "timing_attack" and step in (8, 9, 10):
                recovery *= 0.55
            recovery += k_t * max(0.0, avg_neighbor_trust - trust[node_id])

            disturbance_attack = 0.0
            cognition_attack = 0.0
            trust_attack = 0.0
            if node_id in attack_nodes:
                if adversarial_profile == "coordinated_spikes":
                    disturbance_attack += 0.12
                elif adversarial_profile == "cognitive_amp":
                    cognition_attack += 0.18
                elif adversarial_profile == "trust_targeted":
                    trust_attack += 0.12
                elif adversarial_profile == "timing_attack":
                    disturbance_attack += 0.10
                    trust_attack += 0.08

            updated_disturbance = max(
                0.0,
                disturbance[node_id]
                + external
                + (k_d * avg_neighbor_disturbance)
                - (params.lam * disturbance[node_id])
                + disturbance_attack,
            )
            updated_cognition = max(
                0.0,
                cognition[node_id]
                + (params.alpha * updated_disturbance)
                + (k_c * avg_neighbor_cognition)
                - (params.mu * cognition[node_id])
                + cognition_attack,
            )
            updated_identity = clamp(
                identity[node_id]
                + 0.015
                + (0.02 * avg_neighbor_identity)
                - (0.10 * abs(trust[node_id] - avg_neighbor_trust))
                - (0.08 * updated_disturbance)
                - (0.06 * updated_cognition),
            )
            updated_trust = clamp(
                trust[node_id]
                - (params.a * updated_disturbance)
                + (params.b * updated_identity)
                - (params.c * updated_cognition)
                + recovery
                - trust_attack,
            )

            next_trust.append(updated_trust)
            next_disturbance.append(updated_disturbance)
            next_cognition.append(updated_cognition)
            next_identity.append(updated_identity)

        trust = next_trust
        disturbance = next_disturbance
        cognition = next_cognition
        identity = next_identity

        for node_id in range(node_count):
            local_recovery = 0.02 + (0.04 if trust[node_id] < 0.55 else 0.0)
            local_margin = collapse_margin(params, identity[node_id], local_recovery, disturbance[node_id], cognition[node_id])
            node_failed = trust[node_id] < COLLAPSE_T_THRESHOLD or (disturbance[node_id] >= COLLAPSE_D_THRESHOLD and local_margin < 0.0)
            if node_failed:
                consecutive_failure[node_id] += 1
            else:
                consecutive_failure[node_id] = 0
            if consecutive_failure[node_id] >= 3:
                failed[node_id] = True

        failed_share = sum(failed) / node_count
        peak_failed_share = max(peak_failed_share, failed_share)
        divergence = statistics.pstdev(trust) + statistics.pstdev(disturbance) + statistics.pstdev(cognition)
        peak_divergence = max(peak_divergence, divergence)
        if systemic_collapse_time is None and (failed_share >= 0.30 or (statistics.fmean(trust) < 0.35 and statistics.fmean(disturbance) > 0.50)):
            systemic_collapse_time = step

    healthy_nodes = [node_id for node_id, node_failed in enumerate(failed) if not node_failed]
    components = healthy_components(neighbors, healthy_nodes)
    largest_cluster_ratio = (components[0] / max(1, len(healthy_nodes))) if healthy_nodes else 0.0
    fragmented = int(bool(healthy_nodes) and largest_cluster_ratio < 0.70)

    return {
        "systemic_collapse": int(systemic_collapse_time is not None),
        "time_to_systemic_collapse": -1 if systemic_collapse_time is None else systemic_collapse_time,
        "healthy_cluster_ratio": round(largest_cluster_ratio, 4),
        "fragmented": fragmented,
        "failed_node_share": round(sum(failed) / node_count, 4),
        "mean_final_trust": round(statistics.fmean(trust), 4),
        "peak_divergence": round(peak_divergence, 4),
        "peak_failed_share": round(peak_failed_share, 4),
        "false_stability": int(systemic_collapse_time is None and peak_failed_share >= 0.20 and statistics.fmean(trust) >= 0.55),
    }


def run_network_phase(config: CampaignConfig, seed: int) -> tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    topologies = ["fully_connected", "random", "clustered"]
    node_counts = [20, 50, 100]
    regimes = [
        ("weak", 0.04, 0.03),
        ("intermediate", 0.10, 0.08),
        ("strong", 0.16, 0.14),
    ]
    k_t_values = [0.00, 0.04, 0.08, 0.12, 0.16, 0.20]

    raw_rows: List[Dict[str, object]] = []
    summary_rows: List[Dict[str, object]] = []

    for topology in topologies:
        for node_count in node_counts:
            for regime_name, k_d, k_c in regimes:
                kt_runs: Dict[float, List[Dict[str, object]]] = {}
                for k_t in k_t_values:
                    scenario_rows = []
                    for run_index in range(config.network_runs):
                        result = run_network_scenario(
                            BASELINE_PARAMS,
                            topology=topology,
                            node_count=node_count,
                            k_d=k_d,
                            k_c=k_c,
                            k_t=k_t,
                            steps=config.network_steps,
                            run_seed=seed + node_count * 1000 + run_index * 17 + int(k_d * 1000) + int(k_t * 1000),
                        )
                        row = {
                            "topology": topology,
                            "node_count": node_count,
                            "regime_name": regime_name,
                            "k_d": k_d,
                            "k_c": k_c,
                            "k_t": k_t,
                            "run_index": run_index,
                            **result,
                        }
                        scenario_rows.append(row)
                        raw_rows.append(row)
                    kt_runs[k_t] = scenario_rows
                    summary_rows.append(
                        {
                            "topology": topology,
                            "node_count": node_count,
                            "regime_name": regime_name,
                            "k_d": k_d,
                            "k_c": k_c,
                            "k_t": k_t,
                            "cascade_probability": round(sum(int(row["systemic_collapse"]) for row in scenario_rows) / len(scenario_rows), 4),
                            "fragmentation_rate": round(sum(int(row["fragmented"]) for row in scenario_rows) / len(scenario_rows), 4),
                            "false_stability_rate": round(sum(int(row["false_stability"]) for row in scenario_rows) / len(scenario_rows), 4),
                            "avg_time_to_systemic_collapse": round(statistics.fmean(int(row["time_to_systemic_collapse"]) for row in scenario_rows if int(row["time_to_systemic_collapse"]) >= 0), 4) if any(int(row["time_to_systemic_collapse"]) >= 0 for row in scenario_rows) else -1,
                            "avg_mean_final_trust": round(statistics.fmean(float(row["mean_final_trust"]) for row in scenario_rows), 4),
                            "avg_healthy_cluster_ratio": round(statistics.fmean(float(row["healthy_cluster_ratio"]) for row in scenario_rows), 4),
                        }
                    )

                threshold = next(
                    (
                        k_t for k_t in k_t_values
                        if sum(int(row["systemic_collapse"]) for row in kt_runs[k_t]) / len(kt_runs[k_t]) <= 0.10
                    ),
                    "not_found",
                )
                summary_rows.append(
                    {
                        "topology": topology,
                        "node_count": node_count,
                        "regime_name": regime_name,
                        "k_d": k_d,
                        "k_c": k_c,
                        "k_t": "k_T_star",
                        "cascade_probability": threshold,
                        "fragmentation_rate": "",
                        "false_stability_rate": "",
                        "avg_time_to_systemic_collapse": "",
                        "avg_mean_final_trust": "",
                        "avg_healthy_cluster_ratio": "",
                    }
                )
    return raw_rows, summary_rows


def run_adversarial_phase(config: CampaignConfig, seed: int) -> tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    attack_profiles = ["coordinated_spikes", "cognitive_amp", "trust_targeted", "timing_attack"]
    topologies = ["fully_connected", "random", "clustered"]
    raw_rows: List[Dict[str, object]] = []
    summary_rows: List[Dict[str, object]] = []

    for profile in attack_profiles:
        for topology in topologies:
            scenario_rows = []
            for run_index in range(config.adversarial_runs):
                result = run_network_scenario(
                    BASELINE_PARAMS,
                    topology=topology,
                    node_count=50,
                    k_d=0.10,
                    k_c=0.08,
                    k_t=0.12,
                    steps=config.network_steps,
                    run_seed=seed + run_index * 19 + len(profile) * 100 + len(topology) * 1000,
                    adversarial_profile=profile,
                )
                row = {
                    "attack_profile": profile,
                    "topology": topology,
                    "run_index": run_index,
                    **result,
                }
                scenario_rows.append(row)
                raw_rows.append(row)

            summary_rows.append(
                {
                    "attack_profile": profile,
                    "topology": topology,
                    "systemic_collapse_rate": round(sum(int(row["systemic_collapse"]) for row in scenario_rows) / len(scenario_rows), 4),
                    "false_stability_rate": round(sum(int(row["false_stability"]) for row in scenario_rows) / len(scenario_rows), 4),
                    "recovery_success_rate": round(sum(int(row["systemic_collapse"]) == 0 for row in scenario_rows) / len(scenario_rows), 4),
                    "avg_failed_node_share": round(statistics.fmean(float(row["failed_node_share"]) for row in scenario_rows), 4),
                    "avg_healthy_cluster_ratio": round(statistics.fmean(float(row["healthy_cluster_ratio"]) for row in scenario_rows), 4),
                }
            )
    return raw_rows, summary_rows


def build_hero_sequences(seed: int) -> List[Dict[str, object]]:
    rng = random.Random(seed)
    rows: List[Dict[str, object]] = []
    for index in range(200):
        disturbance = [0.46, 0.58, 0.78, 0.88, 0.92, 0.95, 0.90, 0.84, 0.78, 0.70, 0.62, 0.56]
        trust = [0.42, 0.34, 0.24, 0.18, 0.12, 0.08, 0.06, 0.05, 0.08, 0.12, 0.18, 0.24]
        failures = [1, 2, 2, 3, 3, 3, 3, 3, 2, 2, 1, 1]
        collapse_cycle = 4
        disturbance = [value + rng.uniform(-0.02, 0.02) for value in disturbance]
        trust = [max(0.0, value + rng.uniform(-0.015, 0.015)) for value in trust]
        rows.append(
            {
                "name": f"fast_collapse_{index}",
                "class_name": "fast_collapse",
                "disturbance": disturbance,
                "trust": trust,
                "failures": failures,
                "collapse_cycle": collapse_cycle,
            }
        )
    for index in range(220):
        disturbance = [0.44, 0.56, 0.72, 0.78, 0.81, 0.80, 0.76, 0.72, 0.66, 0.58, 0.50, 0.44]
        trust = [0.46, 0.38, 0.28, 0.22, 0.18, 0.15, 0.15, 0.18, 0.22, 0.28, 0.34, 0.40]
        failures = [1, 1, 2, 2, 2, 3, 3, 3, 2, 2, 1, 1]
        rows.append(
            {
                "name": f"genuine_sustained_{index}",
                "class_name": "genuine",
                "disturbance": disturbance,
                "trust": trust,
                "failures": failures,
                "collapse_cycle": 8,
            }
        )
    for index in range(220):
        disturbance = [0.38, 0.42, 0.91, 0.54, 0.46, 0.40, 0.38, 0.36, 0.35, 0.34, 0.34, 0.34]
        trust = [0.54, 0.46, 0.22, 0.34, 0.42, 0.48, 0.52, 0.54, 0.55, 0.56, 0.56, 0.56]
        failures = [0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        rows.append(
            {
                "name": f"adversarial_spike_{index}",
                "class_name": "adversarial",
                "disturbance": disturbance,
                "trust": trust,
                "failures": failures,
                "collapse_cycle": None,
            }
        )
    return rows


def hero_gate_cycle(sequence: Dict[str, object], option: HeroGateOption) -> int | None:
    duration_cycles = max(1, math.ceil(option.duration_hours / 12))
    disturbance = sequence["disturbance"]
    trust = sequence["trust"]
    failures = sequence["failures"]
    for cycle in range(duration_cycles - 1, len(disturbance)):
        window = range(cycle - duration_cycles + 1, cycle + 1)
        disturbance_gate = all(disturbance[index] > 0.70 for index in window)
        trust_gate = all(trust[index] < 0.25 for index in window)
        failures_gate = all(failures[index] >= 2 for index in window)
        if disturbance_gate and trust_gate and failures_gate:
            return cycle
        if option.fast_trigger:
            if disturbance[cycle] > 0.88 and trust[cycle] < 0.12 and failures[cycle] >= 2:
                return cycle
    return None


def run_hero_flag_phase(seed: int) -> tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    options = [
        HeroGateOption("gate_72h", 72, False),
        HeroGateOption("gate_48h", 48, False),
        HeroGateOption("gate_24h", 24, False),
        HeroGateOption("gate_12h", 12, False),
        HeroGateOption("gate_conditional_fast", 24, True),
    ]
    raw_rows: List[Dict[str, object]] = []
    summary_rows: List[Dict[str, object]] = []

    sequences = build_hero_sequences(seed)
    for option in options:
        option_rows = []
        for sequence in sequences:
            activation_cycle = hero_gate_cycle(sequence, option)
            collapse_cycle = sequence["collapse_cycle"]
            activated = activation_cycle is not None
            false_positive = int(sequence["class_name"] == "adversarial" and activated)
            false_negative = int(sequence["class_name"] != "adversarial" and not activated)
            survives = int(sequence["class_name"] == "adversarial" or (activated and (collapse_cycle is None or activation_cycle < collapse_cycle)))
            option_rows.append(
                {
                    "gate_option": option.name,
                    "scenario": sequence["name"],
                    "class_name": sequence["class_name"],
                    "activation_cycle": -1 if activation_cycle is None else activation_cycle,
                    "collapse_cycle": -1 if collapse_cycle is None else collapse_cycle,
                    "time_to_intervention_hours": -1 if activation_cycle is None else activation_cycle * 12,
                    "time_to_collapse_hours": -1 if collapse_cycle is None else collapse_cycle * 12,
                    "false_positive": false_positive,
                    "false_negative": false_negative,
                    "survives": survives,
                }
            )
        raw_rows.extend(option_rows)
        adversarial_rows = [row for row in option_rows if row["class_name"] == "adversarial"]
        genuine_rows = [row for row in option_rows if row["class_name"] != "adversarial"]
        summary_rows.append(
            {
                "gate_option": option.name,
                "false_positive_rate": round(sum(int(row["false_positive"]) for row in adversarial_rows) / len(adversarial_rows), 4),
                "false_negative_rate": round(sum(int(row["false_negative"]) for row in genuine_rows) / len(genuine_rows), 4),
                "survival_rate_under_true_critical": round(sum(int(row["survives"]) for row in genuine_rows) / len(genuine_rows), 4),
                "avg_time_to_intervention_hours": round(statistics.fmean(int(row["time_to_intervention_hours"]) for row in genuine_rows if int(row["time_to_intervention_hours"]) >= 0), 4),
                "fast_collapse_survival_rate": round(sum(int(row["survives"]) for row in genuine_rows if row["class_name"] == "fast_collapse") / len([row for row in genuine_rows if row["class_name"] == "fast_collapse"]), 4),
            }
        )
    return raw_rows, summary_rows


def simulate_dual_failure_recovery(
    support: DualFailureSupportConfig,
    *,
    runs: int,
    seed: int,
) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for run_index in range(runs):
        rng = random.Random(seed + run_index * 29 + len(support.name) * 100)
        trust = 0.70
        disturbance = 0.24
        cognition = 0.18
        identity = 0.78
        belonging = 0.76
        collapse_step: int | None = None
        recovered_step: int | None = None

        for step in range(18):
            if step in (2, 3, 4, 5):
                identity -= 0.16 + rng.uniform(0.0, 0.03)
                belonging -= 0.18 + rng.uniform(0.0, 0.03)
                disturbance += 0.08
                cognition += 0.05

            identity = clamp(identity + 0.02 - (0.10 * disturbance) - (0.14 * max(0.0, 0.50 - belonging)))
            belonging = clamp(belonging + 0.02 - (0.12 * disturbance) - (0.12 * cognition))

            recovery = 0.02
            if trust < 0.55:
                recovery += 0.05
            recovery += support.staged_reentry_bonus * max(0.0, 1.0 - step / 18)
            if step in (6, 7, 8):
                recovery += support.coordination_assist
            if step == 6:
                trust = clamp(trust + support.temporary_trust_boost)

            disturbance = max(0.0, disturbance + 0.03 - (BASELINE_PARAMS.lam * disturbance) - (0.30 * support.coordination_assist))
            cognition = max(0.0, cognition + (BASELINE_PARAMS.alpha * disturbance) - (BASELINE_PARAMS.mu * cognition) - (0.25 * support.coordination_assist))
            trust = clamp(trust - (BASELINE_PARAMS.a * disturbance) + (BASELINE_PARAMS.b * identity) - (BASELINE_PARAMS.c * cognition) + recovery)

            if collapse_step is None and (trust < COLLAPSE_T_THRESHOLD or (disturbance >= COLLAPSE_D_THRESHOLD and collapse_margin(BASELINE_PARAMS, identity, recovery, disturbance, cognition) < 0.0)):
                collapse_step = step
            if recovered_step is None and step >= 8 and trust > 0.58 and identity > 0.50 and belonging > 0.46 and disturbance < 0.34:
                recovered_step = step

        if recovered_step is None and (trust < 0.50 or identity < 0.25 or belonging < 0.25):
            collapse_step = 17 if collapse_step is None else collapse_step

        rows.append(
            {
                "support_profile": support.name,
                "run_index": run_index,
                "collapsed": int(collapse_step is not None),
                "collapse_step": -1 if collapse_step is None else collapse_step,
                "recovered": int(recovered_step is not None),
                "recovery_step": -1 if recovered_step is None else recovered_step,
                "final_trust": round(trust, 4),
                "final_identity": round(identity, 4),
                "final_belonging": round(belonging, 4),
                "final_disturbance": round(disturbance, 4),
                "final_cognition": round(cognition, 4),
            }
        )
    return rows


def run_dual_failure_flag_phase(seed: int) -> tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    supports = [
        DualFailureSupportConfig("current_structure", 0.0, 0.0, 0.0),
        DualFailureSupportConfig("temporary_trust_boost", 0.12, 0.0, 0.0),
        DualFailureSupportConfig("coordination_assist", 0.0, 0.10, 0.0),
        DualFailureSupportConfig("staged_reentry", 0.0, 0.0, 0.08),
        DualFailureSupportConfig("combined_minimal_support", 0.08, 0.08, 0.06),
    ]
    raw_rows: List[Dict[str, object]] = []
    summary_rows: List[Dict[str, object]] = []

    for support in supports:
        scenario_rows = simulate_dual_failure_recovery(support, runs=240, seed=seed)
        raw_rows.extend(scenario_rows)
        summary_rows.append(
            {
                "support_profile": support.name,
                "recovery_probability": round(sum(int(row["recovered"]) for row in scenario_rows) / len(scenario_rows), 4),
                "collapse_probability": round(sum(int(row["collapsed"]) for row in scenario_rows) / len(scenario_rows), 4),
                "avg_time_to_irreversible_collapse": round(statistics.fmean(int(row["collapse_step"]) for row in scenario_rows if int(row["collapse_step"]) >= 0), 4) if any(int(row["collapse_step"]) >= 0 for row in scenario_rows) else -1,
                "avg_recovery_step": round(statistics.fmean(int(row["recovery_step"]) for row in scenario_rows if int(row["recovery_step"]) >= 0), 4) if any(int(row["recovery_step"]) >= 0 for row in scenario_rows) else -1,
                "avg_final_trust": round(statistics.fmean(float(row["final_trust"]) for row in scenario_rows), 4),
            }
        )

    search_candidates: List[DualFailureSupportConfig] = []
    for trust_boost in (0.0, 0.08, 0.12, 0.16):
        for coordination_assist in (0.0, 0.08, 0.12, 0.16):
            for staged_reentry in (0.0, 0.06, 0.10, 0.14):
                search_candidates.append(
                    DualFailureSupportConfig(
                        name=f"grid_tb{trust_boost:.2f}_ca{coordination_assist:.2f}_sr{staged_reentry:.2f}",
                        temporary_trust_boost=trust_boost,
                        coordination_assist=coordination_assist,
                        staged_reentry_bonus=staged_reentry,
                    )
                )

    qualifying_rows: List[Dict[str, object]] = []
    for candidate in search_candidates:
        scenario_rows = simulate_dual_failure_recovery(candidate, runs=80, seed=seed + 10_000)
        recovery_probability = sum(int(row["recovered"]) for row in scenario_rows) / len(scenario_rows)
        collapse_probability = sum(int(row["collapsed"]) for row in scenario_rows) / len(scenario_rows)
        support_cost = candidate.temporary_trust_boost + candidate.coordination_assist + candidate.staged_reentry_bonus
        if recovery_probability >= 0.50:
            qualifying_rows.append(
                {
                    "support_profile": candidate.name,
                    "temporary_trust_boost": candidate.temporary_trust_boost,
                    "coordination_assist": candidate.coordination_assist,
                    "staged_reentry_bonus": candidate.staged_reentry_bonus,
                    "recovery_probability": round(recovery_probability, 4),
                    "collapse_probability": round(collapse_probability, 4),
                    "support_cost": round(support_cost, 4),
                }
            )

    if qualifying_rows:
        qualifying_rows.sort(key=lambda row: (row["support_cost"], -row["recovery_probability"]))
        summary_rows.append({**qualifying_rows[0], "support_profile": "minimal_recovery_condition"})
    else:
        summary_rows.append(
            {
                "support_profile": "minimal_recovery_condition",
                "temporary_trust_boost": "not_found",
                "coordination_assist": "not_found",
                "staged_reentry_bonus": "not_found",
                "recovery_probability": 0.0,
                "collapse_probability": 1.0,
                "support_cost": "not_found",
            }
        )
    return raw_rows, summary_rows


def build_campaign_report(
    monte_summary: Dict[str, object],
    regime_boundaries: Sequence[Dict[str, object]],
    network_summary: Sequence[Dict[str, object]],
    adversarial_summary: Sequence[Dict[str, object]],
    hero_summary: Sequence[Dict[str, object]],
    dual_summary: Sequence[Dict[str, object]],
    output_dir: Path,
) -> str:
    hero_72 = next(row for row in hero_summary if row["gate_option"] == "gate_72h")
    hero_24 = next(row for row in hero_summary if row["gate_option"] == "gate_24h")
    hero_48 = next(row for row in hero_summary if row["gate_option"] == "gate_48h")
    hero_fast = next(row for row in hero_summary if row["gate_option"] == "gate_conditional_fast")
    dual_current = next(row for row in dual_summary if row["support_profile"] == "current_structure")
    dual_combined = next(row for row in dual_summary if row["support_profile"] == "combined_minimal_support")
    dual_minimal = next(row for row in dual_summary if row["support_profile"] == "minimal_recovery_condition")

    kt_star_rows = [row for row in network_summary if row["k_t"] == "k_T_star"]
    systematic_collapse_rows = [
        row for row in network_summary
        if row["k_t"] != "k_T_star" and isinstance(row["cascade_probability"], float) and row["cascade_probability"] >= 0.8
    ]
    metastable_boundary_count = sum(1 for row in regime_boundaries if row["stable_to_metastable_disturbance_threshold"] != "not_reached")

    flags: List[str] = []
    if float(hero_72["fast_collapse_survival_rate"]) < 0.50:
        flags.append("The current 72h Hero gate is structurally unsafe in the fast-collapse family and needs a V4.1 patch before CN translation.")
    if float(dual_current["recovery_probability"]) < 0.20:
        flags.append("Simultaneous 5.2 + 5.3 degradation is not recoverable under the current structure in this campaign and needs a V4.1 patch before CN translation.")
    if systematic_collapse_rows:
        flags.append("Some network coupling regimes collapse systematically under the locked equations; those unsafe coupling bands should be treated as validated exclusion zones.")

    lines = [
        "# SOE V4 Full Simulation Expansion Campaign",
        "",
        "## Inputs Used",
        "",
        "- `SOE_V4.docx`.",
        "- `SOE Simulation Log-Completed.docx` used as the local Version 12 reference because no separate `SOE_Simulation_Log_v12_Integrated.docx` file was found in the workspace or Desktop scan.",
        "- `Secondary_Simulation_Log_v3.docx`.",
        "- Prior v1.3 and v2.0 baseline code in the workspace.",
        "",
        "## Assumptions",
        "",
        "- Phase 3 node failure was counted when `T < 0.25` for 3 consecutive cycles, or when `D >= 0.44` for 3 consecutive cycles with negative support margin `bI + R - aD - cC < 0`.",
        "- Hero-gate comparison used `12h` measurement cycles so that `72h = 6 cycles`, `48h = 4`, `24h = 2`, and `12h = 1`.",
        "",
        "## Phase 5 First",
        "",
        f"Hero 72h gate: false positive `{hero_72['false_positive_rate']}`, false negative `{hero_72['false_negative_rate']}`, fast-collapse survival `{hero_72['fast_collapse_survival_rate']}`.",
        f"Hero 48h gate fast-collapse survival: `{hero_48['fast_collapse_survival_rate']}`.",
        f"Hero 24h gate fast-collapse survival: `{hero_24['fast_collapse_survival_rate']}`.",
        f"Conditional fast-trigger survival: `{hero_fast['fast_collapse_survival_rate']}` with false positive `{hero_fast['false_positive_rate']}`.",
        f"Dual failure current-structure recovery probability: `{dual_current['recovery_probability']}` with collapse probability `{dual_current['collapse_probability']}`.",
        f"Dual failure combined-minimal-support recovery probability: `{dual_combined['recovery_probability']}` with collapse probability `{dual_combined['collapse_probability']}`.",
        f"Minimal recovery condition from the support search: trust boost `{dual_minimal['temporary_trust_boost']}`, coordination assist `{dual_minimal['coordination_assist']}`, staged re-entry `{dual_minimal['staged_reentry_bonus']}`, recovery probability `{dual_minimal['recovery_probability']}`.",
        "",
        "## Phase 1 Monte Carlo",
        "",
        f"Survival rate `{monte_summary['survival_rate']}`, stable rate `{monte_summary['stable_rate']}`, metastable rate `{monte_summary['metastable_rate']}`, collapse rate `{monte_summary['collapse_rate']}`.",
        f"Collapse-time distribution: P10 `{monte_summary['collapse_time_p10']}`, P50 `{monte_summary['collapse_time_p50']}`, P90 `{monte_summary['collapse_time_p90']}`.",
        f"Collapse-band entry rate `{monte_summary['collapse_band_entry_rate']}`, post-shock recovery success `{monte_summary['recovery_success_rate_after_shock']}`.",
        "",
        "## Phase 2 Regime Mapping",
        "",
        f"Regime-boundary cells reaching metastable transition: `{metastable_boundary_count}`.",
        "- Boundary details are saved in the regime boundary CSV.",
        "",
        "## Phase 3 Network Stress",
        "",
        f"`k_T*` rows written for all topology / node-count / coupling-regime combinations: `{len(kt_star_rows)}`.",
        f"Systematic-collapse cells (cascade probability >= 0.8): `{len(systematic_collapse_rows)}`.",
        "",
        "## Phase 4 Adversarial Scenarios",
        "",
    ]
    for row in adversarial_summary:
        lines.append(
            f"- {row['attack_profile']} / {row['topology']}: collapse `{row['systemic_collapse_rate']}`, false stability `{row['false_stability_rate']}`, recovery `{row['recovery_success_rate']}`."
        )
    lines.extend(
        [
            "",
            "## V4.1 Flags Before CN Translation",
            "",
        ]
    )
    if flags:
        for flag in flags:
            lines.append(f"- {flag}")
    else:
        lines.append("- No additional simulation blocker crossed the V4.1 flag threshold in this campaign.")

    lines.extend(
        [
            "",
            "## Output Files",
            "",
            f"- [phase5_hero_summary.csv]({(output_dir / 'phase5_hero_summary.csv').resolve().as_posix()})",
            f"- [phase5_dual_failure_summary.csv]({(output_dir / 'phase5_dual_failure_summary.csv').resolve().as_posix()})",
            f"- [phase1_monte_carlo_summary.csv]({(output_dir / 'phase1_monte_carlo_summary.csv').resolve().as_posix()})",
            f"- [phase2_regime_boundaries.csv]({(output_dir / 'phase2_regime_boundaries.csv').resolve().as_posix()})",
            f"- [phase3_network_summary.csv]({(output_dir / 'phase3_network_summary.csv').resolve().as_posix()})",
            f"- [phase4_adversarial_summary.csv]({(output_dir / 'phase4_adversarial_summary.csv').resolve().as_posix()})",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the SOE V4 full simulation expansion campaign.")
    parser.add_argument("--seed", type=int, default=42, help="Base random seed.")
    parser.add_argument("--monte-carlo-runs", type=int, default=320, help="Number of Phase 1 stochastic runs.")
    parser.add_argument("--regime-runs", type=int, default=12, help="Runs per regime-map cell.")
    parser.add_argument("--network-runs", type=int, default=12, help="Runs per network-stress cell.")
    parser.add_argument("--adversarial-runs", type=int, default=20, help="Runs per adversarial cell.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("soe_v4") / "outputs" / "full_campaign",
        help="Output directory for campaign results.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = CampaignConfig(
        seed=args.seed,
        monte_carlo_runs=args.monte_carlo_runs,
        regime_runs=args.regime_runs,
        network_runs=args.network_runs,
        adversarial_runs=args.adversarial_runs,
    )
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    hero_rows, hero_summary = run_hero_flag_phase(args.seed)
    write_csv(output_dir / "phase5_hero_runs.csv", hero_rows)
    write_csv(output_dir / "phase5_hero_summary.csv", hero_summary)

    dual_rows, dual_summary = run_dual_failure_flag_phase(args.seed)
    write_csv(output_dir / "phase5_dual_failure_runs.csv", dual_rows)
    write_csv(output_dir / "phase5_dual_failure_summary.csv", dual_summary)

    monte_rows, monte_summary = run_monte_carlo_phase(config, args.seed)
    write_csv(output_dir / "phase1_monte_carlo_runs.csv", monte_rows)
    write_csv(output_dir / "phase1_monte_carlo_summary.csv", [monte_summary])

    regime_grid, regime_boundaries = run_regime_mapping_phase(config, args.seed)
    write_csv(output_dir / "phase2_regime_grid.csv", regime_grid)
    write_csv(output_dir / "phase2_regime_boundaries.csv", regime_boundaries)

    network_rows, network_summary = run_network_phase(config, args.seed)
    write_csv(output_dir / "phase3_network_runs.csv", network_rows)
    write_csv(output_dir / "phase3_network_summary.csv", network_summary)

    adversarial_rows, adversarial_summary = run_adversarial_phase(config, args.seed)
    write_csv(output_dir / "phase4_adversarial_runs.csv", adversarial_rows)
    write_csv(output_dir / "phase4_adversarial_summary.csv", adversarial_summary)

    report = build_campaign_report(
        monte_summary,
        regime_boundaries,
        network_summary,
        adversarial_summary,
        hero_summary,
        dual_summary,
        output_dir,
    )
    (output_dir / "campaign_report.md").write_text(report, encoding="utf-8")

    print("SOE V4 full campaign complete")
    print(f"Phase 5 hero rows: {len(hero_rows)}")
    print(f"Monte Carlo survival rate: {monte_summary['survival_rate']}")
    print(f"Saved outputs to {output_dir}")


if __name__ == "__main__":
    main()
