import unittest

from governance_loop_sim import State
from governance_network_sim import apply_coupling, update_activation_mask


class GovernanceNetworkSimTests(unittest.TestCase):
    def test_activation_threshold_blocks_subthreshold_neighbors(self) -> None:
        states = [
            State(trust=0.7, disturbance=0.10, stability=0.8, cognitive_distortion=0.1),
            State(trust=0.7, disturbance=0.20, stability=0.8, cognitive_distortion=0.4),
        ]
        updated = apply_coupling(
            states,
            neighbors=[[1], [0]],
            k_d=0.5,
            k_c=0.5,
            migration_rate=0.0,
            activation_threshold=0.25,
            propagation_exponent=2.0,
        )

        self.assertAlmostEqual(updated[0].disturbance, states[0].disturbance)
        self.assertAlmostEqual(updated[0].cognitive_distortion, states[0].cognitive_distortion)
        self.assertAlmostEqual(updated[1].disturbance, states[1].disturbance)

    def test_nonlinear_propagation_uses_active_neighbor_disturbance_power(self) -> None:
        states = [
            State(trust=0.7, disturbance=0.10, stability=0.8, cognitive_distortion=0.1),
            State(trust=0.7, disturbance=0.50, stability=0.8, cognitive_distortion=0.4),
        ]
        updated = apply_coupling(
            states,
            neighbors=[[1], [0]],
            k_d=0.5,
            k_c=0.5,
            migration_rate=0.0,
            activation_threshold=0.25,
            propagation_exponent=2.0,
        )

        self.assertAlmostEqual(updated[0].disturbance, 0.225)
        self.assertAlmostEqual(updated[0].cognitive_distortion, 0.15)

    def test_neighbor_feedback_scales_active_input_by_ratio(self) -> None:
        states = [
            State(trust=0.7, disturbance=0.10, stability=0.8, cognitive_distortion=0.1),
            State(trust=0.7, disturbance=0.50, stability=0.8, cognitive_distortion=0.4),
            State(trust=0.7, disturbance=0.50, stability=0.8, cognitive_distortion=0.4),
        ]
        updated = apply_coupling(
            states,
            neighbors=[[1, 2], [0], [0]],
            k_d=0.5,
            k_c=0.5,
            migration_rate=0.0,
            activation_threshold=0.25,
            propagation_exponent=2.0,
            neighbor_feedback_strength=0.4,
        )

        self.assertAlmostEqual(updated[0].disturbance, 0.275)
        self.assertAlmostEqual(updated[0].cognitive_distortion, 0.17)

    def test_hysteresis_keeps_active_node_on_until_lower_threshold(self) -> None:
        states = [
            State(trust=0.7, disturbance=0.12, stability=0.8, cognitive_distortion=0.1),
            State(trust=0.7, disturbance=0.08, stability=0.8, cognitive_distortion=0.1),
        ]
        active_mask = update_activation_mask(
            states,
            previous_active_mask=[True, True],
            activation_threshold=0.20,
            deactivation_threshold=0.10,
        )

        self.assertEqual(active_mask, [True, False])


if __name__ == "__main__":
    unittest.main()
