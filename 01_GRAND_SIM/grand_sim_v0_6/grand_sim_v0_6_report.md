# SOE Grand Simulation v0.6 Focused Stress Report

## Transfer Configuration

- Federation Psi profile: `stability_heavy_no_regime`.
- Federation Psi weights: `T=0.2`, `D=0.2`, `G=0.15`, `S=0.35`, `regime=0.0`.
- Federation Psi threshold: `0.3`.
- Locked `psi_lambda`: `0.1`.
- v0.6 goal: extend the frozen v0.5 main matrix into CL09 topology lag, CL05 unbalanced hubs, and CL10 resource stress.

## Batch

- Runs: `630`.
- Scenarios: `21`.
- Profiles: `3`.
- Traceability statuses: `{'supported': 5, 'supported_in_v0_6_regression': 1, 'context_dependent_unbalanced_tested': 1, 'measured': 1, 'supported_in_v0_6_stress': 1, 'stress_measured_v0_6': 1}`.
- Interpretation boundary: architecture/simulation evidence only; not deployment-ready.

## Mid-Stress Scenario Snapshot

| Scenario | Ignition rate | Avg peak collapse | Avg topology wrong-monitoring steps | Avg resource floor steps | Avg routing-delay loss |
|---|---:|---:|---:|---:|---:|
| async_message_loss | 0.0 | 0.1 | 0.0 | 3.9 | 0.0 |
| federation_bridge_stress | 0.0 | 0.1 | 0.0 | 81.0 | 0.0 |
| federation_cluster_attack | 0.0 | 0.333333 | 0.0 | 82.3 | 0.0 |
| governance_capture | 1.0 | 1.0 | 0.0 | 0.0 | 0.0 |
| hub_2_balanced | 1.0 | 1.0 | 0.0 | 20.8 | 0.0 |
| hub_2_single_hub_failure | 1.0 | 0.5 | 0.0 | 71.3 | 0.0 |
| hub_2_unbalanced_primary_failure | 1.0 | 0.948333 | 0.0 | 72.0 | 0.0 |
| hub_3_balanced | 1.0 | 0.998333 | 0.0 | 62.2 | 0.0 |
| hub_3_single_hub_failure | 0.0 | 0.11 | 0.0 | 26.5 | 0.0 |
| hub_3_unbalanced_primary_failure | 0.1 | 0.32 | 0.0 | 42.1 | 0.0 |
| hub_3_unbalanced_secondary_failure | 0.0 | 0.103334 | 0.0 | 20.5 | 0.0 |
| mixed_hia_identity | 0.0 | 0.003333 | 0.0 | 0.0 | 0.0 |
| psi_corruption | 0.0 | 0.333333 | 0.0 | 80.4 | 0.0 |
| resource_budget_shock | 1.0 | 1.0 | 0.0 | 112.3 | 0.0 |
| resource_routing_delay | 1.0 | 1.0 | 0.0 | 106.0 | 0.010361 |
| ring_baseline | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| star_unsafe_reference | 1.0 | 1.0 | 0.0 | 0.0 | 0.0 |
| topology_drift | 1.0 | 1.0 | 25.0 | 23.0 | 0.0 |
| topology_lag_centralizing | 1.0 | 1.0 | 50.0 | 29.7 | 0.0 |
| topology_misclassification_async | 1.0 | 1.0 | 65.0 | 0.0 | 0.0 |
| trigger_b_deadlock | 1.0 | 1.0 | 0.0 | 107.0 | 0.0 |

## Claim Traceability

| Claim | Status | Metric | Value |
|---|---|---|---:|
| CL01 | supported | federation_c04_trigger_A_violations | 0 |
| CL02 | supported_in_v0_6_regression | on_time_tpr;false_positive_rate;avg_lead_to_collapse30 | 1.0;0.0;7.8625 |
| CL03 | supported | avg_deadlock_trigger_B_count | 93.3 |
| CL04 | supported | star_sustained_ignition_rate | 0.666667 |
| CL05 | context_dependent_unbalanced_tested | all_hub_delta;single_hub_delta;unbalanced_primary_delta;hub3_secondary_ignition | 0.0;0.333333;0.3;0.333333 |
| CL06 | measured | mixed_hia_identity_peak_collapse | 0.334444 |
| CL07 | supported | avg_governance_capture_false_stability_steps | 59.566667 |
| CL08 | supported | avg_async_false_stability_steps | 0.233333 |
| CL09 | supported_in_v0_6_stress | avg_latency;avg_wrong_monitoring_steps;avg_topology_false_stability_steps;max_wrong_monitoring_window | 46.666667;46.666667;0.0;65 |
| CL10 | stress_measured_v0_6 | resource_exhaustion_rate_all_runs;stress_exhaustion_rate;avg_stress_floor_steps;avg_routing_delay_loss | 0.41746;1.0;112.583333;0.005169 |

## Artifacts

- `grand_sim_v0_6_runs.csv`
- `grand_sim_v0_6_steps.csv`
- `grand_sim_v0_6_scenario_summary.csv`
- `grand_sim_v0_6_traceability.csv`
