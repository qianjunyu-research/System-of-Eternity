import unittest

from governance_loop_sim import build_config, default_parameters
from governance_two_node_threshold_map import (
    DELAY_LEVELS,
    DISTURBANCE_LEVELS,
    TRUST_COUPLING_LEVELS,
    average_metrics,
    build_suite,
    build_threshold_rows,
)


class GovernanceTwoNodeThresholdMapTests(unittest.TestCase):
    def test_average_metrics_preserves_b_failure_and_trust(self) -> None:
        rows = [
            {
                "node_a_final_stability": 1.0,
                "node_b_final_stability": 0.8,
                "node_a_stability_rate": 1.0,
                "node_b_stability_rate": 0.5,
                "node_a_failure": 0.0,
                "node_b_failure": 1.0,
                "node_a_recovered": 0.0,
                "node_b_recovered": 0.0,
                "propagated_breach": 1.0,
                "propagated_failure": 1.0,
                "synchronization_correlation": 0.2,
                "avg_stability_gap": 0.3,
                "simultaneous_breach": 0.0,
                "node_a_final_trust": 0.9,
                "node_b_final_trust": 0.6,
            },
            {
                "node_a_final_stability": 0.8,
                "node_b_final_stability": 0.6,
                "node_a_stability_rate": 0.8,
                "node_b_stability_rate": 0.0,
                "node_a_failure": 0.0,
                "node_b_failure": 0.0,
                "node_a_recovered": 1.0,
                "node_b_recovered": 1.0,
                "propagated_breach": 1.0,
                "propagated_failure": 0.0,
                "synchronization_correlation": 0.4,
                "avg_stability_gap": 0.1,
                "simultaneous_breach": 1.0,
                "node_a_final_trust": 0.7,
                "node_b_final_trust": 0.8,
            },
        ]

        averaged = average_metrics(rows)

        self.assertAlmostEqual(averaged["node_b_failure"], 0.5)
        self.assertAlmostEqual(averaged["node_b_final_trust"], 0.7)
        self.assertAlmostEqual(averaged["node_b_final_stability"], 0.7)

    def test_build_threshold_rows_picks_smallest_zero_failure(self) -> None:
        summary_rows = [
            {
                "disturbance_level": 0.2,
                "coupling_delay": 0,
                "trust_coupling": 0.0,
                "node_b_failure": 0.10,
                "node_b_final_stability": 0.92,
                "node_b_final_trust": 0.80,
                "node_a_final_stability": 1.0,
                "node_a_final_trust": 0.96,
            },
            {
                "disturbance_level": 0.2,
                "coupling_delay": 0,
                "trust_coupling": 0.02,
                "node_b_failure": 0.00,
                "node_b_final_stability": 0.98,
                "node_b_final_trust": 0.95,
                "node_a_final_stability": 1.0,
                "node_a_final_trust": 0.99,
            },
            {
                "disturbance_level": 0.2,
                "coupling_delay": 0,
                "trust_coupling": 0.05,
                "node_b_failure": 0.00,
                "node_b_final_stability": 0.99,
                "node_b_final_trust": 0.99,
                "node_a_final_stability": 1.0,
                "node_a_final_trust": 1.0,
            },
        ]

        threshold_rows = build_threshold_rows(
            summary_rows,
            disturbance_levels=(0.2,),
            delay_levels=(0,),
            trust_levels=(0.0, 0.01, 0.02, 0.05),
        )

        self.assertEqual(len(threshold_rows), 1)
        self.assertEqual(threshold_rows[0]["k_t_star"], 0.02)
        self.assertTrue(threshold_rows[0]["threshold_found"])

    def test_build_suite_covers_full_grid(self) -> None:
        config = build_config(default_parameters())

        summary_rows, _, threshold_rows = build_suite(
            config,
            disturbance_levels=DISTURBANCE_LEVELS,
            delay_levels=DELAY_LEVELS,
            trust_levels=TRUST_COUPLING_LEVELS,
            runs=1,
            steps=2,
            seed=1,
            disturbance_coupling=0.05,
            cognition_coupling=0.05,
        )

        self.assertEqual(len(summary_rows), len(DISTURBANCE_LEVELS) * len(DELAY_LEVELS) * len(TRUST_COUPLING_LEVELS))
        self.assertEqual(len(threshold_rows), len(DISTURBANCE_LEVELS) * len(DELAY_LEVELS))


if __name__ == "__main__":
    unittest.main()
