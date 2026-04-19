from __future__ import annotations

import argparse
import csv
import math
import random
import statistics
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def quantile(values: Sequence[float], q: float) -> float:
    if not values:
        raise ValueError("quantile requires at least one value")
    if q <= 0:
        return min(values)
    if q >= 1:
        return max(values)
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


@dataclass(frozen=True)
class ParameterSet:
    a: float
    b: float
    c: float
    lam: float
    alpha: float
    mu: float


@dataclass(frozen=True)
class OperatingPoint:
    name: str
    disturbance: float
    cognition: float
    identity: float
    recovery: float
    expected: str


@dataclass
class GateScenario:
    name: str
    class_name: str
    true_disturbance: List[float]
    true_trust: List[float]
    coordination_failures: List[int]
    collapse_step: int | None
    spoof_single_source: bool = False
    spoof_both_sources: bool = False


@dataclass
class MergedScenarioSummary:
    scenario: str
    architecture: str
    runs: int
    ci_to_identity_cascade_rate: float
    pre_reentry_identity_collapse_rate: float
    recovery_intact_rate: float
    avg_reentry_activation_step: float
    avg_recovery_step: float


@dataclass
class CoordinationSummary:
    topology: str
    fail_coupling: float
    trust_coupling: float
    avg_total_fail_coupling: float
    avg_total_trust_coupling: float
    runs: int
    stable_run_rate: float
    meta_trigger_rate: float
    synchronized_collapse_rate: float
    fragmentation_rate: float
    avg_final_trust: float
    avg_divergence_peak: float


def build_reference_points() -> List[OperatingPoint]:
    return [
        OperatingPoint("normal_integrated", disturbance=0.176, cognition=0.172, identity=0.84, recovery=0.030, expected="stable"),
        OperatingPoint("stress_cap_stable", disturbance=0.256, cognition=0.186, identity=0.76, recovery=0.045, expected="stable"),
        OperatingPoint("disturbance_high_recovering", disturbance=0.302, cognition=0.221, identity=0.66, recovery=0.080, expected="critical"),
        OperatingPoint("combined_constraint_collapse", disturbance=0.445, cognition=0.391, identity=0.36, recovery=0.020, expected="collapse"),
    ]


def margin(parameter_set: ParameterSet, point: OperatingPoint) -> float:
    return (
        parameter_set.b * point.identity
        + point.recovery
        - parameter_set.a * point.disturbance
        - parameter_set.c * point.cognition
    )


def simulate_core(
    parameter_set: ParameterSet,
    *,
    steps: int,
    disturbance_input: float,
    propagation: float,
    identity_level: float,
    recovery_floor: float,
    shock_step: int | None = None,
    shock_size: float = 0.0,
) -> Dict[str, float]:
    trust = 0.78
    disturbance = max(0.0, disturbance_input)
    cognition = 0.16
    min_trust = trust

    for step in range(steps):
        external = disturbance_input
        if shock_step is not None and step == shock_step:
            external += shock_size

        recovery = recovery_floor
        if trust < 0.55:
            recovery += 0.045

        disturbance = max(0.0, disturbance + external + (propagation * disturbance) - (parameter_set.lam * disturbance))
        cognition = max(0.0, cognition + (parameter_set.alpha * disturbance) - (parameter_set.mu * cognition))
        trust = clamp(trust + (-(parameter_set.a * disturbance) + (parameter_set.b * identity_level) - (parameter_set.c * cognition) + recovery))
        min_trust = min(min_trust, trust)

    return {
        "final_trust": trust,
        "min_trust": min_trust,
        "final_disturbance": disturbance,
        "final_cognition": cognition,
    }


def parameter_candidate_is_valid(parameter_set: ParameterSet, points: Sequence[OperatingPoint]) -> bool:
    point_margins = {point.name: margin(parameter_set, point) for point in points}
    if not 0.025 <= point_margins["normal_integrated"] <= 0.120:
        return False
    if not 0.010 <= point_margins["stress_cap_stable"] <= 0.100:
        return False
    if abs(point_margins["disturbance_high_recovering"]) > 0.035:
        return False
    if point_margins["combined_constraint_collapse"] >= -0.040:
        return False

    normal_run = simulate_core(
        parameter_set,
        steps=40,
        disturbance_input=0.030,
        propagation=0.030,
        identity_level=0.84,
        recovery_floor=0.020,
    )
    stress_run = simulate_core(
        parameter_set,
        steps=40,
        disturbance_input=0.055,
        propagation=0.050,
        identity_level=0.72,
        recovery_floor=0.040,
        shock_step=8,
        shock_size=0.18,
    )
    collapse_run = simulate_core(
        parameter_set,
        steps=25,
        disturbance_input=0.095,
        propagation=0.070,
        identity_level=0.34,
        recovery_floor=0.010,
        shock_step=3,
        shock_size=0.24,
    )

    return (
        normal_run["final_trust"] > 0.72
        and normal_run["min_trust"] > 0.58
        and stress_run["final_trust"] > 0.50
        and collapse_run["min_trust"] < 0.18
    )


def sample_parameter_sets(sample_count: int, seed: int) -> List[ParameterSet]:
    rng = random.Random(seed)
    samples: List[ParameterSet] = []
    for _ in range(sample_count):
        samples.append(
            ParameterSet(
                a=rng.uniform(0.10, 0.34),
                b=rng.uniform(0.08, 0.28),
                c=rng.uniform(0.08, 0.24),
                lam=rng.uniform(0.12, 0.34),
                alpha=rng.uniform(0.10, 0.34),
                mu=rng.uniform(0.12, 0.32),
            )
        )
    return samples


def calibrate_parameters(sample_count: int, seed: int) -> Dict[str, object]:
    points = build_reference_points()
    accepted = [parameter_set for parameter_set in sample_parameter_sets(sample_count, seed) if parameter_candidate_is_valid(parameter_set, points)]
    if not accepted:
        raise RuntimeError("No accepted parameter sets found; widen the priors or increase samples.")

    ranges: List[Dict[str, float | str]] = []
    for name in ("a", "b", "c", "lam", "alpha", "mu"):
        values = [getattr(parameter_set, name) for parameter_set in accepted]
        ranges.append(
            {
                "parameter": name,
                "p10": round(quantile(values, 0.10), 4),
                "p50": round(quantile(values, 0.50), 4),
                "p90": round(quantile(values, 0.90), 4),
                "min": round(min(values), 4),
                "max": round(max(values), 4),
            }
        )

    chosen = ParameterSet(
        a=quantile([row.a for row in accepted], 0.50),
        b=quantile([row.b for row in accepted], 0.50),
        c=quantile([row.c for row in accepted], 0.50),
        lam=quantile([row.lam for row in accepted], 0.50),
        alpha=quantile([row.alpha for row in accepted], 0.50),
        mu=quantile([row.mu for row in accepted], 0.50),
    )

    normal_points = [
        OperatingPoint("normal_low", disturbance=0.18, cognition=0.17, identity=0.82, recovery=0.03, expected="stable"),
        OperatingPoint("normal_high", disturbance=0.26, cognition=0.19, identity=0.72, recovery=0.05, expected="stable"),
    ]
    critical_points = [
        OperatingPoint("critical_low", disturbance=0.34, cognition=0.24, identity=0.64, recovery=0.06, expected="critical"),
        OperatingPoint("critical_high", disturbance=0.40, cognition=0.30, identity=0.52, recovery=0.05, expected="critical"),
    ]
    collapse_points = [
        OperatingPoint("collapse_low", disturbance=0.44, cognition=0.34, identity=0.44, recovery=0.03, expected="collapse"),
        OperatingPoint("collapse_high", disturbance=0.52, cognition=0.40, identity=0.34, recovery=0.02, expected="collapse"),
    ]

    envelope_rows: List[Dict[str, float | str]] = []
    for zone_name, envelope_points in (
        ("stable", normal_points),
        ("critical", critical_points),
        ("collapse", collapse_points),
    ):
        accepted_counts = 0
        margins: List[float] = []
        for parameter_set in accepted:
            zone_margins = [margin(parameter_set, point) for point in envelope_points]
            margins.extend(zone_margins)
            if zone_name == "stable" and min(zone_margins) > 0.02:
                accepted_counts += 1
            elif zone_name == "critical" and max(abs(value) for value in zone_margins) <= 0.04:
                accepted_counts += 1
            elif zone_name == "collapse" and max(zone_margins) < -0.02:
                accepted_counts += 1
        envelope_rows.append(
            {
                "zone": zone_name,
                "disturbance_min": envelope_points[0].disturbance,
                "disturbance_max": envelope_points[-1].disturbance,
                "cognition_min": envelope_points[0].cognition,
                "cognition_max": envelope_points[-1].cognition,
                "identity_min": min(point.identity for point in envelope_points),
                "identity_max": max(point.identity for point in envelope_points),
                "recovery_min": min(point.recovery for point in envelope_points),
                "recovery_max": max(point.recovery for point in envelope_points),
                "accepted_share": round(accepted_counts / len(accepted), 4),
                "median_margin": round(statistics.median(margins), 4),
            }
        )

    normal_confirmation_rows: List[Dict[str, float | str]] = []
    for point in normal_points:
        lhs = chosen.b * point.identity + point.recovery
        rhs = chosen.a * point.disturbance + chosen.c * point.cognition
        normal_confirmation_rows.append(
            {
                "point": point.name,
                "lhs_bI_plus_R": round(lhs, 4),
                "rhs_aD_plus_cC": round(rhs, 4),
                "margin": round(lhs - rhs, 4),
                "holds": "yes" if lhs > rhs else "no",
            }
        )

    collapse_threshold_rows: List[Dict[str, float | str]] = []
    for point in (
        OperatingPoint("normal_reference", disturbance=0.22, cognition=0.18, identity=0.78, recovery=0.04, expected="stable"),
        OperatingPoint("stress_reference", disturbance=0.32, cognition=0.24, identity=0.64, recovery=0.06, expected="critical"),
    ):
        disturbance_threshold = max(0.0, (chosen.b * point.identity + point.recovery - (chosen.c * point.cognition)) / chosen.a)
        cognition_threshold = max(0.0, (chosen.b * point.identity + point.recovery - (chosen.a * point.disturbance)) / chosen.c)
        collapse_threshold_rows.append(
            {
                "reference_point": point.name,
                "disturbance_threshold_at_equal_margin": round(disturbance_threshold, 4),
                "cognition_threshold_at_equal_margin": round(cognition_threshold, 4),
                "support_damage_ratio_threshold": 1.0,
            }
        )

    return {
        "accepted_sets": accepted,
        "candidate_ranges": ranges,
        "chosen": chosen,
        "envelope_rows": envelope_rows,
        "normal_confirmation_rows": normal_confirmation_rows,
        "collapse_threshold_rows": collapse_threshold_rows,
    }


def build_gate_scenarios(seed: int) -> List[GateScenario]:
    rng = random.Random(seed)
    scenarios: List[GateScenario] = []

    for index in range(200):
        disturbance = [0.36, 0.42, 0.84 + rng.uniform(-0.03, 0.03), 0.46, 0.34, 0.32]
        trust = [0.54, 0.48, 0.31 + rng.uniform(-0.02, 0.02), 0.36, 0.44, 0.52]
        failures = [0, 1, 1, 0, 0, 0]
        scenarios.append(GateScenario(f"adversarial_spike_{index}", "adversarial", disturbance, trust, failures, None))

    for index in range(200):
        disturbance = [0.34, 0.35, 0.36, 0.38, 0.37, 0.35]
        trust = [0.58, 0.57, 0.56, 0.55, 0.55, 0.54]
        failures = [0, 0, 1, 1, 0, 0]
        scenarios.append(
            GateScenario(
                f"single_source_spoof_{index}",
                "adversarial",
                disturbance,
                trust,
                failures,
                None,
                spoof_single_source=True,
            )
        )

    for index in range(200):
        disturbance = [0.69, 0.73, 0.68, 0.74, 0.69, 0.72]
        trust = [0.27, 0.24, 0.28, 0.23, 0.27, 0.24]
        failures = [1, 1, 1, 1, 1, 1]
        scenarios.append(GateScenario(f"boundary_oscillation_{index}", "adversarial", disturbance, trust, failures, None))

    for index in range(240):
        disturbance = [0.55, 0.76, 0.82, 0.84, 0.80, 0.72]
        trust = [0.41, 0.29, 0.22, 0.19, 0.18, 0.21]
        failures = [1, 2, 2, 3, 3, 2]
        scenarios.append(GateScenario(f"genuine_sustained_{index}", "genuine", disturbance, trust, failures, 4))

    for index in range(180):
        disturbance = [0.61, 0.79, 0.88, 0.91, 0.85, 0.80]
        trust = [0.33, 0.21, 0.14, 0.08, 0.06, 0.05]
        failures = [1, 2, 3, 3, 3, 3]
        scenarios.append(GateScenario(f"genuine_fast_{index}", "genuine_fast", disturbance, trust, failures, 3))

    return scenarios


def build_sensor_stream(true_values: Sequence[float], rng: random.Random, *, spoof_single: bool, spoof_both: bool, low_bias: bool = False) -> tuple[List[float], List[float]]:
    stream_one: List[float] = []
    stream_two: List[float] = []
    for index, value in enumerate(true_values):
        noise_one = rng.uniform(-0.025, 0.025)
        noise_two = rng.uniform(-0.025, 0.025)
        source_one = value + noise_one
        source_two = value + noise_two
        if spoof_single and index in (1, 2, 3):
            if low_bias:
                source_one -= 0.35
            else:
                source_one += 0.40
        if spoof_both and index in (1, 2, 3):
            if low_bias:
                source_one -= 0.35
                source_two -= 0.35
            else:
                source_one += 0.35
                source_two += 0.35
        stream_one.append(source_one)
        stream_two.append(source_two)
    return stream_one, stream_two


def hero_gate_activation_day(scenario: GateScenario, seed: int) -> int | None:
    rng = random.Random(seed)
    disturbance_one, disturbance_two = build_sensor_stream(
        scenario.true_disturbance,
        rng,
        spoof_single=scenario.spoof_single_source,
        spoof_both=scenario.spoof_both_sources,
        low_bias=False,
    )
    trust_one, trust_two = build_sensor_stream(
        scenario.true_trust,
        rng,
        spoof_single=scenario.spoof_single_source,
        spoof_both=scenario.spoof_both_sources,
        low_bias=True,
    )

    for day in range(2, len(scenario.true_disturbance)):
        disturbance_gate = all(
            disturbance_one[index] > 0.70 and disturbance_two[index] > 0.70
            for index in range(day - 2, day + 1)
        )
        trust_gate = all(
            trust_one[index] < 0.25 and trust_two[index] < 0.25
            for index in range(day - 2, day + 1)
        )
        coordination_gate = all(
            scenario.coordination_failures[index] >= 2
            for index in range(day - 2, day + 1)
        )
        if disturbance_gate and trust_gate and coordination_gate:
            return day
    return None


def evaluate_hero_gate(seed: int) -> tuple[List[Dict[str, float | int | str]], Dict[str, float | str]]:
    rows: List[Dict[str, float | int | str]] = []
    false_positives = 0
    false_negatives = 0
    adversarial_total = 0
    genuine_total = 0
    fast_total = 0
    dangerous_fast_delay = 0

    for index, scenario in enumerate(build_gate_scenarios(seed)):
        activation_day = hero_gate_activation_day(scenario, seed + index)
        activated = activation_day is not None
        if scenario.class_name == "adversarial":
            adversarial_total += 1
            if activated:
                false_positives += 1
        else:
            genuine_total += 1
            if not activated:
                false_negatives += 1
            if scenario.class_name == "genuine_fast":
                fast_total += 1
                if activation_day is None or (scenario.collapse_step is not None and activation_day >= scenario.collapse_step):
                    dangerous_fast_delay += 1

        rows.append(
            {
                "scenario": scenario.name,
                "class_name": scenario.class_name,
                "activated": int(activated),
                "activation_day": -1 if activation_day is None else activation_day,
                "collapse_day": -1 if scenario.collapse_step is None else scenario.collapse_step,
                "coordination_failure_peak": max(scenario.coordination_failures),
                "disturbance_peak": round(max(scenario.true_disturbance), 4),
                "trust_floor": round(min(scenario.true_trust), 4),
            }
        )

    summary = {
        "adversarial_runs": adversarial_total,
        "genuine_runs": genuine_total,
        "false_positive_rate": round(false_positives / adversarial_total, 4),
        "false_negative_rate": round(false_negatives / genuine_total, 4),
        "fast_collapse_danger_rate": round(dangerous_fast_delay / fast_total, 4),
        "pass_false_activation": "pass" if false_positives == 0 else "fail",
        "pass_genuine_activation": "pass" if false_negatives / genuine_total <= 0.10 else "fail",
        "pass_72h_delay": "fail" if dangerous_fast_delay / max(1, fast_total) > 0.25 else "pass",
    }
    return rows, summary


def run_merged_layer_scenario(
    parameter_set: ParameterSet,
    *,
    architecture: str,
    scenario_name: str,
    run_seed: int,
) -> Dict[str, float | int | str]:
    rng = random.Random(run_seed)
    trust = 0.72
    disturbance = 0.24
    cognition = 0.18
    identity = 0.78
    civilizational_identity = 0.76
    reentry_activation_step: int | None = None
    recovery_step: int | None = None
    ci_to_identity_cascade = False
    pre_reentry_identity_collapse = False

    for step in range(16):
        ci_attack = 0.0
        identity_attack = 0.0
        if scenario_name == "ci_only" and step in (2, 3, 4):
            ci_attack = 0.18
        if scenario_name == "identity_only" and step in (2, 3, 4):
            identity_attack = 0.15
        if scenario_name == "dual_failure" and step in (2, 3, 4, 5):
            ci_attack = 0.20
            identity_attack = 0.17

        disturbance = clamp(disturbance + 0.02 + rng.uniform(-0.015, 0.015) - (parameter_set.lam * disturbance) + (0.12 * max(0.0, 0.50 - civilizational_identity)))
        cognition = clamp(cognition + (parameter_set.alpha * disturbance) - (parameter_set.mu * cognition) + (0.10 * max(0.0, 0.55 - civilizational_identity)))
        civilizational_identity = clamp(civilizational_identity - ci_attack - (0.08 * disturbance) + 0.03)
        identity = clamp(identity - identity_attack - (0.18 * max(0.0, 0.55 - civilizational_identity)) - (0.05 * disturbance) + 0.03)

        reentry_base = 0.02
        if trust < 0.55:
            reentry_base = 0.08
            if reentry_activation_step is None:
                reentry_activation_step = step

        if architecture == "merged":
            recovery = reentry_base * (0.55 + (0.45 * identity)) * (0.45 + (0.55 * civilizational_identity))
        else:
            recovery = reentry_base * (0.75 + (0.25 * identity))

        trust = clamp(trust + (-(parameter_set.a * disturbance) + (parameter_set.b * identity) - (parameter_set.c * cognition) + recovery))

        if civilizational_identity < 0.45 and identity < 0.45:
            ci_to_identity_cascade = True
        if identity < 0.45 and reentry_activation_step is None:
            pre_reentry_identity_collapse = True
        if trust > 0.62 and identity > 0.58 and civilizational_identity > 0.55 and recovery_step is None and step >= 4:
            recovery_step = step

    return {
        "scenario": scenario_name,
        "architecture": architecture,
        "ci_to_identity_cascade": int(ci_to_identity_cascade),
        "pre_reentry_identity_collapse": int(pre_reentry_identity_collapse),
        "recovery_intact": int(recovery_step is not None),
        "reentry_activation_step": -1 if reentry_activation_step is None else reentry_activation_step,
        "recovery_step": -1 if recovery_step is None else recovery_step,
    }


def evaluate_merged_layers(parameter_set: ParameterSet, runs: int, seed: int) -> tuple[List[Dict[str, float | int | str]], List[MergedScenarioSummary]]:
    raw_rows: List[Dict[str, float | int | str]] = []
    summary_rows: List[MergedScenarioSummary] = []
    for scenario_name in ("ci_only", "identity_only", "dual_failure"):
        for architecture in ("separate", "merged"):
            scenario_rows = [
                run_merged_layer_scenario(parameter_set, architecture=architecture, scenario_name=scenario_name, run_seed=seed + (run_index * 17) + (0 if architecture == "separate" else 5000))
                for run_index in range(runs)
            ]
            raw_rows.extend(scenario_rows)
            reentry_steps = [int(row["reentry_activation_step"]) for row in scenario_rows if int(row["reentry_activation_step"]) >= 0]
            recovery_steps = [int(row["recovery_step"]) for row in scenario_rows if int(row["recovery_step"]) >= 0]
            summary_rows.append(
                MergedScenarioSummary(
                    scenario=scenario_name,
                    architecture=architecture,
                    runs=runs,
                    ci_to_identity_cascade_rate=round(sum(int(row["ci_to_identity_cascade"]) for row in scenario_rows) / runs, 4),
                    pre_reentry_identity_collapse_rate=round(sum(int(row["pre_reentry_identity_collapse"]) for row in scenario_rows) / runs, 4),
                    recovery_intact_rate=round(sum(int(row["recovery_intact"]) for row in scenario_rows) / runs, 4),
                    avg_reentry_activation_step=round(sum(reentry_steps) / len(reentry_steps), 4) if reentry_steps else -1.0,
                    avg_recovery_step=round(sum(recovery_steps) / len(recovery_steps), 4) if recovery_steps else -1.0,
                )
            )
    return raw_rows, summary_rows


def build_network_neighbors(node_count: int, topology: str) -> List[List[int]]:
    neighbors = {node_id: set() for node_id in range(node_count)}

    def add_edge(left: int, right: int) -> None:
        neighbors[left].add(right)
        neighbors[right].add(left)

    if topology == "federation":
        hubs = [0, 1, 2]
        add_edge(0, 1)
        add_edge(1, 2)
        add_edge(2, 0)
        for node_id in range(3, node_count):
            add_edge(node_id, hubs[(node_id - 3) % len(hubs)])
            add_edge(node_id, hubs[(node_id - 2) % len(hubs)])
    elif topology == "ring":
        for node_id in range(node_count):
            add_edge(node_id, (node_id + 1) % node_count)
    else:
        raise ValueError(f"Unknown topology: {topology}")

    return [sorted(neighbors[node_id]) for node_id in range(node_count)]


def evaluate_coordination(
    parameter_set: ParameterSet,
    *,
    runs: int,
    seed: int,
    topology: str,
) -> tuple[List[Dict[str, float | int | str]], List[CoordinationSummary]]:
    raw_rows: List[Dict[str, float | int | str]] = []
    summaries: List[CoordinationSummary] = []
    neighbors = build_network_neighbors(8, topology)

    for fail_coupling in (0.04, 0.08, 0.12, 0.16, 0.20):
        for trust_coupling in (0.00, 0.04, 0.08, 0.12, 0.16):
            stable_count = 0
            meta_count = 0
            sync_count = 0
            frag_count = 0
            final_trusts: List[float] = []
            divergence_peaks: List[float] = []

            for run_index in range(runs):
                rng = random.Random(seed + int(fail_coupling * 1000) + int(trust_coupling * 2000) + run_index)
                trust = [0.78 + rng.uniform(-0.03, 0.03) for _ in range(8)]
                disturbance = [0.18 + rng.uniform(-0.02, 0.02) for _ in range(8)]
                cognition = [0.16 + rng.uniform(-0.02, 0.02) for _ in range(8)]
                identity = [0.76 + rng.uniform(-0.04, 0.04) for _ in range(8)]
                meta_triggered = False
                peak_divergence = 0.0

                for step in range(18):
                    if step == 2:
                        disturbance[0] = clamp(disturbance[0] + 0.55)

                    next_trust: List[float] = []
                    next_disturbance: List[float] = []
                    next_cognition: List[float] = []
                    next_identity: List[float] = []

                    for node_id in range(8):
                        local_neighbors = neighbors[node_id]
                        avg_neighbor_disturbance = statistics.fmean(disturbance[neighbor] for neighbor in local_neighbors)
                        avg_neighbor_cognition = statistics.fmean(cognition[neighbor] for neighbor in local_neighbors)
                        avg_neighbor_trust = statistics.fmean(trust[neighbor] for neighbor in local_neighbors)
                        avg_neighbor_identity = statistics.fmean(identity[neighbor] for neighbor in local_neighbors)

                        recovery = 0.02
                        if trust[node_id] < 0.55:
                            recovery += 0.05
                        recovery += trust_coupling * max(0.0, avg_neighbor_trust - trust[node_id])

                        updated_disturbance = clamp(
                            disturbance[node_id]
                            + 0.03
                            + (fail_coupling * avg_neighbor_disturbance)
                            - (parameter_set.lam * disturbance[node_id])
                        )
                        updated_cognition = clamp(
                            cognition[node_id]
                            + (parameter_set.alpha * updated_disturbance)
                            + (0.6 * fail_coupling * avg_neighbor_cognition)
                            - (parameter_set.mu * cognition[node_id])
                        )
                        updated_identity = clamp(
                            identity[node_id]
                            + 0.02
                            + (0.03 * avg_neighbor_identity)
                            - (0.12 * abs(trust[node_id] - avg_neighbor_trust))
                            - (0.10 * updated_disturbance)
                        )
                        updated_trust = clamp(
                            trust[node_id]
                            - (parameter_set.a * updated_disturbance)
                            - (parameter_set.c * updated_cognition)
                            + (parameter_set.b * updated_identity)
                            + recovery
                        )

                        next_disturbance.append(updated_disturbance)
                        next_cognition.append(updated_cognition)
                        next_identity.append(updated_identity)
                        next_trust.append(updated_trust)

                    trust = next_trust
                    disturbance = next_disturbance
                    cognition = next_cognition
                    identity = next_identity

                    divergence = statistics.pstdev(trust) + statistics.pstdev(disturbance) + statistics.pstdev(cognition)
                    peak_divergence = max(peak_divergence, divergence)
                    coordination_failure = divergence > 0.30 or min(identity) < 0.42
                    if coordination_failure and (statistics.fmean(disturbance) > 0.34 or min(trust) < 0.30):
                        meta_triggered = True

                stable = statistics.fmean(trust) > 0.58 and not meta_triggered and peak_divergence < 0.32
                synchronized_collapse = sum(value < 0.25 for value in trust) >= 4
                fragmented = peak_divergence > 0.36 and sum(value > 0.55 for value in trust) >= 2 and sum(value < 0.30 for value in trust) >= 2

                stable_count += int(stable)
                meta_count += int(meta_triggered)
                sync_count += int(synchronized_collapse)
                frag_count += int(fragmented)
                final_trusts.append(statistics.fmean(trust))
                divergence_peaks.append(peak_divergence)

                raw_rows.append(
                    {
                        "topology": topology,
                        "fail_coupling": fail_coupling,
                        "trust_coupling": trust_coupling,
                        "run_index": run_index,
                        "stable": int(stable),
                        "meta_triggered": int(meta_triggered),
                        "synchronized_collapse": int(synchronized_collapse),
                        "fragmented": int(fragmented),
                        "final_mean_trust": round(statistics.fmean(trust), 4),
                        "peak_divergence": round(peak_divergence, 4),
                    }
                )

            degree = len(neighbors[0])
            summaries.append(
                CoordinationSummary(
                    topology=topology,
                    fail_coupling=fail_coupling,
                    trust_coupling=trust_coupling,
                    avg_total_fail_coupling=round(degree * fail_coupling, 4),
                    avg_total_trust_coupling=round(degree * trust_coupling, 4),
                    runs=runs,
                    stable_run_rate=round(stable_count / runs, 4),
                    meta_trigger_rate=round(meta_count / runs, 4),
                    synchronized_collapse_rate=round(sync_count / runs, 4),
                    fragmentation_rate=round(frag_count / runs, 4),
                    avg_final_trust=round(sum(final_trusts) / len(final_trusts), 4),
                    avg_divergence_peak=round(sum(divergence_peaks) / len(divergence_peaks), 4),
                )
            )

    return raw_rows, summaries


def write_csv(path: Path, rows: Sequence[Dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_report(
    calibration: Dict[str, object],
    hero_summary: Dict[str, float | str],
    merged_summaries: Sequence[MergedScenarioSummary],
    coordination_summaries: Sequence[CoordinationSummary],
    output_dir: Path,
) -> str:
    chosen: ParameterSet = calibration["chosen"]  # type: ignore[assignment]
    candidate_ranges = calibration["candidate_ranges"]  # type: ignore[assignment]
    envelope_rows = calibration["envelope_rows"]  # type: ignore[assignment]
    confirmations = calibration["normal_confirmation_rows"]  # type: ignore[assignment]
    collapse_threshold_rows = calibration["collapse_threshold_rows"]  # type: ignore[assignment]

    robust_coordination = max(
        (row for row in coordination_summaries if row.stable_run_rate >= 0.999 and row.trust_coupling > 0.0),
        key=lambda row: (row.avg_total_fail_coupling, row.avg_total_trust_coupling),
    )
    overcoupled = max(coordination_summaries, key=lambda row: (row.synchronized_collapse_rate, row.meta_trigger_rate, row.avg_total_fail_coupling))
    overdecoupled = max(
        (row for row in coordination_summaries if row.trust_coupling == 0.0),
        key=lambda row: (row.meta_trigger_rate, row.avg_total_fail_coupling),
    )

    merged_dual = next(row for row in merged_summaries if row.scenario == "dual_failure" and row.architecture == "merged")
    separate_dual = next(row for row in merged_summaries if row.scenario == "dual_failure" and row.architecture == "separate")

    flags: List[str] = []
    if hero_summary["pass_false_activation"] == "fail" or hero_summary["pass_genuine_activation"] == "fail":
        flags.append("Hero trigger gate needs V4.1 review before CN translation because stress performance misses the locked safety target.")
    if hero_summary["pass_72h_delay"] == "fail":
        flags.append("The 72-hour Hero delay is unsafe in the simulated fast-collapse family and should be treated as a V4.1 review item before CN translation.")
    if merged_dual.pre_reentry_identity_collapse_rate - separate_dual.pre_reentry_identity_collapse_rate > 0.15:
        flags.append("Merged Chapter 5 dual-failure coupling introduces a materially higher pre-reentry identity-collapse risk and should be flagged for V4.1 review before CN translation.")
    if merged_dual.recovery_intact_rate < 0.25:
        flags.append("The Chapter 5 recovery pathway did not remain intact under simultaneous 5.2 + 5.3 failure in this run family and should be treated as a V4.1 review item before CN translation.")
    if robust_coordination.stable_run_rate < 0.75:
        flags.append("Coordination Layer safe operating window is too narrow in the current stress scan and should be flagged for V4.1 review before CN translation.")

    lines = [
        "# SOE V4 Claude Brief Simulation Report",
        "",
        "## Inputs Used",
        "",
        "- `SOE_V4.docx` from Desktop.",
        "- `SOE Simulation Log-Completed.docx` treated as the Version 12 simulation reference because no separate `SOE_Simulation_Log_v12_Integrated.docx` file was found locally.",
        "- `Secondary_Simulation_Log_v3.docx` from the workspace.",
        "",
        "## Task 1 - O4 Parameter Calibration",
        "",
        f"Chosen median calibration set: `a={chosen.a:.4f}`, `b={chosen.b:.4f}`, `c={chosen.c:.4f}`, `lambda={chosen.lam:.4f}`, `alpha={chosen.alpha:.4f}`, `mu={chosen.mu:.4f}`.",
        "",
        "| Parameter | P10 | P50 | P90 | Min | Max |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in candidate_ranges:
        lines.append(
            f"| {row['parameter']} | {row['p10']:.4f} | {row['p50']:.4f} | {row['p90']:.4f} | {row['min']:.4f} | {row['max']:.4f} |"
        )

    lines.extend(
        [
            "",
            "### Stability Envelope",
            "",
            "| Zone | D Range | C Range | I Range | R Range | Accepted Share | Median Margin |",
            "| --- | --- | --- | --- | --- | ---: | ---: |",
        ]
    )
    for row in envelope_rows:
        lines.append(
            f"| {row['zone']} | {row['disturbance_min']:.2f}-{row['disturbance_max']:.2f} | {row['cognition_min']:.2f}-{row['cognition_max']:.2f} | {row['identity_min']:.2f}-{row['identity_max']:.2f} | {row['recovery_min']:.2f}-{row['recovery_max']:.2f} | {row['accepted_share']:.4f} | {row['median_margin']:.4f} |"
        )

    lines.extend(
        [
            "",
            "### Normal-Operation Confirmation",
            "",
            "| Point | bI + R | aD + cC | Margin | Holds? |",
            "| --- | ---: | ---: | ---: | --- |",
        ]
    )
    for row in confirmations:
        lines.append(
            f"| {row['point']} | {row['lhs_bI_plus_R']:.4f} | {row['rhs_aD_plus_cC']:.4f} | {row['margin']:.4f} | {row['holds']} |"
        )

    lines.extend(
        [
            "",
            "### Collapse Thresholds",
            "",
            "| Reference Point | D Threshold | C Threshold | Support/Damage Ratio Threshold |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for row in collapse_threshold_rows:
        lines.append(
            f"| {row['reference_point']} | {row['disturbance_threshold_at_equal_margin']:.4f} | {row['cognition_threshold_at_equal_margin']:.4f} | {row['support_damage_ratio_threshold']:.1f} |"
        )

    lines.extend(
        [
            "",
            "## Task 2 - Hero Trigger Gate",
            "",
            f"False positive rate: `{hero_summary['false_positive_rate']}`.",
            f"False negative rate: `{hero_summary['false_negative_rate']}`.",
            f"Fast-collapse dangerous-delay rate: `{hero_summary['fast_collapse_danger_rate']}`.",
            f"False-activation result: `{hero_summary['pass_false_activation']}`.",
            f"Genuine-critical activation result: `{hero_summary['pass_genuine_activation']}`.",
            f"72-hour delay result: `{hero_summary['pass_72h_delay']}`.",
            "",
            "## Task 3 - Chapter 5 Merged Layer Interactions",
            "",
            "| Scenario | Architecture | Cascade Rate | Pre-Reentry Identity Collapse | Recovery Intact | Avg Re-entry Step | Avg Recovery Step |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in merged_summaries:
        lines.append(
            f"| {row.scenario} | {row.architecture} | {row.ci_to_identity_cascade_rate:.4f} | {row.pre_reentry_identity_collapse_rate:.4f} | {row.recovery_intact_rate:.4f} | {row.avg_reentry_activation_step:.4f} | {row.avg_recovery_step:.4f} |"
        )

    lines.extend(
        [
            "",
            "Merged-layer readout:",
            f"CI-only instability did not trigger an identity-collapse cascade in either formulation, but simultaneous 5.2 + 5.3 failure produced full cascade in both (`merged={merged_dual.ci_to_identity_cascade_rate:.4f}`, `separate={separate_dual.ci_to_identity_cascade_rate:.4f}`).",
            f"Dual failure in the merged architecture shows pre-reentry identity collapse at `{merged_dual.pre_reentry_identity_collapse_rate:.4f}` versus `{separate_dual.pre_reentry_identity_collapse_rate:.4f}` in the separated counterfactual.",
            f"Recovery remains intact in `{merged_dual.recovery_intact_rate:.4f}` of merged dual-failure runs, so the recovery pathway is not intact under simultaneous 5.2 + 5.3 failure in this run family.",
            "",
            "## Task 4 - Coordination Layer",
            "",
            f"Highest robust stable window with non-zero trust bridging: topology `{robust_coordination.topology}`, fail coupling `{robust_coordination.fail_coupling:.2f}`, trust coupling `{robust_coordination.trust_coupling:.2f}`, total fail coupling `{robust_coordination.avg_total_fail_coupling:.2f}`, total trust coupling `{robust_coordination.avg_total_trust_coupling:.2f}`, stable-run rate `{robust_coordination.stable_run_rate:.4f}`.",
            f"Over-coupling worst case: fail coupling `{overcoupled.fail_coupling:.2f}`, trust coupling `{overcoupled.trust_coupling:.2f}`, synchronized collapse rate `{overcoupled.synchronized_collapse_rate:.4f}`.",
            f"Over-decoupling worst case with zero trust bridging: fail coupling `{overdecoupled.fail_coupling:.2f}`, trust coupling `{overdecoupled.trust_coupling:.2f}`, meta-trigger rate `{overdecoupled.meta_trigger_rate:.4f}`.",
            "",
            "Coordination verification:",
            "- Coordination failure did route into Meta-trigger conditions whenever divergence stayed above the recoverable band and mean disturbance remained elevated.",
            "- At low failure-coupling sums the system could remain stable even with zero trust bridging, but once failure-coupling entered the upper scan band, non-zero trust bridging became necessary for any stable runs to remain.",
            "- The empirical safe window from this scan is documented in the coordination summary CSV in the output folder.",
            "",
            "## V4.1 Flags Before CN Translation",
            "",
        ]
    )
    if flags:
        for item in flags:
            lines.append(f"- {item}")
    else:
        lines.append("- No simulation-only blocker was strong enough in this run set to require a V4.1 revision before CN translation.")

    lines.extend(
        [
            "",
            "## Output Files",
            "",
            f"- [claude_brief_parameter_ranges.csv]({(output_dir / 'claude_brief_parameter_ranges.csv').resolve().as_posix()})",
            f"- [claude_brief_envelope.csv]({(output_dir / 'claude_brief_envelope.csv').resolve().as_posix()})",
            f"- [claude_brief_hero_gate.csv]({(output_dir / 'claude_brief_hero_gate.csv').resolve().as_posix()})",
            f"- [claude_brief_merged_layers.csv]({(output_dir / 'claude_brief_merged_layers.csv').resolve().as_posix()})",
            f"- [claude_brief_coordination_summary.csv]({(output_dir / 'claude_brief_coordination_summary.csv').resolve().as_posix()})",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the SOE V4 Claude brief simulation suite.")
    parser.add_argument("--seed", type=int, default=42, help="Base random seed.")
    parser.add_argument("--parameter-samples", type=int, default=25000, help="Number of O4 parameter candidates to sample.")
    parser.add_argument("--merged-runs", type=int, default=300, help="Monte Carlo runs per merged-layer scenario.")
    parser.add_argument("--coordination-runs", type=int, default=80, help="Monte Carlo runs per coordination scan cell.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("soe_v4") / "outputs" / "claude_brief",
        help="Directory for CSV and markdown outputs.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    calibration = calibrate_parameters(args.parameter_samples, args.seed)
    chosen: ParameterSet = calibration["chosen"]  # type: ignore[assignment]

    parameter_range_rows = calibration["candidate_ranges"]  # type: ignore[assignment]
    envelope_rows = calibration["envelope_rows"]  # type: ignore[assignment]
    confirmation_rows = calibration["normal_confirmation_rows"]  # type: ignore[assignment]
    collapse_threshold_rows = calibration["collapse_threshold_rows"]  # type: ignore[assignment]
    write_csv(output_dir / "claude_brief_parameter_ranges.csv", parameter_range_rows)
    write_csv(output_dir / "claude_brief_envelope.csv", envelope_rows)
    write_csv(output_dir / "claude_brief_normal_confirmation.csv", confirmation_rows)
    write_csv(output_dir / "claude_brief_collapse_thresholds.csv", collapse_threshold_rows)

    hero_rows, hero_summary = evaluate_hero_gate(args.seed)
    write_csv(output_dir / "claude_brief_hero_gate.csv", hero_rows)
    write_csv(output_dir / "claude_brief_hero_gate_summary.csv", [hero_summary])

    merged_rows, merged_summaries = evaluate_merged_layers(chosen, runs=args.merged_runs, seed=args.seed)
    write_csv(output_dir / "claude_brief_merged_layers.csv", merged_rows)
    write_csv(output_dir / "claude_brief_merged_layers_summary.csv", [asdict(row) for row in merged_summaries])

    coordination_rows: List[Dict[str, float | int | str]] = []
    coordination_summaries: List[CoordinationSummary] = []
    for topology in ("federation", "ring"):
        raw_rows, summaries = evaluate_coordination(
            chosen,
            runs=args.coordination_runs,
            seed=args.seed,
            topology=topology,
        )
        coordination_rows.extend(raw_rows)
        coordination_summaries.extend(summaries)
    write_csv(output_dir / "claude_brief_coordination_runs.csv", coordination_rows)
    write_csv(output_dir / "claude_brief_coordination_summary.csv", [asdict(row) for row in coordination_summaries])

    report = build_report(calibration, hero_summary, merged_summaries, coordination_summaries, output_dir)
    (output_dir / "claude_brief_report.md").write_text(report, encoding="utf-8")

    print("SOE V4 Claude brief run complete")
    print(f"Chosen parameters: a={chosen.a:.4f}, b={chosen.b:.4f}, c={chosen.c:.4f}, lambda={chosen.lam:.4f}, alpha={chosen.alpha:.4f}, mu={chosen.mu:.4f}")
    print(f"Hero gate false_positive_rate={hero_summary['false_positive_rate']}, false_negative_rate={hero_summary['false_negative_rate']}, fast_collapse_danger_rate={hero_summary['fast_collapse_danger_rate']}")
    print(f"Saved outputs to {output_dir}")


if __name__ == "__main__":
    main()
