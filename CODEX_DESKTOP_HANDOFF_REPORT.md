# Codex Desktop Handoff Report - SOE Governance + Star Topology Work

Prepared: 2026-05-07

This report reconstructs the website/mobile Codex work that was not visible to the local Desktop session. The local PC source repo was dirty and partly conflicted, so this clean worktree was created from `origin/codex/find-file-upload-options-on-mobile-app`, the newest visible remote branch containing the v13/v15/v16/v17 simulation artifacts.

## Executive Summary

The recent work expanded the System of Eternity repository into a governance and topology diagnostic workspace.

Main workstreams:

- v1.3 governance diagnostics with dynamic governance coupling.
- C3/SOE explicit `star` topology support.
- Star topology architectural stress tests: v15 hub stress, v16 `k_D` ceiling sweep, v17 hub protection sweep.
- Transfer preparation for local/Desktop continuity.
- Desktop document layer added separately under `docs/latest_desktop_research_2026_05_07/`.

The key architectural finding is that star topology with hub stress is qualitatively dangerous in this model. Reducing the disturbance coupling ceiling alone did not remove sustained ignition in the tested range, and capping hub disturbance exposure also did not reduce sustained ignition below the required `0.05` threshold.

## Important Code Changes

Core files:

- `governance_loop_sim.py`
- `governance_integration.py`
- `governance_regime_scan.py`
- `governance_network_sim.py`
- `soe_simulation.py`

Dynamic governance coupling:

- Added `governance_coupling_floor`.
- Added `governance_coupling_alpha`.
- Corrected `f_min` mapping: `f_min` is the governance coupling floor for dynamic `k_D(t)`, not `disturbance_baseline`.
- Corrected `alpha_gov` scale to architecture values: `0.03, 0.05, 0.07, 0.10, 0.15`.
- Added telemetry such as `governance_coupling_k` and `disturbance_damping_target`.
- Added `recovery_to_stable_conversion_rate` to regime summaries.

Star topology:

- `soe_simulation.py` supports `--topology star`.
- `governance_network_sim.py` supports topology-aware neighbor construction for `ring` and `star`.
- In star mode, node `0` is the hub and all other nodes are peripherals.
- Hub stress remains connected to peripherals; it is not a disconnected-node test.

## Diagnostic Drivers

Governance v1.3:

- `governance_blocking_diagnostic_v13.py`
- `governance_capacity_sweep.py`
- `governance_v13_followup_simulations.py`

Star topology:

- `star_hub_stress_simulation.py`
- `star_ceiling_calibration_sweep.py`
- `hub_protection_simulation.py`

## Key Results

v13 governance:

- Joint diagnostic grid used `f_min = 0.05, 0.10, 0.15, 0.20, 0.25, 0.30`.
- `alpha_gov = 0.03, 0.05, 0.07, 0.10, 0.15`.
- `30` runs and `150` steps per configuration.
- `G(t)` dynamic verification reported zero absolute error for the implemented coupling-update check.

v15 star hub stress:

- `sustained_ignition_rate = 0.43333333333333335`.
- `avg_peripheral_failure_rate = 0.5849943502824858`.
- `avg_peripheral_failure_peak = 0.7497175141242938`.
- `avg_ignition_onset_step = 8.0`.
- `avg_hub_min_stability = 0.4789618530065622`.
- Result: topology-conditioned systemic risk.

v16 star ceiling sweep:

- Tested `k_D = 0.05, 0.07, 0.09, 0.10, 0.11, 0.12, 0.13, 0.15`.
- No tested `k_D` dropped sustained ignition below `0.05`.
- Provisional `0.10` ceiling was not safe under the tested conditions.

v17 hub protection sweep:

- Tested `D_hub_cap = 0.8, 0.6, 0.4, 0.3, 0.2, 0.1`.
- No tested cap dropped sustained ignition below `0.05`.
- Hub protection was not sufficient as a standalone fix.
- Hub minimum stability improves as cap decreases, while peripheral collapse risk remains non-zero.

## Desktop Document Layer

The newest local research layer was found on the PC Desktop, not in Git history. It is archived in this branch under:

- `docs/latest_desktop_research_2026_05_07/System of Eternity/`
- `docs/latest_desktop_research_2026_05_07/Research Work/`

Important latest documents:

- `SOE Failure Layer v1.2.docx`
- `ACGM v1.1 EN.docx`
- `SOE_C00_ProgramIndex_v2_1.docx`
- `SOE Architecture v2 Integration Snapshot.docx`

Document-layer conclusions:

- `f_min = 0.30` is locked by simulation as the disturbance coupling floor.
- Star topology is marked mandatory avoidance.
- Hub protection redistributes load and does not solve star fragility by itself.
- Federation topology is promising but requires `S_threshold` recalibration because existing thresholds create about `90%` false alarms.
- v19 scope: federation `S_threshold` calibration and SSL identity dynamics.

## Reproduction Commands

```bash
python governance_blocking_diagnostic_v13.py --runs 30 --steps 150 --f-min-values 0.05 0.10 0.15 0.20 0.25 0.30 --alpha-gov-values 0.03 0.05 0.07 0.10 0.15 --skip-w-calibration --output v13_blocking_diagnostic_summary.csv --raw-output v13_blocking_diagnostic_runs.csv
python governance_v13_followup_simulations.py
python star_hub_stress_simulation.py
python star_ceiling_calibration_sweep.py
python hub_protection_simulation.py
python soe_simulation.py --years 500 --topology star --runs 100 --output c3_star_topology_runs.csv
```

## Suggested Next Steps

1. Keep this clean worktree as the local recovery point.
2. Confirm `governance_network_sim.py` has no conflict markers.
3. If continuing simulation work, begin v19 federation `S_threshold` calibration.
4. If continuing architecture work, start from `docs/latest_desktop_research_2026_05_07/System of Eternity/SOE Architecture Design v2 - Institutional Mechanisms/SOE_C00_ProgramIndex_v2_1.docx`.
5. Do not delete generated artifacts unless they have been deliberately transferred or re-generated.
