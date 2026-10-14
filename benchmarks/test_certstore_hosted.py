# SPDX-License-Identifier: Apache-2.0
"""Incident 2026-10-14: production signed certificates with the public development secret and issued them without
authentication. These tests lock the fix: hosted mode refuses to sign with the dev secret, refuses to validate a
dev-key certificate, rejects a foreign key id, and the API process refuses to start hosted without its secrets."""
import importlib, os, subprocess, sys
from pathlib import Path
import pytest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _store(monkeypatch, **env):
    for k in ("CAPAS_HOSTED", "CAPAS_SIGNING_SECRET", "CAPAS_KEY_ID"):
        monkeypatch.delenv(k, raising=False)
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    import capas_certstore
    return importlib.reload(capas_certstore)


def test_local_dev_still_reproducible(monkeypatch, tmp_path):
    cs = _store(monkeypatch, CAPAS_DATA_DIR=str(tmp_path))
    rec = cs.issue({"verdict": "HOLD"})
    assert rec["key_id"] == "capas-dev-key" and cs.verify(rec)["valid"]


def test_hosted_refuses_to_sign_with_public_secret(monkeypatch, tmp_path):
    cs = _store(monkeypatch, CAPAS_HOSTED="1", CAPAS_DATA_DIR=str(tmp_path))
    with pytest.raises(cs.SigningNotConfigured):
        cs.issue({"verdict": "ACCEPT"})
    cs = _store(monkeypatch, CAPAS_HOSTED="1", CAPAS_SIGNING_SECRET="capas-dev-secret", CAPAS_KEY_ID="prod-1", CAPAS_DATA_DIR=str(tmp_path))
    with pytest.raises(cs.SigningNotConfigured):
        cs.issue({"verdict": "ACCEPT"})


def test_hosted_rejects_forged_dev_key_certificate(monkeypatch, tmp_path):
    dev = _store(monkeypatch, CAPAS_DATA_DIR=str(tmp_path))
    forged = dev.issue({"verdict": "ACCEPT"}, persist=False)          # what anyone can do with the public secret
    cs = _store(monkeypatch, CAPAS_HOSTED="1", CAPAS_SIGNING_SECRET="x" * 48, CAPAS_KEY_ID="prod-1", CAPAS_DATA_DIR=str(tmp_path))
    v = cs.verify(forged)
    assert v["valid"] is False and "development key" in v["reason"]


def test_hosted_signs_and_verifies_with_private_key_and_rejects_old_keys(monkeypatch, tmp_path):
    cs = _store(monkeypatch, CAPAS_HOSTED="1", CAPAS_SIGNING_SECRET="s" * 48, CAPAS_KEY_ID="prod-1", CAPAS_DATA_DIR=str(tmp_path))
    rec = cs.issue({"verdict": "HOLD"}, persist=False)
    assert rec["key_id"] == "prod-1" and cs.verify(rec)["valid"]
    cs2 = _store(monkeypatch, CAPAS_HOSTED="1", CAPAS_SIGNING_SECRET="t" * 48, CAPAS_KEY_ID="prod-2", CAPAS_DATA_DIR=str(tmp_path))
    assert cs2.verify(rec)["valid"] is False                          # rotation revokes everything issued before


def test_api_refuses_to_start_hosted_without_secrets():
    env = {k: v for k, v in os.environ.items() if not k.startswith("CAPAS_")}
    env.update(CAPAS_HOSTED="1", PORT="0")
    r = subprocess.run([sys.executable, str(ROOT / "capas_api.py")], env=env, capture_output=True, text=True, timeout=60)
    assert r.returncode == 78 and "REFUSING to start in hosted mode" in r.stderr
