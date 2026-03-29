import random
import unittest

from governance_falsification import (
    apply_direct_targets,
    choose_continuous_targets,
    choose_no_trust_response,
    derived_cap_strength,
    run_batch,
    step_system_derived_cap,
)
from governance_loop_sim import Config, Interventions, State


class GovernanceFalsificationTests(unittest.TestCase):
    def test_no_trust_controller_never_requests_trust_recovery(self) -> None:
        config = Config()
        previous = State(trust=0.79, disturbance=0.44, stability=0.82, cognitive_distortion=0.34)
        current = State(trust=0.70, disturbance=0.58, stability=0.75, cognitive_distortion=0.49)

        actions, decision = choose_no_trust_response(current, previous, config)

        self.assertEqual(decision, "compound_stress_no_trust")
        self.assertNotIn("trust_recovery", actions)

    def test_continuous_targets_become_budget_bounded_when_applied(self) -> None:
        config = Config(intervention_budget=1.0, activation_gain=1.0, intervention_decay=0.0)
        previous = State(trust=0.80, disturbance=0.20, stability=0.84, cognitive_distortion=0.18)
        current = State(trust=0.52, disturbance=0.71, stability=0.70, cognitive_distortion=0.55)

        targets, _ = choose_continuous_targets(current, previous, config)
        applied = apply_direct_targets(Interventions(), targets, config)

        total = (
            applied.disturbance_damping
            + applied.cognitive_filtering
            + applied.trust_recovery
            + applied.reinforcement
        )
        self.assertLessEqual(total, config.intervention_budget + 1e-9)

    def test_derived_cap_strength_rises_with_stress_and_trust_erosion(self) -> None:
        previous = State(trust=0.82, disturbance=0.22, stability=0.84, cognitive_distortion=0.16)
        mild = State(trust=0.80, disturbance=0.24, stability=0.82, cognitive_distortion=0.18)
        severe = State(trust=0.68, disturbance=0.65, stability=0.74, cognitive_distortion=0.58)

        mild_cap = derived_cap_strength(mild, previous)
        severe_cap = derived_cap_strength(severe, previous)

        self.assertGreater(severe_cap, mild_cap)
        self.assertTrue(0.0 <= severe_cap <= 1.0)

    def test_step_system_derived_cap_emits_cap_metric(self) -> None:
        config = Config()
        previous = State(trust=0.79, disturbance=0.20, stability=0.83, cognitive_distortion=0.18)
        current = State(trust=0.75, disturbance=0.26, stability=0.81, cognitive_distortion=0.22)

        _, extras = step_system_derived_cap(current, previous, Interventions(), config, random.Random(4))

        self.assertIn("derived_cap_strength", extras)
        self.assertTrue(0.0 <= extras["derived_cap_strength"] <= 1.0)

    def test_run_batch_returns_summary_row(self) -> None:
        summary, raw_rows = run_batch(
            Config(),
            test_name="smoke",
            scenario="baseline",
            runs=2,
            steps=8,
            seed=9,
        )

        self.assertEqual(summary["test_name"], "smoke")
        self.assertEqual(summary["scenario"], "baseline")
        self.assertEqual(len(raw_rows), 2)


if __name__ == "__main__":
    unittest.main()
