# SOE Node v0.1 Execution Spec

Status: planning and audit packet. Not deployment-ready.

## Purpose

Node v0.1 is the first small executable container test for translating SOE simulation variables into human/agent interaction tracking. It is not a public governance deployment, not a policy trial, and not an architecture proof. Its purpose is to test whether daily observable signals can be mapped into bounded SOE state variables without creating false precision or metric artifacts.

## Source Boundary

- v0.7 Grand Simulation is the current simulation evidence base.
- C07 `Psi_extended` remains the federation Trigger A source of truth.
- C04 S-threshold remains valid for non-federation Trigger A only.
- C02 v2.1 remains source of truth for T-G loop break margins.
- C05 v2.1 remains source of truth for H/I/A node class treatment.
- `f_min = 0.30` and `kappa_min = 0.25` remain distinct.

## Node v0.1 Scope

Node v0.1 should track a small, consent-based, low-stakes interaction group over short daily windows.

Recommended initial size:
- 3 to 7 human participants or simulated participants.
- 1 to 3 AI/agent participants.
- 7 to 14 daily log days.

Allowed activities:
- Structured discussion.
- Decision proposal and response.
- Conflict or disagreement logging.
- Repair/recovery attempt logging.
- Optional asynchronous message-delay simulation.

Disallowed activities:
- Real authority over people or resources.
- Psychological profiling.
- Medical, legal, financial, employment, or safety-critical decisions.
- Claims of governance readiness.

## State Variable Mapping

All values must be normalized to `[0.0, 1.0]`. Missing data must remain missing, not silently converted to neutral values.

The required normalization contract is defined in `SOE_Node_v0_1_Normalization_Spec.md`. That file is part of the executable packet, not optional background. Node v0.1 uses `normalization_profile_id = node_v0_1_default` unless a later reviewed packet changes the caps or formulas.

Reviewer correction from the multi-AI review:
- Unbounded fields such as `message_delay_minutes`, `unresolved_issue_count`, `misunderstanding_count`, and `contradiction_count` must use explicit caps before entering T/D/C/I/S.
- 1 to 5 ratings are ordinal approximations. They are acceptable only for a bounded local audit and must not be described as validated interval measurements.
- Trigger sanity requires topology context in the daily log.

### T: Trust

Tracks willingness to rely on others and the system after an interaction.

Inputs:
- `trust_rating`: participant self-report, 1 to 5.
- `follow_through_score`: observed completion of agreed action, 0 to 1.
- `repair_acceptance`: whether repair after disagreement was accepted, 0 to 1.

Suggested formula:

```text
T = clamp(0.50 * norm_1_5(trust_rating)
        + 0.30 * follow_through_score
        + 0.20 * repair_acceptance)
```

Artifact guard:
- Do not infer trust from politeness alone.
- If `trust_rating` is missing, mark `T_missing = 1` and compute only an optional sensitivity score.

### D: Disturbance

Tracks disruption, conflict, delay, uncertainty, or overload.

Inputs:
- `conflict_intensity`: 0 to 4.
- `message_delay_minutes`: capped at `delay_cap_minutes`.
- `unresolved_issue_count`: capped at `issue_cap`.
- `surprise_or_shock`: 0 or 1.

Default caps:
- `delay_cap_minutes = 120`
- `issue_cap = 5`

Suggested formula:

```text
D = clamp(0.35 * norm_0_4(conflict_intensity)
        + 0.25 * capped_delay_score
        + 0.25 * capped_issue_score
        + 0.15 * surprise_or_shock)
```

Artifact guard:
- Do not let one long idle period create high disturbance unless it blocked coordination.
- Log whether delay was expected, neutral, or harmful.

### C: Cognition / Cognitive Distortion

Tracks confusion, misinterpretation, contradiction, or narrative distortion.

Inputs:
- `misunderstanding_count`: capped.
- `contradiction_count`: capped.
- `clarity_rating`: 1 to 5, inverted.
- `correction_needed`: 0 or 1.

Default caps:
- `misunderstanding_cap = 5`
- `contradiction_cap = 5`

Suggested formula:

```text
C = clamp(0.30 * capped_misunderstanding_score
        + 0.25 * capped_contradiction_score
        + 0.30 * (1 - norm_1_5(clarity_rating))
        + 0.15 * correction_needed)
```

Artifact guard:
- Disagreement is not automatically cognitive distortion.
- Count only confusion, contradiction, or demonstrable misread.

### I: Identity / Role Coherence

Tracks whether participant roles, commitments, and belonging remain coherent.

Inputs:
- `role_clarity_rating`: 1 to 5.
- `belonging_rating`: 1 to 5, human/institutional nodes only.
- `role_conflict_flag`: 0 or 1.
- `withdrawal_flag`: 0 or 1.

Suggested H/I node formula:

```text
I = clamp(0.45 * norm_1_5(role_clarity_rating)
        + 0.35 * norm_1_5(belonging_rating)
        + 0.10 * (1 - role_conflict_flag)
        + 0.10 * (1 - withdrawal_flag))
```

Suggested A node formula:

```text
I_A = clamp(0.70 * norm_1_5(role_clarity_rating)
          + 0.20 * (1 - role_conflict_flag)
          + 0.10 * (1 - withdrawal_flag))
```

Artifact guard:
- Do not ask AI/agent nodes for belonging as if they were human.
- Do not collapse H/I/A formulas.

### S: Stability

Tracks functional state of the local interaction node.

Suggested formula:

```text
S = clamp(0.45 * T
        + 0.25 * I
        + 0.15 * (1 - D)
        + 0.15 * (1 - C))
```

Artifact guard:
- Stability is a derived state, not a direct self-report.
- Keep raw T/D/C/I values visible so S cannot hide contradictory evidence.

## Governance / Trigger Mapping

Node v0.1 should not activate any real intervention. It may only label events for review.

Trigger labels:
- `watch`: mild deterioration, review at end of day.
- `pause`: interaction should pause for clarification.
- `repair`: explicit recovery conversation needed.
- `abort`: stop the test session for safety or consent reasons.

Suggested non-federation Trigger A:

```text
if S < 0.48:
    trigger_A_source = "C04_S_THRESHOLD"
```

Suggested federation Trigger A only if multiple subgroups exist:

```text
if psi_extended >= 0.30:
    trigger_A_source = "C07_PSI_EXTENDED"
```

Topology fields are required for trigger auditing:
- `active_topology_type`
- `detected_topology_type`
- `topology_confidence_0_1`
- `subgroup_id`
- `federation_id`

If `active_topology_type = federation`, C07 `Psi_extended` is the only valid Trigger A source. If `active_topology_type` is non-federation, C04 S-threshold is allowed and C07 is not used as Trigger A. If topology is `unknown`, the row cannot support architecture evidence and must be routed to human review.

## Gate Criteria

Gate criteria must prevent premature claims. Passing a gate means the packet can proceed to the next local test, not real deployment.

Gate 1: Data Completeness
- At least 95% required fields present.
- Missingness by participant or node class must be reported.
- No imputation hidden inside final T/D/C/I/S.

Gate 2: Bounds Integrity
- All normalized T/D/C/I/S values remain in `[0.0, 1.0]`.
- Raw values remain available for audit.
- No variable is overwritten by derived S.
- `normalization_profile_id`, caps, and normalized component scores are present.

Gate 3: Artifact Resistance
- Long delays are not counted as high D unless harmful.
- Disagreement is not counted as high C unless confusion/contradiction is present.
- Politeness is not counted as trust.
- AI nodes do not use human belonging formula.

Gate 4: Trigger Sanity
- Trigger labels must match source hierarchy.
- C04 S-threshold is not used for federation Trigger A.
- C07 Psi is not used for non-federation Trigger A.
- Topology fields are present before any Trigger A row is interpreted.

Gate 5: Human Safety / Consent
- Participants can pause or exit.
- No hidden scoring is used to rank humans.
- No real-world authority is delegated to the model.

## Stop Conditions

Stop Node v0.1 immediately if:
- Consent is withdrawn.
- Participants treat scores as judgment or authority.
- Logs include sensitive personal data outside agreed scope.
- Any output is used for real decisions.
- More than 5% of required fields are missing for two consecutive days.
- Any variable mapping creates obvious artifacts that reviewers cannot correct.

## Expected Outputs

- `SOE_Node_v0_1_Daily_Log_Template.csv`
- Completed daily logs.
- `SOE_Node_v0_1_Field_Dictionary.md`
- `SOE_Node_v0_1_Normalization_Spec.md`
- Reviewer notes.
- A short post-test synthesis with:
  - mapping failures
  - artifact risks
  - trigger sanity
  - whether another container planning pass is needed

## Interpretation Boundary

Node v0.1 can only support:

```text
The SOE state-variable logging scheme is structurally testable in a bounded container setting.
```

It cannot support:

```text
SOE is deployment-ready.
SOE can govern real groups.
Subjective scores are validated real-world proxies.
```
