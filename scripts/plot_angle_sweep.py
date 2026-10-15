#!/usr/bin/env python3
"""Figure: effect of the support (overhang) angle on each method.

    python scripts/plot_angle_sweep.py results_angles/sweep_summary.csv --size 60 \
        --out fig_angle_sweep            # writes fig_angle_sweep.pdf and .png

For every overhang angle, the median over meshes of the change relative to the
initial pose (PrusaSlicer estimates) in support filament and in print time, one
line per method. Two panels share the x axis (two measures, two axes; never a
dual y-axis). Series are told apart by colour, marker and line style, so the
figure survives greyscale printing and colour-vision deficiencies. Every
number plotted comes from sweep_summary.csv; nothing is interpolated or
smoothed. The per-angle numbers are also printed as a table (stdout).
"""
import argparse, csv, statistics
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# categorical slots in fixed order (validated: adjacent CVD dE >= 9.1, normal-vision >= 19.6)
STYLE = {
    "castro-eq":    ("Ours",                    "#2a78d6", "o", "-"),
    "ezair":        ("Ezair et al. (2015)",     "#eb6834", "s", "--"),
    "goguelin-len": ("Goguelin et al. (2021)",  "#1baf7a", "^", "-."),
    "alexander":    ("Alexander et al. (1998)", "#eda100", "D", ":"),
    "tweaker3-sur": ("Tweaker-3 (surface)",     "#e87ba4", "v", (0, (5, 1, 1, 1))),
    "tweaker3-vol": ("Tweaker-3 (volume)",      "#e87ba4", "v", (0, (5, 1, 1, 1))),
}
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--size", type=float, default=None, help="part size to plot (default: the only one)")
    ap.add_argument("--methods", default="castro-eq,ezair,goguelin-len,alexander,tweaker3-sur")
    ap.add_argument("--out", default="fig_angle_sweep")
    a = ap.parse_args()
    rows = [r for r in csv.DictReader(open(a.csv, encoding="utf-8")) if r.get("status", "ok") == "ok"]
    sizes = sorted({float(r["size_mm"]) for r in rows})
    size = a.size if a.size is not None else sizes[0]
    if a.size is None and len(sizes) > 1:
        print(f"several sizes {sizes}; plotting {size} (use --size)")
    rows = [r for r in rows if float(r["size_mm"]) == size]
    by = defaultdict(dict)
    for r in rows:
        by[(float(r["overhang_deg"]), r["mesh"])][r["pose"]] = r
    angles = sorted({k[0] for k in by})
    methods = [m for m in a.methods.split(",") if any(m in P for P in by.values())]

    med = {}
    print("angle  " + "  ".join(f"{m:>22s}" for m in methods) + "   (median % change: support / time; n meshes)")
    for ang in angles:
        line = f"{ang:5g}  "
        for m in methods:
            sup, tim = [], []
            for (g, mesh), P in by.items():
                if g != ang or m not in P or "initial" not in P:
                    continue
                s0, t0 = float(P["initial"]["support_filament_mm"]), float(P["initial"]["time_min"])
                if s0 > 0:
                    sup.append(100 * (float(P[m]["support_filament_mm"]) / s0 - 1))
                tim.append(100 * (float(P[m]["time_min"]) / t0 - 1))
            med[(ang, m)] = (statistics.median(sup) if sup else float("nan"),
                             statistics.median(tim) if tim else float("nan"), len(tim))
            line += f"{med[(ang, m)][0]:+9.1f} / {med[(ang, m)][1]:+6.1f} (n={len(tim)})"
        print(line)

    plt.rcParams.update({"font.size": 12, "axes.labelsize": 13, "legend.fontsize": 11,
                         "xtick.labelsize": 11, "ytick.labelsize": 11, "axes.edgecolor": INK2,
                         "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
                         "pdf.fonttype": 42})
    fig, axs = plt.subplots(1, 2, figsize=(10, 4.2), sharex=True)
    for ax, k, lab in ((axs[0], 0, "Support filament: median change (%)"),
                       (axs[1], 1, "Print time: median change (%)")):
        ax.axhline(0, color=INK2, lw=1)
        for m in methods:
            name, col, mk, ls = STYLE.get(m, (m, "#52514e", "o", "-"))
            ys = [med[(g, m)][k] for g in angles]
            # "Ours" on top (drawn last in z) so coincident lines stay visible:
            # a baseline that ties with it shows as its dashes over a solid line
            top = m == "castro-eq"
            ax.plot(angles, ys, color=col, marker=mk, ms=9 if top else 7, lw=2.5 if top else 2,
                    ls=ls, label=name, markeredgecolor="white", markeredgewidth=1,
                    zorder=3 if top else 4, alpha=1.0)
        ax.set_ylabel(lab)
        ax.set_xlabel("Overhang angle from the vertical (deg)")
        ax.set_xticks(angles)
        ax.grid(axis="y", color=GRID, lw=0.8)
        ax.spines[["top", "right"]].set_visible(False)
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=min(5, len(methods)), frameon=False,
               bbox_to_anchor=(0.5, 1.02), handlelength=3)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    for ext in ("pdf", "png"):
        fig.savefig(f"{a.out}.{ext}", dpi=200, bbox_inches="tight")
    print(f"wrote {a.out}.pdf/.png  (size {size:g} mm, PrusaSlicer estimates relative to the initial pose)")


if __name__ == "__main__":
    main()
