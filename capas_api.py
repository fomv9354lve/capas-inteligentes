"""CAPAS live API — the thin backend that connects the tool to the REAL engine.

Stdlib only (no FastAPI/Flask, so it stays light). One server: it serves the static site
(docs/) AND exposes the deterministic engine over POST /api/{gate,reward,certificate}.
Single source of truth = capas_sdk; the front-end never reimplements the gate, so the tool
always reflects the engine (re-derivation, fail-closed, honest scope).

    python3 capas_api.py 8799      # then point ngrok at :8799
"""
from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import capas_sdk  # noqa: E402

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
        ct = body.get("claim_type", ""); ev = body.get("evidence", {}) or {}; txt = body.get("claim_text", "") or ct
        try:
            if self.path == "/api/gate":
                out = capas_sdk.gate(ct, ev, txt)
            elif self.path == "/api/reward":
                out = {"reward": capas_sdk.reward(ct, ev, txt)}
            elif self.path == "/api/certificate":
                out = capas_sdk.certificate(ct, ev, txt)
            else:
                return self._json({"error": "unknown endpoint"}, 404)
        except Exception as e:
            return self._json({"error": repr(e)}, 500)
        self._json(out)

    def do_GET(self):
        p = self.path.split("?")[0]
        if p in ("/", ""):
            p = "/index.html"
        f = (DOCS / p.lstrip("/")).resolve()
        if not str(f).startswith(str(DOCS)) or not f.is_file():
            return self._json({"error": "not found"}, 404)
        data = f.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", _CTYPE.get(f.suffix.lstrip(".").lower(), "application/octet-stream"))
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
