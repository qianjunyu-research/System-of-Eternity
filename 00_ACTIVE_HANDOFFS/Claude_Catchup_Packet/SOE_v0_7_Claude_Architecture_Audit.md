# SOE v0.7 Claude Architecture Audit

Status: architecture-auditor review received after prior data-use limit.

## Verdict

Pass. Simulation phase can close. Pivot to paper-evidence consolidation.

## Top Findings

1. CL02A stability-term ablation failure is important for the paper, not a blocker.
   - With `psi_w_s = 0.0`, on-time TPR drops to `0.0` at low/mid stress and detection only occurs late at high stress.
   - `Psi_extended` should be described as primarily a stability-precursor detector.
   - Required paper caveat: if `S_network` is compromised or gamed without affecting collapse dynamics, the detector can fail.

2. CL09 hidden-collapse overlap is confirmed but narrow.
   - Hidden-collapse overlap appears in several topology lag/misclassification conditions.
   - Blind false stability appears in one tested condition: `topology_lag_resource_cascade / low`, about `4.9` steps.
   - Honest wording: topology lag can overlap with hidden collapse; in one tested condition it produced a brief false-stability window.

3. CL05 is complete enough for paper evidence.
   - Balanced single-hub failure separates 2-hub from 3-hub.
   - Unbalanced primary failure separates 2-hub from 3-hub.
   - Unbalanced secondary failure does not separate 2-hub from 3-hub because both survive at mid stress.
   - Status remains context-dependent mitigation.

4. CL10 graded resource stress is paper-ready as stress evidence.
   - Exhaustion incidence remains 100 percent in pressure scenarios.
   - The meaningful gradient is in floor duration and routing-delay loss.
   - No additional pass required.

5. CL02 regression is clean.
   - Average lead is `8.175`.
   - Drift from v0.6 is treated as seed noise from the expanded batch.

## Source Hierarchy

No source-hierarchy contradictions found.

## Terminal Claim Status

| Claim | Terminal Status |
|---|---|
| CL01 | supported |
| CL02 | supported_in_v0_7_regression |
| CL03 | supported |
| CL04 | supported |
| CL05 | context_dependent_unbalanced_tested |
| CL06 | measured |
| CL07 | supported |
| CL08 | supported |
| CL09 | impact_tested_v0_7 |
| CL10 | graded_stress_measured_v0_7 |

## Recommendation

Close the simulation phase and begin paper-evidence consolidation.

CL06 is the only remaining measured-only claim, but it is not architecturally critical enough to justify another simulation batch. Treat it as future work.

Node v0.1 remains a bounded planning/audit packet and must not be described as deployment-ready.
