from __future__ import annotations

import argparse
import csv
import json
import random
import statistics
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

from .soe_v2_core import (
    build_phase1_civilization,
    build_phase1_config,
    clone_graph,
    apply_initial_failures,
)
from .soe_v3_metrics import (
    compute_cascade_depth,
    compute_critical_node_index,
    compute_failure_rate,
    compute_resource_exhaustion_map,
    compute_survival_clusters,
    compute_time_to_collapse,
)
from .soe_v3_topology import PHASE1_TOPOLOGIES, build_phase1_topology


FAILURE_POLICIES = {
    "none",
    "highest-degree",
    "lowest-degree",
    "specific",
}


@dataclass(frozen=True)
class Phase1RunConfig:
    topology: str
    seed: int = 1
    years: int = 500
    step_years: int = 10
    random_edge_probability: float = 0.06
    contagion_penalty: float = 0.08
    governance_survival_threshold: float = 0.45
    failure_policy: str = "highest-degree"
    failure_count: int = 1
    failure_node_ids: Tuple[int, ...] = ()

    def validate(self) -> None:
        if self.topology not in PHASE1_TOPOLOGIES:
            raise ValueError(f"topology must be one of {PHASE1_TOPOLOGIES}")
        if self.failure_policy not in FAILURE_POLICIES:
            raise ValueError(f"failure_policy must be one of {sorted(FAILURE_POLICIES)}")
        if self.failure_count < 0:
            raise ValueError("failure_count must be non-negative")
        if not 0.0 <= self.random_edge_probability <= 1.0:
            raise ValueError("random_edge_probability must be between 0 and 1")


@dataclass
class Phase1RunResult:
    config: Phase1RunConfig
    initial_node_count: int
    initial_failure_ids: Tuple[int, ...]
    history_rows: List[Dict[str, float | int | str]]
    summary: Dict[str, object]
    cni_rows: List[Dict[str, float | int]] | None = None


def resolve_failure_targets(
    graph,
    config: Phase1RunConfig,
) -> Tuple[int, ...]:
    node_ids = list(graph.adjacency)
    if config.failure_policy == "none" or config.failure_count == 0:
        return ()
    if config.failure_policy == "specific":
        return tuple(node_id for node_id in config.failure_node_ids if node_id in graph.adjacency)

    reverse = config.failure_policy == "highest-degree"
    ranked = sorted(
        node_ids,
        key=lambda node_id: (graph.degree(node_id), -node_id if reverse else node_id),
        reverse=reverse,
    )
    return tuple(ranked[: config.failure_count])


def capture_step_row(
    civilization,
    *,
    topology: str,
    year: int,
    events: Sequence[str],
    initial_node_count: int,
) -> Dict[str, float | int | str]:
    active_nodes = list(civilization.nodes)
    failed_node_ids = set(civilization.failed_node_ids)
    stable_node_ids = {node.node_id for node in active_nodes if node.node_id not in failed_node_ids}
    avg_stability = (
        statistics.fmean(node.governance_stability for node in active_nodes)
        if active_nodes
        else 0.0
    )
    return {
        "topology": topology,
        "year": year,
        "active_nodes": len(active_nodes),
        "failed_node_count": len(failed_node_ids),
        "failure_rate": compute_failure_rate(initial_node_count, failed_node_ids),
        "avg_stability": avg_stability,
        "connected_components": civilization.current_component_count(),
        "largest_component_ratio": civilization.largest_component_ratio(),
        "stable_cluster_count": len(compute_survival_clusters(civilization.network, stable_node_ids)),
        "events": ";".join(events),
    }


def summarize_phase1_run(
    civilization,
    *,
    config: Phase1RunConfig,
    initial_graph,
    history_rows: Sequence[Dict[str, float | int | str]],
    initial_failure_ids: Sequence[int],
    initial_node_count: int,
) -> Dict[str, object]:
    active_nodes = list(civilization.nodes)
    failed_node_ids = set(civilization.failed_node_ids)
    stable_node_ids = {node.node_id for node in active_nodes if node.node_id not in failed_node_ids}
    survival_clusters = compute_survival_clusters(civilization.network, stable_node_ids)
    final_avg_stability = (
        statistics.fmean(node.governance_stability for node in active_nodes)
        if active_nodes
        else 0.0
    )
    return {
        "topology": config.topology,
        "seed": config.seed,
        "initial_node_count": initial_node_count,
        "final_active_nodes": len(active_nodes),
        "edge_count": initial_graph.number_of_edges(),
        "initial_failure_ids": list(initial_failure_ids),
        "final_failed_node_count": len(failed_node_ids),
        "failure_rate": compute_failure_rate(initial_node_count, failed_node_ids),
        "cascade_depth": compute_cascade_depth(initial_graph, initial_failure_ids, failed_node_ids),
        "time_to_collapse": compute_time_to_collapse(
            history_rows,
            stability_threshold=config.governance_survival_threshold,
        ),
        "final_avg_stability": final_avg_stability,
        "final_connected_components": civilization.current_component_count(),
        "survival_clusters": survival_clusters,
        "largest_survival_cluster": max(survival_clusters, default=0),
        "resource_exhaustion_nodes": compute_resource_exhaustion_map(),
    }


def run_phase1_experiment(
    config: Phase1RunConfig,
    *,
    include_cni: bool = False,
    cni_limit: int | None = None,
) -> Phase1RunResult:
    config.validate()
    base_config = build_phase1_config(
        years=config.years,
        step_years=config.step_years,
        governance_survival_threshold=config.governance_survival_threshold,
        contagion_penalty=config.contagion_penalty,
    )
    rng = random.Random(config.seed)
    preview_graph = build_phase1_topology(
        config.topology,
        list(range(60)),
        rng,
        random_edge_probability=config.random_edge_probability,
    )

    civilization = build_phase1_civilization(base_config, config.seed, preview_graph)
    initial_graph = clone_graph(civilization.network)
    initial_node_count = len(civilization.nodes)
    actual_failure_ids = apply_initial_failures(
        civilization,
        resolve_failure_targets(civilization.network, config),
    )

    history_rows: List[Dict[str, float | int | str]] = [
        capture_step_row(
            civilization,
            topology=config.topology,
            year=0,
            events=("initial_state",),
            initial_node_count=initial_node_count,
        )
    ]

    for step_index in range(1, base_config.steps + 1):
        year = step_index * base_config.step_years
        events = civilization.step(year)
        history_rows.append(
            capture_step_row(
                civilization,
                topology=config.topology,
                year=year,
                events=events,
                initial_node_count=initial_node_count,
            )
        )

    summary = summarize_phase1_run(
        civilization,
        config=config,
        initial_graph=initial_graph,
        history_rows=history_rows,
        initial_failure_ids=actual_failure_ids,
        initial_node_count=initial_node_count,
    )
    result = Phase1RunResult(
        config=config,
        initial_node_count=initial_node_count,
        initial_failure_ids=tuple(actual_failure_ids),
        history_rows=history_rows,
        summary=summary,
    )
    if include_cni:
        result.cni_rows = compute_cni_rows(result, limit=cni_limit)
    return result


def compute_cni_rows(
    baseline_result: Phase1RunResult,
    *,
    limit: int | None = None,
) -> List[Dict[str, float | int]]:
    if baseline_result.config.failure_policy != "none" or baseline_result.initial_failure_ids:
        baseline_result = run_phase1_experiment(
            replace(
                baseline_result.config,
                failure_policy="none",
                failure_count=0,
                failure_node_ids=(),
            ),
            include_cni=False,
        )

    baseline_summary = baseline_result.summary
    baseline_stability = float(baseline_summary["final_avg_stability"])
    topology = baseline_result.config.topology
    candidate_count = baseline_result.initial_node_count if limit is None else min(limit, baseline_result.initial_node_count)

    baseline_graph = build_phase1_topology(
        topology,
        list(range(baseline_result.initial_node_count)),
        random.Random(baseline_result.config.seed),
        random_edge_probability=baseline_result.config.random_edge_probability,
    )
    ranked_candidates = sorted(
        baseline_graph.adjacency,
        key=lambda node_id: (baseline_graph.degree(node_id), -node_id),
        reverse=True,
    )[:candidate_count]

    rows: List[Dict[str, float | int]] = []
    for node_id in ranked_candidates:
        stressed_config = replace(
            baseline_result.config,
            failure_policy="specific",
            failure_node_ids=(node_id,),
            failure_count=1,
        )
        stressed_result = run_phase1_experiment(stressed_config, include_cni=False)
        stressed_stability = float(stressed_result.summary["final_avg_stability"])
        rows.append(
            {
                "node_id": node_id,
                "degree": baseline_graph.degree(node_id),
                "critical_node_index": compute_critical_node_index(
                    baseline_stability,
                    stressed_stability,
                ),
                "stressed_failure_rate": float(stressed_result.summary["failure_rate"]),
            }
        )
    return sorted(rows, key=lambda row: (-float(row["critical_node_index"]), -int(row["degree"]), int(row["node_id"])))


def run_phase1_suite(
    *,
    topologies: Sequence[str] = PHASE1_TOPOLOGIES,
    seed: int = 1,
    years: int = 500,
    step_years: int = 10,
    random_edge_probability: float = 0.06,
    failure_policy: str = "highest-degree",
    failure_count: int = 1,
) -> List[Phase1RunResult]:
    return [
        run_phase1_experiment(
            Phase1RunConfig(
                topology=topology,
                seed=seed,
                years=years,
                step_years=step_years,
                random_edge_probability=random_edge_probability,
                failure_policy=failure_policy,
                failure_count=failure_count,
            )
        )
        for topology in topologies
    ]


def write_rows(rows: Sequence[Dict[str, object]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.suffix.lower() == ".csv":
        with output_path.open("w", newline="", encoding="utf-8") as handle:
            fieldnames = list(rows[0].keys()) if rows else []
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        return
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(list(rows), handle, indent=2)


def print_result(result: Phase1RunResult) -> None:
    summary = result.summary
    print(f"Topology: {summary['topology']}")
    print(f"Initial failures: {summary['initial_failure_ids']}")
    print(f"Final failure rate: {float(summary['failure_rate']):.3f}")
    print(f"Cascade depth: {summary['cascade_depth']}")
    collapse = summary["time_to_collapse"]
    print(f"Time to collapse: {collapse if collapse is not None else 'not reached'}")
    print(f"Final average stability: {float(summary['final_avg_stability']):.3f}")
    print(f"Survival clusters: {summary['survival_clusters']}")
    if result.cni_rows:
        top_cni = ", ".join(
            f"{row['node_id']}={float(row['critical_node_index']):.3f}"
            for row in result.cni_rows[:5]
        )
        print(f"Top critical nodes: {top_cni}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run SOE v3 Phase 1 topology experiments.")
    parser.add_argument("--topology", choices=[*PHASE1_TOPOLOGIES, "all"], default="all")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--years", type=int, default=500)
    parser.add_argument("--step-years", type=int, default=10)
    parser.add_argument("--random-edge-probability", type=float, default=0.06)
    parser.add_argument("--failure-policy", choices=sorted(FAILURE_POLICIES), default="highest-degree")
    parser.add_argument("--failure-count", type=int, default=1)
    parser.add_argument("--failure-node-ids", default="")
    parser.add_argument("--include-cni", action="store_true")
    parser.add_argument("--cni-limit", type=int, default=10)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--history-output", type=Path)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    failure_node_ids = tuple(
        int(part.strip())
        for part in args.failure_node_ids.split(",")
        if part.strip()
    )

    if args.topology == "all":
        results = run_phase1_suite(
            topologies=PHASE1_TOPOLOGIES,
            seed=args.seed,
            years=args.years,
            step_years=args.step_years,
            random_edge_probability=args.random_edge_probability,
            failure_policy=args.failure_policy,
            failure_count=args.failure_count,
        )
        for result in results:
            print_result(result)
            print("")
        if args.output:
            write_rows([result.summary for result in results], args.output)
        return

    result = run_phase1_experiment(
        Phase1RunConfig(
            topology=args.topology,
            seed=args.seed,
            years=args.years,
            step_years=args.step_years,
            random_edge_probability=args.random_edge_probability,
            failure_policy="specific" if failure_node_ids else args.failure_policy,
            failure_count=args.failure_count,
            failure_node_ids=failure_node_ids,
        ),
        include_cni=args.include_cni,
        cni_limit=args.cni_limit,
    )
    print_result(result)
    if args.output:
        write_rows([result.summary], args.output)
    if args.history_output:
        write_rows(result.history_rows, args.history_output)
    if args.include_cni and result.cni_rows and args.output:
        cni_path = args.output.with_name(f"{args.output.stem}_cni{args.output.suffix}")
        write_rows(result.cni_rows, cni_path)


if __name__ == "__main__":
    main()
