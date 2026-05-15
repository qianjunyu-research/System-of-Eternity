# SOE Node v0.1 Daily Log Field Dictionary

Use this with `SOE_Node_v0_1_Daily_Log_Template.csv`.

## Required Identifiers

- `date`: ISO date.
- `session_id`: unique daily/session id.
- `observer_id`: person or agent recording the row.
- `node_id`: participant or agent id.
- `node_class`: one of `H`, `I`, `A`.
- `interaction_id`: unique interaction or discussion id.
- `active_topology_type`: one of `single_group`, `ring_mesh`, `star`, `hub_redundant`, `federation`, `unknown`.
- `detected_topology_type`: observed topology label using the same allowed set.
- `topology_confidence_0_1`: confidence that detected topology is correct.
- `subgroup_id`: subgroup or cluster id; blank if not applicable.
- `federation_id`: federation id; blank if not applicable.
- `normalization_profile_id`: formula/cap profile. Initial value is `node_v0_1_default`.
- `ordinal_rating_method`: how 1 to 5 ratings were interpreted; initial value is `bounded_ordinal_linear_v0_1`.

## Raw Inputs

- `trust_rating_1_5`: self-report or observer-coded trust. Must be blank if unknown.
- `follow_through_score_0_1`: observed follow-through on agreed action.
- `repair_acceptance_0_1`: whether repair attempt was accepted.
- `conflict_intensity_0_4`: 0 none, 4 severe.
- `message_delay_minutes`: delay that affected coordination.
- `delay_harmful_0_1`: whether delay actually harmed coordination.
- `unresolved_issue_count`: count after interaction.
- `surprise_or_shock_0_1`: unexpected disruptive event.
- `misunderstanding_count`: count of observed misunderstandings.
- `contradiction_count`: count of unresolved contradictions.
- `clarity_rating_1_5`: clarity of shared understanding.
- `correction_needed_0_1`: whether correction was required.
- `role_clarity_rating_1_5`: clarity of participant/agent role.
- `belonging_rating_1_5`: only for H/I nodes; blank for A nodes.
- `role_conflict_0_1`: whether role expectations conflicted.
- `withdrawal_0_1`: whether node disengaged or withdrew.

## Normalization Inputs

These fields make the transfer math auditable.

- `delay_cap_minutes`: default `120`.
- `issue_cap`: default `5`.
- `misunderstanding_cap`: default `5`.
- `contradiction_cap`: default `5`.
- `trust_rating_confidence_0_1`: confidence in the trust rating.
- `clarity_rating_confidence_0_1`: confidence in the clarity rating.
- `role_clarity_rating_confidence_0_1`: confidence in role clarity rating.
- `belonging_rating_confidence_0_1`: confidence in belonging rating; blank for A nodes.

## Normalized Component Scores

- `capped_delay_score`: `delay_harmful_0_1 * cap_score(message_delay_minutes, delay_cap_minutes)`.
- `capped_issue_score`: capped unresolved issue score.
- `capped_misunderstanding_score`: capped misunderstanding score.
- `capped_contradiction_score`: capped contradiction score.

## Derived SOE Variables

- `T_value`: normalized trust.
- `D_value`: normalized disturbance.
- `C_value`: normalized cognitive distortion.
- `I_value`: normalized identity/role coherence.
- `S_value`: derived stability.

All derived variables must be `[0.0, 1.0]`.

## Trigger / Gate Fields

- `trigger_label`: blank, `watch`, `pause`, `repair`, or `abort`.
- `trigger_source`: blank, `C04_S_THRESHOLD`, `C07_PSI_EXTENDED`, `HUMAN_SAFETY`, or `DATA_QUALITY`.
- `psi_extended_value`: blank unless federation logic applies.
- `gate_data_completeness_pass`: 0 or 1.
- `gate_bounds_pass`: 0 or 1.
- `gate_artifact_resistance_pass`: 0 or 1.
- `gate_trigger_sanity_pass`: 0 or 1.
- `gate_consent_safety_pass`: 0 or 1.
- `stop_condition_flag`: 0 or 1.

## Artifact Flags

- `artifact_delay_without_harm`: delay is high but not harmful.
- `artifact_disagreement_not_confusion`: disagreement occurred without cognitive distortion.
- `artifact_politeness_not_trust`: polite tone should not inflate trust.
- `artifact_ai_belonging_misapplied`: A node was incorrectly assigned belonging.

## Notes

- `raw_notes`: short human-readable context.
- `reviewer_notes`: later auditor notes.

## Missing Data Rule

Blank means missing. Do not replace missing with 0.5 unless a separate sensitivity analysis explicitly says so.

## Topology Rule

Gate G04 cannot pass unless `active_topology_type` is present. Federation Trigger A must use `C07_PSI_EXTENDED`; non-federation Trigger A may use `C04_S_THRESHOLD`. If topology is `unknown`, the row may only support a human-review label, not an architecture claim.
