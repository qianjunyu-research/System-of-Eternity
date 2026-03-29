import unittest

from governance_two_node_advanced_followups import average_metrics


class GovernanceTwoNodeAdvancedFollowupTests(unittest.TestCase):
    def test_average_metrics_aggregates_expected_fields(self) -> None:
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
                "node_a_stability_rate": 0.5,
                "node_b_stability_rate": 0.0,
                "node_a_failure": 1.0,
                "node_b_failure": 1.0,
                "node_a_recovered": 0.0,
                "node_b_recovered": 1.0,
                "propagated_breach": 1.0,
                "propagated_failure": 0.0,
                "synchronization_correlation": 0.4,
                "avg_stability_gap": 0.1,
                "simultaneous_breach": 1.0,
                "node_a_final_trust": 0.7,
                "node_b_final_trust": 0.4,
            },
        ]

        averaged = average_metrics(rows)

        self.assertAlmostEqual(averaged["node_b_final_stability"], 0.7)
        self.assertAlmostEqual(averaged["node_b_failure"], 1.0)
        self.assertAlmostEqual(averaged["node_b_final_trust"], 0.5)


if __name__ == "__main__":
    unittest.main()
