import pathlib
from dataclasses import asdict
from typing import Dict, List

from governance_integration import build_integrated_config
from governance_loop_sim import Config, write_csv
from governance_network_sim import run_network


def build_locked_config() -> Config:
    base = build_integrated_config(Config())
    return Config(
        **{
            **asdict(base),
            "disturbance_noise": 0.055,
            "governance_coupling_floor": 0.30,
            "governance_coupling_alpha": 0.10,
            "shock_prob": 0.15,
            "shock_impact": 0.48,
            "noise_level": 0.055,
            "execution_delay": 0.0,
            "max_delay": 0.0,
        }
    )


def summarize_per_run(nodes, run_index: int, seed: int, threshold: float, k_d_value: float) -> Dict[str, object]:
    hub = nodes[0]
    peripherals = nodes[1:]
    hub_stabilities = [row["stability"] for row in hub.history]

    peripheral_failure_share_by_step: List[float] = []
    for step in range(len(hub.history)):
        step_rows = [node.history[step] for node in peripherals]
        failed = sum(1 for row in step_rows if row["stability"] < threshold)
        peripheral_failure_share_by_step.append(failed / max(1, len(peripherals)))

    sustained = False
    onset_step = ""
    longest = 0
    run_len = 0
    run_start = None
    for step, share in enumerate(peripheral_failure_share_by_step):
        if share >= 0.80:
            run_len += 1
            if run_start is None:
                run_start = step
        else:
            if run_len > longest:
                longest = run_len
            if run_len >= 10 and not sustained:
                sustained = True
                onset_step = run_start
            run_len = 0
            run_start = None
    if run_len > longest:
        longest = run_len
    if run_len >= 10 and not sustained:
        sustained = True
        onset_step = run_start

    peripheral_last_step = [node.history[-1] for node in peripherals]
    final_cooperation = sum(row["trust"] for row in peripheral_last_step) / max(1, len(peripherals))
    final_trust = final_cooperation
    collapsed = 1 if peripheral_failure_share_by_step[-1] >= 0.80 else 0

    return {
        "k_D_value": k_d_value,
        "run_index": run_index,
        "seed": seed,
        "hub_final_stability": hub_stabilities[-1],
        "hub_min_stability": min(hub_stabilities),
        "peripheral_failure_rate": sum(peripheral_failure_share_by_step) / len(peripheral_failure_share_by_step),
        "peripheral_failure_peak": max(peripheral_failure_share_by_step),
        "sustained_ignition_observed": int(sustained),
        "ignition_onset_step": onset_step,
        "ignition_duration_steps": longest,
        "final_cooperation": final_cooperation,
        "final_trust": final_trust,
        "collapsed": collapsed,
    }


def main() -> None:
    config = build_locked_config()
    k_d_values = [0.05, 0.07, 0.09, 0.10, 0.11, 0.12, 0.13, 0.15]
    runs = 30
    steps = 150
    seed_start = 42
    node_count = 60

    run_rows: List[Dict[str, object]] = []
    summary_rows: List[Dict[str, object]] = []

    for k_d_value in k_d_values:
        scenario_rows = []
        for run_index in range(runs):
            seed = seed_start + run_index
            nodes, _ = run_network(
                config,
                node_count=node_count,
                steps=steps,
                run_seed=seed,
                coupled=True,
                k_d=k_d_value,
                k_c=0.10,
                migration_rate=0.20,
                topology="star",
                hub_disturbance=0.8,
            )
            row = summarize_per_run(nodes, run_index, seed, config.stability_threshold, k_d_value)
            run_rows.append(row)
            scenario_rows.append(row)

        ignition_rows = [r for r in scenario_rows if r["ignition_onset_step"] != ""]
        summary_rows.append(
            {
                "k_D_value": k_d_value,
                "runs": runs,
                "sustained_ignition_rate": sum(int(r["sustained_ignition_observed"]) for r in scenario_rows) / runs,
                "avg_peripheral_failure_rate": sum(float(r["peripheral_failure_rate"]) for r in scenario_rows) / runs,
                "avg_peripheral_failure_peak": sum(float(r["peripheral_failure_peak"]) for r in scenario_rows) / runs,
                "avg_ignition_onset_step": (
                    sum(float(r["ignition_onset_step"]) for r in ignition_rows) / len(ignition_rows)
                    if ignition_rows
                    else ""
                ),
                "avg_hub_min_stability": sum(float(r["hub_min_stability"]) for r in scenario_rows) / runs,
                "avg_final_cooperation": sum(float(r["final_cooperation"]) for r in scenario_rows) / runs,
                "pct_collapsed": sum(int(r["collapsed"]) for r in scenario_rows) / runs,
            }
        )

    write_csv(pathlib.Path("star_ceiling_sweep_runs.csv"), run_rows)
    write_csv(pathlib.Path("star_ceiling_sweep_summary.csv"), summary_rows)

    safe_rows = [row for row in summary_rows if float(row["sustained_ignition_rate"]) < 0.05]
    first_safe = safe_rows[0]["k_D_value"] if safe_rows else "none_in_sweep"

    ignition_rates = [float(row["sustained_ignition_rate"]) for row in summary_rows]
    ignition_drop_shape = "cliff" if any(abs(a - b) >= 0.20 for a, b in zip(ignition_rates, ignition_rates[1:])) else "gradient"
    provisional_safe = any(abs(float(row["k_D_value"]) - 0.10) < 1e-9 and float(row["sustained_ignition_rate"]) < 0.05 for row in summary_rows)

    note_lines = [
        f"First k_D where sustained_ignition_rate < 0.05: {first_safe}.",
        f"Ignition transition shape across sweep: {ignition_drop_shape}.",
        f"Recommended locked ceiling for star topology: {first_safe if first_safe != 'none_in_sweep' else '< 0.05 (requires lower test range)'}.",
        f"Provisional 0.10 ceiling status: {'confirmed safe' if provisional_safe else 'requires further reduction'}.",
        "Observed anomaly: hub stability remains comparatively high while peripheral failure can still surge in ignition regimes.",
    ]
    pathlib.Path("star_ceiling_note.txt").write_text("\n".join(note_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
