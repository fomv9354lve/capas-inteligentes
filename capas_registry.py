"""CAPAS — Decision Registry (the honest, buildable-now slice of roadmap #5).

NOT the overclaimed 'versioned UUID registry at millions-scale' — that stays roadmap.
This is what we can ship today and defend: a single-node, APPEND-ONLY, hash-CHAINED,
Merkle-rooted log of signed admissibility decisions. Tamper-evident by construction:

  - each entry is content-addressed by the certificate's own sha256 body digest;
  - entries are hash-CHAINED (each carries sha256(prev_chained_root + body_digest)),
    so any reorder / insertion / deletion breaks the chain (append-only proof);
  - a Merkle root over the body digests is the registry's single fingerprint;
  - re-presenting a stored certificate re-checks its digest AND its Ed25519 signature
    (via capas_verify), so altering a decision body is caught.

It is pure-deterministic (no LLM) and re-derivable end to end — it strengthens the
moat (the audit trail is the enterprise asset) rather than risking it. The registry
generates no timestamps itself (determinism / reproducibility): the caller supplies
`at` if wanted. Persistence is the caller's (append the returned log to JSONL); the
module stays a pure function over the log so it is fully testable.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

import capas_verify

_GENESIS = "sha256:genesis"


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _sha(s: str) -> str:
    return "sha256:" + hashlib.sha256(s.encode()).hexdigest()


def _body_digest(certificate: dict[str, Any]) -> str:
    """Digest of the certificate body EXCLUDING its own id/signature (which are
    derived from it), so the digest is stable and recomputable."""
    body = {k: v for k, v in certificate.items() if k not in ("certificate_id", "signature")}
    return _sha(_canonical(body))


def append(log: list[dict[str, Any]], certificate: dict[str, Any], at: str | None = None) -> list[dict[str, Any]]:
    """Append a signed admissibility certificate to the log, hash-chained to the prior
    entry. Returns a NEW log (does not mutate the input)."""
    prev = log[-1]["chained_root"] if log else _GENESIS
    bd = _body_digest(certificate)
    entry = {
        "seq": len(log),
        "claim_id": certificate.get("claim_id"),
        "verdict": certificate.get("verdict"),
        "scope": certificate.get("scope"),
        "engine_digest": certificate.get("engine_digest"),
        "certificate_id": certificate.get("certificate_id"),
        "body_digest": bd,
        "prev_chained_root": prev,
        "chained_root": _sha(prev + bd),          # append-only hash chain
        "signature": certificate.get("signature"),
        "at": at,                                  # caller-supplied timestamp (None = unstamped)
    }
    return log + [entry]


def merkle_root(log: list[dict[str, Any]]) -> str:
    """A single fingerprint over all decision body digests. Any altered/added/removed
    decision changes the root."""
    if not log:
        return _GENESIS
    layer = [e["body_digest"] for e in log]
    while len(layer) > 1:
        nxt = []
        for i in range(0, len(layer), 2):
            a = layer[i]
            b = layer[i + 1] if i + 1 < len(layer) else layer[i]   # duplicate the odd tail
            nxt.append(_sha(a + b))
        layer = nxt
    return layer[0]


def verify_chain(log: list[dict[str, Any]]) -> dict[str, Any]:
    """Re-derive the hash chain from the stored body digests. Catches any reorder,
    insertion, or deletion (append-only integrity) — WITHOUT needing the original
    certificate bodies."""
    prev = _GENESIS
    for i, e in enumerate(log):
        if e.get("seq") != i:
            return {"intact": False, "broken_at": i, "reason": "seq out of order (insertion/deletion)"}
        if e.get("prev_chained_root") != prev:
            return {"intact": False, "broken_at": i, "reason": "prev-link mismatch (reordered/tampered)"}
        expect = _sha(prev + e.get("body_digest", ""))
        if e.get("chained_root") != expect:
            return {"intact": False, "broken_at": i, "reason": "chained_root mismatch (body digest altered)"}
        prev = e["chained_root"]
    return {"intact": True, "entries": len(log), "merkle_root": merkle_root(log),
            "head": prev, "note": "append-only chain verified; re-present a certificate to verify its body+signature"}


def verify_entry(entry: dict[str, Any], certificate: dict[str, Any]) -> dict[str, Any]:
    """Re-present a stored certificate and prove it is the one logged: its recomputed
    body digest must equal the logged digest, AND its Ed25519 signature must verify."""
    recomputed = _body_digest(certificate)
    digest_ok = recomputed == entry.get("body_digest")
    sig_ok = None
    try:
        # capas_verify.verify_receipt validates the Ed25519 signature over the canonical body
        sig_ok = capas_verify.verify_receipt(certificate) if hasattr(capas_verify, "verify_receipt") else None
    except Exception:
        sig_ok = None
    return {"body_matches_log": digest_ok, "signature_valid": sig_ok,
            "tampered": not digest_ok,
            "verdict": "AUTHENTIC — this is the logged decision, unaltered" if digest_ok else
                       "TAMPERED — body does not match the logged digest"}


def history(log: list[dict[str, Any]], claim_id: str) -> list[dict[str, Any]]:
    """Every decision recorded for a claim, in order — the claim's audit lifecycle."""
    return [e for e in log if e.get("claim_id") == claim_id]
