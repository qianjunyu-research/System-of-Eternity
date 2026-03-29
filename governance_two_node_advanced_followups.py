import argparse
import csv
import pathlib
from typing import Dict, List, Tuple

from governance_integration import build_integrated_config
from governance_loop_sim import Config, apply_overrides, build_config, default_parameters, write_csv
from governance_two_node_sim import build_constraint_config, run_two_node_scenario


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


def run_average(
    config_a: Config,
    config_b: Config,
    *,
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
                "label": label,
                "run_index": run_index,
                "seed": seed + run_index,
                **kwargs,
                **summary,
            }
        )

    return {"label": label, **average_metrics(run_rows)}, run_rows


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

    trust_kwargs = {
        "disturbance_coupling": 0.05,
        "cognition_coupling": 0.05,
        "node_a_injection": 0.48,
    }
    for label, trust_coupling in (
        ("trust_coupling_off", 0.0),
        ("trust_coupling_on", 0.05),
    ):
        summary, rows = run_average(
            high,
            low,
            label=label,
            runs=runs,
            steps=steps,
            seed=seed,
            kwargs={**trust_kwargs, "trust_coupling": trust_coupling},
        )
        summary_rows.append(summary)
        raw_rows.extend(rows)

    asym_base = {
        "node_a_injection": 0.48,
        "disturbance_coupling": 0.0,
        "cognition_coupling": 0.0,
    }
    for label, disturbance_coupling_ab, disturbance_coupling_ba in (
        ("unequal_coupling_ab_dominant", 0.20, 0.05),
        ("unequal_coupling_ba_dominant", 0.05, 0.20),
    ):
        summary, rows = run_average(
            high,
            low,
            label=label,
            runs=runs,
            steps=steps,
            seed=seed,
            kwargs={
                **asym_base,
                "disturbance_coupling_ab": disturbance_coupling_ab,
                "disturbance_coupling_ba": disturbance_coupling_ba,
                "cognition_coupling_ab": disturbance_coupling_ab,
                "cognition_coupling_ba": disturbance_coupling_ba,
            },
        )
        summary_rows.append(summary)
        raw_rows.extend(rows)

    delay_base = {
        "disturbance_coupling": 0.20,
        "cognition_coupling": 0.20,
        "node_a_injection": 0.48,
    }
    for label, coupling_delay in (
        ("time_delay_0", 0),
        ("time_delay_2", 2),
    ):
        summary, rows = run_average(
            high,
            low,
            label=label,
            runs=runs,
            steps=steps,
            seed=seed,
            kwargs={**delay_base, "coupling_delay": coupling_delay},
        )
        summary_rows.append(summary)
        raw_rows.extend(rows)

    return summary_rows, raw_rows


def print_suite(summary_rows: List[Dict[str, float]]) -> None:
    print("Governance two-node advanced follow-up summary")
    for row in summary_rows:
        print(
            f"- {row['label']}: "
            f"A failure={row['node_a_failure']:.3f}, "
            f"B failure={row['node_b_failure']:.3f}, "
            f"B stability={row['node_b_final_stability']:.3f}, "
            f"propagated_failure={row['propagated_failure']:.3f}, "
            f"sync={row['synchronization_correlation']:.3f}"
        )


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


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run advanced follow-up tests for the 2-node SOE v1.3 model."
    )
    parser.add_argument("--steps", type=int, default=100, help="Number of time steps per run.")
    parser.add_argument("--runs", type=int, default=20, help="Number of randomized runs per scenario.")
    parser.add_argument("--seed", type=int, default=42, help="Base random seed.")
    parser.add_argument(
        "--output-prefix",
        type=pathlib.Path,
        default=pathlib.Path("governance_two_node_advanced"),
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
    write_csv(summary_path, summary_rows)
    write_csv_union(runs_path, raw_rows)
    print_suite(summary_rows)
    print(f"Saved summary to {summary_path}")
    print(f"Saved runs to {runs_path}")


if __name__ == "__main__":
    main()
