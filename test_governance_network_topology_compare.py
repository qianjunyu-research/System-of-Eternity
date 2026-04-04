import random
import unittest

from governance_network_topology_compare import (
    classify_spatial_distribution,
    graph_to_neighbors,
    normalize_topologies,
    parse_float_list,
    shortest_path_distances,
)
from soe_v3.soe_v3_topology import build_phase1_topology


class GovernanceNetworkTopologyCompareTests(unittest.TestCase):
    def test_graph_to_neighbors_preserves_chain_shape(self) -> None:
        graph = build_phase1_topology("chain", list(range(5)), random.Random(1))
        neighbors = graph_to_neighbors(graph)
        self.assertEqual(neighbors[0], [1])
        self.assertEqual(neighbors[2], [1, 3])
        self.assertEqual(neighbors[4], [3])

    def test_shortest_path_distances_for_star(self) -> None:
        graph = build_phase1_topology("star", list(range(5)), random.Random(1))
        distances = shortest_path_distances(graph, origin_index=0)
        self.assertEqual(distances[0], 0)
        self.assertEqual(distances[4], 1)

    def test_classify_spatial_distribution_detects_network_wide_chain(self) -> None:
        graph = build_phase1_topology("chain", list(range(8)), random.Random(1))
        label = classify_spatial_distribution(graph, [0, 1, 2, 3, 4, 5, 6], origin_index=0)
        self.assertEqual(label, "network_wide")

    def test_classify_spatial_distribution_detects_hub_localized_star(self) -> None:
        graph = build_phase1_topology("star", list(range(8)), random.Random(1))
        label = classify_spatial_distribution(graph, [0, 3, 5], origin_index=0)
        self.assertEqual(label, "hub_localized")

    def test_normalize_topologies_accepts_user_friendly_aliases(self) -> None:
        topologies = normalize_topologies("chain, star, random, fully connected")
        self.assertEqual(topologies, ("chain", "star", "random-sparse", "fully-connected"))

    def test_parse_float_list_reads_csv_values(self) -> None:
        values = parse_float_list("0.02, 0.03, 0.05")
        self.assertEqual(values, (0.02, 0.03, 0.05))


if __name__ == "__main__":
    unittest.main()
