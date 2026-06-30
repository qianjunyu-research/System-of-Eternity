# SOE Hostile Packet Draft Process

Date: 2026-06-22

Status: DRAFT PROCESS / DESIGN ONLY

## 1. Drafting Principle

Hostile packets should be designed as adversarial test instruments, not as persuasion documents.

The goal is not to prove SOE works. The goal is to expose whether SOE's architecture, evidence boundaries, communication, and implementation assumptions fail under hostile interpretation.

## 2. Draft Sequence

Use this order for each essential packet:

1. Define the hostile question.
2. Define the target failure mode.
3. Define what source material reviewers or participants would see.
4. Define who is allowed to review or participate.
5. Define what independence rules prevent self-certification.
6. Define the question instrument or test procedure.
7. Define scoring and coding rules, including how borderline and minority findings are preserved.
8. Define failure triggers before any review or execution.
9. Define preregistration fields if the packet could later be executed.
10. Define what a pass can and cannot mean.
11. Define privacy, data, consent, and withdrawal rules if any human contact is ever involved.
12. Add a meta-evaluation block asking reviewers to attack the packet design itself.
13. Add a hold checklist that separates design acceptance from execution authorization.
14. Generate a hash manifest from actual files.

## 3. Required Packet Skeleton

Every essential hostile packet should include:

- `READ_FIRST`
- design overview
- source material or test material
- independence and reviewer/participant rules
- question instrument or adversarial task
- scoring and coding protocol
- preregistration template or explicit reason why preregistration is not applicable
- failure consequence map
- overclaim and non-upgrade rules
- pre-execution hold checklist
- multi-AI review prompt
- file manifest
- hash manifest

If the packet involves real people later, add:

- consent/privacy/data/withdrawal template
- compensation/no-coercion note
- raw-response storage plan

## 4. Review Verdict Pattern

Each hostile packet should use constrained verdicts:

```text
ACCEPT_[PACKET_NAME]
PATCH_NEEDED_[PACKET_NAME]
BLOCKER_[CONTACT_OR_EXECUTION_DRIFT]
BLOCKER_[SELF_CERTIFICATION_OR_OVERCLAIM]
```

The exact labels can vary, but the packet must distinguish ordinary patch needs from execution drift and self-certification/overclaim blockers.

## 5. Non-Upgrade Rule

No hostile packet may upgrade its own result into:

- empirical validation
- deployment readiness
- pilot readiness
- real-world safety proof
- governance authority
- policy authority
- public adoption evidence
- real-world node recognition
- Operation Layer freeze

At most, a design-stage or review-stage result can support a narrow claim such as:

```text
This packet was reviewed for design adequacy and revised against identified failure modes.
```

Execution-stage results, if ever authorized later, must still be bounded to their actual test surface.

## 6. No-Zip Rule

Do not create zip files for hostile packets by default.

Use ordinary folders. Keep file names explicit. Use `hash_manifest.csv` for integrity.
