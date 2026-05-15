# SOE Grand Simulation v0.3 Focused Calibration Report

## Scope

v0.3 is a focused calibration/reproduction package, not a broad C00-C08 matrix.

Focus areas:

- CL02 Psi federation detector calibration.
- CL09 topology detection lag and misclassification.
- v18 hub-redundancy reproduction comparison.

## Psi Sweep

- Accepted locked-lambda candidates: `34`.
- Recommended locked candidate: `stability_heavy`, `psi_lambda = 0.10`, `psi_threshold = 0.30`.
- Candidate metrics: detected TPR `1.0`, on-time TPR `1.0`, missed rate `0.0`, false positive rate `0.0`, average lead `11.8125` steps.
- Status: calibration path found, but precursor independence is not established because `psi_score` includes `collapse_share` through `regime_weight`. CL02 should not be marked supported in the main grand-sim matrix until the regime term is ablated/decomposed and the main matrix is patched and rerun.

## Topology Lag

- Worst wrong-monitoring condition: recheck interval `10`, detection delay `20`, misclassification rate `0.25`.
- Worst-condition metrics: centralizing detection rate `0.0`, star-adjacent detection rate `0.8`, average star-adjacent latency `21.25`, average wrong-monitoring steps `52.0`, average star-adjacent undetected steps `27.0`.
- Named risk: the worst condition misses the intermediate `centralizing` topology entirely, so transition-specific monitoring never activates in that case.

## Hub Reproduction

| Comparison | v18 ignition | v0.2 mid-stress ignition | Delta |
|---|---:|---:|---:|
| v18_2hub_balanced | 1.0 | 1.0 | 0.0 |
| v18_3hub_balanced | 0.0 | 1.0 | 1.0 |
| v18_2hub_unbalanced | 1.0 |  |  |
| v18_3hub_unbalanced | 0.0 |  |  |

## Artifacts

- `grand_sim_v0_3_psi_sweep_runs.csv`
- `grand_sim_v0_3_psi_sweep_summary.csv`
- `grand_sim_v0_3_topology_lag_runs.csv`
- `grand_sim_v0_3_topology_lag_summary.csv`
- `grand_sim_v0_3_hub_reproduction_comparison.csv`
