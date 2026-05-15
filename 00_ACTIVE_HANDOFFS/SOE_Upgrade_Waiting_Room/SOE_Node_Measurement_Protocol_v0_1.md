# SOE Node Measurement Protocol v0.1

Status: required protocol before Node v0.2 or any pilot-facing claim.

Date: 2026-05-12

## 1. Purpose

This protocol defines how bounded Node tests may score T/D/C/I/S without pretending that the scores are validated real-world equivalents of simulation variables.

Node measurement is allowed only as local audit instrumentation until separately validated.

## 2. Evidence Boundary

Allowed claim after a compliant bounded test:

```text
The SOE Node measurement protocol was structurally usable in a bounded container setting.
```

Blocked claims:

- SOE variables are empirically validated.
- T/D/C/I/S scores are objective human-measurement instruments.
- Node results validate SOE dynamics.
- Node results prove ignition, propagation, pilot readiness, or deployment readiness.

## 3. Consent and Scope

Before any structured Node v0.2 test:

- participants must give explicit informed consent,
- participants must be told scores are research/audit labels, not personal rankings,
- pause and exit rights must be clear,
- sensitive domains are excluded unless separately reviewed,
- no medical, legal, financial, employment, safety-critical, or coercive decisions may be made from scores.

Node B or any future partner must opt in to structured participation. Passive awareness from v0.1 is not enough.

## 4. Required Log Fields

Every row must include:

- date,
- session ID,
- observer ID,
- node ID,
- node class,
- interaction ID,
- active topology type,
- detected topology type,
- topology confidence,
- subgroup ID where applicable,
- federation ID where applicable,
- normalization profile ID,
- raw inputs,
- normalized component scores,
- T/D/C/I/S values,
- missingness flags,
- artifact flags,
- trigger label/source,
- raw notes,
- reviewer notes.

## 5. Variable Rubrics

### T: Trust

Definition: willingness and ability to rely on another node or the local system after the interaction.

Allowed indicators:

- trust rating,
- follow-through,
- repair acceptance,
- reliability after disagreement.

Artifact guards:

- politeness is not trust,
- compliance under pressure is not trust,
- high familiarity is not proof of system robustness.

### D: Disturbance

Definition: disruption, conflict, delay, uncertainty, overload, or external shock.

Allowed indicators:

- conflict intensity,
- harmful delay,
- unresolved issue count,
- surprise/shock event.

Artifact guards:

- a long idle period is not D unless it harms coordination,
- inconvenience is not automatically structural disturbance.

### C: Cognitive Distortion

Definition: confusion, contradiction, misread system state, or distorted shared understanding.

Allowed indicators:

- misunderstanding count,
- contradiction count,
- clarity rating inverted,
- correction needed.

Artifact guards:

- disagreement is not automatically cognitive distortion,
- moral difference is not automatically cognitive distortion,
- coordination failure is downstream C08 behavior, not the C variable itself.

### I: Identity Support / Role Coherence

Definition: clarity and stability of node role, mandate, belonging, or functional legitimacy.

Allowed indicators:

- role clarity,
- belonging for H nodes,
- mandate recognition for I nodes,
- role conflict,
- withdrawal.

Artifact guards:

- AI nodes do not receive psychological belonging scores,
- institutional nodes require functional proxies, not feelings,
- role obedience is not the same as identity support.

### S: Stability

Definition: derived local functional stability.

Rule:

```text
S must be computed from T/I/D/C components and kept auditable. It must not replace the raw variables.
```

Artifact guards:

- S cannot hide high D or high C,
- S cannot be a direct self-report,
- S cannot be used alone for human judgment.

## 6. Default Normalization Contract

Use `node_measurement_v0_1_default` unless reviewed.

```text
clamp(x) = min(1.0, max(0.0, x))
norm_1_5(r) = clamp((r - 1) / 4)
norm_0_4(x) = clamp(x / 4)
cap_score(x, cap) = clamp(min(x, cap) / cap)
```

Default caps:

- `delay_cap_minutes = 120`
- `issue_cap = 5`
- `misunderstanding_cap = 5`
- `contradiction_cap = 5`

Missing data:

- blank means missing,
- do not replace missing values with 0, 0.5, or neutral values unless a separate sensitivity analysis says so.

## 7. Inter-Rater Logic

Before stronger Node v0.2 claims:

- at least one second rater, reviewer, or post-hoc audit path must exist,
- rater disagreement must be logged,
- disagreement must not be averaged away without explanation,
- low-confidence ratings must remain visible.

Suggested fields:

- `trust_rating_confidence_0_1`
- `clarity_rating_confidence_0_1`
- `role_clarity_rating_confidence_0_1`
- `belonging_or_proxy_confidence_0_1`
- `rater_disagreement_flag`
- `rater_disagreement_notes`

## 8. Trigger Source Rules

If `active_topology_type = federation`:

```text
Trigger A source must be C07_PSI_EXTENDED.
```

If non-federation:

```text
Trigger A may use C04_S_THRESHOLD.
```

If topology is unknown:

```text
No row may support architecture evidence. Route to human review as watch/pause only.
```

## 9. Gates

| Gate | Pass condition |
|---|---|
| NM-G01 Data completeness | At least 95 percent required fields present; missingness reported. |
| NM-G02 Bounds integrity | All derived values in [0,1]; raw values, caps, profile ID, and component scores retained. |
| NM-G03 Artifact resistance | Delay, disagreement, politeness, and AI-belonging artifacts checked. |
| NM-G04 Trigger sanity | Trigger source matches topology. |
| NM-G05 H/I/A integrity | Node class formulas remain distinct. |
| NM-G06 Consent/safety | Pause/exit rights and no real authority use. |
| NM-G07 Audit trail | Raw logs and reviewer notes retained. |

## 10. Stop Conditions

Stop the test if:

- consent is withdrawn,
- scores are treated as judgment or authority,
- sensitive data appears outside agreed scope,
- missingness exceeds 5 percent for two consecutive sessions,
- artifact flags cannot be resolved,
- any participant experiences distress or coercion,
- outputs begin influencing real decisions.

## 11. Node v0.1 Carryover Patch

The Node v0.1 completion report date typo should be corrected in a new version:

```text
May 6-8212, 2026
```

to:

```text
May 6-12, 2026
```

Do not silently alter the frozen record. Use a versioned correction note.
