# SOE Paper Evidence Consolidation v0.1

Status: paper-evidence consolidation packet after Grand Simulation v0.7 closure.

## Executive Decision

The Grand Simulation phase should close at v0.7. The next primary artifact is the paper evidence section, not another simulation batch.

Claude's architecture-auditor verdict:

```text
Pass. Simulation phase can close. Pivot to paper-evidence consolidation.
```

The evidence base is strong enough for simulation-level claims:

- 870 runs.
- 139,200 step rows.
- 29 scenarios.
- 3 parameter profiles.
- Required validation checks passed.
- No source-hierarchy contradictions found by the final multi-AI review cycle.

## Interpretation Boundary

Allowed claim:

```text
The integrated simulation provides reproducible simulation-level evidence for the tested SOE governance architecture claims.
```

Blocked claims:

```text
SOE is deployment-ready.
SOE can govern real groups.
The simulation validates real-world social proxies.
The federation detector is independent of stability signals.
Three hubs are equivalent to a mesh.
Resource recovery is proven under realistic operational constraints.
```

## Terminal Claim Status

| Claim | Paper Status | Evidence Interpretation |
|---|---|---|
| CL01 | supported | Federation Trigger A respects the source hierarchy: C04 S-threshold is not used for federation Trigger A. |
| CL02 | supported_in_v0_7_regression | `Psi_extended` works as the tested federation detector under the locked v0.7 configuration. |
| CL02A | adversarial_measured_v0_7 | The detector depends materially on the stability term; this is a required caveat, not a blocker. |
| CL03 | supported | The T-G loop break condition remains positive in the tested floor regime. |
| CL04 | supported | Star topology remains unsafe under the tested assumptions. |
| CL05 | context_dependent_unbalanced_tested | Three hubs mitigate specific single-hub failures, but do not provide mesh equivalence and do not survive all-hub stress. |
| CL06 | measured | H/I/A identity separation is measured but not stress-tested enough for a strong architecture claim. Treat as future work. |
| CL07 | supported | Formal governance can mask ineffective governance under capture-like conditions. |
| CL08 | supported | Async/message loss can create hidden-collapse behavior under tested conditions. |
| CL09 | impact_tested_v0_7 | Topology lag can overlap with hidden collapse; one tested condition produced a brief false-stability window. |
| CL10 | graded_stress_measured_v0_7 | Resource stress produces meaningful gradients in floor duration and routing-delay loss, while pressure scenarios still exhaust. |

## Paper-Ready Thesis

The v0.7 integrated batch converts the SOE architecture from isolated component tests into a reproducible simulation evidence base. It supports the source hierarchy and the main detector/topology/resource claims inside the tested simulation envelope, while also sharpening several caveats. The strongest supported results are federation Trigger A separation, `Psi_extended` regression performance, star-topology risk, governance-capture false stability, async hidden-collapse behavior, and finite-resource sensitivity. The main limiting results are the stability-term dependence of `Psi_extended`, context-dependent hub mitigation, narrow but real topology-lag false stability, and measured-only H/I/A identity evidence.

## Required Paper Caveats

1. `Psi_extended` is primarily a stability-precursor detector. The stability term is not optional in the tested configuration.
2. CL09 should not be overstated. Topology lag overlaps hidden collapse in several conditions, but blind false stability is narrow.
3. CL05 should remain context-dependent. Three hubs help under single-hub and unbalanced-primary failures but do not imply mesh equivalence.
4. CL10 should be described as stress evidence. The tested pressure scenarios all exhaust; the useful result is duration and routing-loss gradient.
5. CL06 should be listed as measured/future work rather than promoted to a supported deployment claim.

## Next Artifact

Draft or patch the paper with:

1. A Grand Simulation methods subsection.
2. A claim-status evidence table.
3. A concise results subsection for CL01-CL10.
4. A limitations subsection that explicitly records CL02A, CL05, CL06, CL09, and CL10 caveats.
5. A reproducibility appendix listing code hashes and CSV outputs.
