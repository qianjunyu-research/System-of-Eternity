# SOE Grand Sim v0.4 Copilot Aggregation Report

Purpose: local follow-up to Copilot partial review. These tables quantify threshold curves, original-vs-ablation deltas, and scenario-level term contributions.

## Key Rows

| Variant | Profile | Threshold | on-time TPR | FP rate | avg lead | accepted |
|---|---|---:|---:|---:|---:|---:|
| `with_regime_original` | `stability_heavy` | 0.3 | 1.0 | 0.0 | 12.0625 | 1 |
| `no_regime_ablation` | `stability_heavy` | 0.3 | 1.0 | 0.0 | 10.9375 | 1 |
| `with_regime_original` | `v02_default` | 0.22 | 1.0 | 1.0 | 52.1625 | 0 |
| `no_regime_ablation` | `v02_default` | 0.22 | 1.0 | 0.0 | 20.25 | 1 |
| `with_regime_original` | `v02_default` | 0.2 | 1.0 | 1.0 | 52.1625 | 0 |
| `no_regime_ablation` | `v02_default` | 0.2 | 1.0 | 1.0 | 52.1625 | 0 |
| `with_regime_original` | `regime_heavy` | 0.3 | 1.0 | 0.0 | 7.8625 | 1 |
| `no_regime_ablation` | `regime_heavy` | 0.3 | 0.5 | 0.0 | 4.325 | 0 |

## Interpretation

- The conservative transfer row remains `no_regime_ablation / stability_heavy / 0.30`.
- `regime_heavy / 0.30` fails strict ablation and remains excluded.
- `v02_default / 0.22` remains exploratory: it has strong lead time, but `0.20` hits false positive rate `1.0`.

## Generated Artifacts

- `grand_sim_v0_4_threshold_curve_table.csv`
- `grand_sim_v0_4_ablation_delta_table.csv`
- `grand_sim_v0_4_term_breakdown_by_scenario.csv`
