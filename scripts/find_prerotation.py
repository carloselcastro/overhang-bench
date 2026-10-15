#!/usr/bin/env python3
"""Find the pre-rotation that puts a mesh in the frame used by Castro (2020).

    python scripts/find_prerotation.py meshes/heart.obj --t1 -2.6011 --t2 0.0370

Tries the 24 axis-aligned rotations (the rotation group of the cube), optimizes
`castro-eq` in each frame (bench, S^2 search) and reports the angular
distance between the optimum found and the (t1, t2) of Table 4.2.1. The frame
with a near-zero distance is the dissertation's; put its spec in the
`prerotation` column of data/castro2020_meshes.csv.
"""
import argparse, csv, itertools, math, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def rot(axis, deg):
    c, s = round(math.cos(math.radians(deg))), round(math.sin(math.radians(deg)))
    if axis == "x":
        return ((1, 0, 0), (0, c, -s), (0, s, c))
    if axis == "y":
        return ((c, 0, s), (0, 1, 0), (-s, 0, c))
    return ((c, -s, 0), (s, c, 0), (0, 0, 1))


def mul(A, B):
    return tuple(tuple(sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)) for i in range(3))


def cube_group():
    seen = {}
    for ax, ay, az in itertools.product((0, 90, 180, 270), repeat=3):
        Q = mul(rot("z", az), mul(rot("y", ay), rot("x", ax)))  # x first, then y, then z
        if Q not in seen:
            spec = ",".join(f"r{a}{d}" for a, d in (("x", ax), ("y", ay), ("z", az)) if d)
            seen[Q] = spec
    return list(seen.values())


def d_of(t1, t2):
    return (-math.sin(t2), math.sin(t1) * math.cos(t2), math.cos(t1) * math.cos(t2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mesh")
    ap.add_argument("--t1", type=float, required=True)
    ap.add_argument("--t2", type=float, required=True)
    ap.add_argument("--bench", default=None)
    a = ap.parse_args()
    bench = a.bench
    if not bench:
        for c in ("build/bench", "build/bench.exe", "build/Release/bench.exe", "build-dev/bench"):
            if (ROOT / c).is_file():
                bench = str(ROOT / c); break
    if not bench:
        sys.exit("bench not found; pass --bench")
    ref = d_of(a.t1, a.t2)
    specs = cube_group()
    tmp = Path(tempfile.mkdtemp())
    res = []
    for spec in specs:
        out = tmp / (spec or "identity")
        arg = a.mesh + (f"@{spec}" if spec else "")
        subprocess.run([bench, "--out", str(out), "--no-stl", "--objectives", "castro-eq",
                        "--searches", "sphere,mcd", arg], capture_output=True)
        rows = list(csv.DictReader(open(out / "orientations.csv", encoding="utf-8")))
        r = min(rows, key=lambda r: float(r["fval"]))
        d = d_of(float(r["t1"]), float(r["t2"]))
        ang = math.degrees(math.acos(max(-1, min(1, sum(x * y for x, y in zip(d, ref))))))
        res.append((ang, spec or "(none)", float(r["t1"]), float(r["t2"])))
    res.sort()
    print(f"{'angle to table':>15s}  {'pre-rotation':14s}  optimum found (t1, t2)")
    for ang, spec, t1, t2 in res[:6]:
        print(f"{ang:13.2f}°  {spec:14s}  ({t1:+.4f}, {t2:+.4f})")
    print(f"\nbest: '{res[0][1]}'  ({res[0][0]:.2f}° from Table 4.2.1)")


if __name__ == "__main__":
    main()
