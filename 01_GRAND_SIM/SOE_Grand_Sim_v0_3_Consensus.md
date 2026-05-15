# SOE Grand Sim v0.3 Multi-AI Consensus

Date: 2026-05-08

Input artifact: `C:\Users\M7120\Desktop\New Microsoft Word Document.docx`

Extracted text: `SOE_Grand_Sim_v0_3_Multi_AI_Review_extracted.txt`

Reviewers represented: Grok, ChatGPT, Claude, Le Chat, Gemini, Copilot.

## Executive Verdict

v0.3 is a valid focused calibration/reproduction package. It should not be treated as a full integrated C00-C08 rerun, architecture-final evidence, or deployment-ready evidence.

The strict consensus wording is:

- CL02: calibration path found at locked `psi_lambda = 0.10`, candidate `psi_threshold = 0.30`; precursor independence is not established because the v0.3 `psi_score` includes `collapse_share` through `regime_weight`.
- CL09: stress-tested; delayed/misclassified topology observation can create long wrong-monitoring windows.
- CL05: context-dependent hub mitigation validated; three hubs survive v18 standalone dynamics and v0.2 single-hub failure, but not v0.2 integrated all-hub stress.

Where reviewers disagree, this consensus follows the more conservative Claude/Copilot/ChatGPT wording over Le Chat/Gemini's stronger "resolved/conclusive" language.

## Consensus By Claim

| Claim | v0.2 status | v0.3 consensus | Evidence | Remaining gate |
|---|---|---|---|---|
| CL02 Psi federation detector | inconclusive | calibration path found, independence not established | accepted locked-lambda candidates at `psi_lambda = 0.10`, threshold `0.30`; top candidate TPR `1.0`, on-time TPR `1.0`, FP `0.0`; `psi_score` includes `regime_weight(collapse_share)` | ablate/remove regime term or decompose contributions before main-matrix claim upgrade |
| CL09 topology lag | measured but not stress-tested | stress-tested | worst summary row has `52.0` avg wrong-monitoring steps and `27.0` avg star-undetected steps | integrate lag/misclassification into main matrix |
| CL05 hub mitigation | context-dependent | context-dependent validated | v18 2 hubs fail / 3 hubs survive; v0.2 integrated all-hub 3 hubs fail | add integrated unbalanced hub scenarios |

## Top Findings

1. **CL02 is promising but not closed.** The v0.3 event-conditioned TP/FP/FN sweep fixes the blunt v0.2 run-rate metric. However, the perfect score is inflated by a confirmed circularity risk: `psi_score` uses `collapse_share` through `regime_weight`, while the event boundary is also `collapse_share >= 0.30`.

2. **The Psi candidate should not be transferred as final before ablation.** The correct language is "calibration path found; precursor independence not established," not "supported in the grand sim." v0.4 should first test `w_r = 0.0` or log term contributions at detection time, then patch/rerun the main matrix if the independent terms still perform.

3. **CL09 now has real stress evidence.** The topology lag suite shows wrong-monitoring windows, with raw-run distribution checks showing median `20.0`, p75 `40.0`, p95 `45.0`, and max `75.0` wrong-monitoring steps across 360 lag runs.

4. **The worst CL09 case misses centralization entirely.** Under recheck interval `10`, detection delay `20`, and misclassification `0.25`, `centralizing_detection_rate = 0.0`. This should be a named risk because transitional monitoring never activates.

5. **Hub mitigation remains context-bound.** v18 standalone reproduces the clean 2-hub/3-hub boundary, while v0.2 integrated all-hub stress still defeats 3 hubs. v0.4 should add integrated unbalanced hub cases before calling the comparison complete.

6. **No direct source-hierarchy contradiction was found.** Federation Trigger A remains C07 `Psi_extended`; non-federation C04 S-threshold remains allowed; `f_min = 0.30` and `kappa_min = 0.25` remain distinct in the v0.2 code path imported by v0.3.

## Reviewer-Specific Notes

| Reviewer | Useful signal | Consensus handling |
|---|---|---|
| Grok | warned against CL02 overclaim and transfer failure | accepted |
| ChatGPT | correctly framed v0.3 as calibration-level evidence | accepted |
| Claude | confirmed circular-signal risk from `regime_weight(collapse_share)`, plus centralizing miss, unbalanced hub gap, and report wording issue | accepted as primary audit caveats |
| Le Chat | confirmed source hierarchy and v0.4 implementation direction | accepted, but "resolved" wording downgraded |
| Gemini | verified topology/math direction and role compliance | accepted, but "conclusive/frozen" wording downgraded |
| Copilot | requested raw-run checks, traceability checks, and transfer validation | accepted |

## v0.4 Go/No-Go

Go for v0.4 diagnostic implementation, but not for claim finalization.

v0.4 must be framed as a diagnostic transfer/validation run:

1. Add a CL02 ablation sweep with `w_r = 0.0` and/or a contribution decomposition that logs each Psi term at `detect_step`.
2. Only after the ablation passes, patch federation Trigger A threshold to `0.30` with locked `psi_lambda = 0.10` and rerun the main matrix.
3. Add topology detection lag/misclassification to the main matrix and update CL09 traceability.
4. Add integrated unbalanced hub scenarios matching v18 configs D/E where possible.
5. Add harsher resource-budget contention/routing-delay stress for CL10.
6. Produce automated traceability checks for required run/step columns and claim-to-output mapping.

Deployment readiness remains blocked.
