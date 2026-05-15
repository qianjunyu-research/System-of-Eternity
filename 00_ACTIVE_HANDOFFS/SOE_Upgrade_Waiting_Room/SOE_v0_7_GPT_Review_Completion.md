# SOE v0.7 GPT Review Completion

Status: late v0.7 review completion from GPT, incorporated as consensus support with one correction.

## Verdict

Pass with caveats.

v0.7 is sufficient to begin:

- paper-evidence consolidation
- Governance Architecture wording freeze
- Node/container v0.1 planning as a bounded planning/audit packet

v0.7 is not sufficient for:

- deployment readiness
- container execution readiness
- real-world implementation

No v0.8 is required before paper-evidence consolidation unless another reviewer finds a source-hierarchy contradiction, reproducibility failure, or a claim that cannot be fixed by wording.

## Review Findings

1. CL09 is impact-tested, but narrowly.
   - Average latency: `46.666667`.
   - Average wrong-monitoring: `46.666667`.
   - Average hidden-collapse overlap: `0.244444`.
   - Maximum wrong window: `65`.
   - Correct wording: CL09 is impact-tested for stale-topology / hidden-collapse overlap; broad blind false-stability was not established.

2. CL02 regression holds, but CL02A exposes detector dependency.
   - Default on-time TPR: `1.0`.
   - Default false-positive rate: `0.0`.
   - Average lead: `8.175`.
   - Stability-term ablation on-time TPR: `0.0`.
   - Average ablation lead: `-4.1`.
   - Required wording: `Psi_extended` is a stability-heavy precursor detector under the tested configuration.

3. CL05 remains context-dependent.
   - Three hubs are context-dependent mitigation under localized/unbalanced conditions.
   - Three hubs are not mesh equivalence or universal hub safety.

4. CL10 remains harsh but useful.
   - Stress exhaustion: `1.0`.
   - Pressure exhaustion: `1.0`.
   - The useful gradient is floor duration and routing-delay loss, not exhaustion incidence.

5. No source-hierarchy contradiction appears.
   - Federation Trigger A: C07 `Psi_extended`.
   - Non-federation Trigger A: C04 S-threshold allowed.
   - `psi_lambda = 0.10`.
   - Federation `psi_threshold = 0.30`.
   - `psi_w_regime = 0.0`.
   - `f_min = 0.30` and `kappa_min = 0.25` remain distinct.

## Correction To Preserve

GPT stated that topology false-stability remains `0.0`. The raw v0.7 topology-impact summary contains one nonzero case:

```text
topology_lag_resource_cascade / low_stress:
avg_hidden_collapse_steps = 6.2
avg_blind_no_trigger_steps = 0.0
avg_topology_false_stability_steps = 4.9
```

Therefore, the paper wording already used in v0.4 is more precise:

```text
Topology lag can overlap with hidden collapse; in one tested condition it produced a brief false-stability window.
```

## Final Safe Status Labels

| Claim | Final safe status |
|---|---|
| CL02 | `supported_in_v0_7_regression` |
| CL02A | `adversarial_measured_v0_7`; stability-term dependence required caveat |
| CL05 | `context_dependent_unbalanced_tested` |
| CL09 | `impact_tested_v0_7`; hidden-collapse overlap observed, broad blind false-stability not established |
| CL10 | `graded_stress_measured_v0_7`; gradient observed, recovery not proven |

## Impact On v0.4 Draft

No structural draft change required. The v0.4 draft already uses the corrected CL09 wording, preserves CL02A as a caveat, keeps CL05 context-dependent, and blocks deployment/container-execution claims.
