import unittest

from soe_v4.claude_brief_suite import (
    GateScenario,
    OperatingPoint,
    ParameterSet,
    calibrate_parameters,
    hero_gate_activation_day,
    margin,
)


class SOEV4ClaudeBriefTests(unittest.TestCase):
    def test_margin_matches_structural_inequality(self) -> None:
        parameter_set = ParameterSet(a=0.2, b=0.22, c=0.15, lam=0.2, alpha=0.2, mu=0.2)
        point = OperatingPoint("test", disturbance=0.2, cognition=0.1, identity=0.8, recovery=0.04, expected="stable")
        self.assertGreater(margin(parameter_set, point), 0.0)

    def test_gate_does_not_fire_on_single_spike(self) -> None:
        scenario = GateScenario(
            name="single_spike",
            class_name="adversarial",
            true_disturbance=[0.4, 0.8, 0.4, 0.4],
            true_trust=[0.4, 0.2, 0.4, 0.4],
            coordination_failures=[1, 1, 1, 1],
            collapse_step=None,
        )
        self.assertIsNone(hero_gate_activation_day(scenario, 1))

    def test_calibration_finds_candidates_in_smaller_sample(self) -> None:
        result = calibrate_parameters(5000, 3)
        self.assertTrue(result["accepted_sets"])


if __name__ == "__main__":
    unittest.main()
