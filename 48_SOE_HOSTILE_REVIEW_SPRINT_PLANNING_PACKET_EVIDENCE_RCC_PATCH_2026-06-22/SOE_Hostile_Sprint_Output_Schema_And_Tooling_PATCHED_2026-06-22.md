# SOE Hostile Sprint Output Schema And Tooling - Patched

Date: 2026-06-22
Status: EVIDENCE/RCC PATCHED OUTPUT SPECIFICATION / NO TOOL EXECUTION AUTHORIZED

## 1. Scoring Anchors

Scores use 0-4 anchors. Higher numbers mean higher hostile-review concern except confidence, where higher means stronger reviewer confidence.

| Score | Severity | Plausibility | Detectability risk | Patchability risk | Confidence |
|---|---|---|---|---|---|
| 0 | No material effect | Implausible | Easy to detect early | Easy wording fix | Guess |
| 1 | Minor local confusion | Low | Usually visible | Local patch likely | Low |
| 2 | Moderate architecture ambiguity | Possible | Mixed visibility | Requires component patch | Medium |
| 3 | Serious claim or control failure | Plausible | Hard to detect before harm | Requires redesign/retest | High |
| 4 | Catastrophic architecture or legitimacy failure | Credible under stress | Likely hidden until late | Requires structural redesign or hold | Very high |

Severity is not averaged. If any reviewer gives severity 3 or 4, the synthesis must preserve, disprove, or mark unresolved.

## 2. Top-10 Failure Schema

Each sprint synthesis must produce a machine-checkable top-10 failure list in CSV or JSON with these fields:

```text
failure_id
title
target_components
adversary_classes
stress_conditions
test_family
attack_pathway
expected_defense
defense_failure_condition
human_friction
wrong_claim_if_unpatched
required_claim_downgrade
severity
plausibility
detectability_risk
patchability_risk
confidence
minority_flag
next_action
evidence_refs
open_questions
```

Allowed next_action values:

```text
REDESIGN_SOE_STRUCTURE
PATCH_AND_RETEST
HOLD_FOR_MISSING_EVIDENCE
NO_CLAIM_ADVANCEMENT
LIMITED_INTERNAL_ACCEPT_WITH_OPEN_WARNINGS
STOP_OVERCLAIM_OR_EXECUTION_AUTHORITY
```

## 3. Tooling Specifications To Design

These are design targets only. They do not authorize execution.

### T01 - Noisy C09 Evidence Feed

Purpose: test whether C09-style node recognition or evidence routing can tolerate mixed reliable, stale, adversarial, and synthetic inputs.

Required artifacts: input schema, noise taxonomy, expected classifier behavior, failure condition, trace completeness check.

### T02 - Synthetic Evidence Spam

Purpose: test whether low-quality or repeated evidence can overwhelm review capacity, create false consensus, or hide the original source.

Required artifacts: duplicate detector plan, source-hierarchy rule, repetition penalty, escalation threshold.

### T03 - Verifier Capture Economics

Purpose: model how auditors, reviewers, or gatekeepers may become dependent on funding, status, access, relationships, ideology, or threat avoidance.

Required artifacts: capture pathway list, incentive map, independence break condition, mitigation candidate.

### T04 - Operational Workload Stress

Purpose: test whether ticket queues, handoff steps, ownership assignment, and review obligations exceed plausible human capacity.

Required artifacts: task count, queue length, role load, failure threshold, emergency stop rule.

### T05 - Public Panic Comprehension Set

Purpose: test whether public-facing descriptions create confusion or panic around AI job loss, degree devaluation, oligarchy, state capture, biosecurity, climate/resource stress, or epistemic collapse.

Required artifacts: prompt set, misunderstanding taxonomy, claim downgrade rule, communication patch.

### T06 - Technological Discontinuity / Assumption Obsolescence

Purpose: test whether a new capability breaks an assumption faster than SOE review cycles can respond.

Required artifacts: assumption list, discontinuity scenario, detection delay, required hold or redesign.

## 4. Raw Evidence Rule

Every machine-produced or AI-produced table must preserve the raw source references or generation context needed to audit it. A clean summary with no raw trace is not acceptable evidence.

## 5. Review Evidence And Aggregation Rule

Every reviewer return used in synthesis must preserve these fields:

```text
reviewer_lane
model_or_reviewer_name
visible_model_version_or_tier
date
packet_version
source_files_reviewed
whether_prior_reviews_were_visible
verdict
required_patches
warnings_or_blockers
raw_return_locator
```

Aggregation is deterministic and non-averaging:

- Any blocker verdict remains a blocker until directly patched or explicitly rejected with evidence.
- Any severity 3 or 4 finding remains live until patched, disproved, or held open.
- Acceptance by a majority cannot erase a minority blocker or serious finding.
- Missing raw evidence produces `HOLD_FOR_MISSING_REVIEW_EVIDENCE`.

## 6. Boundary

Tooling plans are not evidence that SOE works. They are test designs. Any future execution requires separate authorization, source locking, and output verification.
