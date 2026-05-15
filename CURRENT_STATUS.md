# SOE Current Workspace Status

This workspace is intentionally in a quality-control pause before the full SOE upgrade.

## Active Direction

- Grand Simulation work is complete enough to support paper writing.
- The paper/manuscript thread is the active production lane.
- Full SOE upgrade should wait for Claude's independent audit when Claude is available again.
- Grok fast mode should not be treated as expert validation.

## Do Not Disturb Yet

Do not move or delete these while the paper thread is still active:

- `soe_grand_sim_v0_7.py`
- `grand_sim_v0_7`
- `rendered_paper_manuscript_v0_1`
- raw CSV evidence files used by the paper packet
- modified tracked Python files reported by `git status`

## Active Handoff Folders

The safest handoff folders are now under `00_ACTIVE_HANDOFFS`:

- `Claude_Catchup_Packet`
  - compact files for Claude to review once the limit clears
- `Current_Paper_Evidence_Packet`
  - claim table, methods, results, limitations, evidence consolidation, and reviewer prompt
- `SOE_Upgrade_Waiting_Room`
  - SOE Node v0.1 and upgrade-adjacent materials to hold until after paper freeze and Claude audit

These folders currently contain copied files, not moved originals. The root evidence trail is preserved.

## Cleanup Policy

- Empty mistaken folders can be deleted after verification.
- Temporary/render folders can be archived later.
- Research artifacts should be grouped or copied before deletion is considered.
- Final cleanup should happen after the current paper is frozen.

## Cleanup Already Done

- Deleted empty mistaken `New project`, `New project 2`, `New project 3`, `New project 4`, `New project 5`, and `New project 6` folders from Documents.
- Deleted empty obsolete rendered-output folders.
- Deleted Python `__pycache__` folders.
- Deleted LibreOffice/render working folders named `lo_render_tmp*`.
- Preserved Grand Simulation outputs, raw CSV evidence, rendered final outputs, review packets, scripts, and modified tracked source files.

## Wider Computer Cleanup Done

- Excluded `C:\Users\M7120\Desktop\VolkNet` from cleanup.
- Deleted `C:\Users\M7120\Downloads\LibreOffice_26.2.3_Win_x86-64.msi` after verifying LibreOffice is installed in `C:\Program Files\LibreOffice`.
- Deleted old user-temp files older than 7 days from `C:\Users\M7120\AppData\Local\Temp`.
- Removed about 6.2 GB total, mostly old temp archive fragments and installer leftovers.
- Preserved the Downloads copy of `SOE Architecture v2 Integration Snapshot.docx`.

## Additional PC Optimization Done

- Deleted crash dumps from `C:\Users\M7120\AppData\Local\CrashDumps`.
- Deleted Python package cache files from `C:\Users\M7120\AppData\Local\pip\Cache`.
- Removed about 827 MB in this additional pass.

## Optimization Candidates Not Changed

- `C:\Users\M7120\AppData\Local\NVIDIA\DXCache` is about 9.7 GB. It is rebuildable shader cache, but deleting it can cause temporary game stutter, so it was left intact.
- Recycle Bin has about 421 MB. It was left intact because emptying it is permanent.
- Startup apps include Steam, QQ, UC Cloud/Browser, uTorrent, MuMu Player, Player2, Proton VPN/Drive, Adobe sync, CurseForge, Discord, and Grammarly. These were only audited, not disabled.
- `C:\Users\M7120\.cache\codex-runtimes` is about 769 MB and was preserved because Codex uses it.
