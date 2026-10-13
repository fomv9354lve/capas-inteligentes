#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Conformance gate `no_llm_verdict`: the verdict is a deterministic function of the payload, with no
language model, network or clock in the decision path.
What it measures (the §6 counter-signature of 2026-10-13 found the previous script under this label
measured Cara-1/Cara-2 decoupling instead):
  (1) STATIC: the transitive call graph of decide_external_claim (and every function it calls in capas.py
      and the invariant modules) contains no network / LLM-client / random / clock call.
  (2) DYNAMIC: every payload in the Ginibre blind corpora (if present) plus a built-in set decides to the
      SAME verdict, reason and audit_hash on two runs in two fresh interpreters, with the network blocked.
Run: `python3 benchmarks/verify_determinism.py`."""
from __future__ import annotations
import ast, json, os, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

FORBIDDEN = {"urlopen", "Request", "requests", "httpx", "socket", "openai", "anthropic", "random", "randint",
             "choice", "shuffle", "time", "now", "today", "uuid4", "getenv", "environ", "input"}
MODULES = ["capas.py", "capas_invariants.py", "capas_claim_state.py", "capas_quantum_physics.py", "capas_rmt.py", "capas_language.py"]


def static_check() -> list[str]:
    funcs: dict[str, ast.FunctionDef] = {}
    for m in MODULES:
        p = ROOT / m
        if not p.exists():
            continue
        for node in ast.walk(ast.parse(p.read_text())):
            if isinstance(node, ast.FunctionDef):
                funcs.setdefault(node.name, node)
    # Documented exception: _source_url_verified fetches a remote source ONLY under the opt-in env flag
    # CAPAS_VERIFY_REMOTE_SOURCES=1, and only to compare bytes against a sha256 the payload DECLARES
    # (unreachable -> False, fail-closed). Without the flag the decision path never touches the network.
    # The guard itself is asserted below so the exception cannot silently widen.
    src = (ROOT / "capas.py").read_text()
    i = src.index("def _source_url_verified")
    guard_ok = 'os.environ.get("CAPAS_VERIFY_REMOTE_SOURCES") != "1"' in src[i:i + 800]
    seen, todo, bad = set(), ["decide_external_claim"], ([] if guard_ok else ["_source_url_verified: opt-in network guard missing"])
    seen.add("_source_url_verified")
    while todo:
        name = todo.pop()
        if name in seen or name not in funcs:
            continue
        seen.add(name)
        for n in ast.walk(funcs[name]):
            if isinstance(n, ast.Call):
                f = n.func
                callee = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else None)
                if callee in FORBIDDEN:
                    # allow datetime use only for age computations on DECLARED timestamps (no clock read)
                    bad.append(f"{name} -> {callee}")
                elif callee and callee not in seen:
                    todo.append(callee)
    return bad


def _payloads() -> list[dict]:
    out = [{"schema_version": "capas-claim-payload-v3", "claim": {"id": f"d{i}", "type": t, "text": "x"}, "evidence": e}
           for i, (t, e) in enumerate([
               ("exact_model_solution", {"abs_error": 0.3, "tolerance": 1.0}),
               ("exact_model_solution", {"abs_error": 3.0, "tolerance": 1.0}),
               ("exact_model_solution", {"abs_error": 0.0, "tolerance": 1e-3}),
               ("statistical_confidence", {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True}),
               ("proof_admissibility", {"claim_scope": "universal", "steps_all_valid": True, "load_bearing_step_identified": True, "uniform_bound_proven": False}),
               ("reproducibility_check", {"artifact_available": True, "independent_reproduction_pass": False}),
           ])]
    G = Path("/Users/kreniq/Desktop/KRENIQ/AI Projects/01. Investigacion/Paper - Inverse Ginibre Overlap/CAPAS_CORPUS_2026-10-12")
    for f in ("PARA_CAPAS_claims.jsonl", "PARA_CAPAS_claims_X4.jsonl", "PARA_CAPAS_claims_X5.jsonl"):
        if (G / f).exists():
            out += [json.loads(l)["payload"] for l in (G / f).read_text(encoding="utf-8").splitlines() if l.strip()]
    return out


RUNNER = r'''
import json, sys, socket
sys.path.insert(0, %r)
class _Blocked(socket.socket):
    def connect(self, *a, **k): raise RuntimeError("network blocked")
    def connect_ex(self, *a, **k): raise RuntimeError("network blocked")
socket.socket = _Blocked
socket.create_connection = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("network blocked"))
import capas
out = []
for p in json.load(open(sys.argv[1])):
    d = capas.decide_external_claim(p); d = d.get("decision", d)
    out.append([d.get("verdict"), d.get("reason"), d.get("audit_hash")])
print(json.dumps(out))
''' % str(ROOT)


def dynamic_check(payloads: list[dict]) -> list[str]:
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(payloads, f); pf = f.name
    runs = []
    for _ in range(2):
        r = subprocess.run([sys.executable, "-c", RUNNER, pf], capture_output=True, text=True, timeout=900, env={**os.environ, "PYTHONHASHSEED": str(_ * 7919)})
        if r.returncode != 0:
            os.unlink(pf); return [f"run failed: {r.stderr[-300:]}"]
        runs.append(json.loads(r.stdout))
    os.unlink(pf)
    diffs = [f"payload #{i}: {a} != {b}" for i, (a, b) in enumerate(zip(*runs)) if a != b]
    return diffs


def main() -> int:
    bad = static_check()
    payloads = _payloads()
    diffs = dynamic_check(payloads)
    if bad or diffs:
        print("FAIL:\n  " + "\n  ".join(bad + diffs)); return 1
    print(f"OK: decide_external_claim call graph has no network/LLM/random/clock call (sole exception: remote source "
          f"hash check behind the opt-in CAPAS_VERIFY_REMOTE_SOURCES=1 guard, asserted present); {len(payloads)} payloads "
          f"decide to identical verdict+reason+audit_hash across two fresh interpreters with the network blocked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
