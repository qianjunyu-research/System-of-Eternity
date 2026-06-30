# SOE Hostile Review Flaw Taxonomy And Verdicts

Date: 2026-06-18

Status: Review rubric

## 1. Verdicts

### ACCEPT_HOSTILE_REVIEW_PREP_PACKAGE

Use only if:

- adversary classes are broad and strong;
- no major obvious hostile class is missing;
- review questions are clear;
- evidence boundaries are preserved;
- no deployment/readiness overclaim appears;
- package is suitable to become the basis for later hostile sprint planning.

### PATCH_NEEDED_HOSTILE_REVIEW_PREP_PACKAGE

Use if:

- the direction is correct but important adversary classes or tests are missing;
- some language is ambiguous but not an affirmative overclaim;
- reviewer instructions are incomplete;
- source map or scope boundaries need correction.

### BLOCKER_HOSTILE_REVIEW_PREP_OVERCLAIM

Use if the package implies any of these:

- SOE is deployment-ready;
- hostile review preparation validates SOE;
- simulation evidence proves real-world governance function;
- C09 can recognize real-world nodes safely;
- Operation Layer is frozen;
- prior SGS/TGS results prove real-world safety;
- fiction/media findings count as evidence that SOE controls work.

### BLOCKER_HOSTILE_REVIEW_PREP_WEAK_ADVERSARY_MODEL

Use if the package fails to include serious adversarial pressure, such as:

- malicious human coalitions;
- ideological laundering;
- legal reinterpretation;
- propaganda;
- insider compromise;
- economic capture;
- security-state capture;
- slow corruption;
- AI-assisted evidence manipulation;
- real-organization implementation failure.

## 2. Flaw Severity

### P0 - Blocker

The package would cause the hostile sprint to be misleading or unsafe.

Examples:

- treats hostile review as validation;
- omits adaptive adversaries;
- permits deployment-readiness language;
- treats perfect-input simulation as real-world resilience;
- excludes ideological or political capture from scope.

### P1 - Required Patch

The package is directionally right but would produce weaker review results unless fixed.

Examples:

- missing public-panic category;
- unclear output format;
- weak C09 stress questions;
- no slow-corruption tests;
- no economic capture tests.

### P2 - Recommended Improvement

Useful but not required before multi-AI review.

Examples:

- better wording;
- clearer ordering;
- extra examples;
- optional reviewer role splits.

### P3 - Nonblocking Polish

Style, formatting, or clarity improvements only.

## 3. Specific Red Flags

Reviewers should flag any package language that:

- says or implies "SOE solves";
- treats simulation outputs as empirical evidence;
- treats public fear mapping as proof of problem coverage;
- assumes adversaries are honest;
- relies on perfect gate inputs;
- treats C09 as real-world node-recognition ready;
- treats a successful review process as human approval;
- suggests external AI review is equivalent to peer review;
- suggests implementation can proceed without a real-world experimental environment.

## 4. Acceptance Threshold

The package should not be accepted merely because it is clear or well written. It should be accepted only if it is hard enough to make future review painful in useful ways.

The best outcome is not "reviewers agree SOE is strong." The best outcome is that reviewers find the right failure surfaces before expensive sprint execution begins.

