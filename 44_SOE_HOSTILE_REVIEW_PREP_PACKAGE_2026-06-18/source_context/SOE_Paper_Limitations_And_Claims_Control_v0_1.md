# SOE Paper Limitations And Claims Control v0.1

## Purpose

This file prevents the paper from overclaiming the v0.7 simulation evidence.

## Core Limitation Statement

The v0.7 Grand Simulation is reproducible simulation evidence for a declared architecture and scenario matrix. It is not deployment evidence, field validation, or proof that the SOE variables are validated real-world proxies.

## Required Caveats By Claim

### CL02 / CL02A: Federation Detection

Paper-safe wording:

```text
The tested `Psi_extended` configuration detects federation collapse precursors in the simulation with on-time TPR 1.0 and false-positive rate 0.0. However, adversarial ablation shows this performance depends materially on the stability term.
```

Do not claim:

```text
Psi_extended is an independent precursor detector.
Psi_extended is robust to removal or manipulation of stability signals.
```

### CL05: Hub Mitigation

Paper-safe wording:

```text
Three hubs mitigate specific single-hub and unbalanced-primary failure modes but do not provide mesh equivalence and do not survive simultaneous all-hub stress.
```

Do not claim:

```text
Three hubs are safe.
Three hubs solve hub fragility.
Three hubs are equivalent to federation or mesh redundancy.
```

### CL06: H/I/A Identity

Paper-safe wording:

```text
The simulation preserves distinct H/I/A identity formulas and measures mixed-node behavior, but dedicated identity stress remains future work.
```

Do not claim:

```text
H/I/A identity dynamics are validated.
Identity proxies are ready for real-world scoring.
```

### CL09: Topology Lag

Paper-safe wording:

```text
Topology lag can overlap with hidden collapse; in one tested condition it produced a brief false-stability window.
```

Do not claim:

```text
Topology lag broadly creates undetected collapse across the matrix.
The detector is fully robust against topology lag.
```

### CL10: Finite Resources

Paper-safe wording:

```text
Resource stress produces meaningful gradients in floor duration and routing-delay loss. In the tested pressure scenarios, exhaustion incidence remains 100 percent.
```

Do not claim:

```text
Resource recovery is proven.
The architecture is operationally resource-safe.
```

## Readiness Labels

Allowed:

- architecture-ready
- simulation-ready
- simulation-level evidence
- paper-evidence consolidation
- bounded Node planning/audit packet

Blocked:

- deployment-ready
- operationally validated
- field-tested
- human-subject validated
- real-world governance proof

## Reviewer Red Flags

Ask reviewers to flag any sentence that:

1. Turns simulation evidence into deployment evidence.
2. Says `Psi_extended` is stability-independent.
3. Treats three hubs as universally safe.
4. Treats CL06 as stress-tested.
5. Treats resource exhaustion as solved.
6. Hides the difference between topology hidden-collapse overlap and blind false stability.
7. Uses "validated" without specifying "simulation-level."
