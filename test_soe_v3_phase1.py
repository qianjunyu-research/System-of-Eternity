import random
import unittest

from soe_v3.soe_v3_metrics import compute_cascade_depth, compute_survival_clusters
from soe_v3.soe_v3_runner import Phase1RunConfig, compute_cni_rows, run_phase1_experiment
from soe_v3.soe_v3_topology import (
    build_chain_topology,
    build_fully_connected_topology,
    build_random_sparse_topology,
    build_star_topology,
)


class SOEV3TopologyTests(unittest.TestCase):
    def test_fully_connected_topology_has_complete_edge_count(self) -> None:
        graph = build_fully_connected_topology([0, 1, 2, 3])
        self.assertEqual(graph.number_of_edges(), 6)

    def test_chain_topology_has_expected_end_degrees(self) -> None:
        graph = build_chain_topology([0, 1, 2, 3, 4])
        self.assertEqual(graph.degree(0), 1)
        self.assertEqual(graph.degree(2), 2)
        self.assertEqual(graph.degree(4), 1)

    def test_star_topology_uses_first_node_as_hub(self) -> None:
        graph = build_star_topology([0, 1, 2, 3, 4])
        self.assertEqual(graph.degree(0), 4)
        self.assertTrue(all(graph.degree(node_id) == 1 for node_id in [1, 2, 3, 4]))

    def test_random_sparse_topology_keeps_backbone_connected(self) -> None:
        graph = build_random_sparse_topology([0, 1, 2, 3, 4], random.Random(1))
        self.assertEqual(graph.connected_components_count(), 1)
        self.assertGreaterEqual(graph.number_of_edges(), 4)


class SOEV3MetricTests(unittest.TestCase):
    def test_survival_clusters_returns_component_sizes(self) -> None:
        graph = build_chain_topology([0, 1, 2, 3, 4])
        clusters = compute_survival_clusters(graph, [0, 1, 3])
        self.assertEqual(clusters, [2, 1])

    def test_cascade_depth_measures_distance_from_origin(self) -> None:
        graph = build_chain_topology([0, 1, 2, 3, 4])
        depth = compute_cascade_depth(graph, [0], [0, 1, 2, 3])
        self.assertEqual(depth, 3)


class SOEV3RunnerTests(unittest.TestCase):
    def test_phase1_run_produces_summary_and_history(self) -> None:
        result = run_phase1_experiment(
            Phase1RunConfig(
                topology="chain",
                seed=3,
                years=40,
                step_years=10,
                failure_policy="specific",
                failure_node_ids=(0,),
            )
        )

        self.assertEqual(result.summary["topology"], "chain")
        self.assertEqual(len(result.history_rows), 5)
        self.assertEqual(result.summary["initial_failure_ids"], [0])
        self.assertIn("failure_rate", result.summary)
        self.assertIn("survival_clusters", result.summary)

    def test_cni_rows_rank_requested_candidates(self) -> None:
        result = run_phase1_experiment(
            Phase1RunConfig(
                topology="star",
                seed=5,
                years=20,
                step_years=10,
                failure_policy="none",
            )
        )
        cni_rows = compute_cni_rows(result, limit=3)
        self.assertEqual(len(cni_rows), 3)
        self.assertGreaterEqual(cni_rows[0]["critical_node_index"], cni_rows[-1]["critical_node_index"])


if __name__ == "__main__":
    unittest.main()
