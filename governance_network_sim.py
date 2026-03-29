import argparse
import csv
import pathlib
import random
import statistics
from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

from governance_loop_sim import (
    Config,
    Interventions,
    State,
    activate_interventions,
    apply_overrides,
    choose_governance_response,
    clamp,
    default_parameters,
    drain_due_decisions,
    queue_decision,
    resolve_execution_delay,
    sample_observation,
    smooth_observation,
    step_system,
    summarize_run,
)


@dataclass
class NodeRuntime:
    node_index: int
    state: State
    observed_state: State
    previous_observed_state: State
    interventions: Interventions
    decision_queue: List[Tuple[int, List[str], str]]
    dynamics_rng: random.Random
    execution_rng: random.Random
    observation_rng: random.Random
    history: List[Dict[str, float]]


def build_node_config(overrides: List[str]) -> Config:
    params = default_parameters()
    params.update(
        {
            "intervention_budget": 1.0,
            "execution_delay": 2.0,
            "max_delay": 0.0,
            "alpha": 1.0,
            "noise_level": 0.0,
            "trust_threshold_offset": 0.006,
            "disturbance_threshold_offset": 0.04,
            "compound_sensitivity_offset": 0.05,
            "trust_cap_strength": 1.0,
        }
    )
    params = apply_overrides(params, overrides)
    return Config(**params)


def build_neighbors(node_count: int, coupled: bool) -> List[List[int]]:
    if not coupled:
        return [[] for _ in range(node_count)]
    neighbors: List[List[int]] = []
    for index in range(node_count):
        left = (index - 1) % node_count
        right = (index + 1) % node_count
        neighbors.append(sorted({left, right}))
    return neighbors


def initialize_nodes(config: Config, node_count: int, run_seed: int) -> List[NodeRuntime]:
    nodes: List[NodeRuntime] = []
    init_rng = random.Random(run_seed + 500)
    for node_index in range(node_count):
        state = State(
            trust=clamp(config.initial_trust + init_rng.uniform(-0.03, 0.03)),
            disturbance=clamp(config.initial_disturbance + init_rng.uniform(-0.03, 0.03)),
            stability=clamp(config.initial_stability + init_rng.uniform(-0.02, 0.02)),
            cognitive_distortion=clamp(config.initial_cognitive_distortion + init_rng.uniform(-0.03, 0.03)),
        )
        observed_state = sample_observation(state, config.noise_level, random.Random(run_seed + 20_000 + node_index))
        nodes.append(
            NodeRuntime(
                node_index=node_index,
                state=state,
                observed_state=observed_state,
                previous_observed_state=State(**observed_state.__dict__),
                interventions=Interventions(),
                decision_queue=[],
                dynamics_rng=random.Random(run_seed + node_index),
                execution_rng=random.Random(run_seed + 10_000 + node_index),
                observation_rng=random.Random(run_seed + 20_000 + node_index),
                history=[],
            )
        )
    return nodes


def apply_coupling(
    states: List[State],
    neighbors: Sequence[Sequence[int]],
    k_d: float,
    k_c: float,
    migration_rate: float,
) -> List[State]:
    updated = [State(**state.__dict__) for state in states]

    for node_index, node_neighbors in enumerate(neighbors):
        if not node_neighbors:
            continue
        avg_neighbor_disturbance = sum(states[j].disturbance for j in node_neighbors) / len(node_neighbors)
        avg_neighbor_cognition = sum(states[j].cognitive_distortion for j in node_neighbors) / len(node_neighbors)
        updated[node_index].disturbance = clamp(updated[node_index].disturbance + (k_d * avg_neighbor_disturbance))
        updated[node_index].cognitive_distortion = clamp(
            updated[node_index].cognitive_distortion + (k_c * avg_neighbor_cognition)
        )

    trust_deltas = [0.0 for _ in states]
    seen_edges = set()
    for node_index, node_neighbors in enumerate(neighbors):
        for neighbor_index in node_neighbors:
            edge = tuple(sorted((node_index, neighbor_index)))
            if edge in seen_edges:
                continue
            seen_edges.add(edge)
            stability_gap = updated[neighbor_index].stability - updated[node_index].stability
            if stability_gap > 0.0:
                delta = migration_rate * stability_gap
                trust_deltas[node_index] -= delta
                trust_deltas[neighbor_index] += delta
            elif stability_gap < 0.0:
                delta = migration_rate * (-stability_gap)
                trust_deltas[neighbor_index] -= delta
                trust_deltas[node_index] += delta

    for node_index, trust_delta in enumerate(trust_deltas):
        updated[node_index].trust = clamp(updated[node_index].trust + trust_delta)

    return updated


def run_network(config: Config, node_count: int, steps: int, run_seed: int, coupled: bool, k_d: float, k_c: float, migration_rate: float) -> Tuple[List[NodeRuntime], Dict[str, float]]:
    nodes = initialize_nodes(config, node_count=node_count, run_seed=run_seed)
    neighbors = build_neighbors(node_count, coupled=coupled)

    for step in range(steps):
        local_next_states: List[State] = []
        step_extras: List[Dict[str, float]] = []
        executed_action_counts: List[int] = []
        executed_decision_labels: List[str] = []
        sampled_delays: List[int] = []

        for node in nodes:
            actions, decision = choose_governance_response(node.observed_state, node.previous_observed_state, config)
            sampled_delay = resolve_execution_delay(config, node.execution_rng)
            queue_decision(node.decision_queue, step, sampled_delay, actions, decision)
            node.decision_queue, executed_actions, executed_decisions = drain_due_decisions(node.decision_queue, step)
            node.interventions = activate_interventions(node.interventions, executed_actions, config)
            next_state, extras = step_system(node.state, node.interventions, config, node.dynamics_rng)

            local_next_states.append(next_state)
            step_extras.append(extras)
            executed_action_counts.append(len(executed_actions))
            executed_decision_labels.append("|".join(executed_decisions) if executed_decisions else "idle")
            sampled_delays.append(sampled_delay)

        if coupled:
            coupled_next_states = apply_coupling(
                local_next_states,
                neighbors=neighbors,
                k_d=k_d,
                k_c=k_c,
                migration_rate=migration_rate,
            )
        else:
            coupled_next_states = local_next_states

        step_stabilities = [state.stability for state in coupled_next_states]
        step_variance = statistics.pvariance(step_stabilities) if len(step_stabilities) > 1 else 0.0

        for node, next_state, extras, executed_count, executed_label, sampled_delay in zip(
            nodes,
            coupled_next_states,
            step_extras,
            executed_action_counts,
            executed_decision_labels,
            sampled_delays,
        ):
            sampled_observation = sample_observation(next_state, config.noise_level, node.observation_rng)
            next_observed_state = smooth_observation(sampled_observation, node.observed_state, config.alpha)
            intervention_total = (
                node.interventions.disturbance_damping
                + node.interventions.cognitive_filtering
                + node.interventions.trust_recovery
                + node.interventions.reinforcement
            )
            node.history.append(
                {
                    "step": step,
                    "node_index": node.node_index,
                    "trust": next_state.trust,
                    "disturbance": next_state.disturbance,
                    "stability": next_state.stability,
                    "cognitive_distortion": next_state.cognitive_distortion,
                    "trust_filtered": next_observed_state.trust,
                    "disturbance_filtered": next_observed_state.disturbance,
                    "cognitive_distortion_filtered": next_observed_state.cognitive_distortion,
                    "disturbance_damping": node.interventions.disturbance_damping,
                    "cognitive_filtering": node.interventions.cognitive_filtering,
                    "trust_recovery": node.interventions.trust_recovery,
                    "reinforcement": node.interventions.reinforcement,
                    "intervention_total": intervention_total,
                    "executed_action_count": executed_count,
                    "executed_decisions": executed_label,
                    "sampled_delay": sampled_delay,
                    "node_stability_variance": step_variance,
                    **extras,
                }
            )
            node.previous_observed_state = State(**node.observed_state.__dict__)
            node.observed_state = next_observed_state
            node.state = next_state

    node_summaries = [summarize_run(node.history, threshold=config.stability_threshold) for node in nodes]
    final_stabilities = [float(summary["final_stability"]) for summary in node_summaries]
    summary = {
        "avg_final_stability": sum(final_stabilities) / len(final_stabilities),
        "avg_stability_rate": sum(float(summary["stability_rate"]) for summary in node_summaries) / len(node_summaries),
        "node_failures": sum(int(summary["failure_case"]) for summary in node_summaries),
        "node_recoveries": sum(int(summary["recovered_run"]) for summary in node_summaries),
        "stability_variance": statistics.pvariance(final_stabilities) if len(final_stabilities) > 1 else 0.0,
    }
    return nodes, summary


def aggregate_network_histories(all_runs: List[List[NodeRuntime]], threshold: float) -> List[Dict[str, float]]:
    aggregated: List[Dict[str, float]] = []
    steps = len(all_runs[0][0].history)
    for step in range(steps):
        rows = []
        variances = []
        for nodes in all_runs:
            step_rows = [node.history[step] for node in nodes]
            rows.extend(step_rows)
            variances.append(step_rows[0]["node_stability_variance"])
        aggregated.append(
            {
                "step": step,
                "avg_trust": sum(row["trust"] for row in rows) / len(rows),
                "avg_disturbance": sum(row["disturbance"] for row in rows) / len(rows),
                "avg_stability": sum(row["stability"] for row in rows) / len(rows),
                "avg_cognitive_distortion": sum(row["cognitive_distortion"] for row in rows) / len(rows),
                "avg_intervention_total": sum(row["intervention_total"] for row in rows) / len(rows),
                "stability_share": sum(1 for row in rows if row["stability"] >= threshold) / len(rows),
                "avg_node_stability_variance": sum(variances) / len(variances),
            }
        )
    return aggregated


def write_csv(path: pathlib.Path, rows: List[Dict[str, float]]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a minimal multi-node extension of the governance loop simulation."
    )
    parser.add_argument("--nodes", type=int, default=5, help="Number of nodes in the network.")
    parser.add_argument("--steps", type=int, default=100, help="Number of time steps per run.")
    parser.add_argument("--runs", type=int, default=20, help="Number of randomized runs per scenario.")
    parser.add_argument("--seed", type=int, default=42, help="Base random seed.")
    parser.add_argument("--k-d", type=float, default=0.05, help="Disturbance propagation strength.")
    parser.add_argument("--k-c", type=float, default=0.05, help="Cognitive spread strength.")
    parser.add_argument("--migration-rate", type=float, default=0.02, help="Trust migration strength.")
    parser.add_argument("--output-prefix", type=pathlib.Path, default=pathlib.Path("governance_network"), help="Output file prefix.")
    parser.add_argument(
        "--override",
        action="append",
        default=[],
        help="Override node-level parameters using name=value or comma-separated pairs.",
    )
    return parser


def main() -> None:
    parser = build_argument_parser()
    args = parser.parse_args()
    config = build_node_config(args.override)

    scenarios = [
        ("isolated", False),
        ("coupled", True),
    ]
    results = []

    for scenario_name, coupled in scenarios:
        scenario_runs: List[Dict[str, float]] = []
        all_run_nodes: List[List[NodeRuntime]] = []
        for run_index in range(args.runs):
            nodes, summary = run_network(
                config,
                node_count=args.nodes,
                steps=args.steps,
                run_seed=args.seed + run_index,
                coupled=coupled,
                k_d=args.k_d,
                k_c=args.k_c,
                migration_rate=args.migration_rate,
            )
            all_run_nodes.append(nodes)
            scenario_runs.append(
                {
                    "run_index": run_index,
                    "seed": args.seed + run_index,
                    "scenario": scenario_name,
                    **summary,
                }
            )

        avg_network_stability = sum(row["avg_final_stability"] for row in scenario_runs) / len(scenario_runs)
        avg_stability_rate = sum(row["avg_stability_rate"] for row in scenario_runs) / len(scenario_runs)
        avg_node_failures = sum(row["node_failures"] for row in scenario_runs) / len(scenario_runs)
        avg_node_variance = sum(row["stability_variance"] for row in scenario_runs) / len(scenario_runs)
        results.append(
            {
                "scenario": scenario_name,
                "avg_final_stability": avg_network_stability,
                "avg_stability_rate": avg_stability_rate,
                "avg_node_failures": avg_node_failures,
                "avg_stability_variance": avg_node_variance,
            }
        )

        runs_path = args.output_prefix.with_name(f"{args.output_prefix.name}_{scenario_name}_runs.csv")
        history_path = args.output_prefix.with_name(f"{args.output_prefix.name}_{scenario_name}_history.csv")
        write_csv(runs_path, scenario_runs)
        write_csv(history_path, aggregate_network_histories(all_run_nodes, threshold=config.stability_threshold))

    summary_path = args.output_prefix.with_name(f"{args.output_prefix.name}_summary.csv")
    write_csv(summary_path, results)

    print("Governance network summary")
    print(f"Nodes: {args.nodes}")
    print(f"Runs per scenario: {args.runs}")
    print(f"Steps: {args.steps}")
    for row in results:
        print(
            f"{row['scenario']}: avg final stability={row['avg_final_stability']:.3f}, "
            f"avg stability rate={row['avg_stability_rate']:.3f}, "
            f"avg node failures={row['avg_node_failures']:.2f}, "
            f"avg stability variance={row['avg_stability_variance']:.4f}"
        )
    print(f"Saved summary to {summary_path}")


if __name__ == "__main__":
    main()
