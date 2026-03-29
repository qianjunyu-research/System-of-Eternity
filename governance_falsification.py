import argparse
import csv
import pathlib
import random
from dataclasses import asdict
from typing import Callable, Dict, List, Optional, Tuple

from governance_loop_sim import (
    Config,
    Interventions,
    State,
    activate_interventions,
    apply_budget,
    apply_overrides,
    build_config,
    choose_governance_response,
    clamp,
    decay_interventions,
    default_parameters,
    drain_due_decisions,
    queue_decision,
    resolve_execution_delay,
    run_simulation,
    sample_observation,
    smooth_observation,
    step_system,
    summarize_run,
    write_csv,
)

ActionSelector = Callable[[State, State, Config], Tuple[List[str], str]]
DirectController = Callable[[State, State, Config], Tuple[Interventions, str]]
StepFunction = Callable[[State, State, Interventions, Config, random.Random], Tuple[State, Dict[str, float]]]


def apply_direct_targets(
    interventions: Interventions,
    targets: Interventions,
    config: Config,
) -> Interventions:
    decayed = decay_interventions(interventions, config)
    updated = Interventions(
        disturbance_damping=clamp(decayed.disturbance_damping + (config.activation_gain * targets.disturbance_damping)),
        cognitive_filtering=clamp(decayed.cognitive_filtering + (config.activation_gain * targets.cognitive_filtering)),
        trust_recovery=clamp(decayed.trust_recovery + (config.activation_gain * targets.trust_recovery)),
        reinforcement=clamp(decayed.reinforcement + (config.activation_gain * targets.reinforcement)),
    )
    return apply_budget(updated, config.intervention_budget)


def choose_no_trust_response(current: State, previous: State, config: Config) -> Tuple[List[str], str]:
    disturbance_delta = current.disturbance - previous.disturbance
    cognition_delta = current.cognitive_distortion - previous.cognitive_distortion
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
    )
    disturbance_boundary = (
        current.disturbance >= effective_disturbance_boundary
        or (
            current.disturbance >= (0.90 * effective_disturbance_boundary)
            and disturbance_delta >= max(0.0, 0.50 * config.disturbance_rise_margin)
        )
    )
    cognition_rising = cognition_delta >= config.cognition_rise_margin
    stable_enough = current.stability >= config.stability_threshold

    if compound_stress:
        return (["disturbance_damping", "cognitive_filtering", "reinforcement"], "compound_stress_no_trust")
    if disturbance_boundary:
        return (["disturbance_damping"], "disturbance_boundary_no_trust")
    if cognition_rising:
        return (["cognitive_filtering"], "cognition_rising_no_trust")
    if stable_enough:
        return (["reinforcement"], "stability_reinforcement_no_trust")
    return ([], "idle")


def choose_continuous_targets(current: State, previous: State, config: Config) -> Tuple[Interventions, str]:
    stability_gap = max(0.0, config.stability_threshold - current.stability)
    trust_gap = max(0.0, config.initial_trust - current.trust)
    disturbance_pressure = max(current.disturbance, current.disturbance - previous.disturbance)
    cognition_pressure = max(current.cognitive_distortion, current.cognitive_distortion - previous.cognitive_distortion)

    targets = Interventions(
        disturbance_damping=clamp(disturbance_pressure + (0.50 * stability_gap)),
        cognitive_filtering=clamp(cognition_pressure + (0.50 * stability_gap)),
        trust_recovery=clamp(max(trust_gap, stability_gap)),
        reinforcement=clamp(max(0.0, current.stability - config.stability_threshold) + (0.25 * stability_gap)),
    )
    return targets, "continuous_control"


def step_system_no_trust_channel(
    current: State,
    previous: State,
    interventions: Interventions,
    config: Config,
    rng: random.Random,
) -> Tuple[State, Dict[str, float]]:
    next_state, extras = step_system(current, interventions, config, rng)
    reinforcement_effect = extras["reinforcement_effect"]
    stability_target = clamp(
        config.stability_base_support
        + reinforcement_effect
        - (config.stability_loss_from_disturbance * next_state.disturbance)
        - (config.stability_loss_from_cognition * next_state.cognitive_distortion)
    )
    stability = clamp(
        current.stability + (config.stability_adjustment_rate * (stability_target - current.stability))
    )
    updated_state = State(
        trust=next_state.trust,
        disturbance=next_state.disturbance,
        stability=stability,
        cognitive_distortion=next_state.cognitive_distortion,
    )
    updated_extras = dict(extras)
    updated_extras["stability_target"] = stability_target
    updated_extras["trust_channel_disabled"] = 1.0
    return updated_state, updated_extras


def derived_cap_strength(current: State, previous: State) -> float:
    trust_erosion = max(0.0, previous.trust - current.trust)
    return clamp(
        0.10
        + (0.55 * current.disturbance)
        + (0.45 * current.cognitive_distortion)
        + (1.50 * trust_erosion)
    )


def step_system_derived_cap(
    current: State,
    previous: State,
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
    stress_state = State(
        trust=current.trust,
        disturbance=disturbance,
        stability=current.stability,
        cognitive_distortion=cognitive_distortion,
    )
    cap_strength = derived_cap_strength(stress_state, previous)
    trust_recovery = (config.trust_natural_recovery + trust_recovery_boost) * max(0.0, 1.0 - (cap_strength * current.trust))
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
        "derived_cap_strength": cap_strength,
    }
    return next_state, extras


def run_custom_simulation(
    config: Config,
    steps: int,
    seed: int,
    *,
    action_selector: Optional[ActionSelector] = None,
    direct_controller: Optional[DirectController] = None,
    step_fn: Optional[StepFunction] = None,
    controller_label: str = "custom",
) -> List[Dict[str, float]]:
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
    if step_fn is None:
        step_fn = lambda current, previous, active, cfg, rng: step_system(current, active, cfg, rng)

    for step in range(steps):
        executed_actions: List[str] = []
        executed_decisions: List[str] = []
        sampled_delay = 0

        if direct_controller is not None:
            targets, decision = direct_controller(observed_state, previous_observed_state, config)
            interventions = apply_direct_targets(interventions, targets, config)
            component_pairs = [
                ("disturbance_damping", targets.disturbance_damping),
                ("cognitive_filtering", targets.cognitive_filtering),
                ("trust_recovery", targets.trust_recovery),
                ("reinforcement", targets.reinforcement),
            ]
            executed_actions = [name for name, value in component_pairs if value > 1e-9]
            executed_decisions = [decision] if executed_actions else []
        else:
            selector = action_selector or choose_governance_response
            actions, decision = selector(observed_state, previous_observed_state, config)
            sampled_delay = resolve_execution_delay(config, execution_rng)
            queue_decision(decision_queue, step, sampled_delay, actions, decision)
            decision_queue, executed_actions, executed_decisions = drain_due_decisions(decision_queue, step)
            interventions = activate_interventions(interventions, executed_actions, config)

        next_state, extras = step_fn(state, previous_state, interventions, config, dynamics_rng)
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
                "controller_mode": controller_label,
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


def summarize_batch(
    histories: List[List[Dict[str, float]]],
    config: Config,
    *,
    test_name: str,
    scenario: str,
    note: str = "",
) -> Dict[str, object]:
    summaries = [summarize_run(history, threshold=config.stability_threshold) for history in histories]
    final_stabilities = [float(row["final_stability"]) for row in summaries]
    min_stabilities = [float(row["min_stability"]) for row in summaries]
    stable_run_rate = sum(int(row["stable_run"]) for row in summaries) / len(summaries)
    recovered_run_rate = sum(int(row["recovered_run"]) for row in summaries) / len(summaries)
    failure_rate = sum(int(row["failure_case"]) for row in summaries) / len(summaries)
    avg_final_trust = sum(float(row["final_trust"]) for row in summaries) / len(summaries)
    avg_final_disturbance = sum(float(row["final_disturbance"]) for row in summaries) / len(summaries)
    avg_final_cognition = sum(float(row["final_cognitive_distortion"]) for row in summaries) / len(summaries)
    avg_utilization = sum(float(row["avg_intervention_utilization"]) for row in summaries) / len(summaries)

    derived_caps = [
        row["derived_cap_strength"]
        for history in histories
        for row in history
        if "derived_cap_strength" in row
    ]

    return {
        "test_name": test_name,
        "scenario": scenario,
        "avg_final_stability": sum(final_stabilities) / len(final_stabilities),
        "avg_min_stability": sum(min_stabilities) / len(min_stabilities),
        "stable_run_rate": stable_run_rate,
        "recovered_run_rate": recovered_run_rate,
        "failure_rate": failure_rate,
        "avg_final_trust": avg_final_trust,
        "avg_final_disturbance": avg_final_disturbance,
        "avg_final_cognitive_distortion": avg_final_cognition,
        "avg_intervention_utilization": avg_utilization,
        "avg_derived_cap_strength": (
            (sum(derived_caps) / len(derived_caps)) if derived_caps else ""
        ),
        "note": note,
    }


def run_batch(
    config: Config,
    *,
    test_name: str,
    scenario: str,
    runs: int,
    steps: int,
    seed: int,
    note: str = "",
    action_selector: Optional[ActionSelector] = None,
    direct_controller: Optional[DirectController] = None,
    step_fn: Optional[StepFunction] = None,
    controller_label: str = "baseline",
) -> Tuple[Dict[str, object], List[Dict[str, object]]]:
    histories: List[List[Dict[str, float]]] = []
    raw_rows: List[Dict[str, object]] = []

    for run_index in range(runs):
        run_seed = seed + run_index
        if action_selector is None and direct_controller is None and step_fn is None:
            history = run_simulation(config=config, steps=steps, seed=run_seed)
        else:
            history = run_custom_simulation(
                config=config,
                steps=steps,
                seed=run_seed,
                action_selector=action_selector,
                direct_controller=direct_controller,
                step_fn=step_fn,
                controller_label=controller_label,
            )

        summary = summarize_run(history, threshold=config.stability_threshold)
        histories.append(history)
        raw_rows.append(
            {
                "test_name": test_name,
                "scenario": scenario,
                "run_index": run_index,
                "seed": run_seed,
                **summary,
            }
        )

    return summarize_batch(histories, config, test_name=test_name, scenario=scenario, note=note), raw_rows


def choose_best_damping_proxy(
    base_config: Config,
    *,
    runs: int,
    steps: int,
    seed: int,
) -> Tuple[Dict[str, object], List[Dict[str, object]]]:
    candidate_rows: List[Tuple[Tuple[float, float, float], Dict[str, object], List[Dict[str, object]]]] = []
    for alpha in (0.20, 0.40, 0.60, 0.80):
        for decay in (0.22, 0.35, 0.50, 0.65):
            for gain in (0.40, 0.60, 0.80, 1.00):
                params = asdict(base_config)
                params.update(
                    {
                        "execution_delay": 0.0,
                        "max_delay": 0.0,
                        "alpha": alpha,
                        "intervention_decay": decay,
                        "activation_gain": gain,
                    }
                )
                config = Config(**params)
                summary, raw_rows = run_batch(
                    config,
                    test_name="delay_vs_damping",
                    scenario=f"damping_proxy_a{alpha:.2f}_d{decay:.2f}_g{gain:.2f}",
                    runs=runs,
                    steps=steps,
                    seed=seed,
                    note="Zero-delay threshold controller with smoothing and extra damping.",
                )
                sort_key = (
                    float(summary["stable_run_rate"]),
                    float(summary["avg_final_stability"]),
                    -float(summary["failure_rate"]),
                )
                candidate_rows.append((sort_key, summary, raw_rows))

    candidate_rows.sort(key=lambda item: item[0], reverse=True)
    return candidate_rows[0][1], candidate_rows[0][2]


def build_falsification_suite(
    config: Config,
    *,
    runs: int,
    steps: int,
    seed: int,
) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    summary_rows: List[Dict[str, object]] = []
    raw_rows: List[Dict[str, object]] = []

    baseline_summary, baseline_raw = run_batch(
        config,
        test_name="baseline",
        scenario="threshold_queue_baseline",
        runs=runs,
        steps=steps,
        seed=seed,
        note="Reference threshold-based controller with current default implementation.",
    )
    summary_rows.append(baseline_summary)
    raw_rows.extend(baseline_raw)

    no_trust_params = asdict(config)
    no_trust_params.update(
        {
            "trust_to_stability": 0.0,
            "max_trust_recovery_effect": 0.0,
            "trust_cap_strength": 0.0,
        }
    )
    no_trust_summary, no_trust_raw = run_batch(
        Config(**no_trust_params),
        test_name="de_trust",
        scenario="no_trust_channel",
        runs=runs,
        steps=steps,
        seed=seed,
        note="Trust removed as the privileged stabilization channel; control acts only through disturbance, cognition, and reinforcement.",
        action_selector=choose_no_trust_response,
        step_fn=step_system_no_trust_channel,
        controller_label="no_trust_threshold",
    )
    summary_rows.append(no_trust_summary)
    raw_rows.extend(no_trust_raw)

    continuous_params = asdict(config)
    continuous_params.update({"execution_delay": 0.0, "max_delay": 0.0, "noise_level": 0.0})
    continuous_summary, continuous_raw = run_batch(
        Config(**continuous_params),
        test_name="remove_thresholds",
        scenario="continuous_controller",
        runs=runs,
        steps=steps,
        seed=seed,
        note="Threshold rules replaced by a continuous state-severity controller.",
        direct_controller=choose_continuous_targets,
        controller_label="continuous_direct",
    )
    summary_rows.append(continuous_summary)
    raw_rows.extend(continuous_raw)

    delayed_params = asdict(config)
    delayed_params.update({"execution_delay": 2.0, "max_delay": 0.0})
    delayed_summary, delayed_raw = run_batch(
        Config(**delayed_params),
        test_name="delay_vs_damping",
        scenario="delay_2_baseline",
        runs=runs,
        steps=steps,
        seed=seed,
        note="Reference delayed controller for mechanism comparison.",
    )
    summary_rows.append(delayed_summary)
    raw_rows.extend(delayed_raw)

    damping_summary, damping_raw = choose_best_damping_proxy(config, runs=runs, steps=steps, seed=seed)
    summary_rows.append(damping_summary)
    raw_rows.extend(damping_raw)

    cognition_off_params = asdict(config)
    cognition_off_params.update(
        {
            "initial_cognitive_distortion": 0.0,
            "cognition_baseline": 0.0,
            "cognition_noise": 0.0,
            "cognition_from_disturbance": 0.0,
            "trust_loss_from_cognition": 0.0,
            "stability_loss_from_cognition": 0.0,
            "max_cognitive_filtering_effect": 0.0,
        }
    )
    cognition_off_summary, cognition_off_raw = run_batch(
        Config(**cognition_off_params),
        test_name="cognition_channel",
        scenario="cognition_removed",
        runs=runs,
        steps=steps,
        seed=seed,
        note="Cognitive distortion channel fully disabled.",
    )
    summary_rows.append(cognition_off_summary)
    raw_rows.extend(cognition_off_raw)

    cognition_on_params = asdict(config)
    cognition_on_params.update(
        {
            "initial_cognitive_distortion": max(config.initial_cognitive_distortion, 0.25),
            "cognition_baseline": config.cognition_baseline * 2.0,
            "cognition_noise": config.cognition_noise * 2.0,
            "cognition_from_disturbance": config.cognition_from_disturbance * 2.0,
            "trust_loss_from_cognition": config.trust_loss_from_cognition * 1.5,
            "stability_loss_from_cognition": config.stability_loss_from_cognition * 1.5,
        }
    )
    cognition_on_summary, cognition_on_raw = run_batch(
        Config(**cognition_on_params),
        test_name="cognition_channel",
        scenario="cognition_amplified",
        runs=runs,
        steps=steps,
        seed=seed,
        note="Cognitive distortion channel amplified to test whether C materially affects outcomes.",
    )
    summary_rows.append(cognition_on_summary)
    raw_rows.extend(cognition_on_raw)

    derived_cap_summary, derived_cap_raw = run_batch(
        config,
        test_name="derived_trust_cap",
        scenario="stress_derived_cap",
        runs=runs,
        steps=steps,
        seed=seed,
        note="Trust cap derived from disturbance, cognition, and recent trust erosion instead of fixed externally.",
        step_fn=step_system_derived_cap,
        controller_label="threshold_queue_derived_cap",
    )
    summary_rows.append(derived_cap_summary)
    raw_rows.extend(derived_cap_raw)

    return summary_rows, raw_rows


def print_suite(summary_rows: List[Dict[str, object]]) -> None:
    print("Governance falsification suite")
    for row in summary_rows:
        print(
            f"- {row['test_name']} / {row['scenario']}: "
            f"stable_run_rate={float(row['stable_run_rate']):.3f}, "
            f"failure_rate={float(row['failure_rate']):.3f}, "
            f"avg_final_stability={float(row['avg_final_stability']):.3f}"
        )


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run targeted falsification experiments against the governance loop simulator."
    )
    parser.add_argument("--steps", type=int, default=100, help="Number of time steps per run.")
    parser.add_argument("--runs", type=int, default=20, help="Number of randomized runs per scenario.")
    parser.add_argument("--seed", type=int, default=42, help="Base random seed.")
    parser.add_argument(
        "--override",
        action="append",
        default=[],
        help="Override one or more baseline parameters using name=value or comma-separated name=value pairs.",
    )
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=pathlib.Path("governance_falsification_summary.csv"),
        help="Write scenario summaries to CSV.",
    )
    parser.add_argument(
        "--raw-output",
        type=pathlib.Path,
        help="Write per-run scenario summaries to CSV.",
    )
    return parser


def main() -> None:
    parser = build_argument_parser()
    args = parser.parse_args()

    params = default_parameters()
    params = apply_overrides(params, args.override)
    config = build_config(params)

    summary_rows, raw_rows = build_falsification_suite(
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
