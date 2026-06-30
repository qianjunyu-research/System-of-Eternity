from pathlib import Path
import hashlib


BASE = Path(r"C:\Users\M7120\Desktop\System of Eternity\40_SOE_ARXIV_CSCY_REFRAMING_PACKET_2026-06-05")
META = BASE / "02_METADATA_AND_REVIEW"
DOCX = BASE / "01_REVISED_MANUSCRIPT" / "SOE_Paper_Manuscript_Draft_v0_7_csCY_Reframed_2026-06-05.docx"


README = """# READ FIRST - SOE arXiv cs.CY Reframing Packet

Date: 2026-06-05

Purpose: review a category-framing revision of the SOE Grand Simulation v0.7 manuscript for arXiv `cs.CY` (Computers and Society).

This packet does not reopen the simulation evidence. The simulation data, figures, detector results, traceability claims, and Zenodo companion archive remain unchanged from the v0.7 manuscript package.

Review target:

- `01_REVISED_MANUSCRIPT/SOE_Paper_Manuscript_Draft_v0_7_csCY_Reframed_2026-06-05.docx`

Source reference:

- `03_SOURCE_REFERENCE_NOT_FOR_UPLOAD/SOE_Paper_Manuscript_Draft_v0_7_Codex_source.docx`
- `03_SOURCE_REFERENCE_NOT_FOR_UPLOAD/soe_governance_architecture_grand_sim_v0_7_original_nlin_frame.pdf`

Review question:

Does the revised manuscript honestly fit `cs.CY` as computational governance / Computers and Society research without damaging the original simulation-evidence integrity?

Boundaries:

- Do not ask reviewers to approve deployment, empirical validation, policy adoption, or real-world governance use.
- Do not treat endorsement success as scientific validation.
- Do not alter simulation numbers or evidence conclusions merely for category fit.
- DawLyn Yu is acknowledged as non-author support; QianJun Yu remains sole author unless explicitly changed later.
"""


METADATA = """# arXiv Metadata To Paste - cs.CY Revision

## Title

Simulation-Bounded Governance Architecture: Computational Modeling of Institutional Stability in the System of Eternity

## Authors

QianJun Yu

## Primary category

cs.CY - Computers and Society

## Recommended comment field

7 pages, 3 figures. Companion archive DOI: 10.5281/zenodo.20144235. cs.CY framing revision; simulation evidence unchanged from Grand Simulation v0.7 manuscript package.

## Abstract

This manuscript presents the System of Eternity (SOE) Governance Architecture as a computational governance model for studying society-facing institutional stability under bounded simulation conditions. SOE is represented through theoretical variables T (trust), D (disturbance), C (cognition), I (identity), G (governance capacity), and S (stability). The paper consolidates the frozen v0.4 architecture base after Grand Simulation v0.7 (870 runs; 139,200 step rows; 29 scenarios) and interprets the resulting outputs as architecture-model evidence for claim-bounded public governance reasoning. In the tested matrix, federation monitoring uses C07 Psi_extended rather than the C04 S-threshold for federation Trigger A. Under the locked v0.7 configuration, Psi_extended produced on-time detections with mean lead 8.175 steps and zero false positives in audited no-event rows; stability-term ablation reduced on-time TPR to 0.0 and, at high stress, reversed mean lead to -4.1 steps. These results are simulation evidence only: they do not imply deployment readiness, empirical proxy validity, or governance authority sufficiency. The contribution is a computationally bounded governance-architecture manuscript with explicit claim-to-output traceability, separating simulation-supported public-institutional claims from deployment, policy authority, or real-world validation claims.

## Keywords

computers and society; computational governance; governance-system simulation; institutional modeling; governance architecture; simulation-level evidence; federation monitoring; stability-dependent detector; topology lag; resource-constrained recovery; claim-to-output traceability
"""


REVIEW = """# SEND TO MULTI-AI REVIEW - cs.CY Manuscript Reframing

Review the attached manuscript and answer in the exact verdict format below.

## Context

The manuscript was originally prepared under an `nlin.AO` / adaptive-systems framing. arXiv endorsement became available through `cs.CY`, so the front matter and category-facing language were revised to frame the same work as Computers and Society research: computational governance modeling, public institutional architecture, and simulation-bounded claims about governance systems.

The core simulation evidence must not be changed merely to fit a category. The review should check category fit, integrity, and overclaim risk.

## Files to read

1. `01_REVISED_MANUSCRIPT/SOE_Paper_Manuscript_Draft_v0_7_csCY_Reframed_2026-06-05.docx`
2. Optional source comparison: `03_SOURCE_REFERENCE_NOT_FOR_UPLOAD/SOE_Paper_Manuscript_Draft_v0_7_Codex_source.docx`
3. Optional original PDF: `03_SOURCE_REFERENCE_NOT_FOR_UPLOAD/soe_governance_architecture_grand_sim_v0_7_original_nlin_frame.pdf`

## Questions

1. Does the revised manuscript honestly fit `cs.CY - Computers and Society`?
2. Does the new title/abstract/intro make the category fit clearer without pretending the paper is software, machine learning, or a deployed system?
3. Are all simulation numbers and evidence claims preserved without distortion?
4. Are deployment, empirical validation, policy authority, real-world measurement, and governance-readiness claims still blocked?
5. Is the DawLyn Yu acknowledgment safe as a non-author contribution note?
6. What exact patches, if any, are required before arXiv upload?

## Verdict options

Use exactly one:

```text
ACCEPT_CSCY_REFRAMED_ARXIV_MANUSCRIPT
PATCH_NEEDED_CSCY_REFRAMED_ARXIV_MANUSCRIPT
BLOCKER_CSCY_CATEGORY_OR_OVERCLAIM
```

## Required answer format

```text
Verdict:

Findings:

Required patches:

Overclaim/category concern:

Can this be used for arXiv cs.CY upload after local PDF/export QA?
```
"""


SUMMARY = """# cs.CY Reframing Change Summary

This packet applies an arXiv category-facing revision only. It does not reopen or alter the Grand Simulation v0.7 evidence.

## Changed

- Title changed to emphasize simulation-bounded computational governance.
- Subtitle changed to make institutional-stability modeling visible.
- Abstract reframed around computational governance, society-facing institutional stability, and claim-bounded simulation evidence.
- Keywords expanded with `computers and society`, `computational governance`, `governance-system simulation`, and `institutional modeling`.
- Introduction now includes a category-positioning paragraph for `cs.CY`.
- Contribution statement now names the Computers and Society framing explicitly.
- Limitations add a line clarifying that `cs.CY` framing does not convert SOE into a deployed computing system, policy instrument, or validated socio-technical measurement framework.
- Conclusion now frames the submission path as Computers and Society while preserving all evidence boundaries.
- Added `Acknowledgments and Contribution Note` for DawLyn Yu as non-author support.

## Not changed

- Simulation run count: 870 runs.
- Step rows: 139,200.
- Scenario count: 29.
- CL02 mean lead: 8.175 steps.
- CL02 no-event false positives: zero in audited rows.
- CL02A ablation: on-time TPR 0.0 at low/mid and high-stress mean lead -4.1.
- Companion archive DOI: 10.5281/zenodo.20144235.
- Deployment and empirical-validation boundary language.
"""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    META.mkdir(parents=True, exist_ok=True)
    files = {
        "README_CSCY_REFRAMING_PACKET_2026-06-05.md": README,
        "ARXIV_METADATA_TO_PASTE_csCY_2026-06-05.md": METADATA,
        "SEND_TO_MULTI_AI_CSCY_MANUSCRIPT_REVIEW_2026-06-05.md": REVIEW,
        "CSCY_REFRAMING_CHANGE_SUMMARY_2026-06-05.md": SUMMARY,
    }
    for name, text in files.items():
        (META / name).write_text(text, encoding="utf-8", newline="\n")

    rows = ["# File Manifest - cs.CY Reframing Packet", "", "| File | Bytes | SHA-256 |", "|---|---:|---|"]
    for path in sorted(BASE.rglob("*")):
        if path.is_file():
            rel = path.relative_to(BASE).as_posix()
            rows.append(f"| `{rel}` | {path.stat().st_size} | `{sha256(path)}` |")
    (BASE / "FILE_MANIFEST_CSCY_REFRAMING_PACKET_2026-06-05.md").write_text(
        "\n".join(rows) + "\n", encoding="utf-8", newline="\n"
    )
    print(BASE)


if __name__ == "__main__":
    main()
