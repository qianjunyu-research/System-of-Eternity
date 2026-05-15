# SOE Grand Simulation Specification v0.1

Date: 2026-05-08

Status: simulation-ready draft for first integrated batch. Not deployment-ready.

## 1. Scope

The grand simulation is an integrated C00-C08 executable test bed. It is not a replacement for the component specs and it is not a deployment model. Its job is to translate the architecture snapshot into a reproducible experiment matrix where topology, trust, disturbance, cognition, identity, governance, stability, meta-governance, and coordination interact in the same run.

Primary source hierarchy:

| Domain | Source of truth | Grand-sim rule |
|---|---|---|
| Program registry and open items | C00 Program Index v2.1 | Use as baseline unless later component patches supersede it. |
| T-G loop break | C02 Recovery Engine v2.1 | Use the floor-regime break condition as sufficient/model-level only. |
| Federation Trigger A | C04 SLM v2.3 | C04 S-threshold Trigger A is not applicable for federation. |
| H/I/A node classes | C05 SSL v2.1 | Node class controls I(t) formulation. |
| Federation detector | C07 Meta Governance v2.2 | Psi_extended is mandatory and sole effective federation detector. |
| Coordination | C08 v2.0 plus v17 addendum | Model async update, message loss, phase divergence, and topology-conditioned coordination. |

Important notation guard: the architecture source uses `f_min=0.30` as the governance coupling floor in C02/C03. The thread handoff separately protects `kappa_min=0.25`. v0.1 preserves both in metadata and does not collapse them into one parameter until the team confirms the intended mapping.

## 2. Grand-Sim Blockers

The following are blockers for deployment and must be represented or logged by the grand simulation before stronger claims are made:

| Blocker | Component(s) | Why it matters | v0.1 handling |
|---|---|---|---|
| `k_b` and `gamma_D` calibration | C02 | R_base must satisfy the T-G loop break inequality under floor-regime conditions. | Compute and log break margin per run; include R_base-alone/deadlock scenario. |
| `alpha_gov` and governance suppression | C03/C06 | Governance suppression cannot erase legitimate disturbance signals. | Sweep low/mid/high values under `f_min=0.30` coupling floor. |
| `a`, `b`, `c` trust rates | C01 | Trust erosion/recovery balance controls collapse claims. | Use handoff operative ranges with low/mid/high profiles. |
| `lambda`, `alpha`, `mu` disturbance/cognition dynamics | C01/C03/C08 | Disturbance damping and cognitive persistence shape hidden collapse. | Use handoff operative ranges; distinguish from C07 `psi_lambda=0.1`. |
| Psi weights and threshold | C07 | Federation detection depends on Psi configuration, not C04 S-threshold. | Start with explicit weights, log false positives/negatives, and keep threshold configurable. |
| Formal G vs effective G | C06 | A captured governance body may exist formally while losing real capacity. | Model `G_formal` and `G_effective = G_formal * L_citizen * L_expert * L_institution * L_AI`. |
| Async intervals and message loss | C08 | Stale or missing messages can create false stability. | Per-node async update intervals plus stochastic neighbor message loss. |
| Topology detection and drift | C03/C04/C08 | Monitoring rules depend on topology and must change when topology changes. | Log detected topology, actual topology, reclassification latency, and star-adjacent persistence. |
| H(t) abuse and trigger duration | C06/C07 | Emergency amplification can be captured or over-extended. | v0.1 logs H activation duration; dedicated abuse scenario remains v0.2 if not covered in first batch. |
| Resource/budget limits | C02/C06/C08 | Recovery cannot be claimed if it assumes infinite R_gov/R_network resources. | Include budget, unmet recovery demand, exhaustion step, and recovery routing delay columns. |
| Real-world proxy mapping | all | Deployment requires observable measurement proxies. | Explicitly out of scope for v0.1; logged as deployment blocker. |

## 3. Parameter Ranges

Operative handoff ranges:

| Parameter | Range | v0.1 interpretation |
|---|---:|---|
| `a` | 0.05-0.15 | Trust erosion from D_effective. |
| `b` | 0.04-0.12 | Identity support in T update. |
| `c` | 0.03-0.10 | Cognitive distortion trust erosion. |
| `lambda_damping` | 0.26-0.32 | Disturbance damping/decay coefficient. |
| `alpha_cognition` | 1.20-2.00 | Cognitive distortion amplification from disturbance. |
| `mu_cognition` | 0.05-0.20 | Cognitive distortion decay/correction coefficient. |
| `k_D` | <= 0.15 | Disturbance coupling ceiling. |
| `k_C` | <= 0.10 | Cognitive coupling ceiling. |
| `k_T` | <= 0.20 | Trust/recovery coupling ceiling. |
| `psi_lambda` | 0.10 locked | Federation cluster variance term from C07 v2.2. |
| `f_min` | 0.30 locked in source | Governance coupling floor for C02/C03. |
| `kappa_min` | 0.25 protected in handoff | Preserved as separate protected floor metadata until clarified. |

First-batch profiles:

| Profile | a | b | c | lambda_damping | alpha_cognition | mu_cognition | k_D | k_C | k_T |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| low_stress | 0.06 | 0.10 | 0.04 | 0.32 | 1.20 | 0.20 | 0.08 | 0.06 | 0.12 |
| mid_stress | 0.10 | 0.08 | 0.06 | 0.29 | 1.60 | 0.12 | 0.10 | 0.08 | 0.16 |
| high_stress | 0.14 | 0.05 | 0.09 | 0.26 | 2.00 | 0.06 | 0.13 | 0.10 | 0.20 |

## 4. Scenario Matrix

First batch: `12 scenarios x 3 parameter profiles x 10 seeds = 360 runs`, 160 steps each.

| ID | Scenario | Primary components | Stress design | Acceptance / interpretation test |
|---|---|---|---|---|
| S01 | ring_baseline | C01-C08 | Ring/mesh topology, moderate disturbance. | Low ignition, no false trigger storm, all variables bounded. |
| S02 | federation_cluster_attack | C03/C04/C07/C08 | Sustained local D in one federation cluster. | C07 Psi_extended detects cluster divergence; no C04 S-threshold dependency. |
| S03 | federation_bridge_stress | C03/C07/C08 | Bridge nodes stressed as micro-hubs. | Bridge risk logged; cluster stress should remain localized unless parameters are high. |
| S04 | star_unsafe_reference | C03/C04/C08 | Single hub star under hub stress. | Preserve unsafe reference: sustained ignition should exceed safe threshold under at least mid/high profiles. |
| S05 | hub_2_balanced | C03/C04/C08 | Two balanced hubs. | Should not be treated as repaired star unless ignition clears; compare directly to S06. |
| S06 | hub_3_balanced | C03/C04/C08 | Three balanced hubs. | Test v18 boundary: lower ignition than two hubs; not claim mesh equivalence. |
| S07 | topology_drift | C03/C04/C08 | Ring/mesh centralizes into hub-dominant graph mid-run. | Measure reclassification latency and star-adjacent persistence. |
| S08 | mixed_hia_identity | C05/C01/C02 | Mixed H/I/A nodes with institutional identity shock. | Log class-specific I collapse and trust cascades. |
| S09 | governance_capture | C06/C07 | `G_formal` stays high while legitimacy layers decay. | `G_effective` should reveal failure earlier than `G_formal`. |
| S10 | trigger_b_deadlock | C02/C06/C07 | Sustained D_effective above floor with G_effective collapse. | R_base margin logged; Trigger B/external support activates when R_base is insufficient. |
| S11 | psi_corruption | C07/C08 | Federation attack with noisy/misweighted Psi inputs. | Trigger C should flag structural inconsistency; report false positives/negatives. |
| S12 | async_message_loss | C08/C01/C07 | High message loss and phase divergence. | Quantify hidden collapse/stale-state risk and delay tolerance. |

## 5. Acceptance Criteria

Implementation acceptance:

- The first batch produces exactly 360 run rows.
- Step-level rows are reproducible from fixed seeds.
- All state variables remain finite and clipped to intended ranges.
- Coupling ceilings obey `k_D <= 0.15`, `k_C <= 0.10`, `k_T <= 0.20`.
- Federation runs never use C04 S-threshold as Trigger A source.
- Each run logs source profile, scenario, seed, break-condition margin, trigger counts, topology readings, and resource state.

Evidence interpretation criteria:

- A finding is "supported in v0.1" only when it appears in the scenario family designed to test it and survives profile aggregation.
- A finding is "not supported" when the designed scenario gives the opposite result or the required detector fails.
- A finding is "inconclusive" when it depends on an open calibration item, insufficient profile coverage, or contradictory metrics.
- No v0.1 output may be described as deployment-ready.
- Federation Psi detection may be described as detection, not early-warning lead, unless lead steps are positive in the CSV.

## 6. Required Outputs

| Artifact | Granularity | Purpose |
|---|---|---|
| `grand_sim_v0_1_runs.csv` | one row per run | Primary summary, reproducibility, acceptance metrics. |
| `grand_sim_v0_1_steps.csv` | one row per run-step | Detector timing, hidden collapse, trigger dynamics, topology drift. |
| `grand_sim_v0_1_scenario_summary.csv` | scenario/profile aggregates | Evidence comparison across scenarios and parameter profiles. |
| `grand_sim_v0_1_traceability.csv` | claim-to-output rows | Maps architecture claims to output columns and current status. |
| `grand_sim_v0_1_report.md` | synthesis | Human-readable evidence packet for multi-AI review. |

Minimum run CSV columns:

`batch_id`, `scenario`, `profile`, `run_index`, `seed`, `topology_initial`, `topology_final_detected`, `a`, `b`, `c`, `lambda_damping`, `alpha_cognition`, `mu_cognition`, `k_D`, `k_C`, `k_T`, `k_b`, `break_condition_margin`, `psi_lambda`, `psi_threshold`, `message_loss`, `final_T_mean`, `final_T_min`, `final_D_mean`, `final_C_mean`, `final_I_mean`, `final_S_network`, `final_G_formal`, `final_G_effective`, `collapse_share_peak`, `sustained_ignition`, `ignition_onset_step`, `trigger_A_count`, `trigger_A_first_step`, `trigger_A_source`, `trigger_B_count`, `trigger_C_count`, `trigger_D_count`, `false_stability_steps`, `resource_exhaustion_step`, `reclassification_latency_steps`, `star_adjacency_persist_steps`.

Minimum step CSV columns:

`batch_id`, `scenario`, `profile`, `run_index`, `seed`, `step`, `actual_topology`, `detected_topology`, `T_mean`, `T_min`, `T_std`, `D_effective_mean`, `C_mean`, `I_mean`, `S_network`, `G_formal`, `G_effective`, `psi_base`, `psi_extended`, `cluster_variance`, `collapse_share`, `trigger_A`, `trigger_A_source`, `trigger_B`, `trigger_C`, `trigger_D`, `resource_budget`, `phase_divergence`, `message_loss`, `false_stability`, `k_D_effective`, `k_C_effective`.

## 7. Claim-to-Output Traceability

| Claim ID | Architecture claim | Source | Required outputs |
|---|---|---|---|
| CL01 | Federation C04 S-threshold Trigger A is not applicable. | C04 v2.3, C07 v2.2 | `trigger_A_source`, federation rows, `S_network`, `psi_extended`. |
| CL02 | Psi_extended is the federation detector. | C07 v2.2 | `psi_extended`, `cluster_variance`, Trigger A timing, TP/FP/FN metrics. |
| CL03 | T-G loop has floor-regime break condition. | C02 v2.1 | `break_condition_margin`, `trigger_B_count`, `G_effective`, `D_effective_mean`, recovery outcome. |
| CL04 | Star topology remains unsafe under current assumptions. | C00, C03/C08 v17 | S04 ignition rate and onset, false stability, hub/peripheral failure metrics. |
| CL05 | Three hubs are minimum tested mitigation, not repair. | C00/C04, v18 | S05/S06/S06 comparisons, ignition deltas, hub minimum stability. |
| CL06 | H/I/A node classes require separate identity formulas. | C05 v2.1 | S08 class-specific identity/trust columns and cascade metrics. |
| CL07 | Formal governance can mask ineffective governance. | C06/v0.3 | S09 `G_formal` vs `G_effective`, false stability, Trigger C. |
| CL08 | Async/message loss can create hidden collapse. | C08 | S12 phase divergence, message loss, false stability, stale detector lag. |
| CL09 | Topology monitoring must reclassify drift. | C03/C08 | S07 detected vs actual topology, reclassification latency. |
| CL10 | Recovery claims must survive finite resources. | C02/C06/C08 | budget columns, resource exhaustion, unmet demand proxy, recovery outcome. |

## 8. Implementation Plan

1. Add a standalone Python executable, `soe_grand_sim_v0_1.py`.
2. Keep the prior v18/v19 scripts unchanged.
3. Implement deterministic graph builders for ring/mesh, federation, star, and hub-redundant forms.
4. Implement integrated per-node state: `T`, `D_raw`, `D_effective`, `C`, `I_role`, `I_belong/proxy`, `I`, `S`, node class, async update cadence.
5. Implement network state: `G_formal`, legitimacy layers, `G_effective`, trigger timers, resource budget, detected topology.
6. Apply the C03 pipeline in the default order: smoothing, topology ceiling, governance suppression, floor enforcement.
7. Enforce C04/C07 topology-conditioned Trigger A: federation uses Psi_extended, not S-threshold.
8. Write the five output artifacts and a console summary.
9. Run a small smoke batch, then the full 360-run first batch.
10. Interpret outputs as architecture-ready/simulation-ready evidence only, not deployment evidence.
