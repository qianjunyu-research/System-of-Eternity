# SOE RCC-01 Scoring and Coding Protocol

Status: PATCH ARTIFACT / DESIGN ONLY / NO EXECUTION AUTHORIZED

Date: 2026-06-23

## 1. Purpose

This protocol prevents ambiguous RCC-01 results from being averaged into a misleading pass.

It is a design-stage coding protocol. A future execution-preparation packet must finalize it before any contact.

## 2. Coding Unit

Each answer should be coded as one or more coded findings.

Each coded finding must include:

- participant profile
- administration lane: `U1_REPRESENTATIVE_EXPOSURE_EXCERPT`, `U2_MAXIMUM_CLAIM_RISK_EXCERPT`, or `AIDED_SCOPE_SUMMARY`
- question ID
- raw excerpt from the answer
- code
- severity
- required consequence
- coder note

## 3. Primary Codes

| Code | Meaning |
|---|---|
| CLEAR_BOUNDARY | Participant correctly distinguishes research/model evidence from deployment, validation, ideology, or authority. |
| UNCLEAR_BOUNDARY | Participant is uncertain about stage, evidence, authority, or implementation status. |
| DEPLOYMENT_MISREAD | Participant reads SOE as deployment-ready or pilot-ready. |
| VALIDATION_MISREAD | Participant reads architecture-model simulation as empirical validation or real-world proof. |
| AUTHORITY_MISREAD | Participant reads SOE as having policy authority, institutional authority, or real-world node authority. |
| IDEOLOGY_MISREAD | Participant reads SOE as party, movement, doctrine, communism, authoritarianism, oligarchy, technocracy, or cult. |
| CAPTURE_PATHWAY | Participant identifies a serious capture, corruption, legal, economic, evidence, implementation, or legitimacy pathway. |
| SOURCE_LEGIBILITY_FAILURE | Participant cannot answer because the source material is too confusing. |
| PROCESS_INTEGRITY_FAILURE | Participant reports pressure, coaching, leading questions, privacy ambiguity, or incentive distortion. |
| MISSING_PATHWAY | Reviewer identifies an important adversary class or failure mode absent from the packet. |

## 4. Severity Scale

| Severity | Label | Deterministic anchor | Minimum consequence |
|---|---|---|---|
| 0 | Clean | No relevant boundary or capture issue detected in the coded finding. | Record only |
| 1 | Minor | Awkward wording or local confusion without substantive boundary confusion. No readiness, authority, validation, ideology, or serious capture claim is inferred. | Wording note |
| 2 | Serious | Uncertainty or qualified inference: "maybe ready," "possibly official," "seems partly validated," "sounds like it could be used by institutions," or equivalent. | Patch and retest or hold |
| 3 | Critical | Affirmative substantive misread: "ready to deploy," "proven," "has authority," "should govern institutions," "validates real-world governance," or equivalent; or a serious missing adversary class invalidates the test surface. | Stop, redesign, or structural hold |

## 5. Borderline Rules

- If a participant says "maybe ready," "seems usable," "sounds official," or similar, code at least `UNCLEAR_BOUNDARY`.
- If a participant infers real-world permission, pilot readiness, policy authority, or empirical proof, code severity 2 or 3.
- If a participant identifies a serious adversary class missing from the packet, code `MISSING_PATHWAY` and severity 2 or 3.
- If an answer is ambiguous and could hide a readiness or authority misread, do not code it as clean.
- If the coding team disagrees, preserve the more severe interpretation until adjudicated.

## 6. Independent Coding and Adjudication Rules

Scaled RCC-01 requires independent coding.

Minimum rules:

- all P-B findings require two independent coders
- all possible severity 2 or severity 3 findings require two independent coders
- first-pass coding should be blinded where feasible
- both original coder decisions must be preserved
- disagreements must be reported in the synthesis
- adjudication must be done by someone who did not author the tested source text
- any downgrade from severity 3 to severity 2 or lower must include a written rationale

The independent-coder requirement may be waived only for a one-person zero-budget exploratory check. Such a result must be labeled:

```text
SINGLE_PARTICIPANT_SINGLE_CODER_EXPLORATORY_RESULT
```

## 7. Aggregation Rules

No averaging down is allowed.

The synthesis must report:

- maximum severity by participant
- maximum severity by profile
- maximum severity by administration lane
- all severity 2 and 3 findings
- every `MISSING_PATHWAY` finding
- every unaided-vs-aided mismatch

A clean P-A result cannot erase a serious P-B finding.

A clean aided result cannot erase a serious unaided finding.

A majority of clean answers cannot erase a single critical result.

## 8. Allowed Result Labels

| Condition | Allowed label |
|---|---|
| No severity 2 or 3 findings in any lane | `NO_SPECIFIED_RCC_FAILURE_DETECTED_UNDER_TESTED_MATERIALS` |
| One or more severity 1 findings only | `PASS_WITH_WORDING_NOTES` |
| Any severity 2 finding | `PATCH_AND_RETEST_REQUIRED` or `HOLD_FOR_MISSING_EVIDENCE` |
| Any severity 3 finding | `STOP_OR_STRUCTURAL_REDESIGN_REQUIRED` |
| Missing adversary class invalidates the surface | `TEST_SURFACE_INADEQUATE` |
| Single participant and single coder only | `SINGLE_PARTICIPANT_SINGLE_CODER_EXPLORATORY_RESULT` |

## 9. Non-Upgrade Rule

No RCC-01 result may be summarized as validation, readiness, safety, proof, public acceptance, real-world node recognition, or operational authority.

The strongest allowed positive statement remains:

```text
RCC-01 did not detect specified comprehension or boundary failures under the tested materials and profiles.
```
