# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Verify the pip package is real and complete: every listed module exists, the modules the
CORE SDK needs at runtime are shipped, and a wheel actually BUILDS containing them + the entry
points. This is the 'pip install capas-claim-gate' surface, proven not asserted.
"""
from __future__ import annotations

import ast
import subprocess
import sys
import tomllib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _capas_imports(path: Path) -> set[str]:
    out: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.Import):
            out |= {a.name.split(".")[0] for a in node.names if a.name.startswith("capas")}
        elif isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("capas"):
            out.add(node.module.split(".")[0])
    return out


def run() -> int:
    checks = []
    pp = tomllib.loads((ROOT / "pyproject.toml").read_text())
    shipped = set(pp["tool"]["setuptools"]["py-modules"])
    scripts = pp["project"].get("scripts", {})

    # 1. every shipped module exists
    missing = [m for m in shipped if not (ROOT / f"{m}.py").exists()]
    checks.append((f"all {len(shipped)} shipped py-modules exist", not missing))

    # 2. CRITICAL: the invariant override runs on every decide -> capas_invariants MUST ship
    checks.append(("capas_invariants is shipped (invariant override runs on every gate)",
                   "capas_invariants" in shipped))
    checks.append(("capas_quantum_physics is shipped (gate_quantum + quantum invariants)",
                   "capas_quantum_physics" in shipped))
    checks.append(("capas_mcp is shipped (MCP server surface)", "capas_mcp" in shipped))

    # 3. entry points
    checks.append(("capas-mcp console script -> capas_mcp:serve",
                   scripts.get("capas-mcp") == "capas_mcp:serve"))

    # 4. the SDK's own direct capas-imports are all shipped (closure for the core surface)
    sdk_direct = _capas_imports(ROOT / "capas_sdk.py") | _capas_imports(ROOT / "capas_mcp.py")
    unshipped = sorted(sdk_direct - shipped - {"capas_sdk"})
    checks.append((f"capas_sdk/mcp direct deps shipped ({sorted(sdk_direct)})", not unshipped))

    # 5. a wheel BUILDS (no network: --no-isolation uses the present setuptools) and contains the
    #    critical modules + the entry point metadata.
    out = ROOT / "dist"
    built_ok = False
    try:
        r = subprocess.run([sys.executable, "-m", "build", "--wheel", "--no-isolation",
                            "--outdir", str(out)], cwd=str(ROOT), capture_output=True, text=True, timeout=300)
        wheels = sorted(out.glob("capas_claim_gate-0.4.0-*.whl"))
        if r.returncode == 0 and wheels:
            names = zipfile.ZipFile(wheels[-1]).namelist()
            has_mods = all(f"{m}.py" in names for m in ("capas_invariants", "capas_quantum_physics", "capas_mcp"))
            has_entry = any("entry_points.txt" in n for n in names)
            built_ok = has_mods and has_entry
        else:
            print("   build stderr:", (r.stderr or "")[-300:])
    except Exception as exc:
        print(f"   wheel build skipped/failed: {exc}")
    checks.append(("wheel BUILDS and contains the new modules + entry points", built_ok))

    ok = all(c for _, c in checks)
    for label, c in checks:
        print(f"{'OK ' if c else 'XX '}{label}")
    print("PIP PACKAGE: pass (capas-claim-gate v0.4.0 builds with the full deterministic surface)"
          if ok else "PIP PACKAGE: FAILURES")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
