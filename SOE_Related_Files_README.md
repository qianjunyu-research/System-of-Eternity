# SOE Related Files Packet

Purpose: broader context library for AIs reviewing SOE grand simulation work. This is not the sharp audit packet; `Claude's demand` is the shortest path for the immediate v0.1 audit.

Recommended use:

1. Start with `00_current_grand_sim` if reviewing the current v0.1 batch.
2. Use `01_architecture_and_drafts` to check source-language and paper-history context.
3. Use `02_prior_packets` for prior handoff packets and run summaries.
4. Use `03_prior_code_and_tests` when checking whether v0.1 diverged from earlier executable assumptions.
5. Use `04_soe_v4_context` if connecting governance-architecture results back to SOE V4/V4.1 simulation work.

## What Is Included

| Folder | Contents |
|---|---|
| `00_current_grand_sim` | Current v0.1 prompt, spec, script, report, traceability, scenario summary, and run summary. The huge step CSV is not duplicated here. |
| `01_architecture_and_drafts` | Architecture extracts, v0.1-v0.3 governance drafts, arXiv/paper extracted text, parameter skeleton, and SOE V4.1 docx. |
| `02_prior_packets` | v13/v18/v19 handoff packets, prior summary CSVs, star/hub/federation/Psi summaries. |
| `03_prior_code_and_tests` | Prior simulation scripts and pytest files most relevant to v0.1 audit. |
| `04_soe_v4_context` | SOE v4 package, output reports, and compact CSVs from V4/V4.1 campaigns. |

## Large Raw Files Not Included By Default

Ask QianJun/Codex for these only if needed:

- `grand_sim_v0_1/grand_sim_v0_1_steps.csv` is in `Claude's demand/04_grand_sim_outputs` already.
- Large raw prior CSVs such as `aggregation_comparison_runs.csv`, `psi_variance_runs.csv`, `v13_blocking_diagnostic_runs.csv`, `v19_ssl_dynamics_runs.csv`, and topology compare raw runs are left in the workspace.
- Full rendered document folders are left in the workspace.

## Audit Reminder

Do not treat any Codex-produced simulation as source of truth by itself. Check whether the executable faithfully translates the architecture source hierarchy:

- C04 v2.3 and C07 v2.2 for federation monitoring.
- C02 v2.1 for T-G loop break condition.
- C05 v2.1 for H/I/A node classes.
- C08 v2.0 plus v17 addendum for async/message loss/coordination expectations.

The central v0.1 anomaly is that the integrated model does not reproduce v18's clean "3 hubs safe" boundary. Decide whether that is an implementation issue, parameter artifact, or architecture warning.
