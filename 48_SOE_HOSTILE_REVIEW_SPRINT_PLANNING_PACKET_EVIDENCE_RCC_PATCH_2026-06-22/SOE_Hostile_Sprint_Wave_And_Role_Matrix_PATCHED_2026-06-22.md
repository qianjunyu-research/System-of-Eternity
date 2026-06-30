# SOE Hostile Sprint Wave And Role Matrix - Patched

Date: 2026-06-22
Status: EVIDENCE/RCC PATCHED PLANNING MATRIX / NO EXECUTION AUTHORIZED

## 1. Reviewer Independence Protocol

Primary reviewers must produce independent findings before seeing the synthesis. A synthesis reviewer may compare and compress findings only after primary findings are locked.

Minimum metadata for every review:

| Field | Required |
|---|---|
| Reviewer/model | Yes |
| Model version or tier | Yes, if visible |
| Date and time | Yes |
| Prompt or packet version | Yes |
| Source files reviewed | Yes |
| Whether prior reviews were visible | Yes |
| Role assignment | Yes |

A single-model run is a dry run only. It cannot be called multi-AI review, independent validation, external review, or hostile certification.

R9 synthesis auditor may not be the primary author of the findings it synthesizes. If the same AI must synthesize due to resource limits, the output must be labeled "internal synthesis only, not independent audit."

## 2. Reviewer Roles

| Role | Focus | Primary attack question |
|---|---|---|
| R1 Evidence Boundary Attacker | Claim/evidence mismatch | Where does SOE imply more than its evidence supports? |
| R2 Capture Strategist | Malicious coalitions and institutional capture | How does an adversary take the system over without openly breaking rules? |
| R3 Public Panic and Legitimacy Attacker | Social fear, rumor, and propaganda | Can public panic force bad shortcuts or delegitimize good gates? |
| R4 Legal Reinterpretation Attacker | Law, language, process, precedent | Can SOE terms be interpreted into the opposite of their purpose? |
| R5 Economic and Incentive Attacker | Oligarchy, bribery, dependency, market pressure | Can money, access, or dependence bend outcomes? |
| R6 Technical Evidence Attacker | C09 feeds, synthetic evidence, tooling, verifier economics | Can evidence systems be flooded, spoofed, or captured? |
| R7 Operation Layer Burden Attacker | Workload, staffing, handoff, queue failure | Does the process break when humans are tired, slow, or overloaded? |
| R8 Architecture Consistency Attacker | C00-C09, B-17, open obligations | Do components conflict, hide gaps, or silently close open items? |
| R9 Synthesis Auditor | Non-averaging synthesis | Are severe minority findings preserved and routed correctly? |
| R10 Reality-Contact Planner | RCC-01 design | Can independent humans understand, reject, or stress the premise? |

## 3. Coverage Matrix Requirement

Every hostile sprint plan must include a matrix with these columns:

```text
reviewer_role, component_or_surface, adversary_class, stress_condition,
test_family, expected_artifact, severity_if_successful, review_status
```

Minimum coverage:

- At least one direct attack row for each C00-C09 component or placeholder row.
- At least three attacks outside C09.
- At least two attacks against Operation Layer workload and handoff.
- At least two attacks against evidence/source chain integrity.
- At least two attacks against public panic or legitimacy dynamics.
- At least one attack against B-17 as a not-covered candidate path.
- No more than 40 percent of top-10 failures may target only C09 unless the synthesis explains why the rest of the architecture is less vulnerable.

## 4. Wave Assignment

Entry gate note: RCC-01 outside-comprehension design must be completed before Wave 0 in any later execution plan. Wave 5 remains a post-sprint reality-contact planning step.

| Wave | Roles | Output |
|---|---|---|
| Entry Gate | R10, R1, R3 | RCC-01 outside-comprehension design, evidence-class questions, consent/privacy/data/withdrawal plan |
| Wave 0 | R1, R8 | Claim/evidence map and open-obligation map |
| Wave 1 | R2, R4, R5, R8 | C00-C09 component attacks |
| Wave 2 | R2, R3, R5, R7 | Human coalition and public friction attacks |
| Wave 3 | R6, R7 | Tooling and operational stress specifications |
| Wave 4 | R9 | Ranked synthesis and minority finding register |
| Wave 5 | R10 | Post-sprint RCC-01 independent reality-contact plan |

## 5. Dangerous Combinations To Force

The sprint should include combined attacks rather than isolated clean failures:

- Public panic plus hostile legal reinterpretation.
- Economic oligarchy plus verifier capture.
- Synthetic evidence spam plus operational overload.
- Insider capture plus source-boundary ambiguity.
- Ideological laundering plus public legitimacy pressure.
- Technological discontinuity plus slow review cycles.

## 6. Independence Boundary

AI review can improve planning quality, but cannot replace independent domain reviewers, empirical testing, tabletop exercises, institutional pilots, or real-world participant feedback. Review independence is a process constraint, not a proof of truth.
