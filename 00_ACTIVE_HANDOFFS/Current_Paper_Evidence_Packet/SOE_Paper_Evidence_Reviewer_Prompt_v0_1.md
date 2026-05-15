# SOE Paper Evidence Reviewer Prompt v0.1

You are reviewing the SOE paper-evidence consolidation packet after Grand Simulation v0.7.

## Review Goal

Do not ask for another simulation batch unless you find a source-hierarchy contradiction, reproducibility failure, or a material overclaim that cannot be fixed by wording. The default next phase is paper-evidence consolidation.

## Source Hierarchy

- C07 v2.2: federation Trigger A uses `Psi_extended`.
- C04 v2.3: non-federation Trigger A may use S-threshold.
- C02 v2.1: break-condition margins must remain positive.
- C05 v2.1: H/I/A node classes remain distinct.
- `f_min = 0.30` and `kappa_min = 0.25` remain distinct.

## Evidence Base

- v0.7 Grand Simulation closure batch.
- 870 runs.
- 139,200 step rows.
- 29 scenarios.
- 3 profiles.
- Validation checks passed.
- Claude architecture audit says: simulation phase can close; pivot to paper-evidence consolidation.

## Files To Review

Primary:

- `SOE_Paper_Evidence_Consolidation_v0_1.md`
- `SOE_Paper_Results_Insert_v0_1.md`
- `SOE_Paper_Methods_Reproducibility_v0_1.md`
- `SOE_Paper_Claim_Status_Table_v0_1.csv`
- `SOE_Paper_Limitations_And_Claims_Control_v0_1.md`

Evidence:

- `SOE_Grand_Simulation_v0_7_Findings.md`
- `SOE_v0_7_Claude_Architecture_Audit.md`
- `grand_sim_v0_7_traceability.csv`
- `grand_sim_v0_7_validation_summary.csv`
- `grand_sim_v0_7_focus_summary.csv`
- `grand_sim_v0_7_psi_adversarial_summary.csv`
- `grand_sim_v0_7_topology_impact_summary.csv`
- `grand_sim_v0_7_hub_completeness_summary.csv`
- `grand_sim_v0_7_resource_gradient_summary.csv`
- `grand_sim_v0_7_hashes.csv`

## Reviewer Tasks

1. Check whether each paper claim is supported by the stated v0.7 output columns.
2. Check whether CL02A is disclosed as a required caveat.
3. Check whether CL09 wording stays narrow.
4. Check whether CL05 avoids "three hubs safe" overclaiming.
5. Check whether CL10 avoids implying resource recovery is proven.
6. Check whether CL06 remains measured/future-work.
7. Check whether any wording implies deployment readiness.
8. Check whether another simulation batch is truly necessary or whether wording fixes are enough.

## Requested Output

1. Pass / pass with caveats / block.
2. Top 5 overclaim risks, ordered by severity.
3. Any source-hierarchy contradiction.
4. Any missing traceability link.
5. Specific wording changes needed before the paper.
6. Whether the simulation phase can remain closed.

Use this decision rule:

```text
If the evidence is sufficient but wording overclaims, recommend wording fixes, not a new batch.
```
