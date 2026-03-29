import unittest

from governance_loop_sim import Config
from governance_two_node_followups import average_summaries, clone_config


class GovernanceTwoNodeFollowupsTests(unittest.TestCase):
    def test_clone_config_applies_overrides(self) -> None:
        cloned = clone_config(Config(), intervention_budget=0.40, noise_level=0.02)

        self.assertEqual(cloned.intervention_budget, 0.40)
        self.assertEqual(cloned.noise_level, 0.02)

    def test_average_summaries_averages_metrics(self) -> None:
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
            },
        ]

        averaged = average_summaries(rows)

        self.assertAlmostEqual(averaged["node_a_final_stability"], 0.9)
        self.assertAlmostEqual(averaged["node_b_failure"], 1.0)
        self.assertAlmostEqual(averaged["synchronization_correlation"], 0.3)


if __name__ == "__main__":
    unittest.main()
