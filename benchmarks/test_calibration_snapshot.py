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
