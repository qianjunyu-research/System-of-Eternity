# SOE Grand Sim v0.4 Copilot Partial Review

Date: 2026-05-08

Context: Copilot hit daily attachment limits, so it only reviewed truncated excerpts from:

- `grand_sim_v0_4_psi_ablation_summary.csv`
- `grand_sim_v0_4_psi_contribution_samples.csv`

## Useful Signal

Copilot's partial review confirms the same high-level CSV behavior already captured by the v0.4 consensus:

- Detection performance is threshold-dependent.
- Removing the regime term changes timing and false-positive behavior.
- Contribution samples are useful for checking which terms drive `psi_score`.
- Low thresholds can give earlier warnings but increase sensitivity risk.

## No Consensus Change

This review does not change the current consensus:

- Conservative transfer candidate remains `no_regime_ablation / stability_heavy / psi_threshold = 0.30`.
- `no_regime_ablation / v02_default / psi_threshold = 0.22` remains exploratory because the false-positive boundary is thin.
- `regime_heavy` remains excluded.
- CL02 remains: `precursor independence supported in focused diagnostic; main-matrix transfer pending`.

## Action Taken

Codex generated local aggregation artifacts that do not require Copilot's attach budget:

- `grand_sim_v0_4/grand_sim_v0_4_threshold_curve_table.csv`
- `grand_sim_v0_4/grand_sim_v0_4_ablation_delta_table.csv`
- `grand_sim_v0_4/grand_sim_v0_4_term_breakdown_by_scenario.csv`
- `SOE_Grand_Sim_v0_4_Copilot_Aggregation_Report.md`
