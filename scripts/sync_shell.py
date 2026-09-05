#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Sincroniza el shell de marca hacia este consumidor.

La fuente es el repo kreniq-brand. Este script copia el shell y su lock; nunca al
revés. Si editaste la copia local en vez de la fuente, esto la sobrescribe — que es
justo lo que debe pasar.

Uso:  python3 scripts/sync_shell.py [ruta-a-kreniq-brand]
Por defecto busca ../kreniq-brand, o el valor de $KRENIQ_BRAND.
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
FILES = ("kreniq-shell.css", "lang.js", "krenniq-logo.png", "logo_kreniq_volum_trico.html")


def main() -> int:
    if len(sys.argv) > 1:
        brand = Path(sys.argv[1])
    else:
        brand = Path(os.environ.get("KRENIQ_BRAND", ROOT.parent / "kreniq-brand"))
    brand = brand.expanduser().resolve()

    if not brand.is_dir():
        print(f"FAIL: brand repo not found at {brand}")
        print("      pass its path, or set KRENIQ_BRAND")
        return 1
    lock = brand / "shell.lock.json"
    if not lock.is_file():
        print(f"FAIL: {lock} missing — regenerate the lock in the brand repo")
        return 1

    for name in FILES:
        src = brand / name
        if not src.is_file():
            print(f"FAIL: {src} missing in the brand repo")
            return 1
        shutil.copy2(src, DOCS / name)
    shutil.copy2(lock, DOCS / "shell.lock.json")

    print(f"OK: synced {len(FILES)} shell files + shell.lock.json from {brand}")
    print("    run `python3 designlab/layout_lint.py` to confirm no drift remains.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
