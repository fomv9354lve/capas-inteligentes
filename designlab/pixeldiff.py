#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""pixeldiff — regresión visual de píxeles entre dos screenshots (#2 del backlog de UX).

Compara antes/después (o dos páginas que deberían verse igual), reporta el % de píxeles que
difieren y guarda un heatmap del diff. Convierte "comparar capturas a ojo" en un número.

Uso:  python3 designlab/pixeldiff.py before.png after.png [diff_out.png] [--threshold 1.0]
Exit 0 si la diferencia <= threshold (%), 1 si la supera (apto para CI de regresión visual)."""
from __future__ import annotations
import sys
from PIL import Image, ImageChops


def diff(a_path: str, b_path: str, out: str = "diff.png", threshold: float = 1.0):
    a = Image.open(a_path).convert("RGB")
    b = Image.open(b_path).convert("RGB")
    if a.size != b.size:
        w, h = min(a.width, b.width), min(a.height, b.height)
        print("⚠ tamaños distintos %s vs %s -> recorto a %dx%d" % (a.size, b.size, w, h))
        a, b = a.crop((0, 0, w, h)), b.crop((0, 0, w, h))
    d = ImageChops.difference(a, b)
    bbox = d.getbbox()
    px = a.width * a.height
    # píxeles que difieren (cualquier canal > 12 de 255 = ruido de compresión ignorado)
    gray = d.convert("L")
    changed = sum(1 for v in gray.getdata() if v > 12)
    pct = 100.0 * changed / px
    # heatmap: amplifica el diff para verlo
    d.point(lambda v: min(255, v * 4)).save(out)
    print("diferencia: %.3f%% de los píxeles (%d/%d)  ·  bbox cambios: %s" % (pct, changed, px, bbox))
    print("heatmap -> %s" % out)
    ok = pct <= threshold
    print("%s (threshold %.2f%%)" % ("OK" if ok else "REGRESIÓN", threshold))
    return ok


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    thr = 1.0
    for i, a in enumerate(sys.argv):
        if a == "--threshold" and i + 1 < len(sys.argv):
            thr = float(sys.argv[i + 1])
    if len(args) < 2:
        print("uso: pixeldiff.py before.png after.png [diff_out.png] [--threshold 1.0]"); sys.exit(2)
    out = args[2] if len(args) > 2 else "diff.png"
    sys.exit(0 if diff(args[0], args[1], out, thr) else 1)


if __name__ == "__main__":
    main()
