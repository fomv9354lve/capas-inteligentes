# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Calibration-snapshot invariant, from Atlas's real incident (2026-10-13): a layout chosen on a
June snapshot had two CZ edges degraded x15 and x6 and a qubit at T1 = 54 us; the run came out
10x below prediction and burned QPU before anyone read the live calibration.

Law: a snapshot whose elements (or the layout's elements) break a textbook law, sit far outside
the device's own distribution, or are stale relative to the job, does not enter the triage."""
import json, os
import capas_invariants as ci

def _snap(edges, t1s, measured="2026-10-13 00:25:48"):
    return {"measured": measured,
            "qubits": {str(i): {"t1_us": t, "readout": 0.01} for i, t in enumerate(t1s)},
            "edges": {f"{i}_{i+1}": e for i, e in enumerate(edges)}}

HEALTHY = _snap([0.002, 0.0025, 0.003, 0.0022, 0.0028, 0.0021], [210, 200, 230, 190, 250, 220])

def test_healthy_snapshot_passes():
    a = ci.audit({"calibration_snapshot": HEALTHY})
    assert a["verdict"] == "PASS" and "calibration_snapshot" in a["laws_checked"]

def test_degraded_edges_x15_x6_flag():
    bad = _snap([0.002, 0.0025, 0.03, 0.0022, 0.012, 0.0021], [210, 200, 230, 190, 250, 220])
    a = ci.audit({"calibration_snapshot": bad})
    assert a["verdict"] == "FLAG"
    w = a["results"]["calibration_snapshot"]["why"]
    assert "2_3" in w and "4_5" in w and "x" in w

def test_low_t1_qubit_flags():
    bad = _snap([0.002, 0.0025, 0.003, 0.0022, 0.0028, 0.0021], [210, 200, 54, 190, 250, 220])
    a = ci.audit({"calibration_snapshot": bad})
    assert a["verdict"] == "FLAG" and "t1" in a["results"]["calibration_snapshot"]["why"].lower()

def test_layout_restricts_judgement_to_its_elements():
    bad = _snap([0.002, 0.0025, 0.03, 0.0022, 0.012, 0.0021], [210, 200, 230, 190, 250, 220])
    # layout avoids the two bad edges -> PASS; layout uses one -> FLAG
    assert ci.audit({"calibration_snapshot": {**bad, "layout": {"qubits": ["0", "1"], "edges": ["0_1"]}}})["verdict"] == "PASS"
    assert ci.audit({"calibration_snapshot": {**bad, "layout": {"qubits": ["2", "3"], "edges": ["2_3"]}}})["verdict"] == "FLAG"

def test_stale_snapshot_with_job_date_flags():
    old = {**HEALTHY, "measured": "2026-06-20 10:00:00", "job_date": "2026-10-13 12:00:00"}
    a = ci.audit({"calibration_snapshot": old})
    assert a["verdict"] == "FLAG" and "stale" in a["results"]["calibration_snapshot"]["why"].lower()

def test_textbook_law_per_row_still_applies():
    bad = _snap([0.002] * 6, [210] * 6)
    bad["qubits"]["0"]["t2_us"] = 600.0   # T2 > 2*T1 with Ramsey method -> textbook violation
    assert ci.audit({"calibration_snapshot": bad})["verdict"] == "FLAG"

def test_real_kingston_snapshot_reports_its_outliers():
    f = "/Users/kreniq/Desktop/KRENIQ/AI Projects/01. Investigacion/ATLAS/engine/benchmarks/kingston_calibration_2026-10-13_used.json"
    if not os.path.exists(f):
        return
    a = ci.audit({"calibration_snapshot": json.load(open(f))})
    r = a["results"]["calibration_snapshot"]
    assert "outliers" in r and isinstance(r["outliers"], list)


# --- Atlas's proposed ABSOLUTE policy (pending Osvaldo): edge > 1e-2, T1 < 60 us, freshness same day.
ATLAS_ABS = {"edge_max_abs": 1e-2, "t1_min_us": 60.0, "max_age_days": 0.0}

def test_absolute_edge_threshold_flags_above_1e_2_even_if_relative_passes():
    # all edges ~equally bad: relative filter sees no outlier, absolute one must still flag
    bad = _snap([0.02, 0.021, 0.019, 0.02, 0.022, 0.02], [210] * 6)
    bad["thresholds"] = ATLAS_ABS
    a = ci.audit({"calibration_snapshot": bad})
    assert a["verdict"] == "FLAG" and "1e-02" in a["results"]["calibration_snapshot"]["why"] or "0.01" in a["results"]["calibration_snapshot"]["why"]
    # relative-only policy (absolute switched off) is blind to a uniformly bad device: documents the gap
    rel_only = _snap([0.02, 0.021, 0.019, 0.02, 0.022, 0.02], [210] * 6); rel_only["thresholds"] = {"edge_max_abs": 0.0}
    assert ci.audit({"calibration_snapshot": rel_only})["verdict"] == "PASS"
    # default policy (Osvaldo 2026-10-13: absolute + relative) catches it
    assert ci.audit({"calibration_snapshot": _snap([0.02, 0.021, 0.019, 0.02, 0.022, 0.02], [210] * 6)})["verdict"] == "FLAG"

def test_absolute_t1_floor_60us_flags_59_not_61():
    for t1, want in ((59.0, "FLAG"), (61.0, "PASS")):
        s = _snap([0.002] * 6, [210, 200, t1, 190, 250, 220])
        s["thresholds"] = {"t1_min_us": 60.0, "t1_min_frac_median": 0.0}
        assert ci.audit({"calibration_snapshot": s})["verdict"] == want, t1

def test_same_day_freshness_policy():
    s = {**HEALTHY, "measured": "2026-10-12 23:00:00", "job_date": "2026-10-13 01:00:00", "thresholds": {"max_age_days": 0.0}}
    assert ci.audit({"calibration_snapshot": s})["verdict"] == "FLAG"   # different calendar day
    s = {**HEALTHY, "measured": "2026-10-13 00:25:48", "job_date": "2026-10-13 18:00:00", "thresholds": {"max_age_days": 0.0}}
    assert ci.audit({"calibration_snapshot": s})["verdict"] == "PASS"   # same day


# --- Atlas's three REAL cases (ibm_kingston 2026-10-13, mirror-RB job db6tn74lf4us73dat2sg), frozen.
# Outcomes measured by Atlas: n=12 June layout -> chi2 = 83.4 > 11.07 (5 dof), FALSIFIED; n=8 -> CONFIRMED.
_FIX = os.path.join(os.path.dirname(__file__), "fixtures", "atlas_kingston_2026-10-13.json")
_N12 = {"qubits": [69, 78, 67, 68, 88, 89, 65, 66, 87, 86, 85, 77],
        "edges": ["69_78", "78_89", "67_68", "68_69", "88_89", "65_66", "65_77", "66_67", "87_88", "86_87", "85_86", "77_85"]}
_N8 = {"qubits": [50, 29, 67, 38, 49, 57, 48, 47],
       "edges": ["29_38", "38_49", "49_50", "57_67", "48_49", "47_57", "47_48"]}

def _atlas(**extra):
    snap = json.load(open(_FIX)); snap.pop("_source", None)
    return {"calibration_snapshot": {**snap, **extra}}

def _elements(r):
    return {o["element"] for o in r["outliers"]}

def test_atlas_case1_n12_june_layout_with_jobdate_flags():
    a = ci.audit(_atlas(layout=_N12, job_date="2026-10-13"))
    r = a["results"]["calibration_snapshot"]
    assert a["verdict"] == "FLAG" and _elements(r) == {"86_87", "85_86", "87"} and r["stale_days"] is None

def test_atlas_case2_n12_june_layout_no_jobdate_flags():
    a = ci.audit(_atlas(layout=_N12))
    assert a["verdict"] == "FLAG" and _elements(a["results"]["calibration_snapshot"]) == {"86_87", "85_86", "87"}

def test_atlas_case3_n8_layout_with_jobdate_passes():
    a = ci.audit(_atlas(layout=_N8, job_date="2026-10-13"))
    assert a["verdict"] == "PASS", a["results"]["calibration_snapshot"]["why"]

def test_atlas_medians_as_stated():
    r = ci.audit(_atlas(layout=_N8, job_date="2026-10-13"))["results"]["calibration_snapshot"]["medians"]
    assert abs(r["edge_error"] - 0.00228) < 1e-5 and abs(r["t1_us"] - 209.1) < 0.1 and abs(r["readout"] - 0.0093) < 1e-4

def test_atlas_synthetic_stale_variant_flags():
    # SYNTHETIC (Atlas has no real stale run): same snapshot re-dated to June, job today
    a = ci.audit(_atlas(layout=_N8, measured="2026-06-20 10:00:00", job_date="2026-10-13"))
    assert a["verdict"] == "FLAG" and "stale" in a["results"]["calibration_snapshot"]["why"]
