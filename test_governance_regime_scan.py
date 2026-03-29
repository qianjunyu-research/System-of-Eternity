import unittest

from governance_integration import build_integrated_config
from governance_loop_sim import Config
from governance_regime_scan import classify_first_stressor, summarize_regime_batch


class GovernanceRegimeScanTests(unittest.TestCase):
    def test_classify_first_stressor_prefers_earliest_crossing(self) -> None:
        config = build_integrated_config(Config())
        history = [
            {"step": 0, "trust": 0.82, "disturbance": 0.20, "cognitive_distortion": 0.18},
            {"step": 1, "trust": 0.81, "disturbance": 0.50, "cognitive_distortion": 0.20},
            {"step": 2, "trust": 0.68, "disturbance": 0.52, "cognitive_distortion": 0.30},
        ]

        label = classify_first_stressor(history, config)

        self.assertEqual(label, "disturbance")

    def test_summarize_regime_batch_reports_first_stressor_rates(self) -> None:
        config = build_integrated_config(Config())
        histories = [
            [
                {"step": 0, "stability": 0.84, "trust": 0.82, "disturbance": 0.50, "cognitive_distortion": 0.18, "intervention_total": 0.40},
                {"step": 1, "stability": 0.83, "trust": 0.79, "disturbance": 0.52, "cognitive_distortion": 0.19, "intervention_total": 0.42},
                {"step": 2, "stability": 0.82, "trust": 0.78, "disturbance": 0.40, "cognitive_distortion": 0.20, "intervention_total": 0.41},
                {"step": 3, "stability": 0.81, "trust": 0.77, "disturbance": 0.38, "cognitive_distortion": 0.21, "intervention_total": 0.39},
                {"step": 4, "stability": 0.80, "trust": 0.76, "disturbance": 0.36, "cognitive_distortion": 0.22, "intervention_total": 0.37},
                {"step": 5, "stability": 0.81, "trust": 0.75, "disturbance": 0.35, "cognitive_distortion": 0.23, "intervention_total": 0.36},
            ],
            [
                {"step": 0, "stability": 0.84, "trust": 0.82, "disturbance": 0.20, "cognitive_distortion": 0.45, "intervention_total": 0.35},
                {"step": 1, "stability": 0.83, "trust": 0.80, "disturbance": 0.22, "cognitive_distortion": 0.46, "intervention_total": 0.36},
                {"step": 2, "stability": 0.82, "trust": 0.79, "disturbance": 0.23, "cognitive_distortion": 0.44, "intervention_total": 0.37},
                {"step": 3, "stability": 0.81, "trust": 0.78, "disturbance": 0.24, "cognitive_distortion": 0.43, "intervention_total": 0.38},
                {"step": 4, "stability": 0.80, "trust": 0.77, "disturbance": 0.25, "cognitive_distortion": 0.42, "intervention_total": 0.39},
                {"step": 5, "stability": 0.81, "trust": 0.76, "disturbance": 0.26, "cognitive_distortion": 0.41, "intervention_total": 0.40},
            ],
        ]

        summary = summarize_regime_batch(
            histories,
            config,
            test_name="constraint_activation",
            scenario="smoke",
            note="smoke",
        )

        self.assertEqual(summary["scenario"], "smoke")
        self.assertGreater(summary["disturbance_first_rate"], 0.0)
        self.assertGreater(summary["cognition_first_rate"], 0.0)


if __name__ == "__main__":
    unittest.main()
