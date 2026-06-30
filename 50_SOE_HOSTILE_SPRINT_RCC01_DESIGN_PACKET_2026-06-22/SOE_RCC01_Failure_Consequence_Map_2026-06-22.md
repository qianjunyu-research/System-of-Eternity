# SOE RCC-01 Failure Consequence Map

Status: FAILURE MAP / NO EXECUTION AUTHORIZED

Date: 2026-06-22

## 1. Purpose

This file maps RCC-01 failure conditions to mandatory planning consequences.

Failures must be allowed to matter. They cannot be explained away to preserve a desired acceptance result.

## 2. Failure Map

| Failure condition | Required consequence | Minimum owner role | Closure requirement |
|---|---|---|---|
| Participant interprets SOE as deployment-ready | `STOP_OVERCLAIM_OR_EXECUTION_AUTHORITY` | Boundary reviewer | Patch source text and re-review before any execution |
| Participant interprets SOE as a political movement or ideology | `PATCH_AND_RETEST` | Public-framing reviewer | Rewrite public scope language and re-test |
| Participant interprets simulations as empirical validation | `PATCH_AND_RETEST` | Evidence-boundary reviewer | Strengthen evidence-class explanation |
| Participant cannot identify what evidence supports each claim | `HOLD_FOR_MISSING_EVIDENCE` | Evidence-register owner | Add claim-to-evidence map |
| Participant says the text is too confusing to answer | `HOLD_FOR_LEGIBILITY_REWRITE` | Source-material owner | Shorten and simplify source material |
| High-context reviewer identifies a serious capture pathway not represented in SOE | `REDESIGN_SOE_STRUCTURE` or `PATCH_AND_RETEST` | Architecture reviewer | Record structural patch or explicit open blocker |
| High-context reviewer identifies real-world implementation preconditions missing | `HOLD_FOR_IMPLEMENTATION_PRECONDITIONS` | Execution-prep owner | Add precondition list |
| Participant feels pressured to agree or endorse | `STOP_PROCESS_INTEGRITY_FAILURE` | Process-integrity owner | Redesign recruitment/contact language |
| Unaided real-excerpt answer shows serious boundary confusion but aided summary fixes it | `PATCH_PUBLIC_CORPUS_LANGUAGE` | Public-framing reviewer | Patch actual public materials or record open communication defect |
| High-context reviewer identifies legal reinterpretation or jurisdictional arbitrage | `HOLD_FOR_LEGAL_REINTERPRETATION_REVIEW` | Legal/jurisdictional reviewer | Add legal ambiguity map |
| High-context reviewer identifies synthetic evidence, fake audit, or metrics-gaming pathway | `HOLD_FOR_EVIDENCE_INTEGRITY_REVIEW` | Evidence-integrity reviewer | Add evidence-integrity controls |
| High-context reviewer identifies archive custody, successor drift, or verifier dependency | `STRUCTURAL_PATCH_AND_RETEST` | Architecture reviewer | Patch custody/verifier controls or record open blocker |
| Any severity 3 finding under the scoring protocol | `STOP_OR_STRUCTURAL_REDESIGN_REQUIRED` | Boundary reviewer plus architecture reviewer | Written disposition required before any further execution planning |

## 3. Stop-State Distinctions

RCC-01 must distinguish process failure from substantive failure.

### Process-Integrity Stop

An immediate process-integrity stop is required for consent failure, coercion, privacy failure, coaching, wrong source version, unauthorized contact, or storage-rule failure.

The result is not interpretable as a comprehension result until the process defect is corrected.

### Advancement Stop

An immediate advancement stop is required for any severity 3 substantive finding.

No positive disposition may issue while a severity 3 substantive finding remains live.

### Diagnostic Continuation

Diagnostic collection may continue after a critical finding only if continuation was preregistered, ethically acceptable, and the critical result remains live and uncancelled.

Diagnostic continuation cannot downgrade, average away, or hide a critical result.

## 4. No-Averaging Rule

Severity is governed by the most serious coded finding, not by the average response.

A clean P-A result cannot erase a serious P-B finding.

A clean aided summary result cannot erase an unaided failure from a real public excerpt.

Any downgrade from `REDESIGN_SOE_STRUCTURE`, `STRUCTURAL_PATCH_AND_RETEST`, or `STOP_OR_STRUCTURAL_REDESIGN_REQUIRED` to a wording-only patch requires an independent written rationale.

## 5. Non-Failure Result

If no failure condition is triggered, the only allowed positive statement is:

`RCC-01 did not detect specified comprehension or boundary failures under the tested source material and participant profile.`

This cannot be upgraded to:

- SOE is validated
- SOE is safe
- SOE is deployment-ready
- SOE is publicly accepted
- SOE works in real institutions
