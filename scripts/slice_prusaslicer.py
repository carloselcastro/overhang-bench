#!/usr/bin/env python3
"""Slice every STL in a folder with PrusaSlicer and collect the slicer's own
estimates (filament length/mass, print time) plus the extrusion attributed to
support material, parsed from the ;TYPE: tags of the G-code.

    python scripts/slice_prusaslicer.py results/stl results/prusaslicer.csv \
        [--config scripts/prusaslicer_reference.ini] [--exe prusa-slicer]

On Windows the executable is usually
    "C:\\Program Files\\Prusa3D\\PrusaSlicer\\prusa-slicer-console.exe"

Numbers in the output are PrusaSlicer *estimates* (its G-code time model and
extrusion totals), not measurements of a physical print; report them as such.
"""
import argparse, csv, math, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

TIME_RE = re.compile(r";\s*estimated printing time \(normal mode\)\s*=\s*(.+)")
FIL_MM_RE = re.compile(r";\s*filament used \[mm\]\s*=\s*([\d.]+)")
FIL_G_RE = re.compile(r";\s*filament used \[g\]\s*=\s*([\d.]+)")
FIL_CM3_RE = re.compile(r";\s*filament used \[cm3\]\s*=\s*([\d.]+)")


def parse_time(s):
    tot = 0.0
    for val, unit in re.findall(r"(\d+)\s*([dhms])", s):
        tot += int(val) * {"d": 86400, "h": 3600, "m": 60, "s": 1}[unit]
    return tot / 60.0  # minutes


def parse_gcode(path):
    out = {"time_min": math.nan, "filament_mm": math.nan, "filament_g": math.nan,
           "filament_cm3": math.nan}
    e_by_type, cur_type = {}, "unknown"
    absolute_e, last_e = True, 0.0
    with open(path, encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            if line.startswith(";"):
                if line.startswith(";TYPE:"):
                    cur_type = line[6:].strip()
                for key, rx in (("filament_mm", FIL_MM_RE), ("filament_g", FIL_G_RE),
                                ("filament_cm3", FIL_CM3_RE)):
                    m = rx.match(line)
                    if m:
                        out[key] = float(m.group(1))
                m = TIME_RE.match(line)
                if m:
                    out["time_min"] = parse_time(m.group(1))
                continue
            code = line.split(";", 1)[0].strip()
            if not code:
                continue
            if code.startswith("M82"):
                absolute_e = True
            elif code.startswith("M83"):
                absolute_e = False
            elif code.startswith("G92"):
                m = re.search(r"E(-?[\d.]+)", code)
                if m:
                    last_e = float(m.group(1))
            elif code.startswith(("G1", "G0")):
                m = re.search(r"E(-?[\d.]+)", code)
                if m:
                    e = float(m.group(1))
                    de = e - last_e if absolute_e else e
                    if absolute_e:
                        last_e = e
                    # only moves with XY travel extrude material; E-only moves are
                    # retractions/deretractions and must not be attributed to a type
                    if de > 0 and re.search(r"[XY]-?[\d.]", code):
                        e_by_type[cur_type] = e_by_type.get(cur_type, 0.0) + de
    sup = sum(v for k, v in e_by_type.items() if k.lower().startswith("support material"))
    out["support_filament_mm"] = sup
    out["part_filament_mm"] = sum(e_by_type.values()) - sup
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stl_dir")
    ap.add_argument("out_csv")
    ap.add_argument("--config", default=str(Path(__file__).with_name("prusaslicer_reference.ini")))
    ap.add_argument("--exe", default="prusa-slicer")
    ap.add_argument("--keep-gcode", default=None, help="folder to keep the G-code files")
    ap.add_argument("--overhang-deg", type=float, default=None,
                    help="printable overhang measured from the vertical (overhang-bench convention); "
                         "passed to PrusaSlicer as support_material_threshold = 90 - value "
                         "(PrusaSlicer measures the slope from the horizontal). Default: the .ini value")
    ap.add_argument("--jobs", type=int, default=1, help="slice this many files in parallel")
    ap.add_argument("--threads", type=int, default=None,
                    help="PrusaSlicer --threads N (1 = single-threaded; use it if repeated slicing of "
                         "the same file gives different numbers)")
    ap.add_argument("--repeats", type=int, default=1,
                    help="slice every file N times; report the median and the min/max of time and "
                         "support filament (PrusaSlicer's support generation can be non-deterministic)")
    a = ap.parse_args()

    exe = a.exe if Path(a.exe).is_file() else shutil.which(a.exe)
    if not exe:
        sys.exit(f"PrusaSlicer not found: {a.exe}\n"
                 "Install it (https://www.prusa3d.com/page/prusaslicer_424/) and pass the console "
                 "executable with --exe, e.g.\n"
                 '  --exe "C:\\Program Files\\Prusa3D\\PrusaSlicer\\prusa-slicer-console.exe"\n'
                 "To locate it:  Get-ChildItem 'C:\\Program Files' -Recurse -Filter "
                 "prusa-slicer-console.exe -ErrorAction SilentlyContinue")
    a.exe = exe
    ver = subprocess.run([exe, "--help"], capture_output=True, text=True).stdout.splitlines()[:1]
    print(f"slicer: {exe}  ({ver[0] if ver else 'version unknown'})")
    stls = sorted(Path(a.stl_dir).glob("*.stl"))
    if not stls:
        sys.exit(f"no STL files in {a.stl_dir}")
    gdir = Path(a.keep_gcode) if a.keep_gcode else Path(tempfile.mkdtemp())
    gdir.mkdir(parents=True, exist_ok=True)
    fields = ["mesh", "pose", "slicer_version", "time_min", "filament_mm", "filament_g", "filament_cm3",
              "support_filament_mm", "part_filament_mm", "repeats",
              "time_min_min", "time_min_max", "support_filament_mm_min", "support_filament_mm_max",
              "filament_mm_min", "filament_mm_max", "status"]
    with open(a.out_csv, "w", newline="", encoding="utf-8") as fo:
        w = csv.DictWriter(fo, fieldnames=fields)
        w.writeheader()
        extra = []
        if a.overhang_deg is not None:
            extra = ["--support-material-threshold", f"{90.0 - a.overhang_deg:g}"]
        if a.threads:
            extra += ["--threads", str(a.threads)]
        vname = ver[0].split(" based")[0] if ver else ""

        def slice_one(stl):
            mesh, _, pose = stl.stem.partition("__")
            row = {"mesh": mesh, "pose": pose, "slicer_version": vname}
            runs = []
            for k in range(max(1, a.repeats)):
                g = gdir / (stl.stem + (f"_r{k}" if a.repeats > 1 else "") + ".gcode")
                cmd = [a.exe, "--export-gcode", "--load", a.config, *extra, "--center", "125,105",
                       "--output", str(g), str(stl)]
                p = subprocess.run(cmd, capture_output=True, text=True)
                if p.returncode != 0 or not g.exists():
                    msg = (p.stderr or p.stdout).strip().splitlines()
                    row["status"] = "error: " + (msg[-1][:200] if msg else "")
                    break
                runs.append(parse_gcode(g))
                if not a.keep_gcode:
                    g.unlink()
            if runs and len(runs) == max(1, a.repeats):
                import statistics
                for key in runs[0]:
                    row[key] = statistics.median(r[key] for r in runs)
                for key in ("time_min", "support_filament_mm", "filament_mm"):
                    row[key + "_min"] = min(r[key] for r in runs)
                    row[key + "_max"] = max(r[key] for r in runs)
                row["repeats"] = len(runs)
                row["status"] = "ok"
            if row.get("repeats", 1) > 1:
                print(f"{stl.name:45s} {row.get('status')}  t={row['time_min']:.1f} "
                      f"[{row['time_min_min']:.1f}-{row['time_min_max']:.1f}] min  "
                      f"sup={row['support_filament_mm']/1000:.2f} [{row['support_filament_mm_min']/1000:.2f}-"
                      f"{row['support_filament_mm_max']/1000:.2f}] m  (median [min-max] of {row['repeats']})",
                      flush=True)
                return stl, row
            print(f"{stl.name:45s} {row.get('status')}  t={row.get('time_min', float('nan')):.1f} min  "
                  f"fil={row.get('filament_mm', float('nan'))/1000:.2f} m  "
                  f"sup={row.get('support_filament_mm', float('nan'))/1000:.2f} m", flush=True)
            return stl, row

        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=max(1, a.jobs)) as ex:
            results = dict(ex.map(slice_one, stls))
        for stl in stls:
            mesh, _, pose = stl.stem.partition("__")
            row = results[stl]
            w.writerow(row)


if __name__ == "__main__":
    main()
