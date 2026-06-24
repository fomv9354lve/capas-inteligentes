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
          "svg": "image/svg+xml", "ico": "image/x-icon", "md": "text/plain; charset=utf-8",
          "txt": "text/plain; charset=utf-8"}


def _reason_code(verdict: str, gate_out: dict, re_derivable_hold: bool = False) -> str:
    """Machine-readable reason taxonomy so a caller distinguishes WHY, not just the verdict — turns a bare
    HOLD into 'you omitted a field' vs 'the engine rejects everything'. (Audit attack #4.)"""
    if verdict == "ACCEPT":
        return "evidence_licenses_claim"
    if verdict == "REWRITE":
        return "overclaim_rewrite_to_licensed_wording"
    if verdict == "REJECT":
        return "evidence_contradicts_claim"
    if verdict == "HOLD":
        if re_derivable_hold:
            return "evidence_declared_but_not_re_derivable"   # certificate's stricter bar
        if gate_out.get("schema_errors"):
            return "input_schema_invalid"                     # wrong type / unknown field / bad value (carries a fix)
        return "missing_required_evidence" if (gate_out.get("missing_fields") or []) else "evidence_insufficient"
    return "unknown"


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

    def _json(self, obj, code=200, surface=None):
        data = json.dumps(obj).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json")
        if surface:  # which API surface answered (gate=verdict, certificate=strict signed) — discoverability
            self.send_header("X-CAPAS-Surface", surface)
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
                d = capas.decide_external_claim(body)
                return self._json({"surface": "decide", **d} if isinstance(d, dict) else d, surface="decide")
            except Exception as e:
                return self._json({"error": repr(e)}, 500)
        # verify a posted certificate record (public, no auth — anyone can check tamper-evidence)
        if self.path == "/api/certificate/verify":
            return self._json(capas_certstore.verify(body.get("record") or body))
        ct = body.get("claim_type", ""); ev = body.get("evidence", {}) or {}; txt = body.get("claim_text", "") or ct
        surface = None
        try:
            if self.path == "/api/gate":
                surface = "gate"
                g = capas_sdk.gate(ct, ev, txt)
                out = {"surface": "gate", "reason_code": _reason_code(g.get("verdict"), g), **g}
            elif self.path == "/api/reward":
                out = {"reward": capas_sdk.reward(ct, ev, txt)}
            elif self.path == "/api/quantum":
                out = capas_sdk.gate_quantum(body.get("row") or ev)
            elif self.path == "/api/invariants":
                out = capas_sdk.invariants(body.get("block") or ev)
            elif self.path == "/api/certificate":
                # hosted product: issue a SIGNED, PERSISTED, addressable certificate (auth-gated).
                # Made self-explanatory (discoverability): the verdict is top-level AND we surface the
                # GATE verdict beside it so the gate-ACCEPT / certificate-HOLD duality is never read as a
                # bug. The certificate stays STRICT (re-derivable only) — we make it legible, not softer.
                if not self._authed():
                    return self._json({"error": "unauthorized: set Authorization: Bearer <CAPAS_API_KEY>"}, 401)
                surface = "certificate"
                cert = capas_sdk.certificate(ct, ev, txt)
                g = capas_sdk.gate(ct, ev, txt)
                gate_v = g.get("verdict")
                cert_v = cert.get("verdict")
                rderiv = (cert_v == "HOLD" and gate_v != "HOLD")  # the strict re-derivability bar caused it
                out = {
                    "surface": "certificate",
                    "surface_strictness": "requires RE-DERIVABLE evidence (e.g. raw_data to recompute the "
                                          "number); declared-only values are not enough to ACCEPT here",
                    "verdict": cert_v,
                    "reason_code": _reason_code(cert_v, g, re_derivable_hold=rderiv),
                    "verdict_reason": cert.get("headline_action") or cert.get("headline"),
                    "gate_verdict": gate_v,
                    "gate_reason_code": _reason_code(gate_v, g),
                    "note": f"The GATE (POST /api/gate) decides on DECLARED evidence and returned "
                            f"'{gate_v}'. This CERTIFICATE additionally requires the evidence be re-derivable, "
                            f"so a gate ACCEPT can be a certificate HOLD until you attach raw_data / "
                            f"computation inputs / a registry entry. By design — see GET /api/status.",
                    "certificate": capas_certstore.issue(cert),
                }
            else:
                return self._json({"error": "unknown endpoint"}, 404)
        except Exception as e:
            return self._json({"error": repr(e)}, 500)
        self._json(out, surface=surface)

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
        if p == "/api/status":
            # Discoverability cornerstone: a cold evaluator hitting this GET learns which surface returns
            # the verdict, why the certificate is stricter, and gets copy-paste payloads that reproduce
            # all four verdicts — so nobody mistakes the certificate's strictness for a non-discriminating
            # engine (the "Cold Evaluator Test"). No LLM in the verdict.
            return self._json({
                "service": "CAPAS — deterministic claim-admissibility engine (no language model in the verdict)",
                "the_verdict_endpoint": "POST /api/gate  (or /api/decide) — returns ACCEPT / REWRITE / REJECT / HOLD",
                "surfaces": {
                    "POST /api/gate": "THE VERDICT. Decides on the DECLARED structured evidence. The primary, "
                                      "discriminating endpoint — start here.",
                    "POST /api/decide": "Same engine; takes the full Gate-App payload.",
                    "POST /api/certificate": "A SIGNED, STRICTER artifact: it additionally requires the evidence "
                                             "be RE-DERIVABLE (e.g. raw_data to recompute a p-value). A gate "
                                             "ACCEPT can be a certificate HOLD until you attach re-derivable "
                                             "evidence — by design ('re-derive more than you trust'), not a bug.",
                    "POST /api/certificate/verify": "Check a posted certificate's tamper-evidence.",
                    "GET /api/requirements": "Pre-flight: ?claim_type=<type> returns the exact required/optional "
                                             "evidence fields, their types, and a fillable template — learn what to "
                                             "supply BEFORE submitting, so a HOLD is never a guessing game.",
                },
                "verdicts": ["ACCEPT", "REWRITE", "REJECT", "HOLD"],
                "reason_code_taxonomy": {
                    "evidence_licenses_claim": "ACCEPT — the evidence licenses the claim as worded",
                    "overclaim_rewrite_to_licensed_wording": "REWRITE — threshold passes but the claim over-states it",
                    "evidence_contradicts_claim": "REJECT — the evidence refutes the claim (e.g. p > alpha)",
                    "missing_required_evidence": "HOLD — a required evidence field was not supplied",
                    "input_schema_invalid": "HOLD — payload failed schema validation (wrong type / unknown field / bad value); see schema_errors + resolution (each error names its fix, and did_you_mean catches typos)",
                    "evidence_insufficient": "HOLD — present but not enough to decide",
                    "evidence_declared_but_not_re_derivable": "HOLD (certificate only) — declared, but not re-derivable; supply raw_data",
                },
                "every_hold_ships_a_resolution": "Every HOLD response carries a machine-readable `resolution` (and `did_you_mean` for typos): the exact fields/types/examples or corrections that, applied without changing the facts, move it off HOLD. A HOLD is a waypoint, never a dead end.",
                "reproduce_all_four_on_/api/gate": {
                    "ACCEPT":  {"claim_type": "statistical_confidence", "evidence": {"p_value": 0.03, "alpha": 0.05, "effect_direction_confirmed": True}, "claim_text": "X improves Y"},
                    "REJECT":  {"claim_type": "statistical_confidence", "evidence": {"p_value": 0.20, "alpha": 0.05, "effect_direction_confirmed": True}, "claim_text": "X improves Y"},
                    "REWRITE": {"claim_type": "statistical_confidence", "evidence": {"p_value": 0.03, "alpha": 0.05, "effect_direction_confirmed": False}, "claim_text": "X improves Y"},
                    "HOLD":    {"claim_type": "statistical_confidence", "evidence": {"p_value": 0.03}, "claim_text": "X improves Y (missing required field -> HOLD)"},
                },
            })
        if p == "/api/requirements":
            # A3: pre-flight contract introspection. ?claim_type=<type>[&anchor_mode=<mode>]
            from urllib.parse import urlparse, parse_qs
            import capas
            q = parse_qs(urlparse(self.path).query)
            ct = (q.get("claim_type") or [""])[0]
            am = (q.get("anchor_mode") or [None])[0]
            if not ct:
                return self._json({
                    "endpoint": "GET /api/requirements?claim_type=<type>[&anchor_mode=<mode>]",
                    "purpose": "Returns the exact required/optional evidence fields, their types, and a fillable "
                               "template for a claim type — so you know what to supply BEFORE submitting.",
                    "claim_types": sorted(capas.CLAIM_TYPE_REGISTRY),
                }, surface="requirements")
            req = capas.requirements_for_claim(ct, am)
            if req is None:
                return self._json({"error": f"unknown claim_type {ct!r}",
                                   "claim_types": sorted(capas.CLAIM_TYPE_REGISTRY)}, 404, surface="requirements")
            return self._json(req, surface="requirements")
        if p in ("/", ""):
            # Routing por host (one-ecosystem scheme):
            #   krenniq.com / www.krenniq.com  -> landing KRENIQ (front door, las 2 herramientas)
            #   capas.krenniq.com              -> la herramienta CAPAS (cuando se bindee el subdominio)
            #   capas.lemonground...azure      -> la herramienta CAPAS (host crudo de Azure)
            # APEX-only para la landing: 'capas.krenniq.com' contiene 'krenniq.com' como substring, así
            # que un `in` lo mandaría al landing por error. Match exacto del ápex (sin puerto).
            host = (self.headers.get("Host") or "").lower().split(":")[0]
            p = "/krenniq.html" if host in ("krenniq.com", "www.krenniq.com") else "/index.html"
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
