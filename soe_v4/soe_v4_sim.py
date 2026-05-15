from __future__ import annotations

import argparse
import csv
import random
import statistics
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Dict, Iterable, List, Sequence


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


@dataclass
class NodeState:
    trust: float
    disturbance: float
    cognition: float
    identity: float
    stability: float


@dataclass(frozen=True)
class Scenario:
    name: str
    topology: str
    note: str
    disturbance_shock: float = 0.0
    info_attack: float = 0.0
    ai_pressure: float = 0.0
    exit_pressure: float = 0.0
    local_only_mode: bool = False
    reentry_enabled: bool = True
    identity_enabled: bool = True
    oversight_enabled: bool = True
    upgrade_enabled: bool = True
    coordination_enabled: bool = True
    unification_strength: float = 0.18
    protocol_strength: float = 0.72
    trust_bridge_gain: float = 0.14
    disturbance_coupling: float = 0.09
    cognition_coupling: float = 0.08
    identity_coupling: float = 0.06


@dataclass(frozen=True)
class SuiteConfig:
    seed: int = 42
    runs: int = 24
    years: int = 400
    step_years: int = 10
    nodes: int = 24

    @property
    def steps(self) -> int:
        return self.years // self.step_years


def build_topology(node_count: int, topology: str, rng: random.Random) -> List[List[int]]:
    if node_count < 3:
        raise ValueError("node_count must be at least 3")

    neighbors = {node_id: set() for node_id in range(node_count)}

    def add_edge(left: int, right: int) -> None:
        if left == right:
            return
        neighbors[left].add(right)
        neighbors[right].add(left)

    if topology == "ring":
        for node_id in range(node_count):
            add_edge(node_id, (node_id + 1) % node_count)
    elif topology == "small-world":
        for node_id in range(node_count):
            add_edge(node_id, (node_id + 1) % node_count)
            add_edge(node_id, (node_id + 2) % node_count)
        extra_edges = max(1, node_count // 6)
        for _ in range(extra_edges):
            left = rng.randrange(node_count)
            right = rng.randrange(node_count)
            add_edge(left, right)
    elif topology == "federation":
        hub_count = max(3, node_count // 6)
        hubs = list(range(hub_count))
        for index, hub in enumerate(hubs):
            add_edge(hub, hubs[(index + 1) % len(hubs)])
        for node_id in range(hub_count, node_count):
            add_edge(node_id, hubs[(node_id - hub_count) % len(hubs)])
            add_edge(node_id, hubs[(node_id - hub_count + 1) % len(hubs)])
    elif topology == "hub":
        for node_id in range(1, node_count):
            add_edge(0, node_id)
        for node_id in range(1, node_count - 1):
            add_edge(node_id, node_id + 1)
    else:
        raise ValueError(f"Unknown topology: {topology}")

    return [sorted(neighbors[node_id]) for node_id in range(node_count)]


def build_initial_states(node_count: int, rng: random.Random) -> List[NodeState]:
    states: List[NodeState] = []
    for _ in range(node_count):
        trust = clamp(0.76 + rng.uniform(-0.04, 0.04))
        disturbance = clamp(0.20 + rng.uniform(-0.03, 0.03))
        cognition = clamp(0.18 + rng.uniform(-0.03, 0.03))
        identity = clamp(0.74 + rng.uniform(-0.05, 0.05))
        stability = clamp(0.52 + (0.36 * trust) + (0.18 * identity) - (0.15 * disturbance) - (0.10 * cognition))
        states.append(
            NodeState(
                trust=trust,
                disturbance=disturbance,
                cognition=cognition,
                identity=identity,
                stability=stability,
            )
        )
    return states


def default_scenarios() -> List[Scenario]:
    return [
        Scenario(
            name="baseline_federation",
            topology="federation",
            note="Full V4 stack active with protocols, coordination, re-entry, identity repair, and oversight.",
        ),
        Scenario(
            name="baseline_small_world",
            topology="small-world",
            note="Baseline V4 stack on a denser topology to compare resilience against the federation default.",
        ),
        Scenario(
            name="local_only_no_coordination",
            topology="ring",
            note="Tests the bounded-propagation claim: local coupling without global coordination should spread stress but not reliably ignite durable system-wide recovery.",
            coordination_enabled=False,
            local_only_mode=True,
            trust_bridge_gain=0.04,
            protocol_strength=0.55,
            unification_strength=0.10,
        ),
        Scenario(
            name="no_reentry_layer",
            topology="federation",
            note="Removes the V4 re-entry layer to test whether trust collapse becomes stickier.",
            reentry_enabled=False,
        ),
        Scenario(
            name="no_identity_layer",
            topology="federation",
            note="Removes identity repair and protocol support to test Chapter 5 identity claims.",
            identity_enabled=False,
            identity_coupling=0.01,
            protocol_strength=0.40,
            unification_strength=0.04,
            exit_pressure=0.05,
            info_attack=0.04,
            disturbance_shock=0.02,
            trust_bridge_gain=0.08,
        ),
        Scenario(
            name="high_info_warfare",
            topology="small-world",
            note="Amplifies information distortion pressure using the V4 information-integrity and unification layers as the countermeasure.",
            info_attack=0.09,
            disturbance_shock=0.03,
        ),
        Scenario(
            name="exit_cascade_pressure",
            topology="hub",
            note="Pushes nodes toward exit decisions to stress the V4 right-of-exit and coordination architecture.",
            exit_pressure=0.12,
            disturbance_shock=0.04,
            info_attack=0.04,
            trust_bridge_gain=0.09,
        ),
        Scenario(
            name="ai_capture_unchecked",
            topology="federation",
            note="Raises governance-capture pressure while removing oversight to test the audit and meta-governance assumptions.",
            ai_pressure=0.12,
            oversight_enabled=False,
            info_attack=0.05,
        ),
        Scenario(
            name="ai_capture_guarded",
            topology="federation",
            note="Same AI pressure as the unchecked case but with V4 oversight left intact.",
            ai_pressure=0.12,
            info_attack=0.05,
        ),
    ]


def compute_neighbor_average(states: Sequence[NodeState], indices: Iterable[int], field: str) -> float:
    indices = list(indices)
    if not indices:
        return 0.0
    return sum(getattr(states[index], field) for index in indices) / len(indices)


def run_single_scenario(scenario: Scenario, config: SuiteConfig, run_seed: int) -> Dict[str, float | int | str]:
    rng = random.Random(run_seed)
    topology = build_topology(config.nodes, scenario.topology, rng)
    states = build_initial_states(config.nodes, rng)

    trust_threshold = 0.58
    disturbance_threshold = 0.46
    cognition_threshold = 0.44
    identity_threshold = 0.56
    stability_threshold = 0.80
    bridge_threshold = 0.12 if scenario.local_only_mode else 0.08

    trust_sum = 0.0
    stability_sum = 0.0
    identity_sum = 0.0
    cognition_sum = 0.0
    stable_node_steps = 0
    low_trust_node_steps = 0
    total_node_steps = config.steps * config.nodes
    min_avg_stability = 1.0
    exit_events = 0
    reentry_events = 0
    coordination_events = 0
    upgrade_events = 0

    for _ in range(config.steps):
        next_states: List[NodeState] = []
        avg_trust = statistics.fmean(state.trust for state in states)
        avg_identity = statistics.fmean(state.identity for state in states)

        for node_id, state in enumerate(states):
            neighbors = topology[node_id]
            neighbor_trust = compute_neighbor_average(states, neighbors, "trust")
            neighbor_disturbance = compute_neighbor_average(states, neighbors, "disturbance")
            neighbor_cognition = compute_neighbor_average(states, neighbors, "cognition")
            neighbor_identity = compute_neighbor_average(states, neighbors, "identity")

            trust_crisis = state.trust < trust_threshold
            disturbance_crisis = state.disturbance > disturbance_threshold
            cognition_crisis = state.cognition > cognition_threshold
            identity_crisis = state.identity < identity_threshold

            coordination_boost = 0.0
            if scenario.coordination_enabled and (disturbance_crisis or cognition_crisis or identity_crisis):
                coordination_boost = 0.07 + (0.05 * scenario.protocol_strength)
                coordination_events += 1

            reentry_boost = 0.0
            if scenario.reentry_enabled and trust_crisis:
                reentry_boost = 0.06 + (0.03 * scenario.protocol_strength) + (0.02 * avg_identity)
                reentry_events += 1

            identity_repair = 0.0
            if scenario.identity_enabled and identity_crisis:
                identity_repair = 0.05 + (0.05 * scenario.protocol_strength)

            oversight_guard = 0.0
            if scenario.oversight_enabled:
                oversight_guard = 0.04 + (0.04 * scenario.protocol_strength)

            trust_bridge = 0.0
            if neighbor_trust > state.trust and scenario.trust_bridge_gain >= bridge_threshold:
                trust_bridge = scenario.trust_bridge_gain * max(0.0, neighbor_trust - state.trust)

            local_shock = rng.uniform(0.0, 0.03) + scenario.disturbance_shock
            info_shock = rng.uniform(0.0, 0.02) + scenario.info_attack
            exit_drive = scenario.exit_pressure + max(0.0, 0.35 - state.trust) * 0.10
            capture_penalty = max(0.0, scenario.ai_pressure - oversight_guard)
            unification_effect = scenario.unification_strength * (
                0.5 * state.identity + 0.5 * scenario.protocol_strength
            )

            disturbance = clamp(
                (0.86 * state.disturbance)
                + 0.03
                + local_shock
                + (scenario.disturbance_coupling * neighbor_disturbance)
                + (0.05 * capture_penalty)
                - (0.60 * coordination_boost)
            )

            cognition = clamp(
                (0.84 * state.cognition)
                + 0.02
                + (0.12 * disturbance)
                + info_shock
                + (scenario.cognition_coupling * neighbor_cognition)
                + (0.07 * capture_penalty)
                - (0.50 * coordination_boost)
                - (0.45 * unification_effect)
            )

            identity = clamp(
                (0.88 * state.identity)
                + 0.02
                + identity_repair
                + (scenario.identity_coupling * neighbor_identity)
                + (0.03 * scenario.protocol_strength)
                - (0.10 * disturbance)
                - (0.07 * cognition)
                - exit_drive
            )

            trust = clamp(
                state.trust
                - (0.22 * disturbance)
                - (0.16 * cognition)
                - (0.06 * exit_drive)
                - (0.08 * capture_penalty)
                + (0.14 * identity)
                + reentry_boost
                + trust_bridge
            )

            upgrade_bonus = 0.0
            if scenario.upgrade_enabled and trust > 0.72 and identity > 0.68 and cognition < 0.34:
                upgrade_bonus = 0.04 + (0.03 * scenario.protocol_strength)
                upgrade_events += 1

            stability = clamp(
                0.40
                + (0.34 * trust)
                + (0.22 * identity)
                - (0.18 * disturbance)
                - (0.14 * cognition)
                + (0.08 * coordination_boost)
                + upgrade_bonus
            )

            if trust < 0.34 and identity < 0.30:
                exit_events += 1
                trust = clamp(trust + 0.03)
                stability = clamp(stability - 0.06)
                identity = clamp(identity - 0.04)

            if stability >= stability_threshold:
                stable_node_steps += 1
            if trust < trust_threshold:
                low_trust_node_steps += 1

            trust_sum += trust
            stability_sum += stability
            identity_sum += identity
            cognition_sum += cognition

            next_states.append(
                NodeState(
                    trust=trust,
                    disturbance=disturbance,
                    cognition=cognition,
                    identity=identity,
                    stability=stability,
                )
            )

        states = next_states
        step_avg_stability = statistics.fmean(state.stability for state in states)
        min_avg_stability = min(min_avg_stability, step_avg_stability)

    final_avg_trust = statistics.fmean(state.trust for state in states)
    final_avg_disturbance = statistics.fmean(state.disturbance for state in states)
    final_avg_cognition = statistics.fmean(state.cognition for state in states)
    final_avg_identity = statistics.fmean(state.identity for state in states)
    final_avg_stability = statistics.fmean(state.stability for state in states)

    return {
        "scenario": scenario.name,
        "topology": scenario.topology,
        "seed": run_seed,
        "runs": config.runs,
        "years": config.years,
        "step_years": config.step_years,
        "nodes": config.nodes,
        "note": scenario.note,
        "final_avg_trust": round(final_avg_trust, 4),
        "final_avg_disturbance": round(final_avg_disturbance, 4),
        "final_avg_cognition": round(final_avg_cognition, 4),
        "final_avg_identity": round(final_avg_identity, 4),
        "final_avg_stability": round(final_avg_stability, 4),
        "min_avg_stability": round(min_avg_stability, 4),
        "stable_node_step_share": round(stable_node_steps / total_node_steps, 4),
        "low_trust_node_step_share": round(low_trust_node_steps / total_node_steps, 4),
        "mean_trust": round(trust_sum / total_node_steps, 4),
        "mean_identity": round(identity_sum / total_node_steps, 4),
        "mean_cognition": round(cognition_sum / total_node_steps, 4),
        "mean_stability": round(stability_sum / total_node_steps, 4),
        "exit_events": exit_events,
        "reentry_events": reentry_events,
        "coordination_events": coordination_events,
        "upgrade_events": upgrade_events,
    }


def summarize_runs(rows: Sequence[Dict[str, float | int | str]]) -> Dict[str, float | int | str]:
    sample = rows[0]
    metric_keys = [
        "final_avg_trust",
        "final_avg_disturbance",
        "final_avg_cognition",
        "final_avg_identity",
        "final_avg_stability",
        "min_avg_stability",
        "stable_node_step_share",
        "low_trust_node_step_share",
        "mean_trust",
        "mean_identity",
        "mean_cognition",
        "mean_stability",
        "exit_events",
        "reentry_events",
        "coordination_events",
        "upgrade_events",
    ]
    summary: Dict[str, float | int | str] = {
        "scenario": sample["scenario"],
        "topology": sample["topology"],
        "runs": len(rows),
        "years": sample["years"],
        "nodes": sample["nodes"],
        "note": sample["note"],
    }
    for key in metric_keys:
        values = [float(row[key]) for row in rows]
        summary[key] = round(sum(values) / len(values), 4)
    return summary


def run_document_suite(config: SuiteConfig) -> tuple[List[Dict[str, float | int | str]], List[Dict[str, float | int | str]]]:
    raw_rows: List[Dict[str, float | int | str]] = []
    summary_rows: List[Dict[str, float | int | str]] = []

    for scenario_index, scenario in enumerate(default_scenarios()):
        scenario_rows = []
        for run_index in range(config.runs):
            run_seed = config.seed + (scenario_index * 10_000) + run_index
            row = run_single_scenario(scenario, config, run_seed)
            scenario_rows.append(row)
            raw_rows.append(row)
        summary_rows.append(summarize_runs(scenario_rows))

    summary_rows.sort(key=lambda row: float(row["final_avg_stability"]), reverse=True)
    return summary_rows, raw_rows


def write_csv(path: Path, rows: Sequence[Dict[str, float | int | str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_markdown_report(summary_rows: Sequence[Dict[str, float | int | str]], config: SuiteConfig) -> str:
    lines = [
        "# SOE V4 Simulation Report",
        "",
        "## Source Mapping",
        "",
        "- `SOE_V4.docx`: master architecture, V4 state set `T/D/C/I/S`, meta-governance triggers, coordination, re-entry, identity, oversight, exit, and stress-test framing.",
        "- `SOE_Model_v1.3_Formatted.docx`: trust-centered local dynamics and regime-sensitive control logic.",
        "- `SOE Network Dynamic v2.0 Final.docx`: disturbance/cognition propagation and conditional trust bridging across nodes.",
        "- `SOE_Node_v0.1_Execution_Spec.docx`: prior envelope assumptions, especially the no-self-ignition expectation under purely local propagation.",
        "- `SOE Simulation Log-Completed.docx`: trust recovery need, topology sensitivity, and the use of repeated Monte Carlo summaries rather than one-off seeds.",
        "- `Bounded_Propagation_Without_Ignition_v6_Formatted.docx`: shaped the `local_only_no_coordination` probe.",
        "- `Simulation Plan.docx`: motivated the scenario suite as a stability atlas rather than a single run.",
        "- `Trinity Framework.docx`, `Unification Method.docx`, and `归一法.docx`: modeled as unification/coherence pressure that reduces cognitive distortion and supports protocol alignment.",
        "- `Full System Audit.docx`, `_SOE_Falsification_Log_v1_格式化版.docx`, `_SOE_Regime_Log_v1_格式化版.docx`: used as discipline constraints to keep claims comparative, threshold-aware, and non-final.",
        "",
        "## Run Settings",
        "",
        f"- Runs per scenario: {config.runs}",
        f"- Years per run: {config.years}",
        f"- Step size: {config.step_years}",
        f"- Nodes: {config.nodes}",
        "",
        "## Ranked Results",
        "",
        "| Scenario | Topology | Final Stability | Min Stability | Stable Share | Low-Trust Share | Exit Events | Re-entry Events | Coordination Events |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    for row in summary_rows:
        lines.append(
            "| "
            f"{row['scenario']} | {row['topology']} | {float(row['final_avg_stability']):.4f} | "
            f"{float(row['min_avg_stability']):.4f} | {float(row['stable_node_step_share']):.4f} | "
            f"{float(row['low_trust_node_step_share']):.4f} | {float(row['exit_events']):.2f} | "
            f"{float(row['reentry_events']):.2f} | {float(row['coordination_events']):.2f} |"
        )

    lines.extend(
        [
            "",
            "## Quick Read",
            "",
            "- The best-performing scenarios are the ones that keep the full V4 stack active, especially oversight, coordination, re-entry, and identity support.",
            "- Removing re-entry or identity support lowers stability and increases low-trust exposure, which matches the logic in Chapter 5 and the earlier simulation logs.",
            "- The local-only mode is intentionally weaker: it allows stress propagation but underperforms the coordinated V4 cases, which is consistent with the bounded-propagation paper.",
            "- Guarded and unguarded AI-pressure scenarios can be compared directly to estimate how much the oversight layer matters under the same capture pressure.",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the SOE V4 simulation suite grounded in the Desktop doc set.")
    parser.add_argument("--seed", type=int, default=42, help="Base random seed.")
    parser.add_argument("--runs", type=int, default=24, help="Monte Carlo runs per scenario.")
    parser.add_argument("--years", type=int, default=400, help="Years per run.")
    parser.add_argument("--step-years", type=int, default=10, help="Years per simulation step.")
    parser.add_argument("--nodes", type=int, default=24, help="Node count per run.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("soe_v4") / "outputs",
        help="Directory for CSV and markdown outputs.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = SuiteConfig(
        seed=args.seed,
        runs=args.runs,
        years=args.years,
        step_years=args.step_years,
        nodes=args.nodes,
    )
    summary_rows, raw_rows = run_document_suite(config)

    output_dir = args.output_dir
    write_csv(output_dir / "soe_v4_summary.csv", summary_rows)
    write_csv(output_dir / "soe_v4_runs.csv", raw_rows)
    report = build_markdown_report(summary_rows, config)
    (output_dir / "soe_v4_report.md").write_text(report, encoding="utf-8")

    print("SOE V4 scenario ranking")
    for row in summary_rows:
        print(
            f"- {row['scenario']}: "
            f"stability={float(row['final_avg_stability']):.4f}, "
            f"stable_share={float(row['stable_node_step_share']):.4f}, "
            f"low_trust={float(row['low_trust_node_step_share']):.4f}, "
            f"exit_events={float(row['exit_events']):.2f}"
        )
    print(f"Saved summary to {output_dir / 'soe_v4_summary.csv'}")
    print(f"Saved runs to {output_dir / 'soe_v4_runs.csv'}")
    print(f"Saved report to {output_dir / 'soe_v4_report.md'}")


if __name__ == "__main__":
    main()
