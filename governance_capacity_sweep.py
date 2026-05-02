import argparse
import pathlib
from dataclasses import asdict
from typing import Dict, List, Tuple

from governance_integration import build_integrated_config
from governance_loop_sim import Config, apply_overrides, build_config, default_parameters, write_csv
from governance_regime_scan import run_regime_batch


def build_capacity_suite(
    base_config: Config,
    *,
    capacities: List[float],
    runs: int,
    steps: int,
    seed: int,
) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    integrated = build_integrated_config(base_config)
    summary_rows: List[Dict[str, object]] = []
    raw_rows: List[Dict[str, object]] = []

    for capacity in capacities:
        scenario = f"capacity_{capacity:.2f}".replace(".", "")
        config = Config(**{**asdict(integrated), "intervention_budget": capacity})
        summary_row, raw_row_set = run_regime_batch(
            config,
            test_name="capacity_sweep_v13",
            scenario=scenario,
            runs=runs,
            steps=steps,
            seed=seed,
            note=f"Integrated v1.2 controller at intervention_budget={capacity:.2f}.",
        )
        summary_rows.append(summary_row)
        raw_rows.extend(raw_row_set)

    return summary_rows, raw_rows


def print_suite(summary_rows: List[Dict[str, object]]) -> None:
    print("Governance capacity sweep (v1.2 rewired model)")
    for row in summary_rows:
        print(
            f"- {row['scenario']}: "
            f"stable_run_rate={float(row['stable_run_rate']):.3f}, "
            f"failure_rate={float(row['failure_rate']):.3f}, "
            f"avg_final_stability={float(row['avg_final_stability']):.3f}"
        )


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a capacity sweep against the integrated v1.2 governance model."
    )
    parser.add_argument("--steps", type=int, default=150, help="Number of time steps per run.")
    parser.add_argument("--runs", type=int, default=30, help="Number of randomized runs per scenario.")
    parser.add_argument("--seed", type=int, default=42, help="Base random seed.")
    parser.add_argument(
        "--capacities",
        type=float,
        nargs="+",
        default=[0.45, 0.50, 0.55],
        help="Intervention-budget values to sweep.",
    )
    parser.add_argument(
        "--override",
        action="append",
        default=[],
        help="Override baseline parameters using name=value or comma-separated name=value pairs.",
    )
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=pathlib.Path("v13_capacity_sweep_summary.csv"),
        help="Write scenario summaries to CSV.",
    )
    parser.add_argument(
        "--raw-output",
        type=pathlib.Path,
        default=pathlib.Path("v13_capacity_sweep_runs.csv"),
        help="Write per-run summaries to CSV.",
    )
    return parser


def main() -> None:
    parser = build_argument_parser()
    args = parser.parse_args()

    params = default_parameters()
    params = apply_overrides(params, args.override)
    config = build_config(params)

    summary_rows, raw_rows = build_capacity_suite(
        config,
        capacities=args.capacities,
        runs=args.runs,
        steps=args.steps,
        seed=args.seed,
    )

    print_suite(summary_rows)
    if args.output:
        write_csv(args.output, summary_rows)
        print(f"Saved scenario summaries to {args.output}")
    if args.raw_output:
        write_csv(args.raw_output, raw_rows)
        print(f"Saved per-run summaries to {args.raw_output}")


if __name__ == "__main__":
    main()
