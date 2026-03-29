import random
import unittest

from governance_falsification import choose_continuous_targets
from governance_integration import (
    build_integrated_config,
    choose_continuous_targets_trust_blind,
    make_integrated_step_function,
    run_batch_with_factories,
)
from governance_loop_sim import Config, Interventions, State


class GovernanceIntegrationTests(unittest.TestCase):
    def test_integrated_config_applies_expected_smoothing_profile(self) -> None:
        integrated = build_integrated_config(Config())

        self.assertEqual(integrated.execution_delay, 0.0)
        self.assertEqual(integrated.alpha, 0.80)
        self.assertEqual(integrated.intervention_decay, 0.65)

    def test_trust_blind_controller_ignores_trust_drop_when_other_signals_match(self) -> None:
        config = build_integrated_config(Config())
        previous = State(trust=0.80, disturbance=0.35, stability=0.81, cognitive_distortion=0.20)
        current_low_trust = State(trust=0.55, disturbance=0.52, stability=0.74, cognitive_distortion=0.33)
        current_high_trust = State(trust=0.75, disturbance=0.52, stability=0.74, cognitive_distortion=0.33)

        low_targets, _ = choose_continuous_targets_trust_blind(current_low_trust, previous, config)
        high_targets, _ = choose_continuous_targets_trust_blind(current_high_trust, previous, config)

        self.assertEqual(low_targets, high_targets)

    def test_integrated_step_reports_memory_and_shape_metadata(self) -> None:
        step_fn = make_integrated_step_function(nonlinear_cognition=True, memory_window=3)
        config = build_integrated_config(Config())
        previous = State(trust=0.80, disturbance=0.20, stability=0.84, cognitive_distortion=0.18)
        current = State(trust=0.76, disturbance=0.25, stability=0.82, cognitive_distortion=0.21)

        _, extras = step_fn(current, previous, Interventions(), config, random.Random(5))

        self.assertEqual(extras["memory_window"], 3)
        self.assertEqual(extras["cognition_shape"], "nonlinear")
        self.assertIn("derived_cap_strength", extras)

    def test_run_batch_with_factories_returns_expected_rows(self) -> None:
        summary, raw_rows = run_batch_with_factories(
            build_integrated_config(Config()),
            test_name="integration",
            scenario="smoke",
            runs=2,
            steps=6,
            seed=3,
            controller=choose_continuous_targets,
            step_factory=lambda: make_integrated_step_function(),
        )

        self.assertEqual(summary["test_name"], "integration")
        self.assertEqual(summary["scenario"], "smoke")
        self.assertEqual(len(raw_rows), 2)


if __name__ == "__main__":
    unittest.main()
