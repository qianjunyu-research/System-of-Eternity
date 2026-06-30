# SOE Hostile Sprint Evidence Register Metadata Addendum

Status: METADATA ADDENDUM FOR NEXT PACKET / NO EXECUTION AUTHORIZED

Date: 2026-06-22

## 1. Purpose

The folder 48 evidence register was accepted as sufficient for planning acceptance because it preserved raw paragraph locators and did not claim false convergence.

Future review returns should use a fuller metadata schema so that reviewers can reconstruct what each AI saw and when.

## 2. Required Columns for Future Review Registers

Future hostile-sprint evidence registers should include these columns:

| Column | Purpose |
|---|---|
| Reviewer / system | Which AI or human review lane returned the finding |
| Model or tier if known | Visible model, mode, or tier when available |
| Review date | Date the return was produced |
| Reviewed packet version | Exact folder or zip reviewed |
| Prior-review visibility | Whether the reviewer saw prior AI reviews |
| Raw source location | File, paragraph, or returned document locator |
| Returned verdict | Exact verdict token if supplied |
| Binding status | Accepted, rejected, nonbinding, or informational |
| Serious minority finding? | Whether the finding triggers worst-case inheritance |
| Disposition | How the finding was handled |
| Closure evidence | Artifact or dated decision that closes it |

## 3. Treatment of Scanner-Style Returns

Scanner-style returns may be useful for quick sanity checks, but they must not be treated as controlling if they:

- invent file names not present in the packet
- report missing versions that exist on disk
- convert planning acceptance into execution readiness
- ignore explicit no-execution boundary language
- fail to distinguish reviewed folder contents from inferred project state

The late "Vibe" block in the returned review is therefore treated as nonbinding. Its useful caution is retained: execution-language drift must be blocked.

## 4. Carry-Forward Requirement

The next RCC-01 design or execution-preparation packet must include this metadata schema or explicitly explain why a narrower schema is sufficient.

