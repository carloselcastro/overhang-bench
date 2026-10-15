#!/usr/bin/env python3
"""Objective landscape of Castro (2020), eq. (3.2.4), over the (t1, t2) rectangle.

    python scripts/plot_knight_landscape.py meshes/decimated-knight.off --out fig_knight_landscape

Evaluates the objective exactly as written (barycentric heights, `castro-eq`)
on a 1-degree grid, in the frame of the mesh file as distributed (or rotated
about x with --rotate-x), and writes
<out>.pdf and <out>.png (3D surface, global grid minimum marked).
Reads OFF and OBJ files; needs numpy and matplotlib.
"""
import argparse
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import cm


def load(path):
    if path.lower().endswith(".off"):
        L = [l.split() for l in open(path) if l.strip() and not l.startswith("#")]
        nv, nf = int(L[1][0]), int(L[1][1])
        V = np.array(L[2:2 + nv], float)
        F = np.array([r[1:4] for r in L[2 + nv:2 + nv + nf]], int)
        return V, F
    V, F = [], []
    for l in open(path, errors="ignore"):
        if l.startswith("v "):
            V.append(l.split()[1:4])
        elif l.startswith("f "):
            idx = [int(t.split("/")[0]) - 1 for t in l.split()[1:]]
            F += [[idx[0], idx[k], idx[k + 1]] for k in range(1, len(idx) - 1)]
    return np.array(V, float), np.array(F, int)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mesh")
    ap.add_argument("--out", default="fig_knight_landscape")
    ap.add_argument("--rotate-x", type=float, default=0.0,
                    help="rotate the mesh about x by this many degrees first "
                         "(90 gives the frame of the dissertation's figures for the Knight)")
    a = ap.parse_args()

    V, F = load(a.mesh)
    c, s_ = np.cos(np.radians(a.rotate_x)), np.sin(np.radians(a.rotate_x))
    V = V @ np.array([[1, 0, 0], [0, c, -s_], [0, s_, c]]).T
    p, q, r = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    cr = np.cross(q - p, r - p)
    A = 0.5 * np.linalg.norm(cr, axis=1)
    N = cr / (2 * A[:, None])
    B = (p + q + r) / 3

    def f(t1, t2):
        # build direction in the object frame: d = R(t1,t2)^T e3
        d = np.array([-np.sin(t2), np.sin(t1) * np.cos(t2), np.cos(t1) * np.cos(t2)])
        return np.sum((B @ d - (V @ d).min()) * A * (N @ d) ** 2)

    t1 = np.linspace(-np.pi, np.pi, 361)
    t2 = np.linspace(-np.pi / 2, np.pi / 2, 181)
    Z = np.array([[f(x, y) for x in t1] for y in t2])
    i = np.unravel_index(Z.argmin(), Z.shape)
    print(f"grid minimum at t1={t1[i[1]]:.4f}, t2={t2[i[0]]:.4f}, f={Z[i]:.6g}")

    plt.rcParams.update({"font.size": 17})
    fig = plt.figure(figsize=(6.2, 4.6))
    ax = fig.add_subplot(projection="3d")
    X, Y = np.meshgrid(t1, t2)
    ax.plot_surface(X, Y, Z, cmap=cm.OrRd, rstride=2, cstride=2, linewidth=0, antialiased=True, alpha=.95)
    ax.contour(X, Y, Z, levels=10, colors="k", linewidths=.6)
    ax.scatter([t1[i[1]]], [t2[i[0]]], [Z[i]], color="#1f4e9c", s=60, depthshade=False, zorder=10)
    ax.set_xlabel(r"$\theta_1$ (rad)", labelpad=10)
    ax.set_ylabel(r"$\theta_2$ (rad)", labelpad=10)
    ax.set_zlabel("Objective", labelpad=14)
    ax.set_xticks([-3, -1.5, 0, 1.5, 3]); ax.set_xticklabels(["-3", "-1.5", "0", "1.5", "3"])
    ax.set_yticks([-1.5, 0, 1.5]); ax.set_yticklabels(["-1.5", "0", "1.5"])
    zt = np.linspace(Z.min(), Z.max(), 3)
    ax.set_zticks(zt); ax.set_zticklabels([f"{z:.2g}" for z in zt]); ax.tick_params(axis="z", pad=6)
    ax.view_init(elev=24, azim=-62)
    ax.set_box_aspect((2, 1.1, 1))
    fig.subplots_adjust(left=0, right=0.93, bottom=0.02, top=1)
    fig.savefig(a.out + ".pdf", bbox_inches="tight")
    fig.savefig(a.out + ".png", dpi=110, bbox_inches="tight")


if __name__ == "__main__":
    main()
