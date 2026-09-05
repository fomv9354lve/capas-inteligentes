#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Gate the Azure capture before anything gets recreated.

Recreating a container app requires its full configuration, and Container Apps
secrets are write-only: what is not captured here is not recoverable later. This
refuses to call a dump complete unless every app carries its ingress, resources,
scale, secret names and role inventory, and the environment carries the static IP
and default domain that the DNS cutover is measured against.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from redact_capture import _is_sensitive, MARKER

ENV_NAME = "capas-env"
EXPECTED_CERTS = 3


def _load(path: Path):
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def required_apps(state_dir: Path) -> list[str]:
    """Los nombres los aporta la captura, no el código.

    Hardcodearlos publicaba nombres de cliente en un repo público y ataba el validador
    a una sola máquina: un clon sin esos ficheros fallaba siempre. La captura escribe
    apps.txt; esa es la lista autoritativa de lo que hay que validar.
    """
    f = state_dir / "apps.txt"
    if not f.is_file():
        return []
    return [ln.strip() for ln in f.read_text(encoding="utf-8").splitlines() if ln.strip()]


def validate(state_dir: Path) -> list[str]:
    fails: list[str] = []

    apps = required_apps(state_dir)
    if not apps:
        fails.append("apps.txt missing or empty — the capture recorded no apps")

    for app in apps:
        doc = _load(state_dir / f"app-{app}.json")
        if doc is None:
            fails.append(f"missing or unreadable app config: app-{app}.json")
        else:
            props = doc.get("properties", {})
            ingress = (props.get("configuration") or {}).get("ingress")
            if not ingress or ingress.get("targetPort") is None:
                fails.append(f"{app}: ingress/targetPort not captured — cannot recreate")
            containers = (props.get("template") or {}).get("containers") or []
            if not containers or not containers[0].get("resources"):
                fails.append(f"{app}: container resources not captured — cannot recreate")
            if (props.get("template") or {}).get("scale") is None:
                fails.append(f"{app}: scale not captured — cannot recreate")

        if _load(state_dir / f"secrets-{app}.json") is None:
            fails.append(f"{app}: secret names not captured (secrets-{app}.json)")
        if _load(state_dir / f"roles-{app}.json") is None:
            fails.append(f"{app}: roles inventory not captured (roles-{app}.json) — "
                         "a recreated identity loses every assignment")

    # The credential scan runs over every app-*.json actually present, not just
    # REQUIRED_APPS — the shell redaction is unconditional, so the backstop must be
    # too, or a capture against a different resource group could regress silently.
    for app_file in sorted(state_dir.glob("app-*.json")):
        app = app_file.stem[len("app-"):]
        doc = _load(app_file)
        if doc is None:
            continue
        props = doc.get("properties", {})
        for c in (props.get("template") or {}).get("containers") or []:
            for e in c.get("env") or []:
                name, value = e.get("name", ""), e.get("value")
                if value and value != MARKER and _is_sensitive(name, value):
                    fails.append(f"{app}: env {name} carries a plaintext credential value — "
                                 "the capture must redact it before this dump is committed")

    env = _load(state_dir / f"env-{ENV_NAME}.json")
    if env is None:
        fails.append(f"missing environment config: env-{ENV_NAME}.json")
    else:
        p = env.get("properties", {})
        if not p.get("staticIp"):
            fails.append("environment staticIp not captured — DNS cutover has no baseline")
        if not p.get("defaultDomain"):
            fails.append("environment defaultDomain not captured — CNAME target unknown")

    certs = _load(state_dir / f"certs-{ENV_NAME}.json")
    if certs is None:
        fails.append(f"missing certificate list: certs-{ENV_NAME}.json")
    elif len(certs) != EXPECTED_CERTS:
        fails.append(f"expected {EXPECTED_CERTS} managed certificates, captured {len(certs)}")

    if _load(state_dir / "resources.json") is None:
        fails.append("missing resource inventory: resources.json")

    return fails


def main() -> int:
    state_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "azure_state"
    fails = validate(state_dir)
    if fails:
        print("FAIL:")
        for x in fails:
            print("  -", x)
        return 1
    print(f"OK: capture at {state_dir} is complete — every app carries ingress, resources, scale, "
          "secret names and role inventory; the environment carries staticIp and defaultDomain. "
          "Safe to plan recreation against it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
