import argparse
import csv
import pathlib
from typing import Dict, List, Optional, Sequence, Tuple

from governance_integration import build_integrated_config
from governance_loop_sim import Config, apply_overrides, build_config, default_parameters
from governance_two_node_sim import run_two_node_scenario


DISTURBANCE_LEVELS: Sequence[float] = (0.20, 0.40, 0.60)
DELAY_LEVELS: Sequence[int] = (0, 1, 2)
TRUST_COUPLING_LEVELS: Sequence[float] = (0.00, 0.01, 0.02, 0.05, 0.10, 0.20)


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


def write_csv_union(path: pathlib.Path, rows: List[Dict[str, object]]) -> None:
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
    disturbance_level: float,
    coupling_delay: int,
    trust_coupling: float,
    runs: int,
    steps: int,
    seed: int,
    disturbance_coupling: float,
    cognition_coupling: float,
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
            node_a_injection=disturbance_level,
            trust_coupling=trust_coupling,
            coupling_delay=coupling_delay,
        )
        run_rows.append(
            {
                "disturbance_level": disturbance_level,
                "coupling_delay": coupling_delay,
                "trust_coupling": trust_coupling,
                "run_index": run_index,
                "seed": seed + run_index,
                **summary,
            }
        )

    return {
        "disturbance_level": disturbance_level,
        "coupling_delay": coupling_delay,
        "trust_coupling": trust_coupling,
        **average_metrics(run_rows),
    }, run_rows


def build_threshold_rows(
    summary_rows: List[Dict[str, float]],
    *,
    disturbance_levels: Sequence[float],
    delay_levels: Sequence[int],
    trust_levels: Sequence[float],
) -> List[Dict[str, object]]:
    threshold_rows: List[Dict[str, object]] = []
    for disturbance_level in disturbance_levels:
        for coupling_delay in delay_levels:
            matching_rows = [
                row
                for row in summary_rows
                if row["disturbance_level"] == disturbance_level and row["coupling_delay"] == coupling_delay
            ]
            matching_rows.sort(key=lambda row: trust_levels.index(row["trust_coupling"]))
            threshold_row: Optional[Dict[str, float]] = next(
                (row for row in matching_rows if float(row["node_b_failure"]) <= 1e-12),
                None,
            )
            if threshold_row is None:
                strongest = matching_rows[-1]
                threshold_rows.append(
                    {
                        "disturbance_level": disturbance_level,
                        "coupling_delay": coupling_delay,
                        "k_t_star": None,
                        "threshold_found": False,
                        "node_b_failure_rate": strongest["node_b_failure"],
                        "node_b_final_stability": strongest["node_b_final_stability"],
                        "node_b_final_trust": strongest["node_b_final_trust"],
                        "node_a_final_stability": strongest["node_a_final_stability"],
                        "node_a_final_trust": strongest["node_a_final_trust"],
                    }
                )
                continue

            threshold_rows.append(
                {
                    "disturbance_level": disturbance_level,
                    "coupling_delay": coupling_delay,
                    "k_t_star": threshold_row["trust_coupling"],
                    "threshold_found": True,
                    "node_b_failure_rate": threshold_row["node_b_failure"],
                    "node_b_final_stability": threshold_row["node_b_final_stability"],
                    "node_b_final_trust": threshold_row["node_b_final_trust"],
                    "node_a_final_stability": threshold_row["node_a_final_stability"],
                    "node_a_final_trust": threshold_row["node_a_final_trust"],
                }
            )
    return threshold_rows


def build_suite(
    base_config: Config,
    *,
    disturbance_levels: Sequence[float],
    delay_levels: Sequence[int],
    trust_levels: Sequence[float],
    runs: int,
    steps: int,
    seed: int,
    disturbance_coupling: float,
    cognition_coupling: float,
) -> Tuple[List[Dict[str, float]], List[Dict[str, float]], List[Dict[str, object]]]:
    high = build_integrated_config(base_config)
    low = Config(**{**high.__dict__, "intervention_budget": 0.40})

    summary_rows: List[Dict[str, float]] = []
    raw_rows: List[Dict[str, float]] = []

    for disturbance_level in disturbance_levels:
        for coupling_delay in delay_levels:
            for trust_coupling in trust_levels:
                summary, rows = run_average(
                    high,
                    low,
                    disturbance_level=disturbance_level,
                    coupling_delay=coupling_delay,
                    trust_coupling=trust_coupling,
                    runs=runs,
                    steps=steps,
                    seed=seed,
                    disturbance_coupling=disturbance_coupling,
                    cognition_coupling=cognition_coupling,
                )
                summary_rows.append(summary)
                raw_rows.extend(rows)

    threshold_rows = build_threshold_rows(
        summary_rows,
        disturbance_levels=disturbance_levels,
        delay_levels=delay_levels,
        trust_levels=trust_levels,
    )
    return summary_rows, raw_rows, threshold_rows


def print_threshold_table(threshold_rows: List[Dict[str, object]]) -> None:
    print("Governance two-node recovery-threshold map")
    for row in threshold_rows:
        k_t_star = "NA" if row["k_t_star"] is None else f"{float(row['k_t_star']):.2f}"
        print(
            f"- D={float(row['disturbance_level']):.2f}, "
            f"delay={int(row['coupling_delay'])}: "
            f"k_T*={k_t_star}, "
            f"B failure={float(row['node_b_failure_rate']):.3f}, "
            f"B stability={float(row['node_b_final_stability']):.3f}, "
            f"B trust={float(row['node_b_final_trust']):.3f}"
        )


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Map recovery thresholds for the 2-node SOE model across disturbance and delay levels."
    )
    parser.add_argument("--steps", type=int, default=100, help="Number of time steps per run.")
    parser.add_argument("--runs", type=int, default=20, help="Number of randomized runs per scenario.")
    parser.add_argument("--seed", type=int, default=42, help="Base random seed.")
    parser.add_argument(
        "--disturbance-coupling",
        type=float,
        default=0.05,
        help="Cross-node disturbance spread used for the threshold map.",
    )
    parser.add_argument(
        "--cognition-coupling",
        type=float,
        default=0.05,
        help="Cross-node cognition spread used for the threshold map.",
    )
    parser.add_argument(
        "--output-prefix",
        type=pathlib.Path,
        default=pathlib.Path("governance_two_node_threshold_map"),
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

    summary_rows, raw_rows, threshold_rows = build_suite(
        config,
        disturbance_levels=DISTURBANCE_LEVELS,
        delay_levels=DELAY_LEVELS,
        trust_levels=TRUST_COUPLING_LEVELS,
        runs=args.runs,
        steps=args.steps,
        seed=args.seed,
        disturbance_coupling=args.disturbance_coupling,
        cognition_coupling=args.cognition_coupling,
    )

    summary_path = args.output_prefix.with_name(f"{args.output_prefix.name}_summary.csv")
    runs_path = args.output_prefix.with_name(f"{args.output_prefix.name}_runs.csv")
    thresholds_path = args.output_prefix.with_name(f"{args.output_prefix.name}_thresholds.csv")
    write_csv_union(summary_path, summary_rows)
    write_csv_union(runs_path, raw_rows)
    write_csv_union(thresholds_path, threshold_rows)
    print_threshold_table(threshold_rows)
    print(f"Saved summary to {summary_path}")
    print(f"Saved runs to {runs_path}")
    print(f"Saved thresholds to {thresholds_path}")


if __name__ == "__main__":
    main()
