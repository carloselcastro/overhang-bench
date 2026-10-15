#!/usr/bin/env python3
"""Figures 6-10 of the paper (Knight landscape, local minima, multistart, renders).

    python scripts/make_figures.py --out figures --prusa PATH [--results results]

Writes to --out:
  knight_landscape.pdf   objective landscape of eq. (5) on the Knight (Fig. 6)
  knight_minima.pdf      the optimum and a poor local minimum, rendered (Fig. 7)
  multistart_mcd.pdf     M.C.D. starting points and where they converge (Fig. 8)
  multistart_rcsp.pdf    R.C.S.P. starting points and where they converge (Fig. 9)
  surfaces_opt.pdf       usual orientation vs. ours for four meshes (Fig. 10)
  knight_minima.csv      PrusaSlicer estimates of the two poses of Fig. 7

Everything is computed here with the code of the repository: the local runs
come from `bench --local-minima` (the same L-BFGS-B multistarts as Table 1),
the renders from `viewer --figure`, and the slicer numbers from
slice_prusaslicer.py with the reference profile, single-threaded. All Knight
figures use the frame of the file as distributed.

The "poor local minimum" of Fig. 7 is chosen by a fixed rule: among the local
minima reached by the multistarts whose objective is at least twice the
optimum, the one reached from the most starting points.
"""
import argparse, csv, math, subprocess, sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable
SCR = ROOT / "scripts"
sys.path.insert(0, str(SCR))
from plot_knight_landscape import load  # noqa: E402

KNIGHT = ROOT / "meshes" / "decimated-knight.off"
OURS_RGB = "0.45,0.80,0.68"    # teal: our orientation
OTHER_RGB = "0.93,0.62,0.62"   # pink: usual orientation / poor local minimum
H = math.pi / 4                # M.C.D. cell size


def sh(cmd):
    print("  $", " ".join(str(c) for c in cmd), flush=True)
    subprocess.run([str(c) for c in cmd], check=True)


def find_exe(name):
    for p in (ROOT / "build" / f"{name}.exe", ROOT / "build" / name,
              ROOT / "build" / "Release" / f"{name}.exe"):
        if p.exists():
            return p
    sys.exit(f"{name} not found in build/: build the project first")


def direction(t1, t2):
    return np.array([-np.sin(t2), np.sin(t1) * np.cos(t2), np.cos(t1) * np.cos(t2)])


def landscape(mesh, n1=361, n2=181):
    """Eq. (5) on a regular (t1, t2) grid, vectorized in chunks."""
    V, F = load(str(mesh))
    p, q, r = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    cr = np.cross(q - p, r - p)
    A = 0.5 * np.linalg.norm(cr, axis=1)
    N = cr / (2 * A[:, None])
    B = (p + q + r) / 3
    t1 = np.linspace(-np.pi, np.pi, n1)
    t2 = np.linspace(-np.pi / 2, np.pi / 2, n2)
    T1, T2 = np.meshgrid(t1, t2)
    D = direction(T1.ravel(), T2.ravel()).T             # (n, 3)
    Z = np.empty(len(D))
    for k in range(0, len(D), 4000):
        d = D[k:k + 4000].T
        h = B @ d - (V @ d).min(axis=0)
        Z[k:k + 4000] = (A[:, None] * h * (N @ d) ** 2).sum(axis=0)
    return t1, t2, Z.reshape(T1.shape)


def read_runs(path, mesh="decimated-knight"):
    return [r for r in csv.DictReader(open(path, encoding="utf-8")) if r["mesh"] == mesh]


def cluster(runs, tol_deg=2.0):
    """Group local runs whose end points give build directions within tol_deg."""
    cl = []
    for r in runs:
        t = (float(r["t1"]), float(r["t2"]))
        d = direction(*t)
        for c in cl:
            if d @ c["d"] > math.cos(math.radians(tol_deg)):
                c["n"] += 1
                if float(r["fval"]) < c["f"]:  # keep the best end point of the group
                    c.update(t=t, f=float(r["fval"]))
                break
        else:
            cl.append({"t": t, "d": d, "f": float(r["fval"]), "n": 1})
    return sorted(cl, key=lambda c: c["f"])


def plot_multistart(t1, t2, Z, runs, search, best, out, grid):
    plt.rcParams.update({"font.size": 12, "pdf.fonttype": 42})
    fig, ax = plt.subplots(figsize=(4.6, 3.1))
    ax.contourf(t1, t2, Z, levels=14, cmap="OrRd", alpha=0.75)
    ax.contour(t1, t2, Z, levels=14, colors="k", linewidths=0.4, alpha=0.6)
    if grid:
        for x in np.arange(-np.pi, np.pi + 1e-9, H):
            ax.axvline(x, color="#52514e", lw=0.8)
        for y in np.arange(-np.pi / 2, np.pi / 2 + 1e-9, H):
            ax.axhline(y, color="#52514e", lw=0.8)
    R = [r for r in runs if r["search"] == search]
    for r in R:
        x0, y0, x1, y1 = (float(r[k]) for k in ("start_t1", "start_t2", "t1", "t2"))
        if abs(x1 - x0) < np.pi:  # do not draw paths that wrap around theta_1 = +-pi
            ax.plot([x0, x1], [y0, y1], color="#1f4e9c", lw=0.8, alpha=0.7)
    ax.scatter([float(r["start_t1"]) for r in R], [float(r["start_t2"]) for r in R],
               s=14, color="k", zorder=5, label=f"starts ({len(R)})")
    ax.scatter([float(r["t1"]) for r in R], [float(r["t2"]) for r in R], s=26, facecolor="white",
               edgecolor="#1f4e9c", lw=1.2, zorder=6, label="minima reached")
    ax.scatter([best[0]], [best[1]], marker="*", s=200, color="#1f4e9c", edgecolor="white",
               zorder=7, label=r"$(\theta_1^*,\theta_2^*)$")
    ax.set_xlim(-np.pi, np.pi); ax.set_ylim(-np.pi / 2, np.pi / 2)
    ax.set_xticks([-np.pi, -np.pi / 2, 0, np.pi / 2, np.pi])
    ax.set_xticklabels([r"$-\pi$", r"$-\pi/2$", "0", r"$\pi/2$", r"$\pi$"])
    ax.set_yticks([-np.pi / 2, 0, np.pi / 2])
    ax.set_yticklabels([r"$-\pi/2$", "0", r"$\pi/2$"])
    ax.set_xlabel(r"$\theta_1$ (rad)"); ax.set_ylabel(r"$\theta_2$ (rad)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.24), ncol=3, frameon=False, fontsize=11,
              handletextpad=0.2, columnspacing=0.8)
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)


def render(viewer, mesh, poses_csv, rgb, outdir):
    outdir.mkdir(parents=True, exist_ok=True)
    sh([viewer, mesh, "--poses", poses_csv, "--figure", "--color", rgb, "--screenshots", outdir])


def crop_group(paths):
    """Crop images to the union of their visible (alpha > 0) boxes, keeping one scale."""
    ims = [mpimg.imread(p) for p in paths]
    box = None
    for im in ims:
        ys, xs = np.nonzero(im[..., 3] > 0.02)
        b = (ys.min(), ys.max(), xs.min(), xs.max())
        box = b if box is None else (min(box[0], b[0]), max(box[1], b[1]),
                                     min(box[2], b[2]), max(box[3], b[3]))
    pad = 10
    y0, y1, x0, x1 = box[0] - pad, box[1] + pad, box[2] - pad, box[3] + pad
    return [im[max(0, y0):y1, max(0, x0):x1] for im in ims]


def compose(grid, out, row_labels=None, col_labels=None, width=7.2, fontsize=11):
    nr, nc = len(grid), len(grid[0])
    h = sum(max(im.shape[0] / im.shape[1] for im in row) for row in grid) * width / nc
    fig, axs = plt.subplots(nr, nc, figsize=(width, h + 0.3 * (col_labels is not None)), squeeze=False)
    for i, row in enumerate(grid):
        for j, im in enumerate(row):
            ax = axs[i][j]
            ax.imshow(im); ax.set_xticks([]); ax.set_yticks([])
            for s in ax.spines.values():
                s.set_visible(False)
            if row_labels and j == 0:
                ax.set_ylabel(row_labels[i], fontsize=fontsize)
            if col_labels and i == 0:
                ax.set_title(col_labels[j], fontsize=fontsize)
    fig.tight_layout(pad=0.3, w_pad=0.2, h_pad=0.2)
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="figures")
    ap.add_argument("--results", default="results", help="output of `pipeline.py run`")
    ap.add_argument("--prusa", required=True, help="PrusaSlicer console executable")
    ap.add_argument("--overhang-deg", type=float, default=45.0)
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    tmp = out / "_work"; tmp.mkdir(exist_ok=True)
    bench, viewer = find_exe("bench"), find_exe("viewer")

    # Fig. 6
    sh([PY, SCR / "plot_knight_landscape.py", KNIGHT, "--out", out / "knight_landscape"])

    # local runs of the two multistarts (Table 1 searches)
    lm = tmp / "local_minima.csv"
    lm.unlink(missing_ok=True); (tmp / "orientations.csv").unlink(missing_ok=True)
    for f in ("print_proxy.csv", "poses_eval.csv"):
        (tmp / f).unlink(missing_ok=True)
    sh([bench, "--out", tmp, "--no-stl", "--objectives", "castro-eq", "--searches", "mcd,rcsp",
        "--local-minima", KNIGHT])
    runs = read_runs(lm)
    cl = cluster(runs)
    best = cl[0]
    poor = max((c for c in cl if c["f"] >= 2 * best["f"]), key=lambda c: (c["n"], -c["f"]))
    print(f"optimum ({best['t'][0]:.4f}, {best['t'][1]:.4f}) f={best['f']:.5g}; "
          f"poor local minimum ({poor['t'][0]:.4f}, {poor['t'][1]:.4f}) f={poor['f']:.5g}, "
          f"reached from {poor['n']} starts")

    # Figs. 8-9
    t1, t2, Z = landscape(KNIGHT)
    plot_multistart(t1, t2, Z, runs, "mcd", best["t"], out / "multistart_mcd.pdf", grid=True)
    plot_multistart(t1, t2, Z, runs, "rcsp", best["t"], out / "multistart_rcsp.pdf", grid=False)

    # Fig. 7: slice and render the optimum and the poor local minimum
    k7 = tmp / "knight"; k7.mkdir(exist_ok=True)
    for f in ("print_proxy.csv", "poses_eval.csv"):
        (k7 / f).unlink(missing_ok=True)
    pc = tmp / "knight_poses.csv"
    with open(pc, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["mesh", "pose", "t1", "t2"])
        w.writerow(["decimated-knight", "optimum", *best["t"]])
        w.writerow(["decimated-knight", "local-minimum", *poor["t"]])
    sh([bench, "--out", k7, "--searches", "none", "--poses", pc, "--overhang-deg", a.overhang_deg, KNIGHT])
    sh([PY, SCR / "slice_prusaslicer.py", k7 / "stl", out / "knight_minima.csv", "--exe", a.prusa,
        "--overhang-deg", a.overhang_deg, "--threads", "1", "--jobs", "2"])
    render(viewer, KNIGHT, pc, OURS_RGB, tmp / "r_ours")
    render(viewer, KNIGHT, pc, OTHER_RGB, tmp / "r_other")
    ims = crop_group([tmp / "r_ours" / "decimated-knight__optimum.png",
                      tmp / "r_other" / "decimated-knight__local-minimum.png"])
    compose([ims], out / "knight_minima.pdf", col_labels=["(a)", "(b)"], width=3.6, fontsize=10)

    # Fig. 10: usual orientation (top) and ours (bottom)
    poses = [r for r in csv.DictReader(open(Path(a.results) / "all_poses.csv", encoding="utf-8"))
             if r["pose"] == "castro-eq"]
    pe = tmp / "ours_poses.csv"
    with open(pe, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["mesh", "pose", "t1", "t2"])
        for r in poses:
            w.writerow([r["mesh"], "ours", r["t1"], r["t2"]])
    cols = [("decimated-knight", "decimated-knight.off"), ("horse_quad", "horse_quad.obj"),
            ("bunny", "bunny.off"), ("arm", "arm.obj")]
    top, bottom = [], []
    for name, file in cols:
        render(viewer, ROOT / "meshes" / file, pe, OTHER_RGB, tmp / "r10_other")
        render(viewer, ROOT / "meshes" / file, pe, OURS_RGB, tmp / "r10_ours")
        u, o = crop_group([tmp / "r10_other" / f"{name}__initial.png", tmp / "r10_ours" / f"{name}__ours.png"])
        top.append(u); bottom.append(o)
    compose([top, bottom], out / "surfaces_opt.pdf", row_labels=["Usual orientation", "Ours"])
    print("wrote", ", ".join(str(out / f) for f in ("knight_landscape.pdf", "knight_minima.pdf",
          "multistart_mcd.pdf", "multistart_rcsp.pdf", "surfaces_opt.pdf", "knight_minima.csv")))


if __name__ == "__main__":
    main()
