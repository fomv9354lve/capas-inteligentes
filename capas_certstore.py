"""CAPAS certificate store — the hosted-product layer: issue a SIGNED, PERSISTED, re-derivable
admissibility certificate (the audit artifact a regulated buyer purchases), retrieve it by id,
and VERIFY it for tamper-evidence. Stdlib only (hmac/hashlib/json), no DB dependency.

The signature binds the certificate CONTENT — it proves the artifact was issued by CAPAS and not
altered. It does NOT certify the claim is true (that is the GIGO ceiling): it certifies that THIS
verdict was deterministically produced from THIS evidence by THIS engine version.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
from pathlib import Path
from typing import Any

ALGO = "HMAC-SHA256"
KEY_ID = os.environ.get("CAPAS_KEY_ID", "capas-dev-key")


def _secret() -> bytes:
    # Production sets CAPAS_SIGNING_SECRET; a fixed dev secret keeps local runs reproducible.
    return os.environ.get("CAPAS_SIGNING_SECRET", "capas-dev-secret").encode()


def _store_dir() -> Path:
    d = Path(os.environ.get("CAPAS_DATA_DIR", str(Path(__file__).resolve().parent / "_certs")))
    d.mkdir(parents=True, exist_ok=True)
    return d


def _canonical(obj: Any) -> bytes:
    """Stable serialization so the signature is reproducible (sorted keys, no whitespace drift)."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()


def sign(obj: Any, secret: bytes | None = None) -> str:
    return hmac.new(secret or _secret(), _canonical(obj), hashlib.sha256).hexdigest()


def issue(certificate: dict[str, Any], capas_version: str = "0.3.0",
          persist: bool = True) -> dict[str, Any]:
    """Wrap a CAPAS certificate into a signed, addressable record. The id is content-derived
    (sha256 of the certificate + a nonce) so it is unguessable and collision-resistant."""
    nonce = os.urandom(8).hex()
    cert_id = hashlib.sha256(_canonical(certificate) + nonce.encode()).hexdigest()[:32]
    body = {"certificate_id": cert_id, "capas_version": capas_version,
            "key_id": KEY_ID, "algo": ALGO, "certificate": certificate, "nonce": nonce}
    body["signature"] = sign({k: body[k] for k in ("certificate_id", "capas_version", "key_id",
                                                    "algo", "certificate", "nonce")})
    if persist:
        (_store_dir() / f"{cert_id}.json").write_text(json.dumps(body, indent=2, default=str))
    return body


def get(certificate_id: str) -> dict[str, Any] | None:
    f = _store_dir() / f"{(certificate_id or '').replace('/', '')}.json"
    if not f.is_file():
        return None
    return json.loads(f.read_text())


def verify(record: dict[str, Any]) -> dict[str, Any]:
    """Recompute the signature over the record's content and compare — tamper-evident."""
    if not isinstance(record, dict) or "signature" not in record:
        return {"valid": False, "reason": "no signature on record"}
    expected = sign({k: record.get(k) for k in ("certificate_id", "capas_version", "key_id",
                                                "algo", "certificate", "nonce")})
    valid = hmac.compare_digest(expected, str(record.get("signature", "")))
    return {"valid": valid, "key_id": record.get("key_id"), "algo": record.get("algo"),
            "reason": "signature matches the certificate content" if valid
                      else "signature does NOT match — the certificate was altered or signed by another key"}
