"""CAPAS conformance harness — the Sonobuoy analog: run-it-yourself, get the SAME verdict + hash.

The open-standard's distribution mechanic (per the market research): the mark attests that an artifact
passed THIS suite, and anyone can run the exact same suite and reproduce the exact same result. No private
process to trust. Determinism is the product's structural advantage over a human-audited standard (SOC 2):
the conformance result is a re-derivable hash, not an opinion.

    python3 benchmarks/conformance.py            # run the suite -> CAPAS-CONFORMANT (yes/no) + result hash
    python3 benchmarks/conformance.py --json      # machine-readable conformance record

A PASS here is what a "CAPAS-conformant" claim means: the deterministic core upholds its load-bearing
invariants on this machine, reproducibly.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# the load-bearing conformance suite: each must pass for the mark to be claimable
SUITE = [
    ("fail_closed", "benchmarks/verify_fail_closed.py", "a structurally-deficient claim is never accepted"),
    ("robustness", "benchmarks/verify_robustness.py", "survives hostile input; no crash, no false-accept"),
    ("no_llm_verdict", "benchmarks/verify_cara_decoupling.py", "no language model in the verdict"),
    ("quantum_commitment", "benchmarks/verify_quantum_commitment.py", "quantum-advantage defeater contract"),
    ("pharma_admissibility", "benchmarks/generate_pharma_corpus.py", "pharma statistical-admissibility, fail-closed"),
    ("proof_ledger", "benchmarks/generate_proof_ledger.py", "every public claim CLOSED/BACKED/SCOPED, none bare"),
    ("hold_has_resolution", "benchmarks/verify_hold_has_resolution.py", "no HOLD is a dead end; each ships a constructive way out"),
]


def _run(path: str) -> tuple[bool, str]:
    r = subprocess.run([sys.executable, path], cwd=str(ROOT), capture_output=True, text=True, timeout=600)
    return r.returncode == 0, (r.stdout or r.stderr).strip().splitlines()[-1][:120] if (r.stdout or r.stderr) else ""


def main() -> int:
    results = []
    for cid, path, desc in SUITE:
        ok, tail = _run(path)
        results.append({"id": cid, "path": path, "desc": desc, "pass": ok, "last_line": tail})

    passed = all(r["pass"] for r in results)
    # a re-derivable conformance hash over the (id, pass) pairs — same suite, same machine -> same hash
    digest = hashlib.sha256(
        json.dumps([(r["id"], r["pass"]) for r in results], sort_keys=True).encode()).hexdigest()[:24]
    record = {"conformant": passed, "suite": [{"id": r["id"], "pass": r["pass"]} for r in results],
              "result_hash": "sha256:" + digest,
              "statement": ("CAPAS-CONFORMANT: the deterministic core upholds its load-bearing invariants, "
                            "reproducibly on this machine." if passed else
                            "NOT CONFORMANT: one or more invariants failed — see the suite.")}
    (ROOT / "outputs").mkdir(exist_ok=True)
    (ROOT / "outputs" / "conformance_result.json").write_text(json.dumps(record, indent=2))

    if "--json" in sys.argv:
        print(json.dumps(record, indent=2))
        return 0 if passed else 1

    print("=== CAPAS CONFORMANCE SUITE (run-it-yourself; same suite the certifier runs) ===")
    for r in results:
        print(f"  {'OK ' if r['pass'] else 'XX '}{r['id']:22} {r['desc']}")
    print(f"\nresult hash: sha256:{digest}  (deterministic — reproduces on any machine)")
    print(record["statement"])
    print("Anyone can reproduce this: `python3 benchmarks/conformance.py`. The mark attests a verified "
          "artifact passed exactly this — no private process to trust.")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
