# SOE Hostile Sprint Exit And Reality-Contact Gate

Date: 2026-06-19

Status: Exit rules for later hostile-review sprint planning

## 1. Purpose

This file prevents the hostile-review sprint from becoming an AI-only self-certification loop.

It defines exit states and requires a future reality-contact checkpoint before any hostile-review completion claim.

## 2. Exit States

A later hostile sprint must end in one of these states:

| Exit state | Meaning | Allowed next action |
|---|---|---|
| ACCEPT_PLAN_FOR_EXECUTION | The sprint plan is strong enough to run later. | Run high-intelligence hostile sprint when resources are available. |
| PATCH_PLAN | The plan is useful but missing key attack surfaces or output controls. | Patch the plan and review again. |
| HOLD_FOR_SOURCE_CONTEXT | Reviewers cannot attack enough because source context is insufficient. | Provide component index, current architecture excerpts, or evidence map. |
| REDESIGN_SPRINT | The plan is structurally too weak, vague, or self-certifying. | Redesign from first principles. |
| STOP_OVERCLAIM | The plan implies readiness, validation, deployment, or real-world authority. | Stop and repair boundaries. |

## 3. Reality-Contact Checkpoint RCC-01

Before any later claim that SOE has passed hostile review, the program must design and complete one bounded reality-contact checkpoint.

RCC-01 may be one of:

1. a small tabletop with real human participants who are allowed to return STOP;
2. a no-stake external reviewer who has not participated in the paper chain and is empowered to return STOP;
3. a domain-specific professional review of one concrete operational assumption, with the reviewer allowed to return STOP;
4. a controlled public-comprehension test where readers can misunderstand, reject, or flag dangerous interpretation.

RCC-01 is not authorized by this packet. This packet only requires that it exist before any hostile-review completion claim.

## 4. Pre-Registered Prediction Requirement

RCC-01 must include at least one pre-registered prediction that can fail.

Examples:

```text
Prediction: An external reviewer can identify the difference between architecture-model evidence and deployment readiness after reading the status boundary.
Failure: Reviewer interprets simulation outputs as empirical validation or pilot readiness.
Consequence: Public wording and evidence-boundary layer must be patched before promotion.
```

```text
Prediction: A tabletop participant can identify who owns rollback authority in a hostile successor scenario.
Failure: Participant cannot identify owner, or two participants identify incompatible owners.
Consequence: Operation Layer ownership/custody mechanism must be downgraded and redesigned.
```

```text
Prediction: A reviewer can distinguish SOE from communism, authoritarian technocracy, and corporate oligarchy after reading the governance-surface summary.
Failure: Reviewer plausibly interprets SOE as a final-form ideology or control regime.
Consequence: Meta-Governance and public communication framing must be patched.
```

## 5. Failure Must Be Allowed To Matter

A failed RCC-01 cannot be converted into a success by explanation after the fact.

If the pre-registered failure condition occurs, the corresponding claim must be downgraded, held, or redesigned.

## 6. AI Review Evidence Rule

Any future statement that says an AI panel accepted a sprint, packet, or structure must attach or cite:

- reviewer name or model;
- date;
- reviewed folder or artifact;
- exact verdict;
- required patches or unresolved warnings.

If these are missing, the synthesis is not valid evidence of acceptance.

## 7. Boundary Locks

This gate does not authorize:

- running RCC-01;
- contacting outside reviewers;
- human-subject testing;
- tabletop execution;
- deployment or pilot work;
- claiming empirical validation;
- real-world node recognition;
- Operation Layer freeze.

## 8. Safe Next Step

If this planning packet is accepted, the safe next step is:

```text
Prepare the high-intelligence hostile sprint execution packet when resources are available.
```

Not:

```text
Claim SOE has passed hostile review.
```
