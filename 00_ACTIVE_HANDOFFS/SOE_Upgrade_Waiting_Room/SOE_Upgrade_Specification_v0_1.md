# SOE Upgrade Specification v0.1

Status: planning specification for the SOE Upgrade Phase after Governance Architecture v0.4, Grand Simulation v0.7, and Node v0.1.

Date: 2026-05-12

Scope: produce an upgrade plan and blocker list only. This document does not rewrite the SOE Governance Architecture or the SOE Meta-Governance Framework.

## 1. Executive Decision

The SOE upgrade phase can begin from a stable evidence boundary:

- Grand Simulation v0.7 is closed as simulation-level architecture evidence.
- Grand Simulation v0.7 is not deployment evidence, pilot evidence, empirical proxy validation, or real-world safety proof.
- Node v0.1 is a bounded real-world container record.
- Node v0.1 is not validation evidence for SOE dynamics, ignition, network propagation, or deployment readiness.
- Governance Architecture v0.4 remains the frozen architecture base until patched through a new versioned document.
- Trinity Framework and Unification Method materials may be used as idea-generation and design-review filters, not as mandatory SOE doctrine.

The correct next artifact after this spec is a controlled patch pass for:

1. Governance Architecture ontology and readiness wording.
2. Meta-Governance Framework authority, detector, rollback, and drift-control requirements.
3. A proposed C09 Node Formation and Recognition Layer.
4. A Node measurement protocol before any v0.2 container or pilot expansion.

## 2. Source Hierarchy

Use this hierarchy when resolving contradictions.

| Tier | Source | Authority for upgrade |
|---|---|---|
| 0 | User constraints in this upgrade prompt | Hard boundary for this spec. Do not treat Grand Sim as deployment evidence. Do not treat Node v0.1 as validation evidence. Preserve C as cognitive distortion. Keep `f_min=0.30` and `kappa_min=0.25` distinct. |
| 1 | SOE Governance Architecture v0.4 frozen base and C00-C08 latest component extracts | Current architecture source base. C02 controls recovery and T-G break logic. C04 controls non-federation S-threshold Trigger A. C05 controls H/I/A node classes. C07 controls federation `Psi_extended`. C08 controls coordination/topology-lag behavior. |
| 2 | Grand Simulation v0.7 evidence package and paper evidence consolidation | Simulation-level claim status and caveats. Supports claim-to-output traceability only inside the tested matrix. |
| 3 | arXiv/preprint manuscript v0.7 and Zenodo metadata | Public wording and publication-boundary source. Must remain conservative and simulation-level. |
| 4 | Node v0.1 Execution Spec, Completion Report, Intake Review, Layer Completion Map | Bounded real-world container and measurement-protocol planning source. Does not validate SOE dynamics. |
| 5 | Custom GPT / Meta-AI review | Red-team requirements: ontology cleanup, measurement protocol, adversarial detector testing, trigger authority, cost/feasibility, and drift risk. |
| 6 | Trinity Framework / Unification Method notes | Optional design filters for C09 and drift governance: hard-constraint filter, explicit meta-rule, staged recognition, ADPIE loop, anti-gaming review. |
| 7 | Older SOE Meta-Governance / Civilization materials | Conceptual lineage and hypothesis source only where consistent with frozen architecture and v0.7 boundaries. |

If tiers conflict, prefer the higher tier and record a patch item rather than blending definitions.

## 3. Frozen Grand Simulation v0.7 Claims

These claims are frozen as simulation-level evidence only.

| Claim | Frozen status | Safe interpretation |
|---|---|---|
| CL01 | supported | Federation Trigger A respects source hierarchy: C04 S-threshold was not used for federation Trigger A. |
| CL02 | supported_in_v0_7_regression | Under the locked v0.7 simulation configuration, `Psi_extended` detected federation collapse precursors with on-time TPR 1.0, false-positive rate 0.0, and average lead 8.175 steps. |
| CL02A | adversarial_measured_v0_7 | Stability-term ablation failed: on-time TPR 0.0 and average ablation lead -4.1. `Psi_extended` is stability-heavy under the tested configuration. |
| CL03 | supported | T-G loop floor-regime break condition remained positive in the tested regime; average deadlock Trigger B count was 93.366667. |
| CL04 | supported | Star topology remained unsafe under tested assumptions; star sustained ignition rate was 0.666667 in v0.7. |
| CL05 | context_dependent_unbalanced_tested | Three hubs are context-dependent mitigation in bounded cases, not mesh equivalence or universal hub safety. |
| CL06 | measured | H/I/A identity separation was measured but should remain future work for stronger identity stress claims. |
| CL07 | supported | Formal governance can mask ineffective governance in capture-like simulation conditions; average false-stability steps were 59.433333. |
| CL08 | supported | Async/message loss can create hidden-collapse behavior under tested conditions; average async false-stability steps were 0.366667. |
| CL09 | impact_tested_v0_7 | Topology lag can overlap with hidden collapse; one tested condition produced a brief false-stability window. Broad blind/no-trigger false stability was not established. |
| CL10 | graded_stress_measured_v0_7 | Resource stress produced gradients in floor duration and routing-delay loss; pressure/stress scenarios still exhausted. Recovery under realistic finite resources is not proven. |

Validation snapshot to preserve:

- 870 run rows.
- 139,200 step rows.
- 29 scenarios.
- 3 stress profiles.
- Minimum break-condition margin: 0.006735.
- Maximum `k_D_effective`: 0.13.
- Maximum `k_C_effective`: 0.10.
- Federation C04 Trigger A violations: 0.
- Non-federation C07 Trigger A sources: 0.
- Maximum federation `psi_term_regime`: 0.0.

## 4. Node v0.1 Evidence Boundary

Node v0.1 should be treated as:

- a completed 7-day two-node container record,
- a carryability/logging feasibility record,
- a bridge toward v0.2 planning,
- not pilot evidence,
- not deployment evidence,
- not validation evidence for SOE dynamics,
- not ignition evidence,
- not proof that subjective scores are real-world equivalents of simulation variables.

Safe Node v0.1 claim:

> The SOE structural framework was sustained in one real human two-node interaction container for 7 days.

Blocked Node v0.1 claims:

- SOE was validated in the real world.
- SOE dynamics were empirically confirmed.
- Ignition was observed or validated.
- Node v0.1 proves pilot readiness.
- Observation-track scores are validated real-world T/D/C/I/S measures.

Specific Node v0.1 facts to preserve:

- Gate A passed.
- 7/7 days logged.
- Multiple genuine daily interactions occurred.
- Four conflict events were processed through the Unification Method.
- The relationship was a high-trust two-node family context, so generalization is blocked.
- Node B must explicitly consent before v0.2 structured participation begins.
- The completion report contains a date typo that appears as `May 6-8212, 2026`; patch to `May 6-12, 2026` in the next document version.

## 5. Ontology Cleanup Plan

Canonical ontology for the next SOE patch:

| Term | Canonical meaning |
|---|---|
| `T` | Trust. Recoverability, reliance, and trust trajectory. |
| `D` | Disturbance. Stress/shock signal, filtered as `D_effective` before trust dynamics. |
| `C` | Cognitive distortion. Confusion, contradiction, distorted system-state perception. Not generic cognition and not coordination cost. |
| `I` | Identity support / role coherence, subclassed by H/I/A node class rules. |
| `G` | Governance capacity. Must distinguish `G_formal` from `G_effective` when masking/capture matters. |
| `S` | Stability. Derived state/classification signal, not a direct self-report. |
| `R` | Recovery input/pathway, including internal, network, governance, and baseline recovery. |
| `Psi_base` | C07 meta-governance stress detector for non-federation/secondary monitoring contexts. |
| `Psi_extended` | C07 federation detector with cluster-variance term. It is a detector output, not a primary state variable. |
| `f_min=0.30` | Governance disturbance-coupling floor in the C02/C03/C06 architecture path. |
| `kappa_min=0.25` | Separate protected floor metadata from the handoff; do not collapse into `f_min`. |

Required cleanup patches:

1. Replace `C (cognition)` in the v0.7 manuscript and arXiv metadata with `C (cognitive distortion)`.
2. Patch any phrase that describes `Psi(t)` or `Psi_extended` as a state variable. Use "detector," "stress index," or "derived meta-governance detector output."
3. Add an ontology note that C08 handles coordination failure downstream; it does not redefine `C`.
4. Standardize `G_formal` versus `G_effective` in governance-capture discussion.
5. Add a short collapse/ignition glossary:
   - `collapse30`: simulation event where collapse share crosses 0.30.
   - `ignition`: sustained propagation condition inside the simulation matrix.
   - "real-world collapse" and "civilizational failure" are not inferred from these terms without new calibration.
6. Put `f_min=0.30` and `kappa_min=0.25` in the same notation table with explicit non-equivalence.

## 6. C09 Node Formation and Recognition Layer Proposal

Status: proposed architecture extension only. Not simulation-validated. Not pilot-ready.

Purpose:

C09 defines how SOE nodes are proposed, assessed, provisionally operated, recognized, scaled, paused, merged, split, failed, recovered, or retired without converting open node creation into unchecked systemic risk.

Core design principle:

> Node formation should preserve open civilian/community access to the node-creation pathway while requiring staged evidence of responsibility, resource viability, effective exit, anti-capture safeguards, monitoring, rollback, and scaling safety before full recognition.

Required C09 lifecycle:

| Stage | Function | Required evidence |
|---|---|---|
| Proposal | Any eligible civilian/community/institution can propose a node. | Declared purpose, node class, scope, participants, resources, risk class, exit path. |
| Assessment | Map context, topology, hard constraints, and affected parties. | H/I/A classification, dependency map, topology estimate, data/privacy burden, consent model. |
| Diagnosis | Classify risk and likely failure mode. | Capture risk, resource scarcity, AI authority drift, founder dependence, hard-constraint conflicts. |
| Planning | Design provisional test and measurement protocol. | T/D/C/I/S rubrics, inter-rater plan, stop rules, rollback route, burden limits. |
| Provisional operation | Run bounded, reversible operation. | No real authority over critical resources unless separately authorized; full audit trail. |
| Evaluation | Decide recognition, revision, pause, rollback, or retirement. | Gate results, independent review, artifact-risk review, participant consent review. |
| Recognition | Grant limited or full SOE node recognition. | Measurement integrity, exit rights, anti-capture controls, resource viability, topology safety. |
| Scaling | Increase size/scope only after new review. | Re-run topology, resource, drift, consent, and rollback checks at each scale jump. |

Required C09 gates:

- Node identity declaration: H, I, A, mixed, or institutionally embedded AI.
- Effective exit: participants can leave without loss of basic needs, identity coercion, or hidden dependency.
- Resource viability: no node recognition if resources, staffing, compute, housing/work dependency, or logistics create capture.
- Topology classification: star-adjacent designs must be redesigned before recognition.
- Anti-capture review: no founder, hub, funder, AI operator, or security function may become unchecked final authority.
- Measurement readiness: no recognition evidence without a Node measurement protocol.
- Rollback readiness: every recognition/scaling decision needs pause, downgrade, and retirement paths.
- Beneficial coordination channel: C09 must distinguish harmful cascade from legitimate rapid coordination.

Future C09 simulation scenarios:

- civilian access pathway,
- corporate feudal node,
- fake autonomy with weak exit,
- AI authority drift,
- security/military capture,
- founder charisma capture,
- rollback failure,
- scaling instability,
- irreversible experiment node,
- access capture,
- beneficial rapid coordination mistakenly suppressed.

## 7. Node Measurement Protocol Requirements

Before Node v0.2 or any pilot-facing claim, write a standalone Node Measurement Protocol.

Minimum requirements:

1. Consent and scope
   - Explicit informed consent for all structured participants.
   - Pause/exit rights.
   - No hidden scoring of humans.
   - Burden limits and sensitive-data exclusions.

2. Variable scoring rubrics
   - T, D, C, I, S, and coupling strength require observable scoring rubrics.
   - `C` scoring must count confusion/contradiction/distorted understanding, not mere disagreement.
   - `S` must remain derived and auditable, not a direct self-report.

3. Raw-to-normalized mapping
   - All unbounded counts and delays require caps.
   - Missing data remains missing.
   - 1-to-5 ratings are bounded ordinal approximations, not interval-validated measurements.

4. Inter-rater logic
   - At least one second rater or reviewer path before any stronger Node v0.2 claim.
   - Disagreements between raters should be logged, not averaged away.

5. Topology context
   - Every row must include active topology, detected topology, topology confidence, subgroup ID, and federation ID if applicable.
   - Federation Trigger A must use C07 `Psi_extended`; non-federation Trigger A may use C04 S-threshold.

6. Privacy and safety
   - No medical, legal, employment, financial, or safety-critical authority.
   - Data minimization and local retention rules.
   - Stop conditions for distress, coercion, missingness, or artifact discovery.

7. Audit outputs
   - Raw logs.
   - Normalized variables.
   - Missingness report.
   - Artifact flags.
   - Trigger-source sanity report.
   - Reviewer notes.
   - Post-test synthesis that separates observed container feasibility from SOE validation.

## 8. Drift Layer Requirements

Status: missing/needed layer. Candidate for the next architecture extension after or alongside C09.

Purpose:

The Drift Layer detects slow deviation from SOE's original constraints, source hierarchy, non-terminal principles, measurement rules, and anti-capture structure. It must distinguish adaptive evolution from corruptive drift.

Required monitored drift types:

| Drift type | Description |
|---|---|
| Ontology drift | T/D/C/I/G/S/Psi terms change meaning without versioned approval. |
| Source-hierarchy drift | Lower-tier documents override frozen architecture or evidence boundaries. |
| Detector drift | `Psi_extended` thresholds, weights, inputs, or authority change without audit. |
| Governance-authority drift | Trigger authority, rollback authority, or audit authority concentrates in one actor. |
| Topology drift | Mesh/federation structures gradually become star-adjacent or hub-dominated. |
| Node-recognition drift | C09 recognition becomes automatic, captured, pay-to-play, or founder-controlled. |
| Exit-right drift | Formal exit remains but practical exit becomes costly, stigmatized, or resource-blocked. |
| Resource-dependency drift | Housing, work, compute, medicine, transport, or funding become capture paths. |
| Memory/archive drift | Historical records, prior versions, or caveats are rewritten or silently lost. |
| Beneficial-change suppression | Stability rules begin blocking legitimate rapid coordination or reform. |

Required Drift Layer mechanisms:

- Drift register with dated entries.
- Versioned ontology ledger.
- Threshold/weight change log for C07 detectors.
- Scheduled source-hierarchy audits.
- Topology reclassification audits.
- Exit-right stress tests.
- Node-recognition fairness and capture audits.
- Archive integrity checks.
- Independent review for major drift findings.
- Rollback or constitutional review path for confirmed corruptive drift.

The Drift Layer must not become a permanent veto authority. It detects, classifies, and routes drift; it does not silently govern the whole system.

## 9. `Psi_extended` Adversarial and Circularity Test Requirements

Current v0.7 fact:

`Psi_extended` works in the locked v0.7 simulation configuration, but CL02A shows material dependence on the stability term.

Upgrade requirement:

Before any pilot or deployment language, `Psi_extended` must be tested against adversarial gaming, corrupted stability signals, delayed measurement, and circularity.

Required tests:

| Test | Purpose |
|---|---|
| Stability clamp test | Run `Psi_extended` when S is externally clamped or partially decoupled from collapse dynamics. |
| Stability spoof test | Inject false-stability signals and measure false negatives. |
| Delayed S test | Delay S updates relative to T/D/C/G changes. |
| Corrupted S test | Add targeted noise or manipulation to S while keeping true collapse dynamics unchanged. |
| Threshold gaming test | Adversary injects D/C pulses designed to stay just below `psi_threshold=0.30`. |
| Moving-average reset test | Adversary times pulses to reset or desynchronize detection windows. |
| Operator capture test | Simulate a `Psi_extended` operator drifting threshold from 0.30 upward, such as 0.35, 0.40, 0.45. |
| Topology misclassification test | Combine stale topology detection with federation detector stress. |
| Independent-signal comparison | Compare `Psi_extended` against detectors that do not use S directly. |
| Holdout matrix test | Run on unseen scenarios/profiles rather than only tuned v0.7 cases. |

Metrics required:

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

Blocked detector claims until these tests pass:

- empirical early-warning detector,
- deployment detector,
- stability-independent detector,
- adversarially robust detector,
- real-world safety monitor.

## 10. Readiness Distinctions

Use the following labels consistently.

| Readiness label | Meaning | Current status |
|---|---|---|
| Architecture-ready | The rules are coherent enough to audit and patch as an architecture. | Yes, for v0.4 plus this upgrade spec. |
| Simulation-ready | A proposed mechanism has an executable simulation spec and matrix. | Yes for C00-C08 Grand Simulation lineage; not yet for C09 or Drift Layer. |
| Simulation-evidence-ready | A simulation has produced reproducible evidence for bounded claims. | Yes for Grand Simulation v0.7 claims only. |
| Container-test-ready | A bounded local logging/audit test can be run without real authority. | Node v0.1 record exists; Node v0.2 requires protocol and consent before expansion. |
| Pilot-ready | Real participants/systems can be tested under formal safeguards. | No. Requires measurement validation, consent, privacy/security controls, stop rules, external review, and governance authority limits. |
| Deployment-ready | A real target context can operate SOE mechanisms with authority. | No. Requires target calibration, legal legitimacy, resources, operational monitoring, rollback paths, external audit, and validated measurement. |

Do not use "ready" without specifying which readiness label applies.

## 11. Governance Architecture Patch List

Patch GA-01: Replace `C (cognition)` with `C (cognitive distortion)` in manuscript v0.7, arXiv metadata, and any architecture summary that drifts.

Patch GA-02: Clarify that `Psi_extended` is a derived C07 detector output, not a primary SOE state variable. If the architecture keeps `Psi(t)` as "meta-governance stress index," distinguish it from T/D/C/I/G/S state variables.

Patch GA-03: Add a Readiness Taxonomy section separating architecture-ready, simulation-ready, simulation-evidence-ready, container-test-ready, pilot-ready, and deployment-ready.

Patch GA-04: Add CL02A caveat near every CL02 claim: `Psi_extended` is stability-heavy in the locked v0.7 configuration.

Patch GA-05: Preserve CL05 as context-dependent hub mitigation only. Three hubs are not mesh equivalence, universal hub safety, or common-mode resilience.

Patch GA-06: Preserve CL09 narrow wording: topology lag can overlap hidden collapse; broad blind/no-trigger false stability was not established.

Patch GA-07: Preserve CL10 narrow wording: resource-stress gradients were measured; recovery under realistic finite resources is not proven.

Patch GA-08: Add C09 as a proposed Node Formation and Recognition Layer, clearly marked not simulation-validated.

Patch GA-09: Add Drift Layer requirements or create a separate candidate layer document, clearly marked missing/needed.

Patch GA-10: Add Node v0.1 firewall language wherever Node evidence is mentioned.

Patch GA-11: Add a Node Measurement Protocol dependency before Node v0.2 or any pilot-facing claim.

Patch GA-12: Add a single notation table preserving `f_min=0.30` and `kappa_min=0.25` as distinct floors.

Patch GA-13: Add collapse/ignition glossary to prevent simulation terms from becoming real-world claims.

Patch GA-14: Fix Node v0.1 completion date typo in the next versioned Node document.

## 12. Meta-Governance Framework Patch List

Patch MG-01: Define who computes, updates, audits, pauses, and overrides `Psi_extended`.

Patch MG-02: Add a threshold/weight change-control process for `Psi_extended`, including independent review and rollback.

Patch MG-03: Add detector-adversary and circularity testing as a required pre-pilot gate.

Patch MG-04: Separate detector authority from intervention authority. The same actor should not own sensing, classification, trigger activation, and rollback.

Patch MG-05: Add rollback/deactivation rules for every trigger. No permanent trigger state without constitutional review.

Patch MG-06: Add meta-governance capture scenarios: operator threshold drift, auditor capture, hub/funder capture, security authority capture, AI authority drift.

Patch MG-07: Add Drift Layer routing: meta-governance receives drift findings but cannot silently become final authority.

Patch MG-08: Add cost/feasibility accounting: compute, staffing, latency, compliance, privacy, and resource overhead.

Patch MG-09: Add beneficial coordination protection. SOE should block harmful cascades without suppressing legitimate rapid reform, emergency coordination, whistleblowing, or lifesaving innovation.

Patch MG-10: Add external review requirement before pilot/deployment claims. Multi-AI review is useful internal red-team work, not independent human-domain validation.

## 13. Blocker List

Hard blockers before pilot-ready language:

1. Measurement protocol missing for Node v0.2 and real-world T/D/C/I/S scoring.
2. Inter-rater and proxy-validation plan missing.
3. `Psi_extended` adversarial/circularity tests not run.
4. Trigger authority, rollback authority, and audit authority not separated.
5. Drift Layer not specified.
6. C09 node recognition gates not specified or simulated.
7. Privacy, consent, data-retention, stop-rule, and human-subject safeguards incomplete.
8. Cost/feasibility layer absent.
9. Topology detection and reclassification operational protocol incomplete.
10. External domain review absent.

Hard blockers before deployment-ready language:

1. All pilot blockers remain unresolved.
2. Target-context calibration missing for T/D/C/I/G/S, thresholds, resources, timescales, and topology.
3. Legal/institutional legitimacy not established.
4. Real-world rollback and deactivation not tested.
5. Resource exhaustion and finite-resource recovery not solved.
6. Governance capture and detector-operator capture not tested.
7. Star-adjacent topology redesign process not operational.
8. Exit rights not proven effective under dependency pressure.
9. Archive/memory drift controls not operational.
10. Independent audit and accountability structures not established.

Public release / reproducibility blocker:

1. Zenodo or public archive linkage for the Grand Simulation v0.7 evidence package must be verified and preserved in release metadata before any public v0.5 release packet. This is a traceability requirement only; it does not convert v0.7 simulation evidence into pilot, deployment, or validation evidence.

Non-blockers for this upgrade spec:

- No v0.8 Grand Simulation is required merely to begin the upgrade specification.
- Node v0.1 can remain a bounded real-world container record.
- Trinity/Unification materials can inform C09 but do not need to be accepted as doctrine.
- The v0.7 paper/preprint package can remain closed as long as its caveats are preserved.

## 14. Recommended Work Order

1. Freeze this v0.1 upgrade spec for multi-AI review.
2. Create `SOE_Governance_Architecture_Ontology_Readiness_Patch_v0_1.md`.
3. Create `SOE_C09_Node_Formation_and_Recognition_Layer_v0_1.md`.
4. Create `SOE_Node_Measurement_Protocol_v0_1.md`.
5. Create `SOE_Drift_Layer_Requirements_v0_1.md`.
6. Create `SOE_Psi_Extended_Adversarial_Test_Spec_v0_1.md`.
7. Only after those specs are reviewed, patch the Governance Architecture and Meta-Governance Framework.

## 15. Reviewer Questions

Ask reviewers to answer:

1. Does this spec preserve the evidence boundary between simulation evidence, Node container evidence, pilot readiness, and deployment readiness?
2. Is the ontology cleanup complete, especially `C`, `Psi_extended`, `f_min`, and `kappa_min`?
3. Is C09 scoped as a proposed layer rather than a validated mechanism?
4. Are the Node measurement requirements sufficient before v0.2?
5. Are the Drift Layer requirements strong enough to prevent silent terminal drift?
6. Are the `Psi_extended` adversarial/circularity tests sufficient to answer the stability-dependence critique?
7. Which blockers must be resolved before the Governance Architecture v0.5 patch?
