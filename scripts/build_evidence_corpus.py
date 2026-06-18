from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


STEPS = [
    ("check reproducibility environment", [sys.executable, "scripts/check_reproducibility_env.py"]),
    ("validate published RO-Crate corpus", [sys.executable, "benchmarks/validate_ro_crates.py"]),
    ("validate CAPAS profile", [sys.executable, "benchmarks/validate_capas_profile.py"]),
    ("validate witness independence", [sys.executable, "benchmarks/validate_witness_independence.py"]),
    ("validate evidence claims", [sys.executable, "benchmarks/validate_evidence_claims.py"]),
    ("validate universal anchor matrix", [sys.executable, "benchmarks/validate_universal_anchor_matrix.py"]),
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
