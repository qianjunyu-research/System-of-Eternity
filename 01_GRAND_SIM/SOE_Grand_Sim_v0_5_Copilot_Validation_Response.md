# SOE Grand Sim v0.5 - Copilot Validation Response

Purpose: answer Copilot's text-only caveats against the current v0.5 artifacts without changing the v0.5 claim language beyond the already conservative caveat.

## Verdict

CL02 can remain `supported_in_v0_5_transfer` as simulation-level evidence.

Copilot's requested checks are now represented as local audit artifacts. The only preserved caveat is that v0.5 proves perfect on-time detection at threshold 0.30, not positive early warning in every positive run.

## Check Results

| Check | Result |
|---|---:|
| Federation positive event rows | 80 |
| On-time detections | 80 / 80 |
| Positive-lead detections | 78 / 80 |
| Zero-lead positive detections | 2 / 80 |
| Late or missing positive detections | 0 / 80 |
| Federation false positives on no-event rows | 0 / 40 |
| Federation C04 Trigger A source violations | 0 |
| Non-federation C07 Psi Trigger A sources | 0 |
| Nonzero federation `psi_term_regime` at detect | 0 |
| Bad federation Trigger A source at detect | 0 |

## Interpretation

- The regime loop remains severed: `psi_term_regime` is 0.0 at federation detection in the audited rows.
- The source hierarchy holds: federation Trigger A is C07 `Psi_extended`; non-federation does not use C07 Psi sources.
- The detector is not universally early: 2 positive federation rows have lead 0, so public/cross-team wording must keep the on-time caveat.
- Leave-one-scenario-out does not show a single scenario carrying the result; every omitted-scenario subset preserves on-time TPR 1.0 and false-positive rate 0.0.
- The time-shift delay check behaves as expected: delaying the Psi signal degrades the on-time rate for thin-lead cases, which supports the claim that the measured lead margin matters rather than being a reporting artifact.

## New Audit Artifacts

- `grand_sim_v0_5_copilot_federation_run_excerpt.csv`
- `grand_sim_v0_5_copilot_nonfederation_trigger_excerpt.csv`
- `grand_sim_v0_5_copilot_step_trace_10_positive_runs.csv`
- `grand_sim_v0_5_copilot_detect_step_audit_rows.csv`
- `grand_sim_v0_5_copilot_lead_distribution_by_scenario_profile.csv`
- `grand_sim_v0_5_copilot_leave_one_scenario_out.csv`
- `grand_sim_v0_5_copilot_timeshift_sensitivity.csv`

## Reproducibility Snapshot

Command:

```powershell
& "C:\Users\M7120\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" "C:\Users\M7120\Documents\New project 7\soe_grand_sim_v0_5.py"
```

Script SHA256: `4959112c299030a1feabc79287c999b770a83d755a49fb0f32ef50fa8c34acd7`

Runs CSV SHA256: `f001777ade7b46a408f2a761b38b08de42535383a48cce3871583a6725fc7e63`

Steps CSV SHA256: `e5398d65e44f7585159cfc1955816cfad566dfa23ee5bf1f6ab352798bdf2bc3`

Seed range: 9300 to 9719 (420 unique seeds).

Config snippet:

```python
BATCH_ID = "grand_sim_v0_5"
OUTPUT_PREFIX = BATCH_ID
SEED_START = 9300
PSI_LAMBDA = 0.10
PSI_WEIGHT_PROFILE = "stability_heavy_no_regime"
PSI_W_T = 0.20
PSI_W_D = 0.20
PSI_W_G = 0.15
PSI_W_S = 0.35
PSI_W_REGIME = 0.0
FEDERATION_PSI_THRESHOLD = 0.30
FEDERATION_EVENT_THRESHOLD = 0.30
            psi_threshold=FEDERATION_PSI_THRESHOLD,
            psi_threshold=FEDERATION_PSI_THRESHOLD,
            psi_threshold=FEDERATION_PSI_THRESHOLD,
    term_t = PSI_W_T * (1.0 - t_mean)
    term_d = PSI_W_D * d_mean
    term_g = PSI_W_G * (1.0 - g_effective)
    term_s = PSI_W_S * (1.0 - s_network)
    term_variance = PSI_LAMBDA * variance
            trigger_a = int(psi_extended >= FEDERATION_PSI_THRESHOLD)
        if current_collapse_share >= FEDERATION_EVENT_THRESHOLD:
                "batch_id": BATCH_ID,
                "psi_weight_profile": PSI_WEIGHT_PROFILE,
                "psi_threshold_active": FEDERATION_PSI_THRESHOLD if actual_topology == "federation" else "",
                "psi_w_t": PSI_W_T,
                "psi_w_d": PSI_W_D,
                "psi_w_g": PSI_W_G,
                "psi_w_s": PSI_W_S,
                "psi_w_regime": PSI_W_REGIME,
        "batch_id": BATCH_ID,
        "psi_lambda": PSI_LAMBDA,
        "psi_weight_profile": PSI_WEIGHT_PROFILE if scenario.topology == "federation" else "",
        "psi_threshold": FEDERATION_PSI_THRESHOLD if scenario.topology == "federation" else profile.psi_threshold,
        "psi_w_t": PSI_W_T if scenario.topology == "federation" else "",
        "psi_w_d": PSI_W_D if scenario.topology == "federation" else "",
        "psi_w_g": PSI_W_G if scenario.topology == "federation" else "",
        "psi_w_s": PSI_W_S if scenario.topology == "federation" else "",
        "psi_w_regime": PSI_W_REGIME if scenario.topology == "federation" else "",
                "batch_id": BATCH_ID,
        f"- Federation Psi profile: `{PSI_WEIGHT_PROFILE}`.",
        f"- Federation Psi weights: `T={PSI_W_T}`, `D={PSI_W_D}`, `G={PSI_W_G}`, `S={PSI_W_S}`, `regime={PSI_W_REGIME}`.",
        f"- Federation Psi threshold: `{FEDERATION_PSI_THRESHOLD}`.",
        f"- Locked `psi_lambda`: `{PSI_LAMBDA}`.",
    parser.add_argument("--seed-start", type=int, default=SEED_START)
```

## v0.6 Go/No-Go

Go for v0.6.

Priority remains:
1. CL09 topology lag/misclassification in the main matrix.
2. CL05 integrated unbalanced hub scenarios.
3. CL10 harsher resource-budget and routing-delay stress.

Do not upgrade to deployment-ready language.
