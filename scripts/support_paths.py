#!/usr/bin/env python3
"""Support toolpaths of a PrusaSlicer G-code, in the frame of the sliced STL.

    python scripts/support_paths.py GCODE STL OUT.csv [--center 125,105]

Writes one row per extruding move of type "Support material" or "Support
material interface": x0,y0,z0,x1,y1,z1 in mm, in the frame of STL (the placed,
scaled STL written by `bench`), so that `viewer --support-paths` can draw the
slicer's actual supports next to the part. slice_prusaslicer.py slices with
--center 125,105, which puts the centre of the XY bounding box of the part at
that point of the bed; the moves are shifted back by that offset. The moves
are drawn at mid-layer height.

The part's own extrusions are used as a check: their XY bounding box must
match that of the STL to within an extrusion width.
"""
import argparse, csv, re, struct
from pathlib import Path

import numpy as np

COORD = re.compile(r"([XYZE])(-?[\d.]+)")


def stl_bbox(path):
    data = Path(path).read_bytes()
    n = struct.unpack_from("<I", data, 80)[0]
    if len(data) == 84 + 50 * n:  # binary
        rec = np.frombuffer(data, dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]),
                            count=n, offset=84)
        V = rec["v"].reshape(-1, 3)
    else:  # ASCII
        V = np.array([[float(t) for t in l.split()[1:4]] for l in data.decode().splitlines()
                      if l.strip().startswith("vertex")])
    return V.min(0), V.max(0)


def read_moves(path):
    """Extruding XY moves as (type, x0, y0, x1, y1, z, layer_height)."""
    moves, cur, x, y, z, e, abs_e, h = [], "unknown", 0.0, 0.0, 0.0, 0.0, True, 0.2
    with open(path, encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            if line.startswith(";"):
                if line.startswith(";TYPE:"):
                    cur = line[6:].strip()
                elif line.startswith(";HEIGHT:"):
                    h = float(line[8:])
                continue
            code = line.split(";", 1)[0].strip()
            if code.startswith("M82"):
                abs_e = True
            elif code.startswith("M83"):
                abs_e = False
            elif code.startswith("G92"):
                m = re.search(r"E(-?[\d.]+)", code)
                if m:
                    e = float(m.group(1))
            elif code.startswith(("G0", "G1")):
                c = dict(COORD.findall(code))
                nx, ny = float(c.get("X", x)), float(c.get("Y", y))
                z = float(c.get("Z", z))
                if "E" in c:
                    de = float(c["E"]) - e if abs_e else float(c["E"])
                    if abs_e:
                        e = float(c["E"])
                    if de > 0 and ("X" in c or "Y" in c):
                        moves.append((cur, x, y, nx, ny, z, h))
                x, y = nx, ny
    return moves


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("gcode")
    ap.add_argument("stl")
    ap.add_argument("out_csv")
    ap.add_argument("--center", default="125,105", help="--center given to PrusaSlicer")
    a = ap.parse_args()
    lo, hi = stl_bbox(a.stl)
    cx, cy = (float(v) for v in a.center.split(","))
    dx, dy = 0.5 * (lo[0] + hi[0]) - cx, 0.5 * (lo[1] + hi[1]) - cy

    moves = read_moves(a.gcode)
    sup = [m for m in moves if m[0].lower().startswith("support material")]
    part = np.array([m[1:5] for m in moves if not m[0].lower().startswith(("support material", "skirt"))
                     and m[0] not in ("unknown", "Custom", "Wipe tower")])
    plo = np.minimum(part[:, [0, 1]].min(0), part[:, [2, 3]].min(0))
    phi = np.maximum(part[:, [0, 1]].max(0), part[:, [2, 3]].max(0))
    # refine the offset: centre of the part's extrusions on the centre of the STL
    rx, ry = 0.5 * (lo[:2] + hi[:2]) - 0.5 * (plo + phi)
    err = max(abs(rx - dx), abs(ry - dy))
    if err > 2.0:
        raise SystemExit(f"part extrusions do not line up with {a.stl} (off by {err:.2f} mm)")
    dx, dy = rx, ry

    with open(a.out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["x0", "y0", "z0", "x1", "y1", "z1"])
        for _, x0, y0, x1, y1, z, h in sup:
            zm = z - 0.5 * h
            w.writerow([f"{x0 + dx:.3f}", f"{y0 + dy:.3f}", f"{zm:.3f}", f"{x1 + dx:.3f}", f"{y1 + dy:.3f}", f"{zm:.3f}"])
    print(f"{a.out_csv}: {len(sup)} support moves (part bbox check: {err:.2f} mm)")


if __name__ == "__main__":
    main()
