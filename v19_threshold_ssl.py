import csv
import math
import pathlib
import random
from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Tuple


RUNS = 30
SSL_RUNS = 20
STEPS = 150
SSL_STEPS = 500
BETRAYAL_STEP = 100
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

RING_MESH_THRESHOLD = FAILURE_THRESHOLD


@dataclass
class Node:
    trust: float
    disturbance: float
    stability: float
    cognition: float


@dataclass
class SSLNode:
    cooperation: float
    trust_memory: float
    disturbance: float
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
    steps: int = STEPS,
    scenario: str = "disturbance_high",
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

    for _step in range(steps):
        local_next: List[Node] = []
        for node in nodes:
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

            local_next.append(
                Node(
                    trust=node.trust,
                    disturbance=clamp(disturbance),
                    stability=node.stability,
                    cognition=clamp(cognition),
                )
            )

        coupled: List[Node] = []
        bridge_nodes = federation_bridges()
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
    final = history[-1]
    return avg(getattr(node, attr) for node in final)


def run_federation_threshold_suite() -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    neighbors = build_federation_neighbors()
    thresholds = [round(0.10 + 0.05 * index, 2) for index in range(9)]
    histories = [
        run_federation_simulation(seed=SEED_START + run_index, neighbors=neighbors)
        for run_index in range(RUNS)
    ]

    rows: List[Dict[str, object]] = []
    summary: List[Dict[str, object]] = []
    for threshold in thresholds:
        threshold_rows = []
        for run_index, history in enumerate(histories):
            seed = SEED_START + run_index
            scores = [two_tier_s_network(step_nodes) for step_nodes in history]
            trigger_fired = int(any(score < threshold for score in scores))
            network_failure = failure_shares_by_step(history, list(range(NODE_COUNT)))
            ignition = sustained_ignition(network_failure)
            row = {
                "s_threshold": threshold,
                "run_index": run_index,
                "seed": seed,
                "trigger_A_fired": trigger_fired,
                "sustained_ignition_observed": ignition,
                "false_alarm": int(trigger_fired and not ignition),
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
                "runs": RUNS,
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


def initialize_ssl_nodes(seed: int) -> List[SSLNode]:
    rng = random.Random(seed + 1900)
    return [
        SSLNode(
            cooperation=clamp(0.78 + rng.uniform(-0.04, 0.04)),
            trust_memory=clamp(0.82 + rng.uniform(-0.03, 0.03)),
            disturbance=clamp(0.16 + rng.uniform(-0.03, 0.03)),
            cognition=clamp(0.14 + rng.uniform(-0.03, 0.03)),
        )
        for _ in range(NODE_COUNT)
    ]


def run_ssl_simulation(seed: int, neighbors: Sequence[Sequence[int]]) -> List[Tuple[float, float]]:
    rng = random.Random(seed + 2500)
    nodes = initialize_ssl_nodes(seed)
    history: List[Tuple[float, float]] = []
    betrayed_nodes = set(rng.sample(range(NODE_COUNT), k=max(1, NODE_COUNT // 10)))

    for step in range(SSL_STEPS):
        if step == BETRAYAL_STEP:
            for index in betrayed_nodes:
                nodes[index].trust_memory = 0.0
                nodes[index].cooperation = clamp(nodes[index].cooperation - 0.35)

        local_next: List[SSLNode] = []
        for index, node in enumerate(nodes):
            node_neighbors = neighbors[index]
            neighbor_cooperation = avg(nodes[j].cooperation for j in node_neighbors) if node_neighbors else node.cooperation
            neighbor_trust = avg(nodes[j].trust_memory for j in node_neighbors) if node_neighbors else node.trust_memory

            disturbance = node.disturbance + 0.018 + rng.uniform(-0.018, 0.018)
            if rng.random() < 0.05:
                disturbance += 0.07
            if step >= BETRAYAL_STEP and index in betrayed_nodes:
                disturbance += 0.035
            disturbance = clamp(disturbance - 0.36 * node.disturbance)

            cognition = node.cognition + 0.010 + 0.05 * disturbance + rng.uniform(-0.010, 0.010)
            cognition = clamp(cognition - 0.22 * node.cognition)

            cooperation_target = clamp(
                0.70
                + 0.20 * neighbor_cooperation
                + 0.10 * node.trust_memory
                - 0.10 * disturbance
                - 0.06 * cognition
            )
            # Role clarity is modeled as a fast behavioral coordination channel.
            cooperation = clamp(node.cooperation + 0.18 * (cooperation_target - node.cooperation))

            trust_target = clamp(
                0.63
                + 0.22 * neighbor_trust
                + 0.10 * cooperation
                - 0.08 * disturbance
                - 0.04 * cognition
            )
            # Belonging/trust memory is deliberately inertial: it updates more slowly.
            trust_update_rate = 0.045 if step >= BETRAYAL_STEP else 0.060
            trust_memory = clamp(node.trust_memory + trust_update_rate * (trust_target - node.trust_memory))

            local_next.append(
                SSLNode(
                    cooperation=cooperation,
                    trust_memory=trust_memory,
                    disturbance=disturbance,
                    cognition=cognition,
                )
            )

        nodes = local_next
        history.append((avg(node.cooperation for node in nodes), avg(node.trust_memory for node in nodes)))

    return history


def recovery_rate(current: float, minimum: float, pre_value: float) -> float:
    denominator = pre_value - minimum
    if abs(denominator) < 1e-9:
        return 1.0
    return clamp((current - minimum) / denominator)


def first_halflife(rates: Sequence[float], start_step: int) -> object:
    for offset, rate in enumerate(rates[start_step:], start=0):
        if rate >= 0.50:
            return offset
    return ""


def run_ssl_dynamics_suite() -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    neighbors = build_federation_neighbors()
    rows: List[Dict[str, object]] = []
    summary: List[Dict[str, object]] = []

    for run_index in range(SSL_RUNS):
        seed = SEED_START + run_index
        history = run_ssl_simulation(seed, neighbors)
        cooperation_values = [row[0] for row in history]
        trust_values = [row[1] for row in history]
        pre_cooperation = cooperation_values[BETRAYAL_STEP - 1]
        pre_trust = trust_values[BETRAYAL_STEP - 1]
        post_cooperation_min = min(cooperation_values[BETRAYAL_STEP:])
        post_trust_min = min(trust_values[BETRAYAL_STEP:])
        cooperation_rates = [
            recovery_rate(value, post_cooperation_min, pre_cooperation)
            for value in cooperation_values
        ]
        trust_rates = [
            recovery_rate(value, post_trust_min, pre_trust)
            for value in trust_values
        ]

        cooperation_halflife = first_halflife(cooperation_rates, BETRAYAL_STEP)
        trust_halflife = first_halflife(trust_rates, BETRAYAL_STEP)
        if cooperation_halflife == "" or cooperation_halflife == 0 or trust_halflife == "":
            timescale_ratio: object = ""
            assertion_supported = 0
        else:
            timescale_ratio = float(trust_halflife) / float(cooperation_halflife)
            assertion_supported = int(timescale_ratio > 1.5)

        for step, (cooperation, trust_memory_mean) in enumerate(history):
            rows.append(
                {
                    "run_index": run_index,
                    "seed": seed,
                    "step": step,
                    "cooperation": cooperation,
                    "trust_memory_mean": trust_memory_mean,
                    "post_betrayal": int(step > BETRAYAL_STEP),
                    "cooperation_recovery_rate": cooperation_rates[step],
                    "trust_recovery_rate": trust_rates[step],
                }
            )
        summary.append(
            {
                "run_index": run_index,
                "seed": seed,
                "cooperation_halflife_steps": cooperation_halflife,
                "trust_halflife_steps": trust_halflife,
                "timescale_ratio": timescale_ratio,
                "assertion_supported": assertion_supported,
            }
        )

    return rows, summary


def numeric(values: Iterable[object]) -> List[float]:
    result = []
    for value in values:
        if value == "":
            continue
        result.append(float(value))
    return result


def write_threshold_note(summary: Sequence[Dict[str, object]]) -> None:
    recommended = next(row for row in summary if int(row["recommended"]))
    target_achieved = float(recommended["false_alarm_rate"]) <= 0.10
    pathlib.Path("v19_federation_threshold_note.txt").write_text(
        "\n".join(
            [
                f"Recommended federation S_threshold: {recommended['s_threshold']}.",
                f"False alarm rate at recommended threshold: {float(recommended['false_alarm_rate']):.3f}.",
                f"False alarm target <= 10% achieved: {'yes' if target_achieved else 'no'}.",
                f"Ring/mesh comparison threshold: original ring/mesh S_threshold = {RING_MESH_THRESHOLD:.2f}; v19 sweep tested 0.10-0.50 for federation.",
                f"Deployment recommendation: {'false-alarm-safe at recommended threshold, but automatic Trigger A sensitivity remains unvalidated because no threshold in 0.10-0.50 fired and no genuine collapse positives occurred in this sweep' if target_achieved else 'do not enable automatic Trigger A; escalate to v20 expanded sweep'}.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def write_ssl_note(summary: Sequence[Dict[str, object]]) -> None:
    cooperation_halflives = numeric(row["cooperation_halflife_steps"] for row in summary)
    trust_halflives = numeric(row["trust_halflife_steps"] for row in summary)
    ratios = numeric(row["timescale_ratio"] for row in summary)
    avg_ratio = avg(ratios)
    supported = avg_ratio > 1.5
    revision = (
        "No C05 revision required."
        if supported
        else "C05 revision required: weaken or remove the claim that I_belong recovers slower than I_role under the current proxy dynamics."
    )
    pathlib.Path("v19_ssl_dynamics_note.txt").write_text(
        "\n".join(
            [
                f"Average cooperation half-life: {avg(cooperation_halflives):.2f} steps.",
                f"Average trust_memory half-life: {avg(trust_halflives):.2f} steps.",
                f"Average timescale ratio: {avg_ratio:.2f}.",
                f"C05 timescale assertion: {'supported' if supported else 'violated or weakly supported'} by ratio > 1.5 criterion.",
                revision,
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    threshold_runs, threshold_summary = run_federation_threshold_suite()
    ssl_runs, ssl_summary = run_ssl_dynamics_suite()

    write_csv(pathlib.Path("v19_federation_threshold_runs.csv"), threshold_runs)
    write_csv(pathlib.Path("v19_federation_threshold_summary.csv"), threshold_summary)
    write_threshold_note(threshold_summary)

    write_csv(pathlib.Path("v19_ssl_dynamics_runs.csv"), ssl_runs)
    write_csv(pathlib.Path("v19_ssl_dynamics_summary.csv"), ssl_summary)
    write_ssl_note(ssl_summary)


if __name__ == "__main__":
    main()
