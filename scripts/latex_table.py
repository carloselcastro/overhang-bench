#!/usr/bin/env python3
"""LaTeX table (booktabs) of PrusaSlicer estimates per mesh and method.

    python scripts/latex_table.py results > table_results.tex
    python scripts/latex_table.py results --methods castro-eq,ezair,goguelin-len,alexander,tweaker3-sur

Rows: meshes; columns: the initial pose and each method; two blocks (support
filament in m, print time in min). The best value among the methods (not the
initial pose) is bold; ties are all bold. The slicer version is read from
prusaslicer.csv and written in the caption.
"""
import argparse, csv
from pathlib import Path

NAMES = {"arm": "Arm", "bunny": "Bunny", "camel_b": "Camel", "cow": "Cow", "horse_quad": "Horse",
         "decimated-knight": "Knight", "decimated-max": "Max", "heart": "Heart", "skull": "Skull"}
HEAD = {"initial": ("Initial", ""), "castro-eq": ("Ours", ""), "castro-code": ("Ours", "(code)"),
        "ezair": ("Ezair", "et al.~2015"), "goguelin-len": ("Goguelin", "et al.~2021"),
        "goguelin-vol": ("Goguelin", "et al.~2021 (vol.)"), "alexander": ("Alexander", "et al.~1998"),
        "tweaker3-vol": ("Tweaker-3", "(volume)"), "tweaker3-sur": ("Tweaker-3", "(surface)"),
        "support-volume": ("Support", "volume"), "orca-orient": ("OrcaSlicer", "auto-orient")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results")
    ap.add_argument("--methods", default="castro-eq,ezair,goguelin-len,alexander,tweaker3-vol,tweaker3-sur")
    ap.add_argument("--size-mm", default="60")
    ap.add_argument("--overhang-deg", default="45")
    a = ap.parse_args()
    rows = [r for r in csv.DictReader(open(Path(a.results) / "prusaslicer.csv", encoding="utf-8"))
            if r["status"] == "ok"]
    S = {(r["mesh"], r["pose"]): r for r in rows}
    ver = sorted({r.get("slicer_version", "") for r in rows if r.get("slicer_version")})
    ver = ver[0].replace("PrusaSlicer-", "PrusaSlicer~").split("+")[0] if ver else "PrusaSlicer"
    methods = a.methods.split(",")
    cols = ["initial"] + methods
    meshes = [m for m in NAMES if any((m, p) in S for p in cols)]
    reps = {int(float(r.get("repeats") or 1)) for r in rows}
    if max(reps) > 1:
        tie = (f"Medians of {max(reps)} repeated slicings; best value among the methods in bold, "
               r"together with every method whose min--max range over the repetitions overlaps it.")
    else:
        tie = "Best value among the methods in bold."
    L = []
    L.append(r"\begin{table}[t]")
    L.append(r"\centering")
    L.append(r"\caption{Support filament and print time estimated by " + ver + r" for the initial pose "
             r"(orientation of the input file, $\theta_1=\theta_2=0$) and for the orientation returned by "
             r"each method. Parts scaled to a largest dimension of " + a.size_mm + r"\,mm; 0.4\,mm nozzle, "
             r"0.2\,mm layers, PLA, supports enabled with a " + a.overhang_deg + r"$^\circ$ overhang "
             r"threshold. Values are slicer estimates, not measurements of printed parts. " + tie + "}")
    L.append(r"\label{tab:results}")
    L.append(r"\small")
    L.append(r"\begin{tabular}{l" + "r" * len(cols) + "}")
    L.append(r"\toprule")
    L.append(" & " + " & ".join(HEAD.get(c, (c, ""))[0] for c in cols) + r" \\")
    L.append(" & " + " & ".join(HEAD.get(c, ("", ""))[1] for c in cols) + r" \\")
    L.append(r"\midrule")
    for key, lab, fmt, scale in (("support_filament_mm", "Support filament (m)", "{:.2f}", 1e-3),
                                 ("time_min", "Print time (min)", "{:.0f}", 1.0)):
        L.append(r"\multicolumn{" + str(len(cols) + 1) + r"}{l}{\emph{" + lab + r"}}\\")
        for m in meshes:
            vals = [float(S[(m, c)][key]) * scale if (m, c) in S else None for c in cols]
            shown = [fmt.format(v) if v is not None else "--" for v in vals]

            def rng(c):  # [min, max] over repeated slicings, if available
                r = S.get((m, c), {})
                if r.get(key + "_min") not in (None, "") and int(float(r.get("repeats") or 1)) > 1:
                    return float(r[key + "_min"]) * scale, float(r[key + "_max"]) * scale
                return None

            meths = [c for c, sv in zip(cols, shown) if c != "initial" and sv != "--"]
            if meths and all(rng(c) for c in meths):
                # best = lowest median; a method ties with it when the [min, max] ranges overlap
                b = min(meths, key=lambda c: float(S[(m, c)][key]))
                lo_b, hi_b = rng(b)
                is_best = {c: rng(c)[0] <= hi_b and lo_b <= rng(c)[1] for c in meths}
            else:
                cand = [float(sv) for sv, c in zip(shown, cols) if c != "initial" and sv != "--"]
                best = min(cand) if cand else None
                is_best = {c: float(sv) == best for sv, c in zip(shown, cols) if c != "initial" and sv != "--"}
            cells = [sv if not is_best.get(c) else r"\textbf{" + sv + "}" for sv, c in zip(shown, cols)]
            L.append(f"{NAMES[m]} & " + " & ".join(cells) + r" \\")
        L.append(r"\midrule" if key == "support_filament_mm" else r"\bottomrule")
    L.append(r"\end{tabular}")
    L.append(r"\end{table}")
    print("\n".join(L))


if __name__ == "__main__":
    main()
