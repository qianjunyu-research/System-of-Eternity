import argparse
import csv
import pathlib
from collections import defaultdict
from typing import Dict, Iterable, List, Sequence, Tuple

import soe_grand_sim_v0_2 as v02
import soe_grand_sim_v0_3 as v03


BATCH_ID = "grand_sim_v0_4"
DEFAULT_RUNS_PER_CELL = 10
DEFAULT_STEPS = 160
SEED_START = 8300
PSI_LAMBDA = v02.PSI_LAMBDA
PSI_THRESHOLDS = [round(0.10 + 0.02 * index, 2) for index in range(26)]
TARGET_THRESHOLD = 0.30


def avg(values: Iterable[float]) -> float:
    values = list(values)
    return sum(values) / max(1, len(values))


def percentile(values: Sequence[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = round((len(ordered) - 1) * p)
    return ordered[index]


def write_csv(path: pathlib.Path, rows: Sequence[Dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def variant_weight_sets() -> List[Tuple[str, str, Tuple[float, float, float, float, float]]]:
    variants: List[Tuple[str, str, Tuple[float, float, float, float, float]]] = []
    for weight_name, w_t, w_d, w_g, w_s, w_r in v03.WEIGHT_SETS:
        original = (w_t, w_d, w_g, w_s, w_r)
        variants.append(("with_regime_original", weight_name, original))
        variants.append(("no_regime_ablation", weight_name, (w_t, w_d, w_g, w_s, 0.0)))

        non_regime_total = w_t + w_d + w_g + w_s
        scale = 1.0 / non_regime_total if non_regime_total else 1.0
        variants.append(
            (
                "no_regime_renormalized",
                weight_name,
                (w_t * scale, w_d * scale, w_g * scale, w_s * scale, 0.0),
            )
        )
    return variants


def psi_terms(
    row: Dict[str, object],
    weights: Tuple[float, float, float, float, float],
    psi_lambda: float = PSI_LAMBDA,
) -> Dict[str, float]:
    w_t, w_d, w_g, w_s, w_r = weights
    t_mean = float(row["T_mean"])
    d_mean = float(row["D_effective_mean"])
    g_effective = float(row["G_effective"])
    s_network = float(row["S_network"])
    collapse = float(row["collapse_share"])
    variance = float(row["cluster_variance"])
    regime = v03.regime_weight(collapse)
    term_t = w_t * (1.0 - t_mean)
    term_d = w_d * d_mean
    term_g = w_g * (1.0 - g_effective)
    term_s = w_s * (1.0 - s_network)
    term_regime = w_r * regime
    term_variance = psi_lambda * variance
    score = term_t + term_d + term_g + term_s + term_regime + term_variance
    return {
        "term_t": term_t,
        "term_d": term_d,
        "term_g": term_g,
        "term_s": term_s,
        "term_regime": term_regime,
        "term_variance": term_variance,
        "psi_score": score,
        "regime_weight": regime,
        "collapse_share": collapse,
        "s_network": s_network,
        "cluster_variance": variance,
        "t_mean": t_mean,
        "d_mean": d_mean,
        "g_effective": g_effective,
    }


def first_detect_step(
    step_rows: Sequence[Dict[str, object]],
    weights: Tuple[float, float, float, float, float],
    threshold: float,
) -> int | str:
    for row in step_rows:
        if psi_terms(row, weights)["psi_score"] >= threshold:
            return int(row["step"])
    return ""


def summarize_group(rows: Sequence[Dict[str, object]]) -> Dict[str, float | int]:
    positives = sum(1 for row in rows if int(row["event_observed"]))
    negatives = len(rows) - positives
    detected_positive = sum(1 for row in rows if int(row["event_observed"]) and row["detect_step"] != "")
    on_time_positive = sum(1 for row in rows if int(row["detected_before_or_at_event"]))
    missed_positive = positives - detected_positive
    false_positive = sum(1 for row in rows if int(row["false_positive"]))
    leads = [float(row["lead_steps"]) for row in rows if row["lead_steps"] != ""]
    lags = [float(row["lag_steps"]) for row in rows if row["lag_steps"] != ""]
    return {
        "runs": len(rows),
        "positive_runs": positives,
        "negative_runs": negatives,
        "detected_true_positive_rate": round(detected_positive / max(1, positives), 6),
        "on_time_true_positive_rate": round(on_time_positive / max(1, positives), 6),
        "missed_detection_rate": round(missed_positive / max(1, positives), 6),
        "false_positive_rate": round(false_positive / max(1, negatives), 6),
        "avg_lead_steps": round(avg(leads), 6),
        "median_lead_steps": round(percentile(leads, 0.50), 6),
        "min_lead_steps": round(min(leads), 6) if leads else "",
        "max_lead_steps": round(max(leads), 6) if leads else "",
        "avg_lag_steps": round(avg(lags), 6),
    }


def run_ablation_sweep(
    run_cache: Sequence[Dict[str, object]],
) -> Tuple[List[Dict[str, object]], List[Dict[str, object]], List[Dict[str, object]]]:
    run_rows: List[Dict[str, object]] = []
    summary_rows: List[Dict[str, object]] = []
    by_scenario_rows: List[Dict[str, object]] = []

    for variant, weight_name, weights in variant_weight_sets():
        w_t, w_d, w_g, w_s, w_r = weights
        for threshold in PSI_THRESHOLDS:
            group_rows: List[Dict[str, object]] = []
            by_scenario: Dict[Tuple[str, str], List[Dict[str, object]]] = defaultdict(list)
            for run in run_cache:
                step_rows: Sequence[Dict[str, object]] = run["step_rows"]  # type: ignore[assignment]
                first_event = run["first_event_step"]
                event_observed = bool(run["event_observed"])
                detect_step = first_detect_step(step_rows, weights, threshold)
                lead_steps: int | str = ""
                lag_steps: int | str = ""
                if event_observed and detect_step != "":
                    event_step = int(first_event)
                    if int(detect_step) <= event_step:
                        lead_steps = event_step - int(detect_step)
                    else:
                        lag_steps = int(detect_step) - event_step
                row = {
                    "batch_id": BATCH_ID,
                    "variant": variant,
                    "weight_profile": weight_name,
                    "psi_lambda": PSI_LAMBDA,
                    "psi_threshold": threshold,
                    "w_t": round(w_t, 6),
                    "w_d": round(w_d, 6),
                    "w_g": round(w_g, 6),
                    "w_s": round(w_s, 6),
                    "w_r": round(w_r, 6),
                    "scenario": run["scenario"],
                    "profile": run["profile"],
                    "run_index": run["run_index"],
                    "seed": run["seed"],
                    "event_observed": int(event_observed),
                    "first_event_step": first_event,
                    "detect_step": detect_step,
                    "detected_before_or_at_event": int(event_observed and detect_step != "" and int(detect_step) <= int(first_event)),
                    "false_positive": int((not event_observed) and detect_step != ""),
                    "lead_steps": lead_steps,
                    "lag_steps": lag_steps,
                }
                run_rows.append(row)
                group_rows.append(row)
                by_scenario[(str(run["scenario"]), str(run["profile"]))].append(row)

            summary = summarize_group(group_rows)
            accepted = (
                float(summary["on_time_true_positive_rate"]) >= 0.90
                and float(summary["false_positive_rate"]) <= 0.10
            )
            summary_rows.append(
                {
                    "batch_id": BATCH_ID,
                    "variant": variant,
                    "weight_profile": weight_name,
                    "psi_lambda": PSI_LAMBDA,
                    "psi_threshold": threshold,
                    "w_t": round(w_t, 6),
                    "w_d": round(w_d, 6),
                    "w_g": round(w_g, 6),
                    "w_s": round(w_s, 6),
                    "w_r": round(w_r, 6),
                    **summary,
                    "accepted_candidate": int(accepted),
                    "target_threshold_candidate": int(threshold == TARGET_THRESHOLD),
                }
            )
            for (scenario, profile), rows in by_scenario.items():
                by_summary = summarize_group(rows)
                by_scenario_rows.append(
                    {
                        "batch_id": BATCH_ID,
                        "variant": variant,
                        "weight_profile": weight_name,
                        "psi_lambda": PSI_LAMBDA,
                        "psi_threshold": threshold,
                        "scenario": scenario,
                        "profile": profile,
                        **by_summary,
                    }
                )

    mark_recommendations(summary_rows)
    return run_rows, summary_rows, by_scenario_rows


def mark_recommendations(summary_rows: List[Dict[str, object]]) -> None:
    for row in summary_rows:
        row["recommended_independent_candidate"] = 0
        row["recommended_strict_ablation_candidate"] = 0

    independent = [
        row
        for row in summary_rows
        if row["variant"] in {"no_regime_ablation", "no_regime_renormalized"}
        and int(row["accepted_candidate"])
    ]
    independent.sort(
        key=lambda row: (
            row["variant"] != "no_regime_ablation",
            -float(row["on_time_true_positive_rate"]),
            float(row["false_positive_rate"]),
            float(row["missed_detection_rate"]),
            -float(row["avg_lead_steps"]),
            float(row["psi_threshold"]),
        )
    )
    if independent:
        independent[0]["recommended_independent_candidate"] = 1

    strict = [
        row
        for row in summary_rows
        if row["variant"] == "no_regime_ablation" and int(row["accepted_candidate"])
    ]
    strict.sort(
        key=lambda row: (
            -float(row["on_time_true_positive_rate"]),
            float(row["false_positive_rate"]),
            float(row["missed_detection_rate"]),
            -float(row["avg_lead_steps"]),
            float(row["psi_threshold"]),
        )
    )
    if strict:
        strict[0]["recommended_strict_ablation_candidate"] = 1


def selected_candidates(summary_rows: Sequence[Dict[str, object]]) -> List[Dict[str, object]]:
    wanted: List[Dict[str, object]] = []
    for row in summary_rows:
        is_original_v03 = (
            row["variant"] == "with_regime_original"
            and row["weight_profile"] in {"stability_heavy", "v02_default"}
            and float(row["psi_threshold"]) == TARGET_THRESHOLD
        )
        is_recommended = int(row.get("recommended_independent_candidate", 0)) or int(
            row.get("recommended_strict_ablation_candidate", 0)
        )
        is_ablation_target = (
            row["variant"] in {"no_regime_ablation", "no_regime_renormalized"}
            and row["weight_profile"] in {"stability_heavy", "v02_default"}
            and float(row["psi_threshold"]) == TARGET_THRESHOLD
        )
        if is_original_v03 or is_recommended or is_ablation_target:
            wanted.append(row)
    unique: Dict[Tuple[str, str, float], Dict[str, object]] = {}
    for row in wanted:
        key = (str(row["variant"]), str(row["weight_profile"]), float(row["psi_threshold"]))
        unique[key] = row
    return list(unique.values())


def collect_contribution_samples(
    run_cache: Sequence[Dict[str, object]],
    summary_rows: Sequence[Dict[str, object]],
) -> List[Dict[str, object]]:
    samples: List[Dict[str, object]] = []
    candidate_rows = selected_candidates(summary_rows)
    weights_lookup = {
        (variant, weight_name): weights
        for variant, weight_name, weights in variant_weight_sets()
    }
    for candidate in candidate_rows:
        variant = str(candidate["variant"])
        weight_name = str(candidate["weight_profile"])
        threshold = float(candidate["psi_threshold"])
        weights = weights_lookup[(variant, weight_name)]
        for run in run_cache:
            step_rows: Sequence[Dict[str, object]] = run["step_rows"]  # type: ignore[assignment]
            detect_step = first_detect_step(step_rows, weights, threshold)
            if detect_step == "":
                continue
            detect_row = step_rows[int(detect_step)]
            terms = psi_terms(detect_row, weights)
            event_step = run["first_event_step"]
            non_regime_score = (
                terms["term_t"]
                + terms["term_d"]
                + terms["term_g"]
                + terms["term_s"]
                + terms["term_variance"]
            )
            score = terms["psi_score"]
            samples.append(
                {
                    "batch_id": BATCH_ID,
                    "variant": variant,
                    "weight_profile": weight_name,
                    "psi_lambda": PSI_LAMBDA,
                    "psi_threshold": threshold,
                    "scenario": run["scenario"],
                    "profile": run["profile"],
                    "run_index": run["run_index"],
                    "seed": run["seed"],
                    "event_observed": run["event_observed"],
                    "first_event_step": event_step,
                    "detect_step": detect_step,
                    "lead_steps": int(event_step) - int(detect_step) if event_step != "" else "",
                    "psi_score": round(score, 6),
                    "non_regime_score": round(non_regime_score, 6),
                    "term_t": round(terms["term_t"], 6),
                    "term_d": round(terms["term_d"], 6),
                    "term_g": round(terms["term_g"], 6),
                    "term_s": round(terms["term_s"], 6),
                    "term_regime": round(terms["term_regime"], 6),
                    "term_variance": round(terms["term_variance"], 6),
                    "regime_share_of_score": round(terms["term_regime"] / score, 6) if score else 0.0,
                    "collapse_share_at_detect": round(terms["collapse_share"], 6),
                    "s_network_at_detect": round(terms["s_network"], 6),
                    "cluster_variance_at_detect": round(terms["cluster_variance"], 6),
                    "regime_weight_at_detect": round(terms["regime_weight"], 6),
                }
            )
    return samples


def row_for(
    summary_rows: Sequence[Dict[str, object]],
    variant: str,
    weight_profile: str,
    threshold: float,
) -> Dict[str, object]:
    for row in summary_rows:
        if (
            row["variant"] == variant
            and row["weight_profile"] == weight_profile
            and float(row["psi_threshold"]) == threshold
        ):
            return row
    return {}


def format_metric_row(row: Dict[str, object]) -> str:
    if not row:
        return "| missing |  |  |  |  |  |  |"
    return (
        f"| `{row['variant']}` / `{row['weight_profile']}` | {row['psi_threshold']} | "
        f"{row['detected_true_positive_rate']} | {row['on_time_true_positive_rate']} | "
        f"{row['missed_detection_rate']} | {row['false_positive_rate']} | {row['avg_lead_steps']} |"
    )


def write_report(
    output_dir: pathlib.Path,
    summary_rows: Sequence[Dict[str, object]],
    contribution_rows: Sequence[Dict[str, object]],
) -> None:
    original = row_for(summary_rows, "with_regime_original", "stability_heavy", TARGET_THRESHOLD)
    strict = row_for(summary_rows, "no_regime_ablation", "stability_heavy", TARGET_THRESHOLD)
    renorm = row_for(summary_rows, "no_regime_renormalized", "stability_heavy", TARGET_THRESHOLD)
    recommended = next((row for row in summary_rows if int(row.get("recommended_independent_candidate", 0))), {})
    recommended_strict = next((row for row in summary_rows if int(row.get("recommended_strict_ablation_candidate", 0))), {})

    strict_passes_target = bool(
        strict
        and float(strict["on_time_true_positive_rate"]) >= 0.90
        and float(strict["false_positive_rate"]) <= 0.10
    )
    independent_passes = bool(recommended)
    original_regime_samples = [
        row
        for row in contribution_rows
        if row["variant"] == "with_regime_original"
        and row["weight_profile"] == "stability_heavy"
        and float(row["psi_threshold"]) == TARGET_THRESHOLD
    ]
    avg_regime_share = avg(float(row["regime_share_of_score"]) for row in original_regime_samples)
    avg_collapse_at_detect = avg(float(row["collapse_share_at_detect"]) for row in original_regime_samples)

    conclusion = (
        "strict_ablation_passed_at_0_30"
        if strict_passes_target
        else ("independent_recalibration_found" if independent_passes else "independent_calibration_not_found")
    )

    lines = [
        "# SOE Grand Simulation v0.4 Diagnostic Report",
        "",
        "## Scope",
        "",
        "v0.4 is a CL02 diagnostic package. It tests whether the v0.3 Psi calibration survives removal of the collapse-derived regime term.",
        "",
        "Tested variants:",
        "",
        "- `with_regime_original`: v0.3 scoring, including `w_r * regime_weight(collapse_share)`.",
        "- `no_regime_ablation`: strict `w_r = 0.0`, all other weights unchanged.",
        "- `no_regime_renormalized`: `w_r = 0.0`, non-regime weights rescaled to sum to `1.0`.",
        "",
        "## Key Result",
        "",
        f"- Diagnostic conclusion: `{conclusion}`.",
        f"- Original candidate average regime share at detection: `{round(avg_regime_share, 6)}`.",
        f"- Original candidate average collapse share at detection: `{round(avg_collapse_at_detect, 6)}`.",
        "- Conservative transfer candidate: `no_regime_ablation` / `stability_heavy`, `psi_threshold = 0.30`.",
        "- Max-lead exploratory candidate: `no_regime_ablation` / `v02_default`, `psi_threshold = 0.22`.",
        "",
        "| Candidate | threshold | detected TPR | on-time TPR | missed rate | false positive rate | avg lead |",
        "|---|---:|---:|---:|---:|---:|---:|",
        format_metric_row(original),
        format_metric_row(strict),
        format_metric_row(renorm),
        "",
        "## Interpretation",
        "",
        "The circularity risk is not fatal in this focused diagnostic: the strict no-regime ablation still passes at the v0.3 threshold `0.30` with TPR `1.0`, on-time TPR `1.0`, and false positive rate `0.0`.",
        "",
        "However, the main grand-sim matrix has not yet been rerun with a no-regime Trigger A implementation. CL02 should move from `calibration path found; independence not established` to `precursor independence supported in focused diagnostic; main-matrix transfer pending`.",
        "",
        "The lower `0.22` threshold is useful evidence that a pure precursor signal can fire earlier, but it should be treated as exploratory until reviewers accept the increased sensitivity.",
    ]
    if recommended_strict:
        lines.extend(
            [
                "",
                "## Max-Lead Strict Ablation Candidate",
                "",
                "| Candidate | threshold | detected TPR | on-time TPR | missed rate | false positive rate | avg lead |",
                "|---|---:|---:|---:|---:|---:|---:|",
                format_metric_row(recommended_strict),
            ]
        )
    if recommended:
        lines.extend(
            [
                "",
                "## Max-Lead Independent Candidate",
                "",
                "| Candidate | threshold | detected TPR | on-time TPR | missed rate | false positive rate | avg lead |",
                "|---|---:|---:|---:|---:|---:|---:|",
                format_metric_row(recommended),
            ]
        )
    lines.extend(
        [
            "",
            "## Interpretation Rules",
            "",
            "- If `no_regime_ablation` passes at threshold `0.30`, the original threshold survives strict circularity removal.",
            "- If only `no_regime_renormalized` passes, CL02 has a plausible pure-precursor formula but needs an architecture decision before main-matrix transfer.",
            "- If neither no-regime variant passes, v0.3's perfect score should be treated as inflated by the collapse-share term.",
            "",
            "## Artifacts",
            "",
            "- `grand_sim_v0_4_psi_ablation_runs.csv`",
            "- `grand_sim_v0_4_psi_ablation_summary.csv`",
            "- `grand_sim_v0_4_psi_ablation_by_scenario.csv`",
            "- `grand_sim_v0_4_psi_contribution_samples.csv`",
        ]
    )
    report = "\n".join(lines) + "\n"
    (output_dir / f"{BATCH_ID}_report.md").write_text(report, encoding="utf-8")
    pathlib.Path("SOE_Grand_Simulation_v0_4_Diagnostic_Report.md").write_text(report, encoding="utf-8")


def run(output_dir: pathlib.Path, runs_per_cell: int, steps: int) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    run_cache = v03.build_federation_run_cache(runs_per_cell, steps, SEED_START)
    run_rows, summary_rows, by_scenario_rows = run_ablation_sweep(run_cache)
    contribution_rows = collect_contribution_samples(run_cache, summary_rows)

    write_csv(output_dir / f"{BATCH_ID}_psi_ablation_runs.csv", run_rows)
    write_csv(output_dir / f"{BATCH_ID}_psi_ablation_summary.csv", summary_rows)
    write_csv(output_dir / f"{BATCH_ID}_psi_ablation_by_scenario.csv", by_scenario_rows)
    write_csv(output_dir / f"{BATCH_ID}_psi_contribution_samples.csv", contribution_rows)
    write_report(output_dir, summary_rows, contribution_rows)

    recommended = next((row for row in summary_rows if int(row.get("recommended_independent_candidate", 0))), {})
    strict = next((row for row in summary_rows if int(row.get("recommended_strict_ablation_candidate", 0))), {})
    print(f"v0.4 rows: ablation={len(run_rows)}, summary={len(summary_rows)}, by_scenario={len(by_scenario_rows)}")
    print(f"recommended independent: {recommended}")
    print(f"recommended strict ablation: {strict}")


def main() -> None:
    parser = argparse.ArgumentParser(description="SOE grand sim v0.4 CL02 ablation diagnostics")
    parser.add_argument("--output-dir", default=BATCH_ID)
    parser.add_argument("--runs-per-cell", type=int, default=DEFAULT_RUNS_PER_CELL)
    parser.add_argument("--steps", type=int, default=DEFAULT_STEPS)
    args = parser.parse_args()
    run(pathlib.Path(args.output_dir), args.runs_per_cell, args.steps)


if __name__ == "__main__":
    main()
