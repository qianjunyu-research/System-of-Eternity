# SOE Grand Simulation v0.5 Main-Matrix Transfer Report

## Transfer Configuration

- Federation Psi profile: `stability_heavy_no_regime`.
- Federation Psi weights: `T=0.2`, `D=0.2`, `G=0.15`, `S=0.35`, `regime=0.0`.
- Federation Psi threshold: `0.3`.
- Locked `psi_lambda`: `0.1`.
- Transfer goal: move CL02 from focused diagnostic support to main-matrix transfer evidence.

## Batch

- Runs: `420`.
- Scenarios: `14`.
- Profiles: `3`.
- Traceability statuses: `{'supported': 5, 'supported_in_v0_5_transfer': 1, 'context_dependent': 1, 'measured': 3}`.
- Interpretation boundary: architecture/simulation evidence only; not deployment-ready.

## Mid-Stress Scenario Snapshot

| Scenario | Ignition rate | Avg peak collapse | Avg Trigger A count | Avg false-stability steps |
|---|---:|---:|---:|---:|
| async_message_loss | 0.0 | 0.1 | 0.0 | 0.0 |
| federation_bridge_stress | 0.0 | 0.1 | 0.0 | 0.0 |
| federation_cluster_attack | 0.0 | 0.333333 | 104.3 | 0.0 |
| governance_capture | 1.0 | 1.0 | 61.9 | 78.0 |
| hub_2_balanced | 1.0 | 1.0 | 116.4 | 0.0 |
| hub_2_single_hub_failure | 1.0 | 0.5 | 112.9 | 0.0 |
| hub_3_balanced | 1.0 | 1.0 | 116.0 | 0.0 |
| hub_3_single_hub_failure | 0.0 | 0.135 | 113.1 | 0.0 |
| mixed_hia_identity | 0.0 | 0.0 | 0.0 | 0.0 |
| psi_corruption | 0.0 | 0.333333 | 60.7 | 0.0 |
| ring_baseline | 0.0 | 0.0 | 0.0 | 0.0 |
| star_unsafe_reference | 1.0 | 1.0 | 125.2 | 0.0 |
| topology_drift | 1.0 | 1.0 | 80.0 | 0.0 |
| trigger_b_deadlock | 1.0 | 1.0 | 118.3 | 6.0 |

## Claim Traceability

| Claim | Status | Metric | Value |
|---|---|---|---:|
| CL01 | supported | federation_c04_trigger_A_violations | 0 |
| CL02 | supported_in_v0_5_transfer | on_time_tpr;false_positive_rate;avg_lead_to_collapse30 | 1.0;0.0;7.9875 |
| CL03 | supported | avg_deadlock_trigger_B_count | 93.4 |
| CL04 | supported | star_sustained_ignition_rate | 0.666667 |
| CL05 | context_dependent | all_hub_delta;single_hub_delta | 0.0;0.333333 |
| CL06 | measured | mixed_hia_identity_peak_collapse | 0.333333 |
| CL07 | supported | avg_governance_capture_false_stability_steps | 59.833333 |
| CL08 | supported | avg_async_false_stability_steps | 0.066667 |
| CL09 | measured | avg_reclassification_latency_steps | 0.0 |
| CL10 | measured | resource_exhaustion_rate_all_runs | 0.390476 |

## Artifacts

- `grand_sim_v0_5_runs.csv`
- `grand_sim_v0_5_steps.csv`
- `grand_sim_v0_5_scenario_summary.csv`
- `grand_sim_v0_5_traceability.csv`
