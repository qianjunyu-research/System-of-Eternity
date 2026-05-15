# SOE Grand Sim v0.2 Consensus

Date: 2026-05-08

Reviewers: Claude/GPT, Grok/Copilot, Le Chat, Gemini.

## Consensus

v0.2 is a valid audit-response batch. It resolves the major v0.1 implementation/review issues:

- Federation Trigger A uses C07 `Psi_extended`.
- Non-federation Trigger A correctly keeps C04 S-threshold.
- `break_condition_margin` is logged and positive in all runs.
- Hub redundancy is now separated into all-hub stress and single-hub failure.
- CL05 is correctly `context_dependent`.
- Async hidden-collapse measurement now has `detected_collapse_share` and `async_false_stability`.

## Remaining Issues

| Claim | Status | Next action |
|---|---|---|
| CL02 Psi federation detector | Inconclusive / under-calibrated | Run a dedicated Psi threshold and weight sweep with real TP/FP/FN metrics. |
| CL09 topology drift latency | Measured but not stress-tested | Add delayed/misclassified topology detection and quantify wrong-monitoring windows. |
| v18 hub boundary | Context-dependent | Add v18 reproduction harness in the grand-sim review path. |
| Resource limits | Measured | Add harsher budget contention later; not first v0.3 priority. |

## Important Metric Correction

The v0.2 CL02 metric `federation_psi_detector_run_rate` is too blunt because it counts any federation run without Trigger A as detector failure, including no-event runs where Trigger A should not fire.

v0.3 should compute:

- positive event runs: local federation collapse or cluster-contained collapse occurred.
- negative event runs: no local/systemic collapse occurred.
- true positive rate.
- on-time true positive rate.
- missed detection rate.
- false positive rate.
- average lead/lag steps.

This is the correct way to decide whether `Psi_extended` is under-calibrated.

## v0.3 Scope

Do not run another broad C00-C08 matrix. Run a focused package:

1. Psi threshold/weights sweep for federation.
2. Topology detection lag/misclassification stress test.
3. v18 hub-redundancy reproduction comparison.

Deployment readiness remains blocked.
