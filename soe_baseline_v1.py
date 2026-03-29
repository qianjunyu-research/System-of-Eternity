import argparse
import csv
import pathlib
import random
from dataclasses import dataclass
from typing import Dict, List, Optional


PARAMETER_FILE = pathlib.Path(__file__).with_name("SOE_parameter_skeleton_v1.csv")


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def load_default_parameters(path: pathlib.Path) -> Dict[str, float]:
    params: Dict[str, float] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            params[row["Variable"]] = float(row["Default"])
    return params


def apply_overrides(params: Dict[str, float], overrides: List[str]) -> Dict[str, float]:
    updated = dict(params)
    override_items: List[str] = []
    for item in overrides:
        override_items.extend(part.strip() for part in item.split(",") if part.strip())

    for item in override_items:
        if "=" not in item:
            raise ValueError(f"Override must use name=value form: {item}")
        name, value_text = item.split("=", 1)
        name = name.strip()
        if name not in updated:
            raise ValueError(f"Unknown parameter override: {name}")
        updated[name] = float(value_text.strip())
    return updated


@dataclass
class State:
    cooperation_level: float
    average_trust: float
    ai_capability: float
    governance_capacity: float


def summarize_run(history: List[Dict[str, float]], stability_threshold: float) -> Dict[str, float]:
    cooperation_values = [row["cooperation_level"] for row in history]
    breach_step = next((int(row["step"]) for row in history if row["cooperation_level"] < stability_threshold), None)
    recovery_step = None
    if breach_step is not None:
        recovery_step = next(
            (
                int(row["step"])
                for row in history
                if row["step"] > breach_step and row["cooperation_level"] >= stability_threshold
            ),
            None,
        )

    max_step_change = 0.0
    for left, right in zip(cooperation_values, cooperation_values[1:]):
        max_step_change = max(max_step_change, abs(right - left))

    return {
        "final_cooperation": cooperation_values[-1],
        "min_cooperation": min(cooperation_values),
        "max_cooperation": max(cooperation_values),
        "final_trust": history[-1]["average_trust"],
        "final_ai_capability": history[-1]["ai_capability"],
        "final_governance_capacity": history[-1]["governance_capacity"],
        "first_breach_step": "" if breach_step is None else breach_step,
        "recovery_step": "" if recovery_step is None else recovery_step,
        "stable_run": 1 if breach_step is None else 0,
        "recovered_run": 1 if breach_step is not None and recovery_step is not None else 0,
        "fragile_run": 1 if cooperation_values[-1] < stability_threshold else 0,
        "max_step_change": max_step_change,
    }


def run_baseline(params: Dict[str, float], steps: int, seed: int) -> List[Dict[str, float]]:
    rng = random.Random(seed)
    state = State(
        cooperation_level=0.85,
        average_trust=0.80,
        ai_capability=0.50,
        governance_capacity=params["governance_capacity"],
    )

    history: List[Dict[str, float]] = []

    for step in range(steps):
        shock_event = 1 if rng.random() < params["shock_prob"] else 0
        novelty_event = 1 if rng.random() < params["novelty_rate"] else 0
        betrayal_event = 1 if rng.random() < params["betrayal_frequency"] else 0

        disturbance = params["noise_level"]
        disturbance += shock_event * params["shock_impact"]
        disturbance += novelty_event * params["novelty_impact"]
        disturbance = clamp(disturbance)

        stable_state = state.cooperation_level >= params["stability_threshold"]
        disturbance_multiplier = 1.0
        if stable_state:
            disturbance_multiplier -= 0.50 * params["disturbance_damping"]
        effective_disturbance = clamp(disturbance * disturbance_multiplier)

        distortion = effective_disturbance * params["emotional_weight"] * params["attention_bias"] * (1.0 - params["falsifiability_gate"])
        evidence_quality = params["structural_weight"] * params["falsifiability_gate"]
        effective_info = clamp(
            evidence_quality
            + (0.25 * params["info_spread_rate"])
            - (0.35 * distortion)
        )

        distortion_trust_damage = distortion * params["distortion_impact_on_trust"]
        trust_hit = betrayal_event * params["trust_decay"] * (0.35 + (0.35 * params["memory_factor"]))
        trust_drag = (0.03 * effective_disturbance) + distortion_trust_damage
        recovery_multiplier = params["stability_boost"] if stable_state else 1.0
        trust_recovery = params["recovery_rate"] * recovery_multiplier * (0.60 + effective_info) * (1.0 - state.average_trust)
        state.average_trust = clamp(state.average_trust - trust_hit - trust_drag + trust_recovery)

        ai_growth = params["ai_growth_rate"] * (0.02 + (0.03 * effective_info))
        state.ai_capability = clamp(state.ai_capability + ai_growth * (1.0 - state.ai_capability))

        governance_recovery = (0.05 * effective_info) + (0.02 * max(0.0, state.average_trust - 0.50))
        governance_drag = (0.03 * effective_disturbance) + (0.02 * params["coordination_latency"])
        state.governance_capacity = clamp(
            state.governance_capacity + governance_recovery * (1.0 - state.governance_capacity) - governance_drag
        )

        safe_ai_capacity = max(0.05, state.governance_capacity * params["coupling_threshold"])
        overshoot_penalty = 0.0
        if state.ai_capability > safe_ai_capacity:
            overshoot_gap = state.ai_capability - safe_ai_capacity
            overshoot_penalty = clamp((overshoot_gap / params["coupling_threshold"]) * params["overshoot_penalty"])
            state.governance_capacity = clamp(
                state.governance_capacity - (overshoot_penalty * 0.50 * params["coordination_latency"])
            )

        emergence_support = 0.0
        if rng.random() < params["emergence_rate"]:
            functionality = 0.50 * effective_info + 0.50 * state.average_trust
            stability = 0.60 * state.cooperation_level + 0.40 * state.governance_capacity
            if functionality >= params["F_threshold"] and stability >= params["S_threshold"]:
                emergence_support = params["adaptation_gain"]
                state.governance_capacity = clamp(state.governance_capacity + (0.50 * params["adaptation_gain"]))
            else:
                emergence_support = -params["adaptation_gain"] * params["disruption_strength"]

        support = 0.45
        support += 0.30 * state.average_trust * recovery_multiplier
        support += 0.18 * effective_info
        support += 0.10 * state.governance_capacity
        support += max(0.0, emergence_support)

        stress = 0.20 * effective_disturbance
        stress += 0.16 * distortion
        stress += 0.18 * overshoot_penalty
        stress += 0.08 * betrayal_event
        stress += max(0.0, -emergence_support)

        cooperation_target = clamp(support - stress)
        state.cooperation_level = clamp(
            state.cooperation_level + (0.25 * (cooperation_target - state.cooperation_level))
        )

        history.append(
            {
                "step": step,
                "shock_event": shock_event,
                "novelty_event": novelty_event,
                "betrayal_event": betrayal_event,
                "disturbance": disturbance,
                "effective_disturbance": effective_disturbance,
                "distortion": distortion,
                "distortion_trust_damage": distortion_trust_damage,
                "effective_info": effective_info,
                "cooperation_level": state.cooperation_level,
                "average_trust": state.average_trust,
                "ai_capability": state.ai_capability,
                "governance_capacity": state.governance_capacity,
                "overshoot_penalty": overshoot_penalty,
                "emergence_support": emergence_support,
                "stable_state": 1 if stable_state else 0,
            }
        )

    return history


def aggregate_histories(histories: List[List[Dict[str, float]]]) -> List[Dict[str, float]]:
    aggregated: List[Dict[str, float]] = []
    for step in range(len(histories[0])):
        step_rows = [history[step] for history in histories]
        aggregated.append(
            {
                "step": step,
                "avg_cooperation_level": sum(row["cooperation_level"] for row in step_rows) / len(step_rows),
                "avg_average_trust": sum(row["average_trust"] for row in step_rows) / len(step_rows),
                "avg_ai_capability": sum(row["ai_capability"] for row in step_rows) / len(step_rows),
                "avg_governance_capacity": sum(row["governance_capacity"] for row in step_rows) / len(step_rows),
                "avg_disturbance": sum(row["disturbance"] for row in step_rows) / len(step_rows),
                "avg_effective_disturbance": sum(row["effective_disturbance"] for row in step_rows) / len(step_rows),
                "avg_distortion_trust_damage": sum(row["distortion_trust_damage"] for row in step_rows) / len(step_rows),
                "avg_effective_info": sum(row["effective_info"] for row in step_rows) / len(step_rows),
                "stable_share": sum(1 for row in step_rows if row["stable_state"] == 1) / len(step_rows),
            }
        )
    return aggregated


def write_csv(path: pathlib.Path, rows: List[Dict[str, float]]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the small SOE baseline model from the parameter skeleton.")
    parser.add_argument("--parameters", type=pathlib.Path, default=PARAMETER_FILE, help="CSV file containing variable defaults.")
    parser.add_argument("--steps", type=int, default=100, help="Number of simulation steps per run.")
    parser.add_argument("--runs", type=int, default=20, help="Number of randomized runs.")
    parser.add_argument("--seed", type=int, default=42, help="Base random seed.")
    parser.add_argument(
        "--override",
        action="append",
        default=[],
        help="Override one parameter using name=value. Repeat for multiple overrides.",
    )
    parser.add_argument("--output", type=pathlib.Path, help="Write aggregated step history to CSV.")
    parser.add_argument("--raw-output", type=pathlib.Path, help="Write per-run summaries to CSV.")
    return parser


def main() -> None:
    parser = build_argument_parser()
    args = parser.parse_args()

    params = load_default_parameters(args.parameters)
    params = apply_overrides(params, args.override)
    histories: List[List[Dict[str, float]]] = []
    run_rows: List[Dict[str, float]] = []

    for run_index in range(args.runs):
        history = run_baseline(params=params, steps=args.steps, seed=args.seed + run_index)
        summary = summarize_run(history, stability_threshold=params["stability_threshold"])
        histories.append(history)
        run_rows.append({"run_index": run_index, "seed": args.seed + run_index, **summary})

    stable_runs = sum(int(row["stable_run"]) for row in run_rows)
    recovered_runs = sum(int(row["recovered_run"]) for row in run_rows)
    fragile_runs = sum(int(row["fragile_run"]) for row in run_rows)

    avg_final_cooperation = sum(float(row["final_cooperation"]) for row in run_rows) / len(run_rows)
    avg_min_cooperation = sum(float(row["min_cooperation"]) for row in run_rows) / len(run_rows)
    avg_final_trust = sum(float(row["final_trust"]) for row in run_rows) / len(run_rows)
    avg_final_ai = sum(float(row["final_ai_capability"]) for row in run_rows) / len(run_rows)
    avg_final_governance = sum(float(row["final_governance_capacity"]) for row in run_rows) / len(run_rows)
    avg_max_step_change = sum(float(row["max_step_change"]) for row in run_rows) / len(run_rows)

    print("SOE baseline summary")
    print(f"Runs: {args.runs}")
    print(f"Steps: {args.steps}")
    print(f"Stability threshold: {params['stability_threshold']:.2f}")
    print(f"Stable runs (never below threshold): {stable_runs}/{args.runs}")
    print(f"Recovered runs (drop then recover): {recovered_runs}/{args.runs}")
    print(f"Fragile runs (end below threshold): {fragile_runs}/{args.runs}")
    print(f"Average final cooperation: {avg_final_cooperation:.3f}")
    print(f"Average minimum cooperation: {avg_min_cooperation:.3f}")
    print(f"Average final trust: {avg_final_trust:.3f}")
    print(f"Average final AI capability: {avg_final_ai:.3f}")
    print(f"Average final governance capacity: {avg_final_governance:.3f}")
    print(f"Average largest step-to-step cooperation change: {avg_max_step_change:.3f}")

    if args.output:
        write_csv(args.output, aggregate_histories(histories))
        print(f"Saved aggregated history to {args.output}")

    if args.raw_output:
        write_csv(args.raw_output, run_rows)
        print(f"Saved run summaries to {args.raw_output}")


if __name__ == "__main__":
    main()
