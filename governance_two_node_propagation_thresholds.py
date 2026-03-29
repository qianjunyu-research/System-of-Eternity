import argparse
import csv
import pathlib
from typing import Dict, List, Tuple

from governance_integration import build_integrated_config
from governance_loop_sim import Config, apply_overrides, build_config, default_parameters
from governance_two_node_sim import run_two_node_scenario


def average_metrics(rows: List[Dict[str, float]]) -> Dict[str, float]:
    keys = [
        "node_a_final_stability",
        "node_b_final_stability",
        "node_a_stability_rate",
        "node_b_stability_rate",
        "node_a_failure",
        "node_b_failure",
        "node_a_recovered",
        "node_b_recovered",
        "propagated_breach",
        "propagated_failure",
        "synchronization_correlation",
        "avg_stability_gap",
        "simultaneous_breach",
        "node_a_final_trust",
        "node_b_final_trust",
    ]
    return {key: sum(float(row[key]) for row in rows) / len(rows) for key in keys}


def write_csv_union(path: pathlib.Path, rows: List[Dict[str, float]]) -> None:
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


def run_average(
    config_a: Config,
    config_b: Config,
    *,
    test_group: str,
    label: str,
    runs: int,
    steps: int,
    seed: int,
    kwargs: Dict[str, float],
) -> Tuple[Dict[str, float], List[Dict[str, float]]]:
    run_rows: List[Dict[str, float]] = []
    for run_index in range(runs):
        _, _, summary = run_two_node_scenario(
            config_a,
            config_b,
            steps=steps,
            run_seed=seed + run_index,
            **kwargs,
        )
        run_rows.append(
            {
                "test_group": test_group,
                "label": label,
                "run_index": run_index,
                "seed": seed + run_index,
                **kwargs,
                **summary,
            }
        )

    return {"test_group": test_group, "label": label, **kwargs, **average_metrics(run_rows)}, run_rows


def build_suite(
    base_config: Config,
    *,
    runs: int,
    steps: int,
    seed: int,
) -> Tuple[List[Dict[str, float]], List[Dict[str, float]]]:
    high = build_integrated_config(base_config)
    low = Config(**{**high.__dict__, "intervention_budget": 0.40})

    summary_rows: List[Dict[str, float]] = []
    raw_rows: List[Dict[str, float]] = []

    threshold_base = {
        "disturbance_coupling": 0.05,
        "cognition_coupling": 0.05,
        "node_a_injection": 0.48,
    }
    for trust_coupling in (0.00, 0.05, 0.10, 0.20):
        summary, rows = run_average(
            high,
            low,
            test_group="test_a_t_coupling_threshold",
            label=f"threshold_t_{trust_coupling:.2f}",
            runs=runs,
            steps=steps,
            seed=seed,
            kwargs={**threshold_base, "trust_coupling": trust_coupling},
        )
        summary_rows.append(summary)
        raw_rows.extend(rows)

    mixed_base = {
        "disturbance_coupling": 0.05,
        "cognition_coupling": 0.05,
        "node_a_injection": 0.48,
    }
    for trust_coupling in (0.00, 0.01, 0.02, 0.03, 0.05):
        summary, rows = run_average(
            high,
            low,
            test_group="test_b_mixed_channels",
            label=f"mixed_channels_t_{trust_coupling:.2f}",
            runs=runs,
            steps=steps,
            seed=seed,
            kwargs={**mixed_base, "trust_coupling": trust_coupling},
        )
        summary_rows.append(summary)
        raw_rows.extend(rows)

    delay_configs = (
        ("delay0_t_0.00", 0, 0.00),
        ("delay2_t_0.00", 2, 0.00),
        ("delay2_t_0.05", 2, 0.05),
        ("delay2_t_0.10", 2, 0.10),
        ("delay2_t_0.20", 2, 0.20),
    )
    delay_base = {
        "disturbance_coupling": 0.20,
        "cognition_coupling": 0.20,
        "node_a_injection": 0.48,
    }
    for label, coupling_delay, trust_coupling in delay_configs:
        summary, rows = run_average(
            high,
            low,
            test_group="test_c_delay_t_interaction",
            label=label,
            runs=runs,
            steps=steps,
            seed=seed,
            kwargs={
                **delay_base,
                "coupling_delay": coupling_delay,
                "trust_coupling": trust_coupling,
            },
        )
        summary_rows.append(summary)
        raw_rows.extend(rows)

    return summary_rows, raw_rows


def print_suite(summary_rows: List[Dict[str, float]]) -> None:
    print("Governance two-node propagation threshold summary")
    for row in summary_rows:
        print(
            f"- {row['test_group']} / {row['label']}: "
            f"B failure={row['node_b_failure']:.3f}, "
            f"B stability={row['node_b_final_stability']:.3f}, "
            f"B trust={row['node_b_final_trust']:.3f}, "
            f"propagated_failure={row['propagated_failure']:.3f}, "
            f"sync={row['synchronization_correlation']:.3f}"
        )


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run trust-coupling threshold and delay interaction tests for the 2-node SOE v1.3 model."
    )
    parser.add_argument("--steps", type=int, default=100, help="Number of time steps per run.")
    parser.add_argument("--runs", type=int, default=20, help="Number of randomized runs per scenario.")
    parser.add_argument("--seed", type=int, default=42, help="Base random seed.")
    parser.add_argument(
        "--output-prefix",
        type=pathlib.Path,
        default=pathlib.Path("governance_two_node_propagation"),
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

    params = default_parameters()
    params = apply_overrides(params, args.override)
    config = build_config(params)

    summary_rows, raw_rows = build_suite(
        config,
        runs=args.runs,
        steps=args.steps,
        seed=args.seed,
    )

    summary_path = args.output_prefix.with_name(f"{args.output_prefix.name}_summary.csv")
    runs_path = args.output_prefix.with_name(f"{args.output_prefix.name}_runs.csv")
    write_csv_union(summary_path, summary_rows)
    write_csv_union(runs_path, raw_rows)
    print_suite(summary_rows)
    print(f"Saved summary to {summary_path}")
    print(f"Saved runs to {runs_path}")


if __name__ == "__main__":
    main()
