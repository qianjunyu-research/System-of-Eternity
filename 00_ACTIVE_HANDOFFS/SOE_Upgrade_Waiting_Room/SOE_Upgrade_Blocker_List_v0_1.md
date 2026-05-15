# SOE Upgrade Blocker List v0.1

Status: companion blocker list for `SOE_Upgrade_Specification_v0_1.md`.

Date: 2026-05-12

## Evidence Boundary

Not blockers:

- Grand Simulation v0.7 may remain closed as simulation-level architecture evidence.
- Node v0.1 may remain a completed bounded container record.
- The upgrade phase may begin without reopening the v0.7 simulation.

Blocked:

- Grand Simulation v0.7 as deployment evidence.
- Node v0.1 as validation evidence.
- Preprint readiness as pilot readiness.
- `Psi_extended` as an empirical early-warning detector.
- Three hubs as universal safety or mesh equivalence.
- Resource stress evidence as recovery proof.

## Ontology Blockers

| ID | Blocker | Required action |
|---|---|---|
| O-01 | v0.7 manuscript/arXiv metadata still use `C (cognition)`. | Patch to `C (cognitive distortion)`. |
| O-02 | Frozen architecture wording can make `Psi(t)` sound like a state variable. | Patch `Psi_base`/`Psi_extended` as detector outputs, not primary state variables. |
| O-03 | `f_min=0.30` and `kappa_min=0.25` could be collapsed by future reviewers. | Put both in a notation table with explicit non-equivalence. |
| O-04 | Collapse/ignition terms can drift from simulation events into real-world claims. | Add glossary and evidence-boundary note. |

## Pilot-Readiness Blockers

| ID | Blocker | Required action |
|---|---|---|
| P-01 | No standalone Node Measurement Protocol. | Define T/D/C/I/S/coupling rubrics, raw-to-normalized mapping, missingness, and artifact flags. |
| P-02 | No inter-rater reliability plan. | Add second-rater/reviewer logic and disagreement handling. |
| P-03 | Node v0.2 consent boundary unresolved. | Require explicit informed consent before structured participation. |
| P-04 | Privacy/security/stop-rule package incomplete. | Define data minimization, retention, stop conditions, and sensitive-domain exclusions. |
| P-05 | `Psi_extended` adversarial/circularity tests not run. | Write and run stability clamp/spoof/delay/corruption, threshold gaming, and operator-capture tests. |
| P-06 | Trigger authority and rollback authority not separated. | Define who senses, triggers, audits, pauses, overrides, and rolls back. |
| P-07 | C09 node recognition gates missing. | Define staged proposal, provisional operation, recognition, scaling, rollback, and retirement gates. |
| P-08 | Drift Layer missing. | Define ontology, detector, topology, exit-right, resource-dependency, and memory/archive drift controls. |
| P-09 | Topology detection operational protocol incomplete. | Define classification, confidence, reclassification interval, and stale-topology response. |
| P-10 | External domain review absent. | Seek human expert review before pilot/deployment claims. |

## Deployment-Readiness Blockers

| ID | Blocker | Required action |
|---|---|---|
| D-01 | Target-context calibration missing. | Calibrate variables, thresholds, resources, timescales, topology, and trigger rules for a real context. |
| D-02 | Measurement proxies not validated. | Demonstrate reliability and validity for T/D/C/I/G/S measurements. |
| D-03 | Legal/institutional legitimacy missing. | Define lawful authority, accountability, appeal, and external oversight. |
| D-04 | Rollback paths not operationally tested. | Test pause, downgrade, retirement, and recovery procedures. |
| D-05 | Finite-resource recovery not proven. | Add resource envelopes, triage rules, depletion models, and stress tests. |
| D-06 | Capture scenarios incomplete. | Test governance capture, detector-operator capture, AI authority drift, funder capture, and security capture. |
| D-07 | Star-adjacent redesign process missing. | Define mandatory redesign path before any operation in star-adjacent topology. |
| D-08 | Effective exit not proven. | Test whether participants/nodes can actually exit under dependency pressure. |
| D-09 | Archive and memory drift controls missing. | Add versioned records, hash/traceability checks, and historical caveat preservation. |
| D-10 | Cost/feasibility layer absent. | Model compute, staffing, latency, compliance, privacy, and social burden costs. |

## Immediate Patch Targets

1. Governance Architecture ontology/readiness patch.
2. C09 Node Formation and Recognition Layer.
3. Node Measurement Protocol.
4. Drift Layer Requirements.
5. `Psi_extended` Adversarial Test Specification.
6. Meta-Governance authority/rollback/capture patch.

## Highest-Risk Overclaim Sentences To Prevent

- "SOE is validated in the real world."
- "Grand Simulation v0.7 proves deployment readiness."
- "Node v0.1 proves SOE works."
- "`Psi_extended` is an independent early-warning detector."
- "Three hubs are safe."
- "Resource recovery is proven."
- "Preprint-ready means pilot-ready."
