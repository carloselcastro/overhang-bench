#!/usr/bin/env python3
"""Run Tweaker-3 (Schranz; https://github.com/ChristophSchranz/Tweaker-3) as an
external orientation baseline on the *initial* STLs written by `bench`, and
convert its answer to the (t1,t2) parameterization of Castro (2020).

    python scripts/run_tweaker.py results/stl results/external_poses.csv \
        --tweaker path/to/Tweaker-3/Tweaker.py

Tweaker-3 reports "Tweaked Z-axis": the unit vector, in the input frame, that
becomes the build (up) direction. That is exactly d = R^T e3 of overhang-bench;
(t1,t2) = (atan2(dy,dz), asin(-dx)). The initial STL differs from the mesh
frame only by a uniform scale and a translation, so d carries over unchanged.

Two variants are run, matching Tweaker-3's own options:
  tweaker3-vol  -x -min vol   (extended mode, minimize support volume; default)
  tweaker3-sur  -x -min sur   (extended mode, minimize overhanging surface)
Output columns: mesh,pose,t1,t2,dx,dy,dz,seconds,unprintability
(the first four are what `bench --poses` reads).
"""
import argparse, csv, math, re, subprocess, sys, time
from pathlib import Path

AX_RE = re.compile(r"Tweaked Z-axis:\s*\[([^\]]+)\]")
UNP_RE = re.compile(r"Unprintability:\s*([-\d.eE+]+)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stl_dir")
    ap.add_argument("out_csv")
    ap.add_argument("--tweaker", required=True, help="path to Tweaker.py")
    ap.add_argument("--python", default=sys.executable)
    ap.add_argument("--repeats", type=int, default=5,
                    help="Tweaker-3's extended mode is stochastic: run it N times and keep the result "
                         "with the lowest unprintability (Tweaker's own criterion)")
    a = ap.parse_args()
    if not Path(a.tweaker).is_file():
        sys.exit(f"Tweaker.py not found: {a.tweaker}\n"
                 "Clone it first:  git clone https://github.com/ChristophSchranz/Tweaker-3.git ../Tweaker-3\n"
                 "and install its only dependency:  pip install \"numpy>=1.16\"")
    rows = []
    for stl in sorted(Path(a.stl_dir).glob("*__initial.stl")):
        mesh = stl.stem.split("__")[0]
        for label, mode in (("tweaker3-vol", "vol"), ("tweaker3-sur", "sur")):
            best, dt = None, 0.0
            for _ in range(max(1, a.repeats)):
                t0 = time.perf_counter()
                p = subprocess.run([a.python, a.tweaker, "-i", str(stl), "-x", "-r", "-min", mode],
                                   capture_output=True, text=True)
                dt += time.perf_counter() - t0
                m_ = AX_RE.search(p.stdout)
                u_ = UNP_RE.search(p.stdout)
                if m_ and (best is None or (u_ and float(u_.group(1)) < best[1])):
                    best = (m_, float(u_.group(1)) if u_ else float("inf"), p)
            if best is None:
                print(f"{mesh} {label}: FAILED\n{p.stdout[-500:]}\n{p.stderr[-500:]}", file=sys.stderr)
                continue
            m, _, p = best
            dt /= max(1, a.repeats)
            d = [float(x) for x in m.group(1).replace(",", " ").split()]
            n = math.sqrt(sum(x * x for x in d)); d = [x / n for x in d]
            t1 = math.atan2(d[1], d[2]); t2 = math.asin(max(-1.0, min(1.0, -d[0])))
            u = UNP_RE.search(p.stdout)
            rows.append({"mesh": mesh, "pose": label, "t1": t1, "t2": t2, "dx": d[0], "dy": d[1],
                         "dz": d[2], "seconds": dt, "unprintability": float(u.group(1)) if u else ""})
            print(f"{mesh:18s} {label}: d=({d[0]:+.4f},{d[1]:+.4f},{d[2]:+.4f})  "
                  f"t=({t1:+.4f},{t2:+.4f})  {dt:.2f}s")
    with open(a.out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["mesh", "pose", "t1", "t2", "dx", "dy", "dz", "seconds",
                                          "unprintability"])
        w.writeheader(); w.writerows(rows)


if __name__ == "__main__":
    main()
