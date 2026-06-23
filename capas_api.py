"""CAPAS live API — the thin backend that connects the tool to the REAL engine.

Stdlib only (no FastAPI/Flask, so it stays light). One server: it serves the static site
(docs/) AND exposes the deterministic engine over POST /api/{gate,reward,certificate}.
Single source of truth = capas_sdk; the front-end never reimplements the gate, so the tool
always reflects the engine (re-derivation, fail-closed, honest scope).

    python3 capas_api.py 8799      # then point ngrok at :8799
"""
from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import capas_sdk  # noqa: E402
import capas_certstore  # noqa: E402

# Hosted-product auth: if CAPAS_API_KEY is set, write/issue endpoints require it (Bearer or
# X-API-Key). Unset -> open (local dev). Read/verify of a certificate stays public by design.
_API_KEY = os.environ.get("CAPAS_API_KEY")

DOCS = ROOT / "docs"
_CTYPE = {"html": "text/html", "js": "application/javascript", "css": "text/css",
          "png": "image/png", "jpeg": "image/jpeg", "jpg": "image/jpeg", "json": "application/json",
          "svg": "image/svg+xml", "ico": "image/x-icon"}


class H(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("ngrok-skip-browser-warning", "1")

    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()

    def _authed(self) -> bool:
        if not _API_KEY:
            return True
        hdr = self.headers.get("Authorization", "")
        token = hdr[7:] if hdr.startswith("Bearer ") else self.headers.get("X-API-Key", "")
        import hmac
        return hmac.compare_digest(token or "", _API_KEY)

    def _json(self, obj, code=200):
        data = json.dumps(obj).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data))); self._cors(); self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if not self.path.startswith("/api/"):
            return self._json({"error": "not found"}, 404)
        try:
            n = int(self.headers.get("Content-Length", 0) or 0)
            body = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return self._json({"error": "bad json"}, 400)
        # /api/decide takes the FULL payload (what the Gate App pastes) -> the real engine,
        # a drop-in for the app's client-side rule().
        if self.path == "/api/decide":
            import capas
            try:
                return self._json(capas.decide_external_claim(body))
            except Exception as e:
                return self._json({"error": repr(e)}, 500)
        # verify a posted certificate record (public, no auth — anyone can check tamper-evidence)
        if self.path == "/api/certificate/verify":
            return self._json(capas_certstore.verify(body.get("record") or body))
        ct = body.get("claim_type", ""); ev = body.get("evidence", {}) or {}; txt = body.get("claim_text", "") or ct
        try:
            if self.path == "/api/gate":
                out = capas_sdk.gate(ct, ev, txt)
            elif self.path == "/api/reward":
                out = {"reward": capas_sdk.reward(ct, ev, txt)}
            elif self.path == "/api/quantum":
                out = capas_sdk.gate_quantum(body.get("row") or ev)
            elif self.path == "/api/invariants":
                out = capas_sdk.invariants(body.get("block") or ev)
            elif self.path == "/api/certificate":
                # hosted product: issue a SIGNED, PERSISTED, addressable certificate (auth-gated)
                if not self._authed():
                    return self._json({"error": "unauthorized: set Authorization: Bearer <CAPAS_API_KEY>"}, 401)
                out = capas_certstore.issue(capas_sdk.certificate(ct, ev, txt))
            else:
                return self._json({"error": "unknown endpoint"}, 404)
        except Exception as e:
            return self._json({"error": repr(e)}, 500)
        self._json(out)

    def do_GET(self):
        p = self.path.split("?")[0]
        # hosted product: retrieve a persisted certificate by id (public read + verify)
        if p.startswith("/api/certificate/"):
            cid = p[len("/api/certificate/"):]
            rec = capas_certstore.get(cid)
            if rec is None:
                return self._json({"error": "certificate not found"}, 404)
            rec["verification"] = capas_certstore.verify(rec)
            return self._json(rec)
        if p == "/api/health":
            return self._json({"status": "ok", "auth_required": bool(_API_KEY)})
        if p in ("/", ""):
            p = "/index.html"
        f = (DOCS / p.lstrip("/")).resolve()
        if not str(f).startswith(str(DOCS)) or not f.is_file():
            return self._json({"error": "not found"}, 404)
        data = f.read_bytes()
        # Freshness contract: every asset carries a content ETag and is served `no-cache`
        # (cache, but ALWAYS revalidate). After a deploy a normal reload picks up the new bytes
        # instantly — no hard-reload, no stale "missing sections". Unchanged files return 304
        # against the ETag, so revalidation stays cheap. This is what makes the deploy cycle clean.
        import hashlib
        etag = '"' + hashlib.sha256(data).hexdigest()[:16] + '"'
        if self.headers.get("If-None-Match") == etag:
            self.send_response(304); self.send_header("ETag", etag)
            self.send_header("Cache-Control", "no-cache"); self._cors(); self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Type", _CTYPE.get(f.suffix.lstrip(".").lower(), "application/octet-stream"))
        self.send_header("Cache-Control", "no-cache")
        self.send_header("ETag", etag)
        self.send_header("Content-Length", str(len(data))); self._cors(); self.end_headers()
        self.wfile.write(data)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    import os
    # PORT from env (Render/Railway/Fly/HF Spaces inject it); arg or 8799 for local.
    port = int(os.environ.get("PORT") or (sys.argv[1] if len(sys.argv) > 1 else 8799))
    # 0.0.0.0 so a host/container can route to it; localhost-only when run with --local.
    host = "127.0.0.1" if "--local" in sys.argv else "0.0.0.0"
    print(f"CAPAS live API on {host}:{port}  (static docs/ + POST /api/gate|reward|certificate)")
    ThreadingHTTPServer((host, port), H).serve_forever()
