# SOE Grand Simulation v0.2 Report

## Batch

- Runs: `420`.
- Scenarios: `14`.
- Profiles: `3`.
- Traceability statuses: `{'supported': 5, 'inconclusive': 1, 'context_dependent': 1, 'measured': 3}`.
- Interpretation boundary: architecture/simulation evidence only; not deployment-ready.

## Mid-Stress Scenario Snapshot

| Scenario | Ignition rate | Avg peak collapse | Avg Trigger A count | Avg false-stability steps |
|---|---:|---:|---:|---:|
| async_message_loss | 0.0 | 0.1 | 0.0 | 0.0 |
| federation_bridge_stress | 0.0 | 0.1 | 0.0 | 0.0 |
| federation_cluster_attack | 0.0 | 0.333333 | 0.0 | 0.0 |
| governance_capture | 1.0 | 1.0 | 62.5 | 78.0 |
| hub_2_balanced | 1.0 | 1.0 | 113.7 | 0.0 |
| hub_2_single_hub_failure | 1.0 | 0.5 | 112.1 | 0.0 |
| hub_3_balanced | 1.0 | 0.998333 | 115.8 | 0.0 |
| hub_3_single_hub_failure | 0.0 | 0.116667 | 113.4 | 0.0 |
| mixed_hia_identity | 0.0 | 0.0 | 0.0 | 0.0 |
| psi_corruption | 0.0 | 0.333333 | 0.0 | 0.0 |
| ring_baseline | 0.0 | 0.0 | 0.0 | 0.0 |
| star_unsafe_reference | 1.0 | 1.0 | 126.9 | 0.0 |
| topology_drift | 1.0 | 1.0 | 80.0 | 0.0 |
| trigger_b_deadlock | 1.0 | 1.0 | 118.3 | 6.0 |

## Claim Traceability

| Claim | Status | Metric | Value |
|---|---|---|---:|
| CL01 | supported | federation_c04_trigger_A_violations | 0 |
| CL02 | inconclusive | federation_psi_detector_run_rate | 0.333333 |
| CL03 | supported | avg_deadlock_trigger_B_count | 93.4 |
| CL04 | supported | star_sustained_ignition_rate | 0.666667 |
| CL05 | context_dependent | all_hub_delta;single_hub_delta | 0.0;0.333333 |
| CL06 | measured | mixed_hia_identity_peak_collapse | 0.333333 |
| CL07 | supported | avg_governance_capture_false_stability_steps | 59.666667 |
| CL08 | supported | avg_async_false_stability_steps | 0.133333 |
| CL09 | measured | avg_reclassification_latency_steps | 0.0 |
| CL10 | measured | resource_exhaustion_rate_all_runs | 0.352381 |

## Artifacts

- `grand_sim_v0_2_runs.csv`
- `grand_sim_v0_2_steps.csv`
- `grand_sim_v0_2_scenario_summary.csv`
- `grand_sim_v0_2_traceability.csv`
