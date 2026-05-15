# SOE Grand Sim v0.5 Multi-AI Consensus

Date: 2026-05-08

Input artifact: `C:\Users\M7120\Desktop\Multi AI Review.docx`

Extracted text: `SOE_Grand_Sim_v0_5_Multi_AI_Review_extracted.txt`

Reviewers represented: Grok, Gemini, ChatGPT, Copilot text-only, Claude. Le Chat could not access v0.5 files.

## Executive Verdict

v0.5 validly upgrades CL02 to:

> `supported_in_v0_5_transfer`

The no-regime `stability_heavy / psi_threshold = 0.30` federation detector transfers into the integrated main matrix with no federation C04 violations, no regime-term leakage, and no false positives in no-event federation runs.

This is still simulation evidence, not deployment readiness.

## Core Evidence

| Metric | Result |
|---|---:|
| Main-matrix runs | 420 |
| Step rows | 67,200 |
| Federation transfer rows | 120 |
| Positive federation event rows | 80 |
| No-event federation rows | 40 |
| On-time detections | 80 / 80 |
| Missed detections | 0 / 80 |
| False positives | 0 / 40 |
| On-time TPR | 1.0 |
| False-positive rate | 0.0 |
| Avg lead to `collapse_share >= 0.30` | 7.9875 |
| Federation `psi_w_regime` | 0.0 |
| Federation C04 Trigger A violations | 0 |

## Consensus Findings

1. **CL02 transfer succeeds.** Grok, Gemini, ChatGPT, and Claude agree the conservative no-regime detector validly transfers into the main matrix.

2. **Lead time compresses under integration.** v0.4 focused lead was about `10.94`; v0.5 integrated lead is `7.9875`. This is acceptable but should be reported clearly.

3. **Two positive runs have zero lead.** Both are `psi_corruption / mid_stress`; detection occurs at the event step. CL02 remains on-time, but not every detection is early.

4. **No source-hierarchy contradiction was found.** Federation Trigger A uses C07 `Psi_extended`; non-federation Trigger A remains C04 S-threshold; `f_min` and `kappa_min` remain distinct.

5. **Copilot's text-only cautions were addressed locally.** Additional validation artifacts check required columns, non-federation Trigger A sources, runtime `psi_term_regime = 0.0`, threshold sensitivity, lead distribution, and sample step traces.

## Caveats

- Do not say deployment-ready.
- Do not say final architecture proof.
- Do not say every positive run has positive lead.
- Do not revive `regime_heavy` or `v02_default / 0.22` as defaults.

## Next Batch

Go for v0.6 focused on the remaining non-CL02 issues:

1. CL09: integrate topology lag/misclassification into the main matrix.
2. CL05: add integrated unbalanced hub scenarios.
3. CL10: add harsher resource-budget/routing-delay stress.
4. Optional: adversarial Psi stress later, including stability-term ablation and high-variance/no-collapse federation cases.

## Go/No-Go

Go for v0.6.

No-go for deployment readiness.
