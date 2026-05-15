# SOE Grand Sim v0.5 - Copilot Code Excerpts

These are the exact local code excerpts requested for v0.5 CL02 validation.

## Federation Psi Computation

```python
632: def federation_psi_terms(
633:     t_mean: float,
634:     d_mean: float,
635:     g_effective: float,
636:     s_network: float,
637:     variance: float,
638: ) -> Dict[str, float]:
639:     term_t = PSI_W_T * (1.0 - t_mean)
640:     term_d = PSI_W_D * d_mean
641:     term_g = PSI_W_G * (1.0 - g_effective)
642:     term_s = PSI_W_S * (1.0 - s_network)
643:     term_regime = 0.0
644:     term_variance = PSI_LAMBDA * variance
645:     psi_base = term_t + term_d + term_g + term_s + term_regime
646:     psi_extended = psi_base + term_variance
647:     return {
648:         "psi_base": psi_base,
649:         "psi_extended": psi_extended,
650:         "psi_term_t": term_t,
651:         "psi_term_d": term_d,
652:         "psi_term_g": term_g,
653:         "psi_term_s": term_s,
654:         "psi_term_regime": term_regime,
655:         "psi_term_variance": term_variance,
656:     }
657: 
658: 
659: def first_or_blank(values: Sequence[int]) -> object:
660:     return values[0] if values else ""
661: 
```

## Per-Step Ordering Around Topology, State Update, Psi, and Trigger A

```python
721:         detected_topology = detect_topology(actual_topology, detected_topology, step)
722:         if actual_topology in ("star_adjacent", "star") or actual_topology.startswith("hub_2"):
723:             star_adjacency_persist_steps += 1
724:             if first_star_adjacent_step is None:
725:                 first_star_adjacent_step = step
726:         if (
727:             first_star_adjacent_step is not None
728:             and reclassification_latency == ""
729:             and previous_detected != detected_topology
730:             and detected_topology in ("star_adjacent", "star", "hub_2")
731:         ):
732:             reclassification_latency = step - first_star_adjacent_step
733: 
734:         trust: List[float] = state["T"]  # type: ignore[assignment]
735:         d_raw: List[float] = state["D_raw"]  # type: ignore[assignment]
736:         d_smooth: List[float] = state["D_smooth"]  # type: ignore[assignment]
737:         d_eff: List[float] = state["D_eff"]  # type: ignore[assignment]
738:         cognition: List[float] = state["C"]  # type: ignore[assignment]
739:         role: List[float] = state["I_role"]  # type: ignore[assignment]
740:         belong: List[float] = state["I_belong"]  # type: ignore[assignment]
741:         identity: List[float] = state["I"]  # type: ignore[assignment]
742:         stability: List[float] = state["S"]  # type: ignore[assignment]
743:         node_classes: List[str] = state["class"]  # type: ignore[assignment]
744:         update_intervals: List[int] = state["update_interval"]  # type: ignore[assignment]
745:         update_phases: List[int] = state["update_phase"]  # type: ignore[assignment]
746: 
747:         g_effective = clamp(g_formal * layers["citizen"] * layers["expert"] * layers["institution"] * layers["ai"])
748:         k_d_ceiling = topology_ceiling(actual_topology, profile)
749:         suppression = max(F_MIN, 1.0 - profile.alpha_gov * g_effective)
750:         k_d_effective = min(0.15, k_d_ceiling * suppression)
751:         k_c_effective = min(0.10, profile.k_C * suppression)
752:         k_t_effective = min(0.20, profile.k_T)
753: 
754:         next_raw = d_raw[:]
755:         next_smooth = d_smooth[:]
756:         next_eff = d_eff[:]
757:         next_cognition = cognition[:]
758:         next_role = role[:]
759:         next_belong = belong[:]
760:         next_identity = identity[:]
761:         next_trust = trust[:]
762:         next_stability = stability[:]
763: 
764:         for node in range(NODE_COUNT):
765:             raw = d_raw[node]
766:             raw += scenario.base_disturbance
767:             raw += rng.uniform(-scenario.noise, scenario.noise)
768:             if rng.random() < scenario.shock_prob:
769:                 raw += scenario.shock_impact
770:             raw -= profile.lambda_damping * d_raw[node]
771:             raw = apply_scenario_disturbance(scenario, step, node, raw)
772:             next_raw[node] = clamp(raw)
773: 
774:             smooth_weight = 1.0 / max(1, profile.tau_smooth)
775:             next_smooth[node] = clamp((1.0 - smooth_weight) * d_smooth[node] + smooth_weight * next_raw[node])
776: 
777:         for node in range(NODE_COUNT):
778:             node_neighbors = neighbors[node]
779:             d_neighbor, _seen_d = neighbor_average(next_smooth, node_neighbors, rng, message_loss, next_smooth[node])
780:             c_neighbor, _seen_c = neighbor_average(cognition, node_neighbors, rng, message_loss, cognition[node])
781:             multiplier = propagation_multiplier(node, scenario, actual_topology, node_neighbors)
782:             next_eff[node] = clamp(next_smooth[node] + k_d_effective * d_neighbor * multiplier)
783: 
784:             misinformation = 0.0
785:             if scenario.psi_corruption and 35 <= step <= 110 and cluster_of(node) == 0:
786:                 misinformation = 0.025
787:             if scenario.async_loss and rng.random() < 0.06:
788:                 misinformation += 0.018
789:             correction = 0.028 * g_effective
790:             next_cognition[node] = clamp(
791:                 cognition[node]
792:                 + (0.080 * profile.alpha_cognition * next_eff[node])
793:                 + (k_c_effective * c_neighbor * multiplier)
794:                 + misinformation
795:                 - (profile.mu_cognition * cognition[node])
796:                 - correction
797:             )
798: 
799:         for node in range(NODE_COUNT):
800:             attack = identity_attack_amount(scenario, step, node_classes[node])
801:             next_role[node] = clamp(
802:                 role[node]
803:                 + (0.009 * g_effective)
804:                 - (0.030 * next_eff[node])
805:                 - (0.018 * next_cognition[node])
806:                 - attack
807:             )
808:             if node_classes[node] == "A":
809:                 next_belong[node] = 0.0
810:                 next_identity[node] = next_role[node]
811:             else:
812:                 ci_drag = 0.020 * max(0.0, 0.60 - avg(belong))
813:                 next_belong[node] = clamp(
814:                     belong[node]
815:                     + (0.006 * g_effective)
816:                     - (0.022 * next_eff[node])
817:                     - (0.020 * next_cognition[node])
818:                     - ci_drag
819:                     - attack
820:                 )
821:                 if node_classes[node] == "H":
822:                     next_identity[node] = clamp(0.55 * next_role[node] + 0.45 * next_belong[node])
823:                 else:
824:                     proxy = clamp(0.34 * next_belong[node] + 0.33 * layers["institution"] + 0.33 * layers["citizen"])
825:                     next_identity[node] = clamp(0.55 * next_role[node] + 0.45 * proxy)
826: 
827:         trigger_b_pre = (
828:             avg(next_eff) > 0.54
829:             and g_effective < 0.14
830:             and avg(trust) < 0.46
831:         )
832:         external_support = 0.0
833:         if trigger_b_pre:
834:             external_intervention_count += 1
835:             external_support = 0.030
836: 
837:         total_recovery_demand = 0.0
838:         for node in range(NODE_COUNT):
839:             if step % update_intervals[node] != update_phases[node]:
840:                 continue
841: 
842:             node_neighbors = neighbors[node]
843:             t_neighbor, seen_t = neighbor_average(trust, node_neighbors, rng, message_loss, trust[node])
844:             donor_pool = max(0.0, t_neighbor - T_RESERVE) if seen_t else 0.0
845:             r_internal = 0.010 * trust[node] * (1.0 - next_eff[node])
846:             r_network_raw = k_t_effective * donor_pool * max(0.0, 1.0 - trust[node]) * next_identity[node]
847:             r_gov = 0.014 * g_effective * max(0.0, 1.0 - trust[node]) * next_identity[node]
848:             r_base = profile.k_b * (1.0 + profile.gamma_D * next_eff[node]) * math.exp(-profile.beta * trust[node])
849:             demand = max(0.0, 0.55 - trust[node]) * (r_network_raw + r_gov + external_support)
850:             total_recovery_demand += demand
851: 
852:             resource_scale = 1.0
853:             if demand > 0.0:
854:                 if resource_budget <= 0.0:
855:                     resource_scale = 0.0
856:                     if resource_exhaustion_step == "":
857:                         resource_exhaustion_step = step
858:                 elif demand > resource_budget:
859:                     resource_scale = resource_budget / demand
860:                     resource_budget = 0.0
861:                     if resource_exhaustion_step == "":
862:                         resource_exhaustion_step = step
863:                 else:
864:                     resource_budget -= demand
865: 
866:             max_unmet_recovery_demand = max(max_unmet_recovery_demand, demand * (1.0 - resource_scale))
867: 
868:             recovery = r_internal + (r_network_raw * resource_scale) + (r_gov * resource_scale) + r_base
869:             if external_support > 0.0:
870:                 recovery += external_support * max(0.0, 1.0 - trust[node]) * resource_scale
871: 
872:             d_trust = (
873:                 -(profile.a * next_eff[node] * (1.0 + 0.50 * next_cognition[node]))
874:                 + (profile.b * (next_identity[node] - 0.50))
875:                 - (profile.c * next_cognition[node])
876:                 + recovery
877:             )
878:             next_trust[node] = clamp(trust[node] + d_trust, T_FLOOR, 1.0)
879: 
880:         for node in range(NODE_COUNT):
881:             next_stability[node] = clamp(
882:                 (0.48 * next_trust[node])
883:                 + (0.22 * next_identity[node])
884:                 + (0.17 * (1.0 - next_eff[node]))
885:                 + (0.13 * (1.0 - next_cognition[node]))
886:             )
887: 
888:         state["T"] = next_trust
889:         state["D_raw"] = next_raw
890:         state["D_smooth"] = next_smooth
891:         state["D_eff"] = next_eff
892:         state["C"] = next_cognition
893:         state["I_role"] = next_role
894:         state["I_belong"] = next_belong
895:         state["I"] = next_identity
896:         state["S"] = next_stability
897: 
898:         t_mean = avg(next_trust)
899:         d_mean = avg(next_eff)
900:         c_mean = avg(next_cognition)
901:         i_mean = avg(next_identity)
902:         s_network = compute_s_network(scenario, actual_topology, state)
903:         current_collapse_share = collapse_share(state)
904:         variance = cluster_variance(state) if actual_topology == "federation" else 0.0
905: 
906:         observed_t = t_mean
907:         observed_d = d_mean
908:         observed_g = g_effective
909:         observed_s = s_network
910:         missing_fraction = 0.0
911:         if scenario.psi_corruption:
912:             observed_t = clamp(t_mean + 0.16)
913:             observed_d = clamp(d_mean - 0.11)
914:             observed_g = max(g_effective, g_formal)
915:             observed_s = clamp(s_network + 0.12)
916:             missing_fraction = 0.28
917:         psi_terms = federation_psi_terms(
918:             observed_t,
919:             observed_d,
920:             observed_g,
921:             observed_s,
922:             variance if actual_topology == "federation" else 0.0,
923:         )
924:         psi_base = psi_terms["psi_base"]
925:         psi_extended = psi_terms["psi_extended"]
926: 
927:         if actual_topology == "federation":
928:             trigger_a = int(psi_extended >= FEDERATION_PSI_THRESHOLD)
929:             trigger_a_source = "C07_PSI_EXTENDED" if trigger_a else ""
930:         else:
931:             trigger_a = int(s_network < S_THRESHOLD)
932:             trigger_a_source = "C04_S_THRESHOLD" if trigger_a else ""
```

## Reproducibility Hashes

- Script SHA256: `4959112c299030a1feabc79287c999b770a83d755a49fb0f32ef50fa8c34acd7`
- Runs CSV SHA256: `f001777ade7b46a408f2a761b38b08de42535383a48cce3871583a6725fc7e63`
- Steps CSV SHA256: `e5398d65e44f7585159cfc1955816cfad566dfa23ee5bf1f6ab352798bdf2bc3`
- Runs data rows: `420`
- Steps data rows: `67200`

## Short Interpretation

- `federation_psi_terms()` uses current-step `t_mean`, `d_mean`, `g_effective`, `s_network`, and current cluster variance. It does not use `collapse_share` or future event labels.
- `PSI_W_REGIME = 0.0`, so `term_regime` is logged but contributes zero in the federation path.
- Federation Trigger A is assigned by `trigger_a = int(psi_extended >= FEDERATION_PSI_THRESHOLD)` and `trigger_a_source = "C07_PSI_EXTENDED"`.
- Non-federation Trigger A remains topology-local C04 S-threshold logic.
