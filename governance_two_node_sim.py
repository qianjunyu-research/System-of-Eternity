import argparse
import pathlib
import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from governance_falsification import apply_direct_targets, choose_continuous_targets
from governance_integration import build_integrated_config, make_integrated_step_function
from governance_loop_sim import (
    Config,
    Interventions,
    State,
    apply_overrides,
    build_config,
    default_parameters,
    sample_observation,
    smooth_observation,
    summarize_run,
    write_csv,
)


@dataclass
class TwoNodeRuntime:
    node_name: str
    config: Config
    step_fn: object
    state: State
    previous_state: State
    observed_state: State
    previous_observed_state: State
    interventions: Interventions
    dynamics_rng: random.Random
    observation_rng: random.Random
    history: List[Dict[str, float]]


def build_constraint_config(base: Config) -> Config:
    params = base.__dict__.copy()
    params.update(
        {
            "intervention_budget": 0.40,
            "alpha": 1.00,
            "intervention_decay": 0.22,
            "shock_prob": 0.15,
            "shock_impact": 0.48,
        }
    )
    return Config(**params)


def initialize_node(
    node_name: str,
    config: Config,
    *,
    seed: int,
) -> TwoNodeRuntime:
    state = State(
        trust=config.initial_trust,
        disturbance=config.initial_disturbance,
        stability=config.initial_stability,
        cognitive_distortion=config.initial_cognitive_distortion,
    )
    observed_state = sample_observation(state, config.noise_level, random.Random(seed + 20_000))
    return TwoNodeRuntime(
        node_name=node_name,
        config=config,
        step_fn=make_integrated_step_function(),
        state=state,
        previous_state=State(**state.__dict__),
        observed_state=observed_state,
        previous_observed_state=State(**observed_state.__dict__),
        interventions=Interventions(),
        dynamics_rng=random.Random(seed),
        observation_rng=random.Random(seed + 20_000),
        history=[],
    )


def apply_cross_node_coupling(
    node_a_state: State,
    node_b_state: State,
    *,
    disturbance_coupling: float,
    cognition_coupling: float,
    trust_coupling: float = 0.0,
    disturbance_coupling_ab: Optional[float] = None,
    disturbance_coupling_ba: Optional[float] = None,
    cognition_coupling_ab: Optional[float] = None,
    cognition_coupling_ba: Optional[float] = None,
    trust_coupling_ab: Optional[float] = None,
    trust_coupling_ba: Optional[float] = None,
) -> Tuple[State, State, Dict[str, float], Dict[str, float]]:
    disturbance_coupling_ab = disturbance_coupling if disturbance_coupling_ab is None else disturbance_coupling_ab
    disturbance_coupling_ba = disturbance_coupling if disturbance_coupling_ba is None else disturbance_coupling_ba
    cognition_coupling_ab = cognition_coupling if cognition_coupling_ab is None else cognition_coupling_ab
    cognition_coupling_ba = cognition_coupling if cognition_coupling_ba is None else cognition_coupling_ba
    trust_coupling_ab = trust_coupling if trust_coupling_ab is None else trust_coupling_ab
    trust_coupling_ba = trust_coupling if trust_coupling_ba is None else trust_coupling_ba

    a_from_b_disturbance = disturbance_coupling_ba * node_b_state.disturbance
    b_from_a_disturbance = disturbance_coupling_ab * node_a_state.disturbance
    a_from_b_cognition = cognition_coupling_ba * node_b_state.cognitive_distortion
    b_from_a_cognition = cognition_coupling_ab * node_a_state.cognitive_distortion
    a_from_b_trust = trust_coupling_ba * node_b_state.trust
    b_from_a_trust = trust_coupling_ab * node_a_state.trust

    updated_a = State(
        trust=min(1.0, node_a_state.trust + a_from_b_trust),
        disturbance=min(1.0, node_a_state.disturbance + a_from_b_disturbance),
        stability=node_a_state.stability,
        cognitive_distortion=min(1.0, node_a_state.cognitive_distortion + a_from_b_cognition),
    )
    updated_b = State(
        trust=min(1.0, node_b_state.trust + b_from_a_trust),
        disturbance=min(1.0, node_b_state.disturbance + b_from_a_disturbance),
        stability=node_b_state.stability,
        cognitive_distortion=min(1.0, node_b_state.cognitive_distortion + b_from_a_cognition),
    )
    extras_a = {
        "disturbance_inflow": a_from_b_disturbance,
        "cognition_inflow": a_from_b_cognition,
        "trust_inflow": a_from_b_trust,
    }
    extras_b = {
        "disturbance_inflow": b_from_a_disturbance,
        "cognition_inflow": b_from_a_cognition,
        "trust_inflow": b_from_a_trust,
    }
    return updated_a, updated_b, extras_a, extras_b


def inject_disturbance(node: TwoNodeRuntime, amount: float) -> None:
    node.state = State(
        trust=node.state.trust,
        disturbance=min(1.0, node.state.disturbance + amount),
        stability=node.state.stability,
        cognitive_distortion=node.state.cognitive_distortion,
    )
    node.observed_state = State(
        trust=node.observed_state.trust,
        disturbance=min(1.0, node.observed_state.disturbance + amount),
        stability=node.observed_state.stability,
        cognitive_distortion=node.observed_state.cognitive_distortion,
    )


def pearson_correlation(values_x: List[float], values_y: List[float]) -> float:
    if len(values_x) != len(values_y) or not values_x:
        raise ValueError("Correlation inputs must be non-empty and the same length.")
    mean_x = sum(values_x) / len(values_x)
    mean_y = sum(values_y) / len(values_y)
    centered_x = [value - mean_x for value in values_x]
    centered_y = [value - mean_y for value in values_y]
    numerator = sum(x * y for x, y in zip(centered_x, centered_y))
    denom_x = sum(x * x for x in centered_x)
    denom_y = sum(y * y for y in centered_y)
    if denom_x == 0.0 and denom_y == 0.0:
        return 1.0
    if denom_x == 0.0 or denom_y == 0.0:
        return 0.0
    return numerator / ((denom_x ** 0.5) * (denom_y ** 0.5))


def run_two_node_scenario(
    config_a: Config,
    config_b: Config,
    *,
    steps: int,
    run_seed: int,
    disturbance_coupling: float,
    cognition_coupling: float,
    node_a_injection: float,
    trust_coupling: float = 0.0,
    disturbance_coupling_ab: Optional[float] = None,
    disturbance_coupling_ba: Optional[float] = None,
    cognition_coupling_ab: Optional[float] = None,
    cognition_coupling_ba: Optional[float] = None,
    trust_coupling_ab: Optional[float] = None,
    trust_coupling_ba: Optional[float] = None,
    coupling_delay: int = 0,
) -> Tuple[TwoNodeRuntime, TwoNodeRuntime, Dict[str, float]]:
    node_a = initialize_node("A", config_a, seed=run_seed)
    node_b = initialize_node("B", config_b, seed=run_seed + 1_000)
    coupling_queue: List[Tuple[int, Dict[str, float], Dict[str, float]]] = []

    for step in range(steps):
        if step == 0 and node_a_injection > 0.0:
            inject_disturbance(node_a, node_a_injection)

        per_node_rows: List[Tuple[TwoNodeRuntime, State, Dict[str, float], int]] = []
        for node in (node_a, node_b):
            targets, decision = choose_continuous_targets(
                node.observed_state,
                node.previous_observed_state,
                node.config,
            )
            node.interventions = apply_direct_targets(node.interventions, targets, node.config)
            next_state, extras = node.step_fn(
                node.state,
                node.previous_state,
                node.interventions,
                node.config,
                node.dynamics_rng,
            )
            action_count = sum(
                1
                for value in (
                    targets.disturbance_damping,
                    targets.cognitive_filtering,
                    targets.trust_recovery,
                    targets.reinforcement,
                )
                if value > 1e-9
            )
            per_node_rows.append((node, next_state, {**extras, "decision": decision}, action_count))

        if coupling_delay <= 0:
            coupled_a, coupled_b, coupling_a, coupling_b = apply_cross_node_coupling(
                per_node_rows[0][1],
                per_node_rows[1][1],
                disturbance_coupling=disturbance_coupling,
                cognition_coupling=cognition_coupling,
                trust_coupling=trust_coupling,
                disturbance_coupling_ab=disturbance_coupling_ab,
                disturbance_coupling_ba=disturbance_coupling_ba,
                cognition_coupling_ab=cognition_coupling_ab,
                cognition_coupling_ba=cognition_coupling_ba,
                trust_coupling_ab=trust_coupling_ab,
                trust_coupling_ba=trust_coupling_ba,
            )
        else:
            due_a = {"disturbance_inflow": 0.0, "cognition_inflow": 0.0, "trust_inflow": 0.0}
            due_b = {"disturbance_inflow": 0.0, "cognition_inflow": 0.0, "trust_inflow": 0.0}
            remaining_queue: List[Tuple[int, Dict[str, float], Dict[str, float]]] = []
            for due_step, inflow_a, inflow_b in coupling_queue:
                if due_step <= step:
                    for key in due_a:
                        due_a[key] += inflow_a[key]
                        due_b[key] += inflow_b[key]
                else:
                    remaining_queue.append((due_step, inflow_a, inflow_b))
            coupling_queue = remaining_queue

            coupled_a = State(
                trust=min(1.0, per_node_rows[0][1].trust + due_a["trust_inflow"]),
                disturbance=min(1.0, per_node_rows[0][1].disturbance + due_a["disturbance_inflow"]),
                stability=per_node_rows[0][1].stability,
                cognitive_distortion=min(1.0, per_node_rows[0][1].cognitive_distortion + due_a["cognition_inflow"]),
            )
            coupled_b = State(
                trust=min(1.0, per_node_rows[1][1].trust + due_b["trust_inflow"]),
                disturbance=min(1.0, per_node_rows[1][1].disturbance + due_b["disturbance_inflow"]),
                stability=per_node_rows[1][1].stability,
                cognitive_distortion=min(1.0, per_node_rows[1][1].cognitive_distortion + due_b["cognition_inflow"]),
            )
            coupling_a = dict(due_a)
            coupling_b = dict(due_b)
            _, _, scheduled_a, scheduled_b = apply_cross_node_coupling(
                coupled_a,
                coupled_b,
                disturbance_coupling=disturbance_coupling,
                cognition_coupling=cognition_coupling,
                trust_coupling=trust_coupling,
                disturbance_coupling_ab=disturbance_coupling_ab,
                disturbance_coupling_ba=disturbance_coupling_ba,
                cognition_coupling_ab=cognition_coupling_ab,
                cognition_coupling_ba=cognition_coupling_ba,
                trust_coupling_ab=trust_coupling_ab,
                trust_coupling_ba=trust_coupling_ba,
            )
            coupling_queue.append((step + coupling_delay, scheduled_a, scheduled_b))
        coupled_states = {
            "A": (coupled_a, coupling_a),
            "B": (coupled_b, coupling_b),
        }

        stability_gap = abs(coupled_a.stability - coupled_b.stability)
        both_below_threshold = int(
            coupled_a.stability < config_a.stability_threshold and coupled_b.stability < config_b.stability_threshold
        )

        for node, _, extras, action_count in per_node_rows:
            next_state, coupling_extras = coupled_states[node.node_name]
            sampled_observation = sample_observation(next_state, node.config.noise_level, node.observation_rng)
            next_observed_state = smooth_observation(sampled_observation, node.observed_state, node.config.alpha)
            intervention_total = (
                node.interventions.disturbance_damping
                + node.interventions.cognitive_filtering
                + node.interventions.trust_recovery
                + node.interventions.reinforcement
            )
            node.history.append(
                {
                    "step": step,
                    "node": node.node_name,
                    "trust": next_state.trust,
                    "disturbance": next_state.disturbance,
                    "stability": next_state.stability,
                    "cognitive_distortion": next_state.cognitive_distortion,
                    "trust_filtered": next_observed_state.trust,
                    "disturbance_filtered": next_observed_state.disturbance,
                    "cognitive_distortion_filtered": next_observed_state.cognitive_distortion,
                    "disturbance_damping": node.interventions.disturbance_damping,
                    "cognitive_filtering": node.interventions.cognitive_filtering,
                    "trust_recovery": node.interventions.trust_recovery,
                    "reinforcement": node.interventions.reinforcement,
                    "intervention_total": intervention_total,
                    "executed_action_count": action_count,
                    "stability_gap": stability_gap,
                    "both_below_threshold": both_below_threshold,
                    "coupling_delay": coupling_delay,
                    **extras,
                    **coupling_extras,
                }
            )
            node.previous_state = State(**node.state.__dict__)
            node.previous_observed_state = State(**node.observed_state.__dict__)
            node.state = next_state
            node.observed_state = next_observed_state

    summary_a = summarize_run(node_a.history, threshold=config_a.stability_threshold)
    summary_b = summarize_run(node_b.history, threshold=config_b.stability_threshold)
    stability_series_a = [row["stability"] for row in node_a.history]
    stability_series_b = [row["stability"] for row in node_b.history]
    synchronization = pearson_correlation(stability_series_a, stability_series_b)
    avg_gap = sum(abs(a - b) for a, b in zip(stability_series_a, stability_series_b)) / len(stability_series_a)
    propagation_breach = int(any(row["stability"] < config_b.stability_threshold for row in node_b.history))
    simultaneous_breach = int(any(row["both_below_threshold"] for row in node_a.history))
    summary = {
        "node_a_final_stability": float(summary_a["final_stability"]),
        "node_b_final_stability": float(summary_b["final_stability"]),
        "node_a_stability_rate": float(summary_a["stability_rate"]),
        "node_b_stability_rate": float(summary_b["stability_rate"]),
        "node_a_failure": int(summary_a["failure_case"]),
        "node_b_failure": int(summary_b["failure_case"]),
        "node_a_recovered": int(summary_a["recovered_run"]),
        "node_b_recovered": int(summary_b["recovered_run"]),
        "node_a_final_trust": float(summary_a["final_trust"]),
        "node_b_final_trust": float(summary_b["final_trust"]),
        "propagated_breach": propagation_breach,
        "propagated_failure": int(summary_b["failure_case"]),
        "synchronization_correlation": synchronization,
        "avg_stability_gap": avg_gap,
        "simultaneous_breach": simultaneous_breach,
    }
    return node_a, node_b, summary


def build_two_node_scenarios(base_config: Config) -> List[Tuple[str, Config, Config, float]]:
    integrated = build_integrated_config(base_config)
    low_control = Config(**{**integrated.__dict__, "intervention_budget": 0.40})
    constraint = build_constraint_config(integrated)

    return [
        ("node_a_disturbance_only", integrated, integrated, 0.48),
        ("node_a_high_node_b_low", integrated, low_control, 0.48),
        ("both_constraint", constraint, constraint, 0.48),
    ]


def run_suite(
    base_config: Config,
    *,
    runs: int,
    steps: int,
    seed: int,
    disturbance_coupling: float,
    cognition_coupling: float,
) -> Tuple[List[Dict[str, float]], List[Dict[str, float]]]:
    summary_rows: List[Dict[str, float]] = []
    raw_rows: List[Dict[str, float]] = []

    for scenario_name, config_a, config_b, node_a_injection in build_two_node_scenarios(base_config):
        scenario_runs: List[Dict[str, float]] = []
        for run_index in range(runs):
            _, _, summary = run_two_node_scenario(
                config_a,
                config_b,
                steps=steps,
                run_seed=seed + run_index,
                disturbance_coupling=disturbance_coupling,
                cognition_coupling=cognition_coupling,
                node_a_injection=node_a_injection,
            )
            scenario_runs.append(
                {
                    "scenario": scenario_name,
                    "run_index": run_index,
                    "seed": seed + run_index,
                    **summary,
                }
            )

        summary_rows.append(
            {
                "scenario": scenario_name,
                "node_a_avg_final_stability": sum(row["node_a_final_stability"] for row in scenario_runs) / len(scenario_runs),
                "node_b_avg_final_stability": sum(row["node_b_final_stability"] for row in scenario_runs) / len(scenario_runs),
                "node_a_stable_run_rate": sum(1 for row in scenario_runs if row["node_a_failure"] == 0 and row["node_a_recovered"] == 0) / len(scenario_runs),
                "node_b_stable_run_rate": sum(1 for row in scenario_runs if row["node_b_failure"] == 0 and row["node_b_recovered"] == 0) / len(scenario_runs),
                "node_a_failure_rate": sum(row["node_a_failure"] for row in scenario_runs) / len(scenario_runs),
                "node_b_failure_rate": sum(row["node_b_failure"] for row in scenario_runs) / len(scenario_runs),
                "node_a_recovery_rate": sum(row["node_a_recovered"] for row in scenario_runs) / len(scenario_runs),
                "node_b_recovery_rate": sum(row["node_b_recovered"] for row in scenario_runs) / len(scenario_runs),
                "node_a_avg_final_trust": sum(row["node_a_final_trust"] for row in scenario_runs) / len(scenario_runs),
                "node_b_avg_final_trust": sum(row["node_b_final_trust"] for row in scenario_runs) / len(scenario_runs),
                "propagated_breach_rate": sum(row["propagated_breach"] for row in scenario_runs) / len(scenario_runs),
                "propagated_failure_rate": sum(row["propagated_failure"] for row in scenario_runs) / len(scenario_runs),
                "avg_synchronization_correlation": (
                    sum(row["synchronization_correlation"] for row in scenario_runs) / len(scenario_runs)
                ),
                "avg_stability_gap": sum(row["avg_stability_gap"] for row in scenario_runs) / len(scenario_runs),
                "simultaneous_breach_rate": sum(row["simultaneous_breach"] for row in scenario_runs) / len(scenario_runs),
            }
        )
        raw_rows.extend(scenario_runs)

    return summary_rows, raw_rows


def print_suite(summary_rows: List[Dict[str, float]]) -> None:
    print("Governance two-node summary")
    for row in summary_rows:
        print(
            f"- {row['scenario']}: "
            f"A stability={row['node_a_avg_final_stability']:.3f}, "
            f"B stability={row['node_b_avg_final_stability']:.3f}, "
            f"A failure={row['node_a_failure_rate']:.3f}, "
            f"B failure={row['node_b_failure_rate']:.3f}, "
            f"propagated_failure={row['propagated_failure_rate']:.3f}, "
            f"sync={row['avg_synchronization_correlation']:.3f}"
        )


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a 2-node SOE v1.3 simulation with disturbance and cognition coupling."
    )
    parser.add_argument("--steps", type=int, default=100, help="Number of time steps per run.")
    parser.add_argument("--runs", type=int, default=20, help="Number of randomized runs per scenario.")
    parser.add_argument("--seed", type=int, default=42, help="Base random seed.")
    parser.add_argument("--disturbance-coupling", type=float, default=0.05, help="Cross-node disturbance spread.")
    parser.add_argument("--cognition-coupling", type=float, default=0.05, help="Cross-node cognition spread.")
    parser.add_argument(
        "--output-prefix",
        type=pathlib.Path,
        default=pathlib.Path("governance_two_node"),
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

    summary_rows, raw_rows = run_suite(
        config,
        runs=args.runs,
        steps=args.steps,
        seed=args.seed,
        disturbance_coupling=args.disturbance_coupling,
        cognition_coupling=args.cognition_coupling,
    )

    summary_path = args.output_prefix.with_name(f"{args.output_prefix.name}_summary.csv")
    runs_path = args.output_prefix.with_name(f"{args.output_prefix.name}_runs.csv")
    write_csv(summary_path, summary_rows)
    write_csv(runs_path, raw_rows)
    print_suite(summary_rows)
    print(f"Saved summary to {summary_path}")
    print(f"Saved runs to {runs_path}")


if __name__ == "__main__":
    main()
