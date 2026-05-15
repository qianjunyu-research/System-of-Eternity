# SOE Grand Sim v0.5 Reviewer Update Prompt

We are reviewing the SOE Grand Simulation v0.5 main-matrix transfer run.

Do not debate SOE as a whole. Audit whether the v0.4 no-regime CL02 detector transfers into the integrated main matrix.

## Context

v0.4 established:

- conservative transfer candidate: `no_regime_ablation / stability_heavy / psi_threshold = 0.30`
- `psi_lambda = 0.10`
- `w_r = 0.0`
- exclude `regime_heavy`
- defer `v02_default / 0.22`

v0.5 applies that candidate inside the main integrated matrix.

## Files To Inspect First

- `SOE_Grand_Simulation_v0_5_Transfer_Report.md`
- `soe_grand_sim_v0_5.py`
- `grand_sim_v0_5_traceability.csv`
- `grand_sim_v0_5_federation_transfer_summary.csv`
- `grand_sim_v0_5_validation_summary.csv`
- `grand_sim_v0_5_scenario_summary.csv`

Raw optional:

- `grand_sim_v0_5_runs.csv`
- `grand_sim_v0_5_steps.csv`

## v0.5 Claims

1. Federation Trigger A uses the no-regime `stability_heavy` detector.
2. Federation `psi_w_regime = 0.0`.
3. CL02 has on-time TPR `1.0`, false-positive rate `0.0`, and avg lead `7.9875` steps across federation transfer scenarios.
4. CL02 status can move to `supported_in_v0_5_transfer`.
5. Deployment readiness remains blocked.

## Requested Output

Return:

1. Top 5 findings, ordered by severity.
2. Any direct contradiction with the source hierarchy.
3. Whether CL02 is validly supported in the v0.5 main-matrix transfer run.
4. What must be fixed before the next batch.
5. Any files needed from QianJun.

Strict wording:

- Do say: `CL02 supported in v0.5 main-matrix transfer`.
- Do not say: deployment-ready.
- Do not revive `regime_heavy` or the `0.22` max-lead candidate as defaults.
