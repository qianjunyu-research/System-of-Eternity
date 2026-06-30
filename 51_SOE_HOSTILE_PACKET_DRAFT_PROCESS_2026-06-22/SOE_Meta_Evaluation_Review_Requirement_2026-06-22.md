# SOE Meta-Evaluation Review Requirement

Date: 2026-06-22

Status: REQUIRED REVIEW BLOCK FOR HOSTILE PACKETS

## 1. Purpose

The strongest later AI reviewers should not be trapped inside the questions written by weaker or lower-budget drafting passes.

Every hostile packet must therefore invite reviewers to evaluate the packet itself.

## 2. Required Meta-Evaluation Block

Add this block to every hostile packet's multi-AI review prompt:

```text
Meta-evaluation requirement:

Do not only answer the packet's stated questions. Evaluate whether the packet itself is sufficient.

Identify:
- missing adversary classes
- missing public-fear or legitimacy pathways
- missing corruption, coercion, insider, or capture mechanisms
- missing legal/political/economic implementation constraints
- weak or leading questions
- source material that functions as an answer key rather than a genuine test surface
- ambiguous failure triggers
- scoring rules that could launder failure into success
- missing preregistration or change-control rules
- weak minority-finding preservation
- evidence boundaries that are too weak
- places where a positive result could be overclaimed
- any execution drift, contact drift, recruitment drift, or self-certification risk

If the packet's own design is inadequate, return PATCH_NEEDED or BLOCKER even if the packet answers its own questions cleanly.
```

## 3. Required Final Review Question

Every review prompt should end with:

```text
If you had to redesign this packet before spending real money or high-tier model budget on it, what would you change?
```

## 4. Blocker Rule

If reviewers find that the packet can create a false sense of validation, execution readiness, public readiness, or authority, the correct verdict is a blocker, not an ordinary patch.

## 5. Design Consequence

The packet author must patch the packet before any future execution-preparation gate.

Meta-evaluation findings are not optional comments. They are part of the hostile test surface.
