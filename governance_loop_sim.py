import argparse
import csv
import pathlib
import random
from dataclasses import asdict, dataclass, fields
from typing import Dict, List, Tuple


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


@dataclass
class Config:
    initial_trust: float = 0.80
    initial_disturbance: float = 0.18
    initial_stability: float = 0.85
    initial_cognitive_distortion: float = 0.16
    stability_threshold: float = 0.80

    disturbance_baseline: float = 0.05
    disturbance_noise: float = 0.05
    disturbance_decay: float = 0.24
    shock_prob: float = 0.05
    shock_impact: float = 0.24

    cognition_baseline: float = 0.03
    cognition_noise: float = 0.03
    cognition_decay: float = 0.18
    cognition_from_disturbance: float = 0.16

    trust_loss_from_disturbance: float = 0.16
    trust_loss_from_cognition: float = 0.12
    trust_natural_recovery: float = 0.08
    trust_cap_strength: float = 1.0

    stability_base_support: float = 0.50
    trust_to_stability: float = 0.62
    stability_loss_from_disturbance: float = 0.22
    stability_loss_from_cognition: float = 0.14
    stability_adjustment_rate: float = 0.28

    compound_disturbance_threshold: float = 0.52
    compound_cognition_threshold: float = 0.42
    disturbance_boundary: float = 0.46
    trust_decline_margin: float = 0.012
    disturbance_rise_margin: float = 0.012
    cognition_rise_margin: float = 0.012

    intervention_budget: float = 1.00
    intervention_decay: float = 0.22
    activation_gain: float = 0.80
    alpha: float = 1.0
    execution_delay: float = 0.0
    max_delay: float = 0.0
    noise_level: float = 0.0
    trust_threshold_offset: float = 0.0
    disturbance_threshold_offset: float = 0.0
    compound_sensitivity_offset: float = 0.0

    max_disturbance_damping_effect: float = 0.55
    max_cognitive_filtering_effect: float = 0.60
    max_trust_recovery_effect: float = 0.30
    max_reinforcement_effect: float = 0.22
    governance_coupling_floor: float = 0.05
    governance_coupling_alpha: float = 0.10


@dataclass
class State:
    trust: float
    disturbance: float
    stability: float
    cognitive_distortion: float


@dataclass
class Interventions:
    disturbance_damping: float = 0.0
    cognitive_filtering: float = 0.0
    trust_recovery: float = 0.0
    reinforcement: float = 0.0


def default_parameters() -> Dict[str, float]:
    cfg = Config()
    return {field.name: float(getattr(cfg, field.name)) for field in fields(Config)}


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


def build_config(params: Dict[str, float]) -> Config:
    return Config(**params)


def smooth_observation(actual: State, previous_observed: State, alpha: float) -> State:
    alpha = clamp(alpha)
    return State(
        trust=clamp((alpha * actual.trust) + ((1.0 - alpha) * previous_observed.trust)),
        disturbance=clamp((alpha * actual.disturbance) + ((1.0 - alpha) * previous_observed.disturbance)),
        stability=actual.stability,
        cognitive_distortion=clamp(
            (alpha * actual.cognitive_distortion)
            + ((1.0 - alpha) * previous_observed.cognitive_distortion)
        ),
    )


def sample_observation(actual: State, noise_level: float, rng: random.Random) -> State:
    if noise_level <= 0.0:
        return State(**asdict(actual))
    return State(
        trust=clamp(actual.trust + rng.gauss(0.0, noise_level)),
        disturbance=clamp(actual.disturbance + rng.gauss(0.0, noise_level)),
        stability=actual.stability,
        cognitive_distortion=clamp(actual.cognitive_distortion + rng.gauss(0.0, noise_level)),
    )


def compute_trust_recovery_effect(base_recovery: float, trust: float, cap_strength: float) -> float:
    cap_multiplier = 1.0 - (cap_strength * trust)
    return base_recovery * max(0.0, cap_multiplier)


def choose_governance_response(current: State, previous: State, config: Config) -> Tuple[List[str], str]:
    trust_delta = current.trust - previous.trust
    disturbance_delta = current.disturbance - previous.disturbance
    cognition_delta = current.cognitive_distortion - previous.cognitive_distortion
    effective_trust_decline_margin = max(0.0, config.trust_decline_margin - config.trust_threshold_offset)
    effective_disturbance_rise_margin = max(0.0, config.disturbance_rise_margin - config.disturbance_threshold_offset)
    effective_disturbance_boundary = max(0.0, config.disturbance_boundary - config.disturbance_threshold_offset)
    effective_compound_disturbance_threshold = max(
        0.0, config.compound_disturbance_threshold - config.compound_sensitivity_offset
    )
    effective_compound_cognition_threshold = max(
        0.0, config.compound_cognition_threshold - config.compound_sensitivity_offset
    )

    compound_stress = (
        current.disturbance >= effective_compound_disturbance_threshold
        and current.cognitive_distortion >= effective_compound_cognition_threshold
    ) or (
        trust_delta <= -effective_trust_decline_margin
        and disturbance_delta >= effective_disturbance_rise_margin
    )

    trust_declining = trust_delta <= -effective_trust_decline_margin
    disturbance_boundary = (
        current.disturbance >= effective_disturbance_boundary
        or (
            current.disturbance >= (0.90 * effective_disturbance_boundary)
            and disturbance_delta >= (0.50 * effective_disturbance_rise_margin)
        )
    )
    cognition_rising = cognition_delta >= config.cognition_rise_margin
    stable_enough = current.stability >= config.stability_threshold

    if compound_stress:
        return (
            ["disturbance_damping", "cognitive_filtering", "trust_recovery"],
            "compound_stress",
        )
    if trust_declining:
        return (["trust_recovery"], "trust_decline")
    if disturbance_boundary:
        return (["disturbance_damping"], "disturbance_boundary")
    if cognition_rising:
        return (["cognitive_filtering"], "cognition_rising")
    if stable_enough:
        return (["reinforcement"], "stability_reinforcement")
    return ([], "idle")


def resolve_execution_delay(config: Config, rng: random.Random) -> int:
    stochastic_max = max(0, int(config.max_delay))
    if stochastic_max >= 1:
        return rng.randint(1, stochastic_max)
    return max(0, int(config.execution_delay))


def queue_decision(
    decision_queue: List[Tuple[int, List[str], str]],
    current_step: int,
    execution_delay: int,
    actions: List[str],
    decision: str,
) -> None:
    if not actions:
        return
    execute_step = current_step + max(0, execution_delay)
    decision_queue.append((execute_step, list(actions), decision))


def drain_due_decisions(
    decision_queue: List[Tuple[int, List[str], str]],
    current_step: int,
) -> Tuple[List[Tuple[int, List[str], str]], List[str], List[str]]:
    remaining: List[Tuple[int, List[str], str]] = []
    executed_decisions: List[str] = []
    combined_actions: List[str] = []

    for execute_step, actions, decision in decision_queue:
        if execute_step <= current_step:
            executed_decisions.append(decision)
            for action in actions:
                if action not in combined_actions:
                    combined_actions.append(action)
        else:
            remaining.append((execute_step, actions, decision))

    return remaining, combined_actions, executed_decisions


def decay_interventions(interventions: Interventions, config: Config) -> Interventions:
    decay_factor = 1.0 - config.intervention_decay
    return Interventions(
        disturbance_damping=clamp(interventions.disturbance_damping * decay_factor),
        cognitive_filtering=clamp(interventions.cognitive_filtering * decay_factor),
        trust_recovery=clamp(interventions.trust_recovery * decay_factor),
        reinforcement=clamp(interventions.reinforcement * decay_factor),
    )


def apply_budget(interventions: Interventions, budget: float) -> Interventions:
    total = (
        interventions.disturbance_damping
        + interventions.cognitive_filtering
        + interventions.trust_recovery
        + interventions.reinforcement
    )
    if total <= budget or total == 0.0:
        return interventions

    scale = budget / total
    return Interventions(
        disturbance_damping=interventions.disturbance_damping * scale,
        cognitive_filtering=interventions.cognitive_filtering * scale,
        trust_recovery=interventions.trust_recovery * scale,
        reinforcement=interventions.reinforcement * scale,
    )


def activate_interventions(interventions: Interventions, actions: List[str], config: Config) -> Interventions:
    updated = decay_interventions(interventions, config)
    if actions:
        share = config.intervention_budget / len(actions)
        for action in actions:
            current_value = getattr(updated, action)
            setattr(updated, action, clamp(current_value + (config.activation_gain * share)))
    return apply_budget(updated, config.intervention_budget)


def step_system(
    current: State,
    interventions: Interventions,
    config: Config,
    rng: random.Random,
) -> Tuple[State, Dict[str, float]]:
    shock_event = 1 if rng.random() < config.shock_prob else 0
    disturbance_noise = rng.uniform(-config.disturbance_noise, config.disturbance_noise)
    disturbance_damping = interventions.disturbance_damping * config.max_disturbance_damping_effect

    disturbance = current.disturbance
    disturbance += config.disturbance_baseline
    disturbance += disturbance_noise
    disturbance += shock_event * config.shock_impact
    disturbance -= config.disturbance_decay * current.disturbance
    disturbance -= disturbance_damping * current.disturbance
    disturbance = clamp(disturbance)

    cognition_noise = rng.uniform(-config.cognition_noise, config.cognition_noise)
    cognitive_filtering = interventions.cognitive_filtering * config.max_cognitive_filtering_effect

    cognitive_distortion = current.cognitive_distortion
    cognitive_distortion += config.cognition_baseline
    cognitive_distortion += cognition_noise
    cognitive_distortion += config.cognition_from_disturbance * disturbance
    cognitive_distortion -= config.cognition_decay * current.cognitive_distortion
    cognitive_distortion -= cognitive_filtering * current.cognitive_distortion
    cognitive_distortion = clamp(cognitive_distortion)

    trust_recovery_boost = interventions.trust_recovery * config.max_trust_recovery_effect
    trust_loss = (
        config.trust_loss_from_disturbance * disturbance
        + config.trust_loss_from_cognition * cognitive_distortion
    )
    trust_recovery = compute_trust_recovery_effect(
        config.trust_natural_recovery + trust_recovery_boost,
        current.trust,
        config.trust_cap_strength,
    )
    trust = clamp(current.trust - trust_loss + trust_recovery)

    reinforcement_effect = 0.0
    if current.stability >= config.stability_threshold:
        reinforcement_effect = interventions.reinforcement * config.max_reinforcement_effect

    stability_target = clamp(
        config.stability_base_support
        + (config.trust_to_stability * trust)
        + reinforcement_effect
        - (config.stability_loss_from_disturbance * disturbance)
        - (config.stability_loss_from_cognition * cognitive_distortion)
    )
    stability = clamp(
        current.stability + (config.stability_adjustment_rate * (stability_target - current.stability))
    )

    next_state = State(
        trust=trust,
        disturbance=disturbance,
        stability=stability,
        cognitive_distortion=cognitive_distortion,
    )
    extras = {
        "shock_event": shock_event,
        "disturbance_noise": disturbance_noise,
        "cognition_noise": cognition_noise,
        "disturbance_damping_effect": disturbance_damping,
        "cognitive_filtering_effect": cognitive_filtering,
        "trust_recovery_effect": trust_recovery_boost,
        "reinforcement_effect": reinforcement_effect,
        "stability_target": stability_target,
    }
    return next_state, extras


def summarize_run(history: List[Dict[str, float]], threshold: float) -> Dict[str, float]:
    stability_values = [row["stability"] for row in history]
    trust_values = [row["trust"] for row in history]

    breach_step = next((int(row["step"]) for row in history if row["stability"] < threshold), None)
    recovery_step = None
    if breach_step is not None:
        recovery_step = next(
            (
                int(row["step"])
                for row in history
                if row["step"] > breach_step and row["stability"] >= threshold
            ),
            None,
        )

    failure_reason = ""
    if breach_step is not None and recovery_step is None:
        failure_reason = "never_recovered"
    elif stability_values[-1] < threshold:
        failure_reason = "ended_below_threshold"

    intervention_utilization = sum(row["intervention_total"] for row in history) / len(history)
    stability_rate = sum(1 for row in history if row["stability"] >= threshold) / len(history)

    return {
        "final_stability": stability_values[-1],
        "min_stability": min(stability_values),
        "max_stability": max(stability_values),
        "final_trust": trust_values[-1],
        "final_disturbance": history[-1]["disturbance"],
        "final_cognitive_distortion": history[-1]["cognitive_distortion"],
        "stability_rate": stability_rate,
        "first_breach_step": "" if breach_step is None else breach_step,
        "recovery_step": "" if recovery_step is None else recovery_step,
        "stable_run": 1 if breach_step is None else 0,
        "recovered_run": 1 if breach_step is not None and recovery_step is not None else 0,
        "failure_case": 1 if failure_reason else 0,
        "failure_reason": failure_reason,
        "avg_intervention_utilization": intervention_utilization,
    }


def run_simulation(config: Config, steps: int, seed: int) -> List[Dict[str, float]]:
    dynamics_rng = random.Random(seed)
    execution_rng = random.Random(seed + 10_001)
    observation_rng = random.Random(seed + 20_003)
    state = State(
        trust=config.initial_trust,
        disturbance=config.initial_disturbance,
        stability=config.initial_stability,
        cognitive_distortion=config.initial_cognitive_distortion,
    )
    previous_state = State(**asdict(state))
    observed_state = sample_observation(state, config.noise_level, observation_rng)
    previous_observed_state = State(**asdict(observed_state))
    interventions = Interventions()
    decision_queue: List[Tuple[int, List[str], str]] = []
    history: List[Dict[str, float]] = []

    for step in range(steps):
        actions, decision = choose_governance_response(observed_state, previous_observed_state, config)
        sampled_delay = resolve_execution_delay(config, execution_rng)
        queue_decision(decision_queue, step, sampled_delay, actions, decision)
        decision_queue, executed_actions, executed_decisions = drain_due_decisions(decision_queue, step)
        interventions = activate_interventions(interventions, executed_actions, config)
        next_state, extras = step_system(state, interventions, config, dynamics_rng)
        sampled_observation = sample_observation(next_state, config.noise_level, observation_rng)
        next_observed_state = smooth_observation(sampled_observation, observed_state, config.alpha)

        intervention_total = (
            interventions.disturbance_damping
            + interventions.cognitive_filtering
            + interventions.trust_recovery
            + interventions.reinforcement
        )

        history.append(
            {
                "step": step,
                "decision": decision,
                "executed_decisions": "|".join(executed_decisions) if executed_decisions else "idle",
                "executed_action_count": len(executed_actions),
                "alpha": config.alpha,
                "execution_delay": max(0, int(config.execution_delay)),
                "sampled_delay": sampled_delay,
                "max_delay": max(0, int(config.max_delay)),
                "noise_level": max(0.0, config.noise_level),
                "trust": next_state.trust,
                "trust_filtered": next_observed_state.trust,
                "disturbance": next_state.disturbance,
                "disturbance_filtered": next_observed_state.disturbance,
                "stability": next_state.stability,
                "cognitive_distortion": next_state.cognitive_distortion,
                "cognitive_distortion_filtered": next_observed_state.cognitive_distortion,
                "disturbance_damping": interventions.disturbance_damping,
                "cognitive_filtering": interventions.cognitive_filtering,
                "trust_recovery": interventions.trust_recovery,
                "reinforcement": interventions.reinforcement,
                "intervention_total": intervention_total,
                **extras,
            }
        )

        previous_state = State(**asdict(state))
        previous_observed_state = State(**asdict(observed_state))
        observed_state = next_observed_state
        state = next_state

    return history


def aggregate_histories(histories: List[List[Dict[str, float]]], threshold: float) -> List[Dict[str, float]]:
    aggregated: List[Dict[str, float]] = []
    for step in range(len(histories[0])):
        rows = [history[step] for history in histories]
        aggregated.append(
            {
                "step": step,
                "avg_trust": sum(row["trust"] for row in rows) / len(rows),
                "avg_trust_filtered": sum(row["trust_filtered"] for row in rows) / len(rows),
                "avg_disturbance": sum(row["disturbance"] for row in rows) / len(rows),
                "avg_disturbance_filtered": sum(row["disturbance_filtered"] for row in rows) / len(rows),
                "avg_stability": sum(row["stability"] for row in rows) / len(rows),
                "avg_cognitive_distortion": sum(row["cognitive_distortion"] for row in rows) / len(rows),
                "avg_cognitive_distortion_filtered": sum(
                    row["cognitive_distortion_filtered"] for row in rows
                ) / len(rows),
                "avg_disturbance_damping": sum(row["disturbance_damping"] for row in rows) / len(rows),
                "avg_cognitive_filtering": sum(row["cognitive_filtering"] for row in rows) / len(rows),
                "avg_trust_recovery": sum(row["trust_recovery"] for row in rows) / len(rows),
                "avg_reinforcement": sum(row["reinforcement"] for row in rows) / len(rows),
                "avg_intervention_total": sum(row["intervention_total"] for row in rows) / len(rows),
                "stability_share": sum(1 for row in rows if row["stability"] >= threshold) / len(rows),
                "shock_share": sum(row["shock_event"] for row in rows) / len(rows),
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
    parser = argparse.ArgumentParser(
        description="Simulate a closed-loop trust-disturbance-stability-cognition system with governance mechanism activation."
    )
    parser.add_argument("--steps", type=int, default=100, help="Number of time steps per run.")
    parser.add_argument("--runs", type=int, default=20, help="Number of randomized runs.")
    parser.add_argument("--seed", type=int, default=42, help="Base random seed.")
    parser.add_argument(
        "--override",
        action="append",
        default=[],
        help="Override one or more parameters using name=value or comma-separated name=value pairs.",
    )
    parser.add_argument("--output", type=pathlib.Path, help="Write aggregated step history to CSV.")
    parser.add_argument("--raw-output", type=pathlib.Path, help="Write per-run summaries to CSV.")
    parser.add_argument("--dump-parameters", action="store_true", help="Print default adjustable parameters and exit.")
    return parser


def main() -> None:
    parser = build_argument_parser()
    args = parser.parse_args()

    params = default_parameters()
    params = apply_overrides(params, args.override)

    if args.dump_parameters:
        print("Adjustable parameters")
        for name in sorted(params):
            print(f"{name}={params[name]:.3f}")
        return

    config = build_config(params)
    histories: List[List[Dict[str, float]]] = []
    run_rows: List[Dict[str, float]] = []

    for run_index in range(args.runs):
        history = run_simulation(config=config, steps=args.steps, seed=args.seed + run_index)
        summary = summarize_run(history, threshold=config.stability_threshold)
        histories.append(history)
        run_rows.append({"run_index": run_index, "seed": args.seed + run_index, **summary})

    stability_rate = sum(float(row["stability_rate"]) for row in run_rows) / len(run_rows)
    recovery_success = sum(int(row["recovered_run"]) for row in run_rows)
    failure_cases = sum(int(row["failure_case"]) for row in run_rows)
    stable_runs = sum(int(row["stable_run"]) for row in run_rows)
    avg_final_stability = sum(float(row["final_stability"]) for row in run_rows) / len(run_rows)
    avg_final_trust = sum(float(row["final_trust"]) for row in run_rows) / len(run_rows)
    avg_intervention_utilization = sum(float(row["avg_intervention_utilization"]) for row in run_rows) / len(run_rows)

    print("Governance loop simulation summary")
    print(f"Runs: {args.runs}")
    print(f"Steps: {args.steps}")
    print(f"Stability threshold: {config.stability_threshold:.2f}")
    print(f"Stability rate: {stability_rate:.3f}")
    print(f"Stable runs (never below threshold): {stable_runs}/{args.runs}")
    print(f"Recovery success: {recovery_success}/{args.runs}")
    print(f"Failure cases: {failure_cases}/{args.runs}")
    print(f"Average final stability: {avg_final_stability:.3f}")
    print(f"Average final trust: {avg_final_trust:.3f}")
    print(f"Average intervention utilization: {avg_intervention_utilization:.3f}")

    if args.output:
        write_csv(args.output, aggregate_histories(histories, threshold=config.stability_threshold))
        print(f"Saved aggregated history to {args.output}")

    if args.raw_output:
        write_csv(args.raw_output, run_rows)
        print(f"Saved run summaries to {args.raw_output}")


if __name__ == "__main__":
    main()
