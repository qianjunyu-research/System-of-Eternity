# SOE Civilization Simulation

This workspace now contains a small Python simulation inspired by the "System of Eternity (SOE)" document you referenced. It models a node-based civilization across 1,000 years with 10-year steps and tracks:

- `nodes`
- `population`
- `technology`
- `automation`
- `AI capability`
- `governance stability`
- `abundance`
- `protocol cohesion`

The simulation includes SOE-style dynamics:

- node fragmentation and node exit
- peaceful upgrades and peaceful replacement
- ideological conflict and infrastructure crises
- abundance transition
- AI superintelligence and AI governance-node emergence

## Run

```bash
python soe_simulation.py
```

Use a fixed seed for reproducible runs:

```bash
python soe_simulation.py --seed 42
```

Write the full history to JSON or CSV:

```bash
python soe_simulation.py --output history.json
python soe_simulation.py --output history.csv
```

Change the time horizon or preview size:

```bash
python soe_simulation.py --years 2000 --step-years 20 --preview-rows 20
```

Tune the core dynamics directly:

```bash
python soe_simulation.py --automation-growth-multiplier 2.4
python soe_simulation.py --ai-growth-multiplier 0.6
python soe_simulation.py --initial-protocol-cohesion 0.78 --cooperation-multiplier 1.75
```

Run the built-in comparison for the baseline and recommended experiment set:

```bash
python soe_simulation.py --experiments
python soe_simulation.py --experiments --output experiment_results.csv
python soe_simulation.py --experiments --raw-output experiment_runs.csv
```

Aggregate many runs per scenario to reduce single-seed bias:

```bash
python soe_simulation.py --experiments --runs 100
python soe_simulation.py --experiments --runs 100 --output monte_carlo_results.csv
python soe_simulation.py --experiments --runs 500 --output monte_carlo_summary_500.csv --raw-output monte_carlo_runs_500.csv
```

Run the v1.5 bureaucratic-layer baseline:

```bash
python soe_simulation.py --bureaucratic-layer
python soe_simulation.py --bureaucratic-layer --output c_v15_base_1.csv
```

Inject the Node Omega administrative shock at year 150:

```bash
python soe_simulation.py --bureaucratic-layer --omega-shock-year 150 --output gx_shock_1.csv
```

Run the v2.0 network-topology layer over a 500-year horizon:

```bash
python soe_simulation.py --years 500 --topology random
python soe_simulation.py --years 500 --topology scale-free
python soe_simulation.py --years 500 --topology small-world
python soe_simulation.py --years 500 --topology federation
```

Run the four 100-run topology batches and write one CSV per topology:

```bash
python soe_simulation.py --years 500 --topology random --runs 100 --output gm_net_1.csv
python soe_simulation.py --years 500 --topology scale-free --runs 100 --output gm_net_2.csv
python soe_simulation.py --years 500 --topology small-world --runs 100 --output gm_net_3.csv
python soe_simulation.py --years 500 --topology federation --runs 100 --output gm_net_4.csv
```

Run the stressed topology test with harsher contagion and a 10-node shock at year 200:

```bash
python soe_simulation.py --years 500 --topology random --contagion-penalty 0.20 --systemic-shock-year 200 --systemic-shock-count 10 --systemic-shock-stability 0.10 --runs 100 --output gm_net_stress_1.csv
python soe_simulation.py --years 500 --topology scale-free --contagion-penalty 0.20 --systemic-shock-year 200 --systemic-shock-count 10 --systemic-shock-stability 0.10 --runs 100 --output gm_net_stress_2.csv
python soe_simulation.py --years 500 --topology small-world --contagion-penalty 0.20 --systemic-shock-year 200 --systemic-shock-count 10 --systemic-shock-stability 0.10 --runs 100 --output gm_net_stress_3.csv
python soe_simulation.py --years 500 --topology federation --contagion-penalty 0.20 --systemic-shock-year 200 --systemic-shock-count 10 --systemic-shock-stability 0.10 --runs 100 --output gm_net_stress_4.csv
```

Run the v2.1 decapitation strike against the highest-degree hubs:

```bash
python soe_simulation.py --years 300 --topology random --contagion-penalty 0.35 --initial-protocol-cohesion 0.45 --shock-year 200 --systemic-shock-count 10 --shock-target hubs --runs 20 --output gm_net_decap_1.csv
python soe_simulation.py --years 300 --topology scale-free --contagion-penalty 0.35 --initial-protocol-cohesion 0.45 --shock-year 200 --systemic-shock-count 10 --shock-target hubs --runs 20 --output gm_net_decap_2.csv
python soe_simulation.py --years 300 --topology small-world --contagion-penalty 0.35 --initial-protocol-cohesion 0.45 --shock-year 200 --systemic-shock-count 10 --shock-target hubs --runs 20 --output gm_net_decap_3.csv
python soe_simulation.py --years 300 --topology federation --contagion-penalty 0.35 --initial-protocol-cohesion 0.45 --shock-year 200 --systemic-shock-count 10 --shock-target hubs --runs 20 --output gm_net_decap_4.csv
```

Run the v2.2 total hub removal batch, which physically erases the 10 targeted hubs at year 200:

```bash
python soe_simulation.py --years 300 --topology random --contagion-penalty 0.35 --initial-protocol-cohesion 0.45 --shock-year 200 --systemic-shock-count 10 --shock-target hubs --hub-failure-mode remove --runs 20 --output gm_net_rem_1.csv
python soe_simulation.py --years 300 --topology scale-free --contagion-penalty 0.35 --initial-protocol-cohesion 0.45 --shock-year 200 --systemic-shock-count 10 --shock-target hubs --hub-failure-mode remove --runs 20 --output gm_net_rem_2.csv
python soe_simulation.py --years 300 --topology small-world --contagion-penalty 0.35 --initial-protocol-cohesion 0.45 --shock-year 200 --systemic-shock-count 10 --shock-target hubs --hub-failure-mode remove --runs 20 --output gm_net_rem_3.csv
python soe_simulation.py --years 300 --topology federation --contagion-penalty 0.35 --initial-protocol-cohesion 0.45 --shock-year 200 --systemic-shock-count 10 --shock-target hubs --hub-failure-mode remove --runs 20 --output gm_net_rem_4.csv
```

Run the focused governance falsification suite for the single-node control model:

```bash
python governance_falsification.py
python governance_falsification.py --runs 50 --steps 120
python governance_falsification.py --output governance_falsification_summary.csv --raw-output governance_falsification_runs.csv
```

The falsification suite compares:

- baseline threshold control
- de-trust control with the trust channel removed
- continuous control without hard thresholds
- delayed control versus the best zero-delay damping proxy
- cognition removed versus cognition amplified
- fixed trust cap versus a stress-derived trust cap

Run the follow-up governance integration suite for the post-falsification v1.2 candidate:

```bash
python governance_integration.py
python governance_integration.py --runs 50 --steps 120
python governance_integration.py --output governance_integration_summary.csv --raw-output governance_integration_runs.csv
```

The integration suite checks:

- the fully combined v1.2 candidate with continuous control, smoothing, cognition, and a derived trust cap
- whether trust must be read directly by the controller
- whether linear and nonlinear cognition channels behave differently
- how explicit trust-erosion memory windows change stability

Run the constrained-regime scan when the integrated controller starts stabilizing everything:

```bash
python governance_regime_scan.py
python governance_regime_scan.py --runs 50 --steps 120
python governance_regime_scan.py --output governance_regime_summary.csv --raw-output governance_regime_runs.csv
```

The regime scan weakens capacity and smoothing, raises disturbance severity, and combines stressors to show which signals become binding first.

## Notes

The script records an initial state at year `0`, then advances the model in 10-year increments up to the final year. The output printed to stdout is a preview plus a short summary; the optional file output contains the full history.

## Multi-AI Chat Prototype

This workspace also now includes a local prototype for the multi-AI chat platform idea in `multi_ai_platform`.

Fastest option: open `multi_ai_platform/static/index.html` directly in a browser.

If you want the local Python server version, run it from the workspace root:

```powershell
.\start_multi_ai_platform.ps1
```

Then open `http://127.0.0.1:8008`.

The prototype uses mocked Codex, Claude, Gemini, Grok, and ChatGPT participants to demonstrate:

- one shared transcript
- hand-raise turn order with one speaker at a time
- direct addressing like `Claude, answer this`
- optional auto-play for hands-free turn advancement
- private work boxes with a share-back-to-room flow
- private work can keep going while the main room is paused
- simulation requests that wait on the user and accept pasted results
- rolling summary compression
- separate per-model token budgets
- strict pause mode that stops the whole room if the next speaker cannot afford a turn
- manual token top-ups and resume
