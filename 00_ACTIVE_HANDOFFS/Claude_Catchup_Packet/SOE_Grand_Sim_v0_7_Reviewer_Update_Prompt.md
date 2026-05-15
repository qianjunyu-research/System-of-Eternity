# SOE Grand Simulation v0.7 Multi-AI Review Prompt

You are reviewing the SOE Grand Simulation v0.7 focused closure batch.

Do not reopen v0.5/v0.6 unless v0.7 introduces a new contradiction.

Locked constraints:
- Federation Trigger A = C07 `Psi_extended` only.
- Non-federation Trigger A = C04 S-threshold allowed.
- `psi_lambda = 0.10`.
- Default federation `psi_threshold = 0.30`.
- Default federation Psi profile = `stability_heavy_no_regime`.
- `psi_w_regime = 0.0`.
- `f_min = 0.30` and `kappa_min = 0.25` remain distinct.
- Simulation evidence only; no deployment/container readiness claim.

v0.7 purpose:
1. CL09 impact coupling: test whether wrong topology monitoring overlaps with hidden collapse or blind false stability.
2. CL05 completeness: add `hub_2_unbalanced_secondary_failure`.
3. CL10 graded resource stress: mild/mid/harsh pressure plus prior harsh stressors.
4. CL02 adversarial check: remove the stability term in one federation ablation scenario.

Main question:
Does v0.7 close the simulation-phase caveats enough to begin paper-evidence consolidation and container-test planning, or is another simulation batch needed first?

Requested output:
1. Pass / pass with caveats / block.
2. Top 5 findings, ordered by severity.
3. Any source-hierarchy contradiction.
4. CL09: is impact tested, or still only measured?
5. CL02A: how serious is the failed stability-term ablation?
6. CL10: does the all-exhaustion result mean the resource gradient is still too harsh?
7. Recommended next phase: v0.8 simulation, paper evidence consolidation, or Node/container v0.1 planning.
