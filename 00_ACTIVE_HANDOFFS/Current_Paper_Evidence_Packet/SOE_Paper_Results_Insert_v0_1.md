# SOE Paper Results Insert v0.1

Use this as source text for the paper's simulation-evidence section. Keep the conservative language.

## Grand Simulation Evidence

We implemented an integrated Grand Simulation for the C00-C08 governance architecture rather than testing each component in isolation. The v0.7 closure batch included 870 runs across 29 scenarios, three stress profiles, and 139,200 step rows. The batch preserved the locked source hierarchy: federation Trigger A used C07 `Psi_extended`, non-federation Trigger A allowed the C04 S-threshold, C02 break-condition margins remained positive, H/I/A identity classes remained distinct, and the `f_min = 0.30` and `kappa_min = 0.25` floors remained separate.

The v0.7 validation checks passed. The minimum break-condition margin was `0.006735`, maximum `k_D_effective` was `0.13`, maximum `k_C_effective` was `0.10`, federation C04 Trigger A violations were `0`, non-federation C07 Trigger A sources were `0`, and the maximum federation `psi_term_regime` was `0.0`.

## Federation Detection

The v0.7 federation detector regression supported CL02 under the tested configuration. `Psi_extended` achieved on-time true-positive rate `1.0`, false-positive rate `0.0`, and average lead to collapse threshold `8.175` steps. This supports `Psi_extended` as the tested federation Trigger A detector inside the simulation envelope.

However, the stability-term ablation is a required caveat. When the stability contribution was removed (`psi_s_weight_scale = 0.0`), on-time true-positive rate fell to `0.0`, and average lead was `-4.1`. This shows that the tested detector is primarily a stability-precursor detector rather than a stability-independent multi-signal detector. The paper should state that adversarial conditions which degrade detection without degrading `S_network` could evade the tested detector.

## Topology And Hub Mitigation

Star topology remained unsafe under the tested assumptions, with a sustained ignition rate of `0.666667`.

Hub redundancy remained context-dependent. Three hubs mitigated balanced single-hub failure and unbalanced primary-hub failure at mid stress, while simultaneous all-hub stress broke both two-hub and three-hub configurations. Secondary unbalanced failure did not separate two-hub from three-hub cases because both survived at mid stress. The correct interpretation is that three hubs are a minimum tested mitigation under specific failure modes, not mesh equivalence and not a universal repair mechanism.

## Topology Lag

Topology-lag stress tests supported CL09 as impact-tested rather than merely measured. Average reclassification latency and wrong-monitoring duration were both `46.666667` steps, with maximum wrong-monitoring window `65` steps. Hidden-collapse overlap was nonzero. The honest interpretation is narrow: stale topology can overlap with hidden collapse, and in one tested condition it produced a brief false-stability window. The result does not show widespread blind false stability across all topology-lag scenarios.

## Governance Capture And Async Collapse

Governance-capture scenarios supported the claim that formal governance can mask ineffective governance. Average governance-capture false-stability duration was `59.433333` steps.

Async/message-loss scenarios supported hidden-collapse sensitivity, with average async false-stability steps `0.366667`. This should be interpreted as simulation-level evidence that coordination delays can hide collapse-like behavior under the tested detector and topology assumptions.

## Resource Stress

Finite-resource stress supported CL10 as stress evidence. Overall resource exhaustion rate was `0.470115`, while targeted stress and pressure scenarios exhausted at `1.0`. The meaningful gradient was not exhaustion incidence; it was the duration of the resource-floor regime and routing-delay loss. Average stress-floor duration was `100.273333` steps, and average routing-delay loss was `0.004152`.

This supports the claim that recovery analysis must account for finite resources and routing delay. It does not prove recovery under realistic operational constraints.

## H/I/A Identity Classes

H/I/A identity separation was measured, with mixed H/I/A identity peak collapse `0.334444`. This supports preserving separate formulas for human, institutional, and agent nodes in the architecture, but the evidence should remain measured/future-work rather than promoted to a strong stress-tested claim.

## Summary

The v0.7 Grand Simulation supports the main architecture claims at simulation level while preserving critical caveats. The simulation phase can close and the evidence can move into paper consolidation. No result supports deployment readiness.
