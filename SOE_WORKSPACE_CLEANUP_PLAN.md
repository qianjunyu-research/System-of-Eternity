# SOE Workspace Cleanup Plan

Purpose: make `C:\Users\M7120\Documents\New project 7` easier to use without losing audit evidence, breaking reproducibility, or mixing active SOE upgrade work with older simulation debris.

## Current State

The root folder currently mixes several different classes of material:

- active source code and tests
- Grand Simulation v0.1-v0.7 scripts, outputs, findings, prompts, and review packets
- governance architecture extracts and rendered document outputs
- paper evidence packet files
- SOE Node v0.1 files
- older v13/v18/v19/wave-boundary simulation outputs
- LibreOffice/render temporary folders
- many untracked Git files

The repository also has modified tracked source files:

- `governance_integration.py`
- `governance_loop_sim.py`
- `governance_network_sim.py`
- `governance_regime_scan.py`
- `soe_simulation.py`

These should not be moved or overwritten during cleanup unless the active coding thread explicitly says so.

## Cleanup Principle

Do not delete research artifacts. Archive or group them with clear names.

For SOE quality control, the workspace should preserve:

- source hierarchy
- simulation version history
- reviewer packets
- final/frozen outputs
- paper evidence chain
- Claude catch-up material

Temporary render folders and duplicate extraction files can be moved later, but only after the current final paper thread no longer needs them.

## Proposed Top-Level Layout

Recommended future layout:

- `00_ACTIVE_HANDOFFS`
  - files currently meant for Claude, GPT, Gemini, Le Chat, Copilot, or human review
- `01_GRAND_SIM`
  - Grand Simulation scripts, version folders, findings, consensus files, and output packets
- `02_PAPER_AND_EVIDENCE`
  - paper inserts, claim-status tables, limitations, methods, and reviewer prompts
- `03_GOVERNANCE_ARCHITECTURE`
  - architecture extracts, rendered architecture versions, freeze candidates, and audit notes
- `04_NODE_SPEC`
  - SOE Node v0.1 execution spec, daily log template, gate criteria, normalization spec, and review files
- `05_PRIOR_SIM_HISTORY`
  - v13, v18, v19, wave-boundary, star/hub, federation, and older governance simulations
- `90_ARCHIVE_RENDER_OUTPUTS`
  - rendered document folders and render QA outputs
- `99_TEMP_LOCAL`
  - LibreOffice temp folders, `__pycache__`, scratch extraction files

## Safe First Cleanup

The safest first pass is:

1. Create the folder layout above.
2. Copy or move only obvious derivative packets and rendered outputs.
3. Leave tracked code, tests, and active root scripts in place.
4. Leave raw CSV evidence in place until a manifest exists.
5. Create a root `CURRENT_STATUS.md` that says what is active, what is frozen, and what Claude still needs to review.

## High-Risk Items

Do not move these yet:

- active modified tracked Python files
- `soe_grand_sim_v0_7.py`
- `grand_sim_v0_7`
- current paper manuscript/render folders until the paper thread is done
- raw CSV files used by paper evidence tables
- any file referenced by the current paper draft or Claude packet

## Suggested Next Action

Create a non-destructive handoff folder first:

- `00_ACTIVE_HANDOFFS/Claude_Catchup_Packet`
- `00_ACTIVE_HANDOFFS/Current_Paper_Evidence_Packet`
- `00_ACTIVE_HANDOFFS/SOE_Upgrade_Waiting_Room`

Then move/copy only the small markdown, docx, and CSV files needed for review. Keep the large raw simulation folders where they are until the final paper has been checked.
