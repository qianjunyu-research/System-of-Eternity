# SOE v3 Phase 1

This folder holds the isolated Phase 1 implementation for SOE v3.

The goal is to extend the existing v2 engine with new topology comparisons
without modifying the long-running `soe_simulation.py` branch directly.

## Scope

Phase 1 includes:

- `fully-connected`
- `chain`
- `star`
- `random-sparse`

Phase 1 intentionally does not include:

- heterogeneity
- resource constraints

## Files

- `soe_v2_core.py`: adapter into the current v2 simulation engine
- `soe_v3_topology.py`: Phase 1 topology builders
- `soe_v3_metrics.py`: failure, cascade, collapse, and survival-cluster metrics
- `soe_v3_runner.py`: runner and CLI for Phase 1 experiments

## Run

Single topology:

```powershell
python -m soe_v3.soe_v3_runner --topology chain --failure-policy highest-degree
```

All Phase 1 topologies:

```powershell
python -m soe_v3.soe_v3_runner --topology all --output soe_v3/outputs/phase1_summary.csv
```

Single topology with a fixed failure seed and CNI:

```powershell
python -m soe_v3.soe_v3_runner --topology star --failure-policy specific --failure-node-ids 0 --include-cni --output soe_v3/outputs/star_summary.json
```

## Notes

- The runner reuses the v2 civilization dynamics and swaps in the requested
  Phase 1 graph at initialization time.
- The random-sparse graph starts from a chain backbone so topology comparisons
  begin from a connected graph instead of mixing propagation with random
  initial fragmentation.
- Resource exhaustion is stubbed as an empty metric for now because the
  resource layer belongs to Phase 3.
