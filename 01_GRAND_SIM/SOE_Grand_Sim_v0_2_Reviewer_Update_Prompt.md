# SOE Grand Simulation v0.2 Reviewer Update Prompt

Use this after reviewers have already seen the v0.1 packet.

## Situation

Claude/GPT/Grok/Copilot reviews of v0.1 converged on four major issues:

1. The 2-hub / 3-hub anomaly was suspicious because v0.1 stressed all hubs simultaneously at the same high disturbance floor.
2. `false_stability` did not actually test async stale-state hidden collapse.
3. Per-hub stability was not logged, making worst-hub vs average-hub failure hard to distinguish.
4. CL08 should not be treated as a normal inconclusive result when the metric was mis-specified.

Codex created v0.2 as an audit-response batch. v0.1 is preserved as baseline evidence.

## What Changed In v0.2

Files:

- `soe_grand_sim_v0_2.py`
- `SOE_Grand_Simulation_v0_2_Audit_Response.md`
- `grand_sim_v0_2/grand_sim_v0_2_report.md`
- `grand_sim_v0_2/grand_sim_v0_2_traceability.csv`
- `grand_sim_v0_2/grand_sim_v0_2_scenario_summary.csv`
- `grand_sim_v0_2/grand_sim_v0_2_runs.csv`
- `grand_sim_v0_2/grand_sim_v0_2_steps.csv`

Changes:

- Added `hub_2_single_hub_failure`.
- Added `hub_3_single_hub_failure`.
- Preserved original all-hub stress scenarios.
- Added `detected_collapse_share`.
- Added `async_false_stability`.
- Added per-hub stability columns: `hub1_S`, `hub2_S`, `hub3_S`, `hub_min_S`, `hub_avg_S`, plus run-level min/final hub columns.
- CL05 now reports `context_dependent`.
- CL08 now uses async-specific detected-vs-actual collapse gap.

## v0.2 Batch

- `14 scenarios x 3 profiles x 10 seeds = 420 runs`
- `160 steps/run = 67,200 step rows`

Validation:

- Coupling ceilings held.
- All C02 break margins positive.
- Federation C04 Trigger A violations: `0`.

## Key v0.2 Result

Mid-stress hub results:

| Scenario | Ignition rate | Avg peak collapse |
|---|---:|---:|
| `hub_2_balanced` all-hub stress | 1.0 | 1.0 |
| `hub_3_balanced` all-hub stress | 1.0 | 0.998333 |
| `hub_2_single_hub_failure` | 1.0 | 0.5 |
| `hub_3_single_hub_failure` | 0.0 | 0.116667 |

Interpretation:

Three hubs are a minimum tested mitigation under single-hub failure and v18-style assumptions, not a general repair guarantee under simultaneous all-hub integrated stress.

## What Reviewers Should Do Now

Do not repeat only the v0.1 review. Audit the v0.2 delta:

1. Did v0.2 fairly answer the simultaneous-hub-stress critique?
2. Is the new single-hub-failure comparison actually fair to v18?
3. Is `async_false_stability` now a valid CL08 metric?
4. Does CL05's `context_dependent` status avoid overclaiming?
5. Does CL02 still require a Psi threshold sweep before any federation detector claim can be upgraded?

Return:

1. Which v0.1 criticisms are resolved.
2. Which v0.1 criticisms remain unresolved.
3. Any new v0.2 implementation bugs.
4. Whether v0.2 is a valid audit-response batch.
5. What v0.3 should do next.
