import argparse
import pathlib
from dataclasses import asdict
from typing import Dict, List, Tuple

from governance_falsification import choose_continuous_targets, run_custom_simulation
from governance_integration import build_integrated_config, make_integrated_step_function
from governance_loop_sim import Config, apply_overrides, build_config, default_parameters, summarize_run, write_csv


def percentile(values: List[float], p: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("Cannot compute percentile of empty values.")
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * p
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] + ((ordered[upper] - ordered[lower]) * weight)


def describe_final_trust(values: List[float]) -> Dict[str, float]:
    return {
        "trust_mean": sum(values) / len(values),
        "trust_min": min(values),
        "trust_p25": percentile(values, 0.25),
        "trust_median": percentile(values, 0.50),
        "trust_p75": percentile(values, 0.75),
        "trust_max": max(values),
        "trust_saturation_rate": sum(1 for value in values if value >= 0.99) / len(values),
    }


def build_constraint_config(base: Config) -> Config:
    return Config(
        **{
            **asdict(base),
            "intervention_budget": 0.40,
            "alpha": 1.00,
            "intervention_decay": 0.22,
            "shock_prob": 0.15,
            "shock_impact": 0.48,
        }
    )


def run_scenario(
    config: Config,
    *,
    scenario: str,
    runs: int,
    steps: int,
    seed: int,
) -> Tuple[Dict[str, float], List[Dict[str, float]]]:
    summaries: List[Dict[str, float]] = []
    final_trusts: List[float] = []
    raw_rows: List[Dict[str, float]] = []

    for run_index in range(runs):
        history = run_custom_simulation(
            config=config,
            steps=steps,
            seed=seed + run_index,
            direct_controller=choose_continuous_targets,
            step_fn=make_integrated_step_function(cap_mode="none"),
            controller_label=f"{scenario}_no_cap",
        )
        summary = summarize_run(history, threshold=config.stability_threshold)
        final_trust = float(history[-1]["trust"])
        summaries.append(summary)
        final_trusts.append(final_trust)
        raw_rows.append(
            {
                "scenario": scenario,
                "run_index": run_index,
                "seed": seed + run_index,
                "final_trust": final_trust,
                **summary,
            }
        )

    distribution = describe_final_trust(final_trusts)
    summary_row = {
        "scenario": scenario,
        "stable_run_rate": sum(int(row["stable_run"]) for row in summaries) / len(summaries),
        "failure_rate": sum(int(row["failure_case"]) for row in summaries) / len(summaries),
        "recovered_run_rate": sum(int(row["recovered_run"]) for row in summaries) / len(summaries),
        "avg_final_stability": sum(float(row["final_stability"]) for row in summaries) / len(summaries),
        "avg_min_stability": sum(float(row["min_stability"]) for row in summaries) / len(summaries),
        **distribution,
    }
    return summary_row, raw_rows


def build_no_cap_suite(
    base_config: Config,
    *,
    runs: int,
    steps: int,
    seed: int,
) -> Tuple[List[Dict[str, float]], List[Dict[str, float]]]:
    integrated = build_integrated_config(base_config)
    scenarios = [
        ("baseline_high_control_no_cap", integrated),
        ("constraint_regime_no_cap", build_constraint_config(integrated)),
    ]

    summary_rows: List[Dict[str, float]] = []
    raw_rows: List[Dict[str, float]] = []
    for scenario_name, config in scenarios:
        summary_row, raw_row_set = run_scenario(
            config,
            scenario=scenario_name,
            runs=runs,
            steps=steps,
            seed=seed,
        )
        summary_rows.append(summary_row)
        raw_rows.extend(raw_row_set)
    return summary_rows, raw_rows


def print_suite(summary_rows: List[Dict[str, float]]) -> None:
    print("Governance no-cap comparison")
    for row in summary_rows:
        print(
            f"- {row['scenario']}: "
            f"stable_run_rate={float(row['stable_run_rate']):.3f}, "
            f"failure_rate={float(row['failure_rate']):.3f}, "
            f"avg_final_stability={float(row['avg_final_stability']):.3f}, "
            f"trust_median={float(row['trust_median']):.3f}, "
            f"trust_max={float(row['trust_max']):.3f}, "
            f"trust_saturation_rate={float(row['trust_saturation_rate']):.3f}"
        )


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare the regime-aware integrated model with the trust cap removed."
    )
    parser.add_argument("--steps", type=int, default=100, help="Number of time steps per run.")
    parser.add_argument("--runs", type=int, default=20, help="Number of randomized runs per scenario.")
    parser.add_argument("--seed", type=int, default=42, help="Base random seed.")
    parser.add_argument(
        "--override",
        action="append",
        default=[],
        help="Override baseline parameters using name=value or comma-separated name=value pairs.",
    )
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=pathlib.Path("governance_no_cap_summary.csv"),
        help="Write scenario summaries to CSV.",
    )
    parser.add_argument(
        "--raw-output",
        type=pathlib.Path,
        help="Write per-run summaries to CSV.",
    )
    return parser


def main() -> None:
    parser = build_argument_parser()
    args = parser.parse_args()

    params = default_parameters()
    params = apply_overrides(params, args.override)
    config = build_config(params)

    summary_rows, raw_rows = build_no_cap_suite(
        config,
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
