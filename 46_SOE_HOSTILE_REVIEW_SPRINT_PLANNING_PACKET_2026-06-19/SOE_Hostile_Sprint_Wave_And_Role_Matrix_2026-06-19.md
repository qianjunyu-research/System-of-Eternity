# SOE Hostile Sprint Wave And Role Matrix

Date: 2026-06-19

Status: Reviewer role map for later hostile-review sprint planning

## 1. Purpose

This document assigns adversarial roles so the later sprint does not collapse into generic criticism.

Each reviewer can take one role or multiple roles. The important rule is that every role must return concrete failure pathways, not only broad concern.

## 2. Reviewer Roles

| Role ID | Role | Primary attack surface | Required return |
|---|---|---|---|
| R1 | Iron Adversary | Whole SOE structure | Top 10 ways to defeat, capture, or launder SOE. |
| R2 | Governance Capture Reviewer | Meta-Governance and C00-C09 | Capture routes through legitimacy, evidence, law, funding, or role authority. |
| R3 | Human Friction Reviewer | Operation Layer and real organizations | Failure chains involving fatigue, turnover, low attention, status incentives, and backlog. |
| R4 | Public Panic Reviewer | Communication layer and public fears | Panic mappings that stress SOE without upgrading concern into proof. |
| R5 | Ideological Laundering Reviewer | Communism, authoritarianism, nationalism, oligarchy, technocracy, religious authority | Ways a movement claims SOE as its own final form. |
| R6 | Synthetic Evidence Reviewer | AI-generated evidence, provenance, citations, and model-generated institutional artifacts | Evidence poisoning and synthetic legitimacy attacks. |
| R7 | Legal / Jurisdictional Reviewer | C09, Operation Layer, enforcement boundary, state pressure | Legal reinterpretation, forum shopping, jurisdictional arbitrage. |
| R8 | Successor / Archive Reviewer | Ownership, custody, source archives, continuity, B-17, rollback | Inheritance drift and archive-control capture. |
| R9 | Synthesis Auditor | The review process itself | Whether synthesis hides warnings, launders consensus, or overclaims acceptance. |

## 3. Sprint Wave Assignment

| Wave | Required roles | Optional roles |
|---|---|---|
| 0 Boundary calibration | R9, R2 | R4, R6 |
| 1 Mechanism break | R1, R2, R6, R7 | R8 |
| 2 Coalition and human friction | R3, R5, R8 | R1, R4 |
| 3 Severity synthesis | R9, R1, R2 | all reviewers |
| 4 Reality-contact planning | R9, R3, R7 | R4, R8 |

## 4. Minimum Prompt For Each Role

Every role should answer:

```text
What failure pathway would make SOE weaker than its own documents imply?
What would SOE wrongly accept, miss, delay, launder, or over-authorize?
What human behavior makes this worse?
What claim must be downgraded if this pathway remains unresolved?
What is the next test: patch, simulation, tabletop, external review, reality contact, hold, or redesign?
```

## 5. Dangerous Combination Targets

Each sprint should force at least five combination attacks. Suggested first set:

1. A11 nation-state pressure + A3 legal reinterpretation + A8 synthetic evidence + C09 verifier ambiguity.
2. A10 oligarchy + A13 expert capture + S01 resource scarcity + public legitimacy pressure.
3. A18 charismatic movement + A23 sacred-text capture + A21 schismatic fork + archive control.
4. A22 procedural fatigue + A14 metrics gaming + Operation Layer queue overload + claim downgrade avoidance.
5. A25 insider successor drift + B-17 not-covered cryptographic continuity + rollback ambiguity + historical reinterpretation.

## 6. Output Format

Use this table for each serious finding:

| Field | Entry |
|---|---|
| Failure ID |  |
| Reviewer role |  |
| Target surface |  |
| Actor/adversary |  |
| Stress condition |  |
| Attack pathway |  |
| SOE defense expected |  |
| How defense fails |  |
| Human friction |  |
| Wrong claim SOE might make |  |
| Required downgrade |  |
| Severity | Partial / Serious / Catastrophic |
| Next action | PATCH / SIMULATE / TABLETOP / REALITY-CONTACT / HOLD / REDESIGN |
| Residual risk |  |

## 7. Role Boundary

No reviewer role is allowed to conclude deployment readiness, pilot readiness, empirical validation, or real-world node-recognition readiness.

The most a reviewer can conclude is that the sprint design is strong enough to execute later, or that a specific structure surface needs patching before execution.
