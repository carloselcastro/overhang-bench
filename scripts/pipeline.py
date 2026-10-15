#!/usr/bin/env python3
"""End-to-end pipeline of overhang-bench (works the same on Windows and Linux).

  python scripts/pipeline.py run   --out results       [--size-mm 60] [--overhang-deg 45]
  python scripts/pipeline.py sweep --base results --out results_sweep \
                                   [--sizes 40,60,100] [--angles 40,45,50]

Common options:
  --prusa  PATH   PrusaSlicer console executable (required for slicer numbers)
  --tweaker PATH  Tweaker-3's Tweaker.py (optional baseline)
  --orca   PATH   orca-slicer / bambu-studio executable (optional baseline)
  --bench  PATH   bench executable (auto-detected in build/)
  --jobs N        parallel slicer processes
  --meshes a,b    subset of the manifest (data/castro2020_meshes.csv)

`run` (one configuration):
  1. optimize every objective with its search strategies
       castro-code, castro-eq, alexander : grid, mcd-asrun, mcd, rcsp, sphere
       ezair, support-volume             : ezair (5-degree sampling + 100 DFO starts)
       goguelin-len, goguelin-vol        : sphere
  2. write the initial STLs and run the external baselines on them
  3. evaluate every pose (proxy, STL, all objectives), slice them, write report.md

`sweep` (sensitivity to part size and overhang angle): the optima of
castro-code, castro-eq and ezair do not depend on either (the objectives are
homogeneous in the scale and have no angle parameter), so they are taken from
--base. Alexander (lengths in cm, overhang angle), goguelin-len (critical angle)
and, with --reopt-support, the support-volume ablation are re-optimized for
every configuration; the
external baselines are re-run for every size. Every pose is then sliced with
the configuration's overhang threshold. Writes <out>/sweep_summary.{csv,md}.
"""
import argparse, csv, os, shutil, statistics, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable
SCR = ROOT / "scripts"


def sh(cmd, **kw):
    print("  $", " ".join(str(c) for c in cmd), flush=True)
    r = subprocess.run([str(c) for c in cmd], **kw)
    if r.returncode != 0:
        sys.exit(f"command failed ({r.returncode})")


def find_bench(explicit):
    if explicit:
        return Path(explicit)
    for c in ("build/bench", "build/bench.exe", "build/Release/bench.exe", "build-dev/bench"):
        if (ROOT / c).is_file():
            return ROOT / c
    sys.exit("bench executable not found; build it (cmake --build build) or pass --bench")


def manifest(subset):
    rows = list(csv.DictReader(open(ROOT / "data/castro2020_meshes.csv", encoding="utf-8")))
    out = []
    for r in rows:
        if subset and r["mesh"] not in subset:
            continue
        f = ROOT / "meshes" / r["file"]
        if not f.is_file():
            print(f"  (skipping {r['mesh']}: {f} not found)")
            continue
        out.append((r["mesh"], str(f) + (f"@{r['prerotation']}" if r["prerotation"] else "")))
    if not out:
        sys.exit("no meshes found; run scripts/fetch_meshes.py")
    return out


def write_poses(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["mesh", "pose", "t1", "t2"])
        w.writeheader()
        w.writerows(rows)


# The pose of the proposed method is the best minimizer of its two multistart
# strategies (M.C.D. with cell centres, R.C.S.P.), as described in the paper;
# grid, mcd-asrun and sphere are run only for comparison.
POSE_SEARCHES = {"castro-code": {"mcd", "rcsp"}, "castro-eq": {"mcd", "rcsp"}}


def best_poses(orient_csv, objectives=None):
    best = {}
    for r in csv.DictReader(open(orient_csv, encoding="utf-8")):
        if objectives and r["objective"] not in objectives:
            continue
        if r["search"] not in POSE_SEARCHES.get(r["objective"], {r["search"]}):
            continue
        k = (r["mesh"], r["objective"])
        if k not in best or float(r["fval"]) < float(best[k]["fval"]):
            best[k] = r
    return [{"mesh": m, "pose": o, "t1": r["t1"], "t2": r["t2"]} for (m, o), r in best.items()]


def external(stl_dir, out, a):
    rows = []
    if a.tweaker:
        f = out / "tweaker_poses.csv"
        sh([PY, SCR / "run_tweaker.py", stl_dir, f, "--tweaker", a.tweaker])
        rows += list(csv.DictReader(open(f, encoding="utf-8")))
    if a.orca:
        f = out / "orca_poses.csv"
        sh([PY, SCR / "run_orca.py", stl_dir, f, "--exe", a.orca])
        rows += list(csv.DictReader(open(f, encoding="utf-8")))
    return [{"mesh": r["mesh"], "pose": r["pose"], "t1": r["t1"], "t2": r["t2"]} for r in rows]


def evaluate(bench, out, meshes, poses, size, ang, a):
    """Proxy + STL + objective values for `poses`, then slicer and report."""
    for f in ("print_proxy.csv", "poses_eval.csv"):
        (out / f).unlink(missing_ok=True)
    shutil.rmtree(out / "stl", ignore_errors=True)
    write_poses(out / "all_poses.csv", poses)
    sh([bench, "--out", out, "--size-mm", size, "--overhang-deg", ang, "--searches", "none",
        "--poses", out / "all_poses.csv", *[m for _, m in meshes]])
    if a.prusa:
        extra = []
        if a.slicer_threads:
            extra += ["--threads", a.slicer_threads]
        if a.slicer_repeats > 1:
            extra += ["--repeats", a.slicer_repeats]
        sh([PY, SCR / "slice_prusaslicer.py", out / "stl", out / "prusaslicer.csv", "--exe", a.prusa,
            "--overhang-deg", ang, "--jobs", a.jobs, *extra])
    if (out / "orientations.csv").exists():
        sh([PY, SCR / "analyze.py", out])


def initial_stls(bench, out, meshes, size, ang):
    tmp = out / "_initial"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    write_poses(tmp / "p.csv", [{"mesh": n, "pose": "initial", "t1": 0, "t2": 0} for n, _ in meshes])
    sh([bench, "--out", tmp, "--size-mm", size, "--overhang-deg", ang, "--searches", "none",
        "--poses", tmp / "p.csv", *[m for _, m in meshes]])
    return tmp / "stl"


def cmd_run(a):
    bench = find_bench(a.bench)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    meshes = manifest(a.meshes)
    (out / "orientations.csv").unlink(missing_ok=True)
    groups = [("castro-code,castro-eq,alexander", "grid,mcd-asrun,mcd,rcsp,sphere"),
              ("ezair,support-volume", "ezair"),
              ("goguelin-len,goguelin-vol", "sphere")]
    for objs, searches in groups:
        sh([bench, "--out", out, "--size-mm", a.size_mm, "--overhang-deg", a.overhang_deg, "--no-stl",
            "--objectives", objs, "--searches", searches, *[m for _, m in meshes]])
    ext = external(initial_stls(bench, out, meshes, a.size_mm, a.overhang_deg), out, a)
    poses = []
    for n, _ in meshes:
        poses.append({"mesh": n, "pose": "initial", "t1": 0, "t2": 0})
        poses += [p for p in best_poses(out / "orientations.csv") if p["mesh"] == n]
        poses += [p for p in ext if p["mesh"] == n]
    evaluate(bench, out, meshes, poses, a.size_mm, a.overhang_deg, a)


def cmd_sweep(a):
    bench = find_bench(a.bench)
    base = Path(a.base)
    if not (base / "orientations.csv").exists():
        sys.exit(f"{base}/orientations.csv not found: run `pipeline.py run --out {base}` first")
    meshes = manifest(a.meshes)
    # size/angle-independent optima; the support-volume ablation depends on both,
    # so it enters the sweep only when re-optimized (--reopt-support)
    fixed = best_poses(base / "orientations.csv", {"castro-code", "castro-eq", "ezair"})
    # depend on the overhang angle (and alexander also on the size): re-optimized
    reopt = "alexander,goguelin-len" + (",support-volume" if a.reopt_support else "")
    sizes = [float(x) for x in a.sizes.split(",")]
    angles = [float(x) for x in a.angles.split(",")]
    root = Path(a.out); root.mkdir(parents=True, exist_ok=True)
    rows = []
    for size in sizes:
        ext = None
        for ang in angles:
            tag = f"size{size:g}_ang{ang:g}"
            out = root / tag; out.mkdir(parents=True, exist_ok=True)
            print(f"\n=== {tag} ===", flush=True)
            (out / "orientations.csv").unlink(missing_ok=True)
            sh([bench, "--out", out, "--size-mm", size, "--overhang-deg", ang, "--no-stl",
                "--objectives", reopt, "--searches", "sphere", "--sphere-n", a.sphere_n,
                *[m for _, m in meshes]])
            if ext is None:  # external baselines depend on the size only
                ext = external(initial_stls(bench, out, meshes, size, ang), out, a)
            poses = []
            for n, _ in meshes:
                poses.append({"mesh": n, "pose": "initial", "t1": 0, "t2": 0})
                poses += [p for p in fixed if p["mesh"] == n]
                poses += [p for p in best_poses(out / "orientations.csv") if p["mesh"] == n]
                poses += [p for p in ext if p["mesh"] == n]
            evaluate(bench, out, meshes, poses, size, ang, a)
            if (out / "prusaslicer.csv").exists():
                for r in csv.DictReader(open(out / "prusaslicer.csv", encoding="utf-8")):
                    if r["status"] == "ok":
                        rows.append({"size_mm": size, "overhang_deg": ang, **r})
    if not rows:
        print("no slicer results (pass --prusa); per-configuration proxies are in each folder")
        return
    with open(root / "sweep_summary.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    summarize(rows, root / "sweep_summary.md")


def summarize(rows, path):
    by = {}
    for r in rows:
        by.setdefault((r["size_mm"], r["overhang_deg"], r["mesh"]), {})[r["pose"]] = r
    methods = sorted({r["pose"] for r in rows} - {"initial"})
    out = ["# Sweep summary (PrusaSlicer estimates, not measurements)\n",
           "Median over meshes of the change relative to the initial pose (negative = less than the "
           "initial pose), and number of meshes where the method is the best of all poses "
           "(ties count for every tied method).\n"]
    for key, lab in (("support_filament_mm", "support filament"), ("time_min", "print time"),
                     ("filament_mm", "total filament")):
        out.append(f"\n## {lab}\n")
        out.append("| size (mm) | overhang (deg) | " + " | ".join(methods) + " |")
        out.append("|---|---|" + "---|" * len(methods))
        for size, ang in sorted({(k[0], k[1]) for k in by}):
            ms = [k[2] for k in by if k[0] == size and k[1] == ang]
            cells = []
            for m in methods:
                red, wins = [], 0
                for mesh in ms:
                    P = by[(size, ang, mesh)]
                    if m not in P or "initial" not in P:
                        continue
                    v0, v = float(P["initial"][key]), float(P[m][key])
                    if v0 > 0:
                        red.append(1 - v / v0)
                    best = min(float(p[key]) for p in P.values())
                    wins += abs(v - best) <= 1e-9 * max(1.0, best) or v <= best
                cells.append(f"{-100 * statistics.median(red):+.0f}% ({wins}/{len(ms)})" if red else "–")
            out.append(f"| {size:g} | {ang:g} | " + " | ".join(cells) + " |")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {path}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("run", "sweep"):
        p = sub.add_parser(name)
        p.add_argument("--out", required=True)
        p.add_argument("--bench"); p.add_argument("--prusa"); p.add_argument("--tweaker"); p.add_argument("--orca")
        p.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) // 2))
        p.add_argument("--meshes", type=lambda s: set(s.split(",")), default=None)
        p.add_argument("--slicer-threads", type=int, default=None,
                       help="PrusaSlicer --threads (1 = single-threaded, deterministic if the slicer is)")
        p.add_argument("--slicer-repeats", type=int, default=1,
                       help="slice every pose N times and report median and min/max")
    r = sub.choices["run"]
    r.add_argument("--size-mm", type=float, default=60.0)
    r.add_argument("--overhang-deg", type=float, default=45.0)
    s = sub.choices["sweep"]
    s.add_argument("--base", required=True, help="results folder of a previous `run`")
    s.add_argument("--sizes", default="40,60,100")
    s.add_argument("--angles", default="40,45,50")
    s.add_argument("--sphere-n", type=int, default=4000)
    s.add_argument("--reopt-support", action="store_true",
                   help="re-optimize the support-volume ablation per configuration (slow)")
    a = ap.parse_args()
    cmd_run(a) if a.cmd == "run" else cmd_sweep(a)


if __name__ == "__main__":
    main()
