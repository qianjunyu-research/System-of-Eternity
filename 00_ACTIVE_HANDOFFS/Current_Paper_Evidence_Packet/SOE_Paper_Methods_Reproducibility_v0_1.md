# SOE Paper Methods And Reproducibility v0.1

## Simulation Scope

The Grand Simulation is an integrated C00-C08 simulation harness. Its purpose is to test whether component-level governance mechanisms compose under combined topology, detector, resource, identity, async, and governance-capture stresses.

v0.7 is the closure batch used for paper-evidence consolidation.

## v0.7 Batch Summary

| Item | Value |
|---|---:|
| Runs | 870 |
| Step rows | 139,200 |
| Scenarios | 29 |
| Stress profiles | 3 |
| Step budget per run | 160 |

## Locked Source Hierarchy

- C07 v2.2: federation Trigger A uses `Psi_extended`.
- C04 v2.3: non-federation Trigger A may use S-threshold.
- C02 v2.1: T-G loop break-condition margins must remain positive.
- C05 v2.1: H/I/A node classes use distinct identity formulas.
- `f_min = 0.30` and `kappa_min = 0.25` remain distinct.

## Federation Detector Configuration

v0.7 paper configuration:

```text
psi_profile = stability_heavy_no_regime
psi_lambda = 0.10
psi_threshold = 0.30
psi_w_t = 0.20
psi_w_d = 0.20
psi_w_g = 0.15
psi_w_s = 0.35
psi_w_regime = 0.00
```

The regime term is disabled for federation detection in this closure batch.

## Validation Snapshot

| Validation Check | Value | Status |
|---|---:|---|
| `min_break_condition_margin` | 0.006735 | pass |
| `max_k_D_effective` | 0.13 | pass |
| `max_k_C_effective` | 0.10 | pass |
| `federation_c04_trigger_A_violations` | 0 | pass |
| `nonfederation_c07_trigger_A_sources` | 0 | pass |
| `federation_positive_event_rows` | 80 | pass |
| `federation_on_time_positive_rows` | 80 | pass |
| `federation_false_positive_rows` | 0 | pass |
| `max_federation_step_term_regime` | 0.0 | pass |

## Reproducibility Hashes

| Artifact | SHA-256 |
|---|---|
| `soe_grand_sim_v0_7.py` | `c9b96fc5d6722fc2cb894d9537a01567bafcf1c5b656bffb99d2ea8b1647d3f4` |
| `grand_sim_v0_7_runs.csv` | `9f8bbc3bb4213a1f4b5d2a4dadedffda5bf8f84ca0ab723fb807390da7005aa0` |
| `grand_sim_v0_7_steps.csv` | `9be1d13cb272ea7a234c18b53e14e162ad07852bb6d416b665a6203d465724e4` |

## Required Evidence Files

Minimum paper evidence packet:

- `soe_grand_sim_v0_7.py`
- `grand_sim_v0_7_report.md`
- `grand_sim_v0_7_traceability.csv`
- `grand_sim_v0_7_validation_summary.csv`
- `grand_sim_v0_7_focus_summary.csv`
- `grand_sim_v0_7_psi_adversarial_summary.csv`
- `grand_sim_v0_7_topology_impact_summary.csv`
- `grand_sim_v0_7_hub_completeness_summary.csv`
- `grand_sim_v0_7_resource_gradient_summary.csv`
- `grand_sim_v0_7_hashes.csv`

Full reproducibility packet additionally includes:

- `grand_sim_v0_7_runs.csv`
- `grand_sim_v0_7_steps.csv`
- `grand_sim_v0_7_scenario_summary.csv`
- `grand_sim_v0_7_cl09_impact_examples.csv`

## Paper Methods Language

Use this conservative wording:

```text
The simulation should be interpreted as architecture-level computational evidence under a declared scenario matrix, not as empirical validation of real-world governance behavior.
```

Do not describe the batch as:

```text
field validation
deployment test
human-subject validation
real-world governance readiness
```
