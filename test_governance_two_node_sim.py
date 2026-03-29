import unittest

from governance_loop_sim import Config, State
from governance_two_node_sim import (
    apply_cross_node_coupling,
    build_constraint_config,
    build_two_node_scenarios,
    pearson_correlation,
)


class GovernanceTwoNodeSimTests(unittest.TestCase):
    def test_cross_node_coupling_spreads_disturbance_and_cognition(self) -> None:
        node_a = State(trust=0.8, disturbance=0.6, stability=0.8, cognitive_distortion=0.3)
        node_b = State(trust=0.8, disturbance=0.2, stability=0.8, cognitive_distortion=0.1)

        updated_a, updated_b, extras_a, extras_b = apply_cross_node_coupling(
            node_a,
            node_b,
            disturbance_coupling=0.05,
            cognition_coupling=0.10,
        )

        self.assertAlmostEqual(updated_a.disturbance, 0.61)
        self.assertAlmostEqual(updated_b.disturbance, 0.23)
        self.assertAlmostEqual(updated_a.cognitive_distortion, 0.31)
        self.assertAlmostEqual(updated_b.cognitive_distortion, 0.13)
        self.assertAlmostEqual(extras_b["disturbance_inflow"], 0.03)

    def test_cross_node_coupling_supports_directional_trust_flow(self) -> None:
        node_a = State(trust=0.9, disturbance=0.2, stability=0.8, cognitive_distortion=0.1)
        node_b = State(trust=0.4, disturbance=0.2, stability=0.8, cognitive_distortion=0.1)

        updated_a, updated_b, extras_a, extras_b = apply_cross_node_coupling(
            node_a,
            node_b,
            disturbance_coupling=0.0,
            cognition_coupling=0.0,
            trust_coupling=0.0,
            trust_coupling_ab=0.2,
            trust_coupling_ba=0.0,
        )

        self.assertAlmostEqual(updated_a.trust, 0.9)
        self.assertAlmostEqual(updated_b.trust, 0.58)
        self.assertAlmostEqual(extras_b["trust_inflow"], 0.18)
        self.assertAlmostEqual(extras_a["trust_inflow"], 0.0)

    def test_build_constraint_config_lowers_capacity_and_smoothing(self) -> None:
        constrained = build_constraint_config(Config())

        self.assertEqual(constrained.intervention_budget, 0.40)
        self.assertEqual(constrained.alpha, 1.00)
        self.assertEqual(constrained.intervention_decay, 0.22)

    def test_two_node_scenarios_define_three_requested_cases(self) -> None:
        scenarios = build_two_node_scenarios(Config())

        self.assertEqual([name for name, *_ in scenarios], [
            "node_a_disturbance_only",
            "node_a_high_node_b_low",
            "both_constraint",
        ])

    def test_pearson_correlation_handles_identical_series(self) -> None:
        self.assertEqual(pearson_correlation([1.0, 1.0], [1.0, 1.0]), 1.0)


if __name__ == "__main__":
    unittest.main()
