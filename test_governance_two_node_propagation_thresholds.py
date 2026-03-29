import unittest

from governance_loop_sim import build_config, default_parameters
from governance_two_node_propagation_thresholds import average_metrics, build_suite


class GovernanceTwoNodePropagationThresholdTests(unittest.TestCase):
    def test_average_metrics_tracks_trust_and_failure_fields(self) -> None:
        rows = [
            {
                "node_a_final_stability": 1.0,
                "node_b_final_stability": 0.8,
                "node_a_stability_rate": 1.0,
                "node_b_stability_rate": 0.4,
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
                "node_b_final_trust": 0.5,
            },
            {
                "node_a_final_stability": 0.8,
                "node_b_final_stability": 0.6,
                "node_a_stability_rate": 0.8,
                "node_b_stability_rate": 0.2,
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
                "node_b_final_trust": 0.9,
            },
        ]

        averaged = average_metrics(rows)

        self.assertAlmostEqual(averaged["node_b_failure"], 0.5)
        self.assertAlmostEqual(averaged["node_b_final_trust"], 0.7)
        self.assertAlmostEqual(averaged["avg_stability_gap"], 0.2)

    def test_build_suite_includes_requested_scan_labels(self) -> None:
        config = build_config(default_parameters())

        summary_rows, _ = build_suite(config, runs=1, steps=2, seed=1)

        labels = {row["label"] for row in summary_rows}
        self.assertIn("threshold_t_0.00", labels)
        self.assertIn("threshold_t_0.20", labels)
        self.assertIn("mixed_channels_t_0.01", labels)
        self.assertIn("delay2_t_0.20", labels)


if __name__ == "__main__":
    unittest.main()
