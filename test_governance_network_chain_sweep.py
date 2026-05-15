import unittest

from governance_network_chain_sweep import (
    build_chain_neighbors,
    contiguous_cluster_sizes,
    measure_run_metrics,
    near_threshold_rows,
)
from governance_network_sim import apply_intrinsic_decay
from governance_loop_sim import State


class GovernanceNetworkChainSweepTests(unittest.TestCase):
    def test_build_chain_neighbors_has_no_wraparound(self) -> None:
        neighbors = build_chain_neighbors(5)
        self.assertEqual(neighbors[0], [1])
        self.assertEqual(neighbors[2], [1, 3])
        self.assertEqual(neighbors[4], [3])

    def test_measure_run_metrics_tracks_propagation_beyond_origin(self) -> None:
        class FakeNode:
            def __init__(self, rows):
                self.history = rows

        def make_row(step: int, stability: float, disturbance: float) -> dict:
            return {
                "step": step,
                "stability": stability,
                "trust": 0.7,
                "disturbance": disturbance,
                "cognitive_distortion": 0.1,
                "intervention_total": 0.0,
            }

        nodes = [
            FakeNode([make_row(0, 0.20, 0.8), make_row(1, 0.20, 0.8)]),
            FakeNode([make_row(0, 0.60, 0.2), make_row(1, 0.20, 0.8)]),
            FakeNode([make_row(0, 0.70, 0.2), make_row(1, 0.60, 0.4)]),
        ]
        metrics = measure_run_metrics(nodes, threshold=0.3, origin_index=0)

        self.assertAlmostEqual(metrics["failure_rate"], 2 / 3)
        self.assertAlmostEqual(metrics["affected_share"], 0.5)
        self.assertEqual(metrics["cascade_depth"], 1)
        self.assertEqual(metrics["sustained_failure_steps"], 1)
        self.assertEqual(metrics["time_to_collapse"], 1)
        self.assertEqual(metrics["propagated"], 0)
        self.assertEqual(metrics["last_affected_node"], 1)
        self.assertEqual(metrics["survival_cluster_sizes"], "1")

    def test_measure_run_metrics_requires_more_than_single_remote_breach(self) -> None:
        class FakeNode:
            def __init__(self, rows):
                self.history = rows

        def make_row(step: int, stability: float) -> dict:
            return {
                "step": step,
                "stability": stability,
                "trust": 0.7,
                "disturbance": 0.2,
                "cognitive_distortion": 0.1,
                "intervention_total": 0.0,
            }

        nodes = [
            FakeNode([make_row(0, 0.20), make_row(1, 0.20), make_row(2, 0.20)]),
            FakeNode([make_row(0, 0.60), make_row(1, 0.60), make_row(2, 0.60)]),
            FakeNode([make_row(0, 0.60), make_row(1, 0.20), make_row(2, 0.60)]),
            FakeNode([make_row(0, 0.70), make_row(1, 0.70), make_row(2, 0.70)]),
            FakeNode([make_row(0, 0.70), make_row(1, 0.70), make_row(2, 0.70)]),
            FakeNode([make_row(0, 0.70), make_row(1, 0.70), make_row(2, 0.70)]),
            FakeNode([make_row(0, 0.70), make_row(1, 0.70), make_row(2, 0.70)]),
        ]
        metrics = measure_run_metrics(nodes, threshold=0.3, origin_index=0)

        self.assertAlmostEqual(metrics["affected_share"], 1 / 6)
        self.assertEqual(metrics["cascade_depth"], 2)
        self.assertEqual(metrics["sustained_failure_steps"], 1)
        self.assertEqual(metrics["propagated"], 0)

    def test_measure_run_metrics_requires_all_three_thresholds(self) -> None:
        class FakeNode:
            def __init__(self, rows):
                self.history = rows

        def make_row(step: int, stability: float) -> dict:
            return {
                "step": step,
                "stability": stability,
                "trust": 0.7,
                "disturbance": 0.4,
                "cognitive_distortion": 0.2,
                "intervention_total": 0.0,
            }

        stable = [make_row(0, 0.70), make_row(1, 0.70), make_row(2, 0.70), make_row(3, 0.70)]
        failed = [make_row(0, 0.20), make_row(1, 0.20), make_row(2, 0.20), make_row(3, 0.20)]
        nodes = [
            FakeNode(failed),
            FakeNode(failed),
            FakeNode(failed),
            FakeNode(failed),
            FakeNode(failed),
            FakeNode(failed),
            FakeNode(stable),
        ]
        metrics = measure_run_metrics(nodes, threshold=0.3, origin_index=0)

        self.assertAlmostEqual(metrics["affected_share"], 5 / 6)
        self.assertEqual(metrics["cascade_depth"], 5)
        self.assertEqual(metrics["sustained_failure_steps"], 4)
        self.assertEqual(metrics["propagated"], 1)

    def test_contiguous_cluster_sizes_breaks_on_affected_nodes(self) -> None:
        self.assertEqual(contiguous_cluster_sizes(8, [0, 1, 4, 7]), [2, 2])

    def test_near_threshold_rows_filters_partial_propagation(self) -> None:
        rows = [
            {"near_threshold": 0, "propagation_share": 0.0, "avg_cascade_depth": 0.0, "avg_failure_rate": 0.2},
            {"near_threshold": 1, "propagation_share": 0.5, "avg_cascade_depth": 1.2, "avg_failure_rate": 0.3},
            {"near_threshold": 1, "propagation_share": 0.25, "avg_cascade_depth": 0.8, "avg_failure_rate": 0.25},
        ]

        filtered = near_threshold_rows(rows)

        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0]["propagation_share"], 0.5)

    def test_apply_intrinsic_decay_subtracts_fraction_of_previous_state(self) -> None:
        current_states = [
            State(trust=0.60, disturbance=0.40, stability=0.50, cognitive_distortion=0.30)
        ]
        previous_states = [
            State(trust=0.80, disturbance=0.20, stability=0.90, cognitive_distortion=0.10)
        ]

        decayed = apply_intrinsic_decay(current_states, previous_states, alpha=0.10)

        self.assertAlmostEqual(decayed[0].trust, 0.60)
        self.assertAlmostEqual(decayed[0].disturbance, 0.38)
        self.assertAlmostEqual(decayed[0].stability, 0.50)
        self.assertAlmostEqual(decayed[0].cognitive_distortion, 0.29)


if __name__ == "__main__":
    unittest.main()
