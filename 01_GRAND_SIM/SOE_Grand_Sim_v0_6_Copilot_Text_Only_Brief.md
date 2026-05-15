# SOE Grand Simulation v0.6 - Copilot Text-Only Brief

You are reviewing the SOE Grand Simulation v0.6 focused stress batch.

Context:
- v0.5 CL02 was closed as `supported_in_v0_5_transfer`.
- v0.6 keeps CL02 as a regression check and focuses on CL09, CL05, and CL10.
- Treat this as simulation evidence only, not deployment-ready evidence.

Batch:
- 21 scenarios x 3 profiles x 10 seeds = 630 runs.
- 100,800 step rows.
- Script: `soe_grand_sim_v0_6.py`.

Locked constraints:
- Federation Trigger A = C07 `Psi_extended` only.
- Non-federation Trigger A = C04 S-threshold allowed.
- `psi_lambda = 0.10`.
- Federation `psi_threshold = 0.30`.
- Federation Psi profile = `stability_heavy_no_regime`.
- `psi_w_regime = 0.0`.
- `f_min = 0.30` and `kappa_min = 0.25` remain distinct.

Validation:
- Run rows: 630.
- Step rows: 100,800.
- Min break-condition margin: 0.006735.
- Max `k_D_effective`: 0.13.
- Max `k_C_effective`: 0.10.
- Federation C04 Trigger A violations: 0.
- Non-federation C07 Psi Trigger A sources: 0.
- Max federation `psi_term_regime`: 0.0.
- Federation positive event rows: 80.
- Federation on-time detections: 80 / 80.
- Federation false positives: 0.

Traceability:
- CL02 regression: `supported_in_v0_6_regression`.
  - Metric: `on_time_tpr;false_positive_rate;avg_lead_to_collapse30`.
  - Value: `1.0;0.0;7.8625`.

- CL09 topology lag: `supported_in_v0_6_stress`.
  - Metric: `avg_latency;avg_wrong_monitoring_steps;avg_topology_false_stability_steps;max_wrong_monitoring_window`.
  - Value: `46.666667;46.666667;0.0;65`.
  - Important caveat: wrong-monitoring windows are confirmed, but topology false-stability steps stayed 0. Audit whether status should be supported or only measured.

- CL05 unbalanced hubs: `context_dependent_unbalanced_tested`.
  - Metric: `all_hub_delta;single_hub_delta;unbalanced_primary_delta;hub3_secondary_ignition`.
  - Value: `0.0;0.333333;0.3;0.333333`.
  - Interpretation: three hubs still mitigate bounded/localized and some unbalanced conditions, but not all-hub/high-stress failure. Do not call three hubs a repair or mesh equivalent.

- CL10 resource stress: `stress_measured_v0_6`.
  - Metric: `resource_exhaustion_rate_all_runs;stress_exhaustion_rate;avg_stress_floor_steps;avg_routing_delay_loss`.
  - Value: `0.41746;1.0;112.583333;0.005169`.
  - Interpretation: the new resource stress scenarios force 100% exhaustion and measurable routing-delay loss. Audit whether the stress is appropriately harsh or too harsh.

Requested review:
1. Pass / pass with caveats / block.
2. Top 5 findings, ordered by severity.
3. Any source-hierarchy contradiction.
4. Should CL09 stay `supported_in_v0_6_stress`, or be downgraded because topology false-stability steps are 0?
5. Are CL05 unbalanced hub scenarios fair?
6. Is CL10 resource stress too harsh or useful?
7. What should v0.7 do next?

Do not reopen v0.5 CL02 unless v0.6 introduces a new contradiction.
