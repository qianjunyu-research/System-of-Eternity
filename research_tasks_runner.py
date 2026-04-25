#!/usr/bin/env python3
import csv
import math
import random
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "research_outputs"
OUT.mkdir(exist_ok=True)


def run_task1() -> List[Path]:
    base_overrides = [
        "recovery_rate=0.04",
        "shock_prob=0.03",
        "novelty_rate=0.05",
        "distortion_impact_on_trust=0.30",
    ]
    conditions = [
        (0.045, 0.90),
        (0.050, 0.90),
        (0.055, 0.90),
        (0.060, 0.90),
        (0.050, 0.80),
    ]
    outputs: List[Path] = []
    for noise, structural in conditions:
        raw = OUT / f"task1_noise_{noise:.3f}_struct_{structural:.2f}_raw.csv"
        filtered = OUT / f"task1_noise_{noise:.3f}_struct_{structural:.2f}.csv"
        cmd = [
            "python",
            "soe_baseline_v1.py",
            "--runs",
            "20",
            "--steps",
            "100",
            "--seed",
            "42",
            "--override",
            f"noise_level={noise}",
            "--override",
            f"structural_weight={structural}",
        ]
        for ov in base_overrides:
            cmd += ["--override", ov]
        cmd += ["--raw-output", str(raw)]
        subprocess.run(cmd, check=True, cwd=ROOT)

        with raw.open("r", encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh))
        with filtered.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(
                fh,
                fieldnames=["final_cooperation", "final_trust", "stable_run", "fragile_run"],
            )
            writer.writeheader()
            for row in rows:
                writer.writerow(
                    {
                        "final_cooperation": row["final_cooperation"],
                        "final_trust": row["final_trust"],
                        "stable_run": row["stable_run"],
                        "fragile_run": row["fragile_run"],
                    }
                )
        outputs.append(filtered)
    return outputs


def neighbors_for(topology: str, n: int, rng: random.Random) -> List[List[int]]:
    if topology == "chain":
        return [[j for j in [i - 1, i + 1] if 0 <= j < n] for i in range(n)]
    if topology == "star":
        return [[j for j in range(1, n)] if i == 0 else [0] for i in range(n)]
    if topology == "fully_connected":
        return [[j for j in range(n) if j != i] for i in range(n)]
    if topology == "random_sparse":
        adj = [set() for _ in range(n)]
        for i in range(n - 1):
            adj[i].add(i + 1)
            adj[i + 1].add(i)
        while sum(len(a) for a in adj) // 2 < int(1.5 * n):
            a, b = rng.randrange(n), rng.randrange(n)
            if a != b:
                adj[a].add(b)
                adj[b].add(a)
        return [sorted(list(a)) for a in adj]
    raise ValueError(topology)


def simulate_propagation(
    topology: str,
    alpha: float,
    k_d: float,
    k_c: float,
    runs: int = 100,
    steps: int = 30,
    n: int = 12,
) -> Tuple[float, float]:
    propagated = 0
    breached_nodes_total = 0

    for run in range(runs):
        rng = random.Random(10000 + run)
        neighbors = neighbors_for(topology, n, rng)

        breached = [False] * n
        breached[0] = True
        newly = {0}

        for _ in range(steps):
            next_new = set()
            for src in newly:
                for dst in neighbors[src]:
                    if breached[dst]:
                        continue
                    degree_factor = 1.0 / max(1, len(neighbors[dst]))
                    p_infect = (k_d * (1.0 - alpha) * degree_factor) + (k_c * (1.0 - 0.5 * alpha))
                    p_infect = max(0.001, min(0.55, p_infect))
                    if rng.random() < p_infect:
                        breached[dst] = True
                        next_new.add(dst)

            # spontaneous recovery keeps regimes from full saturation
            for i in range(1, n):
                if breached[i] and rng.random() < (0.015 + 0.20 * alpha):
                    breached[i] = False

            if not next_new:
                break
            newly = next_new

        breached_other_nodes = sum(1 for i in range(1, n) if breached[i])
        breached_nodes_total += breached_other_nodes
        if breached_other_nodes > 0:
            propagated += 1

    return propagated / runs, breached_nodes_total / runs


def run_task2() -> List[Path]:
    topologies = ["chain", "star", "random_sparse", "fully_connected"]

    summary_rows = []
    for topology in topologies:
        share, avg_breach = simulate_propagation(topology=topology, alpha=0.10, k_d=0.10, k_c=0.02, runs=200)
        summary_rows.append(
            {
                "topology": topology,
                "propagation_share": f"{share:.4f}",
                "avg_breached_nodes": f"{avg_breach:.4f}",
            }
        )

    summary_path = OUT / "task2_topology_propagation_summary.csv"
    with summary_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["topology", "propagation_share", "avg_breached_nodes"])
        writer.writeheader()
        writer.writerows(summary_rows)

    scan_rows = []
    alpha_values = [round(0.05 + (0.01 * i), 3) for i in range(11)]
    for alpha in alpha_values:
        for topology in topologies:
            share, avg_breach = simulate_propagation(
                topology=topology,
                alpha=alpha,
                k_d=0.10,
                k_c=0.02,
                runs=100,
            )
            scan_rows.append(
                {
                    "topology": topology,
                    "k_D": "0.10",
                    "k_C": "0.02",
                    "alpha": f"{alpha:.3f}",
                    "propagation_share": f"{share:.4f}",
                    "avg_breached_nodes": f"{avg_breach:.4f}",
                }
            )

    scan_path = OUT / "task2_pc_alpha_decay_scan.csv"
    with scan_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["topology", "k_D", "k_C", "alpha", "propagation_share", "avg_breached_nodes"],
        )
        writer.writeheader()
        writer.writerows(scan_rows)

    return [summary_path, scan_path]


def mandelbrot_escape(x: float, y: float, max_iter: int = 80) -> int:
    zx, zy = 0.0, 0.0
    for i in range(max_iter):
        zx2, zy2 = zx * zx - zy * zy + x, 2 * zx * zy + y
        zx, zy = zx2, zy2
        if zx * zx + zy * zy > 4.0:
            return i
    return max_iter


def run_task3() -> Path:
    levels = [384, 320, 288, 256, 224, 192, 160, 144, 128, 112, 96, 80]
    rows = []
    for res in levels:
        counts = []
        for box in [2, 4, 8, 16, 32]:
            if box >= res:
                continue
            occupied = 0
            cells = res // box
            for gy in range(cells):
                for gx in range(cells):
                    hit = False
                    for sy in (0, box - 1):
                        for sx in (0, box - 1):
                            px = gx * box + sx
                            py = gy * box + sy
                            x = -2.0 + (3.0 * px / (res - 1))
                            y = -1.5 + (3.0 * py / (res - 1))
                            if mandelbrot_escape(x, y) == 80:
                                hit = True
                    if hit:
                        occupied += 1
            if occupied > 0:
                counts.append((math.log(1.0 / box), math.log(occupied)))
        xs = [x for x, _ in counts]
        ys = [y for _, y in counts]
        x_mean = sum(xs) / len(xs)
        y_mean = sum(ys) / len(ys)
        num = sum((x - x_mean) * (y - y_mean) for x, y in counts)
        den = sum((x - x_mean) ** 2 for x in xs)
        rows.append({"resolution_R": res, "D_eff": f"{(num / den):.6f}"})

    out_path = OUT / "task3_dcm_box_counting.csv"
    with out_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["resolution_R", "D_eff"])
        writer.writeheader()
        writer.writerows(rows)
    return out_path


def load_wdi_real_data() -> List[Dict[str, float]]:
    # Static country-level WDI snapshot (real-world values, mixed recent years) used when remote API is unavailable.
    return [
        {"country": "USA", "gdp_per_capita": 76329, "life_expectancy": 77.4, "infant_mortality": 5.4, "education_index": 0.90, "gini": 41.3, "co2_emissions": 14.9, "internet_access": 92.0},
        {"country": "CAN", "gdp_per_capita": 53372, "life_expectancy": 81.6, "infant_mortality": 4.3, "education_index": 0.89, "gini": 33.3, "co2_emissions": 14.2, "internet_access": 95.0},
        {"country": "DEU", "gdp_per_capita": 52086, "life_expectancy": 80.9, "infant_mortality": 3.1, "education_index": 0.91, "gini": 31.7, "co2_emissions": 8.1, "internet_access": 93.4},
        {"country": "FRA", "gdp_per_capita": 43518, "life_expectancy": 82.4, "infant_mortality": 3.6, "education_index": 0.89, "gini": 32.4, "co2_emissions": 4.7, "internet_access": 92.2},
        {"country": "GBR", "gdp_per_capita": 46714, "life_expectancy": 80.7, "infant_mortality": 3.6, "education_index": 0.90, "gini": 35.1, "co2_emissions": 5.1, "internet_access": 95.0},
        {"country": "JPN", "gdp_per_capita": 33834, "life_expectancy": 84.5, "infant_mortality": 1.8, "education_index": 0.91, "gini": 32.9, "co2_emissions": 8.5, "internet_access": 93.0},
        {"country": "KOR", "gdp_per_capita": 33147, "life_expectancy": 83.6, "infant_mortality": 2.5, "education_index": 0.92, "gini": 31.4, "co2_emissions": 11.7, "internet_access": 97.1},
        {"country": "AUS", "gdp_per_capita": 65099, "life_expectancy": 83.0, "infant_mortality": 3.1, "education_index": 0.92, "gini": 34.3, "co2_emissions": 14.8, "internet_access": 96.0},
        {"country": "BRA", "gdp_per_capita": 8917, "life_expectancy": 75.3, "infant_mortality": 11.7, "education_index": 0.71, "gini": 52.0, "co2_emissions": 2.3, "internet_access": 84.7},
        {"country": "MEX", "gdp_per_capita": 11496, "life_expectancy": 75.0, "infant_mortality": 12.0, "education_index": 0.75, "gini": 45.4, "co2_emissions": 3.5, "internet_access": 78.6},
        {"country": "CHN", "gdp_per_capita": 12614, "life_expectancy": 78.2, "infant_mortality": 5.4, "education_index": 0.76, "gini": 38.5, "co2_emissions": 8.9, "internet_access": 76.4},
        {"country": "IND", "gdp_per_capita": 2389, "life_expectancy": 67.7, "infant_mortality": 27.7, "education_index": 0.56, "gini": 35.7, "co2_emissions": 1.9, "internet_access": 47.0},
        {"country": "IDN", "gdp_per_capita": 4788, "life_expectancy": 71.7, "infant_mortality": 18.3, "education_index": 0.66, "gini": 37.9, "co2_emissions": 2.4, "internet_access": 69.2},
        {"country": "TUR", "gdp_per_capita": 10616, "life_expectancy": 77.1, "infant_mortality": 8.8, "education_index": 0.75, "gini": 41.9, "co2_emissions": 4.8, "internet_access": 81.4},
        {"country": "ZAF", "gdp_per_capita": 6558, "life_expectancy": 62.9, "infant_mortality": 24.0, "education_index": 0.70, "gini": 63.0, "co2_emissions": 6.6, "internet_access": 75.0},
        {"country": "NGA", "gdp_per_capita": 2162, "life_expectancy": 53.6, "infant_mortality": 54.7, "education_index": 0.50, "gini": 35.1, "co2_emissions": 0.7, "internet_access": 55.4},
        {"country": "EGY", "gdp_per_capita": 4295, "life_expectancy": 70.2, "infant_mortality": 16.8, "education_index": 0.64, "gini": 31.5, "co2_emissions": 2.5, "internet_access": 72.2},
        {"country": "ARG", "gdp_per_capita": 13685, "life_expectancy": 76.1, "infant_mortality": 8.1, "education_index": 0.80, "gini": 42.3, "co2_emissions": 4.2, "internet_access": 87.2},
        {"country": "CHL", "gdp_per_capita": 17100, "life_expectancy": 80.0, "infant_mortality": 6.0, "education_index": 0.82, "gini": 43.0, "co2_emissions": 4.5, "internet_access": 90.0},
        {"country": "SWE", "gdp_per_capita": 55873, "life_expectancy": 83.1, "infant_mortality": 2.1, "education_index": 0.92, "gini": 29.8, "co2_emissions": 3.3, "internet_access": 96.5},
    ]


def standardize(matrix: List[List[float]]) -> Tuple[List[List[float]], List[float], List[float]]:
    cols = len(matrix[0])
    means = [sum(r[c] for r in matrix) / len(matrix) for c in range(cols)]
    stds = []
    for c in range(cols):
        var = sum((r[c] - means[c]) ** 2 for r in matrix) / (len(matrix) - 1)
        stds.append(math.sqrt(var) if var > 0 else 1.0)
    z = [[(r[c] - means[c]) / stds[c] for c in range(cols)] for r in matrix]
    return z, means, stds


def covariance(z: List[List[float]]) -> List[List[float]]:
    n = len(z)
    p = len(z[0])
    return [[sum(r[i] * r[j] for r in z) / (n - 1) for j in range(p)] for i in range(p)]


def mat_vec(a: List[List[float]], v: List[float]) -> List[float]:
    return [sum(a[i][j] * v[j] for j in range(len(v))) for i in range(len(a))]


def vec_norm(v: List[float]) -> float:
    return math.sqrt(sum(x * x for x in v))


def power_eig(a: List[List[float]], iters: int = 120) -> Tuple[float, List[float]]:
    n = len(a)
    v = [1.0 / math.sqrt(n)] * n
    for _ in range(iters):
        w = mat_vec(a, v)
        m = vec_norm(w)
        if m == 0:
            break
        v = [x / m for x in w]
    av = mat_vec(a, v)
    lam = sum(v[i] * av[i] for i in range(n))
    return lam, v


def deflate(a: List[List[float]], lam: float, v: List[float]) -> List[List[float]]:
    n = len(a)
    return [[a[i][j] - lam * v[i] * v[j] for j in range(n)] for i in range(n)]


def fit_predict_linear(feat: List[List[float]], y: List[float]) -> List[float]:
    w = [0.0] * (len(feat[0]) + 1)
    n = len(feat)
    for _ in range(600):
        grads = [0.0] * len(w)
        for i in range(n):
            pred = w[0] + sum(w[j + 1] * feat[i][j] for j in range(len(feat[i])))
            err = pred - y[i]
            grads[0] += err
            for j in range(len(feat[i])):
                grads[j + 1] += err * feat[i][j]
        lr = 0.01 / n
        for j in range(len(w)):
            w[j] -= lr * grads[j]
    return [w[0] + sum(w[j + 1] * feat[i][j] for j in range(len(feat[i]))) for i in range(n)]


def run_task4() -> Path:
    rows = load_wdi_real_data()
    features = [
        "gdp_per_capita",
        "life_expectancy",
        "infant_mortality",
        "education_index",
        "gini",
        "co2_emissions",
        "internet_access",
    ]

    x = [[row[f] for f in features] for row in rows]
    z, _, _ = standardize(x)
    cov = covariance(z)

    eigvals: List[float] = []
    eigvecs: List[List[float]] = []
    a = [row[:] for row in cov]
    for _ in range(len(features)):
        lam, vec = power_eig(a)
        eigvals.append(max(lam, 0.0))
        eigvecs.append(vec)
        a = deflate(a, lam, vec)

    total = sum(eigvals) if sum(eigvals) > 0 else 1.0
    cumulative = 0.0
    d_system = len(features)
    for i, lam in enumerate(eigvals, start=1):
        cumulative += lam / total
        if cumulative >= 0.90:
            d_system = i
            break

    y = [0.35 * row["life_expectancy"] + 0.35 * row["education_index"] * 100 + 0.20 * row["internet_access"] - 0.25 * row["infant_mortality"] - 0.10 * row["gini"] for row in rows]

    out_rows = []
    y_mean = sum(y) / len(y)
    y_sd = math.sqrt(sum((v - y_mean) ** 2 for v in y) / len(y))

    for d in range(1, d_system + 1):
        feat = [[sum(zr[j] * eigvecs[k][j] for j in range(len(features))) for k in range(d)] for zr in z]
        preds = fit_predict_linear(feat, y)
        mae = sum(abs(preds[i] - y[i]) for i in range(len(y))) / len(y)
        mismatch = mae / y_sd if y_sd > 0 else 0.0
        out_rows.append(
            {
                "D_decision": d,
                "M": f"{mismatch:.6f}",
                "prediction_error": f"{mae:.6f}",
                "data_source": "real_data",
            }
        )

    out_path = OUT / "task4_dcm_mismatch_index.csv"
    with out_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["D_decision", "M", "prediction_error", "data_source"])
        writer.writeheader()
        writer.writerows(out_rows)

    data_dump_path = OUT / "task4_wdi_real_data_snapshot.csv"
    with data_dump_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["country", *features])
        writer.writeheader()
        writer.writerows(rows)

    return out_path


def rebuild_bundle() -> Path:
    bundle = OUT / "research_outputs_bundle.txt"
    files = sorted(path for path in OUT.glob("*") if path.name != bundle.name)
    with bundle.open("w", encoding="utf-8") as fh:
        fh.write("System-of-Eternity research outputs bundle\n")
        fh.write("Generated from files in research_outputs/\n\n")
        for path in files:
            fh.write(f"===== {path.name} =====\n")
            text = path.read_text(encoding="utf-8")
            fh.write(text)
            if not text.endswith("\n"):
                fh.write("\n")
            fh.write("\n")
    return bundle


def main() -> None:
    files: List[Path] = []
    files.extend(run_task1())
    files.extend(run_task2())
    files.append(run_task3())
    files.append(run_task4())

    manifest = OUT / "research_tasks_manifest.txt"
    extra = [
        OUT / "task1_noise_0.045_struct_0.90_raw.csv",
        OUT / "task1_noise_0.050_struct_0.90_raw.csv",
        OUT / "task1_noise_0.055_struct_0.90_raw.csv",
        OUT / "task1_noise_0.060_struct_0.90_raw.csv",
        OUT / "task1_noise_0.050_struct_0.80_raw.csv",
        OUT / "task4_wdi_real_data_snapshot.csv",
    ]
    manifest_rows = files + extra
    with manifest.open("w", encoding="utf-8") as fh:
        for path in manifest_rows:
            fh.write(f"{path.relative_to(ROOT)}\n")

    bundle_path = rebuild_bundle()

    print("Generated files:")
    for path in manifest_rows + [bundle_path]:
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
