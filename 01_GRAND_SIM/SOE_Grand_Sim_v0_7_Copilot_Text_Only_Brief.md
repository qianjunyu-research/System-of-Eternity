# SOE Grand Simulation v0.7 - Copilot Text-Only Brief

Review the v0.7 focused closure batch.

Batch:
- 870 runs.
- 139,200 step rows.
- 29 scenarios x 3 profiles x 10 seeds.

Validation:
- Min break margin: 0.006735.
- Max k_D_effective: 0.13.
- Max k_C_effective: 0.10.
- Federation C04 Trigger A violations: 0.
- Non-federation C07 Psi Trigger A sources: 0.
- Max federation psi_term_regime: 0.0.

Focus results:
- CL02 regression: on-time TPR 1.0, FP 0.0, avg lead 8.175, status supported_in_v0_7_regression.
- CL02A stability-term ablation: on-time TPR 0.0, avg lead -4.1, status adversarial_measured_v0_7.
- CL09 impact: avg latency 46.67, avg wrong-monitoring 46.67, avg hidden-collapse overlap 0.244, blind/no-trigger 0.0, topology false-stability 0.0, max window 65.
- CL05: all-hub delta 0.0, single-hub delta 0.333333, unbalanced primary delta 0.333333, unbalanced secondary delta 0.0, hub3 secondary ignition 0.333333.
- CL10: all-run exhaustion 0.470115, stress exhaustion 1.0, pressure exhaustion 1.0, avg stress floor steps 100.273333, avg routing-delay loss 0.004152.

Key interpretation:
- CL09 is impact-tested: stale topology can overlap hidden collapse, but blind/no-trigger false stability remains 0.
- CL02 default detector still works, but it depends materially on the stability term; ablation fails.
- CL10 gradient appears in floor duration/routing loss, not exhaustion incidence.

Question:
Is v0.7 enough to start paper-evidence consolidation and Node/container v0.1 planning, or do we need a v0.8 simulation first?

Requested output:
- Pass / pass with caveats / block.
- Top 5 findings.
- Any source-hierarchy contradiction.
- Whether CL02A is a serious caveat.
- Whether CL10 needs another graded pass.
- Recommended next phase.
