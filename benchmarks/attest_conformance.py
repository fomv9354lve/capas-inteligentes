#!/usr/bin/env python3
"""CAPAS conformance ATTESTATION runner — the outsider-runnable packet builder for GOVERNANCE.md §5/§6.

Run-it-yourself, get the SAME verdict + the SAME hashes the certifier gets. Emits a content-addressed
attestation packet (to stdout) that a third party re-derives bit-for-bit at the pinned commit. No auth,
no private process, no employee in the loop — the Sonobuoy / Certified-Kubernetes mechanic (Charter §8).

    python3 benchmarks/attest_conformance.py            # human summary -> stdout
    python3 benchmarks/attest_conformance.py --json     # the attestation packet -> stdout (PR this)

Grounded in: benchmarks/conformance.py (8-item SUITE + result_hash), capas.verify_audit_hash (the public
re-derivation that POST /api/gate/verify calls; capas_api.py:102), GOVERNANCE.md §5 (self-run determinism),
§6 (mark granted only by passing §5), §8 (yearly re-certification). Writes NOTHING to disk by design.

Clone-and-run promise: this runner needs ONLY a `git clone` of the repo on the PYTHONPATH. It imports the
in-tree `capas` module directly (the same module the API and the SDK wrap). If the optional convenience
package `capas_sdk` is installed it is used; if not, the runner degrades to calling `capas.gate` /
`capas.verify_audit_hash` directly. There is no `pip install` prerequisite to reproduce the attestation.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))  # make the in-tree `capas` module importable from a bare clone

# The canonical gate fixture every attestation must verify: a stable ACCEPT whose audit_hash re-derives.
# Deterministic and machine-independent (no timing / random / network) — this is the cross-machine
# determinism witness, deliberately NOT the raw suite timing (see the result_hash caveat at the bottom).
GATE_FIXTURE = {
    "claim_type": "statistical_confidence",
    "evidence": {"p_value": 0.03, "alpha": 0.05, "effect_direction_confirmed": True},
    "claim_text": "X improves Y",
}


def _git_head() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT),
                              capture_output=True, text=True, timeout=30).stdout.strip() or "UNKNOWN"
    except Exception:
        return "UNKNOWN"


def _run_suite() -> dict:
    """Invoke the SAME suite the certifier runs and parse its machine-readable record."""
    r = subprocess.run([sys.executable, "benchmarks/conformance.py", "--json"],
                       cwd=str(ROOT), capture_output=True, text=True, timeout=900)
    try:
        return json.loads(r.stdout)
    except Exception:
        raise SystemExit("conformance.py did not emit JSON:\n" + (r.stdout or r.stderr))


# Canonical claim-payload schema the engine validates against (capas_sdk._SCHEMA). Used by the degrade
# path to build the same payload capas_sdk.gate() builds, so the audit_hash is identical either way.
_SCHEMA = "capas-claim-payload-v3"


def _gate(claim_type: str, evidence: dict, claim_text: str) -> dict:
    """Produce a gate result. Prefer the convenience SDK; degrade to the in-tree capas module if absent,
    so an outsider with only a `git clone` (no pip install of capas_sdk) can still run this.

    Both paths terminate in capas.decide_external_claim(payload) — the reference entrypoint capas_sdk.gate
    wraps — so the produced gate result (and therefore its audit_hash) is byte-identical across paths."""
    try:
        import capas_sdk  # optional convenience wrapper
        return capas_sdk.gate(claim_type, evidence, claim_text)
    except Exception:
        import capas  # always present in a clone — the module the SDK and the API both wrap
        # Replicate capas_sdk._payload(): claim.text must be non-empty or schema validation HOLDs everything.
        payload = {
            "schema_version": _SCHEMA,
            "claim": {"id": "claim", "type": claim_type,
                      "text": claim_text or claim_type or "claim"},
            "evidence": evidence or {},
        }
        return capas.decide_external_claim(payload)


def _gate_and_verify() -> dict:
    """Produce a gate result and re-derive its audit_hash via the public function /api/gate/verify uses.

    Verify-endpoint contract (capas_api.py:100-102): POST /api/gate/verify accepts EITHER a body shaped
    {"result": <gate-result>} OR a bare gate-result body (`body.get('result') or body`), and returns
    capas.verify_audit_hash(...) -> {"verified", "claimed", "recomputed", "recipe"}. This runner calls
    capas.verify_audit_hash directly, which is exactly what that endpoint invokes — so posting this packet's
    gate result to the endpoint reproduces the same {verified, recomputed} this function records.
    """
    import capas
    g = _gate(GATE_FIXTURE["claim_type"], GATE_FIXTURE["evidence"], GATE_FIXTURE["claim_text"])
    v = capas.verify_audit_hash(g)
    # Negative control: a tampered copy MUST fail to verify, proving the hash actually binds the verdict.
    tampered = dict(g)
    tampered["verdict"] = "REJECT" if g.get("verdict") != "REJECT" else "ACCEPT"
    tamper_caught = capas.verify_audit_hash(tampered).get("verified") is False
    return {
        "verdict": g.get("verdict"),
        "audit_hash": g.get("audit_hash"),
        "verified": v.get("verified"),
        "recomputed": v.get("recomputed"),
        "tamper_detected": tamper_caught,
        "recipe": v.get("recipe"),
    }


def build_packet() -> dict:
    suite = _run_suite()
    gate = _gate_and_verify()
    body = {
        "attestation_kind": "CAPAS-self-run-conformance",
        "governance_ref": "GOVERNANCE.md §5-§6 (self-run deterministic conformance; mark via §5)",
        "commit": _git_head(),
        "python": sys.version.split()[0],
        "conformant": suite.get("conformant"),
        "result_hash": suite.get("result_hash"),
        "suite": suite.get("suite"),
        "gate_fixture": GATE_FIXTURE,
        "gate_verification": gate,
        # The mark is claimable iff ALL of these hold; an adjudicator re-derives every one at `commit`.
        "claimable": bool(
            suite.get("conformant") is True
            and isinstance(suite.get("result_hash"), str)
            and gate.get("verified") is True
            and gate.get("tamper_detected") is True
        ),
        "how_to_re_derive": [
            "git checkout <commit>",
            "python3 benchmarks/conformance.py --json   # reproduce result_hash",
            "python3 benchmarks/attest_conformance.py --json   # reproduce this packet (sans packet_hash)",
            "POST the gate result to /api/gate/verify (no auth; bare result or {\"result\": ...}) "
            "OR call capas.verify_audit_hash(result)",
        ],
    }
    # Content-address the packet: the adjudicator recomputes this over `body` and confirms a match,
    # so the packet is tamper-evident with no key — same determinism-not-opinion stance as §5.
    packet_hash = "sha256:" + hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()
    return {**body, "packet_hash": packet_hash}


def main() -> int:
    p = build_packet()
    if "--json" in sys.argv:
        print(json.dumps(p, indent=2))
        return 0 if p["claimable"] else 1
    gv = p["gate_verification"]
    print("=== CAPAS CONFORMANCE ATTESTATION (run-it-yourself; the certifier re-derives this) ===")
    print(f"  commit         {p['commit']}")
    print(f"  conformant     {p['conformant']}   result_hash {p['result_hash']}")
    print(f"  gate verdict   {gv['verdict']}   audit_hash verified {gv['verified']}   "
          f"tamper_detected {gv['tamper_detected']}")
    print(f"  CLAIMABLE      {p['claimable']}")
    print(f"  packet_hash    {p['packet_hash']}")
    print("Submit the --json packet via PR. The mark attests passing exactly this — §6.")
    return 0 if p["claimable"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
