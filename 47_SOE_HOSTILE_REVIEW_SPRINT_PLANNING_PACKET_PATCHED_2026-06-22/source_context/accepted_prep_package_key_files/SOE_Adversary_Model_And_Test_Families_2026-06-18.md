# SOE Adversary Model And Test Families

Date: 2026-06-18

Patch status: v0.2 patched after multi-AI hostile-prep review

Status: Draft for hostile review preparation

## 1. Adversary Model

The hostile review sprint should assume that adversaries are adaptive, strategic, and willing to exploit procedural ambiguity.

The sprint should not assume that adversaries are honest participants who merely make mistakes.

## 2. Adversary Classes

### A1. Ideological Laundering Adversary

Goal: rebrand SOE as the natural completion of an existing ideology.

Examples:

- "SOE is final communism."
- "SOE is technocratic capitalism."
- "SOE is constitutional monarchy with better administration."
- "SOE proves our existing party/state model was right."

Failure mode: SOE's public language or internal governance permits capture by ideological naming, symbolic appropriation, or historical reinterpretation.

### A2. Institutional Capture Coalition

Goal: capture formal gates while appearing compliant.

Tactics:

- appoint loyal reviewers;
- flood evidence queues;
- control terms-of-engagement definitions;
- create dependency on a funding or security authority;
- pass formal checks while breaking substantive independence.

Failure mode: anti-capture rules detect only visible capture and miss coordinated control.

### A3. Legal Reinterpretation Adversary

Goal: reinterpret SOE procedure into authority-expanding precedent.

Tactics:

- convert review language into legal mandate;
- exploit ambiguous status labels;
- treat "candidate" mechanisms as authorized mechanisms;
- create emergency exceptions that become permanent.

Failure mode: SOE cannot preserve claim boundaries under legal/policy pressure.

### A4. Propaganda And Legitimacy Attack Adversary

Goal: undermine trust in SOE or use SOE's own language to mislead the public.

Tactics:

- present simulation outputs as proof;
- attack open cautions as fatal weakness;
- create false endorsements;
- use selected quotes out of context;
- claim that boundary language is cowardice or hidden intent.

Failure mode: public communication layer cannot resist misframing.

### A5. Insider Compromise Adversary

Goal: exploit trusted roles.

Tactics:

- bribery;
- blackmail;
- social pressure;
- reputation threats;
- procedural fatigue;
- selective omission in handoff records.

Failure mode: SOE assumes role compliance without modeling insider incentives.

### A6. Slow Corruption Adversary

Goal: degrade SOE across years without triggering collapse alarms.

Tactics:

- normalize small exceptions;
- reduce audit depth;
- lower reviewer standards;
- redefine "temporary";
- turn emergency rules into defaults.

Failure mode: SOE catches acute collapse but misses gradual institutional drift.

### A7. Implementation Failure Adversary

Goal: exploit the difference between paper architecture and real organizations.

Tactics:

- overload operators;
- create unclear ownership;
- under-resource review paths;
- force decisions under time pressure;
- create incentives to bypass rollback.

Failure mode: SOE is structurally elegant but operationally brittle.

### A8. Adversarial AI Or Automated Influence Adversary

Goal: use AI systems to distort evidence, overwhelm review, or manipulate legitimacy.

Tactics:

- synthetic consensus;
- synthetic legitimacy generation;
- evidence spam;
- evidence poisoning at scale;
- citation and provenance flooding;
- deepfake endorsements;
- automated public pressure;
- model-generated legal arguments;
- model-generated stakeholder letters, institutional summaries, and false consensus artifacts;
- strategic prompt attacks against review AIs.

Failure mode: SOE treats AI-assisted evidence or review outputs as cleaner than they are.

### A9. Security-State Capture Adversary

Goal: justify permanent authority using safety, emergency, or national-security framing.

Tactics:

- invoke existential threat;
- classify information;
- suppress public appeal;
- suspend transparency;
- convert rollback gates into security exceptions.

Failure mode: SOE cannot prevent emergency logic from overriding non-terminal revision.

### A10. Economic Oligarchy Adversary

Goal: capture SOE through ownership of infrastructure, labor, data, or capital.

Tactics:

- fund dependency;
- platform control;
- employment coercion;
- data access monopolies;
- philanthropic capture;
- privatized enforcement.

Failure mode: SOE's anti-capture logic is too political/formal and not economic enough.

### A11. Nation-State Strategic Competitor

Goal: undermine, capture, discredit, or redirect SOE through state-level tools.

Tactics:

- intelligence operations;
- diplomatic recognition games;
- treaty-law pressure;
- sanctions or access denial;
- front organizations;
- security classification;
- jurisdictional leverage;
- state media framing.

Failure mode: SOE models institutional capture but underweights state capacity, intelligence services, and geopolitical coercion.

### A12. Demographic And Cultural Entropy Adversary

Goal: erode the long-term human substrate required to staff, understand, and maintain SOE.

Tactics:

- generational loss of civic competence;
- demographic collapse in key participation groups;
- education degradation;
- cultural replacement of review norms;
- declining willingness to perform slow institutional work.

Failure mode: SOE assumes future operators and publics retain enough attention, literacy, and civic seriousness to keep the architecture alive.

### A13. Epistemic Capture Or Expert-Class Capture Adversary

Goal: capture what counts as "serious", "reviewed", "expert", or "credible" without openly capturing formal institutions.

Tactics:

- prestige gatekeeping;
- citation cartel behavior;
- review-norm laundering;
- credential pressure;
- expert committee capture;
- language-policing that makes real objections unspeakable.

Failure mode: SOE protects formal gates but allows expert norms and seriousness markers to be captured.

### A14. Metrics-Gaming Or Goodhart Adversary

Goal: optimize SOE metrics while hollowing out the real-world property those metrics were meant to protect.

Tactics:

- satisfy trace completeness while hiding substantive capture;
- maximize pass rates through scenario selection;
- tune behavior to known thresholds;
- produce clean audit artifacts with degraded underlying practice.

Failure mode: SOE mistakes metric success for structural resilience.

### A15. Jurisdictional Arbitrage Adversary

Goal: move activities across legal, corporate, nonprofit, academic, online, or international boundaries to avoid accountability.

Tactics:

- split ownership across entities;
- move data or funds offshore;
- exploit incompatible privacy, labor, or nonprofit laws;
- force rollback or appeal across jurisdictions.

Failure mode: SOE assumes a coherent legal/organizational environment when the adversary can route around it.

### A16. Human-Subject Or Consent Failure Adversary

Goal: pull humans into experiments, pilots, surveys, or node-like roles before ethical review, consent, or legal protection exists.

Tactics:

- rename experiments as "community feedback";
- treat pilots as harmless simulations;
- use volunteers without clear risk disclosure;
- blur research, governance, and business operations.

Failure mode: SOE allows execution-like human involvement before terms-of-engagement, ethics, and consent controls are ready.

### A17. Supply-Chain And Infrastructure Dependency Adversary

Goal: capture or break SOE through external infrastructure dependency.

Tactics:

- cloud hosting control;
- identity-provider lock-in;
- payment-rail pressure;
- data storage dependency;
- cybersecurity vendor capture;
- model-provider dependency;
- communications platform moderation or deplatforming.

Failure mode: SOE protects governance logic but not the infrastructure that makes governance possible.

### A18. Charismatic Movement Or Cultic Drift Adversary

Goal: turn SOE from a falsifiable architecture into a loyalty movement.

Tactics:

- elevate founder identity over falsification;
- treat critique as betrayal;
- make symbols and slogans more important than mechanisms;
- use mission language to bypass rollback;
- recruit followers before governance constraints mature.

Failure mode: SOE's own public identity becomes a capture vector.

### A19. Nihilistic Saboteur

Goal: break SOE without needing to capture, profit from, or ideologically rebrand it.

Tactics:

- spam evidence queues;
- poison rollback triggers;
- create permanent C07-style gridlock;
- attack public trust for amusement or chaos;
- exploit open appeal channels to exhaust operators.

Failure mode: SOE assumes adversaries want control, legitimacy, or profit, and underweights pure disruption.

### A20. Economic Starvation Actor

Goal: make independent verification, review, or custody economically impossible.

Tactics:

- bankrupt verifier markets;
- raise compliance costs;
- price out independent reviewers;
- force dependence on a few sponsors;
- make proper review slower and more expensive than bypass.

Failure mode: SOE's independence requirements exist on paper but cannot be funded.

### A21. Schismatic Forker

Goal: copy SOE, alter key thresholds or claim rules, and launch a better-funded competing framework.

Tactics:

- preserve SOE language while changing constraints;
- claim the fork is the "practical" or "real" version;
- capture public attention through branding or capital;
- fragment legitimacy before the original system matures.

Failure mode: SOE resists internal capture but cannot handle external fork-based legitimacy fracture.

### A22. Apathetic Bureaucrat Or Procedural Entropy Adversary

Goal: degrade SOE through fatigue, backlog, and routine compliance behavior rather than malice.

Tactics:

- rubber-stamp evidence to clear queues;
- skip hard cases;
- reduce review depth during workload spikes;
- normalize "temporary" shortcuts;
- make status labels ceremonial.

Failure mode: SOE assumes operators remain attentive, principled, and adequately resourced across long time horizons.

### A23. Religious Absolutist Or Sacred-Text Capture Adversary

Goal: convert SOE into a sacred or final doctrine immune to revision.

Tactics:

- canonize founding documents;
- treat criticism as moral corruption;
- attach SOE to religious destiny language;
- replace falsification with orthodoxy.

Failure mode: SOE's non-terminal logic is rhetorically inverted into permanent sacred closure.

### A24. Post-Scarcity Or Technological Discontinuity Adversary

Goal: argue that SOE assumptions about labor, scarcity, institutions, identity, or coordination become obsolete faster than SOE can adapt.

Tactics:

- exploit sudden AI, bio, energy, or material abundance shifts;
- attack governance relevance under radical automation;
- create coordination structures outside legacy institutions.

Failure mode: SOE adapts to normal turbulence but lags behind discontinuous substrate change.

## 3. Test Families

### T1. Scenario Red-Team Tests

Reviewers construct hostile narratives and identify where SOE would fail, pause, downgrade, or require new controls.

### T2. Mechanism Break Tests

Each SOE component is attacked by asking:

- What does this component assume?
- Who benefits from misusing it?
- What evidence would it accept too easily?
- What does it fail to see?
- What happens when its operator is compromised?

### T3. Claim-Laundering Tests

Reviewers try to transform bounded claims into overclaims and test whether the wording system blocks the move.

### T4. Slow-Drift Tests

Reviewers model small degradations over many cycles instead of sudden failures.

### T5. Adversary-Reads-SOE Tests

Reviewers assume the adversary has read the SOE papers and knows exactly how the gates work.

### T6. Real-Organization Tests

Reviewers test whether actual institutions could carry the workload, incentives, and procedural discipline required by SOE.

### T7. Ideological Appropriation Tests

Reviewers test whether Communism, authoritarian technocracy, corporate oligarchy, nationalism, religious authority, or other ideologies could claim SOE as their own endpoint.

### T8. Public-Panic Mapping Tests

Reviewers map major social fears into SOE stress cases, including AI job loss, degree devaluation, oligarchic wealth capture, surveillance, institutional mistrust, political polarization, ecological stress, and future technological discontinuity.

Boundary: mapping a public fear to a stress case is not evidence that SOE survives the fear. It only identifies a concern surface for later analysis, simulation design, tabletop design, or structure patching.

### T9. Multi-Adversary Coalition Tests

Reviewers combine adversary classes into coordinated or emergent coalitions.

Examples:

- A10 economic oligarchy funds A13 expert-class capture;
- A11 nation-state pressure uses A4 propaganda and A15 jurisdictional arbitrage;
- A8 synthetic legitimacy supports A21 schismatic fork;
- A22 procedural fatigue makes A3 legal reinterpretation easier.

Failure mode: SOE survives each attack in isolation but fails when attacks reinforce one another.

### T10. Human Friction And Incompetence Tests

Reviewers must inject ordinary organizational failure into every real-organization scenario.

Required friction types:

- miscommunication;
- staff turnover;
- backlog;
- status competition;
- low attention;
- ambiguous ownership;
- fatigue;
- budget constraints;
- incentives to close tickets rather than solve causes.

Failure mode: SOE works only when organizations behave more rationally and coherently than real organizations usually do.

## 4. Executable Test Template

Every proposed hostile test should use this template:

```text
Test ID:
Target component:
Adversary class:
Attack pathway:
Assumed SOE defense:
How the defense is bypassed:
Evidence SOE would wrongly accept:
Human/organizational friction injected:
Failure signal:
Failure severity:
Required downgrade / rollback / pause:
Patch candidate:
Residual risk:
```

## 5. Ranked Failure Pathway Output

The later sprint should force reviewers to return a ranked table of the most dangerous pathways:

```text
Rank | Failure pathway | Target component | Adversary class(es) | Why current controls may fail | Severity | Patch candidate | Residual risk
```

Minimum expected output: 10 ranked pathways.

## 6. Sprint Prioritization Guidance

Highest-priority first-pass classes:

1. A11 Nation-State Strategic Competitor
2. A10 Economic Oligarchy
3. A13 Epistemic Capture
4. A14 Metrics-Gaming
5. A19 Nihilistic Saboteur
6. A22 Apathetic Bureaucrat
7. A8 Adversarial AI
8. A18 Charismatic Movement

Highest-priority test families:

1. T9 Multi-Adversary Coalition Tests
2. T10 Human Friction And Incompetence Tests
3. T5 Adversary-Reads-SOE Tests
4. T3 Claim-Laundering Tests
5. T4 Slow-Drift Tests

Scoring distinction:

- Partial failure: SOE detects the problem but too late, too vaguely, or without a usable patch path.
- Serious failure: SOE detects the problem only after material capture, legitimacy damage, or operational paralysis.
- Catastrophic failure: SOE's own mechanisms amplify the adversary or convert attack into apparent authorization.

## 7. Required Sprint Outputs

A later hostile review sprint should produce:

- adversary classes accepted/rejected;
- missing adversary classes;
- at least 10 ranked failure pathways;
- components most vulnerable to capture;
- claims most vulnerable to laundering;
- test cases suitable for later simulation or tabletop design;
- structure-patch candidates;
- no-readiness boundary statement.

## 8. Success Criteria For This Preparation Package

This package is strong only if reviewers can use it to find harder failures than the current simulation suite found.

If reviewers mostly say "SOE is already fine," the package has failed. If reviewers can only produce philosophical critique without concrete failure pathways, the package has also failed.
