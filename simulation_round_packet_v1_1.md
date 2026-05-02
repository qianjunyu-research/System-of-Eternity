# Buffer v1.1 — Simulation Round Packet (2026-04-26)

## Run Context
- Round type: **Simulation round** (not review).
- External source docs: attempted retrieval from the three provided Google Docs links, but this environment cannot reach docs.google.com (HTTP 403 tunnel failure).
- Execution fallback: ran the requested simulation/diagnostic directly in-repo using available models and produced output artifacts.

## C3 Star Topology Simulation
Command:
`python soe_simulation.py --years 500 --topology star --runs 100 --output c3_star_topology_runs.csv`

Key outcomes:
- Survived final year: **91%**
- Avg final governance stability: **0.912**
- Avg final human control index: **1.000**
- Avg final connected components: **1.000**
- Contagion containment: **0.010**
- Collapse rate: **0%**
- Recovery rate: **100%**

Artifact:
- `c3_star_topology_runs.csv`

## Action List
1. Treat star-topology C3 as operationally stable under the tested envelope.
2. Keep human control safeguards unchanged for next round (human control remained at 1.000).
3. Add targeted disturbance stress around the star hub in the next batch to test single-point fragility.
4. Run a comparative C3 sweep: `star` vs `small-world` vs `federation` with matched seeds.
5. If you provide Drive access/exported text, I will align terminology and thresholds exactly to your governance module language.

## Governance Section (from Governance Module v1.0 diagnostic run)
Command:
`python governance_regime_scan.py --runs 50 --steps 120 --output rewired_governance_diagnostic_summary.csv --raw-output rewired_governance_diagnostic_runs.csv`

Diagnostic snapshot:
- `baseline_integrated`: stable_run_rate=1.000, failure_rate=0.000, avg_final_stability=1.000
- `capacity_060`: stable_run_rate=1.000, failure_rate=0.000, avg_final_stability=0.990
- `capacity_040`: stable_run_rate=0.640, failure_rate=0.040, avg_final_stability=0.954
- `smoothing_low`: stable_run_rate=1.000, failure_rate=0.000, avg_final_stability=1.000
- `disturbance_high`: stable_run_rate=0.160, failure_rate=0.080, avg_final_stability=0.934
- `combined_constraint`: stable_run_rate=0.000, failure_rate=0.840, avg_final_stability=0.578

Interpretation:
- The rewired governance controller appears robust in baseline and mild-capacity-constrained regimes.
- Failure concentrates under combined capacity + disturbance pressure.
- Disturbance becomes the dominant first-binding channel in stressed regimes, indicating the next optimization should prioritize disturbance damping under constrained capacity.

Artifacts:
- `rewired_governance_diagnostic_summary.csv`
- `rewired_governance_diagnostic_runs.csv`
- `simulation_round_raw_data_pack.txt` (combined raw dump for quick transfer)
