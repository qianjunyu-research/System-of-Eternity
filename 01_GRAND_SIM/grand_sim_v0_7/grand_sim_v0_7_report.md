# SOE Grand Simulation v0.7 Focused Closure Report

## Transfer Configuration

- Federation Psi profile: `stability_heavy_no_regime`.
- Federation Psi weights: `T=0.2`, `D=0.2`, `G=0.15`, `S=0.35`, `regime=0.0`.
- Federation Psi threshold: `0.3`.
- Locked `psi_lambda`: `0.1`.
- v0.7 goal: test CL09 downstream impact, complete CL05 unbalanced hub coverage, grade CL10 resource stress, and add a light CL02 adversarial regression.

## Batch

- Runs: `870`.
- Scenarios: `29`.
- Profiles: `3`.
- Traceability statuses: `{'supported': 5, 'supported_in_v0_7_regression': 1, 'adversarial_measured_v0_7': 1, 'context_dependent_unbalanced_tested': 1, 'measured': 1, 'impact_tested_v0_7': 1, 'graded_stress_measured_v0_7': 1}`.
- Interpretation boundary: architecture/simulation evidence only; not deployment-ready.

## Mid-Stress Scenario Snapshot

| Scenario | Ignition rate | Avg peak collapse | Avg topology wrong-monitoring steps | Avg topology hidden-collapse steps | Avg resource floor steps | Avg routing-delay loss |
|---|---:|---:|---:|---:|---:|---:|
| async_message_loss | 0.0 | 0.1 | 0.0 | 0.0 | 4.7 | 0.0 |
| federation_bridge_stress | 0.0 | 0.1 | 0.0 | 0.0 | 77.9 | 0.0 |
| federation_cluster_attack | 0.0 | 0.333333 | 0.0 | 0.0 | 79.8 | 0.0 |
| governance_capture | 1.0 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| hub_2_balanced | 1.0 | 1.0 | 0.0 | 0.0 | 38.2 | 0.0 |
| hub_2_single_hub_failure | 1.0 | 0.5 | 0.0 | 0.0 | 67.2 | 0.0 |
| hub_2_unbalanced_primary_failure | 1.0 | 0.955 | 0.0 | 0.0 | 70.8 | 0.0 |
| hub_2_unbalanced_secondary_failure | 0.0 | 0.3 | 0.0 | 0.0 | 60.9 | 0.0 |
| hub_3_balanced | 1.0 | 0.998333 | 0.0 | 0.0 | 59.9 | 0.0 |
| hub_3_single_hub_failure | 0.0 | 0.108333 | 0.0 | 0.0 | 16.3 | 0.0 |
| hub_3_unbalanced_primary_failure | 0.0 | 0.325 | 0.0 | 0.0 | 36.6 | 0.0 |
| hub_3_unbalanced_secondary_failure | 0.0 | 0.091667 | 0.0 | 0.0 | 14.8 | 0.0 |
| mixed_hia_identity | 0.0 | 0.003333 | 0.0 | 0.0 | 0.0 | 0.0 |
| psi_corruption | 0.0 | 0.333333 | 0.0 | 0.0 | 82.3 | 0.0 |
| psi_stability_ablation | 0.0 | 0.333333 | 0.0 | 0.0 | 72.0 | 0.0 |
| resource_budget_shock | 1.0 | 1.0 | 0.0 | 0.0 | 112.6 | 0.0 |
| resource_pressure_harsh | 1.0 | 1.0 | 0.0 | 0.0 | 106.0 | 0.010357 |
| resource_pressure_mid | 1.0 | 1.0 | 0.0 | 0.0 | 89.9 | 0.0 |
| resource_pressure_mild | 1.0 | 1.0 | 0.0 | 0.0 | 85.0 | 0.0 |
| resource_routing_delay | 1.0 | 1.0 | 0.0 | 0.0 | 106.0 | 0.010416 |
| ring_baseline | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| star_unsafe_reference | 1.0 | 1.0 | 0.0 | 0.0 | 12.8 | 0.0 |
| topology_drift | 1.0 | 1.0 | 25.0 | 0.0 | 20.5 | 0.0 |
| topology_lag_centralizing | 1.0 | 1.0 | 50.0 | 0.0 | 29.5 | 0.0 |
| topology_lag_governance_capture | 1.0 | 1.0 | 65.0 | 7.6 | 0.0 | 0.0 |
| topology_lag_identity_shock | 1.0 | 1.0 | 65.0 | 6.7 | 0.0 | 0.0 |
| topology_lag_resource_cascade | 1.0 | 1.0 | 65.0 | 0.9 | 105.5 | 0.008292 |
| topology_misclassification_async | 1.0 | 1.0 | 65.0 | 2.2 | 0.0 | 0.0 |
| trigger_b_deadlock | 1.0 | 1.0 | 0.0 | 0.0 | 106.9 | 0.0 |

## Claim Traceability

| Claim | Status | Metric | Value |
|---|---|---|---:|
| CL01 | supported | federation_c04_trigger_A_violations | 0 |
| CL02 | supported_in_v0_7_regression | on_time_tpr;false_positive_rate;avg_lead_to_collapse30 | 1.0;0.0;8.175 |
| CL02A | adversarial_measured_v0_7 | ablation_on_time_tpr;avg_ablation_lead | 0.0;-4.1 |
| CL03 | supported | avg_deadlock_trigger_B_count | 93.366667 |
| CL04 | supported | star_sustained_ignition_rate | 0.666667 |
| CL05 | context_dependent_unbalanced_tested | all_hub_delta;single_hub_delta;unbalanced_primary_delta;unbalanced_secondary_delta;hub3_secondary_ignition | 0.0;0.333333;0.333333;0.0;0.333333 |
| CL06 | measured | mixed_hia_identity_peak_collapse | 0.334444 |
| CL07 | supported | avg_governance_capture_false_stability_steps | 59.433333 |
| CL08 | supported | avg_async_false_stability_steps | 0.366667 |
| CL09 | impact_tested_v0_7 | avg_latency;avg_wrong_monitoring;avg_hidden_collapse;avg_blind_no_trigger;avg_topology_false_stability;max_wrong_window | 46.666667;46.666667;0.244444;0.0;0.0;65 |
| CL10 | graded_stress_measured_v0_7 | resource_exhaustion_rate_all_runs;stress_exhaustion_rate;pressure_exhaustion_rate;avg_stress_floor_steps;avg_routing_delay_loss | 0.470115;1.0;1.0;100.273333;0.004152 |

## Artifacts

- `grand_sim_v0_7_runs.csv`
- `grand_sim_v0_7_steps.csv`
- `grand_sim_v0_7_scenario_summary.csv`
- `grand_sim_v0_7_traceability.csv`
