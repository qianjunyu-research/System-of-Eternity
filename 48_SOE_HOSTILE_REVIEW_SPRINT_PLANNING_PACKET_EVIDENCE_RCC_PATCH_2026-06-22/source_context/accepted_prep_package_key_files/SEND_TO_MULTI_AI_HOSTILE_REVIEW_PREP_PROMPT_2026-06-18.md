# Send-To-Multi-AI Prompt - SOE Hostile Review Prep

Please review the attached folder:

```text
45_SOE_HOSTILE_REVIEW_PREP_PACKAGE_PATCHED_2026-06-18
```

You are reviewing the hostile review preparation design for SOE, not SOE's deployment readiness.

Required verdict:

```text
ACCEPT_HOSTILE_REVIEW_PREP_PACKAGE
PATCH_NEEDED_HOSTILE_REVIEW_PREP_PACKAGE
BLOCKER_HOSTILE_REVIEW_PREP_OVERCLAIM
BLOCKER_HOSTILE_REVIEW_PREP_WEAK_ADVERSARY_MODEL
```

Please answer:

1. Is the adversary model strong enough?
2. What adversary classes are missing?
3. Are the test families capable of finding meaningful failures?
4. Does the package avoid overclaim?
5. Does it preserve SGS/TGS as simulation evidence only?
6. Does it preserve fiction/media as scenario-seed material only?
7. Does it avoid treating multi-AI agreement as peer review or empirical replication?
8. Does it include enough architecture context to make concrete attacks rather than vague critique?
9. Can this become the basis for the later hostile review sprint planning packet?

Required output addition:

```text
Rank | Failure pathway | Target component | Adversary class(es) | Why current controls may fail | Severity | Patch candidate | Residual risk
```

Return at least 10 ranked failure pathways if the package is strong enough to support them. Be adversarial. Do not praise unless the package survives attack.
