# SOE Grand Simulation v0.7 Findings

## Executive Verdict

v0.7 ran successfully as a focused closure batch.

- Runs: 870.
- Step rows: 139,200.
- Scenarios: 29.
- Profiles: 3.
- Boundary: simulation evidence only, not deployment-ready or container-ready evidence.

## Claim Status

| Claim | Status | Metric | Value |
|---|---|---|---:|
| CL02 | supported_in_v0_7_regression | on_time_tpr;false_positive_rate;avg_lead_to_collapse30 | 1.0;0.0;8.175 |
| CL02A | adversarial_measured_v0_7 | ablation_on_time_tpr;avg_ablation_lead | 0.0;-4.1 |
| CL05 | context_dependent_unbalanced_tested | all_hub_delta;single_hub_delta;unbalanced_primary_delta;unbalanced_secondary_delta;hub3_secondary_ignition | 0.0;0.333333;0.333333;0.0;0.333333 |
| CL09 | impact_tested_v0_7 | avg_latency;avg_wrong_monitoring;avg_hidden_collapse;avg_blind_no_trigger;avg_topology_false_stability;max_wrong_window | 46.666667;46.666667;0.244444;0.0;0.0;65 |
| CL10 | graded_stress_measured_v0_7 | resource_exhaustion_rate_all_runs;stress_exhaustion_rate;pressure_exhaustion_rate;avg_stress_floor_steps;avg_routing_delay_loss | 0.470115;1.0;1.0;100.273333;0.004152 |

## Main Findings

1. CL09 impact coupling is now tested. Wrong-monitoring remains large (avg 46.67, max 65), and hidden-collapse overlap is no longer zero (avg 0.244 steps across all topology stress rows). Blind/no-trigger topology false stability remains 0, so the honest conclusion is: stale topology can overlap with hidden collapse, but the tested trigger set still prevents fully blind false stability.

2. CL05 hub completeness improved. `hub_2_unbalanced_secondary_failure` was added. At mid stress, primary unbalanced failure strongly separates 2 hubs from 3 hubs; secondary unbalanced failure does not separate them. Three hubs remain context-dependent mitigation, not mesh equivalence.

3. CL10 now has a severity gradient mostly in resource-floor duration and routing delay, not in exhaustion incidence. All graded pressure scenarios still eventually exhaust, but mild and mid pressure shorten floor duration relative to harsh/routing scenarios.

4. CL02 regression survives, but the adversarial stability-term ablation fails. With `psi_s_weight_scale = 0.0`, ablation on-time TPR is 0.0 and average lead is -4.1, showing the v0.5/v0.6 detector depends materially on the stability term. This is useful adversarial evidence, not a source-hierarchy violation.

## Validation Snapshot

- Min break-condition margin: 0.006735.
- Max `k_D_effective`: 0.130000.
- Max `k_C_effective`: 0.100000.
- Federation C04 Trigger A violations: 0.
- Non-federation C07 Trigger A sources: 0.
- Max federation `psi_term_regime`: 0.000000.

## Reviewer Focus

Ask reviewers to attack:

1. Whether CL09 can now be described as impact-tested rather than merely wrong-monitoring-tested.
2. Whether the zero blind/no-trigger result is genuine robustness or still a metric limitation.
3. Whether the failed stability-term ablation should become a required detector-design caveat.
4. Whether CL10 needs another pass because exhaustion incidence is still 100% in graded pressure scenarios.
5. Whether the simulation program is ready to pivot from more batches to paper-evidence consolidation plus container-test planning.
