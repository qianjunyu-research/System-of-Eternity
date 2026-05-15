# SOE Node v0.1 Normalization Spec

Status: required companion spec for the Node v0.1 planning packet.

## Purpose

This file closes the main multi-AI review blocker: raw daily-log fields must not be converted into T/D/C/I/S by guesswork. Every unbounded count or time value must pass through an explicit bounded transfer function before it can affect an SOE state variable.

Node v0.1 is still a bounded container-test planning packet. These formulas make the logging design auditable; they do not validate the proxies as real-world governance measures.

## Global Rules

- All derived variables must be in `[0.0, 1.0]`.
- Blank raw fields remain missing. Do not silently convert missing data to `0.0`, `0.5`, or any neutral value.
- Every completed daily-log row must record `normalization_profile_id`.
- The initial locked profile is `node_v0_1_default`.
- Any change to caps, weights, or formulas creates a new profile id and must be logged.
- Ratings on 1 to 5 scales are ordinal approximations. They may be used for a bounded pilot only if reviewer notes preserve that they are not interval-validated measurements.

## Clamp Function

```text
clamp(x) = min(1.0, max(0.0, x))
```

## Rating Normalization

```text
norm_1_5(r) = clamp((r - 1) / 4)
norm_0_4(x) = clamp(x / 4)
```

Interpretation guard:
- A value of `4` is not assumed to be exactly twice a value of `2`.
- The formula only creates a bounded audit score for a small local test.
- If a reviewer believes a rating is ambiguous, record a lower `*_confidence_0_1` value and explain it in `reviewer_notes`.

## Count And Delay Normalization

Default caps for `node_v0_1_default`:

```text
delay_cap_minutes = 120
issue_cap = 5
misunderstanding_cap = 5
contradiction_cap = 5
```

Capped linear score:

```text
cap_score(x, cap) = clamp(min(x, cap) / cap)
```

Delay must be gated by harm:

```text
capped_delay_score = delay_harmful_0_1 * cap_score(message_delay_minutes, delay_cap_minutes)
```

Counts:

```text
capped_issue_score = cap_score(unresolved_issue_count, issue_cap)
capped_misunderstanding_score = cap_score(misunderstanding_count, misunderstanding_cap)
capped_contradiction_score = cap_score(contradiction_count, contradiction_cap)
```

Artifact guard:
- A long idle delay with `delay_harmful_0_1 = 0` contributes `0` to D through delay.
- Disagreement without confusion must be logged separately and must not inflate C by itself.

## State Variable Formulas

T:

```text
T = clamp(0.50 * norm_1_5(trust_rating_1_5)
        + 0.30 * follow_through_score_0_1
        + 0.20 * repair_acceptance_0_1)
```

D:

```text
D = clamp(0.35 * norm_0_4(conflict_intensity_0_4)
        + 0.25 * capped_delay_score
        + 0.25 * capped_issue_score
        + 0.15 * surprise_or_shock_0_1)
```

C:

```text
C = clamp(0.30 * capped_misunderstanding_score
        + 0.25 * capped_contradiction_score
        + 0.30 * (1 - norm_1_5(clarity_rating_1_5))
        + 0.15 * correction_needed_0_1)
```

I for H/I nodes:

```text
I_HI = clamp(0.45 * norm_1_5(role_clarity_rating_1_5)
           + 0.35 * norm_1_5(belonging_rating_1_5)
           + 0.10 * (1 - role_conflict_0_1)
           + 0.10 * (1 - withdrawal_0_1))
```

I for A nodes:

```text
I_A = clamp(0.70 * norm_1_5(role_clarity_rating_1_5)
          + 0.20 * (1 - role_conflict_0_1)
          + 0.10 * (1 - withdrawal_0_1))
```

S:

```text
S = clamp(0.45 * T
        + 0.25 * I
        + 0.15 * (1 - D)
        + 0.15 * (1 - C))
```

## Topology Context

Every row must include:

- `active_topology_type`: `single_group`, `ring_mesh`, `star`, `hub_redundant`, `federation`, `unknown`.
- `detected_topology_type`: same allowed set.
- `topology_confidence_0_1`: observer confidence in detected topology.
- `subgroup_id`: blank unless federation or subgroup logic applies.
- `federation_id`: blank unless federation logic applies.

Trigger-source sanity depends on `active_topology_type`, not just on the trigger value:

```text
if active_topology_type == "federation":
    Trigger A source must be C07_PSI_EXTENDED
else:
    Trigger A source may be C04_S_THRESHOLD
```

If topology is `unknown`, Trigger A must be downgraded to `watch` or `pause` for human review rather than treated as architecture evidence.

## Required Audit Columns

The daily log must expose both raw and normalized values:

- raw ratings/counts/delays
- caps used for each row
- normalized component scores
- T/D/C/I/S
- missingness flags
- topology fields
- trigger label/source
- gate pass/fail fields
- artifact flags
- raw notes and reviewer notes

If a summary hides any of those layers, it is not sufficient evidence for Node v0.1.
