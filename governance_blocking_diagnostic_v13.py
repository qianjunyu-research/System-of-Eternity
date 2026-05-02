import argparse
import pathlib
from dataclasses import asdict
from typing import Dict, List, Tuple

from governance_integration import build_integrated_config
from governance_loop_sim import Config, apply_overrides, build_config, default_parameters, write_csv
from governance_regime_scan import run_regime_batch


def run_blocking_diagnostic(
    base_config: Config,
    *,
    runs: int,
    steps: int,
    seed: int,
    f_min_values: List[float],
    alpha_values: List[float],
    w_values: List[float],
    include_w_calibration: bool = True,
) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    integrated = build_integrated_config(base_config)
    disturbance_high = Config(
        **{
            **asdict(integrated),
            "shock_prob": 0.15,
            "shock_impact": 0.48,
        }
    )
    summary_rows: List[Dict[str, object]] = []
    raw_rows: List[Dict[str, object]] = []

    # 1) blocking diagnostic: joint f_min (k_D floor) × alpha_gov (k_D update rate) sweep
    for f_min in f_min_values:
        for alpha_gov in alpha_values:
            scenario = f"disturbance_high_fmin_{f_min:.2f}_agov_{alpha_gov:.2f}".replace(".", "")
            config = Config(
                **{
                    **asdict(disturbance_high),
                    "governance_coupling_floor": f_min,
                    "governance_coupling_alpha": alpha_gov,
                }
            )
            summary_row, raw_row_set = run_regime_batch(
                config,
                test_name="blocking_diagnostic_v13",
                scenario=scenario,
                runs=runs,
                steps=steps,
                seed=seed,
                note=(
                    f"disturbance_high with governance_coupling_floor(f_min)={f_min:.2f} "
                    f"and governance_coupling_alpha(alpha_gov)={alpha_gov:.2f}; "
                    "separate from disturbance_baseline."
                ),
            )
            summary_rows.append(summary_row)
            raw_rows.extend(raw_row_set)

    # 2) Optional W calibration at capacity 0.50
    if include_w_calibration:
        for w_gain in w_values:
            scenario = f"capacity_050_w_{w_gain:.2f}".replace(".", "")
            config = Config(
                **{
                    **asdict(integrated),
                    "intervention_budget": 0.50,
                    "activation_gain": w_gain,
                }
            )
            summary_row, raw_row_set = run_regime_batch(
                config,
                test_name="w_calibration_v13",
                scenario=scenario,
                runs=runs,
                steps=steps,
                seed=seed,
                note=f"Capacity fixed at 0.50 with activation_gain(W)={w_gain:.2f}.",
            )
            summary_rows.append(summary_row)
            raw_rows.extend(raw_row_set)

    return summary_rows, raw_rows


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run blocking diagnostics for v1.3 round: disturbance_high f_min/alpha_gov sweeps "
            "plus W calibration at capacity 0.50."
        )
    )
    parser.add_argument("--steps", type=int, default=150, help="Number of time steps per run.")
    parser.add_argument("--runs", type=int, default=30, help="Number of randomized runs per scenario.")
    parser.add_argument("--seed", type=int, default=42, help="Base random seed.")
    parser.add_argument(
        "--f-min-values",
        type=float,
        nargs="+",
        default=[0.05, 0.10, 0.15, 0.20, 0.25, 0.30],
        help="f_min values for governance coupling floor (k_D minimum) under disturbance_high.",
    )
    parser.add_argument(
        "--alpha-gov-values",
        type=float,
        nargs="+",
        default=[0.03, 0.05, 0.07, 0.10, 0.15],
        help="alpha_gov values for damped k_D update speed in the joint sweep.",
    )
    parser.add_argument(
        "--w-values",
        type=float,
        nargs="+",
        default=[0.60, 0.80, 1.00],
        help="W calibration values (mapped to activation_gain) at capacity 0.50.",
    )
    parser.add_argument(
        "--skip-w-calibration",
        action="store_true",
        help="Skip W calibration and run only the joint disturbance_high f_min × alpha_gov diagnostic.",
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
        default=pathlib.Path("v13_blocking_diagnostic_summary.csv"),
        help="Write scenario summaries to CSV.",
    )
    parser.add_argument(
        "--raw-output",
        type=pathlib.Path,
        default=pathlib.Path("v13_blocking_diagnostic_runs.csv"),
        help="Write per-run summaries to CSV.",
    )
    return parser


def main() -> None:
    parser = build_argument_parser()
    args = parser.parse_args()

    params = default_parameters()
    params = apply_overrides(params, args.override)
    config = build_config(params)

    summary_rows, raw_rows = run_blocking_diagnostic(
        config,
        runs=args.runs,
        steps=args.steps,
        seed=args.seed,
        f_min_values=args.f_min_values,
        alpha_values=args.alpha_gov_values,
        w_values=args.w_values,
        include_w_calibration=not args.skip_w_calibration,
    )

    write_csv(args.output, summary_rows)
    write_csv(args.raw_output, raw_rows)
    print(f"Saved scenario summaries to {args.output}")
    print(f"Saved per-run summaries to {args.raw_output}")


if __name__ == "__main__":
    main()
