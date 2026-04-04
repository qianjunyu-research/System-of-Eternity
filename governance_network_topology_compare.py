import argparse
import pathlib
import random
import statistics
from collections import deque
from typing import Dict, List, Sequence, Tuple

from governance_loop_sim import (
    State,
    activate_interventions,
    drain_due_decisions,
    resolve_execution_delay,
    sample_observation,
    smooth_observation,
)
from governance_network_chain_extended import (
    average_failure_rate,
    average_largest_survival_cluster,
    average_time_to_collapse,
    characterize_spatial_behavior,
    distribution_string,
)
from governance_network_chain_sweep import measure_run_metrics, write_csv_union
from governance_network_sim import apply_coupling, apply_intrinsic_decay, build_node_config, initialize_nodes
from governance_loop_sim import choose_governance_response, queue_decision, step_system
from soe_v3.soe_v3_topology import build_phase1_topology


TOPOLOGIES = ("chain", "star", "random-sparse", "fully-connected")
TOPOLOGY_ALIASES = {
    "chain": "chain",
    "star": "star",
    "random": "random-sparse",
    "random-sparse": "random-sparse",
    "fully-connected": "fully-connected",
    "fully connected": "fully-connected",
    "fully_connected": "fully-connected",
}


def parse_float_list(raw_value: str) -> Tuple[float, ...]:
    values = []
    for part in raw_value.split(","):
        stripped = part.strip()
        if not stripped:
            continue
        values.append(float(stripped))
    if not values:
        raise ValueError("Expected at least one numeric value.")
    return tuple(values)


def normalize_topologies(raw_value: str) -> Tuple[str, ...]:
    values = []
    for part in raw_value.split(","):
        stripped = part.strip().lower()
        if not stripped:
            continue
        normalized = TOPOLOGY_ALIASES.get(stripped)
        if normalized is None:
            raise ValueError(
                f"Unsupported topology '{part}'. Expected one of {sorted(TOPOLOGY_ALIASES)}."
            )
        values.append(normalized)
    if not values:
        raise ValueError("Expected at least one topology.")
    return tuple(values)


def graph_to_neighbors(graph) -> List[List[int]]:
    return [sorted(graph.neighbors(node_id)) for node_id in sorted(graph.adjacency)]


def inject_origin_disturbance(nodes, amount: float) -> None:
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


def shortest_path_distances(graph, origin_index: int = 0) -> Dict[int, int]:
    distances = {origin_index: 0}
    queue = deque([origin_index])
    while queue:
        current = queue.popleft()
        for neighbor in graph.neighbors(current):
            if neighbor in distances:
                continue
            distances[neighbor] = distances[current] + 1
            queue.append(neighbor)
    return distances


def classify_spatial_distribution(graph, affected_indices: Sequence[int], origin_index: int = 0) -> str:
    if not affected_indices:
        return "localized"
    distances = shortest_path_distances(graph, origin_index=origin_index)
    affected_distances = [distances[index] for index in affected_indices if index in distances]
    if not affected_distances:
        return "localized"
    max_distance = max(affected_distances)
    mean_distance = sum(affected_distances) / len(affected_distances)
    if max_distance <= 1:
        return "hub_localized"
    if mean_distance <= max_distance * 0.4:
        return "core_weighted"
    return "network_wide"


def run_topology_network(
    *,
    topology: str,
    node_count: int,
    steps: int,
    run_seed: int,
    k_d: float,
    k_c: float,
    k_t: float,
    origin_injection: float,
    random_edge_probability: float,
    overrides: List[str],
    intrinsic_decay: float = 0.0,
) -> Dict[str, float | int | str]:
    config = build_node_config(overrides)
    nodes = initialize_nodes(config, node_count=node_count, run_seed=run_seed)
    graph = build_phase1_topology(
        topology,
        list(range(node_count)),
        random.Random(run_seed),
        random_edge_probability=random_edge_probability,
    )
    neighbors = graph_to_neighbors(graph)
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
        coupled_next_states = apply_intrinsic_decay(
            coupled_next_states,
            [node.state for node in nodes],
            intrinsic_decay,
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
    affected_indices = [
        index
        for index, node in enumerate(nodes)
        if any(row["stability"] < config.stability_threshold for row in node.history)
    ]
    metrics["spatial_distribution"] = classify_spatial_distribution(graph, affected_indices, origin_index=0)
    metrics["edge_count"] = graph.number_of_edges()
    return metrics


def run_topology_comparison(
    *,
    runs: int,
    seed: int,
    steps: int,
    node_count: int,
    origin_injection: float,
    random_edge_probability: float,
    overrides: List[str],
    topologies: Sequence[str] = TOPOLOGIES,
    k_d: float = 0.05,
    k_c_values: Sequence[float] = (0.05, 0.10),
    k_t: float = 0.02,
    intrinsic_decay_values: Sequence[float] = (0.0,),
) -> Tuple[List[Dict[str, float | int | str]], List[Dict[str, float | int | str]]]:
    raw_rows: List[Dict[str, float | int | str]] = []
    summary_rows: List[Dict[str, float | int | str]] = []

    for topology in topologies:
        for k_c in k_c_values:
            for intrinsic_decay in intrinsic_decay_values:
                combination_rows: List[Dict[str, float | int | str]] = []
                for run_index in range(runs):
                    metrics = run_topology_network(
                        topology=topology,
                        node_count=node_count,
                        steps=steps,
                        run_seed=seed + run_index,
                        k_d=k_d,
                        k_c=k_c,
                        k_t=k_t,
                        origin_injection=origin_injection,
                        random_edge_probability=random_edge_probability,
                        overrides=overrides,
                        intrinsic_decay=intrinsic_decay,
                    )
                    row = {
                        "topology": topology,
                        "chain_length": node_count,
                        "k_D": k_d,
                        "k_C": k_c,
                        "k_T": k_t,
                        "intrinsic_decay": intrinsic_decay,
                        "run_index": run_index,
                        "seed": seed + run_index,
                        **metrics,
                    }
                    raw_rows.append(row)
                    combination_rows.append(row)

                last_affected_values = [int(row["last_affected_node"]) for row in combination_rows]
                propagated_runs = sum(int(row["propagated"]) for row in combination_rows)
                distribution_counts: Dict[str, int] = {}
                for row in combination_rows:
                    label = str(row["spatial_distribution"])
                    distribution_counts[label] = distribution_counts.get(label, 0) + 1

                summary_rows.append(
                    {
                        "topology": topology,
                        "node_count": node_count,
                        "k_D": k_d,
                        "k_C": k_c,
                        "k_T": k_t,
                        "intrinsic_decay": intrinsic_decay,
                        "runs": runs,
                        "steps": steps,
                        "avg_edge_count": sum(float(row["edge_count"]) for row in combination_rows) / runs,
                        "propagation_share": propagated_runs / runs,
                        "avg_failure_rate": average_failure_rate(combination_rows),
                        "avg_time_to_first_propagation": average_time_to_collapse(combination_rows),
                        "avg_largest_survival_cluster": average_largest_survival_cluster(combination_rows),
                        "max_last_affected_node": max(last_affected_values, default=0),
                        "cascade_depth_distribution": distribution_string(
                            [int(row["cascade_depth"]) for row in combination_rows]
                        ),
                        "last_affected_distribution": distribution_string(last_affected_values),
                        "spatial_distribution_counts": "|".join(
                            f"{key}:{distribution_counts[key]}"
                            for key in sorted(distribution_counts)
                        ),
                        "spatial_behavior": characterize_spatial_behavior(
                            node_count=node_count,
                            propagation_share=propagated_runs / runs,
                            last_affected_values=last_affected_values,
                        ),
                    }
                )

    return summary_rows, raw_rows


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare topology effects under fixed governance propagation parameters."
    )
    parser.add_argument("--runs", type=int, default=20, help="Number of runs per configuration.")
    parser.add_argument("--seed", type=int, default=42, help="Base random seed.")
    parser.add_argument("--steps", type=int, default=200, help="Number of time steps per run.")
    parser.add_argument("--nodes", type=int, default=50, help="Number of nodes in the network.")
    parser.add_argument("--origin-injection", type=float, default=0.48, help="Initial disturbance injected into node 0.")
    parser.add_argument("--k-d", type=float, default=0.05, help="Disturbance propagation strength.")
    parser.add_argument(
        "--k-c-values",
        default="0.05,0.10",
        help="Comma-separated cognition propagation strengths.",
    )
    parser.add_argument("--k-t", type=float, default=0.02, help="Trust / migration propagation strength.")
    parser.add_argument(
        "--intrinsic-decay-values",
        default="0.00",
        help="Comma-separated intrinsic decay values applied after the network update.",
    )
    parser.add_argument(
        "--topologies",
        default="chain,star,random-sparse,fully-connected",
        help="Comma-separated topology list. Supports aliases like 'random' and 'fully connected'.",
    )
    parser.add_argument("--random-edge-probability", type=float, default=0.06, help="Extra edge probability for the random sparse graph.")
    parser.add_argument(
        "--output-prefix",
        type=pathlib.Path,
        default=pathlib.Path("governance_topology_compare"),
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
    topologies = normalize_topologies(args.topologies)
    k_c_values = parse_float_list(args.k_c_values)
    intrinsic_decay_values = parse_float_list(args.intrinsic_decay_values)

    summary_rows, raw_rows = run_topology_comparison(
        runs=args.runs,
        seed=args.seed,
        steps=args.steps,
        node_count=args.nodes,
        origin_injection=args.origin_injection,
        random_edge_probability=args.random_edge_probability,
        overrides=args.override,
        topologies=topologies,
        k_d=args.k_d,
        k_c_values=k_c_values,
        k_t=args.k_t,
        intrinsic_decay_values=intrinsic_decay_values,
    )

    summary_path = args.output_prefix.with_name(f"{args.output_prefix.name}_summary.csv")
    runs_path = args.output_prefix.with_name(f"{args.output_prefix.name}_runs.csv")
    write_csv_union(summary_path, summary_rows)
    write_csv_union(runs_path, raw_rows)

    print("Topology comparison summary")
    for row in summary_rows:
        collapse = "n/a" if float(row["avg_time_to_first_propagation"]) < 0 else f"{float(row['avg_time_to_first_propagation']):.2f}"
        print(
            f"{row['topology']} / k_C={float(row['k_C']):.2f} / decay={float(row['intrinsic_decay']):.2f}: "
            f"share={float(row['propagation_share']):.2f}, "
            f"failure={float(row['avg_failure_rate']):.3f}, "
            f"collapse={collapse}, "
            f"largest_cluster={float(row['avg_largest_survival_cluster']):.2f}, "
            f"spatial={row['spatial_distribution_counts']}"
        )
    print(f"Saved summary to {summary_path}")
    print(f"Saved runs to {runs_path}")


if __name__ == "__main__":
    main()
