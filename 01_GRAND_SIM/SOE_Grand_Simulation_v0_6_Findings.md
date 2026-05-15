# SOE Grand Simulation v0.6 Findings

## Executive Verdict

v0.6 ran successfully as a focused stress batch over the frozen v0.5 main matrix.

- Runs: 630.
- Step rows: 100,800.
- Scenarios: 21.
- Profiles: 3.
- Interpretation boundary: simulation evidence only, not deployment-ready evidence.

## Claim Status

| Claim | Status | Metric | Value |
|---|---|---|---:|
| CL02 | supported_in_v0_6_regression | on_time_tpr;false_positive_rate;avg_lead_to_collapse30 | 1.0;0.0;7.8625 |
| CL05 | context_dependent_unbalanced_tested | all_hub_delta;single_hub_delta;unbalanced_primary_delta;hub3_secondary_ignition | 0.0;0.333333;0.3;0.333333 |
| CL09 | supported_in_v0_6_stress | avg_latency;avg_wrong_monitoring_steps;avg_topology_false_stability_steps;max_wrong_monitoring_window | 46.666667;46.666667;0.0;65 |
| CL10 | stress_measured_v0_6 | resource_exhaustion_rate_all_runs;stress_exhaustion_rate;avg_stress_floor_steps;avg_routing_delay_loss | 0.41746;1.0;112.583333;0.005169 |

## Main Findings

1. CL09 is no longer a zero-latency placeholder. The topology stress scenarios produce average wrong-monitoring windows of 25, 50, and 65 steps depending on drift/lag/misclassification mode. This validates the reviewer concern that stale topology maps can persist inside the integrated matrix.

2. CL05 remains context-dependent, now with unbalanced hub evidence. At mid stress, `hub_3_unbalanced_primary_failure` has sustained ignition rate 0.1 versus 1.0 for `hub_2_unbalanced_primary_failure`, but high stress still breaks the 3-hub unbalanced variants. The correct claim is mitigation under bounded/localized assumptions, not repair or mesh equivalence.

3. CL10 is now materially stressed. The two new resource scenarios hit resource exhaustion in 100% of runs, with long resource-floor durations and measurable routing-delay loss in `resource_routing_delay`.

4. CL02 survived as a regression check. The federation detector still reports on-time TPR 1.0, false-positive rate 0.0, and average lead 7.8625 under the expanded v0.6 batch.

## Validation Snapshot

- Min break-condition margin: 0.006735.
- Max `k_D_effective`: 0.130000.
- Max `k_C_effective`: 0.100000.
- Federation C04 Trigger A violations: 0.
- Non-federation C07 Trigger A sources: 0.
- Max federation `psi_term_regime`: 0.000000.

## Reviewer Focus

Ask reviewers to attack:

1. Whether CL09 should be marked `supported_in_v0_6_stress` or merely `measured_with_wrong_monitoring` because topology false-stability steps stayed at 0.
2. Whether the CL05 unbalanced scenarios fairly represent v18-style configs D/E.
3. Whether CL10 resource stress is too harsh, or appropriately harsh for a stress batch.
4. Whether CL02 regression should keep the v0.5 wording unchanged.
