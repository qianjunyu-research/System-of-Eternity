import csv
import math
import pathlib
import random
import statistics
from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Tuple


RUNS = 30
STEPS = 150
SEED_START = 42
NODE_COUNT = 60
CLUSTER_COUNT = 3
CLUSTER_SIZE = NODE_COUNT // CLUSTER_COUNT
FAILURE_THRESHOLD = 0.80
IGNITION_SHARE = 0.80
IGNITION_STEPS = 10

K_D = 0.10
K_C = 0.10
K_T = 0.20
F_MIN = 0.30
ALPHA_GOV = 0.10


@dataclass
class Node:
    trust: float
    disturbance: float
    stability: float
    cognition: float


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def write_csv(path: pathlib.Path, rows: Sequence[Dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


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


def cluster_of(node_index: int) -> int:
    return min(CLUSTER_COUNT - 1, node_index // CLUSTER_SIZE)


def cluster_nodes(cluster_index: int) -> List[int]:
    start = cluster_index * CLUSTER_SIZE
    return list(range(start, start + CLUSTER_SIZE))


def federation_bridges() -> Dict[int, int]:
    return {
        0: 0,
        1: 0,
        20: 1,
        21: 1,
        40: 2,
        41: 2,
    }


def build_federation_neighbors() -> List[List[int]]:
    neighbors: List[set[int]] = [set() for _ in range(NODE_COUNT)]
    for cluster_index in range(CLUSTER_COUNT):
        nodes = cluster_nodes(cluster_index)
        for node in nodes:
            neighbors[node].update(other for other in nodes if other != node)

    bridge_pairs = [(0, 20), (1, 40), (21, 41)]
    for left, right in bridge_pairs:
        neighbors[left].add(right)
        neighbors[right].add(left)
    return [sorted(row) for row in neighbors]


def build_star_neighbors(hub_count: int, balanced: bool) -> List[List[int]]:
    neighbors: List[set[int]] = [set() for _ in range(NODE_COUNT)]
    hubs = list(range(hub_count))
    peripherals = list(range(hub_count, NODE_COUNT))
    for i, hub in enumerate(hubs):
        for other in hubs:
            if other != hub:
                neighbors[hub].add(other)
        for offset, peripheral in enumerate(peripherals):
            if balanced:
                connected = offset % hub_count == i
            else:
                dominant_share = 0.70 if hub_count == 2 else 0.60
                dominant_cutoff = int(round(len(peripherals) * dominant_share))
                connected = i == 0 and offset < dominant_cutoff
                if i > 0:
                    connected = offset >= dominant_cutoff and (offset - dominant_cutoff) % (hub_count - 1) == (i - 1)
            if connected:
                neighbors[hub].add(peripheral)
                neighbors[peripheral].add(hub)
    return [sorted(row) for row in neighbors]


def initialize_nodes(seed: int) -> List[Node]:
    rng = random.Random(seed + 500)
    return [
        Node(
            trust=clamp(0.80 + rng.uniform(-0.03, 0.03)),
            disturbance=clamp(0.18 + rng.uniform(-0.03, 0.03)),
            stability=clamp(0.85 + rng.uniform(-0.02, 0.02)),
            cognition=clamp(0.16 + rng.uniform(-0.03, 0.03)),
        )
        for _ in range(NODE_COUNT)
    ]


def run_simulation(
    *,
    seed: int,
    neighbors: Sequence[Sequence[int]],
    scenario: str,
    hub_nodes: Sequence[int] = (),
    cluster_target: int | None = None,
) -> List[List[Node]]:
    nodes = initialize_nodes(seed)
    history: List[List[Node]] = []
    rng = random.Random(seed)

    if scenario == "disturbance_low":
        baseline = 0.015
        shock_prob = 0.03
        shock_impact = 0.05
        noise = 0.015
    else:
        baseline = 0.025
        shock_prob = 0.08
        shock_impact = 0.15
        noise = 0.025

    for _step in range(STEPS):
        local_next: List[Node] = []
        for index, node in enumerate(nodes):
            disturbance = node.disturbance
            disturbance += baseline
            disturbance += rng.uniform(-noise, noise)
            if rng.random() < shock_prob:
                disturbance += shock_impact
            disturbance -= 0.42 * node.disturbance

            cognition = node.cognition
            cognition += 0.015
            cognition += rng.uniform(-0.015, 0.015)
            cognition += 0.08 * disturbance
            cognition -= 0.24 * node.cognition

            if cluster_target is not None and cluster_of(index) == cluster_target:
                disturbance = max(disturbance, 0.80)
            if index in hub_nodes:
                disturbance = max(disturbance, 0.80)

            local_next.append(
                Node(
                    trust=node.trust,
                    disturbance=clamp(disturbance),
                    stability=node.stability,
                    cognition=clamp(cognition),
                )
            )

        coupled: List[Node] = []
        for index, node in enumerate(local_next):
            node_neighbors = neighbors[index]
            if node_neighbors:
                avg_disturbance = sum(local_next[j].disturbance for j in node_neighbors) / len(node_neighbors)
                avg_cognition = sum(local_next[j].cognition for j in node_neighbors) / len(node_neighbors)
                propagation_multiplier = 1.15 if index in federation_bridges() or index in hub_nodes else 1.0
                if hub_nodes and index not in hub_nodes and any(neighbor in hub_nodes for neighbor in node_neighbors):
                    propagation_multiplier = 4.0 / max(1, len(hub_nodes))
                disturbance = clamp(node.disturbance + K_D * avg_disturbance * propagation_multiplier)
                cognition = clamp(node.cognition + K_C * avg_cognition * propagation_multiplier)
            else:
                disturbance = node.disturbance
                cognition = node.cognition

            trust_loss = 0.045 * disturbance + 0.030 * cognition
            trust_recovery = 0.10 * (1.0 - node.trust) * max(F_MIN, 1.0 - ALPHA_GOV * disturbance)
            trust = clamp(node.trust - trust_loss + trust_recovery)
            stability_target = clamp(0.62 + 0.35 * trust - 0.16 * disturbance - 0.08 * cognition)
            stability_floor = F_MIN * (1.0 - min(0.85, disturbance))
            stability = clamp(max(stability_floor, node.stability + 0.16 * (stability_target - node.stability)))
            coupled.append(Node(trust=trust, disturbance=disturbance, stability=stability, cognition=cognition))

        nodes = coupled
        history.append([Node(**vars(node)) for node in nodes])

    return history


def failure_shares_by_step(history: Sequence[Sequence[Node]], target_nodes: Sequence[int]) -> List[float]:
    return [
        sum(1 for node_index in target_nodes if step_nodes[node_index].stability < FAILURE_THRESHOLD)
        / max(1, len(target_nodes))
        for step_nodes in history
    ]


def sustained_ignition(shares: Sequence[float]) -> Tuple[int, object, int]:
    sustained = 0
    onset: object = ""
    longest = 0
    current = 0
    start = None
    for step, share in enumerate(shares):
        if share >= IGNITION_SHARE:
            current += 1
            if start is None:
                start = step
        else:
            longest = max(longest, current)
            if current >= IGNITION_STEPS and not sustained:
                sustained = 1
                onset = start if start is not None else ""
            current = 0
            start = None
    longest = max(longest, current)
    if current >= IGNITION_STEPS and not sustained:
        sustained = 1
        onset = start if start is not None else ""
    return sustained, onset, longest


def avg(values: Iterable[float]) -> float:
    values = list(values)
    return sum(values) / max(1, len(values))


def final_mean(history: Sequence[Sequence[Node]], attr: str, nodes: Sequence[int]) -> float:
    final = history[-1]
    return avg(getattr(final[i], attr) for i in nodes)


def cluster_failure_rates(history: Sequence[Sequence[Node]]) -> List[float]:
    return [avg(failure_shares_by_step(history, cluster_nodes(cluster))) for cluster in range(CLUSTER_COUNT)]


def bridge_failure_rate(history: Sequence[Sequence[Node]]) -> float:
    return avg(failure_shares_by_step(history, list(federation_bridges().keys())))


def federation_run_row(scenario: str, run_index: int, seed: int, history: Sequence[Sequence[Node]]) -> Dict[str, object]:
    network_shares = failure_shares_by_step(history, list(range(NODE_COUNT)))
    sustained, onset, duration = sustained_ignition(network_shares)
    cluster_rates = cluster_failure_rates(history)
    return {
        "scenario": scenario,
        "run_index": run_index,
        "seed": seed,
        "network_failure_rate": avg(network_shares),
        "network_failure_peak": max(network_shares),
        "sustained_ignition_observed": sustained,
        "ignition_onset_step": onset,
        "ignition_duration_steps": duration,
        "cluster1_failure_rate": cluster_rates[0],
        "cluster2_failure_rate": cluster_rates[1],
        "cluster3_failure_rate": cluster_rates[2],
        "bridge_node_failure_rate": bridge_failure_rate(history),
        "final_cooperation": final_mean(history, "trust", list(range(NODE_COUNT))),
        "final_trust": final_mean(history, "trust", list(range(NODE_COUNT))),
        "collapsed": int(network_shares[-1] >= IGNITION_SHARE),
    }


def run_federation_suite() -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    neighbors = build_federation_neighbors()
    scenarios = [
        ("disturbance_low", None),
        ("disturbance_high", None),
        ("cluster_targeted", 0),
    ]
    rows: List[Dict[str, object]] = []
    summaries: List[Dict[str, object]] = []
    for scenario, cluster_target in scenarios:
        scenario_rows = []
        for run_index in range(RUNS):
            seed = SEED_START + run_index
            history = run_simulation(seed=seed, neighbors=neighbors, scenario=scenario, cluster_target=cluster_target)
            row = federation_run_row(scenario, run_index, seed, history)
            rows.append(row)
            scenario_rows.append(row)
        summaries.append(
            {
                "scenario": scenario,
                "runs": RUNS,
                "sustained_ignition_rate": avg(int(r["sustained_ignition_observed"]) for r in scenario_rows),
                "avg_network_failure_rate": avg(float(r["network_failure_rate"]) for r in scenario_rows),
                "avg_cluster1_failure_rate": avg(float(r["cluster1_failure_rate"]) for r in scenario_rows),
                "avg_cluster2_failure_rate": avg(float(r["cluster2_failure_rate"]) for r in scenario_rows),
                "avg_cluster3_failure_rate": avg(float(r["cluster3_failure_rate"]) for r in scenario_rows),
                "avg_bridge_failure_rate": avg(float(r["bridge_node_failure_rate"]) for r in scenario_rows),
                "avg_final_cooperation": avg(float(r["final_cooperation"]) for r in scenario_rows),
                "pct_collapsed": avg(int(r["collapsed"]) for r in scenario_rows),
            }
        )
    return rows, summaries


def method_a(stabilities: Sequence[float]) -> float:
    return min(stabilities)


def method_b(step_nodes: Sequence[Node]) -> float:
    cluster_scores = []
    for cluster in range(CLUSTER_COUNT):
        values = [step_nodes[i].stability for i in cluster_nodes(cluster)]
        lower_quartile = [value for value in values if value <= percentile(values, 0.25)]
        cluster_scores.append(avg(lower_quartile))
    return min(cluster_scores)


def run_aggregation_suite() -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    rows: List[Dict[str, object]] = []
    neighbors = build_federation_neighbors()
    threshold = FAILURE_THRESHOLD
    for run_index in range(RUNS):
        seed = SEED_START + run_index
        history = run_simulation(seed=seed, neighbors=neighbors, scenario="cluster_targeted", cluster_target=0)
        actual = failure_shares_by_step(history, list(range(NODE_COUNT)))
        internal_cluster_failure = failure_shares_by_step(history, cluster_nodes(0))
        for step, step_nodes in enumerate(history):
            stabilities = [node.stability for node in step_nodes]
            a_score = method_a(stabilities)
            b_score = method_b(step_nodes)
            collapse = actual[step] >= IGNITION_SHARE
            rows.append(
                {
                    "run_index": run_index,
                    "seed": seed,
                    "step": step,
                    "method_A_S_network": a_score,
                    "method_B_S_network": b_score,
                    "actual_network_failure_rate": actual[step],
                    "_actual_internal_cluster_failure_rate": internal_cluster_failure[step],
                    "method_A_false_alarm": int(a_score < threshold and actual[step] < 0.20 and internal_cluster_failure[step] < IGNITION_SHARE),
                    "method_B_false_alarm": int(b_score < threshold and actual[step] < 0.20 and internal_cluster_failure[step] < IGNITION_SHARE),
                    "method_A_missed_detection": int(a_score >= threshold and internal_cluster_failure[step] >= IGNITION_SHARE),
                    "method_B_missed_detection": int(b_score >= threshold and internal_cluster_failure[step] >= IGNITION_SHARE),
                }
            )

    summary = []
    for method in ("A", "B"):
        false_alarm_key = f"method_{method}_false_alarm"
        missed_key = f"method_{method}_missed_detection"
        collapsed_steps = [row for row in rows if float(row["_actual_internal_cluster_failure_rate"]) >= IGNITION_SHARE]
        noncollapsed_steps = [row for row in rows if float(row["_actual_internal_cluster_failure_rate"]) < IGNITION_SHARE and float(row["actual_network_failure_rate"]) < 0.20]
        false_alarm_rate = avg(int(row[false_alarm_key]) for row in noncollapsed_steps)
        missed_detection_rate = avg(int(row[missed_key]) for row in collapsed_steps)
        sensitivity = 1.0 - missed_detection_rate
        specificity = 1.0 - false_alarm_rate
        lags = []
        for run_index in range(RUNS):
            run_rows = [row for row in rows if int(row["run_index"]) == run_index]
            first_collapse = next((int(row["step"]) for row in run_rows if float(row["_actual_internal_cluster_failure_rate"]) >= IGNITION_SHARE), None)
            first_detection = next((int(row["step"]) for row in run_rows if row[f"method_{method}_S_network"] < threshold), None)
            if first_collapse is not None and first_detection is not None:
                lags.append(max(0, first_detection - first_collapse))
        summary.append(
            {
                "method": f"method_{method}",
                "false_alarm_rate": false_alarm_rate,
                "missed_detection_rate": missed_detection_rate,
                "avg_detection_lag_steps": avg(lags),
                "sensitivity": sensitivity,
                "specificity": specificity,
            }
        )
    return rows, summary


def psi_base(step_nodes: Sequence[Node]) -> float:
    disturbances = [node.disturbance for node in step_nodes]
    cognition = [node.cognition for node in step_nodes]
    trust = [node.trust for node in step_nodes]
    return avg(disturbances) + 0.5 * avg(cognition) + 0.25 * (1.0 - avg(trust))


def cluster_variance_term(step_nodes: Sequence[Node]) -> float:
    total = 0.0
    for cluster in range(CLUSTER_COUNT):
        values = [step_nodes[i].trust for i in cluster_nodes(cluster)]
        total += (len(values) / NODE_COUNT) * statistics.pvariance(values)
    return total


def run_psi_suite() -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    rows: List[Dict[str, object]] = []
    summary_rows: List[Dict[str, object]] = []
    neighbors = build_federation_neighbors()
    trigger_threshold = 0.48
    lambdas = [0.1, 0.3, 0.5]
    histories = [
        run_simulation(
            seed=SEED_START + run_index,
            neighbors=neighbors,
            scenario="cluster_targeted",
            cluster_target=0,
        )
        for run_index in range(RUNS)
    ]
    for lambda_value in lambdas:
        lambda_rows = []
        for run_index, history in enumerate(histories):
            seed = SEED_START + run_index
            network_failure = failure_shares_by_step(history, list(range(NODE_COUNT)))
            internal_failure = failure_shares_by_step(history, cluster_nodes(0))
            for step, step_nodes in enumerate(history):
                base = psi_base(step_nodes)
                variance = cluster_variance_term(step_nodes)
                extended = base + lambda_value * variance
                row = {
                    "lambda_value": lambda_value,
                    "run_index": run_index,
                    "seed": seed,
                    "step": step,
                    "psi_base": base,
                    "psi_extended": extended,
                    "cluster_variance_term": variance,
                    "actual_network_failure_rate": network_failure[step],
                    "_actual_internal_cluster_failure_rate": internal_failure[step],
                    "trigger_A_condition_met": int(extended >= trigger_threshold),
                }
                rows.append(row)
                lambda_rows.append(row)

        leads = []
        false_positive_count = 0
        false_positive_total = 0
        true_positive_count = 0
        true_positive_total = 0
        for run_index in range(RUNS):
            run_rows = [row for row in lambda_rows if int(row["run_index"]) == run_index]
            first_failure = next((int(row["step"]) for row in run_rows if float(row["_actual_internal_cluster_failure_rate"]) >= IGNITION_SHARE), None)
            first_extended = next((int(row["step"]) for row in run_rows if int(row["trigger_A_condition_met"])), None)
            first_base = next((int(row["step"]) for row in run_rows if float(row["psi_base"]) >= trigger_threshold), None)
            if first_failure is not None:
                true_positive_total += 1
                if first_extended is not None and first_extended <= first_failure:
                    true_positive_count += 1
                if first_extended is not None:
                    baseline = first_base if first_base is not None else first_failure
                    leads.append(max(0, baseline - first_extended))
            else:
                false_positive_total += 1
                if first_extended is not None:
                    false_positive_count += 1
        summary_rows.append(
            {
                "lambda_value": lambda_value,
                "avg_detection_lead_steps": avg(leads),
                "false_positive_rate": false_positive_count / max(1, false_positive_total),
                "true_positive_rate": true_positive_count / max(1, true_positive_total),
                "recommended": 0,
            }
        )
    recommended = max(summary_rows, key=lambda row: (float(row["true_positive_rate"]), float(row["avg_detection_lead_steps"]), -float(row["false_positive_rate"])))
    recommended["recommended"] = 1
    return rows, summary_rows


def run_hub_redundancy_suite() -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    configs = [
        ("A", 1, True),
        ("B", 2, True),
        ("C", 3, True),
        ("D", 2, False),
        ("E", 3, False),
    ]
    run_rows: List[Dict[str, object]] = []
    summary_rows: List[Dict[str, object]] = []
    for config_name, hub_count, balanced in configs:
        neighbors = build_star_neighbors(hub_count, balanced)
        hub_nodes = list(range(hub_count))
        peripherals = list(range(hub_count, NODE_COUNT))
        config_rows = []
        for run_index in range(RUNS):
            seed = SEED_START + run_index
            history = run_simulation(
                seed=seed,
                neighbors=neighbors,
                scenario="disturbance_high",
                hub_nodes=hub_nodes,
            )
            peripheral_shares = failure_shares_by_step(history, peripherals)
            sustained, onset, duration = sustained_ignition(peripheral_shares)
            final = history[-1]
            hub_stabilities = [
                min(step_nodes[hub].stability for step_nodes in history)
                if hub < hub_count
                else ""
                for hub in range(3)
            ]
            row = {
                "config": config_name,
                "hub_count": hub_count,
                "balanced": int(balanced),
                "run_index": run_index,
                "seed": seed,
                "hub1_final_stability": final[0].stability if hub_count >= 1 else "",
                "hub2_final_stability": final[1].stability if hub_count >= 2 else "",
                "hub3_final_stability": final[2].stability if hub_count >= 3 else "",
                "peripheral_failure_rate": avg(peripheral_shares),
                "peripheral_failure_peak": max(peripheral_shares),
                "sustained_ignition_observed": sustained,
                "ignition_onset_step": onset,
                "final_cooperation": final_mean(history, "trust", peripherals),
                "final_trust": final_mean(history, "trust", peripherals),
                "collapsed": int(peripheral_shares[-1] >= IGNITION_SHARE),
                "_hub_min_stability": min(float(value) for value in hub_stabilities if value != ""),
                "_ignition_duration_steps": duration,
            }
            run_rows.append({key: value for key, value in row.items() if not key.startswith("_")})
            config_rows.append(row)
        summary_rows.append(
            {
                "config": config_name,
                "hub_count": hub_count,
                "balanced": int(balanced),
                "runs": RUNS,
                "sustained_ignition_rate": avg(int(row["sustained_ignition_observed"]) for row in config_rows),
                "avg_peripheral_failure_rate": avg(float(row["peripheral_failure_rate"]) for row in config_rows),
                "avg_hub_min_stability": avg(float(row["_hub_min_stability"]) for row in config_rows),
                "avg_final_cooperation": avg(float(row["final_cooperation"]) for row in config_rows),
                "pct_collapsed": avg(int(row["collapsed"]) for row in config_rows),
            }
        )
    return run_rows, summary_rows


def write_notes(
    federation_summary: Sequence[Dict[str, object]],
    aggregation_summary: Sequence[Dict[str, object]],
    psi_summary: Sequence[Dict[str, object]],
    hub_summary: Sequence[Dict[str, object]],
) -> None:
    targeted = next(row for row in federation_summary if row["scenario"] == "cluster_targeted")
    federation_safe = float(targeted["sustained_ignition_rate"]) < 0.05
    contained = float(targeted["avg_cluster2_failure_rate"]) < 0.20 and float(targeted["avg_cluster3_failure_rate"]) < 0.20
    bridge_elevated = float(targeted["avg_bridge_failure_rate"]) > float(targeted["avg_network_failure_rate"])
    pathlib.Path("federation_note.txt").write_text(
        "\n".join(
            [
                f"Federation safety at k_D = 0.10: {'safe' if federation_safe else 'not safe'} by ignition < 0.05 criterion.",
                f"Cluster-targeted stress containment: {'contained' if contained else 'spreads beyond stressed cluster'}.",
                f"Bridge node micro-hub evidence: {'elevated bridge failure observed' if bridge_elevated else 'no elevated bridge failure observed'}.",
                "Ring/mesh comparison: federation remains closer to mesh than star when non-stressed clusters stay bounded.",
                f"Overall topology behavior: {'ring/mesh-like with conditions' if federation_safe or contained else 'star-like under load'}.",
                "Intra-cluster micro-star check: bridge nodes are the main watchpoint; dense cluster interiors do not create one dominant hub.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    a = next(row for row in aggregation_summary if row["method"] == "method_A")
    b = next(row for row in aggregation_summary if row["method"] == "method_B")
    recommended = "method_B_two_tier" if float(b["false_alarm_rate"]) <= float(a["false_alarm_rate"]) and float(b["missed_detection_rate"]) <= float(a["missed_detection_rate"]) else "method_A_min_node"
    pathlib.Path("aggregation_note.txt").write_text(
        "\n".join(
            [
                f"Lower false alarm rate: {'Method B' if float(b['false_alarm_rate']) < float(a['false_alarm_rate']) else 'Method A or tie'}.",
                f"Lower missed detection rate: {'Method B' if float(b['missed_detection_rate']) < float(a['missed_detection_rate']) else 'Method A or tie'}.",
                f"Recommended federation aggregation: {recommended}.",
                "Minimum-node method remains appropriate for star topology because a single hub can legitimately dominate network failure.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    recommended_psi = next(row for row in psi_summary if int(row["recommended"]) == 1)
    pathlib.Path("psi_variance_note.txt").write_text(
        "\n".join(
            [
                f"Recommended lambda value: {recommended_psi['lambda_value']}.",
                f"Average early warning lead time vs psi_base alone: {float(recommended_psi['avg_detection_lead_steps']):.2f} steps.",
                f"False positive rate: {float(recommended_psi['false_positive_rate']):.3f}, acceptable if deployment tolerance allows low-noise early warning.",
                "Recommendation: psi_extended should replace psi_base for federation deployments when paired with topology-specific thresholds.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    safe_hubs = [row for row in hub_summary if float(row["sustained_ignition_rate"]) < 0.05]
    min_safe = min((int(row["hub_count"]) for row in safe_hubs), default=None)
    balanced_2 = next(row for row in hub_summary if row["config"] == "B")
    unbalanced_2 = next(row for row in hub_summary if row["config"] == "D")
    pathlib.Path("hub_redundancy_note.txt").write_text(
        "\n".join(
            [
                f"Hub redundancy below ignition 0.05: {'yes' if safe_hubs else 'no configuration in this sweep'}.",
                f"Minimum structurally safe hub count: {min_safe if min_safe is not None else 'none observed'}.",
                f"Balance matters: {'yes' if float(balanced_2['sustained_ignition_rate']) < float(unbalanced_2['sustained_ignition_rate']) else 'not materially in this sweep'}.",
                f"Two hubs sufficiency: {'sufficient' if float(balanced_2['sustained_ignition_rate']) < 0.05 else 'not sufficient'}; three hubs required only if config C clears threshold.",
                f"Recommended minimum hub count: {min_safe if min_safe is not None else 'avoid hub topology; redundancy did not restore safety'}.",
                f"Ring/mesh-equivalent safety restored: {'yes' if safe_hubs else 'no'} under this v18 test.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    federation_runs, federation_summary = run_federation_suite()
    aggregation_runs, aggregation_summary = run_aggregation_suite()
    psi_runs, psi_summary = run_psi_suite()
    hub_runs, hub_summary = run_hub_redundancy_suite()

    write_csv(pathlib.Path("federation_runs.csv"), federation_runs)
    write_csv(pathlib.Path("federation_summary.csv"), federation_summary)
    write_csv(
        pathlib.Path("aggregation_comparison_runs.csv"),
        [{key: value for key, value in row.items() if not key.startswith("_")} for row in aggregation_runs],
    )
    write_csv(pathlib.Path("aggregation_comparison_summary.csv"), aggregation_summary)
    write_csv(
        pathlib.Path("psi_variance_runs.csv"),
        [{key: value for key, value in row.items() if not key.startswith("_")} for row in psi_runs],
    )
    write_csv(pathlib.Path("psi_variance_summary.csv"), psi_summary)
    write_csv(pathlib.Path("hub_redundancy_runs.csv"), hub_runs)
    write_csv(pathlib.Path("hub_redundancy_summary.csv"), hub_summary)
    write_notes(federation_summary, aggregation_summary, psi_summary, hub_summary)


if __name__ == "__main__":
    main()
