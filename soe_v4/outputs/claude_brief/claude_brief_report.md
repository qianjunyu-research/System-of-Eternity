# SOE V4 Claude Brief Simulation Report

## Inputs Used

- `SOE_V4.docx` from Desktop.
- `SOE Simulation Log-Completed.docx` treated as the Version 12 simulation reference because no separate `SOE_Simulation_Log_v12_Integrated.docx` file was found locally.
- `Secondary_Simulation_Log_v3.docx` from the workspace.

## Task 1 - O4 Parameter Calibration

Chosen median calibration set: `a=0.2887`, `b=0.1042`, `c=0.1826`, `lambda=0.2770`, `alpha=0.2039`, `mu=0.2319`.

| Parameter | P10 | P50 | P90 | Min | Max |
| --- | ---: | ---: | ---: | ---: | ---: |
| a | 0.2215 | 0.2887 | 0.3321 | 0.1584 | 0.3399 |
| b | 0.0850 | 0.1042 | 0.1330 | 0.0801 | 0.1610 |
| c | 0.1132 | 0.1826 | 0.2289 | 0.0817 | 0.2399 |
| lam | 0.2176 | 0.2770 | 0.3267 | 0.1593 | 0.3400 |
| alpha | 0.1187 | 0.2039 | 0.3063 | 0.1011 | 0.3377 |
| mu | 0.1425 | 0.2319 | 0.3048 | 0.1208 | 0.3199 |

### Stability Envelope

| Zone | D Range | C Range | I Range | R Range | Accepted Share | Median Margin |
| --- | --- | --- | --- | --- | ---: | ---: |
| stable | 0.18-0.26 | 0.17-0.19 | 0.72-0.82 | 0.03-0.05 | 0.5207 | 0.0278 |
| critical | 0.34-0.40 | 0.24-0.30 | 0.52-0.64 | 0.05-0.06 | 0.0014 | -0.0344 |
| collapse | 0.44-0.52 | 0.34-0.40 | 0.34-0.44 | 0.02-0.03 | 1.0000 | -0.1301 |

### Normal-Operation Confirmation

| Point | bI + R | aD + cC | Margin | Holds? |
| --- | ---: | ---: | ---: | --- |
| normal_low | 0.1155 | 0.0830 | 0.0325 | yes |
| normal_high | 0.1251 | 0.1097 | 0.0153 | yes |

### Collapse Thresholds

| Reference Point | D Threshold | C Threshold | Support/Damage Ratio Threshold |
| --- | ---: | ---: | ---: |
| normal_reference | 0.3064 | 0.3166 | 1.0 |
| stress_reference | 0.2872 | 0.1881 | 1.0 |

## Task 2 - Hero Trigger Gate

False positive rate: `0.0`.
False negative rate: `0.0`.
Fast-collapse dangerous-delay rate: `1.0`.
False-activation result: `pass`.
Genuine-critical activation result: `pass`.
72-hour delay result: `fail`.

## Task 3 - Chapter 5 Merged Layer Interactions

| Scenario | Architecture | Cascade Rate | Pre-Reentry Identity Collapse | Recovery Intact | Avg Re-entry Step | Avg Recovery Step |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| ci_only | separate | 0.0000 | 0.0000 | 0.1875 | -1.0000 | 15.0000 |
| ci_only | merged | 0.0000 | 0.0000 | 0.1667 | -1.0000 | 15.0000 |
| identity_only | separate | 0.0000 | 1.0000 | 1.0000 | -1.0000 | 9.9583 |
| identity_only | merged | 0.0000 | 1.0000 | 1.0000 | -1.0000 | 9.9750 |
| dual_failure | separate | 1.0000 | 1.0000 | 0.0000 | 8.9292 | -1.0000 |
| dual_failure | merged | 1.0000 | 1.0000 | 0.0000 | 8.1833 | -1.0000 |

Merged-layer readout:
CI-only instability did not trigger an identity-collapse cascade in either formulation, but simultaneous 5.2 + 5.3 failure produced full cascade in both (`merged=1.0000`, `separate=1.0000`).
Dual failure in the merged architecture shows pre-reentry identity collapse at `1.0000` versus `1.0000` in the separated counterfactual.
Recovery remains intact in `0.0000` of merged dual-failure runs, so the recovery pathway is not intact under simultaneous 5.2 + 5.3 failure in this run family.

## Task 4 - Coordination Layer

Highest robust stable window with non-zero trust bridging: topology `federation`, fail coupling `0.12`, trust coupling `0.16`, total fail coupling `0.60`, total trust coupling `0.80`, stable-run rate `1.0000`.
Over-coupling worst case: fail coupling `0.20`, trust coupling `0.00`, synchronized collapse rate `1.0000`.
Over-decoupling worst case with zero trust bridging: fail coupling `0.20`, trust coupling `0.00`, meta-trigger rate `0.8167`.

Coordination verification:
- Coordination failure did route into Meta-trigger conditions whenever divergence stayed above the recoverable band and mean disturbance remained elevated.
- At low failure-coupling sums the system could remain stable even with zero trust bridging, but once failure-coupling entered the upper scan band, non-zero trust bridging became necessary for any stable runs to remain.
- The empirical safe window from this scan is documented in the coordination summary CSV in the output folder.

## V4.1 Flags Before CN Translation

- The 72-hour Hero delay is unsafe in the simulated fast-collapse family and should be treated as a V4.1 review item before CN translation.
- The Chapter 5 recovery pathway did not remain intact under simultaneous 5.2 + 5.3 failure in this run family and should be treated as a V4.1 review item before CN translation.

## Output Files

- [claude_brief_parameter_ranges.csv](C:/Users/M7120/Documents/New project 7/soe_v4/outputs/claude_brief/claude_brief_parameter_ranges.csv)
- [claude_brief_envelope.csv](C:/Users/M7120/Documents/New project 7/soe_v4/outputs/claude_brief/claude_brief_envelope.csv)
- [claude_brief_hero_gate.csv](C:/Users/M7120/Documents/New project 7/soe_v4/outputs/claude_brief/claude_brief_hero_gate.csv)
- [claude_brief_merged_layers.csv](C:/Users/M7120/Documents/New project 7/soe_v4/outputs/claude_brief/claude_brief_merged_layers.csv)
- [claude_brief_coordination_summary.csv](C:/Users/M7120/Documents/New project 7/soe_v4/outputs/claude_brief/claude_brief_coordination_summary.csv)
