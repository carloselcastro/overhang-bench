#!/usr/bin/env python3
"""Download the libigl meshes used by Castro (2020) into ./meshes.

    python scripts/fetch_meshes.py
"""
import urllib.request
from pathlib import Path

BASE = "https://raw.githubusercontent.com/libigl/libigl-tutorial-data/master/"
FILES = ["arm.obj", "bunny.off", "camel_b.obj", "cow.off", "horse_quad.obj",
         "decimated-knight.off", "decimated-max.obj"]
out = Path(__file__).resolve().parent.parent / "meshes"
out.mkdir(exist_ok=True)
for f in FILES:
    dst = out / f
    if dst.exists():
        print(f"{f}: already here"); continue
    urllib.request.urlretrieve(BASE + f, dst)
    print(f"{f}: ok")
