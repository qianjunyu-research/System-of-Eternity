# GitHub Transfer Manifest

Prepared: 2026-05-07

This branch is a clean local reconstruction of the SOE governance and star-topology work. It was created from `origin/codex/find-file-upload-options-on-mobile-app` because the website handoff commits `5712d50` and `a8c332a` were not visible in this local clone after fetch.

## Branch

- Local branch: `codex/reconstruct-soe-handoff`
- Base remote branch: `origin/codex/find-file-upload-options-on-mobile-app`
- Clean worktree path: `C:\Users\M7120\Documents\SOE-clean-handoff`

## Core Simulation Code

- `soe_simulation.py` - main SOE/C3 simulation, including star topology support.
- `governance_loop_sim.py` - core governance loop model and configurable parameters.
- `governance_integration.py` - integrated governance controller and dynamic `k_D` coupling logic.
- `governance_network_sim.py` - multi-node network simulation with ring/star topology and hub disturbance/cap handling.
- `governance_regime_scan.py` - batch governance diagnostic summaries, including recovery-to-stable conversion.

## v1.3 Governance Diagnostic Drivers

- `governance_blocking_diagnostic_v13.py` - joint `f_min x alpha_gov` blocking diagnostic.
- `governance_capacity_sweep.py` - capacity sweep at selected intervention budgets.
- `governance_v13_followup_simulations.py` - trajectory analysis, `G(t)` verification, and fine `f_min` sweep.

## Star-Topology Diagnostic Drivers

- `star_hub_stress_simulation.py` - v15 star hub stress diagnostic.
- `star_ceiling_calibration_sweep.py` - v16 star `k_D` ceiling calibration sweep.
- `hub_protection_simulation.py` - v17 hub protection (`D_hub_cap`) sweep.

## Decision and Run Artifacts

Star topology:

- `c3_star_topology_runs.csv`
- `star_hub_stress_runs.csv`
- `star_hub_stress_summary.csv`
- `star_hub_stress_note.txt`
- `star_ceiling_sweep_runs.csv`
- `star_ceiling_sweep_summary.csv`
- `star_ceiling_note.txt`
- `hub_protection_runs.csv`
- `hub_protection_summary.csv`
- `hub_protection_note.txt`

v1.3 governance:

- `v13_blocking_diagnostic_runs.csv`
- `v13_blocking_diagnostic_summary.csv`
- `v13_capacity_sweep_runs.csv`
- `v13_capacity_sweep_summary.csv`
- `v13_rewired_governance_diagnostic_runs.csv`
- `v13_rewired_governance_diagnostic_summary.csv`
- `v13_fine_sweep_026_032_runs.csv`
- `v13_fine_sweep_026_032_summary.csv`
- `v13_g_dynamic_verification.csv`
- `v13_trajectory_analysis_fmin_020.csv`
- `rewired_governance_diagnostic_runs.csv`
- `rewired_governance_diagnostic_summary.csv`

Packets and notes:

- `codex_action_list_v13_joint_blocking.md`
- `simulation_round_packet_v1_1.md`
- `simulation_round_raw_data_pack.txt`
- `v13_round_packet.md`
- `v13_round_raw_data_pack.txt`
- `v13_three_simulations_packet.md`
- `CODEX_DESKTOP_HANDOFF_REPORT.md`
- `GITHUB_TRANSFER_MANIFEST.md`
- `DESKTOP_RESEARCH_MANIFEST.md`

## Desktop Research Archive

The latest Desktop document layer is archived under:

- `docs/latest_desktop_research_2026_05_07/System of Eternity/`
- `docs/latest_desktop_research_2026_05_07/Research Work/`

Use the manifest:

- `DESKTOP_RESEARCH_MANIFEST.md`

## Verification Commands

```bash
git status --short
python star_hub_stress_simulation.py
python star_ceiling_calibration_sweep.py
python hub_protection_simulation.py
```
