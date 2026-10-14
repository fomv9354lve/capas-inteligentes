#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Certificate fixtures for the engine-independent checker (CERTIFICATE_SPEC.md) and its mutated-trace suite.
Decides every public redacted payload (research/ginibre_corpus/public/claims_*.jsonl) plus the examples/ payloads
with the CURRENT engine, and writes research/certificates/fixtures.jsonl: one sealed certificate per line,
{payload, certificate, seal, seal_hash}. The seal marks these as test fixtures, not a sealed batch.
Run: python3 scripts/make_certificate_fixtures.py [--check]"""
from __future__ import annotations

import glob, hashlib, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import capas  # noqa: E402

OUT = ROOT / "research" / "certificates" / "fixtures.jsonl"
FIELDS = ("schema_version", "input_claim", "verdict", "reason", "required_fields", "invariant_audit", "audit_hash_recipe",
          "engine_version", "rule_table_sha256", "rules_fired", "evidence_sha256", "notices", "audit_hash")


def H(x) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(x, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def payloads():
    for f in sorted(glob.glob(str(ROOT / "research" / "ginibre_corpus" / "public" / "claims_*.jsonl"))):
        if "X1-3_v2" in f:
            continue   # same claims as v1
        for line in open(f, encoding="utf-8"):
            r = json.loads(line)
            yield {"schema_version": r["schema_version"],
                   "claim": {"id": r["claim"]["id"], "type": r["claim"]["type"], "text": "sha256:" + r["claim"]["text_sha256"]},
                   "evidence": r["evidence"]}
    for f in sorted(glob.glob(str(ROOT / "examples" / "external_claim_*.json"))):
        p = json.load(open(f, encoding="utf-8"))
        if isinstance(p, dict) and "claim" in p:
            yield p


def build() -> str:
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip() or "unknown"
    rows = []
    for p in payloads():
        r = capas.decide_external_claim(p)
        cert = {k: r.get(k) for k in FIELDS}
        seal = {"engine_tag": f"engine-{capas.CAPAS_ENGINE_VERSION}", "engine_commit": "fixture (see git log)",
                "sealed_at": "fixture", "sealed_by": "Krenn-IQ (test fixture, not a sealed batch)", "run_by": "Krenn-IQ"}
        rows.append({"payload": p, "certificate": cert, "seal": seal, "seal_hash": H({"audit_hash": cert["audit_hash"], "seal": seal})})
    del commit
    return "".join(json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n" for x in rows)


def main() -> int:
    text = build()
    if "--check" in sys.argv:
        ok = OUT.is_file() and OUT.read_text(encoding="utf-8") == text
        print("certificate fixtures: in sync" if ok else "FAIL: research/certificates/fixtures.jsonl is stale; run scripts/make_certificate_fixtures.py")
        return 0 if ok else 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}: {text.count(chr(10))} sealed certificates")
    return 0


if __name__ == "__main__":
    sys.exit(main())
