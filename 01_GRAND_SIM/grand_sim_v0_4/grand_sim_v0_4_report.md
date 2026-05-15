# SOE Grand Simulation v0.4 Diagnostic Report

## Scope

v0.4 is a CL02 diagnostic package. It tests whether the v0.3 Psi calibration survives removal of the collapse-derived regime term.

Tested variants:

- `with_regime_original`: v0.3 scoring, including `w_r * regime_weight(collapse_share)`.
- `no_regime_ablation`: strict `w_r = 0.0`, all other weights unchanged.
- `no_regime_renormalized`: `w_r = 0.0`, non-regime weights rescaled to sum to `1.0`.

## Key Result

- Diagnostic conclusion: `strict_ablation_passed_at_0_30`.
- Original candidate average regime share at detection: `0.048829`.
- Original candidate average collapse share at detection: `0.021875`.
- Conservative transfer candidate: `no_regime_ablation` / `stability_heavy`, `psi_threshold = 0.30`.
- Max-lead exploratory candidate: `no_regime_ablation` / `v02_default`, `psi_threshold = 0.22`.
- Excluded profile: `regime_heavy`; no-regime ablation at threshold `0.30` misses `12.5%` of positive runs and is not a transfer candidate.

| Candidate | threshold | detected TPR | on-time TPR | missed rate | false positive rate | avg lead |
|---|---:|---:|---:|---:|---:|---:|
| `with_regime_original` / `stability_heavy` | 0.3 | 1.0 | 1.0 | 0.0 | 0.0 | 12.0625 |
| `no_regime_ablation` / `stability_heavy` | 0.3 | 1.0 | 1.0 | 0.0 | 0.0 | 10.9375 |
| `no_regime_renormalized` / `stability_heavy` | 0.3 | 1.0 | 1.0 | 0.0 | 0.0 | 13.325 |

## Interpretation

The circularity risk is not fatal in this focused diagnostic: the strict no-regime ablation still passes at the v0.3 threshold `0.30` with TPR `1.0`, on-time TPR `1.0`, and false positive rate `0.0`.

However, the main grand-sim matrix has not yet been rerun with a no-regime Trigger A implementation. CL02 should move from `calibration path found; independence not established` to `precursor independence supported in focused diagnostic; main-matrix transfer pending`.

The lower `0.22` threshold is useful evidence that a pure precursor signal can fire earlier, but it should be treated as exploratory until reviewers accept the increased sensitivity.

Reviewer update:

- `regime_heavy` must be excluded from transfer recommendations because it fails strict no-regime ablation at threshold `0.30`.
- The `0.22` max-lead candidate is deferred because the false-positive boundary is thin: `0.22` has FP `0.0`, while `0.20` has FP `1.0`.
- The recommended next step is a main-matrix transfer rerun using `no_regime_ablation / stability_heavy / psi_threshold = 0.30`.

## Max-Lead Strict Ablation Candidate

| Candidate | threshold | detected TPR | on-time TPR | missed rate | false positive rate | avg lead |
|---|---:|---:|---:|---:|---:|---:|
| `no_regime_ablation` / `v02_default` | 0.22 | 1.0 | 1.0 | 0.0 | 0.0 | 20.25 |

## Max-Lead Independent Candidate

| Candidate | threshold | detected TPR | on-time TPR | missed rate | false positive rate | avg lead |
|---|---:|---:|---:|---:|---:|---:|
| `no_regime_ablation` / `v02_default` | 0.22 | 1.0 | 1.0 | 0.0 | 0.0 | 20.25 |

## Interpretation Rules

- If `no_regime_ablation` passes at threshold `0.30`, the original threshold survives strict circularity removal.
- If only `no_regime_renormalized` passes, CL02 has a plausible pure-precursor formula but needs an architecture decision before main-matrix transfer.
- If neither no-regime variant passes, v0.3's perfect score should be treated as inflated by the collapse-share term.

## Artifacts

- `grand_sim_v0_4_psi_ablation_runs.csv`
- `grand_sim_v0_4_psi_ablation_summary.csv`
- `grand_sim_v0_4_psi_ablation_by_scenario.csv`
- `grand_sim_v0_4_psi_contribution_samples.csv`
