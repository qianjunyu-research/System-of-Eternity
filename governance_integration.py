import argparse
import pathlib
import random
from dataclasses import asdict
from typing import Callable, Dict, List, Optional, Tuple

from governance_falsification import (
    choose_continuous_targets,
    run_custom_simulation,
    summarize_batch,
)
from governance_loop_sim import (
    Config,
    Interventions,
    State,
    apply_overrides,
    build_config,
    clamp,
    default_parameters,
    summarize_run,
    write_csv,
)

DirectController = Callable[[State, State, Config], Tuple[Interventions, str]]
DirectControllerFactory = Callable[[], DirectController]
StepFunction = Callable[[State, State, Interventions, Config, random.Random], Tuple[State, Dict[str, float]]]
StepFactory = Callable[[], StepFunction]


def build_integrated_config(base: Config) -> Config:
    params = asdict(base)
    params.update(
        {
            "execution_delay": 0.0,
            "max_delay": 0.0,
            "noise_level": 0.0,
            "alpha": 0.80,
            "intervention_decay": 0.65,
            "activation_gain": 1.00,
            "governance_coupling_floor": 0.05,
            "governance_coupling_alpha": 0.10,
        }
    )
    return Config(**params)


def choose_continuous_targets_trust_blind(
    current: State,
    previous: State,
    config: Config,
) -> Tuple[Interventions, str]:
    stability_gap = max(0.0, config.stability_threshold - current.stability)
    disturbance_pressure = max(current.disturbance, current.disturbance - previous.disturbance)
    cognition_pressure = max(current.cognitive_distortion, current.cognitive_distortion - previous.cognitive_distortion)

    targets = Interventions(
        disturbance_damping=clamp(disturbance_pressure + (0.50 * stability_gap)),
        cognitive_filtering=clamp(cognition_pressure + (0.50 * stability_gap)),
        trust_recovery=clamp((0.50 * stability_gap) + (0.25 * disturbance_pressure) + (0.25 * cognition_pressure)),
        reinforcement=clamp(max(0.0, current.stability - config.stability_threshold) + (0.25 * stability_gap)),
    )
    return targets, "continuous_control_trust_blind"


def make_integrated_step_function(
    *,
    nonlinear_cognition: bool = False,
    memory_window: Optional[int] = None,
    cap_mode: str = "derived",
) -> StepFunction:
    erosion_history: List[float] = []
    disturbance_coupling_k = None

    def step(
        current: State,
        previous: State,
        interventions: Interventions,
        config: Config,
        rng: random.Random,
    ) -> Tuple[State, Dict[str, float]]:
        nonlocal disturbance_coupling_k
        if disturbance_coupling_k is None:
            disturbance_coupling_k = clamp(
                config.governance_coupling_floor,
                low=config.governance_coupling_floor,
                high=config.max_disturbance_damping_effect,
            )

        shock_event = 1 if rng.random() < config.shock_prob else 0
        disturbance_noise = rng.uniform(-config.disturbance_noise, config.disturbance_noise)
        disturbance_damping_target = interventions.disturbance_damping * config.max_disturbance_damping_effect
        disturbance_coupling_k += config.governance_coupling_alpha * (disturbance_damping_target - disturbance_coupling_k)
        disturbance_coupling_k = clamp(
            disturbance_coupling_k,
            low=config.governance_coupling_floor,
            high=config.max_disturbance_damping_effect,
        )
        disturbance_damping = disturbance_coupling_k

        disturbance = current.disturbance
        disturbance += config.disturbance_baseline
        disturbance += disturbance_noise
        disturbance += shock_event * config.shock_impact
        disturbance -= config.disturbance_decay * current.disturbance
        disturbance -= disturbance_damping * current.disturbance
        disturbance = clamp(disturbance)

        cognition_noise = rng.uniform(-config.cognition_noise, config.cognition_noise)
        cognitive_filtering = interventions.cognitive_filtering * config.max_cognitive_filtering_effect
        cognition_drive = config.cognition_from_disturbance * disturbance
        if nonlinear_cognition:
            cognition_drive *= 1.0 + current.cognitive_distortion

        cognitive_distortion = current.cognitive_distortion
        cognitive_distortion += config.cognition_baseline
        cognitive_distortion += cognition_noise
        cognitive_distortion += cognition_drive
        cognitive_distortion -= config.cognition_decay * current.cognitive_distortion
        cognitive_distortion -= cognitive_filtering * current.cognitive_distortion
        cognitive_distortion = clamp(cognitive_distortion)

        effective_cognitive_load = cognitive_distortion
        if nonlinear_cognition:
            effective_cognitive_load = clamp(cognitive_distortion * (1.0 + disturbance), high=2.0)

        current_erosion = max(0.0, previous.trust - current.trust)
        avg_recent_erosion = 0.0
        if memory_window is None:
            effective_erosion = current_erosion
        elif memory_window <= 0:
            effective_erosion = 0.0
        else:
            recent_slice = erosion_history[-memory_window:]
            if recent_slice:
                avg_recent_erosion = sum(recent_slice) / len(recent_slice)
            effective_erosion = avg_recent_erosion

        if cap_mode == "none":
            cap_strength = 0.0
        elif cap_mode == "derived":
            cap_strength = clamp(
                0.10
                + (0.55 * disturbance)
                + (0.45 * cognitive_distortion)
                + (1.50 * effective_erosion)
            )
        else:
            raise ValueError(f"Unknown cap_mode: {cap_mode}")

        trust_recovery_boost = interventions.trust_recovery * config.max_trust_recovery_effect
        trust_loss = (
            config.trust_loss_from_disturbance * disturbance
            + config.trust_loss_from_cognition * effective_cognitive_load
        )
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
            - (config.stability_loss_from_cognition * effective_cognitive_load)
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

        realized_erosion = max(0.0, current.trust - trust)
        if memory_window is not None and memory_window > 0:
            erosion_history.append(realized_erosion)
            if len(erosion_history) > memory_window:
                erosion_history.pop(0)

        extras = {
            "shock_event": shock_event,
            "disturbance_noise": disturbance_noise,
            "cognition_noise": cognition_noise,
            "disturbance_damping_effect": disturbance_damping,
            "disturbance_damping_target": disturbance_damping_target,
            "governance_coupling_k": disturbance_coupling_k,
            "cognitive_filtering_effect": cognitive_filtering,
            "trust_recovery_effect": trust_recovery_boost,
            "reinforcement_effect": reinforcement_effect,
            "stability_target": stability_target,
            "derived_cap_strength": cap_strength,
            "avg_recent_erosion": avg_recent_erosion,
            "effective_cognitive_load": effective_cognitive_load,
            "memory_window": -1 if memory_window is None else memory_window,
            "cognition_shape": "nonlinear" if nonlinear_cognition else "linear",
            "cap_mode": cap_mode,
        }
        return next_state, extras

    return step


def run_batch_with_factories(
    config: Config,
    *,
    test_name: str,
    scenario: str,
    runs: int,
    steps: int,
    seed: int,
    note: str = "",
    controller: Optional[DirectController] = None,
    controller_factory: Optional[DirectControllerFactory] = None,
    step_fn: Optional[StepFunction] = None,
    step_factory: Optional[StepFactory] = None,
    controller_label: str = "integration",
) -> Tuple[Dict[str, object], List[Dict[str, object]]]:
    histories: List[List[Dict[str, float]]] = []
    raw_rows: List[Dict[str, object]] = []

    for run_index in range(runs):
        run_controller = controller_factory() if controller_factory else controller
        run_step_fn = step_factory() if step_factory else step_fn
        history = run_custom_simulation(
            config=config,
            steps=steps,
            seed=seed + run_index,
            direct_controller=run_controller,
            step_fn=run_step_fn,
            controller_label=controller_label,
        )
        summary = summarize_run(history, threshold=config.stability_threshold)
        histories.append(history)
        raw_rows.append(
            {
                "test_name": test_name,
                "scenario": scenario,
                "run_index": run_index,
                "seed": seed + run_index,
                **summary,
            }
        )

    summary_row = summarize_batch(histories, config, test_name=test_name, scenario=scenario, note=note)
    return summary_row, raw_rows


def build_integration_suite(
    config: Config,
    *,
    runs: int,
    steps: int,
    seed: int,
) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    integrated = build_integrated_config(config)
    summary_rows: List[Dict[str, object]] = []
    raw_rows: List[Dict[str, object]] = []

    scenarios = [
        (
            "integration",
            "full_v12_integrated",
            choose_continuous_targets,
            lambda: make_integrated_step_function(),
            "Integrated v1.2 candidate: continuous control, smoothing, cognition active, derived trust cap.",
        ),
        (
            "trust_channel",
            "trust_blind_control",
            choose_continuous_targets_trust_blind,
            lambda: make_integrated_step_function(),
            "Trust remains structural in the state equations but is not read directly by the controller.",
        ),
        (
            "cognition_shape",
            "linear_amplification",
            choose_continuous_targets,
            lambda: make_integrated_step_function(nonlinear_cognition=False),
            "Integrated model with linear cognition channel.",
        ),
        (
            "cognition_shape",
            "nonlinear_amplification",
            choose_continuous_targets,
            lambda: make_integrated_step_function(nonlinear_cognition=True),
            "Integrated model with a nonlinear cognition amplifier.",
        ),
        (
            "memory_window",
            "k0_none",
            choose_continuous_targets,
            lambda: make_integrated_step_function(memory_window=0),
            "Integrated model with no explicit erosion-memory window in the trust cap.",
        ),
        (
            "memory_window",
            "k3_small",
            choose_continuous_targets,
            lambda: make_integrated_step_function(memory_window=3),
            "Integrated model with a 3-step erosion-memory window in the trust cap.",
        ),
        (
            "memory_window",
            "k12_large",
            choose_continuous_targets,
            lambda: make_integrated_step_function(memory_window=12),
            "Integrated model with a 12-step erosion-memory window in the trust cap.",
        ),
    ]

    for test_name, scenario, controller, step_factory, note in scenarios:
        summary_row, raw_row_set = run_batch_with_factories(
            integrated,
            test_name=test_name,
            scenario=scenario,
            runs=runs,
            steps=steps,
            seed=seed,
            note=note,
            controller=controller,
            step_factory=step_factory,
            controller_label=scenario,
        )
        summary_rows.append(summary_row)
        raw_rows.extend(raw_row_set)

    return summary_rows, raw_rows


def print_suite(summary_rows: List[Dict[str, object]]) -> None:
    print("Governance integration suite")
    for row in summary_rows:
        print(
            f"- {row['test_name']} / {row['scenario']}: "
            f"stable_run_rate={float(row['stable_run_rate']):.3f}, "
            f"failure_rate={float(row['failure_rate']):.3f}, "
            f"avg_final_stability={float(row['avg_final_stability']):.3f}"
        )


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run integration-focused experiments for the post-falsification governance model."
    )
    parser.add_argument("--steps", type=int, default=100, help="Number of time steps per run.")
    parser.add_argument("--runs", type=int, default=20, help="Number of randomized runs per scenario.")
    parser.add_argument("--seed", type=int, default=42, help="Base random seed.")
    parser.add_argument(
        "--override",
        action="append",
        default=[],
        help="Override baseline parameters using name=value or comma-separated name=value pairs.",
    )
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=pathlib.Path("governance_integration_summary.csv"),
        help="Write scenario summaries to CSV.",
    )
    parser.add_argument(
        "--raw-output",
        type=pathlib.Path,
        help="Write per-run summaries to CSV.",
    )
    return parser


def main() -> None:
    parser = build_argument_parser()
    args = parser.parse_args()

    params = default_parameters()
    params = apply_overrides(params, args.override)
    config = build_config(params)

    summary_rows, raw_rows = build_integration_suite(
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
