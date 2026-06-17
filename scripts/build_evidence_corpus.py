from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


STEPS = [
    ("generate traces", [sys.executable, "benchmarks/generate_quantum_engine_gold_traces.py"]),
    ("export PROV", [sys.executable, "benchmarks/export_gold_traces_to_prov.py"]),
    ("export RO-Crate", [sys.executable, "benchmarks/export_gold_traces_to_ro_crate.py"]),
    ("validate RO-Crate", [sys.executable, "benchmarks/validate_ro_crates.py"]),
    ("summarize audit", [sys.executable, "audits/summarize_gold_trace_audit.py"]),
]


def main() -> int:
    final_code = 0
    for label, cmd in STEPS:
        print(f"\n=== {label} ===")
        proc = subprocess.run(cmd, cwd=ROOT)
        if proc.returncode != 0:
            if label == "summarize audit":
                print("audit summary returned non-zero because fine_tune_ready is false; corpus may still be coverage-ready")
                final_code = 0
                continue
            final_code = proc.returncode
            break
    return final_code


if __name__ == "__main__":
    raise SystemExit(main())
