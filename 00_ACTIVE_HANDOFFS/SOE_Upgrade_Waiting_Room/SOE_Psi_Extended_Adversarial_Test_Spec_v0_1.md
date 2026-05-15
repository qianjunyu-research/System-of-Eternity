# SOE Psi_extended Adversarial Test Specification v0.1

Status: simulation/test specification. Not yet executed.

Date: 2026-05-12

## 1. Purpose

Grand Simulation v0.7 supports `Psi_extended` as the C07 federation detector under the locked simulation configuration. CL02A also shows that detector performance depends materially on the stability term.

This test spec defines the next required adversarial and circularity tests before any pilot or deployment language can be used.

## 2. Current Evidence Boundary

Frozen v0.7 claim:

```text
Under the locked v0.7 simulation configuration, Psi_extended detected federation collapse precursors with on-time TPR 1.0, false-positive rate 0.0, and average lead 8.175.
```

Required caveat:

```text
Stability-term ablation produced on-time TPR 0.0 and average lead -4.1. Psi_extended is stability-heavy under the tested configuration.
```

Blocked claims until this spec is executed:

- stability-independent detector,
- adversarially robust detector,
- empirical early-warning system,
- deployment monitor,
- real-world safety detector.

## 3. Test Matrix

| Test ID | Test | Purpose |
|---|---|---|
| PSI-A01 | Stability clamp | Clamp S externally to test whether detector is reading collapse or reading its own dependent signal. |
| PSI-A02 | Stability spoof | Inject false-stability signals while collapse dynamics proceed. |
| PSI-A03 | Stability delay | Delay S updates relative to T/D/C/G. |
| PSI-A04 | Stability corruption | Add targeted noise/manipulation to S. |
| PSI-A05 | Threshold gaming | Adversary injects D/C pulses designed to stay just below `psi_threshold=0.30`. |
| PSI-A06 | Moving-average reset | Adversary times pulses to reset/desynchronize detector windows. |
| PSI-A07 | Operator threshold drift | Psi operator shifts threshold from 0.30 to 0.35/0.40/0.45. |
| PSI-A08 | Topology misclassification | Combine stale topology detection with federation detector stress. |
| PSI-A09 | Independent-signal comparison | Compare Psi_extended against non-S-dependent detector variants. |
| PSI-A10 | Holdout scenarios | Run on unseen scenarios/profiles not used for v0.7 tuning. |

## 4. Required Outputs

Run-level outputs:

- scenario,
- profile,
- seed,
- topology,
- adversary type,
- threshold,
- Psi weights,
- S manipulation type,
- positive event flag,
- trigger A source,
- trigger first step,
- collapse30 first step,
- lead to collapse30,
- false positive flag,
- false negative flag,
- source-hierarchy violation flag.

Step-level outputs:

- T_mean,
- T_min,
- D_effective_mean,
- C_mean,
- I_mean,
- S_network_true,
- S_network_observed,
- G_formal,
- G_effective,
- psi_base,
- psi_extended,
- cluster_variance,
- trigger_A,
- trigger_A_source,
- topology_actual,
- topology_detected,
- adversary_action,
- collapse_share.

Summary outputs:

- confusion matrix per scenario,
- TPR,
- FPR,
- FNR,
- mean/median lead,
- late detection rate,
- no-event false positives,
- threshold sensitivity,
- S-corruption sensitivity,
- topology-misclassification sensitivity,
- source-hierarchy violations.

## 5. Pass/Fail Framing

Passing this test does not make `Psi_extended` deployment-ready. It can only upgrade the claim to:

```text
Psi_extended passed the defined adversarial/circularity simulation matrix under tested conditions.
```

Failure outcomes should be preserved as design information, not hidden.

## 6. Acceptance Criteria for Simulation-Ready Status

This spec becomes simulation-ready when:

- exact scenario count is defined,
- seeds are fixed or generated reproducibly,
- adversary functions are coded,
- all required outputs are emitted,
- validation checks verify source hierarchy,
- expected failure interpretations are pre-registered.

## 7. Governance Patch Requirement

Governance Architecture v0.5 should state:

```text
Psi_extended remains a simulation-supported federation detector under v0.7. Its stability dependence requires adversarial and circularity testing before pilot or deployment claims.
```
