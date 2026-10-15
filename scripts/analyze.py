#!/usr/bin/env python3
"""Summarize an overhang-bench run.

    python scripts/analyze.py results [--manifest data/castro2020_meshes.csv]

Reads results/orientations.csv, results/print_proxy.csv and, if present,
results/prusaslicer.csv, and writes results/report.md with:
  1. reproduction check against Castro (2020), Table 4.2.1 (angular distance
     between build directions d, which is the meaningful error: near the poles
     t2 = +-pi/2 the angle t1 is ill-conditioned);
  2. search-strategy comparison (best f found, evaluations, time);
  3. per-mesh print estimates: proxy and PrusaSlicer, per pose;
  4. rank agreement between proxy and PrusaSlicer (Spearman, per metric).
Only standard library is used.
"""
import csv, math, sys, argparse
from pathlib import Path
from collections import defaultdict


def d_of(t1, t2):
    return (-math.sin(t2), math.sin(t1) * math.cos(t2), math.cos(t1) * math.cos(t2))


def ang_deg(a, b):
    c = max(-1.0, min(1.0, sum(x * y for x, y in zip(a, b))))
    return math.degrees(math.acos(c))


def read(p):
    with open(p, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def spearman(x, y):
    def rank(v):
        o = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(o):
            j = i
            while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]:
                j += 1
            for k in range(i, j + 1):
                r[o[k]] = (i + j) / 2
            i = j + 1
        return r
    rx, ry = rank(x), rank(y)
    n = len(x)
    mx, my = sum(rx) / n, sum(ry) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    sx = math.sqrt(sum((a - mx) ** 2 for a in rx)); sy = math.sqrt(sum((b - my) ** 2 for b in ry))
    return sxy / (sx * sy) if sx > 0 and sy > 0 else float("nan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results")
    ap.add_argument("--manifest", default=str(Path(__file__).parent.parent / "data/castro2020_meshes.csv"))
    a = ap.parse_args()
    R = Path(a.results)
    orient = read(R / "orientations.csv")
    proxy = read(R / "print_proxy.csv")
    slicer = read(R / "prusaslicer.csv") if (R / "prusaslicer.csv").exists() else []
    ref = {r["mesh"]: (float(r["table421_t1"]), float(r["table421_t2"])) for r in read(a.manifest)}

    out = []
    w = out.append
    w("# overhang-bench report\n")
    vers = sorted({r.get("slicer_version", "") for r in slicer if r.get("slicer_version")})
    vtxt = ", ".join(vers) if vers else "PrusaSlicer (version not recorded in prusaslicer.csv)"
    w("All print numbers are *estimates*: `proxy` = overhang-bench's vertical-column model; "
      f"`PrusaSlicer` = {vtxt} G-code estimates with scripts/prusaslicer_reference.ini. "
      "None of them is a measurement of a physical print.\n")

    # 1. reproduction
    w("## 1. Reproduction of Castro (2020), Table 4.2.1\n")
    w("Angular distance (degrees) between the build direction of Table 4.2.1 and the one found here.\n")
    w("| mesh | Table 4.2.1 (t1, t2) | objective | search | found (t1, t2) | angle to table (deg) |")
    w("|---|---|---|---|---|---|")
    for r in orient:
        if r["mesh"] not in ref or r["objective"] != "castro-eq":
            continue
        t1, t2 = float(r["t1"]), float(r["t2"])
        rt = ref[r["mesh"]]
        w(f"| {r['mesh']} | ({rt[0]:.4f}, {rt[1]:.4f}) | {r['objective']} | {r['search']} | "
          f"({t1:.4f}, {t2:.4f}) | {ang_deg(d_of(t1, t2), d_of(*rt)):.2f} |")

    # 2. search strategies
    w("\n## 2. Search strategies\n")
    w("f relative to the best value found by any strategy for that (mesh, objective); "
      "0 % = found the best.\n")
    w("| mesh | objective | search | f − f* (%) | evaluations | time (s) |")
    w("|---|---|---|---|---|---|")
    best = defaultdict(lambda: float("inf"))
    for r in orient:
        best[(r["mesh"], r["objective"])] = min(best[(r["mesh"], r["objective"])], float(r["fval"]))
    for r in orient:
        b = best[(r["mesh"], r["objective"])]
        gap = 100 * (float(r["fval"]) - b) / abs(b) if b != 0 else 0.0
        w(f"| {r['mesh']} | {r['objective']} | {r['search']} | {gap:.2f} | {r['evals']} | "
          f"{float(r['seconds']):.2f} |")

    # 3. print estimates
    w("\n## 3. Print estimates per pose\n")
    sl = {(r["mesh"], r["pose"]): r for r in slicer if r.get("status") == "ok"}
    w("| mesh | pose | height (mm) | overhang area (mm²) | proxy support vol. (mm³) | proxy filament (m) | "
      "proxy time (min) | PrusaSlicer filament (m) | PrusaSlicer support filament (m) | PrusaSlicer time (min) |")
    w("|---|---|---|---|---|---|---|---|---|---|")
    for r in proxy:
        s = sl.get((r["mesh"], r["pose"]))
        sf = f"{float(s['filament_mm'])/1000:.2f}" if s else "–"
        ss = f"{float(s['support_filament_mm'])/1000:.2f}" if s else "–"
        st = f"{float(s['time_min']):.0f}" if s else "–"
        w(f"| {r['mesh']} | {r['pose']} | {float(r['height_mm']):.1f} | {float(r['overhang_area_mm2']):.0f} | "
          f"{float(r['support_volume_mm3']):.0f} | {float(r['filament_m']):.2f} | {float(r['time_min']):.0f} | "
          f"{sf} | {ss} | {st} |")

    # 3b. per-method summary (slicer)
    if sl:
        import statistics
        w("\n## 3b. Summary per method (PrusaSlicer estimates)\n")
        w("Median over meshes of the reduction relative to the initial pose; in parentheses, the "
          "number of meshes where the method is the best of all poses (ties count for each tied method).\n")
        meshes_ = sorted({m for m, _ in sl})
        methods = sorted({p for _, p in sl} - {"initial"})
        w("| method | support filament | print time | total filament |")
        w("|---|---|---|---|")
        for m in methods:
            cells = []
            for key in ("support_filament_mm", "time_min", "filament_mm"):
                red, wins, n = [], 0, 0
                for mesh in meshes_:
                    if (mesh, m) not in sl or (mesh, "initial") not in sl:
                        continue
                    n += 1
                    v0, v = float(sl[(mesh, "initial")][key]), float(sl[(mesh, m)][key])
                    if v0 > 0:
                        red.append(1 - v / v0)
                    best = min(float(r[key]) for (mm, _), r in sl.items() if mm == mesh)
                    wins += v <= best * (1 + 1e-9)
                cells.append(f"{-100 * statistics.median(red):+.1f}% ({wins}/{n})" if red else "–")
            w(f"| {m} | " + " | ".join(cells) + " |")

    # 4. proxy vs slicer
    if sl:
        w("\n## 4. Does the proxy rank poses like the slicer?\n")
        w("Spearman rank correlation over all (mesh, pose) pairs, pooled; and per mesh "
          "the fraction of pose pairs ordered the same way (support).\n")
        pairs = [(r, sl[(r["mesh"], r["pose"])]) for r in proxy if (r["mesh"], r["pose"]) in sl]
        for pk, sk, lab in (("support_volume_mm3", "support_filament_mm", "support"),
                            ("filament_m", "filament_mm", "total filament"),
                            ("time_min", "time_min", "time")):
            x = [float(p[pk]) for p, _ in pairs]; y = [float(s[sk]) for _, s in pairs]
            w(f"- {lab}: Spearman ρ = {spearman(x, y):.3f} (n = {len(x)})")
        by = defaultdict(list)
        for p, s in pairs:
            by[p["mesh"]].append((float(p["support_volume_mm3"]), float(s["support_filament_mm"])))
        conc = tot = 0
        for m, v in by.items():
            for i in range(len(v)):
                for j in range(i + 1, len(v)):
                    tot += 1
                    conc += (v[i][0] - v[j][0]) * (v[i][1] - v[j][1]) > 0
        if tot:
            w(f"- within-mesh pairwise agreement on support: {conc}/{tot}")
    (R / "report.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {R / 'report.md'}")


if __name__ == "__main__":
    main()
