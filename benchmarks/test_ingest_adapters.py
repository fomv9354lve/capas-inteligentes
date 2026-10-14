# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Machine-context ingestion: the calibration snapshot comes from Qiskit's BackendProperties (a real artifact shape,
exercised on FakeKingston: 156 qubits, the same device family Atlas runs on), the claim skeletons come from the
pre-registration file, and every declared source is re-hashed. Nothing is typed by a model."""
import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import capas_ingest as ing  # noqa: E402
import capas_invariants as ci  # noqa: E402

qiskit_fp = pytest.importorskip("qiskit_ibm_runtime.fake_provider")


@pytest.fixture(scope="module")
def props():
    return qiskit_fp.FakeKingston().properties()


def test_backend_properties_maps_field_by_field_and_dates_every_parameter(props):
    snap = ing.backend_properties(props, layout=[0, 1, 2], job_date="2026-10-13")
    d = props.to_dict()
    assert snap["backend"] == d["backend_name"] and snap["n"] == len(d["qubits"]) == 156
    # same numbers as the artifact, no transformation beyond naming
    q0 = {p["name"]: p["value"] for p in d["qubits"][0]}
    assert snap["t1_us"]["0"] == pytest.approx(q0["T1"]) and snap["readout"]["0"] == pytest.approx(q0["readout_error"])
    assert "cz" in snap and len(snap["edges"]) == len(snap["cz"]) > 100
    assert set(snap["field_dates"]) == {"t1_us", "t2_us", "readout", "sx", "cz"}
    assert set(snap["field_dates"]["t1_us"]) == set(snap["t1_us"])          # every T1 carries its own date
    assert snap["timezone"] and snap["source"]["input_sha256"] and snap["source"]["adapter"] == "capas_ingest.backend_properties"


def test_backend_properties_invents_nothing(props):
    d = props.to_dict()
    missing = [q for q, plist in enumerate(d["qubits"]) if not any(p["name"] == "T1" for p in plist)]
    snap = ing.backend_properties(props)
    for q in missing:
        assert str(q) not in snap["t1_us"] and str(q) not in snap["field_dates"]["t1_us"]
    assert missing, "FakeKingston is expected to have at least one qubit without T1 (the no-invention case)"


def test_backend_properties_is_deterministic(props):
    a = ing.canonical_json(ing.backend_properties(props, layout=[5, 6]))
    b = ing.canonical_json(ing.backend_properties(props, layout=[5, 6]))
    assert a == b


def test_engine_reads_the_adapter_output_without_shape_hold(props):
    snap = ing.backend_properties(props, layout=[0, 1, 2], job_date="2026-10-13")
    norm, was = ci._normalize_snapshot(snap)
    assert was and set(norm["layout"]["qubits"]) == {"0", "1", "2"}
    a = ci.audit({"calibration_snapshot": snap})
    rep = a["results"]["calibration_snapshot"]
    assert rep["field_freshness"]["status"].startswith("evaluated from field_dates"), rep["field_freshness"]
    assert not any("unreadable" in h or "cannot judge" in h for h in (rep.get("holds") or [])), rep.get("holds")


def test_backend_properties_accepts_json_file(tmp_path, props):
    d = props.to_dict()
    f = tmp_path / "props.json"
    f.write_text(ing.canonical_json(d), encoding="utf-8")        # dates become ISO strings, as a saved export would
    s1, s2 = ing.backend_properties(props), ing.backend_properties(str(f))
    assert s1["t1_us"] == s2["t1_us"] and s1["cz"] == s2["cz"] and s1["field_dates"] == s2["field_dates"]


def test_prereg_skeletons_one_per_metric_and_no_results(tmp_path):
    doc = {"schema": "atlas_prereg/v1", "id": "demo_v1", "registered_utc": "2026-10-13T21:26:17+00:00",
           "supersedes": ["demo_v0"], "pinned_sha256": {"a.py": "00"},
           "metric_definitions": [{"name": "P1", "definition": "sign-flip two tails"}, {"name": "P2", "definition": "theta CI95; bands RECUPERA/PERSISTE"}]}
    f = tmp_path / "prereg.json"; f.write_text(json.dumps(doc), encoding="utf-8")
    rows = ing.prereg(f)
    assert [r["claim"]["id"] for r in rows] == ["atlas:demo_v1:P1", "atlas:demo_v1:P2"]
    assert all(r["claim"]["type"] is None and r["evidence"] == {} for r in rows)      # the adapter never picks a type
    assert rows[0]["meta"]["sources"][0]["sha256"] == ing.sha256_bytes(f.read_bytes())
    assert rows[1]["meta"]["band_words_in_definition"] is True and rows[0]["meta"]["band_words_in_definition"] is False
    doc["results"] = {"P1": "FALSADO"}
    f.write_text(json.dumps(doc), encoding="utf-8")
    with pytest.raises(ValueError):
        ing.prereg(f)


def test_verify_sources_catches_tampering(tmp_path):
    src = tmp_path / "cal.json"; src.write_text('{"a": 1}', encoding="utf-8")
    payload = ing.attach_source({"claim": {"id": "x"}, "evidence": {}}, "cal.json", adapter="test", root=tmp_path)
    assert ing.verify_sources(payload, tmp_path) == []
    src.write_text('{"a": 2}', encoding="utf-8")
    assert any("mismatch" in p for p in ing.verify_sources(payload, tmp_path))
    src.unlink()
    assert any("missing" in p for p in ing.verify_sources(payload, tmp_path))


def test_real_atlas_prereg_v5_if_present():
    f = ROOT.parent / "ATLAS" / "engine" / "benchmarks" / "preregistrations" / "mirror_e4_drift_v5.json"
    if not f.is_file():
        pytest.skip("Atlas prereg not on this machine")
    rows = ing.prereg(f)
    assert {r["meta"]["prereg"]["metric"] for r in rows} >= {"P1_deriva_layout", "P2_persistencia", "P3_decision"}
    assert rows[0]["meta"]["prereg"]["supersedes"] == ["mirror_e4_drift_v4"]
