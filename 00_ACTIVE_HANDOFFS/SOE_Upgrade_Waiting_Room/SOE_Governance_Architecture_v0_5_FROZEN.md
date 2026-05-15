# System of Eternity Governance Architecture v0.5 FROZEN

Status: FROZEN architecture-ready baseline. Not pilot-ready. Not deployment-ready.

Date: 2026-05-13

Source base: SOE Governance Architecture v0.4 FROZEN, Grand Simulation v0.7 evidence package, Node v0.1 execution/intake packet, SOE Upgrade Specification v0.1, first upgrade patch suite, and 2026-05-13 multi-AI review consolidation.

Readiness status: architecture-ready only. Not simulation-evidence-ready for C09 or Drift Layer. Not pilot-ready. Not deployment-ready.

## Version Block

| Field | Value |
|---|---|
| Document | SOE Governance Architecture v0.5 FROZEN |
| Version | v0.5 frozen architecture-ready baseline |
| Supersedes | Supersedes v0.4 as the current architecture-ready baseline only. v0.4 remains preserved as the prior frozen base and source-history record. |
| Primary purpose | Integrate ontology cleanup, readiness distinctions, C09 proposal, Drift Layer requirements, Node measurement boundary, Meta-Governance authority updates, and multi-AI review patches. |
| Evidence base | Grand Simulation v0.7 simulation evidence only; Node v0.1 bounded container record only; C09 and Drift Layer are proposed architecture extensions only. |
| Prohibited interpretation | This document does not establish pilot readiness, deployment readiness, empirical proxy validity, real-world safety, or governance authority sufficiency. |

## 1. Executive Summary

SOE Governance Architecture v0.5 FROZEN upgrades the frozen v0.4 architecture after the Grand Simulation v0.7 closure, Node v0.1 completion/intake review, and multi-AI v0.5 review.

The core architecture remains simulation-constrained and evidence-bounded. Grand Simulation v0.7 supports architecture-level simulation claims across 870 runs, 139,200 step rows, 29 scenarios, and three stress profiles. It does not support deployment claims. Node v0.1 shows that one bounded two-node SOE logging container was sustained for seven days. It does not validate SOE dynamics, ignition, network propagation, pilot readiness, or real-world measurement proxies.

Multi-AI review returned PASS_WITH_PATCHES. This frozen version applies the required architecture-freeze patches while leaving all pilot/deployment blockers intact.

The main v0.5 frozen changes are:

1. Freeze ontology wording: `C` means cognitive distortion, not generic cognition.
2. Clarify that `Psi_base` and `Psi_extended` are C07 detector outputs, not primary SOE state variables.
3. Preserve `f_min=0.30` and `kappa_min=0.25` as distinct floors.
4. Add readiness distinctions: architecture-ready, simulation-ready, simulation-evidence-ready, container-test-ready, pilot-ready, deployment-ready.
5. Add C09 Node Formation and Recognition Layer as a proposed, not-yet-simulated extension.
6. Add Drift Layer requirements as a proposed cross-cutting anti-terminal-drift layer.
7. Strengthen Meta-Governance authority separation, trigger lifecycle, detector change control, capture scenarios, and cost/feasibility gates.
8. Add Node Measurement Protocol as a blocker before Node v0.2 expansion or pilot-facing claims.
9. Add `Psi_extended` adversarial/circularity testing as a blocker before pilot/deployment detector claims.
10. Add C09 gate detail and node-class rules as architecture requirements, not operational validation.
11. Add Drift Layer anti-capture and independent-review requirements.
12. Add Trigger A/B/C/D boundary notes.
13. Add Grand Simulation v0.7 closure wording and public archive linkage requirement.
14. Add defensive red-team guardrails against hidden fitness scoring, exit penalties, irreversible drift lock-in, and single-reviewer drift validation.

## 2. Source Hierarchy

Use this hierarchy when resolving contradictions.

| Tier | Source | Authority |
|---|---|---|
| 0 | Current user constraints | Hard boundary: no Grand Sim deployment claim, no Node validation claim, preserve C as cognitive distortion, preserve `Psi_extended` as detector, keep `f_min` and `kappa_min` distinct. |
| 1 | Governance Architecture v0.4 frozen base and latest C00-C08 extracts | Current architecture source. C02 controls recovery/T-G break logic. C04 controls non-federation S-threshold Trigger A. C05 controls H/I/A classes. C07 controls federation `Psi_extended`. C08 controls coordination/topology-lag behavior. |
| 2 | Grand Simulation v0.7 evidence package | Simulation-level claim status and caveats inside the tested matrix only. |
| 3 | arXiv/preprint manuscript v0.7 and Zenodo metadata | Public wording, publication-boundary source, and archive linkage source. Grand Simulation v0.7 public evidence linkage should preserve the recorded Zenodo DOI `10.5281/zenodo.20144235` where applicable. |
| 4 | Node v0.1 packet and Layer Completion Map | Bounded container evidence and future layer planning. Not validation evidence. |
| 5 | Custom GPT / Meta-AI review | Red-team requirements: ontology cleanup, measurement protocol, adversarial detector testing, authority/cost/feasibility. |
| 6 | Trinity / Unification materials | Optional design filters for C09 and Drift Layer only. Not mandatory doctrine. |

## 3. Canonical Ontology

| Term | Meaning |
|---|---|
| `T(t)` | Trust. Recoverability, reliance, and trust trajectory. |
| `D(t)` | Disturbance. Raw or filtered stress/shock signal, usually processed as `D_effective` before trust dynamics. |
| `C(t)` | Cognitive distortion. Confusion, contradiction, distorted system-state perception. Not generic cognition, coordination cost, or coordination failure. |
| `I(t)` | Identity support / role coherence, subclassed by C05 H/I/A node rules. |
| `G(t)` | Governance capacity. Use `G_formal` and `G_effective` when capture or masking is relevant. |
| `S(t)` | Stability. Derived state/classification signal, not a direct self-report. |
| `R(t)` | Active recovery input/pathway. |
| `Psi_base` | C07 meta-governance stress detector output for non-federation or secondary contexts. |
| `Psi_extended` | C07 federation detector output with cluster-variance term. It is not a primary SOE state variable. |
| `f_min=0.30` | Governance disturbance-coupling floor in the C02/C03/C06 path. |
| `kappa_min=0.25` | Separate protected floor metadata from the simulation handoff. It is not equivalent to `f_min`. |

Required wording rule:

```text
T, D, C, I, G, and S are bounded architecture variables. Psi_base and Psi_extended are C07 detector outputs derived from those and topology-specific signals.
```

## 4. Readiness Taxonomy

No SOE artifact may use "ready" without specifying which readiness category is meant.

| Label | Meaning | v0.5 frozen status |
|---|---|---|
| Architecture-ready | Rules are coherent enough to audit, review, and patch as architecture. | Yes, as frozen baseline. |
| Simulation-ready | A mechanism has executable simulation spec and test matrix. | C00-C08 yes; C09 and Drift Layer no. |
| Simulation-evidence-ready | A simulation produced reproducible evidence for bounded claims. | Grand Simulation v0.7 claims only. |
| Container-test-ready | A bounded local logging/audit test can run without real authority. | Node v0.1 record exists; Node v0.2 requires protocol and consent. |
| Pilot-ready | Real participants/systems can be tested under formal safeguards. | No. |
| Deployment-ready | A target context can operate SOE mechanisms with actual authority. | No. |

Pilot readiness requires measurement validation, consent, privacy/security controls, stop rules, external review, governance authority limits, and operational rollback. Deployment readiness additionally requires target calibration, legal legitimacy, resources, monitoring, external audit, and validated measurement.

## 5. Frozen Grand Simulation v0.7 Claims

Grand Simulation v0.7 is architecture-level simulation evidence only. It does not establish deployment readiness, pilot readiness, empirical proxy validity, real-world safety, or governance-authority sufficiency.

| Claim | Status | Safe v0.5 interpretation |
|---|---|---|
| CL01 | supported | Federation Trigger A respects source hierarchy; C04 S-threshold was not used for federation Trigger A. |
| CL02 | supported_in_v0_7_regression | Under locked v0.7 configuration, `Psi_extended` detected federation collapse precursors with on-time TPR 1.0, false-positive rate 0.0, and average lead 8.175. |
| CL02A | adversarial_measured_v0_7 | Stability-term ablation failed: on-time TPR 0.0 and average lead -4.1. `Psi_extended` is stability-heavy in the tested configuration. |
| CL03 | supported | T-G loop floor-regime break condition remained positive in the tested regime. |
| CL04 | supported | Star topology remains unsafe under tested assumptions. |
| CL05 | context_dependent_unbalanced_tested | Three hubs are context-dependent mitigation, not mesh equivalence or universal hub safety. |
| CL06 | measured | H/I/A identity separation measured; dedicated identity stress remains future work. |
| CL07 | supported | Formal governance can mask ineffective governance in capture-like simulation conditions. |
| CL08 | supported | Async/message loss can create hidden-collapse behavior under tested conditions. |
| CL09 | impact_tested_v0_7 | Topology lag can overlap hidden collapse; broad blind/no-trigger false stability was not established. |
| CL10 | graded_stress_measured_v0_7 | Resource-stress gradients were measured; finite-resource recovery is not proven. |

Validation snapshot:

- Runs: 870.
- Step rows: 139,200.
- Scenarios: 29.
- Profiles: 3.
- Minimum break-condition margin: 0.006735.
- Maximum `k_D_effective`: 0.13.
- Maximum `k_C_effective`: 0.10.
- Federation C04 Trigger A violations: 0.
- Non-federation C07 Trigger A sources: 0.
- Maximum federation `psi_term_regime`: 0.0.

### 5.1 Simulation Closure Confirmation

Grand Simulation v0.7 is the closed terminal evidence batch for this v0.5 architecture freeze.

No v0.5 addition reopens, expands, or upgrades the v0.7 simulation evidence boundary. C09, the Drift Layer, Node v0.2, and `Psi_extended` adversarial/circularity testing are future work streams. They may become simulation-ready or container-test-ready only after separate specifications, review, and execution.

Public archive linkage must be preserved so reviewers can trace v0.7 evidence to the correct archived package. Archive linkage is a reproducibility requirement, not a new evidence claim.

## 6. Node v0.1 Boundary

SOE Node v0.1 is a bounded two-node container record. It shows that one lightweight SOE logging container was sustained for seven days. It does not validate SOE dynamics, ignition, network propagation, real-world measurement proxies, pilot readiness, or deployment readiness.

Allowed Node v0.1 claim:

```text
The SOE structural framework was sustained in one real human two-node interaction container for seven days.
```

Blocked Node v0.1 claims:

- SOE was validated in the real world.
- SOE dynamics were empirically confirmed.
- Ignition was observed or validated.
- Node v0.1 proves pilot readiness.
- Observation-track scores are validated real-world T/D/C/I/S measures.

Node v0.1 carryover issue:

- Correct the completion report typo `May 6-8212, 2026` to `May 6-12, 2026` only through a versioned correction note.

## 7. Component Registry

| ID | Component | v0.5 frozen status |
|---|---|---|
| C00 | Program Index | Existing source registry. Needs v0.5 update to include C09 and Drift Layer proposed-extension status. |
| C01 | Trust Integrity Layer | Existing architecture component. Ontology must preserve T as trust. |
| C02 | Recovery Engine | Existing architecture component. T-G break condition remains simulation-constrained; finite-resource recovery not proven. |
| C03 | Disturbance Buffer | Existing architecture component. Preserve `f_min=0.30` and topology-conditioned disturbance handling. |
| C04 | Stability Lock Mechanism | Existing architecture component. C04 S-threshold Trigger A applies to non-federation; not federation. |
| C05 | Structural Support Layer | Existing architecture component. H/I/A node identity formulas remain distinct. |
| C06 | Governance Module | Existing architecture component. Must distinguish `G_formal` and `G_effective` when capture/masking matters. |
| C07 | Meta-Governance Layer | Existing architecture component. v0.5 adds authority separation, detector change control, trigger lifecycle, and capture gates. |
| C08 | Coordination Layer | Existing architecture component. Handles coordination failure downstream of C; topology lag caveat preserved. |
| C09 | Node Formation and Recognition Layer | Proposed extension. Not simulation-ready or simulation-evidence-ready. |
| DL01 | Drift Layer | Proposed cross-cutting layer. Not simulation-ready or simulation-evidence-ready. |

## 8. C09 Node Formation and Recognition Layer

Status: proposed architecture extension only. C09 is architecture-specified, not simulation-validated, not operationally validated, not pilot-ready, and not deployment-ready.

C09 defines how SOE nodes are proposed, assessed, provisionally operated, recognized, scaled, paused, merged, split, failed, recovered, and retired.

Core rule:

```text
SOE preserves open access to the node-creation pathway, but recognition and scaling require staged evidence of safety, resources, effective exit, anti-capture safeguards, monitoring, rollback, and topology fitness.
```

C09 gates are review requirements. Passing them would not prove that a node is safe in the real world; it would only show that the candidate node satisfied the architecture's stated recognition preconditions under the reviewed context.

Every candidate node must declare a class before measurement or recognition:

| Class | Description | Identity rule |
|---|---|---|
| H | Human participant or human-led small group. | Full C05 H identity formula may apply. |
| I | Institution or formal organization. | Uses role clarity plus functional belonging proxy. |
| A | Pure AI system. | Role-only identity; no psychological belonging. |
| IA | Institutionally embedded AI. | Uses Class I only if organizational embedding is explicit. |
| Mixed | Multiple classes inside one node. | Must specify substructure and measurement rules. |

Unclassified nodes cannot receive full recognition.

C09 lifecycle:

| Stage | Required evidence |
|---|---|
| Proposal | Purpose, node class, participants, intended authority, affected parties, resources, and risks. |
| Assessment | Consent model, topology estimate, hard constraints, privacy burden, resource dependencies. |
| Diagnosis | Capture risk, founder dependence, AI authority drift, star-adjacent topology, exit weakness, resource scarcity. |
| Planning | Measurement protocol, stop rules, rollback route, audit owner, burden limits. |
| Provisional operation | Limited reversible operation with audit trail and no critical authority unless separately authorized. |
| Evaluation | Gate results, artifact review, consent review, topology review, and external critique if needed. |
| Recognition | Effective exit, measurement integrity, anti-capture controls, resource viability, and topology safety. |
| Scaling | Re-run C09 gates at each scope or authority jump. |
| Retirement | Exit completion, dependency unwind, data/archive closure, and accountability note. |

C09 recognition gates:

Gate C09-G01: Identity clarity

- Node class declared.
- Role, scope, and authority boundaries explicit.
- No psychological belonging assigned to AI or institution-only nodes.

Gate C09-G02: Effective exit

- Participants can leave without hidden punishment.
- Exit cannot remove basic needs, housing, work, medical access, safety, or social identity.
- Formal exit is insufficient if practical dependency blocks exit.

Gate C09-G03: Measurement readiness

- T/D/C/I/S scoring protocol exists.
- Missingness and artifact flags are defined.
- At least one review path exists.

Gate C09-G04: Resource viability

- Staffing, compute, money, time, logistics, and compliance burden are identified.
- Resource dependency does not create capture.

Gate C09-G05: Topology fitness

- Topology classified before recognition.
- Star-adjacent structures are redesigned before scaling.
- Federation candidates must support cluster-level monitoring.

Gate C09-G06: Anti-capture

- No founder, hub, funder, AI operator, security function, or evaluator controls all recognition criteria.
- Recognition rules are documented and reviewable.

Gate C09-G07: Rollback readiness

- Pause, downgrade, retirement, and recovery paths exist before operation.
- No trigger or recognition state is permanent without review.

Gate C09-G08: Beneficial coordination protection

- C09 must distinguish harmful cascade from legitimate rapid coordination.
- Emergency response, whistleblowing, lifesaving innovation, and legitimate reform cannot be suppressed merely because they spread quickly.

C09 cannot yet support deployment-ready claims, real authority over people/resources, automatic recognition, automatic scaling, or empirical validation of node legitimacy.

C09 inherits CL09 topology-lag caution. Topology classification can lag actual network behavior, so C09 recognition and scaling must include reclassification triggers and cannot rely on a one-time topology label.

C09 also inherits CL02A measurement caution where recognition depends on stability or detector outputs. A stability-heavy detector result cannot be treated as independent proof of node safety.

## 9. Drift Layer Requirements

Status: proposed cross-cutting architecture layer only. Not simulation-validated, not operationally validated, not pilot-ready, and not deployment-ready.

The Drift Layer detects slow deviation from SOE ontology, evidence boundaries, source hierarchy, topology assumptions, detector settings, node-recognition gates, exit rights, resource dependencies, and archive integrity.

Required drift types:

- ontology drift,
- evidence-boundary drift,
- source-hierarchy drift,
- detector drift,
- topology drift,
- governance-authority drift,
- node-recognition drift,
- exit-right drift,
- resource-dependency drift,
- memory/archive drift,
- beneficial-change suppression.

The Drift Layer detects, classifies, records, and routes drift. It does not become a permanent veto authority and does not silently govern the whole system.

Required records:

- drift register,
- ontology ledger,
- detector threshold/weight ledger,
- source hierarchy ledger,
- topology reclassification log,
- node-recognition decision log,
- exit-right audit log,
- resource dependency log,
- archive/hash/caveat preservation log.

Severity routing:

| Level | Meaning | Action |
|---|---|---|
| D0 | No drift. | Record if audited. |
| D1 | Wording drift only. | Patch language. |
| D2 | Measurement or source ambiguity. | Review before further claims. |
| D3 | Operational risk. | Pause affected mechanism. |
| D4 | Capture or terminal drift risk. | Trigger constitutional/meta-governance review. |

Anti-capture rules:

- No single actor controls drift classification.
- Drift findings are reviewable.
- Dismissed severe findings require written rationale.
- Drift reviewers rotate or have an independent review path.
- Drift Layer authority is bounded to detection and routing unless separately authorized.
- Major pause, rollback, recognition denial, constitutional review, or other irreversible/high-impact action requires independent review.
- The Drift Layer must not become a hidden veto authority.

Defensive red-team guardrails:

- SOE must not introduce an internal fitness score that automatically replaces, removes, or demotes participants or nodes.
- SOE must not attach reputation-decay, exit penalties, or hidden punishment to lawful exit.
- SOE must not permit irreversible evolutionary drift lock-in without versioned review, source-hierarchy check, and independent authority.
- SOE must not treat a single model, single reviewer, or single review thread as sufficient validation for severe drift decisions.

The Drift Layer inherits CL09 topology-lag caution and CL02A stability-dependence caution. Drift findings may use topology or stability signals, but those signals must be treated as context-dependent and reviewable rather than self-validating.

## 10. Meta-Governance Update

C07 remains source of truth for federation `Psi_extended` Trigger A. v0.5 adds the following meta-governance requirements.

Authority separation:

| Function | Rule |
|---|---|
| Sensing | Computes signals such as `Psi_extended`; cannot alone authorize intervention. |
| Classification | Determines event type/severity; must log evidence and uncertainty. |
| Trigger activation | Activates Trigger A/B/C/D labels; must follow source hierarchy and time limits. |
| Intervention/rollback | Performs pause, repair, rollback, downgrade, or deactivation; must be reviewable. |
| Audit | Reviews sensing, classification, trigger, and intervention; must be independent from operator being audited. |

`Psi_extended` change control must record:

- formula,
- weights,
- threshold,
- topology applicability,
- input sources,
- timestamp,
- author/operator,
- reason,
- expected effect,
- rollback threshold,
- reviewer approval,
- adversarial/circularity test status.

Changing `psi_threshold=0.30` or the stability-heavy profile without review creates detector drift.

Every trigger must have activation condition, source component, review interval, deactivation condition, rollback path, abuse/capture warning signs, and evidence log. No trigger may become permanent by inertia.

Trigger boundary notes:

Trigger A:

- Federation: C07 `Psi_extended` only.
- Non-federation: C04 S-threshold may apply.
- Unknown topology: human review or conservative watch only.

Trigger B:

- Cannot be treated as proof of recovery.
- Should record resource availability and unmet recovery demand.

Trigger C:

- Should activate on structural violations such as coupling ceiling breach, source-hierarchy contamination, or recognition-gate failure.

Trigger D:

- Should remain tied to graceful failure, downgrade, or retirement paths, not terminal abandonment.

Major pause, rollback, downgrade, recognition denial, constitutional review, or irreversible/high-impact intervention requires independent review and a recorded decision path.

## 11. Node Measurement Protocol Dependency

Before Node v0.2 or any pilot-facing claim, SOE requires a standalone Node Measurement Protocol that defines:

- explicit informed consent,
- pause/exit rights,
- no hidden scoring of humans,
- T/D/C/I/S and coupling rubrics,
- raw-to-normalized mapping,
- missingness rules,
- artifact flags,
- inter-rater or reviewer logic,
- topology context fields,
- privacy and safety exclusions,
- stop conditions,
- audit outputs.

Node scoring remains local audit instrumentation until independently validated.

Node v0.2 boundary:

Node v0.2 may only be described as a structured bounded measurement/container test after explicit consent, adoption of the Node Measurement Protocol, missingness handling, artifact flags, topology context fields, safety exclusions, stop rules, and at least one review path. It is not a pilot unless separate pilot safeguards, external review, privacy/security controls, and rollback authority are approved.

## 12. `Psi_extended` Adversarial and Circularity Tests

Status: future test specification only. The adversarial/circularity matrix has not been executed or reviewed for v0.5.

Until these tests are executed and reviewed, they do not upgrade the locked Grand Simulation v0.7 detector claim.

Before any pilot or deployment detector claim, `Psi_extended` must be tested against:

- stability clamp,
- stability spoof,
- stability delay,
- stability corruption,
- threshold gaming,
- moving-average reset,
- operator threshold drift,
- topology misclassification,
- independent-signal comparison,
- holdout scenarios.

Required metrics:

- true positives,
- false positives,
- false negatives,
- lead time,
- late detection rate,
- per-scenario confusion matrices,
- confidence intervals where applicable,
- sensitivity to S corruption,
- sensitivity to threshold drift,
- source-hierarchy violations.

Passing those tests would still not make `Psi_extended` deployment-ready. It would only support the bounded claim that `Psi_extended` passed the defined adversarial/circularity simulation matrix under tested conditions.

CL02A remains a required caveat: `Psi_extended` is stability-heavy under the tested v0.7 configuration, so it must not be described as stability-independent or empirically validated as a real-world early-warning system.

## 13. Blockers

Hard blockers before pilot-ready language:

1. Node Measurement Protocol not reviewed/validated.
2. Inter-rater and proxy-validation plan missing.
3. `Psi_extended` adversarial/circularity tests not run.
4. Trigger authority, rollback authority, and audit authority not separated operationally.
5. Drift Layer not simulated or operationalized.
6. C09 node recognition gates not simulated or externally reviewed.
7. Privacy, consent, data-retention, stop-rule, and human-subject safeguards incomplete.
8. Cost/feasibility layer absent.
9. Topology detection and reclassification operational protocol incomplete.
10. External domain review absent.

Publication/reproducibility blocker before public release package:

1. Public archive linkage for Grand Simulation v0.7 evidence must be checked against the recorded Zenodo/public archive target and preserved in release metadata. This requirement preserves reproducibility; it does not expand the evidence claim.

Hard blockers before deployment-ready language:

1. All pilot blockers remain unresolved.
2. Target-context calibration missing.
3. Legal/institutional legitimacy not established.
4. Real-world rollback and deactivation not tested.
5. Finite-resource recovery not solved.
6. Governance capture and detector-operator capture not tested.
7. Star-adjacent topology redesign process not operational.
8. Exit rights not proven effective under dependency pressure.
9. Archive/memory drift controls not operational.
10. Independent audit/accountability structures not established.

## 14. Future Review Questions

Future reviewers should answer:

1. Does v0.5 preserve the Grand Sim and Node v0.1 evidence boundaries?
2. Does the ontology block correctly preserve `C`, `Psi_extended`, `f_min`, and `kappa_min`?
3. Is C09 correctly scoped as proposed, not validated?
4. Is the Drift Layer strong enough to prevent silent terminal drift without becoming a veto authority?
5. Does Meta-Governance authority separation adequately address detector/operator capture?
6. Are the Node Measurement Protocol requirements sufficient before Node v0.2?
7. Are the `Psi_extended` adversarial/circularity tests sufficient before any pilot/deployment detector language?
8. Which items block future simulation, Node v0.2, pilot, or deployment claims?

## 15. Frozen Verdict

v0.5 is frozen as an architecture-ready baseline after multi-AI review patches.

It is not simulation-evidence-ready for C09 or Drift Layer, not pilot-ready, and not deployment-ready.

Frozen baseline wording:

```text
SOE Governance Architecture v0.5 is frozen as the next architecture-ready baseline. Grand Simulation v0.7 remains simulation-only evidence. Node v0.1 remains a bounded two-node container record only. C09, Drift Layer, Node v0.2, and Psi_extended adversarial testing are future work and do not establish pilot or deployment readiness.
```

Recommended next step after this freeze:

```text
Create the frozen v0.5 release packet and update C00 / Meta-Governance patch references without changing evidence boundaries.
```
