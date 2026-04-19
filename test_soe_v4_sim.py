import unittest

from soe_v4.soe_v4_sim import SuiteConfig, build_topology, default_scenarios, run_document_suite


class SOEV4TopologyTests(unittest.TestCase):
    def test_federation_topology_is_connected_by_construction(self) -> None:
        neighbors = build_topology(18, "federation", __import__("random").Random(1))
        self.assertTrue(all(len(node_neighbors) >= 2 for node_neighbors in neighbors))

    def test_hub_topology_has_central_node(self) -> None:
        neighbors = build_topology(12, "hub", __import__("random").Random(1))
        self.assertEqual(len(neighbors[0]), 11)


class SOEV4RunnerTests(unittest.TestCase):
    def test_document_suite_returns_one_summary_per_default_scenario(self) -> None:
        config = SuiteConfig(seed=7, runs=2, years=80, step_years=10, nodes=12)
        summary_rows, raw_rows = run_document_suite(config)
        self.assertEqual(len(summary_rows), len(default_scenarios()))
        self.assertEqual(len(raw_rows), len(default_scenarios()) * config.runs)

    def test_summary_metrics_stay_in_unit_interval_when_expected(self) -> None:
        config = SuiteConfig(seed=9, runs=2, years=60, step_years=10, nodes=12)
        summary_rows, _ = run_document_suite(config)
        for row in summary_rows:
            for key in (
                "final_avg_trust",
                "final_avg_disturbance",
                "final_avg_cognition",
                "final_avg_identity",
                "final_avg_stability",
                "min_avg_stability",
                "stable_node_step_share",
                "low_trust_node_step_share",
            ):
                self.assertGreaterEqual(float(row[key]), 0.0)
                self.assertLessEqual(float(row[key]), 1.0)


if __name__ == "__main__":
    unittest.main()
