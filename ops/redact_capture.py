#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Redact plaintext credential-shaped env values from a captured app document.

`containerapp show` returns env vars verbatim. A credential routed through
`secretRef` is safe to publish; one written as a plain `value` is not, and this
dump is committed. Redaction happens at capture time so the artifact is safe by
construction rather than safe by review.

The marker is deliberately loud: a reader must be able to tell a redacted value
from an empty one.
"""
from __future__ import annotations

import re

# Un nombre se parte en tokens por _ - . y se compara token completo: así KEY casa con
# ANTHROPIC_API_KEY pero no con KEYBOARD, y SALT con ANALYTICS_SALT pero no con SALTY.
_TOKEN = r"(?:^|[_\-.])(?:%s)(?:[_\-.]|$)"

CREDENTIAL_NAME = re.compile(
    _TOKEN % "SECRET|SECRETS|KEY|KEYS|APIKEY|TOKEN|PASSWORD|PASSWD|PWD|SALT|CREDENTIAL|CREDENTIALS|PRIVATE", re.I
)

# Un nombre tipo URL solo es sensible si el VALOR lleva credenciales incrustadas.
# Redactar toda URL perdería config pública y necesaria (p.ej. INVITE_REDIRECT_URL).
URLISH_NAME = re.compile(_TOKEN % "URL|URI|DSN|CONNECTION|CONNSTR|CONN|ENDPOINT", re.I)
EMBEDDED_CREDENTIAL = re.compile(r"://[^/@\s]+:[^/@\s]+@")

MARKER = "[REDACTED-BY-CAPTURE]"


def _is_sensitive(name: str, value: str) -> bool:
    if CREDENTIAL_NAME.search(name):
        return True
    return bool(URLISH_NAME.search(name) and EMBEDDED_CREDENTIAL.search(value))


def redact(doc: dict) -> tuple[dict, list[str]]:
    """Redact in place and return (doc, names redacted). Idempotent."""
    redacted: list[str] = []
    containers = (doc.get("properties", {}).get("template", {}) or {}).get("containers") or []
    for c in containers:
        for e in c.get("env") or []:
            name, value = e.get("name", ""), e.get("value")
            if not value or value == MARKER:
                continue
            if not _is_sensitive(name, value):
                continue
            e["value"] = MARKER
            redacted.append(name)
    return doc, redacted


def main() -> int:
    import json
    import sys

    path = sys.argv[1]
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    doc, names = redact(doc)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2)
        fh.write("\n")
    if names:
        print(f"  redacted in {path}: {', '.join(names)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
