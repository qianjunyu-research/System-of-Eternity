# SOE Governance Architecture Ontology and Readiness Patch v0.1

Status: patch document for upgrading Governance Architecture v0.4 into a v0.5 candidate.

Date: 2026-05-12

Scope: ontology cleanup, source hierarchy preservation, and readiness-language repair. This patch does not add deployment claims.

## 1. Patch Intent

This patch prevents the next Governance Architecture version from drifting across four known risk areas:

1. `C` must remain cognitive distortion.
2. `Psi_extended` must remain a C07 detector output, not a primary SOE state variable.
3. `f_min=0.30` and `kappa_min=0.25` must remain distinct.
4. Architecture-ready, simulation-ready, container-test-ready, pilot-ready, and deployment-ready must not be collapsed.

## 2. Canonical Ontology Block

Insert or replace the architecture notation block with:

```text
Canonical SOE variables and detector outputs

T(t): trust.
D(t): disturbance, usually processed as D_effective before entering trust dynamics.
C(t): cognitive distortion. C is not generic cognition, coordination cost, or coordination failure. Coordination failure is downstream C08 behavior.
I(t): identity support / role coherence, subclassed by C05 node class rules.
G(t): governance capacity. When capture or masking is relevant, distinguish G_formal from G_effective.
S(t): stability, a derived state/classification signal.
R(t): active recovery input/pathway.
Psi_base: C07 meta-governance stress detector output.
Psi_extended: C07 federation detector output with cluster-variance term. Psi_extended is a detector output, not a primary SOE state variable.
f_min=0.30: governance disturbance-coupling floor in the C02/C03/C06 path.
kappa_min=0.25: separate protected floor metadata from the simulation handoff. It is not equivalent to f_min.
```

## 3. Required Replacements

Replace loose wording:

```text
C (cognition)
```

with:

```text
C (cognitive distortion)
```

Replace:

```text
T, D, C, I, G, S, and Psi are state variables
```

with:

```text
T, D, C, I, G, and S are bounded architecture variables. Psi_base and Psi_extended are C07 detector outputs derived from those and topology-specific signals.
```

Replace:

```text
Psi_extended is the federation state variable
```

with:

```text
Psi_extended is the C07 federation detector output.
```

## 4. Readiness Taxonomy

Insert this readiness block in the Purpose/Scope or Deployment Boundary section:

| Label | Meaning | Current status |
|---|---|---|
| Architecture-ready | The rules are coherent enough to audit, review, and patch as an architecture. | Current v0.4/v0.5 line: yes. |
| Simulation-ready | A proposed mechanism has an executable simulation spec and test matrix. | C00-C08: yes. C09 and Drift Layer: not yet. |
| Simulation-evidence-ready | A simulation has produced reproducible evidence for bounded claims. | Grand Simulation v0.7 claims only. |
| Container-test-ready | A bounded local logging/audit test can run without real authority. | Node v0.1 exists; Node v0.2 requires protocol and consent. |
| Pilot-ready | Real participants/systems can be tested under formal safeguards. | No. Requires measurement validation, consent, privacy/security controls, stop rules, external review, and governance authority limits. |
| Deployment-ready | A target context can operate SOE mechanisms with actual authority. | No. Requires target calibration, legal legitimacy, resources, monitoring, rollback paths, external audit, and validated measurement. |

Required sentence:

```text
No SOE artifact may use "ready" without specifying which readiness category is meant.
```

## 5. Grand Simulation Evidence Boundary

Insert near the Grand Simulation evidence summary:

```text
Grand Simulation v0.7 is architecture-level simulation evidence only. It does not establish deployment readiness, pilot readiness, empirical proxy validity, real-world safety, or governance-authority sufficiency.
```

Preserve these frozen metrics:

- Runs: 870.
- Step rows: 139,200.
- Scenarios: 29.
- Profiles: 3.
- Federation C04 Trigger A violations: 0.
- Non-federation C07 Trigger A sources: 0.
- CL02 default detector: on-time TPR 1.0, false-positive rate 0.0, average lead 8.175.
- CL02A stability-term ablation: on-time TPR 0.0, average lead -4.1.

## 6. Node v0.1 Firewall

Insert if Node v0.1 is mentioned:

```text
SOE Node v0.1 is a bounded two-node container record. It shows that one lightweight SOE logging container was sustained for seven days. It does not validate SOE dynamics, ignition, network propagation, real-world measurement proxies, pilot readiness, or deployment readiness.
```

## 7. Caveat Inserts

CL02:

```text
Under the locked v0.7 simulation configuration only, Psi_extended detected federation collapse precursors with mean lead 8.175 steps and zero audited no-event false positives. CL02A shows that this result depends materially on the stability term, so the detector should be described as stability-heavy rather than stability-independent.
```

CL05:

```text
Three hubs provide context-dependent mitigation in bounded/localized tested configurations. They do not establish mesh equivalence, universal hub safety, or resilience to simultaneous all-hub integrated stress.
```

CL09:

```text
Topology lag produced safety-relevant wrong-monitoring windows and selected hidden-collapse overlap cases. The v0.7 matrix did not establish broad blind/no-trigger false stability.
```

CL10:

```text
v0.7 measured resource-stress gradients, floor duration, exhaustion incidence, and routing-delay loss. It did not prove recovery sufficiency or define realistic finite-resource operating envelopes.
```

## 8. Versioning Note

This patch should be applied as part of a new v0.5 candidate, not silently edited into the frozen v0.4 release. Keep v0.4 as the frozen source base.
