# SOE Grand Sim Review Corrections v0.2

Date: 2026-05-08

Purpose: consolidate Le Chat / Gemini review comments against the actual v0.1/v0.2 implementation and source hierarchy.

## Executive Correction

Some review findings are useful, but two high-severity claims are based on misread context:

1. C04 S-threshold is **not banned for all Trigger A**.
2. `break_condition_margin` **was already logged** in v0.1 run rows.

The architecture rule is topology-conditioned:

| Topology | Trigger A source |
|---|---|
| Federation | C07 `Psi_extended`; C04 S-threshold not applicable. |
| Ring / mesh | C04 S-threshold applicable; Psi_base secondary. |
| Star | C04 minimum-node S-threshold applicable; Psi_base secondary. |
| Unknown | C04 conservative minimum-node S-threshold + Psi_base. |

Therefore the proposed fix "remove S_THRESHOLD dependency for all Trigger A" is incorrect and would violate C04/C07 source hierarchy.

## Accepted Findings

| Finding | Status | Response |
|---|---|---|
| v0.1 all-hub stress made the 2-hub/3-hub comparison unfair against v18. | Accepted. | v0.2 added `hub_2_single_hub_failure` and `hub_3_single_hub_failure`. |
| v0.1 async false-stability metric was weak/mis-specified. | Accepted. | v0.2 added `detected_collapse_share` and `async_false_stability`. |
| v0.1 topology drift latency was too clean. | Partly accepted. | v0.2 still measures it, but v0.3 should add delayed/misclassified topology detection. |
| Psi thresholding remains inconclusive. | Accepted. | v0.3 should be a dedicated Psi threshold/weights sweep. |
| Need v18 reproduction inside grand sim. | Accepted. | v0.3 should add a v18-reproduction harness before any stronger hub claim. |

## Rejected Or Corrected Findings

| Claim | Correction |
|---|---|
| "Non-federation S_THRESHOLD use is an architecture breach." | Incorrect. C04 S-threshold is supposed to be used for non-federation topologies. Only federation delegates Trigger A to C07 `Psi_extended`. |
| "CL01 is violated because non-federation uses C04 S-threshold." | Incorrect. CL01 is specifically federation C04 non-applicability. v0.1 and v0.2 both had zero federation C04 Trigger A violations. |
| "`break_condition_margin` is not logged in `runs.csv`." | Incorrect. v0.1 and v0.2 run CSVs include `break_condition_margin`; validation found all margins positive. |
| "S05/S06 comparison logic missing means CL05 invalid." | Overstated. v0.1 traceability computed aggregate hub2-minus-hub3 ignition rate. v0.2 improves this with single-hub and all-hub deltas. |
| "`f_min=0.30` and `kappa_min=0.25` may be sequentially stacked." | Not observed. v0.1/v0.2 log `kappa_min_protected` as metadata and use `f_min=0.30` as the C02/C03 floor. They are not stacked in the code. |

## v0.2 Status After Audit Response

Batch:

- `420` runs.
- `67,200` step rows.
- Coupling ceilings held.
- All C02 break-condition margins positive.
- Federation C04 Trigger A violations: `0`.

Traceability:

| Claim | v0.2 status |
|---|---|
| CL01 federation C04 Trigger A non-applicability | supported |
| CL02 Psi_extended federation detector | inconclusive |
| CL03 T-G loop / Trigger B behavior | supported |
| CL04 star topology unsafe | supported |
| CL05 2-hub / 3-hub mitigation | context_dependent |
| CL06 H/I/A identity behavior | measured |
| CL07 formal governance masking ineffective governance | supported |
| CL08 async/message-loss hidden collapse | supported |
| CL09 topology reclassification | measured |
| CL10 finite-resource recovery constraint | measured |

Hub clarification:

| Scenario | Mid-stress ignition rate | Interpretation |
|---|---:|---|
| `hub_2_balanced` all-hub stress | 1.0 | All-hub integrated stress overwhelms two hubs. |
| `hub_3_balanced` all-hub stress | 1.0 | All-hub integrated stress also overwhelms three hubs. |
| `hub_2_single_hub_failure` | 1.0 | Two hubs fail under single-hub failure at mid stress. |
| `hub_3_single_hub_failure` | 0.0 | Three hubs survive single-hub failure at mid stress. |

Correct wording:

> Three hubs are a minimum tested mitigation under standalone v18 hub-redundancy dynamics and under v0.2 single-hub failure, not a general repair guarantee under integrated all-hub stress.

## What To Send Back To Le Chat / Gemini

Please re-audit against v0.2 and correct the Trigger A interpretation:

- Federation Trigger A: C07 `Psi_extended` only.
- Non-federation Trigger A: C04 S-threshold is allowed and expected.
- Do not request removal of S-threshold globally.
- Check v0.2 files, not only v0.1:
  - `SOE_Grand_Sim_v0_2_Reviewer_Update_Prompt.md`
  - `SOE_Grand_Simulation_v0_2_Audit_Response.md`
  - `soe_grand_sim_v0_2.py`
  - `grand_sim_v0_2_report.md`
  - `grand_sim_v0_2_traceability.csv`
  - `grand_sim_v0_2_scenario_summary.csv`

## v0.3 Priority

The next simulation should not be another broad matrix. It should be a focused calibration/reproduction package:

1. Psi threshold/weights sweep for federation.
2. v18 reproduction harness inside the grand-sim code path.
3. Topology detection lag and misclassification stress.
4. Resource exhaustion stress with routing delay and budget contention.
