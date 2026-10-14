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

def test_default_freshness_is_one_day_after_atlas_blind_batch():
    # Atlas blind batch 2026-06: snapshot 06-22, job 06-23 -> must be fresh under the default (was stale under same-day)
    s = {**HEALTHY, "measured": "2026-06-22 09:00:00", "job_date": "2026-06-23 15:00:00"}
    assert ci.audit({"calibration_snapshot": s})["verdict"] == "PASS"
    s = {**HEALTHY, "measured": "2026-06-21 09:00:00", "job_date": "2026-06-23 15:00:00"}
    assert ci.audit({"calibration_snapshot": s})["verdict"] == "FLAG"
    # integer policy counts calendar days (06-22 23:00 -> 06-23 01:00 is 1 day, fresh); fractional policy counts real days
    s = {**HEALTHY, "measured": "2026-06-22 23:00:00", "job_date": "2026-06-23 01:00:00"}
    assert ci.audit({"calibration_snapshot": s})["verdict"] == "PASS"
    s = {**HEALTHY, "measured": "2026-06-22 23:00:00", "job_date": "2026-06-23 12:00:00", "thresholds": {"max_age_days": 0.25}}
    assert ci.audit({"calibration_snapshot": s})["verdict"] == "FLAG"

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


# --- Atlas case 4, PROSPECTIVE (2026-10-13): layout chosen BY this law on live properties, then run.
# Same circuits as the June-layout n=12 (job db6tn74lf4us73dat2sg). Law-chosen layout: job db6uisamb58s738cem4g,
# prereg mirror_rep12_2026_10_v8. Outcome: F 0.232/0.205/0.145 (d=10/12/16) vs 0.030/0.022/0.011 with the June
# layout; r/layer 15.6% -> 7.6% with equivalent physical CZ counts. PASS/FLAG separated 15.6% from 7.6%.
_FIX4 = os.path.join(os.path.dirname(__file__), "fixtures", "atlas_kingston_2026-10-13_rep12.json")             # layout-only, as Atlas's script wrote it (prereg v8)
_FIX4_FULL = os.path.join(os.path.dirname(__file__), "fixtures", "atlas_kingston_2026-10-13_rep12_fulldevice.json")  # whole device, medians over 156 qubits

def _case4_full():
    w = json.load(open(_FIX4_FULL)); return w.get("calibration_snapshot", w)

def test_atlas_case4_prospective_law_chosen_layout_passes():
    w = json.load(open(_FIX4))
    a = ci.audit({"calibration_snapshot": w["calibration_snapshot"]})
    r = a["results"]["calibration_snapshot"]
    assert a["verdict"] == "PASS" == w["law_verdict_local"] and r["outliers"] == [] and r["stale_days"] is None

def test_atlas_case4_full_device_passes_with_device_medians():
    a = ci.audit({"calibration_snapshot": _case4_full()})
    r = a["results"]["calibration_snapshot"]
    assert a["verdict"] == "PASS" and r["outliers"] == []
    # medians over the whole device, as Atlas states: cz 0.00203, T1 241.4, readout 0.0115
    assert abs(r["medians"]["edge_error"] - 0.00203) < 5e-5 and abs(r["medians"]["t1_us"] - 241.4) < 0.5 and abs(r["medians"]["readout"] - 0.0115) < 2e-4

def test_atlas_threshold_aliases_are_honoured():
    # Atlas writes edge_abs / t1_abs_us; a stricter alias value must change the verdict
    w = json.load(open(_FIX4))["calibration_snapshot"]
    strict = {**w, "thresholds": {**w["thresholds"], "edge_abs": 0.004}}   # worst edge in layout is 0.0048
    assert ci.audit({"calibration_snapshot": strict})["verdict"] == "FLAG"
    strict_t1 = {**w, "thresholds": {**w["thresholds"], "t1_abs_us": 130.0}}  # min T1 in layout is ~122
    assert ci.audit({"calibration_snapshot": strict_t1})["verdict"] == "FLAG"


# --- T2 floor (Atlas, 2026-10-13: official IBM CSV carries T2; 12 qubits < 30 us, three inside layouts that PASSED).
# Off by default until Osvaldo fixes the policy; declarable in thresholds as t2_min_frac_median / t2_min_us.
def _snap_t2(t2s, t1=210.0):
    s = _snap([0.002] * 6, [t1] * 6)
    for i, t2 in enumerate(t2s):
        s["qubits"][str(i)]["t2_us"] = t2; s["qubits"][str(i)]["t2_method"] = "echo"
    return s

def test_t2_floor_off_by_default():
    assert ci.audit({"calibration_snapshot": _snap_t2([140, 150, 19.3, 130, 160, 145])})["verdict"] == "PASS"

def test_t2_relative_floor_flags_below_median_third():
    s = _snap_t2([140, 150, 19.3, 130, 160, 145]); s["thresholds"] = {"t2_min_frac_median": 1 / 3}
    a = ci.audit({"calibration_snapshot": s})
    assert a["verdict"] == "FLAG" and {o["element"] for o in a["results"]["calibration_snapshot"]["outliers"]} == {"2"}

def test_t2_absolute_floor_flags_below_30us():
    s = _snap_t2([140, 150, 28.5, 130, 160, 145]); s["thresholds"] = {"t2_min_us": 30.0}
    assert ci.audit({"calibration_snapshot": s})["verdict"] == "FLAG"
    s["thresholds"] = {"t2_min_us": 25.0}
    assert ci.audit({"calibration_snapshot": s})["verdict"] == "PASS"


# --- declared snapshot in a shape the law cannot read: HOLD, never a silent skip (Atlas E4, 2026-10-13) ---
RAW_E4 = os.path.join(os.path.dirname(__file__), "..", "research", "atlas_corpus", "phase2b", "claims_e4_2026-10-13.jsonl")

def _raw_e4_snapshot():
    with open(RAW_E4, encoding="utf-8") as f:
        rec = json.loads(f.readline())
    return rec["payload"]["evidence"]["invariants"]["calibration_snapshot"]

def test_unreadable_snapshot_shape_holds_not_skips():
    a = ci.audit({"calibration_snapshot": {"backend": "x", "measured": "2026-10-13 11:51:12", "foo": [1, 2, 3]}})
    assert a["applicable"] and a["verdict"] == "HOLD" and "calibration_snapshot" in a["holds"]

def test_raw_ibm_device_file_is_normalized_and_judged():
    snap = _raw_e4_snapshot()
    a = ci.audit({"calibration_snapshot": snap})
    r = a["results"]["calibration_snapshot"]
    assert a["applicable"] and r["normalized_from_raw_device_file"] is True
    assert "layout (24 elements judged" in r["why"]  # 12 qubits + 12 edges inside the layout
    # the E4 layout the day of the run: worst edge 0.62 %, min T1 122 us -> PASS (Atlas's own law said PASS too)
    assert a["verdict"] == "PASS", r["why"]

def test_raw_and_canonical_shapes_agree():
    snap = _raw_e4_snapshot()
    canon = {"measured": snap["measured"], "job_date": snap["job_date"],
             "qubits": {q: {"t1_us": snap["t1_us"].get(q), "readout": snap["readout"].get(q)} for q in snap["readout"]},
             "edges": dict(snap["cz"]),
             "layout": {"qubits": [str(q) for q in snap["layout"]],
                        "edges": [k for k in snap["cz"] if set(k.split("_")) <= {str(q) for q in snap["layout"]}]}}
    a1 = ci.audit({"calibration_snapshot": snap})["results"]["calibration_snapshot"]
    a2 = ci.audit({"calibration_snapshot": canon})["results"]["calibration_snapshot"]
    assert a1["verdict"] == a2["verdict"] and a1["outliers"] == a2["outliers"] and a1["medians"] == a2["medians"]

def test_raw_snapshot_with_degraded_layout_edge_flags():
    snap = json.loads(json.dumps(_raw_e4_snapshot()))
    snap["cz"]["57_67"] = 0.03  # x~20 the device median -> the layout edge is an outlier
    a = ci.audit({"calibration_snapshot": snap})
    assert a["verdict"] == "FLAG" and "57_67" in a["results"]["calibration_snapshot"]["why"]

def test_engine_holds_accept_when_declared_snapshot_is_unreadable():
    import capas
    payload = {"schema_version": "capas-claim-payload-v3",
               "claim": {"id": "t", "type": "exact_model_solution", "text": "fit holds"},
               "evidence": {"test_statistic": {"kind": "chi2", "value": 0.93, "dof": 3, "alpha": 0.05},
                            "n_replicates": 8, "invariants": {"calibration_snapshot": {"backend": "x", "foo": 1}}}}
    r = capas.decide_external_claim(payload)
    assert r["verdict"] == "HOLD" and "could not judge" in r["reason"]


# --- per-field freshness, rule v2 (pre-specified with Atlas 2026-10-13, DEBTS C-9) ---------------------------------
E4B_CAL = os.path.join(os.path.dirname(__file__), "..", "research", "atlas_corpus", "phase2c",
                       "kingston_calibration_live_e4_20261013_1528.json")
REP12 = [67, 57, 65, 66, 46, 47, 63, 64, 43, 45, 44, 56]

def _e4b(**extra):
    with open(E4B_CAL, encoding="utf-8") as f:
        cal = json.load(f)
    return {**cal, "layout": REP12, "job_date": "2026-10-13", **extra}

def test_field_dates_are_read_and_iso_offsets_parse():
    assert ci._parse_ts("2026-10-12T23:28:34-06:00") is not None
    r = ci.audit({"calibration_snapshot": _e4b()})["results"]["calibration_snapshot"]
    ff = r["field_freshness"]
    assert ff["status"].startswith("evaluated from field_dates")
    # 7 qubits of the device carry a T1 dated 2026-10-11 (two calendar days before the job): any in the layout is stale
    assert all(s["source"] == "field_dates" for s in ff["stale"])

def test_field_dates_same_day_policy_flags_previous_evening_t1():
    r = ci.audit({"calibration_snapshot": _e4b(thresholds={"max_age_days": 0})})["results"]["calibration_snapshot"]
    fields = {s["field"] for s in r["field_freshness"]["stale"]}
    assert r["verdict"] == "HOLD" and "t1_us" in fields and "stale_field" in r["why"]
    # readout (12:36 the same day) and cz (04:08 the same day) are fresh under the same-day policy
    assert "readout" not in fields and "cz" not in fields

def test_no_field_dates_no_previous_is_a_notice_not_a_hold():
    snap = {k: v for k, v in _e4b().items() if k != "field_dates"}
    a = ci.audit({"calibration_snapshot": snap})
    assert a["verdict"] == "PASS" and a["results"]["calibration_snapshot"]["field_freshness"]["status"].startswith("not evaluable")

def _pair(prev_measured, cur_measured, job, cur_t1, prev_t1, cur_ro, prev_ro):
    prev = {"measured": prev_measured, "qubits": {str(i): {"t1_us": prev_t1[i], "readout": prev_ro[i]} for i in range(4)},
            "edges": {"0_1": 0.002, "1_2": 0.0021, "2_3": 0.0019}}
    cur = {"measured": cur_measured, "job_date": job, "previous_snapshot": prev,
           "qubits": {str(i): {"t1_us": cur_t1[i], "readout": cur_ro[i]} for i in range(4)},
           "edges": {"0_1": 0.0025, "1_2": 0.0021, "2_3": 0.0019}}
    return cur

def test_identity_inference_continuous_per_element_quantized_whole_field():
    # previous snapshot 3 days before the job; current file "measured" the day of the job
    cur = _pair("2026-10-10 02:00:00", "2026-10-13 11:51:00", "2026-10-13",
                cur_t1=[280.9, 274.7, 300.0, 310.0], prev_t1=[280.9, 274.7, 299.0, 311.0],   # qubits 0,1 identical -> stale
                cur_ro=[0.0157, 0.0133, 0.0189, 0.0201], prev_ro=[0.0157, 0.0133, 0.0189, 0.0201])  # whole field identical -> stale
    r = ci.audit({"calibration_snapshot": cur})["results"]["calibration_snapshot"]
    ff = r["field_freshness"]
    assert ff["status"].startswith("inferred by identity")
    stale = {(s["field"], s["element"]) for s in ff["stale"]}
    assert ("t1_us", "0") in stale and ("t1_us", "1") in stale and ("t1_us", "2") not in stale
    assert ("readout", "*") in stale
    assert ("edges", "1_2") in stale and ("edges", "0_1") not in stale
    assert r["verdict"] == "HOLD" and "lower bound" in r["why"]

def test_identity_inference_quantized_partial_match_does_not_count():
    cur = _pair("2026-10-10 02:00:00", "2026-10-13 11:51:00", "2026-10-13",
                cur_t1=[1, 2, 3, 4], prev_t1=[5, 6, 7, 8],
                cur_ro=[0.0157, 0.0133, 0.0190, 0.0202], prev_ro=[0.0157, 0.0133, 0.0189, 0.0201])  # 2 of 4 identical: chance
    ff = ci.audit({"calibration_snapshot": cur})["results"]["calibration_snapshot"]["field_freshness"]
    assert not any(s["field"] == "readout" for s in ff["stale"])

def test_identity_inference_needs_an_earlier_previous_snapshot():
    cur = _pair("2026-10-13 12:00:00", "2026-10-13 11:51:00", "2026-10-13", [210,220,230,240], [210,220,230,240], [.01,.01,.01,.01], [.01,.01,.01,.01])
    a = ci.audit({"calibration_snapshot": cur})
    assert a["verdict"] == "HOLD" and "not earlier" in a["summary"]

def test_field_dates_take_precedence_over_identity():
    cur = _pair("2026-10-10 02:00:00", "2026-10-13 11:51:00", "2026-10-13", [210,220,230,240], [210,220,230,240], [.01,.01,.01,.01], [.01,.01,.01,.01])
    cur["field_dates"] = {"t1_us": {str(i): "2026-10-13T08:00:00-06:00" for i in range(4)},
                          "readout": {str(i): "2026-10-13T08:00:00-06:00" for i in range(4)}}
    r = ci.audit({"calibration_snapshot": cur})["results"]["calibration_snapshot"]
    assert r["field_freshness"]["status"].startswith("evaluated from field_dates") and r["field_freshness"]["stale"] == []


def test_stale_field_holds_an_accept_but_never_rejects():
    """Decision 2026-10-13 (Atlas): a stale layout field is HOLD, not FLAG -> an ACCEPT becomes HOLD, a REJECT stays."""
    import capas
    snap = _e4b()  # T1 of layout qubit 65 dated 2026-10-11: stale under the 1-day policy
    ev = {"p_value": 7.6e-06, "alpha": 0.05, "effect_direction_confirmed": True, "invariants": {"calibration_snapshot": snap}}
    r = capas.decide_external_claim({"schema_version": "capas-claim-payload-v3",
                                     "claim": {"id": "p1", "type": "statistical_confidence", "text": "F drifted"}, "evidence": ev})
    assert r["verdict"] == "HOLD" and "stale_field" in r["reason"] and "qubit" not in r["reason"].split("stale_field")[0][-5:]
