# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Verify the hosted certificate API end-to-end against a REAL running server: issue a signed +
persisted certificate, retrieve it by id, verify the signature, detect tampering, and enforce
auth. Boots capas_api on an ephemeral port in-process (stdlib http.client), no network.
"""
from __future__ import annotations

import http.client
import json
import os
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _req(port, method, path, body=None, headers=None):
    c = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    c.request(method, path, body=json.dumps(body) if body is not None else None,
              headers={"Content-Type": "application/json", **(headers or {})})
    r = c.getresponse()
    data = json.loads(r.read() or b"{}")
    c.close()
    return r.status, data


def run() -> int:
    # isolate the cert store + require an API key for issuance
    os.environ["CAPAS_DATA_DIR"] = "/tmp/capas_certs_test"
    os.environ["CAPAS_API_KEY"] = "test-key-123"
    os.environ["CAPAS_SIGNING_SECRET"] = "test-secret"
    import importlib
    import capas_api
    importlib.reload(capas_api)
    from http.server import ThreadingHTTPServer

    srv = ThreadingHTTPServer(("127.0.0.1", 0), capas_api.H)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    time.sleep(0.2)

    checks = []
    fin = {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0, "metric_period_match": True}
    issue_body = {"claim_type": "financial_metric_claim", "evidence": fin, "claim_text": "Q3"}

    try:
        # 1. issuance without auth -> 401
        st, _ = _req(port, "POST", "/api/certificate", issue_body)
        checks.append(("issue without API key -> 401", st == 401))

        # 2. issuance with auth -> signed + persisted record with an id
        st, rec = _req(port, "POST", "/api/certificate", issue_body,
                       {"Authorization": "Bearer test-key-123"})
        cid = rec.get("certificate_id")
        checks.append((f"issue with API key -> signed cert id={str(cid)[:12]}…",
                       st == 200 and bool(cid) and "signature" in rec))

        # 3. retrieve by id (public) and the server self-verifies it
        st, got = _req(port, "GET", f"/api/certificate/{cid}")
        checks.append(("retrieve by id -> found + verification.valid",
                       st == 200 and got.get("verification", {}).get("valid") is True))

        # 4. tamper detection: alter the certificate, signature must fail
        tampered = json.loads(json.dumps(rec))
        tampered["certificate"]["verdict"] = "FORGED-ACCEPT"
        st, ver = _req(port, "POST", "/api/certificate/verify", {"record": tampered})
        checks.append(("tampered certificate -> verify.valid is False", ver.get("valid") is False))

        # 5. untampered record verifies true
        st, ver2 = _req(port, "POST", "/api/certificate/verify", {"record": rec})
        checks.append(("original record -> verify.valid is True", ver2.get("valid") is True))

        # 6. health + the new gate endpoints still work
        st, h = _req(port, "GET", "/api/health")
        checks.append(("health reports auth_required=True", h.get("auth_required") is True))
        st, q = _req(port, "POST", "/api/quantum", {"row": {"t1_us": 11.2, "t2_us": 23.44}})
        checks.append(("/api/quantum gates T2>2T1 -> FLAG", q.get("verdict") == "FLAG"))
    finally:
        srv.shutdown()
        os.environ.pop("CAPAS_API_KEY", None)

    ok = all(c for _, c in checks)
    for label, c in checks:
        print(f"{'OK ' if c else 'XX '}{label}")
    print("HOSTED CERTIFICATE API: pass (signed, persisted, tamper-evident, auth-gated issuance)"
          if ok else "HOSTED API: FAILURES")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
