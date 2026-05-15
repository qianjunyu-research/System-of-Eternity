# SOE Grand Simulation v0.2 Audit Response

Date: 2026-05-08

Purpose: respond to Claude/GPT code-level audit of `soe_grand_sim_v0_1.py` without rewriting v0.1 evidence.

## Audit Findings Addressed

| Audit finding | v0.2 response |
|---|---|
| v0.1 stressed all hubs at `D >= 0.78`, making 2-hub and 3-hub comparison unfair against v18. | Added `hub_2_single_hub_failure` and `hub_3_single_hub_failure` scenarios. Original all-hub-stress scenarios are preserved as harsher integrated stress tests. |
| `false_stability` did not measure async stale-state gaps. | Added observer-side `detected_collapse_share`, `async_false_stability`, and `async_false_stability_steps`. CL08 now uses async-specific detected-vs-actual collapse gap. |
| 3-hub topology was not graph-star-like, but min-over-hubs plus all-hub stress created star-like outcome. | Added per-step and per-run hub stability columns: `hub1_S`, `hub2_S`, `hub3_S`, `hub_min_S`, `hub_avg_S`, and min/final hub summary columns. |
| CL08 should not be labeled merely inconclusive with a mis-specified metric. | CL08 now uses the corrected metric and reports `supported` only if async-specific hidden collapse occurs; otherwise `not_supported_in_v0_2`. |

## Batch

`14 scenarios x 3 profiles x 10 seeds = 420 runs`

`160 steps per run = 67,200 step rows`

Outputs:

- `grand_sim_v0_2/grand_sim_v0_2_report.md`
- `grand_sim_v0_2/grand_sim_v0_2_traceability.csv`
- `grand_sim_v0_2/grand_sim_v0_2_scenario_summary.csv`
- `grand_sim_v0_2/grand_sim_v0_2_runs.csv`
- `grand_sim_v0_2/grand_sim_v0_2_steps.csv`

## Validation

- Expected run rows: `420`.
- Expected step rows: `67,200`.
- State variables stayed bounded.
- Coupling ceilings held: `k_D <= 0.15`, `k_C <= 0.10`, `k_T <= 0.20`.
- All C02 break-condition margins were positive.
- Federation had `0` C04 S-threshold Trigger A violations.

## Key v0.2 Results

Traceability statuses:

- CL01 federation C04 Trigger A non-applicability: `supported`.
- CL02 Psi_extended as federation detector: `inconclusive`.
- CL03 T-G loop / Trigger B behavior: `supported`.
- CL04 star topology unsafe: `supported`.
- CL05 2-hub vs 3-hub mitigation: `context_dependent`.
- CL06 H/I/A identity behavior: `measured`.
- CL07 formal governance masking ineffective governance: `supported`.
- CL08 async/message-loss hidden collapse: `supported`.
- CL09 topology reclassification: `measured`.
- CL10 finite-resource recovery constraint: `measured`.

Hub boundary clarification:

| Scenario | Mid-stress ignition rate | Mid-stress avg peak collapse |
|---|---:|---:|
| `hub_2_balanced` | 1.0 | 1.0 |
| `hub_3_balanced` | 1.0 | 0.998333 |
| `hub_2_single_hub_failure` | 1.0 | 0.5 |
| `hub_3_single_hub_failure` | 0.0 | 0.116667 |

Interpretation:

The v0.1 anomaly was partly clarified by stress-mode separation: v0.2 shows that under single-hub failure, three hubs outperform two hubs at mid stress. Under all-hub integrated stress, three hubs still fail. v0.3 later confirmed that v18's standalone hub suite also stresses all hubs but uses simpler dynamics, so the remaining difference is an integration-load delta, not only a stress-mode mismatch. The correct architecture wording is therefore:

> Three hubs are a minimum tested mitigation under standalone v18 hub-redundancy dynamics and under v0.2 single-hub failure, not a general repair guarantee under integrated all-hub stress.

Async clarification:

`async_message_loss` now logs `detected_collapse_share` against actual `collapse_share`. CL08 is supported in v0.2 because the high-stress async family produced nonzero async-specific false-stability steps (`avg_async_false_stability_steps = 0.133333` across all async profiles; high-stress average = `0.4`).

## v0.2 Remaining Open Items

- Psi thresholding remains under-calibrated. CL02 is still inconclusive.
- Governance capture support remains scenario-driven; v0.2 supports detector behavior under forced capture, not real-world capture generality.
- Topology reclassification latency is measured as `0.0` in the current setup because detection updates when the final drift state is reached; v0.3 should test delayed/misclassified topology explicitly.
- Deployment readiness remains blocked.
