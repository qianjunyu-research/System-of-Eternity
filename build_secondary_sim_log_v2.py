from __future__ import annotations

import zipfile
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

ET.register_namespace("w", W_NS)
ET.register_namespace("r", R_NS)


def w_tag(name: str) -> str:
    return f"{{{W_NS}}}{name}"


def add_run(paragraph: ET.Element, text: str, *, bold: bool = False, size: int | None = None) -> None:
    run = ET.SubElement(paragraph, w_tag("r"))
    if bold or size is not None:
        run_props = ET.SubElement(run, w_tag("rPr"))
        if bold:
            ET.SubElement(run_props, w_tag("b"))
        if size is not None:
            ET.SubElement(run_props, w_tag("sz"), {w_tag("val"): str(size)})
            ET.SubElement(run_props, w_tag("szCs"), {w_tag("val"): str(size)})
    text_el = ET.SubElement(run, w_tag("t"))
    if text.startswith(" ") or text.endswith(" "):
        text_el.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    text_el.text = text


def add_paragraph(
    body: ET.Element,
    text: str = "",
    *,
    bold: bool = False,
    size: int | None = None,
    align: str | None = None,
    spacing_before: int | None = None,
    spacing_after: int | None = None,
) -> ET.Element:
    paragraph = ET.SubElement(body, w_tag("p"))
    if align is not None or spacing_before is not None or spacing_after is not None:
        props = ET.SubElement(paragraph, w_tag("pPr"))
        if align is not None:
            ET.SubElement(props, w_tag("jc"), {w_tag("val"): align})
        if spacing_before is not None or spacing_after is not None:
            attrs: dict[str, str] = {}
            if spacing_before is not None:
                attrs[w_tag("before")] = str(spacing_before)
            if spacing_after is not None:
                attrs[w_tag("after")] = str(spacing_after)
            ET.SubElement(props, w_tag("spacing"), attrs)
    add_run(paragraph, text, bold=bold, size=size)
    return paragraph


def add_bullet(body: ET.Element, text: str) -> None:
    add_paragraph(body, f"- {text}", spacing_after=60)


def add_page_break(body: ET.Element) -> None:
    paragraph = ET.SubElement(body, w_tag("p"))
    run = ET.SubElement(paragraph, w_tag("r"))
    ET.SubElement(run, w_tag("br"), {w_tag("type"): "page"})


def build_document_xml() -> bytes:
    document = ET.Element(w_tag("document"))
    body = ET.SubElement(document, w_tag("body"))

    add_paragraph(
        body,
        "Secondary SOE Simulation Log v3",
        bold=True,
        size=30,
        align="center",
        spacing_after=120,
    )
    add_paragraph(
        body,
        "Reviewed and Reformatted Word Edition",
        bold=True,
        size=22,
        align="center",
        spacing_after=180,
    )
    add_paragraph(
        body,
        f"Prepared on {date.today().isoformat()} from Secondary Simulation Log.txt with reviewer corrections applied.",
        align="center",
        spacing_after=240,
    )
    add_paragraph(
        body,
        "Revision note: this edition removes template fragments, separates model versions, softens unsupported claims, and adds an explicit model limitations section.",
        spacing_after=180,
    )

    add_paragraph(body, "Table of Contents", bold=True, size=24, spacing_before=120, spacing_after=120)
    for item in [
        "Scope",
        "Model Versioning",
        "Phase 0 - Early Baseline Sequence",
        "Phase A - Lock Mechanism and Stability Envelope",
        "Phase B - Disturbance Stress",
        "Phase C - Cognitive Upgrade and Cognitive Stress",
        "Phase D - Interaction Tests",
        "Outstanding Questions",
        "Model Limitations",
        "Revised Stability and Failure Laws",
    ]:
        add_bullet(body, item)

    add_page_break(body)

    add_paragraph(body, "Scope", bold=True, size=24, spacing_after=120)
    add_bullet(body, "This log documents the secondary baseline_v1 simulation branch only.")
    add_bullet(body, "It should not be merged numerically with the older macro, topology, or CL-NET branches without explicit model separation.")
    add_bullet(body, "Results are interpreted as model-constrained findings rather than universal SOE laws.")

    add_paragraph(body, "Model Versioning", bold=True, size=24, spacing_before=180, spacing_after=120)
    add_bullet(body, "v1 - lock-mechanism baseline without cognition-to-trust coupling. Reference baseline: BASELINE_LOCK_v1. Result: stable 6/20, recovered 14/20, fragile 3/20, average final cooperation 0.864.")
    add_bullet(body, "v2 - cognition-linked baseline with distortion directly reducing trust. Reference baseline: BASELINE_LOCK_v2. Result: stable 5/20, recovered 14/20, fragile 4/20, average final cooperation 0.852.")
    add_bullet(body, "All cognitive and interaction tests after the cognition upgrade refer to v2, not v1.")

    add_page_break(body)

    add_paragraph(body, "Phase 0 - Early Baseline Sequence", bold=True, size=24, spacing_after=120)
    add_bullet(body, "BASELINE_v1: stable 0/20, recovered 8/20, fragile 20/20, average final cooperation 0.625. Interpretation: dynamic but underpowered.")
    add_bullet(body, "Recovery-rate increase to 0.04 improved recovery strongly but did not create stability.")
    add_bullet(body, "Governance-only improvement had only marginal effect.")
    add_bullet(body, "Lower disturbance and higher structural_weight produced the strongest gains before the lock mechanism was introduced.")
    add_bullet(body, "The key discovery of the early phase was that average cooperation above 0.80 was not enough by itself; the model needed state-dependent reinforcement.")

    add_paragraph(body, "Phase A - Lock Mechanism and Stability Envelope", bold=True, size=24, spacing_before=180, spacing_after=120)
    add_bullet(body, "LOCK_MECHANISM_TEST_v1 introduced stability_threshold 0.80, stability_boost 1.2, and disturbance_damping 0.8.")
    add_bullet(body, "BASELINE_LOCK_v1 result: stable 6/20, recovered 14/20, fragile 3/20, average final cooperation 0.864.")
    add_bullet(body, "Boundary mapping showed the stable region centered near noise_level 0.05 and structural_weight 0.90.")
    add_bullet(body, "Boundary tests: noise 0.045 slightly strengthened the regime; noise 0.055 remained near-flat; noise 0.06 degraded stability; structural_weight 0.80 produced clear weakening.")
    add_bullet(body, "Interpreted carefully: within the tested parameter range, stability appeared bounded, disturbance-limited, and buffered by structure.")

    add_paragraph(body, "Phase B - Disturbance Stress", bold=True, size=24, spacing_before=180, spacing_after=120)
    add_bullet(body, "STRESS_S1 with shock_prob 0.10: stable 5/20, recovered 14/20, fragile 3/20, average final cooperation 0.858.")
    add_bullet(body, "STRESS_S2 with shock_prob 0.15: stable 4/20, recovered 16/20, fragile 4/20, average final cooperation 0.854.")
    add_bullet(body, "Interpretation: within the tested range, higher shock frequency degraded performance gradually and did not produce catastrophic collapse.")

    add_page_break(body)

    add_paragraph(body, "Phase C - Cognitive Upgrade and Cognitive Stress", bold=True, size=24, spacing_after=120)
    add_bullet(body, "Original cognitive stress tests on v1 were effectively null: raising emotional_weight alone barely moved the system.")
    add_bullet(body, "Model upgrade: added distortion_impact_on_trust so distortion now directly reduces trust.")
    add_bullet(body, "BASELINE_LOCK_v2 result after the upgrade: stable 5/20, recovered 14/20, fragile 4/20, average final cooperation 0.852.")
    add_bullet(body, "COG_S1 with emotional_weight 0.40 on v2: stable 4/20, recovered 16/20, fragile 5/20, average final cooperation 0.848.")
    add_bullet(body, "COG_S2 with emotional_weight 0.50 on v2: stable 4/20, recovered 16/20, fragile 5/20, average final cooperation 0.844.")
    add_bullet(body, "Interpretation: cognition became a real but moderate degradation axis once it gained a direct trust pathway.")

    add_paragraph(body, "Phase D - Interaction Tests", bold=True, size=24, spacing_before=180, spacing_after=120)
    add_bullet(body, "X1 shock + cognitive on v2: shock_prob 0.15 and emotional_weight 0.40. Result: stable 2/20, recovered 17/20, fragile 6/20, average final cooperation 0.828.")
    add_bullet(body, "X2 noise + cognitive on v2: noise_level 0.06 and emotional_weight 0.40. Result: stable 4/20, recovered 16/20, fragile 5/20, average final cooperation 0.843.")
    add_bullet(body, "X3 triple interaction on v2: noise_level 0.06, shock_prob 0.15, emotional_weight 0.40. Result: stable 2/20, recovered 16/20, fragile 7/20, average final cooperation 0.816.")
    add_bullet(body, "Interpretation: combined stressors produced the strongest degradation observed in the tested configurations.")
    add_bullet(body, "Important caution: additive versus multiplicative interaction strength has not yet been isolated because shock-only controls were not rerun on the cognition-linked v2 baseline.")

    add_paragraph(body, "Outstanding Questions", bold=True, size=24, spacing_before=180, spacing_after=120)
    add_bullet(body, "Governance null result: governance_capacity produced only marginal improvement in the early branch, and the reason for that weak effect is not yet explained by the model.")
    add_bullet(body, "Lock-mechanism opacity: the log records that stability_boost and disturbance_damping matter, but the exact failure and disengagement conditions of the lock remain under-described.")
    add_bullet(body, "Sample-size caution: 20 runs per condition is enough to detect broad direction, but not enough to support high-confidence probability claims from small differences.")
    add_bullet(body, "Horizon caution: the 100-step window is enough for comparative stress testing, but not enough to prove long-run permanence of the observed regimes.")
    add_bullet(body, "Missing matched controls: shock-only reruns on the cognition-linked v2 baseline are still the cleanest missing control for interaction-strength claims.")

    add_paragraph(body, "Model Limitations", bold=True, size=24, spacing_before=180, spacing_after=120)
    add_bullet(body, "Results are constrained to the tested parameter ranges.")
    add_bullet(body, "Recovery capacity is modeled as stable and does not deplete over time.")
    add_bullet(body, "Trust dynamics are simplified and do not include hard threshold-collapse behavior.")
    add_bullet(body, "Noise is modeled as independent rather than correlated or systemic.")
    add_bullet(body, "The simulated population is homogeneous rather than agent-diverse.")
    add_bullet(body, "The horizon is limited to 100 steps.")
    add_bullet(body, "Twenty runs per condition limits precision of probability estimates.")
    add_bullet(body, "This branch does not yet directly simulate key SOE architectural mechanisms such as right of exit, peaceful replacement, interoperability loss, or ADPIE-style governance evaluation loops.")

    add_page_break(body)

    add_paragraph(body, "Revised Stability and Failure Laws", bold=True, size=24, spacing_after=120)
    add_bullet(body, "Stability requires threshold crossing plus state-dependent reinforcement.")
    add_bullet(body, "Stability is a regime, not an average value.")
    add_bullet(body, "Within the tested range, stability appears to exist inside a bounded parameter region.")
    add_bullet(body, "Within the tested configurations, disturbance was the strongest observed limiting factor.")
    add_bullet(body, "Structural support improves resilience but does not erase disturbance sensitivity.")
    add_bullet(body, "Recovery dynamics preserve operation under stress; the system is recovery-dependent rather than disturbance-free.")
    add_bullet(body, "Within the tested ranges, degradation appeared gradual and no catastrophic collapse was observed.")
    add_bullet(body, "Cognitive distortion is a meaningful secondary stress axis once it is coupled to trust.")
    add_bullet(body, "The trust-recovery loop is a critical dependency.")
    add_bullet(body, "Combined stressors produced the strongest degradation observed, but precise interaction strength remains under-controlled pending matched single-axis reruns on v2.")
    add_bullet(body, "The most severe degradation observed in the tested configurations occurred under volatility combined with weakened trust.")
    add_bullet(body, "These laws describe the current model branch, not universal SOE behavior.")

    add_paragraph(
        body,
        "Core Principle: the modeled system remains stable when it preserves the trust-recovery loop and operates within its disturbance tolerance range.",
        bold=True,
        spacing_before=180,
        spacing_after=120,
    )

    section_props = ET.SubElement(body, w_tag("sectPr"))
    ET.SubElement(section_props, w_tag("pgSz"), {w_tag("w"): "12240", w_tag("h"): "15840"})
    ET.SubElement(section_props, w_tag("pgMar"), {
        w_tag("top"): "1440",
        w_tag("right"): "1440",
        w_tag("bottom"): "1440",
        w_tag("left"): "1440",
        w_tag("header"): "720",
        w_tag("footer"): "720",
        w_tag("gutter"): "0",
    })
    return ET.tostring(document, encoding="utf-8", xml_declaration=True)


CONTENT_TYPES_XML = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
"""

RELS_XML = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
"""

DOCUMENT_RELS_XML = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>
"""


def build_docx(output_path: Path) -> None:
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", CONTENT_TYPES_XML)
        zf.writestr("_rels/.rels", RELS_XML)
        zf.writestr("word/document.xml", build_document_xml())
        zf.writestr("word/_rels/document.xml.rels", DOCUMENT_RELS_XML)


if __name__ == "__main__":
    build_docx(Path(__file__).with_name("Secondary_Simulation_Log_v3.docx"))
