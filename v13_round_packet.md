# v1.3 Blocking Diagnostic Packet (2026-04-26)

## Corrected Parameter Mapping
- `f_min` is the **governance coupling floor** (`governance_coupling_floor`) for damped disturbance coupling `k_D`, **not** `disturbance_baseline`.
- `α_gov` is the coupling update rate (`governance_coupling_alpha`) in:
  - `k_D(t+1) = k_D(t) + α_gov × (f(G(t)) - k_D(t))`, clamped with floor `f_min`.

## Requested Joint Grid (disturbance_high)
- `f_min`: 0.05, 0.10, 0.15, 0.20, 0.25, 0.30
- `α_gov`: 0.03, 0.05, 0.07, 0.10, 0.15
- Full grid: **30 configurations** (6 × 5), **30 runs each**, **150 steps**.
- `disturbance_high`: `shock_prob=0.15`, `shock_impact=0.48`.

## Command Executed
`python governance_blocking_diagnostic_v13.py --runs 30 --steps 150 --f-min-values 0.05 0.10 0.15 0.20 0.25 0.30 --alpha-gov-values 0.03 0.05 0.07 0.10 0.15 --skip-w-calibration --output v13_blocking_diagnostic_summary.csv --raw-output v13_blocking_diagnostic_runs.csv`

## Output Metrics
- `stable_run_rate`
- `failure_rate`
- `recovered_run_rate`
- `recovery_to_stable_conversion_rate` (new)

## Artifacts
- `v13_blocking_diagnostic_summary.csv`
- `v13_blocking_diagnostic_runs.csv`
- `codex_action_list_v13_joint_blocking.md` (copy/paste action handoff)
