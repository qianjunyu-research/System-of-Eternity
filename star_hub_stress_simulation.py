import pathlib
from dataclasses import asdict
from typing import Dict, List, Tuple

from governance_loop_sim import Config, write_csv
from governance_network_sim import run_network
from governance_integration import build_integrated_config


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


def summarize_per_run(nodes, run_index: int, seed: int, threshold: float) -> Dict[str, object]:
    hub = nodes[0]
    peripherals = nodes[1:]

    hub_stabilities = [row["stability"] for row in hub.history]
    peripheral_failure_share_by_step: List[float] = []
    peripheral_avg_disturbance: List[float] = []
    for step in range(len(hub.history)):
        step_rows = [node.history[step] for node in peripherals]
        failed = sum(1 for row in step_rows if row["stability"] < threshold)
        peripheral_failure_share_by_step.append(failed / max(1, len(peripherals)))
        peripheral_avg_disturbance.append(sum(row["disturbance"] for row in step_rows) / max(1, len(peripherals)))

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

    final_cooperation = sum(row["trust"] for row in [node.history[-1] for node in peripherals]) / max(1, len(peripherals))
    final_trust = final_cooperation
    disturbance_first = 1 if peripheral_avg_disturbance[0] <= max(peripheral_avg_disturbance) else 0
    collapsed = 1 if peripheral_failure_share_by_step[-1] >= 0.80 else 0
    failure_reason = "sustained_ignition" if sustained else ("peripheral_collapse" if collapsed else "bounded")

    return {
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
        "disturbance_first": disturbance_first,
        "collapsed": collapsed,
        "failure_reason": failure_reason,
    }


def main() -> None:
    runs = 30
    steps = 150
    seed_start = 42
    node_count = 60
    config = build_locked_config()

    run_rows: List[Dict[str, object]] = []
    for run_index in range(runs):
        seed = seed_start + run_index
        nodes, _ = run_network(
            config,
            node_count=node_count,
            steps=steps,
            run_seed=seed,
            coupled=True,
            k_d=0.15,
            k_c=0.10,
            migration_rate=0.20,
            topology="star",
            hub_disturbance=0.8,
        )
        run_rows.append(summarize_per_run(nodes, run_index, seed, config.stability_threshold))

    summary_row = {
        "scenario": "star_hub_stress",
        "runs": runs,
        "sustained_ignition_rate": sum(int(r["sustained_ignition_observed"]) for r in run_rows) / runs,
        "avg_peripheral_failure_rate": sum(float(r["peripheral_failure_rate"]) for r in run_rows) / runs,
        "avg_peripheral_failure_peak": sum(float(r["peripheral_failure_peak"]) for r in run_rows) / runs,
        "avg_ignition_onset_step": (
            sum(float(r["ignition_onset_step"]) for r in run_rows if r["ignition_onset_step"] != "")
            / max(1, sum(1 for r in run_rows if r["ignition_onset_step"] != ""))
        ),
        "avg_hub_min_stability": sum(float(r["hub_min_stability"]) for r in run_rows) / runs,
        "avg_final_cooperation": sum(float(r["final_cooperation"]) for r in run_rows) / runs,
        "avg_final_trust": sum(float(r["final_trust"]) for r in run_rows) / runs,
    }

    write_csv(pathlib.Path("star_hub_stress_runs.csv"), run_rows)
    write_csv(pathlib.Path("star_hub_stress_summary.csv"), [summary_row])

    note_lines = [
        f"Sustained ignition rate: {summary_row['sustained_ignition_rate']:.3f}.",
        "Hub-to-peripheral propagation was " + ("qualitative/systemic." if summary_row["sustained_ignition_rate"] > 0.10 else "bounded."),
        "Claim 1 (topology modulator) is " + ("contradicted." if summary_row["sustained_ignition_rate"] > 0.10 else "supported."),
        "Claim 2 (local coupling insufficient) is " + ("contradicted." if summary_row["sustained_ignition_rate"] > 0.10 else "supported."),
        "Recommended status: " + (
            "TOPOLOGY-CONDITIONED" if summary_row["sustained_ignition_rate"] > 0.20 else
            "FURTHER TESTING NEEDED" if summary_row["sustained_ignition_rate"] >= 0.05 else
            "RESTORE LOCKED"
        ),
    ]
    pathlib.Path("star_hub_stress_note.txt").write_text("\n".join(note_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
