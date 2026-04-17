# Bounded Propagation Without Ignition:
# Structural Limits of Local Coupling in Governance Network Simulations

## Abstract
We study disturbance propagation in locally coupled governance network simulations across four topologies: chain, star, random-sparse, and fully connected. The implemented simulator evolves node-level trust, disturbance, stability, and cognitive distortion under local coupling, intervention dynamics, and stochastic effects. We evaluate propagation with a strict criterion requiring all three conditions: at least 20% of non-seed nodes affected, cascade depth at least 5, and sustained failure for at least 3 consecutive steps. Across baseline and weakened-coupling regimes, propagation is frequently observed and is often topology-sensitive, but ignition-like global activation is not robustly sustained as a stable phase under the tested local mechanisms. A key result is threshold behavior under targeted intrinsic decay: coarse scans show a transition band between low and high damping, and fine scans show topology-dependent flip windows. Additional gating, nonlinear propagation, feedback, and hysteresis scans further suppress propagation in right-side regimes, including configurations with near-zero propagation share. Overall, the evidence supports bounded or suppressible propagation under local coupling in this model class, and suggests that ignition likely requires additional structural mechanisms beyond purely local interactions.

## 1. Introduction
Understanding when local disturbances become global cascades is a central question in networked governance and complex systems. Local coupling is often assumed to be sufficient for large-scale activation, especially when nonlinear amplification and feedback are present. This assumption is not guaranteed.

This paper evaluates that question empirically using a simulator built around decentralized local interactions. We ask three focused questions:

1. Can local coupling alone reliably produce ignition-like system-wide activation?
2. How strongly does topology change propagation outcomes under the same local rules?
3. Which local extensions (decay targeting, gating, nonlinearity, feedback, hysteresis) meaningfully shift propagation boundaries?

Our conclusions are scoped to the tested simulator family and parameter ranges.

## 2. Model and Scope

### 2.1 Implemented simulator (main evidence source)
The experiments in this paper are produced by the implemented simulation pipeline in:

- [governance_network_sim.py](C:\Users\sosoy\OneDrive\文档\New project 3\System-of-Eternity\governance_network_sim.py)
- [governance_network_chain_sweep.py](C:\Users\sosoy\OneDrive\文档\New project 3\System-of-Eternity\governance_network_chain_sweep.py)
- [governance_network_topology_compare.py](C:\Users\sosoy\OneDrive\文档\New project 3\System-of-Eternity\governance_network_topology_compare.py)

Each node carries continuous state variables (trust, disturbance, stability, cognitive distortion) and adaptive intervention dynamics. Topology enters through local neighbor coupling.

### 2.2 Reduced interpretation model
For interpretation clarity, we emphasize disturbance propagation behavior and propagation outcomes rather than claiming full real-world fidelity. The model is intentionally simplified to isolate structural effects of local coupling.

### 2.3 Topologies
We test four network structures:

- chain
- star
- random-sparse
- fully connected

## 3. Experimental Design

### 3.1 Common setup
Unless otherwise specified:

- node count: `N = 50`
- horizon: `200` steps
- seed node: node `0`
- disturbance injection applied to seed at initialization
- topologies: all four above

Initial states are not zeros. Nodes are initialized near baseline values with small random perturbations in the implemented code.

### 3.2 Propagation criterion
Run-level propagation is classified with a strict conjunction:

- affected share >= 20% of non-seed nodes
- cascade depth >= 5
- sustained failure >= 3 consecutive steps

This is implemented as `X AND D AND T`, not `OR`.

### 3.3 Core observables
We use:

- propagation share (fraction of runs classified as propagation)
- average failure rate (persistent failure indicator from run summaries)
- time to first propagated collapse
- cascade depth distribution
- largest survival cluster
- spatial distribution labels

### 3.4 Experiment families
We report results from multiple families, including:

- baseline topology comparisons
- weakened-coupling and reduced-shock scans
- targeted intrinsic-decay scans (coarse and fine)
- gated and nonlinear propagation scans
- feedback and hysteresis scans

Run counts vary by family (20, 50, or 100), and are recorded per output table.

## 4. Results

### 4.1 Baseline and weakened-coupling regimes
Earlier baseline and weak-coupling families include many configurations with propagation share at or near `1.00` (for example, summaries such as [governance_topology_compare_summary.csv](C:\Users\sosoy\OneDrive\文档\New project 3\System-of-Eternity\governance_topology_compare_summary.csv), [governance_topology_compare_weaker_summary.csv](C:\Users\sosoy\OneDrive\文档\New project 3\System-of-Eternity\governance_topology_compare_weaker_summary.csv), and related cutoff files).

This establishes that local propagation is easy to trigger in portions of the tested space.

### 4.2 Decay targeting is structurally important
Applying intrinsic decay to all state dimensions produced immediate collapse-like behavior in an intermediate run family (high propagation and high failure). Re-targeting intrinsic decay to disturbance-related dimensions changed the dynamics qualitatively and produced threshold-like behavior instead of trivial collapse.

This model-design correction was necessary for meaningful threshold analysis.

### 4.3 Coarse-to-fine decay threshold behavior
Coarse targeted-decay scans showed a transition region between high-propagation and low-propagation regimes. Fine and PC-scale scans (including [governance_topology_compare_decay_targeted_pc_summary.csv](C:\Users\sosoy\OneDrive\文档\New project 3\System-of-Eternity\governance_topology_compare_decay_targeted_pc_summary.csv)) show topology-dependent flip windows in `alpha = 0.076..0.085`.

Representative behavior from the 100-run targeted PC scan:

- `k_C = 0.02`: propagation share declines from roughly `0.35..0.39` at `alpha=0.076` to `0.01..0.03` by `alpha=0.085` depending on topology.
- `k_C = 0.03`: propagation share declines from roughly `0.24..0.51` at `alpha=0.076` to `0.02..0.08` by `alpha=0.085`.

Topology-specific thresholds are not identical. For example, in this family fully connected drops to <= `0.05` earlier than chain in some branches, while random-sparse can remain comparatively persistent in adjacent settings.

### 4.4 Gating, nonlinearity, feedback, and hysteresis
Additional local mechanisms further suppress propagation in large portions of the tested right-side parameter space:

- left-gated families: propagation share up to about `0.60..0.66`
- right-gated families: propagation share around `0.00..0.03`
- right feedback/hysteresis families: propagation share `0.00` throughout reported grids

Relevant tables include:

- [governance_topology_compare_decay_left_gated_summary.csv](C:\Users\sosoy\OneDrive\文档\New project 3\System-of-Eternity\governance_topology_compare_decay_left_gated_summary.csv)
- [governance_topology_compare_decay_right_gated_summary.csv](C:\Users\sosoy\OneDrive\文档\New project 3\System-of-Eternity\governance_topology_compare_decay_right_gated_summary.csv)
- [governance_topology_compare_right_feedback03_summary.csv](C:\Users\sosoy\OneDrive\文档\New project 3\System-of-Eternity\governance_topology_compare_right_feedback03_summary.csv)
- [governance_topology_compare_right_hysteresis_summary.csv](C:\Users\sosoy\OneDrive\文档\New project 3\System-of-Eternity\governance_topology_compare_right_hysteresis_summary.csv)

### 4.5 Interpretation
Propagation and ignition are distinct regimes. The presence of propagation does not imply ignition. In this study, we observe broad conditions where propagation is present but suppressible, and we do not identify a robust sustained global ignition phase as a stable attractor within the tested local-coupling families.

## 5. Discussion

### 5.1 Structural implication
The experiments indicate that local coupling can produce substantial propagation, but the regime is strongly shapeable by damping, gating, and nonlinear local rules. This is consistent with bounded-propagation behavior rather than inevitable ignition.

### 5.2 Why topology still matters
Topology consistently changes quantitative outcomes (threshold location, decay sensitivity, and persistence levels), even when qualitative phase type remains bounded/suppressible in most extended scans.

### 5.3 What this does not prove
These results do not prove ignition is impossible in all network systems. They show that, within this simulator class and tested ranges, local mechanisms alone did not produce a robust sustained ignition phase.

### 5.4 Limitations
Key limitations include:

- finite parameter coverage (despite broad sweeps)
- reliance on a specific propagation classifier
- simulator abstraction of governance processes
- metric design choices (for example, cascade-depth proxy conventions used in current pipeline)

## 6. Conclusion
Within the studied simulator family, local coupling supports propagation but does not reliably yield sustained ignition as a robust phase under tested conditions. Targeted damping and gating-like mechanisms can sharply reduce propagation share, and topology shifts quantitative thresholds rather than guaranteeing a qualitative ignition transition. These findings motivate future work on additional structural ingredients, especially nonlocal/global feedback and alternative state accumulation mechanisms.

## Reproducibility Notes
Main scripts:

- [governance_network_topology_compare.py](C:\Users\sosoy\OneDrive\文档\New project 3\System-of-Eternity\governance_network_topology_compare.py)
- [governance_network_chain_sweep.py](C:\Users\sosoy\OneDrive\文档\New project 3\System-of-Eternity\governance_network_chain_sweep.py)
- [governance_network_sim.py](C:\Users\sosoy\OneDrive\文档\New project 3\System-of-Eternity\governance_network_sim.py)

Representative output summaries:

- [governance_topology_compare_decay_targeted_pc_summary.csv](C:\Users\sosoy\OneDrive\文档\New project 3\System-of-Eternity\governance_topology_compare_decay_targeted_pc_summary.csv)
- [governance_topology_compare_decay_left_gated_summary.csv](C:\Users\sosoy\OneDrive\文档\New project 3\System-of-Eternity\governance_topology_compare_decay_left_gated_summary.csv)
- [governance_topology_compare_decay_right_gated_summary.csv](C:\Users\sosoy\OneDrive\文档\New project 3\System-of-Eternity\governance_topology_compare_decay_right_gated_summary.csv)
- [governance_topology_compare_right_feedback03_summary.csv](C:\Users\sosoy\OneDrive\文档\New project 3\System-of-Eternity\governance_topology_compare_right_feedback03_summary.csv)
- [governance_topology_compare_right_hysteresis_summary.csv](C:\Users\sosoy\OneDrive\文档\New project 3\System-of-Eternity\governance_topology_compare_right_hysteresis_summary.csv)

