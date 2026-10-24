#!/usr/bin/env python3
"""Head-to-head LaTeX table: our orientation against each other method.

    python scripts/head_to_head.py results_angles/sweep_summary.csv --all-angles > table_head_to_head.tex
    python scripts/head_to_head.py results_angles/sweep_summary.csv --overhang-deg 45
    python scripts/head_to_head.py results/prusaslicer.csv --text

A case is one surface sliced with one support threshold. For each other method
and each metric (support filament, print time), the per-case relative
difference 100 (ours - other) / other is summarized by its median over the
cases, by the number of cases where ours is lower / within +-TIE % / higher,
and by the relative difference of the totals over all cases. Negative values
mean that our orientation needs less. With --all-angles every threshold of the
sweep is used (Table 4 of the paper) and the table also gives the range of the
per-threshold totals; otherwise only the rows of --overhang-deg are used when
the CSV has an overhang_deg column.
"""
import argparse, csv, statistics

OURS = "castro-eq"
HEAD = {"ezair": r"\citet{ezair2015orientation}", "goguelin-len": r"\citet{goguelin2021bayesian}",
        "alexander": r"\citet{alexander1998part}",
        "tweaker3-vol": "Tweaker-3 (vol.)", "tweaker3-sur": "Tweaker-3 (surf.)"}
METRICS = (("support_filament_mm", "Support filament"), ("time_min", "Printing time"))


def signed(v):
    s = f"{v:+.1f}"
    return "0.0" if s in ("+0.0", "-0.0") else s


def compare(S, cases, other, key, tie):
    rel = [100 * (float(S[c + (OURS,)][key]) - float(S[c + (other,)][key])) / float(S[c + (other,)][key])
           for c in cases]
    total = 100 * (sum(float(S[c + (OURS,)][key]) for c in cases)
                   / sum(float(S[c + (other,)][key]) for c in cases) - 1)
    wins = sum(r < -tie for r in rel)
    losses = sum(r > tie for r in rel)
    return statistics.median(rel), (wins, len(rel) - wins - losses, losses), total, rel


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", help="sweep_summary.csv or prusaslicer.csv")
    ap.add_argument("--methods", default="ezair,goguelin-len,alexander,tweaker3-vol,tweaker3-sur")
    ap.add_argument("--overhang-deg", type=float, default=45.0)
    ap.add_argument("--all-angles", action="store_true", help="pool every threshold of the sweep")
    ap.add_argument("--tie", type=float, default=1.0, help="tie band in percent (default 1)")
    ap.add_argument("--text", action="store_true", help="plain-text report with per-case values")
    a = ap.parse_args()
    rows = [r for r in csv.DictReader(open(a.csv, encoding="utf-8")) if r.get("status", "ok") == "ok"]
    has_angle = bool(rows) and "overhang_deg" in rows[0]
    if has_angle and not a.all_angles:
        rows = [r for r in rows if float(r["overhang_deg"]) == a.overhang_deg]
    ang = (lambda r: float(r["overhang_deg"])) if has_angle else (lambda r: a.overhang_deg)
    S = {(ang(r), r["mesh"], r["pose"]): r for r in rows}
    methods = a.methods.split(",")
    cases = sorted({(ang(r), r["mesh"]) for r in rows})
    cases = [c for c in cases if all(c + (p,) in S for p in [OURS] + methods)]
    angles = sorted({c[0] for c in cases})
    by_angle = {t: [c for c in cases if c[0] == t] for t in angles}

    if a.text:
        print(f"{len(cases)} cases; thresholds:", ", ".join(f"{t:g}" for t in angles))
        for key, lab in METRICS:
            print(f"== {lab} (ours vs other, %)")
            for p in methods:
                med, (w, t, l), tot, rel = compare(S, cases, p, key, a.tie)
                print(f"  {p:13s} median {med:+6.1f}  W/T/L {w}/{t}/{l}  total {tot:+6.1f}")
                for th in angles:
                    med, (w, t, l), tot, rel = compare(S, by_angle[th], p, key, a.tie)
                    print(f"      {th:4g} deg: median {med:+6.1f}  W/T/L {w}/{t}/{l}  total {tot:+6.1f}  "
                          + " ".join(f"{c[1]}:{r:+.1f}" for c, r in zip(by_angle[th], rel)))
        return

    sweep = len(angles) > 1
    ncol = 4 if sweep else 3
    head = r"Median & L/E/H & Total" + (r" & Range" if sweep else "")
    L = [r"\begin{table*}[!t]" if sweep else r"\begin{table}[!t]", r"\centering", r"\footnotesize",
         r"\setlength{\tabcolsep}{4pt}" if not sweep else "",
         r"\resizebox{\columnwidth}{!}{%" if not sweep else "",
         r"\begin{tabular}{l" + ("rcrr" if sweep else "rcr") * 2 + "}", r"\toprule",
         rf" & \multicolumn{{{ncol}}}{{c}}{{\textbf{{Support filament}}}} & "
         rf"\multicolumn{{{ncol}}}{{c}}{{\textbf{{Printing time}}}} \\",
         rf"\cmidrule(lr){{2-{ncol + 1}}}\cmidrule(lr){{{ncol + 2}-{2 * ncol + 1}}}",
         r"\textbf{Against} & " + head + " & " + head + r" \\", r"\midrule"]
    for p in methods:
        cells = []
        for key, _ in METRICS:
            med, (w, t, l), tot, _ = compare(S, cases, p, key, a.tie)
            cells += [f"${signed(med)}$", f"{w}/{t}/{l}", f"${signed(tot)}$"]
            if sweep:
                per = [compare(S, by_angle[th], p, key, a.tie)[2] for th in angles]
                cells.append(f"$[{signed(min(per))},\\,{signed(max(per))}]$")
        L.append(HEAD.get(p, p) + " & " + " & ".join(cells) + r" \\")
    if sweep:
        where = (rf"over the {len(cases)} cases given by the {len(cases) // len(angles)} surfaces and the "
                 rf"{len(angles)} support thresholds of Figure~\ref{{fig:angle_sweep}} "
                 rf"(\ang{{{angles[0]:g}}} to \ang{{{angles[-1]:g}}}, PrusaSlicer~2.9.6; the angle-dependent "
                 r"methods are re-optimized for each threshold)")
        rng = (r", and \emph{Range} is the smallest and largest value of \emph{Total} when it is computed "
               r"separately for each threshold")
    else:
        where = (rf"over the {len(cases)} surfaces of Table~\ref{{tab:benchmark}} (PrusaSlicer~2.9.6, support "
                 rf"threshold of \ang{{{angles[0]:g}}})")
        rng = ""
    L += [r"\bottomrule", r"\end{tabular}" + ("" if sweep else "}"),
          r"\caption{Head-to-head comparison of our orientation with that of each other method, " + where +
          r". For each case, the relative difference "
          r"$100\,(x_{\mathrm{ours}}-x_{\mathrm{other}})/x_{\mathrm{other}}$ (\%) is computed; "
          r"\emph{Median} is its median over the cases, \emph{L/E/H} counts the cases in which our "
          rf"orientation needs less, about the same (within $\pm$\SI{{{a.tie:g}}}{{\percent}}), or more, "
          r"\emph{Total} is the relative difference of the sums over all cases" + rng +
          r". Negative values favor our method.}",
          r"\label{tab:headtohead}", r"\end{table*}" if sweep else r"\end{table}"]
    print("\n".join(l for l in L if l))


if __name__ == "__main__":
    main()
