# SOE Grand Simulation v0.3 Findings

Date: 2026-05-08

Purpose: focused follow-up to v0.2 reviewer consensus. v0.3 is not a broad C00-C08 rerun; it tests three unresolved questions: CL02 Psi federation calibration, CL09 topology detection lag, and the v18 hub-redundancy boundary.

## Executive Result

v0.3 resolves the main interpretation gap left by v0.2:

- CL02 was not proved broken by the v0.2 run-rate metric; that metric counted no-event federation runs as failures. With event-conditioned TP/FP/FN metrics, `Psi_extended` can be calibrated successfully at the locked `psi_lambda = 0.10`.
- CL09 was genuinely under-stressed in v0.2. Adding delayed and misclassified topology observation creates long wrong-monitoring windows.
- The v18 hub boundary reproduces in the standalone v18 harness, but not under v0.2 integrated all-hub stress. The hub claim must stay context-dependent.

Deployment readiness remains blocked.

## CL02 Psi Sweep

Artifacts:

- `grand_sim_v0_3/grand_sim_v0_3_psi_sweep_runs.csv`
- `grand_sim_v0_3/grand_sim_v0_3_psi_sweep_summary.csv`

Sweep design:

- Federation scenarios: `federation_cluster_attack`, `federation_bridge_stress`, `psi_corruption`, `async_message_loss`.
- Event definition: positive runs are runs where actual `collapse_share >= 0.30`; negative runs are no-collapse federation runs.
- Metrics: detected true positive rate, on-time true positive rate, missed detection rate, false positive rate, average lead/lag.
- Locked architecture constraint: `psi_lambda = 0.10`.

Result:

| Candidate | psi_lambda | psi_threshold | detected TPR | on-time TPR | missed rate | false positive rate | avg lead steps |
|---|---:|---:|---:|---:|---:|---:|---:|
| `stability_heavy` | 0.10 | 0.30 | 1.0 | 1.0 | 0.0 | 0.0 | 11.8125 |
| `trust_stability` | 0.10 | 0.30 | 1.0 | 1.0 | 0.0 | 0.0 | 11.3375 |
| `v02_default` | 0.10 | 0.30 | 1.0 | 1.0 | 0.0 | 0.0 | 9.1375 |

Interpretation:

`Psi_extended` is not structurally invalid. It was under-calibrated in v0.2 because thresholds around `0.52-0.56` were too conservative for the integrated federation scenarios. The conservative v0.3 recommendation is to keep `psi_lambda = 0.10` and lower federation Trigger A threshold to `0.30`, with `stability_heavy` as the best-performing candidate. If minimizing formula churn matters more than lead time, the `v02_default` weights at threshold `0.30` also pass.

Reviewer update:

The perfect sweep scores should be treated as a calibration result, not a proof of detector independence. The event definition uses `collapse_share >= 0.30`, while the v0.3 `psi_score` directly includes `collapse_share` through `regime_weight(collapse)`. v0.4 should ablate the regime term (`w_r = 0.0`) and/or log term contributions at `detect_step` before transferring the threshold into the main matrix.

## CL09 Topology Lag

Artifacts:

- `grand_sim_v0_3/grand_sim_v0_3_topology_lag_runs.csv`
- `grand_sim_v0_3/grand_sim_v0_3_topology_lag_summary.csv`

Stress design:

- Actual topology sequence: `ring_mesh -> centralizing -> star_adjacent`.
- Recheck intervals: `1`, `5`, `10` steps.
- Detection delays: `0`, `5`, `10`, `20` steps.
- Misclassification rates: `0.00`, `0.10`, `0.25`.

Worst observed condition:

| recheck interval | detection delay | misclassification | centralizing detection rate | star-adjacent detection rate | avg star latency | avg wrong-monitoring steps | avg star-undetected steps |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 20 | 0.25 | 0.0 | 0.8 | 21.25 | 52.0 | 27.0 |

Interpretation:

The v0.2 `avg_reclassification_latency_steps = 0.0` should be treated as "not stress-tested," not as evidence of realistic instantaneous topology awareness. v0.3 shows that stale topology maps can produce multi-dozen-step wrong-monitoring windows under modest observation delay and misclassification.

Named risk:

In the worst tested condition, `centralizing_detection_rate = 0.0`. This is stronger than ordinary delay: the intermediate centralizing topology is missed entirely, so topology-specific transitional monitoring never activates in that case.

## Hub Reproduction

Artifacts:

- `grand_sim_v0_3/grand_sim_v0_3_hub_reproduction_comparison.csv`

| Comparison | v18 sustained ignition | v0.2 mid-stress sustained ignition | Delta |
|---|---:|---:|---:|
| `v18_2hub_balanced` | 1.0 | 1.0 | 0.0 |
| `v18_3hub_balanced` | 0.0 | 1.0 | 1.0 |
| `v18_2hub_unbalanced` | 1.0 | n/a | n/a |
| `v18_3hub_unbalanced` | 0.0 | n/a | n/a |

Interpretation:

v18 still reproduces the clean standalone boundary: two hubs fail and three hubs survive. v0.2 integrated all-hub stress still overwhelms three hubs. Therefore the correct claim is:

> Three hubs are a minimum tested mitigation under standalone v18 hub-redundancy dynamics and under v0.2 single-hub failure, not a general repair guarantee under integrated all-hub stress.

## Updated Claim Status

| Claim | v0.2 status | v0.3 update |
|---|---|---|
| CL02 Psi federation detector | inconclusive | calibration path found at locked `psi_lambda = 0.10`; threshold needs lowering to `0.30` before marking supported in the main grand-sim matrix |
| CL05 hub mitigation | context-dependent | confirmed context-dependent: standalone v18 survives at three hubs; integrated all-hub stress does not |
| CL09 topology reclassification | measured | stress-tested; delayed/misclassified detection creates wrong-monitoring windows up to `52.0` steps |

## v0.4 Priorities

1. Patch main grand-sim federation threshold configuration and rerun federation scenarios to confirm CL02 in the integrated matrix.
2. Add topology detection lag/misclassification to the main grand-sim scenarios and update CL09 traceability.
3. Add integrated unbalanced hub scenarios to compare against v18 unbalanced configs.
4. Add harsher resource-budget contention/routing-delay stress for CL10.
