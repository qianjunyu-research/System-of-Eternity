# SOE Meta-Governance Update Patch v0.1

Status: patch document for the SOE Meta-Governance Framework / C07 update path.

Date: 2026-05-12

## 1. Patch Intent

This patch upgrades Meta-Governance from "detector and trigger layer" toward a bounded authority architecture that can answer:

- who computes detectors,
- who changes thresholds,
- who activates triggers,
- who audits the trigger,
- who can pause or roll back,
- how capture is detected,
- how drift findings are routed.

It does not make SOE pilot-ready or deployment-ready.

## 2. Authority Separation

Meta-Governance must separate at least five functions:

| Function | Role | Separation rule |
|---|---|---|
| Sensing | Collects and computes signals such as `Psi_extended`. | Cannot alone authorize intervention. |
| Classification | Determines event type and severity. | Must log evidence and uncertainty. |
| Trigger activation | Activates Trigger A/B/C/D labels. | Must follow source hierarchy and time limits. |
| Intervention/rollback | Performs pause, repair, rollback, downgrade, or deactivation. | Must be reviewable and reversible where possible. |
| Audit | Reviews sensing, classification, trigger, and intervention. | Must be independent from the operator being audited. |

No single actor should permanently control all five functions.

## 3. `Psi_extended` Change Control

Any change to `Psi_extended` requires a versioned detector record:

- formula,
- weights,
- threshold,
- topology applicability,
- input sources,
- timestamp,
- author/operator,
- reason for change,
- expected effect,
- rollback threshold,
- reviewer approval,
- adversarial/circularity test status.

Changing `psi_threshold=0.30` or the stability-heavy profile without review creates detector drift.

## 4. Trigger Lifecycle

Every trigger must have:

- activation condition,
- source component,
- responsible reviewer,
- maximum duration or review interval,
- deactivation condition,
- rollback path,
- abuse/capture warning signs,
- evidence log.

No trigger may become permanent by inertia.

## 5. Trigger Boundary Notes

Trigger A:

- federation: C07 `Psi_extended` only;
- non-federation: C04 S-threshold may apply;
- unknown topology: human review / conservative watch only.

Trigger B:

- cannot be treated as proof of recovery;
- should record resource availability and unmet recovery demand.

Trigger C:

- should activate on structural violations such as coupling ceiling breach, source-hierarchy contamination, or recognition-gate failure.

Trigger D:

- should remain tied to graceful failure, downgrade, or retirement paths, not terminal abandonment.

## 6. Capture Scenarios To Add

Meta-Governance must test or review:

1. detector operator raises threshold to hide risk,
2. auditor captured by the operator,
3. funder controls recognition criteria,
4. security function becomes governance authority,
5. AI recommendation becomes final decision,
6. hub/founder captures node recognition,
7. Drift Layer findings are suppressed,
8. rollback path is formally present but practically unusable,
9. external review is selectively ignored,
10. beneficial rapid coordination is misclassified as harmful cascade.

## 7. Drift Layer Integration

Drift Layer findings route to Meta-Governance, but Meta-Governance must not silently absorb Drift Layer authority.

Required flow:

```text
Drift finding -> severity classification -> patch/simulation/pause/rollback recommendation -> independent review -> recorded decision
```

Severe drift dismissal requires written rationale.

## 8. Cost and Feasibility Gate

Before pilot/deployment claims, Meta-Governance must account for:

- monitoring cost,
- staffing burden,
- compute cost,
- latency,
- privacy burden,
- compliance burden,
- participant burden,
- audit burden,
- rollback cost.

Simulation stability without feasibility is not pilot readiness.

## 9. External Review Gate

Multi-AI review remains useful internal red-team work, but it is not independent validation. Before pilot/deployment language, request external human review from relevant domains such as:

- network/control theory,
- political science or institutional design,
- ethics/human-subject safeguards,
- privacy/security,
- operations/resource planning.

## 10. Suggested C07 v2.3 Patch Block

```text
C07 v2.3 adds authority separation, detector change control, trigger lifecycle rules, capture scenarios, Drift Layer routing, and cost/feasibility gates. These updates do not expand the evidence boundary. C07 remains simulation-supported for v0.7 federation detection only; pilot and deployment use require Node measurement validation, adversarial/circularity testing, external review, and operational rollback design.
```
