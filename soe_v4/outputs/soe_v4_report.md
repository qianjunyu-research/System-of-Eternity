# SOE V4 Simulation Report

## Source Mapping

- `SOE_V4.docx`: master architecture, V4 state set `T/D/C/I/S`, meta-governance triggers, coordination, re-entry, identity, oversight, exit, and stress-test framing.
- `SOE_Model_v1.3_Formatted.docx`: trust-centered local dynamics and regime-sensitive control logic.
- `SOE Network Dynamic v2.0 Final.docx`: disturbance/cognition propagation and conditional trust bridging across nodes.
- `SOE_Node_v0.1_Execution_Spec.docx`: prior envelope assumptions, especially the no-self-ignition expectation under purely local propagation.
- `SOE Simulation Log-Completed.docx`: trust recovery need, topology sensitivity, and the use of repeated Monte Carlo summaries rather than one-off seeds.
- `Bounded_Propagation_Without_Ignition_v6_Formatted.docx`: shaped the `local_only_no_coordination` probe.
- `Simulation Plan.docx`: motivated the scenario suite as a stability atlas rather than a single run.
- `Trinity Framework.docx`, `Unification Method.docx`, and `归一法.docx`: modeled as unification/coherence pressure that reduces cognitive distortion and supports protocol alignment.
- `Full System Audit.docx`, `_SOE_Falsification_Log_v1_格式化版.docx`, `_SOE_Regime_Log_v1_格式化版.docx`: used as discipline constraints to keep claims comparative, threshold-aware, and non-final.

## Run Settings

- Runs per scenario: 12
- Years per run: 300
- Step size: 10
- Nodes: 20

## Ranked Results

| Scenario | Topology | Final Stability | Min Stability | Stable Share | Low-Trust Share | Exit Events | Re-entry Events | Coordination Events |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline_small_world | small-world | 0.6634 | 0.6562 | 0.0354 | 0.0375 | 0.00 | 20.67 | 201.33 |
| baseline_federation | federation | 0.6625 | 0.6563 | 0.0321 | 0.0346 | 0.00 | 18.33 | 201.17 |
| no_reentry_layer | federation | 0.6312 | 0.6311 | 0.0321 | 0.2083 | 0.00 | 0.00 | 201.33 |
| ai_capture_guarded | federation | 0.6200 | 0.5947 | 0.0199 | 0.4881 | 0.00 | 282.00 | 299.00 |
| ai_capture_unchecked | federation | 0.6137 | 0.5855 | 0.0139 | 0.5724 | 0.00 | 331.67 | 331.00 |
| high_info_warfare | small-world | 0.5319 | 0.5156 | 0.0043 | 0.8854 | 0.00 | 511.75 | 527.00 |
| exit_cascade_pressure | hub | 0.2195 | 0.2195 | 0.0000 | 0.8850 | 374.75 | 511.00 | 567.08 |
| no_identity_layer | federation | 0.2181 | 0.2176 | 0.0000 | 0.9044 | 462.92 | 522.67 | 561.83 |
| local_only_no_coordination | ring | 0.0644 | 0.0644 | 0.0203 | 0.7957 | 221.92 | 457.42 | 0.00 |

## Quick Read

- The best-performing scenarios are the ones that keep the full V4 stack active, especially oversight, coordination, re-entry, and identity support.
- Removing re-entry or identity support lowers stability and increases low-trust exposure, which matches the logic in Chapter 5 and the earlier simulation logs.
- The local-only mode is intentionally weaker: it allows stress propagation but underperforms the coordinated V4 cases, which is consistent with the bounded-propagation paper.
- Guarded and unguarded AI-pressure scenarios can be compared directly to estimate how much the oversight layer matters under the same capture pressure.
