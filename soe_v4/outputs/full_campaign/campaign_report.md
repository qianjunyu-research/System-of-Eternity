# SOE V4 Full Simulation Expansion Campaign

## Inputs Used

- `SOE_V4.docx`.
- `SOE Simulation Log-Completed.docx` used as the local Version 12 reference because no separate `SOE_Simulation_Log_v12_Integrated.docx` file was found in the workspace or Desktop scan.
- `Secondary_Simulation_Log_v3.docx`.
- Prior v1.3 and v2.0 baseline code in the workspace.

## Assumptions

- Phase 3 node failure was counted when `T < 0.25` for 3 consecutive cycles, or when `D >= 0.44` for 3 consecutive cycles with negative support margin `bI + R - aD - cC < 0`.
- Hero-gate comparison used `12h` measurement cycles so that `72h = 6 cycles`, `48h = 4`, `24h = 2`, and `12h = 1`.

## Phase 5 First

Hero 72h gate: false positive `0.0`, false negative `0.5238`, fast-collapse survival `0.0`.
Hero 48h gate fast-collapse survival: `0.0`.
Hero 24h gate fast-collapse survival: `0.84`.
Conditional fast-trigger survival: `0.84` with false positive `0.0`.
Dual failure current-structure recovery probability: `0.0` with collapse probability `1.0`.
Dual failure combined-minimal-support recovery probability: `0.0` with collapse probability `1.0`.
Minimal recovery condition from the support search: trust boost `not_found`, coordination assist `not_found`, staged re-entry `not_found`, recovery probability `0.0`.

## Phase 1 Monte Carlo

Survival rate `0.7469`, stable rate `0.6438`, metastable rate `0.1031`, collapse rate `0.2531`.
Collapse-time distribution: P10 `22`, P50 `22`, P90 `22`.
Collapse-band entry rate `0.3812`, post-shock recovery success `0.725`.

## Phase 2 Regime Mapping

Regime-boundary cells reaching metastable transition: `48`.
- Boundary details are saved in the regime boundary CSV.

## Phase 3 Network Stress

`k_T*` rows written for all topology / node-count / coupling-regime combinations: `27`.
Systematic-collapse cells (cascade probability >= 0.8): `54`.

## Phase 4 Adversarial Scenarios

- coordinated_spikes / fully_connected: collapse `0.0`, false stability `0.0`, recovery `1.0`.
- coordinated_spikes / random: collapse `0.0`, false stability `0.0`, recovery `1.0`.
- coordinated_spikes / clustered: collapse `0.0`, false stability `1.0`, recovery `1.0`.
- cognitive_amp / fully_connected: collapse `0.0`, false stability `0.0`, recovery `1.0`.
- cognitive_amp / random: collapse `0.0`, false stability `0.0`, recovery `1.0`.
- cognitive_amp / clustered: collapse `0.0`, false stability `0.0`, recovery `1.0`.
- trust_targeted / fully_connected: collapse `0.0`, false stability `0.0`, recovery `1.0`.
- trust_targeted / random: collapse `0.0`, false stability `0.0`, recovery `1.0`.
- trust_targeted / clustered: collapse `0.0`, false stability `0.0`, recovery `1.0`.
- timing_attack / fully_connected: collapse `0.0`, false stability `0.0`, recovery `1.0`.
- timing_attack / random: collapse `0.0`, false stability `0.0`, recovery `1.0`.
- timing_attack / clustered: collapse `0.0`, false stability `1.0`, recovery `1.0`.

## V4.1 Flags Before CN Translation

- The current 72h Hero gate is structurally unsafe in the fast-collapse family and needs a V4.1 patch before CN translation.
- Simultaneous 5.2 + 5.3 degradation is not recoverable under the current structure in this campaign and needs a V4.1 patch before CN translation.
- Some network coupling regimes collapse systematically under the locked equations; those unsafe coupling bands should be treated as validated exclusion zones.

## Output Files

- [phase5_hero_summary.csv](C:/Users/M7120/Documents/New project 7/soe_v4/outputs/full_campaign/phase5_hero_summary.csv)
- [phase5_dual_failure_summary.csv](C:/Users/M7120/Documents/New project 7/soe_v4/outputs/full_campaign/phase5_dual_failure_summary.csv)
- [phase1_monte_carlo_summary.csv](C:/Users/M7120/Documents/New project 7/soe_v4/outputs/full_campaign/phase1_monte_carlo_summary.csv)
- [phase2_regime_boundaries.csv](C:/Users/M7120/Documents/New project 7/soe_v4/outputs/full_campaign/phase2_regime_boundaries.csv)
- [phase3_network_summary.csv](C:/Users/M7120/Documents/New project 7/soe_v4/outputs/full_campaign/phase3_network_summary.csv)
- [phase4_adversarial_summary.csv](C:/Users/M7120/Documents/New project 7/soe_v4/outputs/full_campaign/phase4_adversarial_summary.csv)
