# SOE Grand Sim v0.4 Diagnostic Throw Packet

Use `01_THROW_FIRST` for every AI.

Start with:

1. `SOE_Grand_Sim_v0_4_Reviewer_Update_Prompt.md`
2. `SOE_Grand_Simulation_v0_4_Diagnostic_Report.md`
3. `soe_grand_sim_v0_4.py`
4. `grand_sim_v0_4_psi_ablation_summary.csv`
5. `grand_sim_v0_4_psi_ablation_by_scenario.csv`
6. `grand_sim_v0_4_psi_contribution_samples.csv`

Use `02_RAW_OPTIONAL` only if an AI asks for the full raw sweep rows.

Safe wording:

- CL02: precursor independence supported in focused diagnostic; main-matrix transfer pending.
- Conservative transfer candidate: `no_regime_ablation / stability_heavy / psi_threshold = 0.30`.
- Exploratory max-lead candidate: `no_regime_ablation / v02_default / psi_threshold = 0.22`.
- Deployment readiness remains blocked.
