import unittest

from soe_v4.full_campaign import (
    HeroGateOption,
    classify_single_run,
    hero_gate_cycle,
)


class SOEV4FullCampaignTests(unittest.TestCase):
    def test_classify_single_run_marks_collapse_when_collapse_time_exists(self) -> None:
        regime = classify_single_run(
            [0.7, 0.5, 0.2],
            [0.2, 0.5, 0.6],
            [0.1, 0.2, 0.3],
            collapse_time=2,
        )
        self.assertEqual(regime, "collapse")

    def test_hero_gate_cycle_respects_duration(self) -> None:
        sequence = {
            "disturbance": [0.8, 0.8, 0.8, 0.6],
            "trust": [0.2, 0.2, 0.2, 0.3],
            "failures": [2, 2, 2, 1],
        }
        self.assertEqual(hero_gate_cycle(sequence, HeroGateOption("72h", 24, False)), 1)
        self.assertIsNone(hero_gate_cycle(sequence, HeroGateOption("72h", 48, False)))


if __name__ == "__main__":
    unittest.main()
