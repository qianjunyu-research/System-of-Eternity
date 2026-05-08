import csv
import math
import pathlib
import random
from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Tuple


RUNS_STEP1 = 20
RUNS_STEP2 = 30
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

STEP1_THRESHOLD = 0.40
D_HUB_VALUES = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
S_THRESHOLDS = [round(0.10 + 0.05 * index, 2) for index in range(13)]


@dataclass
class Node:
    trust: float
    disturbance: float
    stability: float
    cognition: float


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def avg(values: Iterable[float]) -> float:
    values = list(values)
    return sum(values) / max(1, len(values))


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


def run_federation_simulation(
    *,
    seed: int,
    neighbors: Sequence[Sequence[int]],
    d_hub: float,
) -> List[List[Node]]:
    nodes = initialize_nodes(seed)
    history: List[List[Node]] = []
    rng = random.Random(seed)
    bridge_nodes = set(federation_bridges())

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
            if index in bridge_nodes:
                disturbance = max(disturbance, d_hub)

            cognition = node.cognition
            cognition += 0.015
            cognition += rng.uniform(-0.015, 0.015)
            cognition += 0.08 * disturbance
            cognition -= 0.24 * node.cognition

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
                avg_disturbance = avg(local_next[j].disturbance for j in node_neighbors)
                avg_cognition = avg(local_next[j].cognition for j in node_neighbors)
                propagation_multiplier = 1.15 if index in bridge_nodes else 1.0
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


def two_tier_s_network(step_nodes: Sequence[Node]) -> float:
    cluster_scores = []
    for cluster in range(CLUSTER_COUNT):
        values = [step_nodes[i].stability for i in cluster_nodes(cluster)]
        cluster_scores.append(percentile(values, 0.25))
    return min(cluster_scores)


def trigger_fired(history: Sequence[Sequence[Node]], threshold: float) -> int:
    return int(any(two_tier_s_network(step_nodes) < threshold for step_nodes in history))


def failure_shares_by_step(history: Sequence[Sequence[Node]], target_nodes: Sequence[int]) -> List[float]:
    return [
        sum(1 for node_index in target_nodes if step_nodes[node_index].stability < FAILURE_THRESHOLD)
        / max(1, len(target_nodes))
        for step_nodes in history
    ]


def sustained_ignition(shares: Sequence[float]) -> int:
    current = 0
    for share in shares:
        if share >= IGNITION_SHARE:
            current += 1
            if current >= IGNITION_STEPS:
                return 1
        else:
            current = 0
    return 0


def final_mean(history: Sequence[Sequence[Node]], attr: str) -> float:
    return avg(getattr(node, attr) for node in history[-1])


def run_disturbance_calibration() -> Tuple[List[Dict[str, object]], float, bool]:
    neighbors = build_federation_neighbors()
    rows: List[Dict[str, object]] = []
    selected_d_hub = D_HUB_VALUES[-1]
    calibrated = False

    for d_hub in D_HUB_VALUES:
        run_rows = []
        for run_index in range(RUNS_STEP1):
            seed = SEED_START + run_index
            history = run_federation_simulation(seed=seed, neighbors=neighbors, d_hub=d_hub)
            network_failure = failure_shares_by_step(history, list(range(NODE_COUNT)))
            run_rows.append(
                {
                    "trigger_A_fired": trigger_fired(history, STEP1_THRESHOLD),
                    "sustained_ignition_observed": sustained_ignition(network_failure),
                }
            )

        row = {
            "d_hub": d_hub,
            "runs": RUNS_STEP1,
            "trigger_A_fire_rate": avg(int(item["trigger_A_fired"]) for item in run_rows),
            "sustained_ignition_rate": avg(int(item["sustained_ignition_observed"]) for item in run_rows),
        }
        rows.append(row)
        if float(row["trigger_A_fire_rate"]) >= 0.50:
            selected_d_hub = d_hub
            calibrated = True
            break

    return rows, selected_d_hub, calibrated


def run_threshold_sweep(d_hub: float) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    neighbors = build_federation_neighbors()
    histories = [
        run_federation_simulation(seed=SEED_START + run_index, neighbors=neighbors, d_hub=d_hub)
        for run_index in range(RUNS_STEP2)
    ]

    rows: List[Dict[str, object]] = []
    summary: List[Dict[str, object]] = []
    for threshold in S_THRESHOLDS:
        threshold_rows = []
        for run_index, history in enumerate(histories):
            seed = SEED_START + run_index
            network_failure = failure_shares_by_step(history, list(range(NODE_COUNT)))
            ignition = sustained_ignition(network_failure)
            fired = trigger_fired(history, threshold)
            row = {
                "s_threshold": threshold,
                "run_index": run_index,
                "seed": seed,
                "trigger_A_fired": fired,
                "sustained_ignition_observed": ignition,
                "false_alarm": int(fired and not ignition),
                "network_failure_rate": avg(network_failure),
                "final_cooperation": final_mean(history, "trust"),
                "final_trust": final_mean(history, "trust"),
            }
            rows.append(row)
            threshold_rows.append(row)

        ignition_rows = [row for row in threshold_rows if int(row["sustained_ignition_observed"])]
        missed_detection_rate = (
            avg(1 - int(row["trigger_A_fired"]) for row in ignition_rows)
            if ignition_rows
            else 0.0
        )
        summary.append(
            {
                "s_threshold": threshold,
                "runs": RUNS_STEP2,
                "trigger_A_fire_rate": avg(int(row["trigger_A_fired"]) for row in threshold_rows),
                "sustained_ignition_rate": avg(int(row["sustained_ignition_observed"]) for row in threshold_rows),
                "false_alarm_rate": avg(int(row["false_alarm"]) for row in threshold_rows),
                "missed_detection_rate": missed_detection_rate,
                "recommended": 0,
            }
        )

    eligible = [row for row in summary if float(row["false_alarm_rate"]) <= 0.10]
    if eligible:
        recommended = min(eligible, key=lambda row: float(row["s_threshold"]))
    else:
        recommended = min(summary, key=lambda row: float(row["false_alarm_rate"]))
    for row in summary:
        row["recommended"] = int(row is recommended)
    return rows, summary


def write_note(
    *,
    d_hub: float,
    calibrated: bool,
    disturbance_rows: Sequence[Dict[str, object]],
    threshold_summary: Sequence[Dict[str, object]],
) -> None:
    recommended = next(row for row in threshold_summary if int(row["recommended"]))
    target_achieved = float(recommended["false_alarm_rate"]) <= 0.10
    any_trigger = any(float(row["trigger_A_fire_rate"]) > 0.0 for row in threshold_summary)
    structural_observation = (
        "Trigger A never fired in the final threshold sweep; federation two-tier S_network appears resistant to bridge-only D_hub stress."
        if not any_trigger
        else "Trigger A fired only after calibrated bridge disturbance; compare against sustained ignition before deployment."
    )
    pathlib.Path("v19b_note.txt").write_text(
        "\n".join(
            [
                f"D_hub value used: {d_hub} ({'first Step 1 value with trigger_A_fire_rate >= 0.50' if calibrated else 'maximum tested value; Step 1 did not reach trigger_A_fire_rate >= 0.50'}).",
                f"Recommended federation S_threshold: {recommended['s_threshold']}.",
                f"False alarm rate at recommended threshold: {float(recommended['false_alarm_rate']):.3f}.",
                f"False alarm target <= 10% achieved: {'yes' if target_achieved else 'no'}.",
                f"Deployment recommendation: {'do not approve full automation from v19b alone; sensitivity is unresolved' if not any_trigger else ('safe to enable automatic Trigger A at the recommended threshold' if target_achieved else 'manual override remains required; escalate to v20')}.",
                f"Structural observation: {structural_observation}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    disturbance_rows, d_hub, calibrated = run_disturbance_calibration()
    threshold_runs, threshold_summary = run_threshold_sweep(d_hub)

    write_csv(pathlib.Path("v19b_disturbance_calibration.csv"), disturbance_rows)
    write_csv(pathlib.Path("v19b_threshold_runs.csv"), threshold_runs)
    write_csv(pathlib.Path("v19b_threshold_summary.csv"), threshold_summary)
    write_note(
        d_hub=d_hub,
        calibrated=calibrated,
        disturbance_rows=disturbance_rows,
        threshold_summary=threshold_summary,
    )


if __name__ == "__main__":
    main()
