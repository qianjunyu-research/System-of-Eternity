import random
import unittest

from governance_integration import build_integrated_config, make_integrated_step_function
from governance_loop_sim import Config, Interventions, State
from governance_no_cap_compare import describe_final_trust, percentile


class GovernanceNoCapCompareTests(unittest.TestCase):
    def test_percentile_uses_linear_interpolation(self) -> None:
        values = [0.1, 0.2, 0.4, 0.8]

        self.assertAlmostEqual(percentile(values, 0.50), 0.3)
        self.assertAlmostEqual(percentile(values, 0.25), 0.175)

    def test_describe_final_trust_reports_saturation_rate(self) -> None:
        summary = describe_final_trust([0.95, 0.99, 1.0, 0.80])

        self.assertEqual(summary["trust_min"], 0.80)
        self.assertEqual(summary["trust_max"], 1.0)
        self.assertAlmostEqual(summary["trust_saturation_rate"], 0.5)

    def test_no_cap_mode_reports_zero_cap_strength(self) -> None:
        config = build_integrated_config(Config())
        previous = State(trust=0.80, disturbance=0.20, stability=0.84, cognitive_distortion=0.18)
        current = State(trust=0.76, disturbance=0.25, stability=0.82, cognitive_distortion=0.21)
        step_fn = make_integrated_step_function(cap_mode="none")

        _, extras = step_fn(current, previous, Interventions(), config, random.Random(5))

        self.assertEqual(extras["cap_mode"], "none")
        self.assertEqual(extras["derived_cap_strength"], 0.0)


if __name__ == "__main__":
    unittest.main()
