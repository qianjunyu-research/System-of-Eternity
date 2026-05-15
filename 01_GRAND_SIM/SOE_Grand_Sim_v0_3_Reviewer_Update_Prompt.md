# SOE Grand Sim v0.3 Reviewer Update Prompt

We are reviewing the SOE Grand Simulation v0.3 focused calibration package.

Do not debate SOE as a whole. Audit whether v0.3 faithfully answers the unresolved v0.2 questions and whether the interpretation overclaims the evidence.

## Source Hierarchy

1. Architecture snapshots and component specs remain source of truth.
2. C04 v2.3 and C07 v2.2 govern federation monitoring.
3. C02 v2.1 governs T-G loop break condition.
4. C05 v2.1 governs H/I/A node classes.
5. Codex simulation outputs are reproducible artifacts, not source of truth by themselves.

Locked interpretation:

- Federation Trigger A: C07 `Psi_extended` only.
- Non-federation Trigger A: C04 S-threshold is allowed and expected.
- `f_min = 0.30` and `kappa_min = 0.25` are distinct; do not collapse them.
- Deployment readiness remains blocked.

## Role Assignments

- Claude: independent architecture auditor. Attack assumptions, source hierarchy, parameter choices, and interpretation.
- Gemini: math/topology verifier. Inspect graph construction, bridge isolation, hub redundancy, topology drift math, and detector thresholds.
- Grok: stress tester. Identify the weakest claim, suspicious nulls, and ways we may be fooling ourselves.
- ChatGPT: documentation and synthesis. Downgrade overclaims, check claim-to-output traceability, and prepare clean reviewer summaries.
- Copilot: code reviewer. Inspect implementation risks, reproducibility, CSV correctness, and test gaps.
- Le Chat: independence auditor and structural compressor. Cross-reference spec, prompt, code, and outputs into divergence tables.

Any reviewer may jump out of role if they see a serious issue outside their lane, but they should label it explicitly as "outside my assigned lane" and explain why it matters.

QianJun can grant connectors/plugins and can provide additional files on request. Ask for the minimum file set needed for the next finding.

## v0.3 Files To Inspect First

- `SOE_Grand_Simulation_v0_3_Findings.md`
- `SOE_Grand_Sim_v0_2_Consensus.md`
- `soe_grand_sim_v0_3.py`
- `grand_sim_v0_3/grand_sim_v0_3_report.md`
- `grand_sim_v0_3/grand_sim_v0_3_psi_sweep_summary.csv`
- `grand_sim_v0_3/grand_sim_v0_3_topology_lag_summary.csv`
- `grand_sim_v0_3/grand_sim_v0_3_hub_reproduction_comparison.csv`

Ask for raw run CSVs only if needed:

- `grand_sim_v0_3/grand_sim_v0_3_psi_sweep_runs.csv`
- `grand_sim_v0_3/grand_sim_v0_3_topology_lag_runs.csv`

## What v0.3 Claims

1. CL02: the v0.2 run-rate metric was too blunt. Event-conditioned TP/FP/FN sweep finds accepted locked-lambda candidates at `psi_lambda = 0.10`; top candidate is `stability_heavy`, `psi_threshold = 0.30`.
2. CL09: topology lag is now stress-tested. Worst tested condition reaches `52.0` average wrong-monitoring steps.
3. CL05: v18 standalone hub boundary reproduces, but v0.2 integrated all-hub stress still overwhelms three hubs. Hub mitigation remains context-dependent.

## Requested Output Format

Return:

1. Top 5 findings, ordered by severity.
2. Direct contradictions with the source hierarchy, if any.
3. Whether v0.3 validly resolves CL02, CL09, and v18 hub reproduction.
4. What must be fixed before v0.4.
5. Files/connectors/plugins needed from QianJun, if any.

Be strict about wording:

- Say "calibration path found" for CL02 unless the main grand-sim matrix has been patched and rerun.
- Say "stress-tested" for CL09, not deployment-ready.
- Say "context-dependent hub mitigation," not "three hubs are safe" as a universal claim.
