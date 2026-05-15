# Claude Demand Packet

Purpose: give Claude the files requested for independent SOE grand-simulation architecture audit.

Recommended audit order:

1. `00_prompt/SOE_Grand_Sim_Multi_AI_Review_Prompt_v0_1.md`
2. `01_grand_sim/SOE_Grand_Simulation_Spec_v0_1.md`
3. `01_grand_sim/soe_grand_sim_v0_1.py`
4. `02_architecture_sources/SOE_Governance_Architecture_v0_3_extracted.txt`
5. `02_architecture_sources/governance_architecture_extracts/SOE_C02_RecoveryEngine_v2_1.txt`
6. `02_architecture_sources/governance_architecture_extracts/SOE_C04_SLM_v2_3.txt`
7. `02_architecture_sources/governance_architecture_extracts/SOE_C05_SSL_v2_1.txt`
8. `02_architecture_sources/governance_architecture_extracts/SOE_C07_MetaGovernance_v2_2.txt`
9. `04_grand_sim_outputs/grand_sim_v0_1_report.md`
10. `04_grand_sim_outputs/grand_sim_v0_1_traceability.csv`
11. `04_grand_sim_outputs/grand_sim_v0_1_scenario_summary.csv`

Notes:

- The separate extracted component update files currently available locally are C00, C02, C04, C05, and C07. The full `SOE Architecture v2 Integration Snapshot.txt` is included because it contains the broader C01-C08 architecture and v17 addenda context.
- `grand_sim_v0_1_steps.csv` is included but large; use it only when checking detector timing or step-level hidden-collapse claims.
- Treat Codex's v0.1 simulation as reproducible audit material, not source of truth.
- Most important anomaly to audit: v0.1 does not reproduce v18's clean "3 hubs safe" boundary under integrated stress. Determine whether that is a model bug, parameter artifact, or real architecture warning.

Packet layout:

| Folder | Contents |
|---|---|
| `00_prompt` | Multi-AI review prompt and role instructions. |
| `01_grand_sim` | Spec and executable implementation. |
| `02_architecture_sources` | v0.3 architecture synthesis and component extracts. |
| `03_prior_evidence` | v18/v19/star/hub prior packets and summary CSVs. |
| `04_grand_sim_outputs` | v0.1 outputs, including report, traceability, run, summary, and step CSVs. |
