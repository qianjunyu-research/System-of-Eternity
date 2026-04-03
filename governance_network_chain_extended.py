import argparse
import pathlib
from typing import Dict, List, Sequence, Tuple

from governance_network_chain_sweep import run_chain_network, write_csv_union
from governance_network_sim import build_node_config


def distribution_string(values: Sequence[int]) -> str:
    return "|".join(str(value) for value in values)


def average_time_to_collapse(rows: Sequence[Dict[str, float | int | str]]) -> float:
    collapse_values = [float(row["time_to_collapse"]) for row in rows if int(row["time_to_collapse"]) >= 0]
    if not collapse_values:
        return -1.0
    return sum(collapse_values) / len(collapse_values)


def average_failure_rate(rows: Sequence[Dict[str, float | int | str]]) -> float:
    return sum(float(row["failure_rate"]) for row in rows) / len(rows) if rows else 0.0


def average_largest_survival_cluster(rows: Sequence[Dict[str, float | int | str]]) -> float:
    largest_clusters = []
    for row in rows:
        sizes = [int(part) for part in str(row["survival_cluster_sizes"]).split("|") if part]
        largest_clusters.append(max(sizes, default=0))
    return sum(largest_clusters) / len(largest_clusters) if largest_clusters else 0.0


def characterize_spatial_behavior(
    *,
    node_count: int,
    propagation_share: float,
    last_affected_values: Sequence[int],
) -> str:
    max_last = max(last_affected_values, default=0)
    median_like = sorted(last_affected_values)[len(last_affected_values) // 2] if last_affected_values else 0
    if propagation_share < 0.35 and max_last <= max(2, node_count // 10):
        return "decays_early"
    if max_last >= node_count - 1 or median_like >= int(node_count * 0.6):
        return "expands_far"
    return "stabilizes_midchain"


def run_extended_experiment(
    *,
    runs: int,
    seed: int,
    steps: int,
    origin_injection: float,
    overrides: List[str],
) -> Tuple[List[Dict[str, float | int | str]], List[Dict[str, float | int | str]]]:
    config = build_node_config(overrides)
    raw_rows: List[Dict[str, float | int | str]] = []
    summary_rows: List[Dict[str, float | int | str]] = []

    node_counts = (20, 50)
    k_d = 0.05
    k_c_values = (0.05, 0.10)
    k_t_values = (0.00, 0.02, 0.05)

    for node_count in node_counts:
        for k_c in k_c_values:
            for k_t in k_t_values:
                combination_rows: List[Dict[str, float | int | str]] = []
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
                        "chain_length": node_count,
                        "k_D": k_d,
                        "k_C": k_c,
                        "k_T": k_t,
                        "run_index": run_index,
                        "seed": seed + run_index,
                        **metrics,
                    }
                    raw_rows.append(row)
                    combination_rows.append(row)

                cascade_depths = [int(row["cascade_depth"]) for row in combination_rows]
                last_affected_values = [int(row["last_affected_node"]) for row in combination_rows]
                propagated_runs = sum(int(row["propagated"]) for row in combination_rows)
                propagation_share = propagated_runs / runs
                summary_rows.append(
                    {
                        "topology": "chain",
                        "chain_length": node_count,
                        "k_D": k_d,
                        "k_C": k_c,
                        "k_T": k_t,
                        "runs": runs,
                        "steps": steps,
                        "avg_failure_rate": average_failure_rate(combination_rows),
                        "avg_time_to_collapse": average_time_to_collapse(combination_rows),
                        "propagated_runs": propagated_runs,
                        "propagation_share": propagation_share,
                        "avg_largest_survival_cluster": average_largest_survival_cluster(combination_rows),
                        "max_last_affected_node": max(last_affected_values, default=0),
                        "cascade_depth_distribution": distribution_string(cascade_depths),
                        "last_affected_distribution": distribution_string(last_affected_values),
                        "spatial_behavior": characterize_spatial_behavior(
                            node_count=node_count,
                            propagation_share=propagation_share,
                            last_affected_values=last_affected_values,
                        ),
                    }
                )

    return summary_rows, raw_rows


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the extended spatial chain propagation experiment."
    )
    parser.add_argument("--runs", type=int, default=20, help="Number of runs per configuration.")
    parser.add_argument("--seed", type=int, default=42, help="Base random seed.")
    parser.add_argument("--steps", type=int, default=200, help="Number of time steps per run.")
    parser.add_argument("--origin-injection", type=float, default=0.48, help="Initial disturbance injected into node 0.")
    parser.add_argument(
        "--output-prefix",
        type=pathlib.Path,
        default=pathlib.Path("governance_chain_extended"),
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

    summary_rows, raw_rows = run_extended_experiment(
        runs=args.runs,
        seed=args.seed,
        steps=args.steps,
        origin_injection=args.origin_injection,
        overrides=args.override,
    )

    summary_path = args.output_prefix.with_name(f"{args.output_prefix.name}_summary.csv")
    runs_path = args.output_prefix.with_name(f"{args.output_prefix.name}_runs.csv")
    write_csv_union(summary_path, summary_rows)
    write_csv_union(runs_path, raw_rows)

    print("Extended chain propagation summary")
    for row in summary_rows:
        collapse = "n/a" if float(row["avg_time_to_collapse"]) < 0 else f"{float(row['avg_time_to_collapse']):.2f}"
        print(
            f"L={int(row['chain_length'])}, k_C={float(row['k_C']):.2f}, k_T={float(row['k_T']):.2f}: "
            f"share={float(row['propagation_share']):.2f}, "
            f"failure={float(row['avg_failure_rate']):.3f}, "
            f"largest_cluster={float(row['avg_largest_survival_cluster']):.2f}, "
            f"max_last={int(row['max_last_affected_node'])}, "
            f"behavior={row['spatial_behavior']}, "
            f"collapse={collapse}"
        )
    print(f"Saved summary to {summary_path}")
    print(f"Saved runs to {runs_path}")


if __name__ == "__main__":
    main()
