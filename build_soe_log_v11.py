from __future__ import annotations

import argparse
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


def add_page_break(body: ET.Element) -> None:
    paragraph = ET.SubElement(body, w_tag("p"))
    run = ET.SubElement(paragraph, w_tag("r"))
    ET.SubElement(run, w_tag("br"), {w_tag("type"): "page"})


def add_bullet(body: ET.Element, text: str) -> None:
    add_paragraph(body, f"- {text}", spacing_after=60)


def build_document_xml() -> bytes:
    document = ET.Element(w_tag("document"))
    body = ET.SubElement(document, w_tag("body"))

    add_paragraph(
        body,
        "System of Eternity (SOE) Simulation Log v11",
        bold=True,
        size=32,
        align="center",
        spacing_after=120,
    )
    add_paragraph(
        body,
        "Cleaned and Integrated Review Edition",
        bold=True,
        size=22,
        align="center",
        spacing_after=240,
    )
    add_paragraph(
        body,
        f"Prepared on {date.today().isoformat()} from SOE_Simulation_Log_v10.docx and consolidated review input from Codex, Claude, Gemini, Grok, and ChatGPT.",
        align="center",
        spacing_after=240,
    )
    add_paragraph(
        body,
        "Revision note: This edition preserves the completed experiment record while fixing section order, reducing overclaiming, clarifying the meaning of collapse, and separating validated findings from preliminary or superseded material.",
        spacing_after=180,
    )

    add_paragraph(body, "Table of Contents", bold=True, size=24, spacing_before=120, spacing_after=120)
    toc_items = [
        "Core Definitions",
        "Experiment Naming System",
        "Section A - Codex Simulator (Validated Results)",
        "Section B - xAI Simulator (Preliminary Results)",
        "Section C - Agent Simulations (Claude)",
        "Section D - Network Topology Experiments (Gemini / Codex)",
        "Section E - Adversarial Stress Tests (Grok / xAI)",
        "Section F - Cross-Model Experiments",
        "Section G - Bureaucratic Layer Experiments (Codex v1.5)",
        "Section H - Behavior x Topology Integration (CL-NET Series)",
        "Section Y - Execution Layer Constraints",
        "Section X - Core System Laws",
    ]
    for item in toc_items:
        add_bullet(body, item)

    add_page_break(body)

    add_paragraph(body, "Core Definitions", bold=True, size=24, spacing_after=120)
    add_bullet(
        body,
        "Collapse: failure to restore system cooperation above 0.80 within 100 years after a disruption event. In this log, collapse means functional collapse within the recovery window, not extinction or a permanent inability to recover.",
    )
    add_bullet(
        body,
        "Survival: the system remains structurally intact and retains the ability to recover cooperation, even if recovery is delayed.",
    )
    add_bullet(
        body,
        "Recovery: restoration of cooperation above the 0.80 threshold within the defined time window.",
    )
    add_bullet(
        body,
        "Functional Collapse: recovery occurs after the allowed time window or cooperation remains below threshold for too long to preserve effective system operation.",
    )
    add_bullet(
        body,
        "Governance Survival Threshold: governance_stability >= 0.50. Values below 0.50 indicate systemic governance collapse risk in the Codex macro simulator.",
    )
    add_bullet(
        body,
        "Structural Fragmentation: loss of network unity measured through rising connected-component counts or declining largest-component ratio.",
    )

    add_paragraph(body, "Experiment Naming System", bold=True, size=24, spacing_before=180, spacing_after=120)
    add_paragraph(
        body,
        "All experiments use a prefix-based naming system to identify the model family and experiment type. Prefixes: C = Codex macro simulation, CL = Claude agent behavior, GM = Gemini network topology, GX = Grok/xAI stress testing, X = cross-model synthesis. Version numbers increase sequentially when an experiment is rerun with materially different parameters.",
    )
    add_paragraph(
        body,
        "Documentation principles: reproducibility, evidence separation, model independence, and auditability. Validated results are separated from preliminary or model-specific findings whenever direct comparison would be misleading.",
        spacing_after=120,
    )

    add_page_break(body)

    add_paragraph(body, "Section A - Codex Simulator (Validated Results)", bold=True, size=24, spacing_after=120)
    add_paragraph(body, "C-BASE-1 - Baseline Civilization Simulation", bold=True, size=20, spacing_after=60)
    add_paragraph(
        body,
        "Model: SOE Simulation v1 (Codex-generated prototype). Date: 2026-03-13. Simulation length: 1000 years. Time step: 10 years. Fixed seed used for comparison.",
    )
    add_bullet(body, "Final system state: population 73,280,871; nodes 60; technology level 5.002; AI capability 5.934; governance stability 0.213.")
    add_bullet(body, "Abundance transition was not reached. AI superintelligence threshold was crossed in year 680.")
    add_bullet(body, "Most common events: peaceful_upgrade 8, node_fragmentation 6, ai_governance_node 5, ideological_conflict 3, ai_superintelligence 1, infrastructure_crisis 1.")
    add_bullet(body, "Interpretation: long-run fragility emerges when AI capability grows faster than governance capacity.")

    add_paragraph(body, "C-PARAM-1 - Parameter Experiments", bold=True, size=20, spacing_before=120, spacing_after=60)
    add_bullet(body, "C-PARAM-1A - Faster Automation: abundance reached in year 380, peak abundance 0.705, final governance stability 0.009. Automation-driven abundance alone does not stabilize governance.")
    add_bullet(body, "C-PARAM-1B - Slower AI Growth: AI superintelligence threshold moved to year 950, minimum governance stability stayed above 0.50, final stability 0.979. This was one of the most stable single-seed trajectories in the parameter set.")
    add_bullet(body, "C-PARAM-1C - Stronger Node Cooperation: disruption events fell to 0 versus 4 in baseline, but final governance stability still declined to 0.117. Cooperation reduces disruption without fully solving governance drift.")

    add_paragraph(body, "C-MC100-1 and C-MC500-1 - Monte Carlo Validation", bold=True, size=20, spacing_before=120, spacing_after=60)
    add_bullet(body, "C-MC100-1: across tested scenarios, the strongest determinant of long-run stability was AI growth rate relative to governance capacity.")
    add_bullet(body, "C-MC500-1 command: python soe_simulation.py --experiments --runs 500 --output monte_carlo_summary_500.csv --raw-output monte_carlo_runs_500.csv.")
    add_bullet(body, "500-run findings: baseline stable_rate 1%; faster automation stable_rate 0%; slower_ai stable_rate 100%; stronger_cooperation stable_rate 0%; balanced_path stable_rate 100%.")
    add_bullet(body, "Interpretation: abundance alone does not guarantee stability, slower AI growth strongly improves stability, and cooperation alone is insufficient when governance lags technology.")

    add_page_break(body)

    add_paragraph(body, "Section B - xAI Simulator (Preliminary Results)", bold=True, size=24, spacing_after=120)
    add_paragraph(
        body,
        "These results come from a separate node-level simulator and are not directly comparable with the Codex macro simulations. They are retained as preliminary supporting evidence only.",
        spacing_after=120,
    )
    add_paragraph(body, "GX-RES-1 - Node Resilience Test", bold=True, size=20, spacing_after=60)
    add_bullet(body, "Baseline scenario: crisis probability 10%, average final resource level 105.4, fragmentation risk 0.08.")
    add_bullet(body, "Interpretation: the node network remains stable under moderate crisis conditions; resource shocks are absorbed through voluntary cooperation and exploration-driven recovery.")
    add_paragraph(body, "GX-RES-2 - High Crisis Stress Test", bold=True, size=20, spacing_before=120, spacing_after=60)
    add_bullet(body, "High-stress scenario: crisis probability 0.30, fragmentation risk 0.25.")
    add_bullet(body, "Interpretation: frequent crisis events increase fragmentation risk, but the simulated system remains functional in this preliminary model.")

    add_page_break(body)

    add_paragraph(body, "Section C - Agent Simulations (Claude)", bold=True, size=24, spacing_after=120)
    add_paragraph(body, "CL-FORM-1 - Cooperation Emergence Model", bold=True, size=20, spacing_after=60)
    add_bullet(body, "Cooperation emerged naturally in 9 of 10 scenarios without top-down enforcement.")
    add_bullet(body, "Starting from as low as 0.40 mean cooperation, the network self-organized above the 0.80 threshold by year 285.")
    add_bullet(body, "The main failure mode was the reciprocal waiting trap: too many conditional cooperators stalled the network below threshold.")

    add_paragraph(body, "CL-FORM-2 - Trust Dynamics Experiment", bold=True, size=20, spacing_before=120, spacing_after=60)
    add_bullet(body, "Betrayal creates a persistent new equilibrium rather than a temporary dip.")
    add_bullet(body, "Large betrayals and heavier infiltration push cooperation below the 0.80 threshold and do not naturally recover.")
    add_bullet(body, "Trust builds slowly and breaks quickly, indicating the need for an active trust recovery mechanism.")

    add_paragraph(body, "CL-FORM-3 - Time-Horizon Cooperation Test", bold=True, size=20, spacing_before=120, spacing_after=60)
    add_bullet(body, "Planning horizon is decisive: horizon 20 reached final cooperation 0.9887, while short-horizon regimes failed badly.")
    add_bullet(body, "Mixed populations show that short-horizon nodes drag long-horizon nodes downward.")
    add_bullet(body, "Abundance alone did not repair this problem; long-horizon norm formation remains necessary.")

    add_paragraph(body, "Section C Synthesis - Three Requirements for the Formation Layer", bold=True, size=20, spacing_before=120, spacing_after=60)
    add_bullet(body, "The formation layer must catalyze cooperation.")
    add_bullet(body, "The formation layer must protect trust after betrayal.")
    add_bullet(body, "The formation layer must cultivate long-horizon institutional norms.")

    add_page_break(body)

    add_paragraph(body, "Section D - Network Topology Experiments (Gemini / Codex)", bold=True, size=24, spacing_after=120)
    add_paragraph(body, "GM-NET-1/2/3/4 - Baseline Topology Comparison", bold=True, size=20, spacing_after=60)
    add_bullet(body, "All four topologies survived the 500-year horizon under baseline calibration.")
    add_bullet(body, "Random had the strongest raw contagion containment, small-world preserved the most coherent final network, and federation retained the most compartmentalization.")
    add_bullet(body, "Interpretation: topology changes structure under stress, but baseline resilience was too strong for survival to discriminate between topologies.")

    add_paragraph(body, "GM-NET-STRESS-1/2/3/4 - Topology Stress Test", bold=True, size=20, spacing_before=120, spacing_after=60)
    add_bullet(body, "A harsher contagion penalty and a 10-node systemic shock still left all four topologies surviving.")
    add_bullet(body, "Topology differences appeared in containment and cohesion metrics, but not yet in outright failure.")

    add_paragraph(body, "GM-NET-D1 - Decapitation Strike v2.1", bold=True, size=20, spacing_before=120, spacing_after=60)
    add_bullet(body, "Hub-targeted destabilization did not shatter the network under the tested parameters.")
    add_bullet(body, "Interpretation: the architecture was still too resilient for hub-targeting alone to determine outcome.")

    add_paragraph(body, "GM-NET-D2 - Decapitation Strike v2.2 (Hub Removal) - Final Validated Result", bold=True, size=20, spacing_before=120, spacing_after=60)
    add_bullet(body, "Experiment parameters: top 10 highest-degree nodes removed at year 200, contagion penalty 0.35, initial protocol cohesion 0.45, 20 runs, 300-year horizon.")
    add_bullet(body, "Random: survival 1.000, fragmentation 0.70, containment 0.125, largest component 0.985.")
    add_bullet(body, "Scale-free: survival 1.000, fragmentation 4.90, containment 0.112, largest component 0.862.")
    add_bullet(body, "Small-world: survival 1.000, fragmentation 1.45, containment 0.141, largest component 0.867.")
    add_bullet(body, "Federation: survival 1.000, fragmentation 1.20, containment 0.227, largest component 0.968.")
    add_bullet(body, "Interpretation: over-centralization without redundancy is fragile. Structural survival does not imply structural integrity.")

    add_page_break(body)

    add_paragraph(body, "Section E - Adversarial Stress Tests (Grok / xAI)", bold=True, size=24, spacing_after=120)
    add_paragraph(
        body,
        "These experiments come from a different simulator family and should be treated as model-specific stress evidence rather than direct one-to-one comparisons with Codex outputs.",
        spacing_after=120,
    )
    add_bullet(body, "GX-CASCADE-1: baseline survival 45%, high-stress survival below 10%, critical threshold cooperation below 0.75.")
    add_bullet(body, "GX-POLAR-1: baseline survival 62%, high-stress survival 20%, critical threshold polarization above 25% per cycle.")
    add_bullet(body, "GX-AI-TAKE-1: baseline survival 55%, high-stress survival 5%, critical threshold superintelligence before year 400.")
    add_bullet(body, "GX-INFOWAR-1: baseline survival 48%, high-stress survival 1%, critical threshold cooperation below 0.60.")
    add_paragraph(
        body,
        "Cross-experiment reading: these stress tests suggest that cooperation thresholds and coordination bottlenecks matter across architectures, but the exact threshold values should not be treated as perfectly interchangeable across different models.",
        spacing_after=120,
    )

    add_page_break(body)

    add_paragraph(body, "Section F - Cross-Model Experiments", bold=True, size=24, spacing_after=120)
    add_bullet(body, "X-COOP-THRESH-1 - Cooperation Threshold Validation: Not executed. Superseded by later CL-NET synthesis and Section X law statements.")
    add_bullet(body, "X-STABILITY-MAP-1 - Civilizational Stability Landscape: Not executed. Superseded by accumulated Monte Carlo and CL-NET parameter results.")
    add_bullet(body, "X-AI-GOV-1 - AI Governance Architecture Comparison: Not executed. Superseded by Section A and Section G governance findings.")
    add_paragraph(
        body,
        "Section F is retained for audit continuity only. No standalone executed cross-model experiment content is included in this edition.",
        spacing_after=120,
    )

    add_page_break(body)

    add_paragraph(body, "Section G - Bureaucratic Layer Experiments (Codex v1.5)", bold=True, size=24, spacing_after=120)
    add_paragraph(body, "C-V1.5-BASE-1 - Bureaucratic Layer Baseline Calibration", bold=True, size=20, spacing_after=60)
    add_bullet(body, "Average governance utilization 0.881, peak backlog 0.000, minimum human_control_index 1.000.")
    add_bullet(body, "Interpretation: the v1.5 layer operated in the intended utilization band without triggering defensive actions.")

    add_paragraph(body, "GX-SHOCK-1 - Singularity Shock: Administrative DoS", bold=True, size=20, spacing_before=120, spacing_after=60)
    add_bullet(body, "Node Omega injected at year 150 to overload governance bandwidth.")
    add_bullet(body, "Result: 100% survival, final average human_control_index 1.000, dominant defense action proposal_quota, zero AI delegation, zero foundational veto.")
    add_bullet(body, "Interpretation: under current calibration, the administrative overload attack was absorbed by rate limiting rather than forcing AI delegation.")

    add_paragraph(body, "GX-MC100-SHOCK-1 - Shock Scenario Monte Carlo Batch", bold=True, size=20, spacing_before=120, spacing_after=60)
    add_bullet(body, "Across 100 runs, the same pattern held: 100% survival, average human_control_index 1.000, most common defense mechanism proposal_quota, zero runs requiring AI delegation or foundational veto.")
    add_bullet(body, "Known limitation: this result applies to the tested single-Omega configuration and does not by itself validate multi-node, Sybil, or legitimacy-cost variants.")

    add_page_break(body)

    add_paragraph(body, "Section H - Behavior x Topology Integration (CL-NET Series)", bold=True, size=24, spacing_after=120)
    add_paragraph(
        body,
        "All CL-NET collapse and recovery classifications in this section use the definitions above. Collapse means failure to recover above 0.80 within the 100-year recovery window after betrayal, not extinction.",
        spacing_after=120,
    )

    add_paragraph(body, "CL-NET-1 v2.3 - Execution Log", bold=True, size=20, spacing_after=60)
    add_bullet(body, "Configuration: 4 topologies x 4 trust-memory decay values x 100 runs, 500 years total, betrayal at year 100, no infiltration nodes, no additional shocks.")
    add_bullet(body, "Results by decay regime: 0.0 produced 100% functional collapse; 0.05 produced mixed outcomes; 0.10 produced majority recovery; 0.20 produced near-complete recovery.")
    add_bullet(body, "Topology effect: scale-free had the highest collapse probability under stress; small-world and federation were more resilient; random was intermediate.")
    add_bullet(body, "Interpretation: permanent trust memory is the main driver of functional collapse. Topology changes severity and pathway, not the existence of failure.")

    add_paragraph(body, "CL-NET-1 v2.3 - Historical Pre-Execution Specification", bold=True, size=20, spacing_before=120, spacing_after=60)
    add_paragraph(
        body,
        "Status: Archived planning record. The original canonical specification is retained only as historical provenance and is superseded by the completed CL-NET-1 execution log above.",
        spacing_after=120,
    )

    add_paragraph(body, "CL-NET-2 v2.3 - Adversarial Trust Infiltration", bold=True, size=20, spacing_before=120, spacing_after=60)
    add_bullet(body, "Configuration: same topology x decay matrix as CL-NET-1, plus betrayal at year 100 and 10% persistent adversarial infiltration at year 120.")
    add_bullet(body, "Result: collapse_rate 100% and recovery_rate 0% across all 16 configurations.")
    add_bullet(body, "Interpretation: persistent adversarial pressure overwhelms passive trust recovery, even at trust_memory_decay 0.20.")
    add_bullet(body, "Topology effects remained secondary: small-world showed the fastest amplification, federation slowed spread somewhat, and scale-free showed the worst long-run cooperation degradation.")

    add_paragraph(body, "CL-NET-3 v2.4 - Defense Layer Activation", bold=True, size=20, spacing_before=120, spacing_after=60)
    add_bullet(body, "Mechanism: pairwise trust tracking, detection threshold trust below 0.30 for 10 consecutive steps, response via edge severance.")
    add_bullet(body, "Result: collapse_rate 100%, recovery_rate 0%, defended False across all configurations.")
    add_bullet(body, "Defense performance: adversary_isolation_rate 1.000, average time to isolation about 90 to 92 years after infiltration.")
    add_bullet(body, "Best-performing defended cases included small-world 0.20 (final cooperation 0.857, largest component ratio 0.735), federation 0.20 (0.810, 0.677), and scale-free 0.20 (0.809, 0.613).")
    add_bullet(body, "Interpretation: defense isolates adversaries through quarantine, not deletion. Detection and isolation preserve local integrity but do not restore the system within the recovery window.")

    add_paragraph(body, "CL-NET-4 v2.5 - Trust Reconstruction Layer", bold=True, size=20, spacing_before=120, spacing_after=60)
    add_bullet(body, "Mechanisms: defense retained; repair added probabilistic reconnection and trust reinforcement.")
    add_bullet(body, "Result: collapse_rate 100% and recovery_rate 0% across all configurations.")
    add_bullet(body, "Best-performing repair cases: small-world 0.20 (final cooperation 0.856, largest component ratio 0.895), random 0.20 (largest component ratio 0.901, reconnection_rate 0.442, final cooperation 0.789), federation 0.20 (final cooperation 0.811, strong structural recovery).")
    add_bullet(body, "Interpretation: the network can be structurally repaired, but trust restoration remains too slow to beat the 100-year window. Several configurations eventually recover later, but still count as functional collapse.")

    add_paragraph(body, "CL-NET-5 v2.6 - Recovery Acceleration Layer", bold=True, size=20, spacing_before=120, spacing_after=60)
    add_bullet(body, "Mechanisms: defense and repair retained; acceleration added trust-signal propagation up to two hops plus a local group coordination boost.")
    add_bullet(body, "Passing configurations under the success condition cooperation >= 0.80 and collapse_rate < 50%: random 0.05, 0.10, 0.20; small-world 0.10, 0.20; federation 0.10, 0.20; scale-free 0.20.")
    add_bullet(body, "Failing configurations: all 0.00 decay cases; small-world 0.05; federation 0.05; scale-free 0.05 and 0.10.")
    add_bullet(body, "Fastest recovery: random 0.20 in 46.5 years after betrayal; small-world 0.20 in 49.5 years; federation 0.20 in 53.4 years; random 0.10 in 62.3 years.")
    add_bullet(body, "Important caution: signal_propagation_rate was near 1.0 in both successful and failed rows. Signal propagation contributes to recovery, but success still depends on trust decay and topology.")
    add_bullet(body, "Example of late recovery without window success: scale-free 0.05 ended with avg_final_cooperation 0.91 and avg_time_to_recovery 171.7 years, so it remains a failed configuration by the functional-collapse definition.")

    add_paragraph(body, "Section H Synthesis", bold=True, size=20, spacing_before=120, spacing_after=60)
    add_bullet(body, "CL-NET-1 shows that non-zero trust decay is necessary for timely recovery after betrayal.")
    add_bullet(body, "CL-NET-2 shows that persistent adversaries make passive recovery fail universally in the tested matrix.")
    add_bullet(body, "CL-NET-3 shows that detection and isolation alone yield quarantined but fragmented functional collapse.")
    add_bullet(body, "CL-NET-4 shows that structure can be repaired faster than trust.")
    add_bullet(body, "CL-NET-5 shows that accelerated local coordination can restore the system in some parameter regimes, but only when trust adaptability and topology allow recovery to beat the time window.")

    add_page_break(body)

    add_paragraph(body, "Section Y - Execution Layer Constraints (v1.0)", bold=True, size=24, spacing_after=120)
    add_bullet(body, "Trust Recovery Constraint: passive decay alone is insufficient under persistent adversarial pressure. Recovery requires active propagation or coordination mechanisms.")
    add_bullet(body, "Temporal Constraint: systems fail functionally if recovery does not occur within the defined time window, even when eventual recovery is possible.")
    add_bullet(body, "Topology Constraint: system behavior depends on network structure. No topology is universally optimal, and centralized topologies require stronger recovery capacity.")
    add_bullet(body, "Parameter Sensitivity Constraint: system stability exists only within bounded parameter ranges such as trust decay, coordination speed, and event load.")
    add_bullet(body, "Adversarial Persistence Constraint: continuous adversarial pressure prevents passive recovery and forces active regeneration mechanisms.")

    add_page_break(body)

    add_paragraph(body, "Section X - Core System Laws (v1.0)", bold=True, size=24, spacing_after=120)
    add_paragraph(
        body,
        "Synthesis: These laws represent the consolidated results of the SOE simulation program across behavioral, topological, adversarial, and multi-model validation layers.",
        spacing_after=120,
    )
    add_bullet(body, "1. Permanent trust damage suggests functional collapse. In the tested CL-NET regime, if trust memory does not decay, timely recovery becomes impossible.")
    add_bullet(body, "2. Recovery must occur within a critical time window. Systems that recover too slowly enter functional collapse even when eventual cooperation is possible.")
    add_bullet(body, "3. Defense without recovery leads to fragmentation. Isolation of adversaries preserves local integrity but does not by itself restore cooperation.")
    add_bullet(body, "4. Trust propagation contributes to recovery but is not sufficient on its own. Signals must combine with trust adaptability and timing.")
    add_bullet(body, "5. Centralization increases recovery requirements. Highly connected hubs raise fragility under disruption unless redundancy is present.")
    add_bullet(body, "6. System stability is parameter-dependent. Survival depends on trust decay, topology, coordination speed, and event load.")
    add_bullet(body, "7. Recovery requires both trust decay and coordination. Neither mechanism alone was sufficient across the tested matrices.")
    add_bullet(body, "8. Trust recovery has real-world cost constraints. Propagation and repair must be efficient enough to avoid exhausting the system before recovery completes.")
    add_paragraph(
        body,
        "Core Principle: A system survives if it prevents permanent trust damage and restores cooperation within a critical time window.",
        bold=True,
        spacing_before=120,
        spacing_after=120,
    )
    add_paragraph(
        body,
        "Architectural implication: a viable SOE-style system needs trust adaptability, distributed coordination pathways, and recovery mechanisms that act before the functional-collapse window closes.",
        spacing_after=120,
    )
    add_paragraph(
        body,
        "These laws are conditional system laws derived from model-constrained simulations and depend on topology, timing, event load, and parameter regimes.",
        spacing_after=120,
    )

    sect = ET.SubElement(body, w_tag("sectPr"))
    ET.SubElement(sect, w_tag("pgSz"), {w_tag("w"): "12240", w_tag("h"): "15840"})
    ET.SubElement(
        sect,
        w_tag("pgMar"),
        {
            w_tag("top"): "1440",
            w_tag("right"): "1440",
            w_tag("bottom"): "1440",
            w_tag("left"): "1440",
            w_tag("header"): "720",
            w_tag("footer"): "720",
            w_tag("gutter"): "0",
        },
    )

    return ET.tostring(document, encoding="utf-8", xml_declaration=True)


CONTENT_TYPES_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>
"""


PACKAGE_RELS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>
"""


CORE_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
 xmlns:dc="http://purl.org/dc/elements/1.1/"
 xmlns:dcterms="http://purl.org/dc/terms/"
 xmlns:dcmitype="http://purl.org/dc/dcmitype/"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>System of Eternity (SOE) Simulation Log v11</dc:title>
  <dc:creator>Codex</dc:creator>
  <cp:lastModifiedBy>Codex</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">2026-03-22T00:00:00Z</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">2026-03-22T00:00:00Z</dcterms:modified>
</cp:coreProperties>
"""


APP_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
 xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Codex</Application>
</Properties>
"""


DOCUMENT_RELS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>
"""


def build_docx(output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", CONTENT_TYPES_XML)
        zf.writestr("_rels/.rels", PACKAGE_RELS_XML)
        zf.writestr("docProps/core.xml", CORE_XML)
        zf.writestr("docProps/app.xml", APP_XML)
        zf.writestr("word/document.xml", build_document_xml())
        zf.writestr("word/_rels/document.xml.rels", DOCUMENT_RELS_XML)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a cleaned SOE simulation log docx.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("SOE_Simulation_Log_v11.docx"),
        help="Output path for the generated docx.",
    )
    args = parser.parse_args()
    build_docx(args.output)
    print(args.output)


if __name__ == "__main__":
    main()
