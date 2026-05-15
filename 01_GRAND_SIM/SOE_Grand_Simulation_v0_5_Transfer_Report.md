# SOE Grand Simulation v0.5 Main-Matrix Transfer Report

Date: 2026-05-08

Purpose: transfer the v0.4 CL02 no-regime Psi detector into the main integrated grand-sim matrix.

## Transfer Configuration

Federation Trigger A uses:

- variant: `no_regime_ablation`
- weight profile: `stability_heavy`
- `psi_lambda = 0.10`
- `psi_threshold = 0.30`
- `w_r = 0.0`

Weights:

| Term | Weight |
|---|---:|
| `1 - T_mean` | 0.20 |
| `D_effective_mean` | 0.20 |
| `1 - G_effective` | 0.15 |
| `1 - S_network` | 0.35 |
| regime/collapse term | 0.00 |
| `cluster_variance` multiplier | 0.10 |

Non-federation Trigger A remains C04 S-threshold.

## Batch

- Runs: `420`.
- Step rows: `67,200`.
- Scenarios: `14`.
- Profiles: `3`.

## Validation

| Check | Result |
|---|---:|
| Federation C04 Trigger A violations | 0 |
| Max `k_D_effective` | 0.13 |
| Max `k_C_effective` | 0.10 |
| Minimum break-condition margin | 0.006735 |
| Federation `psi_w_regime` values | 0.0 |
| State variable bounds | passed |

## CL02 Transfer Result

Across federation transfer scenarios:

- Federation rows: `120`.
- Positive event rows (`collapse_share >= 0.30`): `80`.
- No-event federation rows: `40`.
- On-time detections: `80 / 80`.
- Missed detections: `0 / 80`.
- False positives: `0 / 40`.
- On-time TPR: `1.0`.
- False-positive rate: `0.0`.
- Average lead to `collapse_share >= 0.30`: `7.9875` steps.
- Lead distribution caveat: two positive `psi_corruption / mid_stress` runs detect at the event step (`lead = 0`), so not every positive run has positive lead.

Traceability status:

> CL02: `supported_in_v0_5_transfer`.

Use careful wording:

> CL02 is supported in the v0.5 main-matrix transfer run. This remains simulation evidence, not deployment readiness.

## Scenario-Level Federation Transfer

| Scenario | Profile | Positive runs | No-event runs | On-time TPR | FP rate | Avg lead |
|---|---|---:|---:|---:|---:|---:|
| `async_message_loss` | high | 10 | 0 | 1.0 | 0.0 | 12.0 |
| `async_message_loss` | low | 0 | 10 | 0.0 | 0.0 | n/a |
| `async_message_loss` | mid | 0 | 10 | 0.0 | 0.0 | n/a |
| `federation_bridge_stress` | high | 10 | 0 | 1.0 | 0.0 | 7.9 |
| `federation_bridge_stress` | low | 0 | 10 | 0.0 | 0.0 | n/a |
| `federation_bridge_stress` | mid | 0 | 10 | 0.0 | 0.0 | n/a |
| `federation_cluster_attack` | high | 10 | 0 | 1.0 | 0.0 | 8.1 |
| `federation_cluster_attack` | low | 10 | 0 | 1.0 | 0.0 | 18.1 |
| `federation_cluster_attack` | mid | 10 | 0 | 1.0 | 0.0 | 9.5 |
| `psi_corruption` | high | 10 | 0 | 1.0 | 0.0 | 2.0 |
| `psi_corruption` | low | 10 | 0 | 1.0 | 0.0 | 3.9 |
| `psi_corruption` | mid | 10 | 0 | 1.0 | 0.0 | 2.4 |

## Other Claim Statuses

From `grand_sim_v0_5_traceability.csv`:

- CL01: `supported`
- CL02: `supported_in_v0_5_transfer`
- CL03: `supported`
- CL04: `supported`
- CL05: `context_dependent`
- CL06: `measured`
- CL07: `supported`
- CL08: `supported`
- CL09: `measured`
- CL10: `measured`

## Interpretation

v0.5 clears the main blocker from v0.4: the no-regime federation detector transfers into the integrated main matrix without losing event detection or creating no-event federation false positives.

This does not close deployment readiness. It does justify updating CL02 from "focused diagnostic only" to "supported in v0.5 main-matrix transfer."

## Remaining Work

1. Add topology detection lag/misclassification to the main matrix for CL09.
2. Add integrated unbalanced hub scenarios to close the v18 D/E comparison gap.
3. Add harsher resource-budget contention/routing-delay stress for CL10.
4. Consider adversarial Psi tests later: stability-term ablation, shuffled controls, and high-variance/no-collapse federation cases.

## Artifacts

- `soe_grand_sim_v0_5.py`
- `grand_sim_v0_5/grand_sim_v0_5_runs.csv`
- `grand_sim_v0_5/grand_sim_v0_5_steps.csv`
- `grand_sim_v0_5/grand_sim_v0_5_scenario_summary.csv`
- `grand_sim_v0_5/grand_sim_v0_5_traceability.csv`
- `grand_sim_v0_5/grand_sim_v0_5_federation_transfer_summary.csv`
- `grand_sim_v0_5/grand_sim_v0_5_validation_summary.csv`
