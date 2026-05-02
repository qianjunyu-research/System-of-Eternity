import argparse
import pathlib
from dataclasses import asdict
from typing import Dict, List

from governance_falsification import choose_continuous_targets, run_custom_simulation
from governance_integration import build_integrated_config, make_integrated_step_function
from governance_loop_sim import Config, apply_overrides, build_config, clamp, default_parameters, write_csv
from governance_regime_scan import run_regime_batch


def build_disturbance_high(base_config: Config) -> Config:
    integrated = build_integrated_config(base_config)
    return Config(
        **{
            **asdict(integrated),
            "shock_prob": 0.15,
            "shock_impact": 0.48,
        }
    )


def run_trajectory_analysis(
    base_config: Config,
    *,
    runs: int,
    steps: int,
    seed: int,
    f_min: float,
    alpha_gov: float,
) -> List[Dict[str, float]]:
    config = Config(
        **{
            **asdict(build_disturbance_high(base_config)),
            "governance_coupling_floor": f_min,
            "governance_coupling_alpha": alpha_gov,
        }
    )

    histories = []
    for run_index in range(runs):
        histories.append(
            run_custom_simulation(
                config=config,
                steps=steps,
                seed=seed + run_index,
                direct_controller=choose_continuous_targets,
                step_fn=make_integrated_step_function(),
                controller_label="trajectory_analysis_20pct",
            )
        )

    rows: List[Dict[str, float]] = []
    for step in range(steps):
        batch = [history[step] for history in histories]
        rows.append(
            {
                "step": step,
                "f_min": f_min,
                "alpha_gov": alpha_gov,
                "avg_stability": sum(row["stability"] for row in batch) / len(batch),
                "avg_trust": sum(row["trust"] for row in batch) / len(batch),
                "avg_disturbance": sum(row["disturbance"] for row in batch) / len(batch),
                "avg_cognitive_distortion": sum(row["cognitive_distortion"] for row in batch) / len(batch),
                "avg_governance_coupling_k": sum(row["governance_coupling_k"] for row in batch) / len(batch),
                "avg_disturbance_damping_target": sum(row["disturbance_damping_target"] for row in batch) / len(batch),
            }
        )
    return rows


def run_g_dynamic_verification(
    base_config: Config,
    *,
    steps: int,
    seed: int,
    f_min: float,
    alpha_gov: float,
) -> List[Dict[str, float]]:
    config = Config(
        **{
            **asdict(build_disturbance_high(base_config)),
            "governance_coupling_floor": f_min,
            "governance_coupling_alpha": alpha_gov,
        }
    )

    history = run_custom_simulation(
        config=config,
        steps=steps,
        seed=seed,
        direct_controller=choose_continuous_targets,
        step_fn=make_integrated_step_function(),
        controller_label="g_dynamic_verification",
    )

    rows: List[Dict[str, float]] = []
    for idx in range(1, len(history)):
        previous = history[idx - 1]
        current = history[idx]
        predicted_next = clamp(
            previous["governance_coupling_k"]
            + (alpha_gov * (current["disturbance_damping_target"] - previous["governance_coupling_k"])),
            low=f_min,
            high=config.max_disturbance_damping_effect,
        )
        error = current["governance_coupling_k"] - predicted_next
        rows.append(
            {
                "step": int(current["step"]),
                "f_min": f_min,
                "alpha_gov": alpha_gov,
                "k_t_minus_1": previous["governance_coupling_k"],
                "target_t": current["disturbance_damping_target"],
                "predicted_k_t": predicted_next,
                "observed_k_t": current["governance_coupling_k"],
                "abs_error": abs(error),
            }
        )
    return rows


def build_fine_values(start: float, stop: float, step: float) -> List[float]:
    values: List[float] = []
    cursor = start
    while cursor <= stop + 1e-9:
        values.append(round(cursor, 2))
        cursor += step
    return values


def run_fine_sweep(
    base_config: Config,
    *,
    runs: int,
    steps: int,
    seed: int,
    alpha_gov: float,
    f_values: List[float],
) -> (List[Dict[str, object]], List[Dict[str, object]]):
    disturbance_high = build_disturbance_high(base_config)
    summary_rows: List[Dict[str, object]] = []
    raw_rows: List[Dict[str, object]] = []

    for f_min in f_values:
        scenario = f"fine_fmin_{f_min:.2f}_agov_{alpha_gov:.2f}".replace(".", "")
        config = Config(
            **{
                **asdict(disturbance_high),
                "governance_coupling_floor": f_min,
                "governance_coupling_alpha": alpha_gov,
            }
        )
        summary_row, raw_row_set = run_regime_batch(
            config,
            test_name="blocking_fine_sweep_v13",
            scenario=scenario,
            runs=runs,
            steps=steps,
            seed=seed,
            note=f"Fine sweep with f_min={f_min:.2f}, alpha_gov={alpha_gov:.2f} under disturbance_high.",
        )
        summary_rows.append(summary_row)
        raw_rows.extend(raw_row_set)

    return summary_rows, raw_rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run requested v1.3 follow-up simulations.")
    parser.add_argument("--runs", type=int, default=30)
    parser.add_argument("--steps", type=int, default=150)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--traj-f-min", type=float, default=0.20)
    parser.add_argument("--traj-alpha-gov", type=float, default=0.10)
    parser.add_argument("--fine-alpha-gov", type=float, default=0.10)
    parser.add_argument("--fine-start", type=float, default=0.26)
    parser.add_argument("--fine-stop", type=float, default=0.32)
    parser.add_argument("--fine-step", type=float, default=0.01)
    parser.add_argument("--override", action="append", default=[])
    parser.add_argument("--trajectory-output", type=pathlib.Path, default=pathlib.Path("v13_trajectory_analysis_fmin_020.csv"))
    parser.add_argument("--g-verify-output", type=pathlib.Path, default=pathlib.Path("v13_g_dynamic_verification.csv"))
    parser.add_argument("--fine-summary-output", type=pathlib.Path, default=pathlib.Path("v13_fine_sweep_026_032_summary.csv"))
    parser.add_argument("--fine-runs-output", type=pathlib.Path, default=pathlib.Path("v13_fine_sweep_026_032_runs.csv"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    params = apply_overrides(default_parameters(), args.override)
    base_config = build_config(params)

    trajectory_rows = run_trajectory_analysis(
        base_config,
        runs=args.runs,
        steps=args.steps,
        seed=args.seed,
        f_min=args.traj_f_min,
        alpha_gov=args.traj_alpha_gov,
    )
    write_csv(args.trajectory_output, trajectory_rows)

    verify_rows = run_g_dynamic_verification(
        base_config,
        steps=args.steps,
        seed=args.seed,
        f_min=args.traj_f_min,
        alpha_gov=args.traj_alpha_gov,
    )
    write_csv(args.g_verify_output, verify_rows)

    fine_values = build_fine_values(args.fine_start, args.fine_stop, args.fine_step)
    fine_summary_rows, fine_run_rows = run_fine_sweep(
        base_config,
        runs=args.runs,
        steps=args.steps,
        seed=args.seed,
        alpha_gov=args.fine_alpha_gov,
        f_values=fine_values,
    )
    write_csv(args.fine_summary_output, fine_summary_rows)
    write_csv(args.fine_runs_output, fine_run_rows)

    max_abs_error = max((float(row["abs_error"]) for row in verify_rows), default=0.0)
    print(f"Saved trajectory analysis to {args.trajectory_output}")
    print(f"Saved G(t) dynamic verification to {args.g_verify_output} (max_abs_error={max_abs_error:.10f})")
    print(f"Saved fine sweep summary to {args.fine_summary_output}")
    print(f"Saved fine sweep runs to {args.fine_runs_output}")


if __name__ == "__main__":
    main()
