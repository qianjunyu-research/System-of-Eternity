# SOE Adversary Model And Test Families

Date: 2026-06-18

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
- evidence spam;
- deepfake endorsements;
- automated public pressure;
- model-generated legal arguments;
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

## 4. Required Sprint Outputs

A later hostile review sprint should produce:

- adversary classes accepted/rejected;
- missing adversary classes;
- top failure pathways;
- components most vulnerable to capture;
- claims most vulnerable to laundering;
- test cases suitable for later simulation or tabletop design;
- structure-patch candidates;
- no-readiness boundary statement.

## 5. Success Criteria For This Preparation Package

This package is strong only if reviewers can use it to find harder failures than the current simulation suite found.

If reviewers mostly say "SOE is already fine," the package has failed.

