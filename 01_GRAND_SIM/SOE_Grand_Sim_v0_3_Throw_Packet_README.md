# SOE Grand Sim v0.3 AI Throw Packet

Use `01_THROW_FIRST` for every AI.

Start with:

1. `SOE_Grand_Sim_v0_3_Reviewer_Update_Prompt.md`
2. `SOE_Grand_Sim_v0_3_Consensus.md`
3. `SOE_Grand_Simulation_v0_3_Findings.md`
4. `SOE_Grand_Sim_v0_3_Multi_AI_Review.docx`

If an AI asks for implementation or numeric verification, give files from `02_SUPPORTING`.

If an AI specifically asks for raw step/run data, give files from `03_RAW_OPTIONAL`.

Strict wording:

- CL02: calibration path found, but precursor independence is not established because `psi_score` includes `collapse_share` through `regime_weight`; v0.4 needs ablation/decomposition before claim upgrade.
- CL09: stress-tested, not deployment-ready.
- CL05: context-dependent hub mitigation, not universal 3-hub safety.

Role reminder:

- Claude: architecture audit.
- Gemini: math/topology verification.
- Grok: stress testing.
- ChatGPT: documentation and synthesis.
- Copilot: code/CSV/reproducibility review.
- Le Chat: independence audit and structural compression.

Any AI may step outside its role only if it clearly labels why.
