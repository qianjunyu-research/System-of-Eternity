# SOE Governance Architecture v0.5 Candidate Reviewer Prompt

You are reviewing the SOE Governance Architecture v0.5 Candidate.

Do not review SOE as a public deployment system. Review whether this candidate correctly upgrades the frozen v0.4 architecture after Grand Simulation v0.7 and Node v0.1 while preserving evidence boundaries.

## Source Packet

Primary file:

- `SOE_Governance_Architecture_v0_5_Candidate.md`

Supporting files:

- `SOE_Upgrade_Specification_v0_1.md`
- `SOE_Upgrade_Blocker_List_v0_1.md`
- `SOE_Governance_Architecture_Ontology_Readiness_Patch_v0_1.md`
- `SOE_C09_Node_Formation_and_Recognition_Layer_v0_1.md`
- `SOE_Node_Measurement_Protocol_v0_1.md`
- `SOE_Drift_Layer_Requirements_v0_1.md`
- `SOE_Psi_Extended_Adversarial_Test_Spec_v0_1.md`
- `SOE_Meta_Governance_Update_Patch_v0_1.md`

## Hard Boundaries

- Grand Simulation v0.7 is simulation-level architecture evidence only.
- Grand Simulation v0.7 is not deployment evidence, pilot evidence, empirical proxy validation, or real-world safety proof.
- Node v0.1 is a bounded two-node container record only.
- Node v0.1 is not validation evidence for SOE dynamics, ignition, network propagation, or deployment readiness.
- `C` must mean cognitive distortion.
- `Psi_extended` must be a C07 detector output, not a primary SOE state variable.
- `f_min=0.30` and `kappa_min=0.25` must remain distinct.
- C09 and Drift Layer are proposed extensions, not simulation-validated mechanisms.

## Review Tasks

Answer these directly:

1. Does v0.5 Candidate preserve all evidence boundaries?
2. Does the ontology block correctly fix `C`, `Psi_extended`, `f_min`, and `kappa_min`?
3. Does the candidate accidentally overclaim Grand Simulation v0.7?
4. Does the candidate accidentally overclaim Node v0.1?
5. Is C09 scoped correctly as a proposed Node Formation and Recognition Layer?
6. Are C09 recognition gates sufficient to prevent node-creation capture?
7. Is the Drift Layer strong enough to detect slow terminal/capture drift without becoming a veto authority?
8. Does the Meta-Governance update sufficiently separate sensing, classification, trigger activation, intervention/rollback, and audit?
9. Are the `Psi_extended` adversarial/circularity tests sufficient before pilot/deployment detector claims?
10. Are the Node Measurement Protocol requirements sufficient before Node v0.2?
11. Which blockers prevent freezing v0.5?
12. Which items can safely remain future work after v0.5 freeze?

## Required Output Format

Return:

1. Verdict: `pass`, `pass_with_patches`, `needs_revision`, or `block`.
2. Hard blockers, if any.
3. Required wording patches.
4. Overclaim risks.
5. Missing requirements.
6. Final recommendation: freeze v0.5, revise v0.5, or split into component specs first.

## Do Not Say

- Do not say SOE is deployment-ready.
- Do not say SOE is pilot-ready.
- Do not say Node v0.1 validates SOE.
- Do not say `Psi_extended` is stability-independent.
- Do not say three hubs are safe.
- Do not say resource recovery is proven.
