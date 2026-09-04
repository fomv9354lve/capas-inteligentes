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

CREDENTIAL_NAME = re.compile(
    r"(SECRET|KEY|TOKEN|PASSWORD|PASSWD|SALT|CONNECTION|CONN_STR|DSN|CREDENTIAL)", re.I
)
MARKER = "[REDACTED-BY-CAPTURE]"


def redact(doc: dict) -> tuple[dict, list[str]]:
    """Redact in place and return (doc, names redacted). Idempotent."""
    redacted: list[str] = []
    containers = (doc.get("properties", {}).get("template", {}) or {}).get("containers") or []
    for c in containers:
        for e in c.get("env") or []:
            name, value = e.get("name", ""), e.get("value")
            if not CREDENTIAL_NAME.search(name):
                continue
            if not value or value == MARKER:
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
