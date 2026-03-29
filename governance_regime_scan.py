import argparse
import pathlib
from dataclasses import asdict
from typing import Dict, List, Tuple

from governance_falsification import choose_continuous_targets, run_custom_simulation
from governance_integration import build_integrated_config, make_integrated_step_function
from governance_loop_sim import Config, apply_overrides, build_config, default_parameters, summarize_run, write_csv


def classify_first_stressor(history: List[Dict[str, float]], config: Config) -> str:
    trust_step = next((int(row["step"]) for row in history if row["trust"] < 0.70), None)
    disturbance_step = next(
        (int(row["step"]) for row in history if row["disturbance"] >= config.disturbance_boundary),
        None,
    )
    cognition_step = next(
        (int(row["step"]) for row in history if row["cognitive_distortion"] >= config.compound_cognition_threshold),
        None,
    )

    candidates = [
        ("trust", trust_step),
        ("disturbance", disturbance_step),
        ("cognition", cognition_step),
    ]
    realized = [(label, step) for label, step in candidates if step is not None]
    if not realized:
        return "none"

    realized.sort(key=lambda item: item[1])
    earliest_step = realized[0][1]
    earliest = [label for label, step in realized if step == earliest_step]
    if len(earliest) == 1:
        return earliest[0]
    return "tie"


def summarize_regime_batch(
    histories: List[List[Dict[str, float]]],
    config: Config,
    *,
    test_name: str,
    scenario: str,
    note: str,
) -> Dict[str, object]:
    summaries = [summarize_run(history, threshold=config.stability_threshold) for history in histories]
    stressors = [classify_first_stressor(history, config) for history in histories]

    return {
        "test_name": test_name,
        "scenario": scenario,
        "stable_run_rate": sum(int(row["stable_run"]) for row in summaries) / len(summaries),
        "failure_rate": sum(int(row["failure_case"]) for row in summaries) / len(summaries),
        "recovered_run_rate": sum(int(row["recovered_run"]) for row in summaries) / len(summaries),
        "avg_final_stability": sum(float(row["final_stability"]) for row in summaries) / len(summaries),
        "avg_min_stability": sum(float(row["min_stability"]) for row in summaries) / len(summaries),
        "avg_final_trust": sum(float(row["final_trust"]) for row in summaries) / len(summaries),
        "avg_min_trust": sum(min(float(row["trust"]) for row in history) for history in histories) / len(histories),
        "avg_final_disturbance": sum(float(row["final_disturbance"]) for row in summaries) / len(summaries),
        "avg_max_disturbance": sum(max(float(row["disturbance"]) for row in history) for history in histories) / len(histories),
        "avg_final_cognitive_distortion": (
            sum(float(row["final_cognitive_distortion"]) for row in summaries) / len(summaries)
        ),
        "avg_max_cognitive_distortion": (
            sum(max(float(row["cognitive_distortion"]) for row in history) for history in histories) / len(histories)
        ),
        "trust_first_rate": sum(1 for label in stressors if label == "trust") / len(stressors),
        "disturbance_first_rate": sum(1 for label in stressors if label == "disturbance") / len(stressors),
        "cognition_first_rate": sum(1 for label in stressors if label == "cognition") / len(stressors),
        "tie_first_rate": sum(1 for label in stressors if label == "tie") / len(stressors),
        "no_stressor_rate": sum(1 for label in stressors if label == "none") / len(stressors),
        "note": note,
    }


def run_regime_batch(
    config: Config,
    *,
    test_name: str,
    scenario: str,
    runs: int,
    steps: int,
    seed: int,
    note: str,
) -> Tuple[Dict[str, object], List[Dict[str, object]]]:
    histories: List[List[Dict[str, float]]] = []
    raw_rows: List[Dict[str, object]] = []

    for run_index in range(runs):
        history = run_custom_simulation(
            config=config,
            steps=steps,
            seed=seed + run_index,
            direct_controller=choose_continuous_targets,
            step_fn=make_integrated_step_function(),
            controller_label=scenario,
        )
        summary = summarize_run(history, threshold=config.stability_threshold)
        histories.append(history)
        raw_rows.append(
            {
                "test_name": test_name,
                "scenario": scenario,
                "run_index": run_index,
                "seed": seed + run_index,
                **summary,
                "first_stressor": classify_first_stressor(history, config),
            }
        )

    return summarize_regime_batch(histories, config, test_name=test_name, scenario=scenario, note=note), raw_rows


def build_regime_suite(
    base_config: Config,
    *,
    runs: int,
    steps: int,
    seed: int,
) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    integrated = build_integrated_config(base_config)
    scenarios: List[Tuple[str, Config, str]] = []

    scenarios.append(
        (
            "baseline_integrated",
            integrated,
            "Reference integrated v1.2 control regime.",
        )
    )

    capacity_060 = Config(**{**asdict(integrated), "intervention_budget": 0.60})
    scenarios.append(
        (
            "capacity_060",
            capacity_060,
            "Reduced control capacity to expose structural dependence.",
        )
    )

    capacity_040 = Config(**{**asdict(integrated), "intervention_budget": 0.40})
    scenarios.append(
        (
            "capacity_040",
            capacity_040,
            "Strongly reduced control capacity to force visible failure modes.",
        )
    )

    smoothing_low = Config(
        **{
            **asdict(integrated),
            "alpha": 1.00,
            "intervention_decay": 0.22,
        }
    )
    scenarios.append(
        (
            "smoothing_low",
            smoothing_low,
            "Reduced smoothing to test whether overreaction returns.",
        )
    )

    disturbance_high = Config(
        **{
            **asdict(integrated),
            "shock_prob": 0.15,
            "shock_impact": 0.48,
        }
    )
    scenarios.append(
        (
            "disturbance_high",
            disturbance_high,
            "Raised shock frequency and magnitude to reactivate latent structure.",
        )
    )

    combined_constraint = Config(
        **{
            **asdict(integrated),
            "intervention_budget": 0.40,
            "alpha": 1.00,
            "intervention_decay": 0.22,
            "shock_prob": 0.15,
            "shock_impact": 0.48,
        }
    )
    scenarios.append(
        (
            "combined_constraint",
            combined_constraint,
            "Low capacity, low smoothing, and high disturbance combined.",
        )
    )

    summary_rows: List[Dict[str, object]] = []
    raw_rows: List[Dict[str, object]] = []

    for scenario_name, config, note in scenarios:
        summary_row, raw_row_set = run_regime_batch(
            config,
            test_name="constraint_activation",
            scenario=scenario_name,
            runs=runs,
            steps=steps,
            seed=seed,
            note=note,
        )
        summary_rows.append(summary_row)
        raw_rows.extend(raw_row_set)

    return summary_rows, raw_rows


def print_suite(summary_rows: List[Dict[str, object]]) -> None:
    print("Governance regime scan")
    for row in summary_rows:
        print(
            f"- {row['scenario']}: "
            f"stable_run_rate={float(row['stable_run_rate']):.3f}, "
            f"failure_rate={float(row['failure_rate']):.3f}, "
            f"avg_final_stability={float(row['avg_final_stability']):.3f}, "
            f"trust_first={float(row['trust_first_rate']):.3f}, "
            f"disturbance_first={float(row['disturbance_first_rate']):.3f}, "
            f"cognition_first={float(row['cognition_first_rate']):.3f}"
        )


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a constrained-regime scan against the integrated v1.2 governance model."
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
        default=pathlib.Path("governance_regime_summary.csv"),
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

    summary_rows, raw_rows = build_regime_suite(
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
