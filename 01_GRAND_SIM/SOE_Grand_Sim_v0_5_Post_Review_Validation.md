# SOE Grand Sim v0.5 Post-Review Validation

Date: 2026-05-08

Purpose: answer the text-only Copilot validation checklist and clarify reviewer caveats before v0.6.

## Added Validation Artifacts

- `grand_sim_v0_5/grand_sim_v0_5_threshold_sensitivity.csv`
- `grand_sim_v0_5/grand_sim_v0_5_threshold_sensitivity_by_scenario.csv`
- `grand_sim_v0_5/grand_sim_v0_5_lead_distribution.csv`
- `grand_sim_v0_5/grand_sim_v0_5_precursor_trace_samples.csv`
- `grand_sim_v0_5/grand_sim_v0_5_review_validation_addendum.csv`

## Copilot Checklist Status

| Check | Result |
|---|---|
| Required run columns present | pass |
| Required step columns present | pass |
| Non-federation C07 Trigger A sources | 0 |
| Max federation step `psi_term_regime` | 0.0 |
| Federation positive runs with on-time/nonnegative lead | 80 / 80 |

## Threshold Sensitivity

| Threshold | On-time TPR | FP rate | Avg lead | Min lead | Max lead |
|---:|---:|---:|---:|---:|---:|
| 0.26 | 1.0 | 0.0 | 11.7 | 3 | 24 |
| 0.28 | 1.0 | 0.0 | 10.1125 | 2 | 22 |
| 0.30 | 1.0 | 0.0 | 7.9875 | 0 | 20 |
| 0.32 | 0.75 | 0.0 | 8.15 | 0 | 18 |
| 0.34 | 0.75 | 0.0 | 6.766667 | 0 | 17 |

Interpretation: `0.30` remains the conservative transfer threshold, but it is close to the upper edge of the passing band. Raising to `0.32` loses on-time coverage.

## Lead Distribution At Threshold 0.30

| Metric | Value |
|---|---:|
| Count | 80 |
| Min | 0 |
| P25 | 3 |
| Median | 8 |
| P75 | 11 |
| P95 | 19 |
| Max | 20 |
| Avg | 7.9875 |

Two `psi_corruption / mid_stress` runs fire at the event step (`lead = 0`). This does not break on-time transfer support, but it means the phrase "positive lead across all runs" should not be used.

## Updated Interpretation

CL02 remains supported in the v0.5 main-matrix transfer run. The precise wording should be:

> CL02 is supported in v0.5 main-matrix transfer with on-time detection, zero federation false positives, and average lead `7.9875`; two positive runs detect at the event step, so not every run has positive lead.

Deployment readiness remains blocked.

