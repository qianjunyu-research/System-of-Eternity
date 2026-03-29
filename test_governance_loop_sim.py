import unittest
import random

from governance_loop_sim import (
    Config,
    Interventions,
    State,
    activate_interventions,
    choose_governance_response,
    compute_trust_recovery_effect,
    default_parameters,
    drain_due_decisions,
    queue_decision,
    resolve_execution_delay,
    run_simulation,
    sample_observation,
    smooth_observation,
    summarize_run,
)


def average_run_metric(config: Config, metric: str, runs: int = 8, steps: int = 80, seed: int = 100) -> float:
    total = 0.0
    for run_index in range(runs):
        history = run_simulation(config, steps=steps, seed=seed + run_index)
        summary = summarize_run(history, threshold=config.stability_threshold)
        total += float(summary[metric])
    return total / runs


class GovernanceLoopTests(unittest.TestCase):
    def test_compound_stress_activates_all_three_core_mechanisms(self) -> None:
        config = Config()
        previous = State(trust=0.72, disturbance=0.40, stability=0.78, cognitive_distortion=0.30)
        current = State(trust=0.68, disturbance=0.56, stability=0.74, cognitive_distortion=0.46)

        actions, decision = choose_governance_response(current, previous, config)

        self.assertEqual(decision, "compound_stress")
        self.assertEqual(
            actions,
            ["disturbance_damping", "cognitive_filtering", "trust_recovery"],
        )

    def test_intervention_budget_is_enforced(self) -> None:
        config = Config(intervention_budget=1.0, intervention_decay=0.0, activation_gain=1.0)
        interventions = Interventions()

        updated = activate_interventions(
            interventions,
            ["disturbance_damping", "cognitive_filtering", "trust_recovery"],
            config,
        )

        total = (
            updated.disturbance_damping
            + updated.cognitive_filtering
            + updated.trust_recovery
            + updated.reinforcement
        )
        self.assertLessEqual(total, config.intervention_budget + 1e-9)

    def test_governance_materially_improves_outcomes(self) -> None:
        params = default_parameters()
        governed = Config(**params)
        unguided = Config(**{**params, "intervention_budget": 0.0, "activation_gain": 0.0})

        governed_final_stability = average_run_metric(governed, "final_stability")
        unguided_final_stability = average_run_metric(unguided, "final_stability")
        governed_failure_rate = average_run_metric(governed, "failure_case")
        unguided_failure_rate = average_run_metric(unguided, "failure_case")

        self.assertGreater(governed_final_stability, unguided_final_stability + 0.15)
        self.assertLess(governed_failure_rate, unguided_failure_rate)

    def test_alpha_one_preserves_raw_observation(self) -> None:
        previous = State(trust=0.70, disturbance=0.20, stability=0.81, cognitive_distortion=0.10)
        actual = State(trust=0.55, disturbance=0.62, stability=0.74, cognitive_distortion=0.48)

        observed = smooth_observation(actual, previous, alpha=1.0)

        self.assertEqual(observed.trust, actual.trust)
        self.assertEqual(observed.disturbance, actual.disturbance)
        self.assertEqual(observed.cognitive_distortion, actual.cognitive_distortion)
        self.assertEqual(observed.stability, actual.stability)

    def test_lower_alpha_smooths_signal_jump(self) -> None:
        previous = State(trust=0.80, disturbance=0.18, stability=0.84, cognitive_distortion=0.16)
        actual = State(trust=0.40, disturbance=0.70, stability=0.70, cognitive_distortion=0.60)

        observed = smooth_observation(actual, previous, alpha=0.2)

        self.assertGreater(observed.trust, actual.trust)
        self.assertLess(observed.disturbance, actual.disturbance)
        self.assertLess(observed.cognitive_distortion, actual.cognitive_distortion)

    def test_zero_observation_noise_preserves_state(self) -> None:
        actual = State(trust=0.63, disturbance=0.41, stability=0.79, cognitive_distortion=0.27)

        observed = sample_observation(actual, noise_level=0.0, rng=random.Random(3))

        self.assertEqual(observed.trust, actual.trust)
        self.assertEqual(observed.disturbance, actual.disturbance)
        self.assertEqual(observed.cognitive_distortion, actual.cognitive_distortion)
        self.assertEqual(observed.stability, actual.stability)

    def test_observation_noise_stays_bounded(self) -> None:
        actual = State(trust=0.02, disturbance=0.98, stability=0.81, cognitive_distortion=0.01)

        observed = sample_observation(actual, noise_level=0.1, rng=random.Random(5))

        self.assertTrue(0.0 <= observed.trust <= 1.0)
        self.assertTrue(0.0 <= observed.disturbance <= 1.0)
        self.assertTrue(0.0 <= observed.cognitive_distortion <= 1.0)
        self.assertEqual(observed.stability, actual.stability)

    def test_trust_cap_reduces_recovery_at_high_trust(self) -> None:
        base_recovery = 0.20
        trust = 0.80

        uncapped = compute_trust_recovery_effect(base_recovery, trust, cap_strength=0.0)
        capped = compute_trust_recovery_effect(base_recovery, trust, cap_strength=1.0)

        self.assertEqual(uncapped, base_recovery)
        self.assertLess(capped, uncapped)

    def test_sensitivity_offsets_trigger_earlier(self) -> None:
        previous = State(trust=0.80, disturbance=0.33, stability=0.83, cognitive_distortion=0.20)
        current = State(trust=0.792, disturbance=0.38, stability=0.81, cognitive_distortion=0.21)

        baseline_actions, baseline_decision = choose_governance_response(current, previous, Config())
        adjusted_actions, adjusted_decision = choose_governance_response(
            current,
            previous,
            Config(
                trust_threshold_offset=0.006,
                disturbance_threshold_offset=0.04,
                compound_sensitivity_offset=0.05,
            ),
        )

        self.assertEqual(baseline_decision, "stability_reinforcement")
        self.assertEqual(baseline_actions, ["reinforcement"])
        self.assertEqual(adjusted_decision, "compound_stress")
        self.assertIn("disturbance_damping", adjusted_actions)

    def test_execution_queue_defers_actions_until_due(self) -> None:
        queue = []

        queue_decision(queue, current_step=0, execution_delay=2.0, actions=["trust_recovery"], decision="trust_decline")

        remaining, actions_now, decisions_now = drain_due_decisions(queue, current_step=0)
        self.assertEqual(actions_now, [])
        self.assertEqual(decisions_now, [])

        remaining, actions_due, decisions_due = drain_due_decisions(remaining, current_step=2)
        self.assertEqual(actions_due, ["trust_recovery"])
        self.assertEqual(decisions_due, ["trust_decline"])

    def test_stochastic_delay_stays_within_declared_range(self) -> None:
        config = Config(max_delay=3.0)
        rng = random.Random(7)

        sampled = [resolve_execution_delay(config, rng) for _ in range(20)]

        self.assertTrue(all(1 <= value <= 3 for value in sampled))
        self.assertGreater(len(set(sampled)), 1)

    def test_run_history_records_queued_execution(self) -> None:
        config = Config(execution_delay=2.0)

        history = run_simulation(config, steps=4, seed=7)

        self.assertEqual(history[0]["executed_decisions"], "idle")
        self.assertEqual(history[1]["executed_decisions"], "idle")
        self.assertNotEqual(history[2]["executed_decisions"], "idle")


if __name__ == "__main__":
    unittest.main()
