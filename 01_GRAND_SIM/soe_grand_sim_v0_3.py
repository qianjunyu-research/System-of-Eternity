import argparse
import csv
import pathlib
import random
from collections import defaultdict
from typing import Dict, Iterable, List, Sequence, Tuple

import soe_grand_sim_v0_2 as v02
import v18_federation_hub_redundancy as v18


BATCH_ID = "grand_sim_v0_3"
OUTPUT_PREFIX = BATCH_ID
DEFAULT_RUNS_PER_CELL = 10
DEFAULT_STEPS = 160
SEED_START = 7300

FEDERATION_SCENARIOS = {
    "federation_cluster_attack",
    "federation_bridge_stress",
    "psi_corruption",
    "async_message_loss",
}

WEIGHT_SETS = [
    ("v02_default", 0.25, 0.25, 0.20, 0.20, 0.10),
    ("disturbance_heavy", 0.20, 0.35, 0.15, 0.20, 0.10),
    ("stability_heavy", 0.20, 0.20, 0.15, 0.35, 0.10),
    ("trust_stability", 0.35, 0.15, 0.10, 0.30, 0.10),
    ("regime_heavy", 0.20, 0.20, 0.15, 0.20, 0.25),
]
PSI_THRESHOLDS = [round(0.30 + 0.02 * index, 2) for index in range(19)]
PSI_LAMBDAS = [0.05, 0.10, 0.20]


def avg(values: Iterable[float]) -> float:
    values = list(values)
    return sum(values) / max(1, len(values))


def write_csv(path: pathlib.Path, rows: Sequence[Dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def regime_weight(collapse_share: float) -> float:
    if collapse_share >= v02.IGNITION_SHARE:
        return 1.0
    if collapse_share >= 0.20:
        return 0.65
    return 0.15


def psi_score(row: Dict[str, object], weights: Tuple[float, float, float, float, float], psi_lambda: float) -> float:
    w_t, w_d, w_g, w_s, w_r = weights
    t_mean = float(row["T_mean"])
    d_mean = float(row["D_effective_mean"])
    g_effective = float(row["G_effective"])
    s_network = float(row["S_network"])
    collapse = float(row["collapse_share"])
    variance = float(row["cluster_variance"])
    base = (
        w_t * (1.0 - t_mean)
        + w_d * d_mean
        + w_g * (1.0 - g_effective)
        + w_s * (1.0 - s_network)
        + w_r * regime_weight(collapse)
    )
    return base + (psi_lambda * variance)


def build_federation_run_cache(runs_per_cell: int, steps: int, seed_start: int) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    scenario_map = {scenario.name: scenario for scenario in v02.scenarios() if scenario.name in FEDERATION_SCENARIOS}
    global_index = 0
    for scenario_name in sorted(FEDERATION_SCENARIOS):
        scenario = scenario_map[scenario_name]
        for profile in v02.profiles():
            for run_index in range(runs_per_cell):
                seed = seed_start + global_index
                run_row, step_rows = v02.run_one(scenario, profile, run_index, seed, steps)
                event_steps = [int(row["step"]) for row in step_rows if float(row["collapse_share"]) >= 0.30]
                first_event_step = event_steps[0] if event_steps else ""
                rows.append(
                    {
                        "scenario": scenario_name,
                        "profile": profile.name,
                        "run_index": run_index,
                        "seed": seed,
                        "event_observed": int(first_event_step != ""),
                        "first_event_step": first_event_step,
                        "peak_collapse_share": run_row["collapse_share_peak"],
                        "step_rows": step_rows,
                    }
                )
                global_index += 1
    return rows


def run_psi_sweep(run_cache: Sequence[Dict[str, object]]) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    candidate_rows: List[Dict[str, object]] = []
    summary_rows: List[Dict[str, object]] = []

    for weight_name, w_t, w_d, w_g, w_s, w_r in WEIGHT_SETS:
        weights = (w_t, w_d, w_g, w_s, w_r)
        for psi_lambda in PSI_LAMBDAS:
            for threshold in PSI_THRESHOLDS:
                positives = 0
                negatives = 0
                detected_positive = 0
                on_time_positive = 0
                missed_positive = 0
                false_positive = 0
                leads: List[float] = []
                lags: List[float] = []

                for run in run_cache:
                    first_event = run["first_event_step"]
                    event_observed = bool(run["event_observed"])
                    if event_observed:
                        positives += 1
                    else:
                        negatives += 1

                    detect_step = ""
                    for row in run["step_rows"]:  # type: ignore[union-attr]
                        if psi_score(row, weights, psi_lambda) >= threshold:
                            detect_step = int(row["step"])
                            break

                    if event_observed:
                        if detect_step == "":
                            missed_positive += 1
                        else:
                            detected_positive += 1
                            event_step = int(first_event)
                            if int(detect_step) <= event_step:
                                on_time_positive += 1
                                leads.append(event_step - int(detect_step))
                            else:
                                lags.append(int(detect_step) - event_step)
                    elif detect_step != "":
                        false_positive += 1

                    candidate_rows.append(
                        {
                            "batch_id": BATCH_ID,
                            "weight_profile": weight_name,
                            "psi_lambda": psi_lambda,
                            "psi_lambda_locked": int(psi_lambda == v02.PSI_LAMBDA),
                            "psi_threshold": threshold,
                            "scenario": run["scenario"],
                            "profile": run["profile"],
                            "run_index": run["run_index"],
                            "seed": run["seed"],
                            "event_observed": int(event_observed),
                            "first_event_step": first_event,
                            "detect_step": detect_step,
                            "detected_before_or_at_event": int(event_observed and detect_step != "" and int(detect_step) <= int(first_event)),
                            "false_positive": int((not event_observed) and detect_step != ""),
                        }
                    )

                detected_tpr = detected_positive / max(1, positives)
                on_time_tpr = on_time_positive / max(1, positives)
                missed_rate = missed_positive / max(1, positives)
                false_positive_rate = false_positive / max(1, negatives)
                accepted = (
                    psi_lambda == v02.PSI_LAMBDA
                    and on_time_tpr >= 0.90
                    and false_positive_rate <= 0.10
                )
                summary_rows.append(
                    {
                        "batch_id": BATCH_ID,
                        "weight_profile": weight_name,
                        "psi_lambda": psi_lambda,
                        "psi_lambda_locked": int(psi_lambda == v02.PSI_LAMBDA),
                        "psi_threshold": threshold,
                        "positive_runs": positives,
                        "negative_runs": negatives,
                        "detected_true_positive_rate": round(detected_tpr, 6),
                        "on_time_true_positive_rate": round(on_time_tpr, 6),
                        "missed_detection_rate": round(missed_rate, 6),
                        "false_positive_rate": round(false_positive_rate, 6),
                        "avg_lead_steps": round(avg(leads), 6),
                        "avg_lag_steps": round(avg(lags), 6),
                        "accepted_candidate": int(accepted),
                    }
                )

    locked = [row for row in summary_rows if int(row["psi_lambda_locked"])]
    ranked = sorted(
        locked,
        key=lambda row: (
            -float(row["on_time_true_positive_rate"]),
            float(row["false_positive_rate"]),
            float(row["missed_detection_rate"]),
            -float(row["avg_lead_steps"]),
            float(row["psi_threshold"]),
        ),
    )
    if ranked:
        ranked[0]["recommended_locked_candidate"] = 1
        for row in summary_rows:
            if "recommended_locked_candidate" not in row:
                row["recommended_locked_candidate"] = 0
    return candidate_rows, summary_rows


def actual_topology_at(step: int) -> str:
    if step < 55:
        return "ring_mesh"
    if step < 80:
        return "centralizing"
    return "star_adjacent"


def run_topology_lag_suite(runs: int, seed_start: int, steps: int = 130) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    run_rows: List[Dict[str, object]] = []
    summary_groups: Dict[Tuple[int, int, float], List[Dict[str, object]]] = defaultdict(list)
    recheck_values = [1, 5, 10]
    detection_delay_values = [0, 5, 10, 20]
    misclassification_values = [0.0, 0.10, 0.25]

    global_index = 0
    for recheck_interval in recheck_values:
        for detection_delay in detection_delay_values:
            for misclassification_rate in misclassification_values:
                for run_index in range(runs):
                    seed = seed_start + global_index
                    rng = random.Random(seed)
                    detected = "ring_mesh"
                    pending_since: Dict[str, int] = {}
                    first_centralizing = ""
                    first_star = ""
                    detected_centralizing = ""
                    detected_star = ""
                    wrong_monitoring_steps = 0
                    star_undetected_steps = 0

                    for step in range(steps):
                        actual = actual_topology_at(step)
                        if actual == "centralizing" and first_centralizing == "":
                            first_centralizing = step
                        if actual == "star_adjacent" and first_star == "":
                            first_star = step
                        if actual != detected:
                            pending_since.setdefault(actual, step)

                        if step % recheck_interval == 0 and actual != detected:
                            age = step - pending_since.get(actual, step)
                            if age >= detection_delay:
                                if rng.random() >= misclassification_rate:
                                    detected = actual
                                    if actual == "centralizing" and detected_centralizing == "":
                                        detected_centralizing = step
                                    if actual == "star_adjacent" and detected_star == "":
                                        detected_star = step

                        if actual != detected:
                            wrong_monitoring_steps += 1
                        if actual == "star_adjacent" and detected != "star_adjacent":
                            star_undetected_steps += 1

                    centralizing_latency = (
                        int(detected_centralizing) - int(first_centralizing)
                        if first_centralizing != "" and detected_centralizing != ""
                        else ""
                    )
                    star_latency = (
                        int(detected_star) - int(first_star)
                        if first_star != "" and detected_star != ""
                        else ""
                    )
                    row = {
                        "batch_id": BATCH_ID,
                        "run_index": run_index,
                        "seed": seed,
                        "recheck_interval": recheck_interval,
                        "detection_delay": detection_delay,
                        "misclassification_rate": misclassification_rate,
                        "first_centralizing_step": first_centralizing,
                        "detected_centralizing_step": detected_centralizing,
                        "centralizing_latency_steps": centralizing_latency,
                        "first_star_adjacent_step": first_star,
                        "detected_star_adjacent_step": detected_star,
                        "star_adjacent_latency_steps": star_latency,
                        "wrong_monitoring_steps": wrong_monitoring_steps,
                        "star_adjacent_undetected_steps": star_undetected_steps,
                    }
                    run_rows.append(row)
                    summary_groups[(recheck_interval, detection_delay, misclassification_rate)].append(row)
                    global_index += 1

    summary_rows: List[Dict[str, object]] = []
    for (recheck_interval, detection_delay, misclassification_rate), rows in sorted(summary_groups.items()):
        central_lats = [float(row["centralizing_latency_steps"]) for row in rows if row["centralizing_latency_steps"] != ""]
        star_lats = [float(row["star_adjacent_latency_steps"]) for row in rows if row["star_adjacent_latency_steps"] != ""]
        summary_rows.append(
            {
                "batch_id": BATCH_ID,
                "recheck_interval": recheck_interval,
                "detection_delay": detection_delay,
                "misclassification_rate": misclassification_rate,
                "runs": len(rows),
                "centralizing_detection_rate": round(len(central_lats) / max(1, len(rows)), 6),
                "avg_centralizing_latency_steps": round(avg(central_lats), 6) if central_lats else "",
                "star_adjacent_detection_rate": round(len(star_lats) / max(1, len(rows)), 6),
                "avg_star_adjacent_latency_steps": round(avg(star_lats), 6) if star_lats else "",
                "avg_wrong_monitoring_steps": round(avg(float(row["wrong_monitoring_steps"]) for row in rows), 6),
                "avg_star_adjacent_undetected_steps": round(avg(float(row["star_adjacent_undetected_steps"]) for row in rows), 6),
            }
        )
    return run_rows, summary_rows


def run_hub_reproduction(output_dir: pathlib.Path) -> List[Dict[str, object]]:
    _v18_runs, v18_summary = v18.run_hub_redundancy_suite()
    v02_summary_path = pathlib.Path("grand_sim_v0_2") / "grand_sim_v0_2_scenario_summary.csv"
    v02_rows: List[Dict[str, str]] = []
    if v02_summary_path.exists():
        with v02_summary_path.open(newline="", encoding="utf-8") as handle:
            v02_rows = list(csv.DictReader(handle))

    rows: List[Dict[str, object]] = []
    v18_by_config = {str(row["config"]): row for row in v18_summary}
    mapping = [
        ("v18_2hub_balanced", "B", "hub_2_balanced"),
        ("v18_3hub_balanced", "C", "hub_3_balanced"),
        ("v18_2hub_unbalanced", "D", ""),
        ("v18_3hub_unbalanced", "E", ""),
    ]
    for comparison, config, v02_scenario in mapping:
        v18_row = v18_by_config[config]
        matching_v02 = [
            row
            for row in v02_rows
            if row.get("scenario") == v02_scenario and row.get("profile") == "mid_stress"
        ]
        v02_ignition = matching_v02[0]["sustained_ignition_rate"] if matching_v02 else ""
        rows.append(
            {
                "batch_id": BATCH_ID,
                "comparison": comparison,
                "v18_config": config,
                "v18_hub_count": v18_row["hub_count"],
                "v18_balanced": v18_row["balanced"],
                "v18_sustained_ignition_rate": round(float(v18_row["sustained_ignition_rate"]), 6),
                "v18_pct_collapsed": round(float(v18_row["pct_collapsed"]), 6),
                "v02_mid_stress_scenario": v02_scenario,
                "v02_mid_stress_sustained_ignition_rate": v02_ignition,
                "delta_v02_minus_v18": round(float(v02_ignition) - float(v18_row["sustained_ignition_rate"]), 6) if v02_ignition != "" else "",
            }
        )
    write_csv(output_dir / f"{OUTPUT_PREFIX}_hub_reproduction_comparison.csv", rows)
    return rows


def write_report(
    output_dir: pathlib.Path,
    psi_summary: Sequence[Dict[str, object]],
    topology_summary: Sequence[Dict[str, object]],
    hub_rows: Sequence[Dict[str, object]],
) -> None:
    locked = [row for row in psi_summary if int(row["psi_lambda_locked"])]
    recommended = next((row for row in locked if int(row.get("recommended_locked_candidate", 0))), locked[0] if locked else {})
    accepted_count = sum(int(row["accepted_candidate"]) for row in psi_summary)
    high_lag = max(topology_summary, key=lambda row: float(row["avg_wrong_monitoring_steps"]))

    lines = [
        "# SOE Grand Simulation v0.3 Focused Calibration Report",
        "",
        "## Scope",
        "",
        "v0.3 is a focused calibration/reproduction package, not a broad C00-C08 matrix.",
        "",
        "Focus areas:",
        "",
        "- CL02 Psi federation detector calibration.",
        "- CL09 topology detection lag and misclassification.",
        "- v18 hub-redundancy reproduction comparison.",
        "",
        "## Psi Sweep",
        "",
        f"- Accepted locked-lambda candidates: `{accepted_count}`.",
        f"- Recommended locked candidate: `{recommended}`.",
        "",
        "## Topology Lag",
        "",
        f"- Worst wrong-monitoring condition: `{high_lag}`.",
        "",
        "## Hub Reproduction",
        "",
        "| Comparison | v18 ignition | v0.2 mid-stress ignition | Delta |",
        "|---|---:|---:|---:|",
    ]
    for row in hub_rows:
        lines.append(
            f"| {row['comparison']} | {row['v18_sustained_ignition_rate']} | {row['v02_mid_stress_sustained_ignition_rate']} | {row['delta_v02_minus_v18']} |"
        )
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            f"- `{OUTPUT_PREFIX}_psi_sweep_runs.csv`",
            f"- `{OUTPUT_PREFIX}_psi_sweep_summary.csv`",
            f"- `{OUTPUT_PREFIX}_topology_lag_runs.csv`",
            f"- `{OUTPUT_PREFIX}_topology_lag_summary.csv`",
            f"- `{OUTPUT_PREFIX}_hub_reproduction_comparison.csv`",
        ]
    )
    (output_dir / f"{OUTPUT_PREFIX}_report.md").write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SOE Grand Simulation v0.3 focused calibration/reproduction package.")
    parser.add_argument("--runs-per-cell", type=int, default=DEFAULT_RUNS_PER_CELL)
    parser.add_argument("--steps", type=int, default=DEFAULT_STEPS)
    parser.add_argument("--seed-start", type=int, default=SEED_START)
    parser.add_argument("--output-dir", default=OUTPUT_PREFIX)
    parser.add_argument("--smoke", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = pathlib.Path(args.output_dir)
    runs_per_cell = args.runs_per_cell
    steps = args.steps
    if args.smoke:
        output_dir = pathlib.Path(f"{OUTPUT_PREFIX}_smoke")
        runs_per_cell = 1
        steps = 30

    run_cache = build_federation_run_cache(runs_per_cell, steps, args.seed_start)
    psi_runs, psi_summary = run_psi_sweep(run_cache)
    topology_runs, topology_summary = run_topology_lag_suite(
        runs=max(3, runs_per_cell),
        seed_start=args.seed_start + 100_000,
    )
    hub_rows = run_hub_reproduction(output_dir)

    write_csv(output_dir / f"{OUTPUT_PREFIX}_psi_sweep_runs.csv", psi_runs)
    write_csv(output_dir / f"{OUTPUT_PREFIX}_psi_sweep_summary.csv", psi_summary)
    write_csv(output_dir / f"{OUTPUT_PREFIX}_topology_lag_runs.csv", topology_runs)
    write_csv(output_dir / f"{OUTPUT_PREFIX}_topology_lag_summary.csv", topology_summary)
    write_report(output_dir, psi_summary, topology_summary, hub_rows)

    accepted = sum(int(row["accepted_candidate"]) for row in psi_summary)
    print(f"Wrote v0.3 focused outputs to {output_dir}")
    print(f"Psi accepted locked-lambda candidates: {accepted}")
    print(f"Topology lag rows: {len(topology_runs)}")


if __name__ == "__main__":
    main()
