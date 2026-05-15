# SOE Grand Sim v0.4 Reviewer Update Prompt

We are reviewing the SOE Grand Simulation v0.4 diagnostic package.

Do not debate SOE as a whole. Audit whether v0.4 correctly addresses the v0.3 CL02 circularity concern.

## Context

v0.3 found a Psi calibration path, but Claude/Grok flagged that `psi_score` included `collapse_share` through `regime_weight(collapse_share)`, while the event definition was also `collapse_share >= 0.30`.

v0.4 tests whether the detector still works if the collapse-derived regime term is removed.

## Source Hierarchy

- Federation Trigger A: C07 `Psi_extended` only.
- Non-federation Trigger A: C04 S-threshold allowed.
- `f_min = 0.30` and `kappa_min = 0.25` are distinct.
- Deployment readiness remains blocked.

## v0.4 Files To Inspect First

- `SOE_Grand_Simulation_v0_4_Diagnostic_Report.md`
- `soe_grand_sim_v0_4.py`
- `grand_sim_v0_4/grand_sim_v0_4_psi_ablation_summary.csv`
- `grand_sim_v0_4/grand_sim_v0_4_psi_ablation_by_scenario.csv`
- `grand_sim_v0_4/grand_sim_v0_4_psi_contribution_samples.csv`

Raw optional file:

- `grand_sim_v0_4/grand_sim_v0_4_psi_ablation_runs.csv`

## v0.4 Claims

1. The strict `w_r = 0.0` no-regime ablation still passes at `psi_threshold = 0.30` for `stability_heavy`.
2. The original v0.3 circularity concern is not fatal in this focused diagnostic.
3. CL02 should move to: `precursor independence supported in focused diagnostic; main-matrix transfer pending`.
4. The lower threshold `0.22` with `v02_default`, `w_r = 0.0` is a max-lead exploratory candidate, not the conservative transfer recommendation.

## Requested Output

Return:

1. Top 5 findings, ordered by severity.
2. Whether the ablation design fairly tests the circularity concern.
3. Whether `no_regime_ablation / stability_heavy / threshold 0.30` is acceptable as conservative transfer candidate.
4. Whether the `0.22` max-lead candidate should be rejected, deferred, or explored further.
5. What must be fixed before the main-matrix transfer rerun.

Use strict wording:

- Do not say CL02 is final.
- Do say: `precursor independence supported in focused diagnostic; main-matrix transfer pending`.
- Do not upgrade to deployment-ready.
