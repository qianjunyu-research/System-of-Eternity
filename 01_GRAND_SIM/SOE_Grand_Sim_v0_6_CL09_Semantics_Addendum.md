# SOE Grand Simulation v0.6 - CL09 Semantics Addendum

## Purpose

Reviewers agreed that v0.6 successfully introduced topology wrong-monitoring windows. The remaining wording risk is that `wrong-monitoring` can be mistaken for `topology false stability`.

## Definitions

`topology_wrong_monitoring = 1` when:

```text
actual_topology != detected_topology
```

This measures stale or misclassified topology maps.

`topology_false_stability = 1` in v0.6 when:

```text
actual_topology != detected_topology
AND detected_topology == "ring_mesh"
AND collapse_share > 0.10
AND S_network > COLLAPSE_S_THRESHOLD
```

This is narrower. It asks whether the system is using a ring-mesh map while actual collapse is already present and the stability readout still looks above the collapse threshold.

## v0.6 Result

- Wrong-monitoring windows are real and large: average 46.67 steps across topology stress scenarios, max 65.
- Topology false-stability stayed 0.

## Interpretation

This means v0.6 supports the claim that topology monitoring can remain stale/misclassified inside the integrated matrix. It does not yet show that this stale map directly creates hidden collapse or a false-stable operational state.

The zero false-stability result may mean either:

1. Other detectors still compensate under these conditions.
2. The v0.6 topology false-stability metric is too narrow.

v0.7 should test this directly with a topology-specific false-stability rule:

```text
actual_topology != detected_topology
AND no topology-aware trigger fired
AND collapse_share or max_cluster_collapse_share is rising
```

## Correct Status

Recommended status:

```text
CL09 supported_in_v0_6_stress, with qualifier
```

Recommended wording:

```text
Wrong-monitoring windows confirmed; topology-induced false stability not observed in v0.6.
```
