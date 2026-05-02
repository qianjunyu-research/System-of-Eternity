# v1.3 Requested Three Simulations (2026-04-26)

## 1) Trajectory analysis on 20%
- Scenario: `disturbance_high`
- Parameters: `f_min=0.20`, `alpha_gov=0.10`
- Runs/steps: `30 runs`, `150 steps`
- Output: `v13_trajectory_analysis_fmin_020.csv`

## 2) G(t) dynamic verification
- Verified update consistency for governance coupling dynamic using:
  - `k_D(t) = clamp(k_D(t-1) + alpha_gov * (target_t - k_D(t-1)), floor=f_min)`
- Scenario: `disturbance_high`, `f_min=0.20`, `alpha_gov=0.10`
- Result: max absolute verification error = `0.0`
- Output: `v13_g_dynamic_verification.csv`

## 3) Fine sweep from 0.26 to 0.32
- Scenario: `disturbance_high`
- Sweep: `f_min ∈ {0.26, 0.27, 0.28, 0.29, 0.30, 0.31, 0.32}`
- Fixed: `alpha_gov=0.10`
- Runs/steps: `30 runs`, `150 steps`
- Outputs:
  - `v13_fine_sweep_026_032_summary.csv`
  - `v13_fine_sweep_026_032_runs.csv`
