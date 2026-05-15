# SOE Grand Simulation v0.6 Multi-AI Review Prompt

You are reviewing the SOE Grand Simulation v0.6 focused stress batch.

Source hierarchy and locked constraints remain unchanged:
- C07 v2.2 is source of truth for federation Trigger A / Psi_extended.
- C04 S-threshold is allowed for non-federation Trigger A.
- C02 v2.1 is source of truth for T-G loop break condition.
- C05 v2.1 is source of truth for H/I/A node classes.
- `f_min = 0.30` and `kappa_min = 0.25` remain distinct.
- Interpret results as simulation evidence only, not deployment-ready proof.

v0.6 purpose:
- Keep v0.5 CL02 as a regression check.
- Add CL09 topology lag/misclassification stress into the main matrix.
- Add CL05 integrated unbalanced hub scenarios.
- Add CL10 harsher resource-budget/routing-delay stress.

Key v0.6 outputs:
- `grand_sim_v0_6_traceability.csv`
- `grand_sim_v0_6_focus_summary.csv`
- `grand_sim_v0_6_topology_lag_summary.csv`
- `grand_sim_v0_6_unbalanced_hub_summary.csv`
- `grand_sim_v0_6_resource_stress_summary.csv`
- `grand_sim_v0_6_validation_summary.csv`
- `SOE_Grand_Simulation_v0_6_Findings.md`
- `soe_grand_sim_v0_6.py`

Main question:
Does v0.6 validly translate the review consensus into focused stress evidence for CL09, CL05, and CL10 while preserving CL02 as a regression check?

Requested output:
1. Pass / pass with caveats / block.
2. Top 5 findings, ordered by severity.
3. Any direct source-hierarchy contradiction.
4. Whether CL09 should be `supported_in_v0_6_stress`, `measured`, or downgraded because topology false-stability steps stayed 0.
5. Whether CL05 unbalanced hubs fairly test the context-dependent hub claim.
6. Whether CL10 resource stress is too harsh or appropriately harsh.
7. What v0.7 should do next.

Do not reopen v0.5 CL02 unless v0.6 introduces a new contradiction.
