#!/usr/bin/env python3
"""Collect every pose to be compared into one CSV for `bench --searches none --poses`:
the initial pose, the best pose of each objective in orientations.csv (lowest f
over all search strategies) and any external poses (e.g. Tweaker-3).

    python scripts/collect_poses.py results [--external results/external_poses.csv]
    -> results/all_poses.csv
"""
import argparse, csv
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("results")
ap.add_argument("--external", action="append", default=[])
a = ap.parse_args()
R = Path(a.results)
best = {}
meshes = []
for r in csv.DictReader(open(R / "orientations.csv", encoding="utf-8")):
    if r["mesh"] not in meshes:
        meshes.append(r["mesh"])
    k = (r["mesh"], r["objective"])
    if k not in best or float(r["fval"]) < float(best[k]["fval"]):
        best[k] = r
rows = []
for m in meshes:
    rows.append({"mesh": m, "pose": "initial", "t1": 0.0, "t2": 0.0})
    for (mm, o), r in best.items():
        if mm == m:
            rows.append({"mesh": m, "pose": o, "t1": r["t1"], "t2": r["t2"]})
    for ext in a.external:
        for r in csv.DictReader(open(ext, encoding="utf-8")):
            if r["mesh"] == m:
                rows.append({"mesh": m, "pose": r["pose"], "t1": r["t1"], "t2": r["t2"]})
with open(R / "all_poses.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["mesh", "pose", "t1", "t2"])
    w.writeheader(); w.writerows(rows)
print(f"wrote {R / 'all_poses.csv'} ({len(rows)} poses)")
