from __future__ import annotations

import importlib.util
import platform
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_MODULES = [
    "numpy",
    "scipy",
    "pyscf",
    "quimb",
    "cotengra",
    "stim",
]

OPTIONAL_MODULES = [
    "rocrate",
]


def main() -> int:
    print(f"python: {sys.executable}")
    print(f"python_version: {platform.python_version()}")
    print(f"platform: {platform.platform()}")
    print(f"capas_root: {ROOT}")

    missing: list[str] = []
    for module in REQUIRED_MODULES:
        spec = importlib.util.find_spec(module)
        if spec is None:
            missing.append(module)
            print(f"{module}: MISSING")
        else:
            origin = spec.origin or "namespace/builtin"
            print(f"{module}: ok ({origin})")

    for module in OPTIONAL_MODULES:
        spec = importlib.util.find_spec(module)
        if spec is None:
            print(f"{module}: optional missing (needed only for external RO-Crate validation)")
        else:
            origin = spec.origin or "namespace/builtin"
            print(f"{module}: optional ok ({origin})")

    if missing:
        print("\nEnvironment is not reproducible for the full corpus.")
        print("Missing modules:")
        for module in missing:
            print(f"- {module}")
        print("\nInstall packages from requirements-corpus.txt.")
        return 1

    print("\nEnvironment check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
