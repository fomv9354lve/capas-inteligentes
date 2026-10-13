# SPDX-License-Identifier: Apache-2.0
"""HEAD must answer like GET minus the body (status + headers). Until 2026-10-13 the server returned 501 to HEAD,
so the documented post-deploy check (`curl -sI`) could never have returned 200 for the capas app."""
import http.client, threading
from http.server import ThreadingHTTPServer
import capas_api


def _serve():
    srv = ThreadingHTTPServer(("127.0.0.1", 0), capas_api.H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def test_head_matches_get_status_and_etag():
    srv = _serve()
    try:
        c = http.client.HTTPConnection("127.0.0.1", srv.server_port, timeout=10)
        c.request("GET", "/index.html"); g = c.getresponse(); gbody = g.read()
        c.request("HEAD", "/index.html"); h = c.getresponse(); hbody = h.read()
        assert g.status == 200 and h.status == 200
        assert hbody == b"" and len(gbody) > 1000
        assert h.getheader("ETag") == g.getheader("ETag")
        assert h.getheader("Content-Length") == g.getheader("Content-Length")
        c.request("HEAD", "/api/health"); assert c.getresponse().status == 200
        c.request("HEAD", "/nope.html"); r = c.getresponse(); r.read(); assert r.status == 404
    finally:
        srv.shutdown()
