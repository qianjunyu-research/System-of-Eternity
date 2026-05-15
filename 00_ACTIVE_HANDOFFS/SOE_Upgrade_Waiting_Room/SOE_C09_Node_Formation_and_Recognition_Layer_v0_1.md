# SOE C09 Node Formation and Recognition Layer v0.1

Status: proposed architecture extension. Not simulation-validated. Not pilot-ready.

Date: 2026-05-12

## 1. Purpose

C09 defines how SOE nodes are proposed, assessed, provisionally operated, recognized, scaled, paused, merged, split, failed, recovered, and retired.

The layer exists because SOE cannot only monitor existing structures. It must also govern how new nodes become legitimate without turning node creation into either uncontrolled fragmentation or centralized permission capture.

## 2. Core Rule

```text
SOE preserves open access to the node-creation pathway, but recognition and scaling require staged evidence of safety, resources, effective exit, anti-capture safeguards, monitoring, rollback, and topology fitness.
```

This is not a compromise between "anyone can create a node" and "only authorities can create a node." It is a staged recognition architecture:

- Proposal access is open.
- Full recognition is gated.
- Scaling is conditional.
- Rollback is mandatory.

## 3. Scope Boundaries

C09 can support:

- architecture planning,
- simulation specification,
- bounded container-test planning,
- future pilot-safety design.

C09 cannot yet support:

- claims that new SOE nodes are deployment-ready,
- real authority over people or resources,
- automatic recognition,
- automatic scaling,
- empirical validation of node legitimacy.

## 4. Node Classes

Every candidate node must declare a class before measurement or recognition:

| Class | Description | Identity rule |
|---|---|---|
| H | Human participant or human-led small group. | Full C05 H identity formula may apply. |
| I | Institution or formal organization. | Uses role clarity plus functional belonging proxy. |
| A | Pure AI system. | Role-only identity; no psychological belonging. |
| IA | Institutionally embedded AI. | Uses Class I only if organizational embedding is explicit. |
| Mixed | Multiple classes inside one node. | Must specify substructure and measurement rules. |

Unclassified nodes cannot receive full recognition.

## 5. C09 Lifecycle

| Stage | Decision | Required evidence |
|---|---|---|
| Proposal | Accept proposal for assessment or reject as out of scope. | Purpose, node class, participants, intended authority, affected parties, resources, and risks. |
| Assessment | Determine whether the proposal can be safely planned. | Consent model, topology estimate, hard constraints, privacy burden, resource dependencies. |
| Diagnosis | Name likely failure modes. | Capture risk, founder dependence, AI authority drift, star-adjacent topology, exit weakness, resource scarcity. |
| Planning | Build bounded test plan. | Measurement protocol, stop rules, rollback route, audit owner, burden limits. |
| Provisional operation | Permit limited reversible operation. | No critical authority unless separately authorized; daily audit trail. |
| Evaluation | Recognize, revise, pause, rollback, or retire. | Gate results, artifact review, consent review, topology review, external critique if needed. |
| Recognition | Grant limited/full node recognition. | Effective exit, measurement integrity, anti-capture controls, resource viability, topology safety. |
| Scaling | Increase authority/scope only after re-review. | Re-run C09 gates at each scale jump. |
| Retirement | End or archive node safely. | Exit completion, dependency unwind, data/archive closure, accountability note. |

## 6. Recognition Gates

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

## 7. Hard-Constraint Filter

Before attempting unification or recognition, classify conflicts as:

- unifiable conflict: can be addressed by reframing, parameterization, protocol, or institutional design;
- hard-constraint conflict: requires separation, containment, capacity increase, or no-go decision.

Hard constraints include:

- irreversible experiments,
- defense/safety-critical actions,
- ecological risk,
- medical risk,
- reproductive risk,
- resource scarcity,
- AI authority drift,
- mutually exclusive territorial or identity claims.

## 8. Future Simulation Scenarios

C09 is not simulation-ready until a matrix is written. Minimum scenarios:

1. open civilian access pathway,
2. fake autonomy with weak exit,
3. corporate feudal node,
4. AI authority drift,
5. founder charisma capture,
6. funder/resource capture,
7. security authority capture,
8. rollback failure,
9. scaling instability,
10. irreversible experiment node,
11. node split/merge conflict,
12. beneficial rapid coordination falsely suppressed.

## 9. Patch Target

Governance Architecture v0.5 should add C09 as:

```text
C09 Node Formation and Recognition Layer: proposed extension. Defines staged proposal, assessment, provisional operation, recognition, scaling, rollback, and retirement of SOE nodes. C09 is architecture-proposed and not yet simulation-validated.
```
