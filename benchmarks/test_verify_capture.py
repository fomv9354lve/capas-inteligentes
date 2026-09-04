# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""The capture validator must reject an incomplete dump before anything is deleted."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ops"))
from verify_capture import REQUIRED_APPS, validate  # noqa: E402


def _app(name: str) -> dict:
    return {
        "name": name,
        "identity": {"type": "SystemAssigned", "principalId": "p-" + name},
        "properties": {
            "configuration": {"ingress": {"targetPort": 8000, "external": True}},
            "template": {
                "containers": [{"image": "acr/x:1", "resources": {"cpu": 0.5, "memory": "1Gi"}}],
                "scale": {"minReplicas": 1, "maxReplicas": 1},
            },
        },
    }


def _complete(tmp: Path) -> Path:
    d = tmp / "azure_state"
    d.mkdir()
    for a in REQUIRED_APPS:
        (d / f"app-{a}.json").write_text(json.dumps(_app(a)))
        (d / f"secrets-{a}.json").write_text("[]")
        (d / f"roles-{a}.json").write_text("[]")
    (d / "env-capas-env.json").write_text(json.dumps(
        {"properties": {"staticIp": "20.232.76.107", "defaultDomain": "x.eastus.azurecontainerapps.io"}}))
    (d / "certs-capas-env.json").write_text(json.dumps([{"name": "c1"}, {"name": "c2"}, {"name": "c3"}]))
    (d / "resources.json").write_text("[]")
    return d


def test_complete_capture_passes(tmp_path):
    assert validate(_complete(tmp_path)) == []


def test_missing_app_is_caught(tmp_path):
    d = _complete(tmp_path)
    (d / "app-teoria.json").unlink()
    fails = validate(d)
    assert any("teoria" in f for f in fails)


def test_missing_role_inventory_is_caught(tmp_path):
    d = _complete(tmp_path)
    (d / "roles-capas.json").unlink()
    fails = validate(d)
    assert any("roles" in f and "capas" in f for f in fails)


def test_app_without_ingress_port_is_caught(tmp_path):
    d = _complete(tmp_path)
    bad = json.loads((d / "app-atlas.json").read_text())
    bad["properties"]["configuration"]["ingress"] = None
    (d / "app-atlas.json").write_text(json.dumps(bad))
    fails = validate(d)
    assert any("atlas" in f and "ingress" in f for f in fails)


def test_env_without_static_ip_is_caught(tmp_path):
    d = _complete(tmp_path)
    (d / "env-capas-env.json").write_text(json.dumps({"properties": {"defaultDomain": "x"}}))
    fails = validate(d)
    assert any("staticIp" in f for f in fails)
