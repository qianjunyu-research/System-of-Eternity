import argparse
import pathlib
from typing import Dict, List, Tuple

from governance_integration import build_integrated_config
from governance_loop_sim import Config, apply_overrides, build_config, default_parameters, write_csv
from governance_two_node_sim import build_constraint_config, run_two_node_scenario


def clone_config(config: Config, **updates: float) -> Config:
    params = config.__dict__.copy()
    params.update(updates)
    return Config(**params)


def average_summaries(rows: List[Dict[str, float]]) -> Dict[str, float]:
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
    ]
    return {key: sum(float(row[key]) for row in rows) / len(rows) for key in keys}


def run_average(
    config_a: Config,
    config_b: Config,
    *,
    label: str,
    disturbance_coupling: float,
    cognition_coupling: float,
    node_a_injection: float,
    runs: int,
    steps: int,
    seed: int,
) -> Tuple[Dict[str, float], List[Dict[str, float]]]:
    run_rows: List[Dict[str, float]] = []
    for run_index in range(runs):
        _, _, summary = run_two_node_scenario(
            config_a,
            config_b,
            steps=steps,
            run_seed=seed + run_index,
            disturbance_coupling=disturbance_coupling,
            cognition_coupling=cognition_coupling,
            node_a_injection=node_a_injection,
        )
        run_rows.append(
            {
                "label": label,
                "run_index": run_index,
                "seed": seed + run_index,
                "disturbance_coupling": disturbance_coupling,
                "cognition_coupling": cognition_coupling,
                **summary,
            }
        )

    averaged = average_summaries(run_rows)
    summary_row = {
        "label": label,
        "disturbance_coupling": disturbance_coupling,
        "cognition_coupling": cognition_coupling,
        **averaged,
    }
    return summary_row, run_rows


def build_followup_suite(
    base_config: Config,
    *,
    runs: int,
    steps: int,
    seed: int,
) -> Tuple[List[Dict[str, float]], List[Dict[str, float]]]:
    integrated = build_integrated_config(base_config)
    low_control = clone_config(integrated, intervention_budget=0.40)
    noisy_integrated = clone_config(integrated, noise_level=0.02)

    summary_rows: List[Dict[str, float]] = []
    raw_rows: List[Dict[str, float]] = []

    for k in (0.05, 0.20, 0.50):
        summary, runs_rows = run_average(
            integrated,
            low_control,
            label=f"coupling_sweep_k_{k:.2f}",
            disturbance_coupling=k,
            cognition_coupling=k,
            node_a_injection=0.48,
            runs=runs,
            steps=steps,
            seed=seed,
        )
        summary_rows.append(summary)
        raw_rows.extend(runs_rows)

    reverse_summary, reverse_rows = run_average(
        low_control,
        integrated,
        label="reverse_asymmetry_a_weak_b_strong",
        disturbance_coupling=0.05,
        cognition_coupling=0.05,
        node_a_injection=0.48,
        runs=runs,
        steps=steps,
        seed=seed,
    )
    summary_rows.append(reverse_summary)
    raw_rows.extend(reverse_rows)

    sync_base_summary, sync_base_rows = run_average(
        integrated,
        integrated,
        label="sync_baseline_no_noise",
        disturbance_coupling=0.05,
        cognition_coupling=0.05,
        node_a_injection=0.48,
        runs=runs,
        steps=steps,
        seed=seed,
    )
    summary_rows.append(sync_base_summary)
    raw_rows.extend(sync_base_rows)

    sync_noise_summary, sync_noise_rows = run_average(
        noisy_integrated,
        noisy_integrated,
        label="sync_noise_002",
        disturbance_coupling=0.05,
        cognition_coupling=0.05,
        node_a_injection=0.48,
        runs=runs,
        steps=steps,
        seed=seed,
    )
    summary_rows.append(sync_noise_summary)
    raw_rows.extend(sync_noise_rows)

    return summary_rows, raw_rows


def print_suite(summary_rows: List[Dict[str, float]]) -> None:
    print("Governance two-node follow-up summary")
    for row in summary_rows:
        print(
            f"- {row['label']}: "
            f"A failure={row['node_a_failure']:.3f}, "
            f"B failure={row['node_b_failure']:.3f}, "
            f"propagated_failure={row['propagated_failure']:.3f}, "
            f"sync={row['synchronization_correlation']:.3f}, "
            f"gap={row['avg_stability_gap']:.3f}"
        )


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run follow-up experiments for the 2-node SOE v1.3 model."
    )
    parser.add_argument("--steps", type=int, default=100, help="Number of time steps per run.")
    parser.add_argument("--runs", type=int, default=20, help="Number of randomized runs per scenario.")
    parser.add_argument("--seed", type=int, default=42, help="Base random seed.")
    parser.add_argument(
        "--output-prefix",
        type=pathlib.Path,
        default=pathlib.Path("governance_two_node_followups"),
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

    summary_rows, raw_rows = build_followup_suite(
        config,
        runs=args.runs,
        steps=args.steps,
        seed=args.seed,
    )

    summary_path = args.output_prefix.with_name(f"{args.output_prefix.name}_summary.csv")
    runs_path = args.output_prefix.with_name(f"{args.output_prefix.name}_runs.csv")
    write_csv(summary_path, summary_rows)
    write_csv(runs_path, raw_rows)
    print_suite(summary_rows)
    print(f"Saved summary to {summary_path}")
    print(f"Saved runs to {runs_path}")


if __name__ == "__main__":
    main()
