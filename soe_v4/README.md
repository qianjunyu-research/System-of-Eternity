# SOE v4 / v4.1 Simulation Suite

This folder holds the GitHub-ready simulation layer for `SOE_V4.docx` and
`SOE_V4_1.docx`.

It keeps the earlier SOE findings as priors, but makes the V4 structure explicit:

- core state variables: `T` trust, `D` disturbance, `C` cognitive distortion, `I` identity stability, `S` stability
- V4 layers: meta-governance, coordination, re-entry, identity repair, upgrade path, and exit pressure
- companion-doc constraints: trust-centered dynamics, thresholded recovery, bounded local propagation, and regime-sensitive claims

The packaged reference document is `docs/SOE_V4_1.docx`.

## Main files

- `soe_v4_sim.py`: V4 runner, scenario suite, CSV writer, and markdown report generator
- `claude_brief_suite.py`: the Claude-brief validation runner
- `full_campaign.py`: the full multi-phase validation campaign

## Committed outputs

The repository keeps compact reports and summary tables only:

- `outputs/soe_v4_report.md`
- `outputs/claude_brief/`
- `outputs/full_campaign/`

Large raw run CSVs are intentionally ignored to keep the branch reviewable on
GitHub.

## Run

```powershell
python -m soe_v4.soe_v4_sim
```

Faster smoke run:

```powershell
python -m soe_v4.soe_v4_sim --runs 8 --years 240 --nodes 18
```

Outputs are written to `soe_v4/outputs/` by default.
