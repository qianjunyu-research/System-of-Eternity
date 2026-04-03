import argparse
import csv
import pathlib
import random
import statistics
from typing import Dict, List, Optional, Sequence, Tuple

from governance_loop_sim import (
    State,
    activate_interventions,
    apply_overrides,
    default_parameters,
    drain_due_decisions,
    resolve_execution_delay,
    sample_observation,
    smooth_observation,
    summarize_run,
)
from governance_network_sim import NodeRuntime, apply_coupling, build_node_config, initialize_nodes
from governance_loop_sim import choose_governance_response, queue_decision, step_system


def build_chain_neighbors(node_count: int) -> List[List[int]]:
    neighbors: List[List[int]] = []
    for index in range(node_count):
        node_neighbors: List[int] = []
        if index > 0:
            node_neighbors.append(index - 1)
        if index < node_count - 1:
            node_neighbors.append(index + 1)
        neighbors.append(node_neighbors)
    return neighbors


def inject_origin_disturbance(nodes: Sequence[NodeRuntime], amount: float) -> None:
    if not nodes or amount <= 0.0:
        return
    origin = nodes[0]
    origin.state = State(
        trust=origin.state.trust,
        disturbance=min(1.0, origin.state.disturbance + amount),
        stability=origin.state.stability,
        cognitive_distortion=origin.state.cognitive_distortion,
    )
    origin.observed_state = State(
        trust=origin.observed_state.trust,
        disturbance=min(1.0, origin.observed_state.disturbance + amount),
        stability=origin.observed_state.stability,
        cognitive_distortion=origin.observed_state.cognitive_distortion,
    )


def write_csv_union(path: pathlib.Path, rows: List[Dict[str, float | int | str]]) -> None:
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
        for row in rows:
            writer.writerow(row)


def contiguous_cluster_sizes(node_count: int, excluded_indices: Sequence[int]) -> List[int]:
    excluded = set(excluded_indices)
    cluster_sizes: List[int] = []
    current = 0
    for index in range(node_count):
        if index in excluded:
            if current:
                cluster_sizes.append(current)
                current = 0
            continue
        current += 1
    if current:
        cluster_sizes.append(current)
    return cluster_sizes


def measure_run_metrics(
    nodes: Sequence[NodeRuntime],
    *,
    threshold: float,
    origin_index: int = 0,
) -> Dict[str, float | int]:
    summaries = [summarize_run(node.history, threshold=threshold) for node in nodes]
    failed_indices = [
        index
        for index, summary in enumerate(summaries)
        if int(summary["failure_case"])
    ]
    affected_indices = [
        index
        for index, summary in enumerate(summaries)
        if summary["first_breach_step"] != ""
    ]
    failure_rate = len(failed_indices) / len(nodes) if nodes else 0.0
    cascade_depth = max((abs(index - origin_index) for index in affected_indices), default=0)
    last_affected_node = max(affected_indices, default=origin_index)
    survival_cluster_sizes = contiguous_cluster_sizes(len(nodes), affected_indices)

    time_to_collapse: Optional[int] = None
    for step in range(len(nodes[0].history) if nodes else 0):
        propagated_failure = any(
            nodes[index].history[step]["stability"] < threshold
            for index in range(len(nodes))
            if index != origin_index
        )
        if propagated_failure:
            time_to_collapse = int(nodes[0].history[step]["step"])
            break

    return {
        "failure_rate": failure_rate,
        "cascade_depth": cascade_depth,
        "time_to_collapse": -1 if time_to_collapse is None else time_to_collapse,
        "propagated": int(any(index != origin_index for index in affected_indices)),
        "last_affected_node": last_affected_node,
        "survival_cluster_sizes": "|".join(str(size) for size in survival_cluster_sizes),
    }


def run_chain_network(
    *,
    config,
    node_count: int,
    steps: int,
    run_seed: int,
    k_d: float,
    k_c: float,
    k_t: float,
    origin_injection: float,
) -> Tuple[List[NodeRuntime], Dict[str, float | int]]:
    nodes = initialize_nodes(config, node_count=node_count, run_seed=run_seed)
    neighbors = build_chain_neighbors(node_count)
    inject_origin_disturbance(nodes, origin_injection)

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

        coupled_next_states = apply_coupling(
            local_next_states,
            neighbors=neighbors,
            k_d=k_d,
            k_c=k_c,
            migration_rate=k_t,
        )

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

    metrics = measure_run_metrics(nodes, threshold=config.stability_threshold, origin_index=0)
    return nodes, metrics


def average_time_to_collapse(rows: Sequence[Dict[str, float | int]]) -> float:
    collapses = [float(row["time_to_collapse"]) for row in rows if int(row["time_to_collapse"]) >= 0]
    if not collapses:
        return -1.0
    return sum(collapses) / len(collapses)


def run_parameter_sweep(
    *,
    node_count: int,
    steps: int,
    runs: int,
    seed: int,
    origin_injection: float,
    overrides: List[str],
) -> Tuple[List[Dict[str, float | int]], List[Dict[str, float | int]]]:
    config = build_node_config(overrides)

    summary_rows: List[Dict[str, float | int]] = []
    raw_rows: List[Dict[str, float | int]] = []
    k_d_values = (0.05, 0.10, 0.15, 0.20)
    k_c_values = (0.05, 0.10, 0.15, 0.20)
    k_t_values = (0.00, 0.02, 0.05, 0.10)

    for k_d in k_d_values:
        for k_c in k_c_values:
            for k_t in k_t_values:
                combination_rows: List[Dict[str, float | int]] = []
                for run_index in range(runs):
                    _, metrics = run_chain_network(
                        config=config,
                        node_count=node_count,
                        steps=steps,
                        run_seed=seed + run_index,
                        k_d=k_d,
                        k_c=k_c,
                        k_t=k_t,
                        origin_injection=origin_injection,
                    )
                    row = {
                        "topology": "chain",
                        "run_index": run_index,
                        "seed": seed + run_index,
                        "k_D": k_d,
                        "k_C": k_c,
                        "k_T": k_t,
                        **metrics,
                    }
                    raw_rows.append(row)
                    combination_rows.append(row)

                propagated_runs = sum(int(row["propagated"]) for row in combination_rows)
                summary_rows.append(
                    {
                        "topology": "chain",
                        "k_D": k_d,
                        "k_C": k_c,
                        "k_T": k_t,
                        "runs": runs,
                        "avg_failure_rate": sum(float(row["failure_rate"]) for row in combination_rows) / runs,
                        "avg_cascade_depth": sum(float(row["cascade_depth"]) for row in combination_rows) / runs,
                        "avg_time_to_collapse": average_time_to_collapse(combination_rows),
                        "propagated_runs": propagated_runs,
                        "propagation_share": propagated_runs / runs,
                        "near_threshold": int(0 < propagated_runs < runs),
                    }
                )

    return summary_rows, raw_rows


def near_threshold_rows(summary_rows: Sequence[Dict[str, float | int]]) -> List[Dict[str, float | int]]:
    return sorted(
        (
            row
            for row in summary_rows
            if int(row["near_threshold"]) == 1
        ),
        key=lambda row: (
            abs(float(row["propagation_share"]) - 0.5),
            -float(row["avg_cascade_depth"]),
            float(row["avg_failure_rate"]),
        ),
    )


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a chain-topology propagation sweep across k_D, k_C, and k_T."
    )
    parser.add_argument("--nodes", type=int, default=5, help="Number of nodes in the chain.")
    parser.add_argument("--steps", type=int, default=100, help="Number of time steps per run.")
    parser.add_argument("--runs", type=int, default=20, help="Number of runs per parameter combination.")
    parser.add_argument("--seed", type=int, default=42, help="Base random seed.")
    parser.add_argument("--origin-injection", type=float, default=0.48, help="Initial disturbance injected into node 0.")
    parser.add_argument(
        "--output-prefix",
        type=pathlib.Path,
        default=pathlib.Path("governance_chain_sweep"),
        help="Output file prefix.",
    )
    parser.add_argument(
        "--override",
        action="append",
        default=[],
        help="Override baseline parameters using name=value or comma-separated pairs.",
    )
    return parser


def main() -> None:
    parser = build_argument_parser()
    args = parser.parse_args()

    summary_rows, raw_rows = run_parameter_sweep(
        node_count=args.nodes,
        steps=args.steps,
        runs=args.runs,
        seed=args.seed,
        origin_injection=args.origin_injection,
        overrides=args.override,
    )

    summary_path = args.output_prefix.with_name(f"{args.output_prefix.name}_summary.csv")
    runs_path = args.output_prefix.with_name(f"{args.output_prefix.name}_runs.csv")
    near_threshold_path = args.output_prefix.with_name(f"{args.output_prefix.name}_near_threshold.csv")
    write_csv_union(summary_path, summary_rows)
    write_csv_union(runs_path, raw_rows)
    threshold_rows = near_threshold_rows(summary_rows)
    write_csv_union(near_threshold_path, threshold_rows)

    print("Chain propagation sweep summary")
    print(f"Nodes: {args.nodes}")
    print(f"Runs per combination: {args.runs}")
    print(f"Origin injection: {args.origin_injection:.2f}")
    print(f"Near-threshold combinations: {len(threshold_rows)}")
    for row in threshold_rows[:10]:
        collapse = "n/a" if float(row["avg_time_to_collapse"]) < 0 else f"{float(row['avg_time_to_collapse']):.2f}"
        print(
            f"k_D={float(row['k_D']):.2f}, "
            f"k_C={float(row['k_C']):.2f}, "
            f"k_T={float(row['k_T']):.2f}: "
            f"share={float(row['propagation_share']):.2f}, "
            f"depth={float(row['avg_cascade_depth']):.2f}, "
            f"failure={float(row['avg_failure_rate']):.3f}, "
            f"collapse={collapse}"
        )
    print(f"Saved summary to {summary_path}")
    print(f"Saved runs to {runs_path}")
    print(f"Saved near-threshold rows to {near_threshold_path}")


if __name__ == "__main__":
    main()
