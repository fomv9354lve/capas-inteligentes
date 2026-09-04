# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""The capture validator must reject an incomplete dump before anything is deleted."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ops"))
from redact_capture import MARKER, redact  # noqa: E402
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


def _with_env(d: Path, app: str, env_entry: dict) -> dict:
    doc = json.loads((d / f"app-{app}.json").read_text())
    doc["properties"]["template"]["containers"][0]["env"] = [env_entry]
    (d / f"app-{app}.json").write_text(json.dumps(doc))
    return doc


def test_plaintext_credential_env_is_caught(tmp_path):
    d = _complete(tmp_path)
    _with_env(d, "atlas", {"name": "ANALYTICS_SALT", "value": "a" * 32})
    fails = validate(d)
    assert any("atlas" in f and "ANALYTICS_SALT" in f for f in fails)


def test_redacted_marker_env_passes(tmp_path):
    d = _complete(tmp_path)
    _with_env(d, "atlas", {"name": "ANALYTICS_SALT", "value": MARKER})
    assert validate(d) == []


def test_empty_credential_env_passes(tmp_path):
    d = _complete(tmp_path)
    _with_env(d, "atlas", {"name": "ANALYTICS_SALT", "value": ""})
    assert validate(d) == []


def test_secret_ref_env_passes(tmp_path):
    d = _complete(tmp_path)
    _with_env(d, "atlas", {"name": "ANTHROPIC_API_KEY", "secretRef": "anthropic-key"})
    assert validate(d) == []


def test_redact_round_trip_is_idempotent():
    doc = _app("atlas")
    doc["properties"]["template"]["containers"][0]["env"] = [
        {"name": "ANALYTICS_SALT", "value": "a" * 32},
        {"name": "ANTHROPIC_API_KEY", "secretRef": "anthropic-key"},
        {"name": "PLAIN_CONFIG", "value": "not-a-secret"},
    ]
    doc, redacted = redact(doc)
    assert redacted == ["ANALYTICS_SALT"]
    env = doc["properties"]["template"]["containers"][0]["env"]
    assert env[0]["value"] == MARKER
    assert "value" not in env[1]
    assert env[2]["value"] == "not-a-secret"

    doc, redacted_again = redact(doc)
    assert redacted_again == []
    env = doc["properties"]["template"]["containers"][0]["env"]
    assert env[0]["value"] == MARKER
    assert env[2]["value"] == "not-a-secret"


def test_keyboard_and_salty_are_not_redacted():
    doc = _app("atlas")
    doc["properties"]["template"]["containers"][0]["env"] = [
        {"name": "KEYBOARD", "value": "qwerty-layout"},
        {"name": "SALTY", "value": "not-a-secret-either"},
    ]
    doc, redacted = redact(doc)
    assert redacted == []
    env = doc["properties"]["template"]["containers"][0]["env"]
    assert env[0]["value"] == "qwerty-layout"
    assert env[1]["value"] == "not-a-secret-either"


def test_known_credential_names_still_redacted():
    doc = _app("atlas")
    doc["properties"]["template"]["containers"][0]["env"] = [
        {"name": "ANTHROPIC_API_KEY", "value": "sk-ant-plaintext"},
        {"name": "ANALYTICS_SALT", "value": "a" * 32},
    ]
    doc, redacted = redact(doc)
    assert set(redacted) == {"ANTHROPIC_API_KEY", "ANALYTICS_SALT"}
    env = doc["properties"]["template"]["containers"][0]["env"]
    assert env[0]["value"] == MARKER
    assert env[1]["value"] == MARKER


def test_database_url_with_embedded_credentials_is_redacted():
    doc = _app("atlas")
    doc["properties"]["template"]["containers"][0]["env"] = [
        {"name": "DATABASE_URL", "value": "postgres://user:pass@host:5432/db"},
    ]
    doc, redacted = redact(doc)
    assert redacted == ["DATABASE_URL"]
    assert doc["properties"]["template"]["containers"][0]["env"][0]["value"] == MARKER


def test_database_url_without_embedded_credentials_passes():
    doc = _app("atlas")
    doc["properties"]["template"]["containers"][0]["env"] = [
        {"name": "DATABASE_URL", "value": "https://host/path"},
    ]
    doc, redacted = redact(doc)
    assert redacted == []
    assert doc["properties"]["template"]["containers"][0]["env"][0]["value"] == "https://host/path"


def test_validator_credential_scan_covers_apps_outside_required(tmp_path):
    d = _complete(tmp_path)
    extra = _app("extra-app")
    extra["properties"]["template"]["containers"][0]["env"] = [
        {"name": "ANALYTICS_SALT", "value": "a" * 32},
    ]
    (d / "app-extra-app.json").write_text(json.dumps(extra))
    fails = validate(d)
    assert any("extra-app" in f and "ANALYTICS_SALT" in f for f in fails)
