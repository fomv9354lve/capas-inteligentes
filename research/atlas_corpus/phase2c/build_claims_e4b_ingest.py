#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Atlas E4b re-coded THROUGH THE ADAPTERS (capas_ingest), to measure how much of the hand coding in
build_claims_e4b.py a machine can replace. Same inputs as the hand version plus the pre-registration file.

What a human/model still declares here, and nothing else — the MAPPING (which prereg metric feeds which CAPAS claim
type, and which fields of the sanitized analysis fill it). Every number is read from a file whose sha256 is recorded
in meta.sources; the claim ids and texts come from the prereg skeletons; the calibration snapshot is the machine
file (already produced by Atlas's qpu_cal_fetch from BackendProperties) with the layout and job date attached.

Usage: python3 build_claims_e4b_ingest.py <sanitized.json> <calibration.json> <prereg.json> <out.jsonl>"""
import hashlib, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
import capas_ingest as ing  # noqa: E402

REP12_LAYOUT = [67, 57, 65, 66, 46, 47, 63, 64, 43, 45, 44, 56]   # pre-registration mirror_e4_drift_v5 (verbatim)
ALPHA = 0.05                                                        # prereg: "alpha nominal 0.05"

# ---- the declared mapping: prereg metric -> CAPAS claim type + which sanitized fields fill the evidence ------------
# P2's band is one-sided in the prereg ("IC_inf >= 0.5 RECUPERA"); it is declared as such and the engine says what it
# can do with it. Nothing is rounded, inverted or filled in.
MAPPING = {
    "P1_deriva_layout": {"type": "statistical_confidence", "p": ("P1", "p"), "stat": ("P1", "mean_diff"), "pairs": ("P1", "pairs"),
                         "direction_rule": "any",           # P1 affirms only "F drifted" (prereg v5: not "the decision expired")
                         "calibration": True},
    "P2_persistencia": {"type": "interval_band_claim", "estimate": ("P2", "theta"), "ci": ("P2", "ci95"),
                        "band": {"low": 0.5, "high": None}, "band_label": "RECUPERA (IC_inf >= 0.5)", "resamples": 10000, "seed": 20261013},
    "P3_decision": {"type": "statistical_confidence", "p": ("P3", "p"), "stat": ("P3", "mean_diff"), "pairs": ("P3", "pairs"),
                    "direction_rule": "negative_both",      # prereg: media<0 on raw F; corrected F reported, must agree
                    "gap_field": ("P3", "gap_s"), "gap_max_s": 1800},
}


def _get(d, path):
    for k in path:
        d = d[k]
    return d


def main() -> int:
    san_p, cal_p, pre_p, out_p = map(Path, sys.argv[1:5])
    san = json.loads(san_p.read_text(encoding="utf-8"))
    cal = json.loads(cal_p.read_text(encoding="utf-8"))
    assert san["prereg_id"] == "mirror_e4_drift_v5"
    skeletons = {r["meta"]["prereg"]["metric"]: r for r in ing.prereg(pre_p)}
    jobs = san["jobs"]
    job_day = jobs["mirror_rb_e4_20261013_1528"]["timestamps"]["running"][:10]
    # the calibration file is Atlas's machine export (qpu_cal_fetch from BackendProperties); attach what the prereg fixes
    snap = {**cal, "layout": REP12_LAYOUT, "job_date": job_day, "timezone": "-06:00",
            "source": {"adapter": "atlas qpu_cal_fetch (BackendProperties)", "input_sha256": ing.sha256_bytes(cal_p.read_bytes())}}
    rows = []
    for metric, m in MAPPING.items():
        sk = skeletons[metric]
        ev = {}
        if m["type"] == "statistical_confidence":
            p, stat, pairs = _get(san, m["p"]), _get(san, m["stat"]), _get(san, m["pairs"])
            if m["direction_rule"] == "any":
                direction = True
            else:
                sec = san["P3"]["corrected"]["mean_diff"]
                gap_ok = _get(san, m["gap_field"]) <= m["gap_max_s"]
                direction = bool(gap_ok and stat < 0 and sec < 0)
            ev = {"p_value": p, "alpha": ALPHA, "effect_direction_confirmed": direction,
                  "test_statistic": {"kind": "paired_sign_flip", "value": stat, "pairs": pairs, "tails": 2}}
            if m.get("calibration"):
                ev["invariants"] = {"calibration_snapshot": snap}
        elif m["type"] == "interval_band_claim":
            lo, hi = _get(san, m["ci"])
            ev = {"estimate": _get(san, m["estimate"]), "ci_low": lo, "ci_high": hi, "ci_level": 0.95,
                  "band": m["band"], "band_pre_registered": True, "method": "bootstrap", "resamples": m["resamples"], "seed": m["seed"],
                  "n_replicates": 18}
        payload = {"schema_version": "capas-claim-payload-v3",
                   "claim": {"id": sk["claim"]["id"], "type": m["type"], "text": sk["claim"]["text"]},
                   "evidence": ev}
        # provenance travels in the ROW (schema v3 allows no `meta` inside the payload); the sealed runner re-hashes it
        row = {"claim_id": payload["claim"]["id"], "contaminado": False, "payload": payload,
               "meta": {"coder": "capas_ingest adapters + declared MAPPING (build_claims_e4b_ingest.py)", "phase": "2c-ingest",
                        "prereg": sk["meta"]["prereg"], "sources": list(sk["meta"]["sources"])}}
        ing.attach_source(row, san_p.name, adapter="sanitized analysis (Atlas qpu_drift_analysis)", root=san_p.parent)
        ing.attach_source(row, cal_p.name, adapter="atlas qpu_cal_fetch (BackendProperties)", root=cal_p.parent)
        rows.append(row)
    body = "\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows) + "\n"
    out_p.write_text(body, encoding="utf-8")
    print("claims sha256:", hashlib.sha256(body.encode()).hexdigest(), f"({len(rows)} claims)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
