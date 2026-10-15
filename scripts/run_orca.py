#!/usr/bin/env python3
"""OrcaSlicer's (or Bambu Studio's) auto-orientation as an external baseline.

    python scripts/run_orca.py results/stl results/orca_poses.csv \
        --exe "C:\\Program Files\\OrcaSlicer\\orca-slicer.exe"

For every *__initial.stl, runs the slicer's CLI with `--orient 1` and exports
the oriented model as STL. The rotation is recovered by matching triangles
between input and output through rigid invariants (sorted edge lengths) and
solving the orthogonal Procrustes problem (Kabsch 1976, Acta Cryst. A32:922)
on the matched barycentres; d = R^T e3 is the object-frame direction that the
slicer put up, converted to (t1, t2) as in run_tweaker.py. The residual of the
fit is reported so a wrong match cannot pass silently.

OrcaSlicer documents its criterion as a weighted cost of overhang area, bottom
contact area, bottom convex-hull area, contour complexity and low-angle face
area (OrcaSlicer wiki, "Auto Orientation").

NOT tested in the environment where this script was written (the slicer was
not installable there): check the residual column and look at one result in
the viewer before trusting the numbers. CLI flags differ between releases; if
yours rejects `--export-stl`, try `--export-3mf` and open the 3MF manually.
"""
import argparse, csv, math, struct, subprocess, sys, tempfile
from pathlib import Path

import numpy as np


def read_stl(path):
    b = Path(path).read_bytes()
    if b[:5] == b"solid" and b"facet" in b[:400]:  # ASCII STL
        vs = [list(map(float, l.split()[1:4])) for l in b.decode(errors="ignore").splitlines()
              if l.strip().startswith("vertex")]
        return np.array(vs, dtype=float).reshape(-1, 3, 3)
    n = struct.unpack("<I", b[80:84])[0]
    a = np.frombuffer(b[84:84 + 50 * n], dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)),
                                                          ("a", "<u2")]))
    return a["v"].astype(float)


def signature(T, scale):
    e = np.stack([np.linalg.norm(T[:, 1] - T[:, 0], axis=1), np.linalg.norm(T[:, 2] - T[:, 1], axis=1),
                  np.linalg.norm(T[:, 0] - T[:, 2], axis=1)], axis=1)
    return np.round(np.sort(e, axis=1) / scale, 4)


def recover_rotation(A, B):
    """A, B: (n,3,3) triangles before/after. Returns R (B ~ R A + t) and RMS residual."""
    scale = np.ptp(A.reshape(-1, 3), axis=0).max()
    sa, sb = signature(A, scale), signature(B, scale)
    ka = {}
    for i, s in enumerate(map(tuple, sa)):
        ka.setdefault(s, []).append(i)
    kb = {}
    for i, s in enumerate(map(tuple, sb)):
        kb.setdefault(s, []).append(i)
    pairs = [(ka[s][0], kb[s][0]) for s in ka if len(ka[s]) == 1 and len(kb.get(s, [])) == 1]
    if len(pairs) < 3:
        raise RuntimeError("not enough uniquely matched triangles")
    ia, ib = map(np.array, zip(*pairs))
    P, Q = A[ia].mean(axis=1), B[ib].mean(axis=1)
    Pc, Qc = P - P.mean(0), Q - Q.mean(0)
    U, _, Vt = np.linalg.svd(Pc.T @ Qc)
    D = np.diag([1, 1, np.sign(np.linalg.det(Vt.T @ U.T))])
    R = Vt.T @ D @ U.T
    res = np.sqrt(np.mean(np.sum((Pc @ R.T - Qc) ** 2, axis=1))) / scale
    return R, res, len(pairs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stl_dir")
    ap.add_argument("out_csv")
    ap.add_argument("--exe", required=True, help="orca-slicer(.exe) or bambu-studio(.exe)")
    ap.add_argument("--label", default="orca-orient")
    a = ap.parse_args()
    if not Path(a.exe).is_file():
        sys.exit(f"slicer not found: {a.exe}")
    rows = []
    tmp = Path(tempfile.mkdtemp())
    for stl in sorted(Path(a.stl_dir).glob("*__initial.stl")):
        mesh = stl.stem.split("__")[0]
        out = tmp / mesh
        out.mkdir(exist_ok=True)
        cmd = [a.exe, "--orient", "1", "--export-stl", "--outputdir", str(out), str(stl)]
        p = subprocess.run(cmd, capture_output=True, text=True)
        outs = sorted(out.glob("*.stl"))
        if not outs:
            print(f"{mesh}: FAILED ({p.returncode})\n{(p.stdout + p.stderr)[-800:]}", file=sys.stderr)
            continue
        try:
            R, res, npairs = recover_rotation(read_stl(stl), read_stl(outs[0]))
        except RuntimeError as e:
            print(f"{mesh}: rotation recovery failed: {e}", file=sys.stderr)
            continue
        d = R.T @ np.array([0.0, 0.0, 1.0])
        t1 = math.atan2(d[1], d[2]); t2 = math.asin(max(-1.0, min(1.0, -d[0])))
        rows.append({"mesh": mesh, "pose": a.label, "t1": t1, "t2": t2, "dx": d[0], "dy": d[1], "dz": d[2],
                     "fit_residual": res, "matched_triangles": npairs})
        flag = "" if res < 1e-3 else "   <-- LARGE RESIDUAL, check this one"
        print(f"{mesh:18s} d=({d[0]:+.4f},{d[1]:+.4f},{d[2]:+.4f})  t=({t1:+.4f},{t2:+.4f})  "
              f"residual={res:.1e} ({npairs} tris){flag}")
    with open(a.out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["mesh", "pose", "t1", "t2", "dx", "dy", "dz", "fit_residual",
                                          "matched_triangles"])
        w.writeheader(); w.writerows(rows)


if __name__ == "__main__":
    main()
