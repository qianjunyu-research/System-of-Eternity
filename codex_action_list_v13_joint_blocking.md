# Codex Action List — v1.3 Blocking Simulation (Copy/Paste)

## Action List (Items #1 and #2 Highlighted)
1. 🔶 **JOINT `f_min × α_gov` diagnostic in `disturbance_high` (this is the blocking simulation for v1.3).**
2. 🔶 **Report the joint-grid outcomes first (stability/failure trends across `f_min` and `α_gov`) before any follow-on calibration.**
3. Keep the run profile aligned with the current v1.3 round settings unless explicitly changed (`30 runs`, `150 steps`).

## Governance Module v1.3 — Corrected `f_min` Constraint Formula
Use the v1.3 mapping `f_min → governance_coupling_floor` (the floor on damped governance coupling `k_D`), separate from `disturbance_baseline`:

`k_D(t+1) = clamp(k_D(t) + α_gov × (f(G(t)) - k_D(t)), low=f_min, high=max_disturbance_damping_effect)`

Where in-code mappings are:
- `f_min := governance_coupling_floor`
- `α_gov := governance_coupling_alpha`
- `disturbance_high := shock_prob=0.15, shock_impact=0.48`

## Execution Command (Joint Diagnostic)
`python governance_blocking_diagnostic_v13.py --runs 30 --steps 150 --f-min-values 0.05 0.10 0.15 0.20 0.25 0.30 --alpha-gov-values 0.03 0.05 0.07 0.10 0.15 --skip-w-calibration --output v13_blocking_diagnostic_summary.csv --raw-output v13_blocking_diagnostic_runs.csv`

Note: `--skip-w-calibration` keeps this run focused on the joint `f_min × α_gov` blocking diagnostic only.
