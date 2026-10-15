# SPDX-License-Identifier: Apache-2.0
"""PLAN_v3 engine rules (owner 2026-10-14: "implementa las 9"): provenance inside decide(), AI-use declaration,
guard band, retraction snapshot, field-level pre-registration adherence, calibrator; plus the rule table as data."""
import hashlib, json, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import capas, capas_rules, capas_ingest, capas_invariants  # noqa: E402


def P(ev, ctype="exact_model_solution", text="F(3,4) matches the closed form", **root):
    return {"schema_version": "capas-claim-payload-v3", "claim": {"id": "t", "type": ctype, "text": text}, "evidence": ev, **root}


OK = {"abs_error": 0.3, "tolerance": 1.0}


def d(p):
    return capas.decide_external_claim(p)


def test_baseline_accept_with_notices():
    r = d(P(dict(OK)))
    assert r["verdict"] == "ACCEPT"
    assert any("ai_use_declared: not declared" in n for n in r["notices"])
    assert any("uncertainty: not declared" in n for n in r["notices"])


def test_provenance_no_root_holds(monkeypatch):
    monkeypatch.delenv("CAPAS_SOURCE_ROOT", raising=False)
    r = d(P(dict(OK), meta={"sources": [{"path": "a.json", "sha256": "0" * 64}]}))
    assert r["verdict"] == "HOLD" and "no CAPAS_SOURCE_ROOT" in r["reason"]


def test_provenance_match_and_mismatch(tmp_path, monkeypatch):
    f = tmp_path / "res.json"; f.write_text('{"x": 1}')
    h = hashlib.sha256(f.read_bytes()).hexdigest()
    monkeypatch.setenv("CAPAS_SOURCE_ROOT", str(tmp_path))
    ok = d(P(dict(OK), meta={"sources": [{"path": "res.json", "sha256": h}]}))
    assert ok["verdict"] == "ACCEPT" and "re-hashed under CAPAS_SOURCE_ROOT and match" in ok["reason"]
    bad = d(P(dict(OK), meta={"sources": [{"path": "res.json", "sha256": "f" * 64}]}))
    assert bad["verdict"] == "HOLD" and "hash differs" in bad["reason"]
    esc = d(P(dict(OK), meta={"sources": [{"path": "../etc/passwd", "sha256": h}]}))
    assert esc["verdict"] == "HOLD" and "absent" in esc["reason"]


def test_provenance_never_raises_reject(tmp_path, monkeypatch):
    monkeypatch.delenv("CAPAS_SOURCE_ROOT", raising=False)
    r = d(P({"abs_error": 3.0, "tolerance": 1.0}, meta={"sources": [{"path": "a", "sha256": "0" * 64}]}))
    assert r["verdict"] == "REJECT"


def test_ai_use_declared_shape():
    r = d(P({**OK, "ai_use_declared": {"tool": "Claude", "purpose": "coding evidence fields", "phase": "extraction"}}))
    assert r["verdict"] == "ACCEPT" and not any("ai_use_declared" in n for n in r["notices"])
    assert d(P({**OK, "ai_use_declared": "none"}))["verdict"] == "ACCEPT"
    bad = d(P({**OK, "ai_use_declared": {"tool": "Claude"}}))
    assert bad["verdict"] == "HOLD" and bad["schema_errors"]


def test_guard_band_holds_only_when_declared():
    assert d(P({"abs_error": 0.95, "tolerance": 1.0}))["verdict"] == "ACCEPT"
    r = d(P({"abs_error": 0.95, "tolerance": 1.0, "abs_error_u": 0.05, "coverage_factor": 2}))
    assert r["verdict"] == "HOLD" and "guard band" in r["reason"]
    far = d(P({"abs_error": 0.2, "tolerance": 1.0, "abs_error_u": 0.05, "coverage_factor": 2}))
    assert far["verdict"] == "ACCEPT"
    rej = d(P({"abs_error": 1.05, "tolerance": 1.0, "abs_error_u": 0.05}))
    assert rej["verdict"] == "REJECT"     # downgrade-only: a REJECT is never softened


def test_retraction_snapshot(tmp_path, monkeypatch):
    ev = {**OK, "cited_dois": ["10.1/abc"]}
    assert d(P(ev))["verdict"] == "HOLD"
    snap = {"source": "Retraction Watch", "date": "2026-10-01", "sha256": "a" * 64}
    assert d(P({**ev, "retraction_snapshot": snap, "cited_doi_retracted": False}))["verdict"] == "ACCEPT"
    hit = d(P({**ev, "retraction_snapshot": snap, "cited_doi_retracted": True}))
    assert hit["verdict"] == "HOLD" and "retracted" in hit["reason"]
    # with a readable file under the source root the engine computes the flag itself
    f = tmp_path / "rw.csv"; f.write_text("10.1/ABC,2025-01-01\n10.9/zzz,2024\n")
    monkeypatch.setenv("CAPAS_SOURCE_ROOT", str(tmp_path))
    snap2 = {**snap, "path": "rw.csv", "sha256": hashlib.sha256(f.read_bytes()).hexdigest()}
    lie = d(P({**ev, "retraction_snapshot": snap2, "cited_doi_retracted": False}))
    assert lie["verdict"] == "HOLD" and "10.1/abc" in lie["reason"]


def test_prereg_field_adherence():
    pre = {"alpha": 0.05, "effect_direction_confirmed": True}
    ev = {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True, "prereg": pre}
    assert d(P(ev, "statistical_confidence", "the treatment lowers blood pressure"))["verdict"] == "ACCEPT"
    dev = d(P({**ev, "alpha": 0.1}, "statistical_confidence", "the treatment lowers blood pressure"))
    assert dev["verdict"] == "REWRITE" and "alpha" in dev["reason"]
    om = d(P({**ev, "prereg": {**pre, "n_replicates": 40}}, "statistical_confidence", "the treatment lowers blood pressure"))
    assert om["verdict"] == "REWRITE" and "n_replicates (not reported)" in om["reason"]


def test_proof_rules_exercised():
    base = {"claim_scope": "bounded", "steps_all_valid": True, "load_bearing_step_identified": False, "uniform_bound_proven": False}
    assert d(P(base, "proof_admissibility", "Lemma 2 holds"))["verdict"] == "REJECT"
    assert d(P({**base, "steps_all_valid": False, "load_bearing_step_identified": True}, "proof_admissibility", "Lemma 2 holds"))["verdict"] == "REJECT"
    u = d(P({**base, "load_bearing_step_identified": True, "claim_scope": "universal"}, "proof_admissibility", "for all n the bound holds"))
    assert u["verdict"] == "REWRITE"


def test_calibrator_and_guard_band_in_snapshot():
    try:
        snap = capas_ingest.backend_properties({"backend_name": "x", "qubits": [], "gates": []}, calibrator={"kind": "automated", "tool": "qiskit-experiments"})
        assert snap["calibrator"] == {"kind": "automated", "tool": "qiskit-experiments"}
        assert "not declared" in capas_ingest.backend_properties({"qubits": [], "gates": []})["calibrator"]
    except Exception as exc:  # pragma: no cover
        raise AssertionError(exc)
    row = {"t1_us": 100.0, "t2_us": 199.0, "readout": 0.01, "t1_us_u": 5.0, "t2_us_u": 5.0}
    r = capas_invariants.check_calibration_snapshot({"calibration_snapshot": {"qubits": {"0": row, "1": {"t1_us": 100.0, "readout": 0.01}}}})
    assert r["verdict"] == "HOLD" and "guard band" in r["why"]
    r2 = capas_invariants.check_calibration_snapshot({"calibration_snapshot": {"qubits": {"0": {"t1_us": 100.0, "t2_us": 120.0, "readout": 0.01},
                                                                                          "1": {"t1_us": 100.0, "readout": 0.01}}}})
    assert r2["uncertainty"] == "uncertainty: not declared"


def test_certificate_fields_and_rule_trace():
    r = d(P(dict(OK)))
    assert r["rules_fired"] and capas_rules.replay(r["rules_fired"]) == "ACCEPT"
    assert r["rule_table_sha256"] == capas_rules.table_sha256()
    assert r["audit_hash_recipe"] == "v2" and capas.reproduce_audit_hash(r) == r["audit_hash"]
    assert r["would_have_failed_if"], "an ACCEPT names what would have failed it"
    h = d(P({"tolerance": 1.0}))
    assert h["verdict"] == "HOLD" and h["hold_class"] == "field_absent"


def test_reject_and_hold_license_nothing():
    """Re-audit fb52d8c: 55 REJECT and 9 HOLD fixtures carried the raw claim text as licensed_claim."""
    rej = d(P({"abs_error": 3.0, "tolerance": 1.0}))
    hold = d(P({"tolerance": 1.0}))
    bad = d({"schema_version": "capas-claim-payload-v3", "claim": {"id": "x", "type": "exact_model_solution", "text": "t"}, "evidence": "no"})
    assert rej["verdict"] == "REJECT" and rej["licensed_claim"] is None
    assert hold["verdict"] == "HOLD" and hold["licensed_claim"] is None
    assert bad["verdict"] == "HOLD" and bad["licensed_claim"] is None
    for r in (rej, hold, bad):
        assert r["admissibility_certificate"]["lattice"]["reuse_boundary"] in capas.REUSE_BOUNDARY_BY_VERDICT[r["verdict"]]
