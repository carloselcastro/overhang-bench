#!/usr/bin/env python3
"""Side-by-side renders of the pose of every method, one row per mesh.

    python scripts/compare_poses.py [--results results] [--out compare]
                                    [--poses initial,castro-eq,alexander,...]
                                    [--meshes cow,skull,...]

Writes to --out:
  <mesh>.png     the poses of one mesh, left to right in --poses order
  all_meshes.png every mesh, one row each (with --meshes, only those)

Each part is rendered by `viewer --figure` on the build plate (z up, seen from
the front), at the same scale within a row, so heights can be compared. Under
each render: the PrusaSlicer estimate of that pose from results/prusaslicer.csv
(support filament / printing time). The pose of our method is drawn in teal,
the others in grey.

For an interactive look at the same comparison, run
    viewer meshes/cow.off --poses results/all_poses.csv \
           --prusaslicer results/prusaslicer.csv --compare
"""
import argparse, csv, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_figures import ROOT, find_exe, render, crop_group  # noqa: E402

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OURS_RGB = "0.45,0.80,0.68"
OTHER_RGB = "0.75,0.75,0.78"
DEFAULT_POSES = ["initial", "castro-eq", "alexander", "ezair", "goguelin-len", "goguelin-vol",
                 "support-volume", "tweaker3-sur", "tweaker3-vol"]
LABELS = {"initial": "usual", "castro-eq": "ours", "alexander": "Alexander", "ezair": "Ezair",
          "goguelin-len": "Goguelin (len)", "goguelin-vol": "Goguelin (vol)",
          "support-volume": "support vol.", "tweaker3-sur": "Tweaker (sur)",
          "tweaker3-vol": "Tweaker (vol)", "castro-code": "castro-code"}


def mesh_file(name):
    for p in sorted((ROOT / "meshes").glob(name + ".*")):
        return p
    sys.exit(f"no mesh file for {name} in meshes/")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results", help="output of `pipeline.py run`")
    ap.add_argument("--out", default="compare")
    ap.add_argument("--poses", default=",".join(DEFAULT_POSES))
    ap.add_argument("--meshes", default="", help="comma-separated; default: every mesh in all_poses.csv")
    a = ap.parse_args()
    res, out = Path(a.results), Path(a.out)
    tmp = out / "_work"; tmp.mkdir(parents=True, exist_ok=True)
    viewer = find_exe("viewer")
    want = a.poses.split(",")

    rows = list(csv.DictReader(open(res / "all_poses.csv", encoding="utf-8")))
    meshes = a.meshes.split(",") if a.meshes else list(dict.fromkeys(r["mesh"] for r in rows))
    sl = {}
    if (res / "prusaslicer.csv").exists():
        sl = {(r["mesh"], r["pose"]): r for r in csv.DictReader(open(res / "prusaslicer.csv", encoding="utf-8"))
              if r.get("status") == "ok"}

    grid = []
    for m in meshes:
        poses = {r["pose"]: r for r in rows if r["mesh"] == m}
        names = [p for p in want if p in poses or p == "initial"]
        pc = tmp / f"{m}_poses.csv"
        with open(pc, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["mesh", "pose", "t1", "t2"])
            for p in names:
                if p != "initial":
                    w.writerow([m, p, poses[p]["t1"], poses[p]["t2"]])
        f = mesh_file(m)
        render(viewer, f, pc, OTHER_RGB, tmp / "grey")
        if "castro-eq" in names:
            render(viewer, f, pc, OURS_RGB, tmp / "ours")
        paths = [tmp / ("ours" if p == "castro-eq" else "grey") / f"{m}__{p}.png" for p in names]
        ims = crop_group(paths)
        caps = []
        for p in names:
            s = sl.get((m, p))
            caps.append(f"{float(s['support_filament_mm']) / 1000:.2f} m / {float(s['time_min']):.0f} min"
                        if s else "")
        grid.append((m, names, ims, caps))
        save([grid[-1]], out / f"{m}.png")
    save(grid, out / "all_meshes.png")
    print("wrote", out)


def save(grid, path):
    nc = max(len(g[1]) for g in grid)
    fig, axs = plt.subplots(len(grid), nc, figsize=(1.6 * nc, 1.9 * len(grid)), squeeze=False)
    for i, (m, names, ims, caps) in enumerate(grid):
        for j in range(nc):
            ax = axs[i][j]
            ax.set_xticks([]); ax.set_yticks([])
            for s in ax.spines.values():
                s.set_visible(False)
            if j >= len(names):
                continue
            ax.imshow(ims[j])
            ax.set_title(LABELS.get(names[j], names[j]), fontsize=9,
                         fontweight="bold" if names[j] == "castro-eq" else "normal")
            ax.set_xlabel(caps[j], fontsize=8)
            if j == 0:
                ax.set_ylabel(m, fontsize=10)
    fig.text(0.5, -0.01, "PrusaSlicer: support filament / printing time", ha="center", va="top", fontsize=8)
    fig.tight_layout(pad=0.4, w_pad=0.3, h_pad=0.6)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
