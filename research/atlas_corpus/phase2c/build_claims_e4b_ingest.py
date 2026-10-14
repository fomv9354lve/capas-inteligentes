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

# ---- the declared mapping: prereg metric -> CAPAS claim type + a results SPEC (field -> path in the sanitized file,
# or {"const": v} for what the coder declares). The adapter copies; it never computes. The one derived field (P3's
# direction, a pre-registered rule) is computed here and recorded as DERIVED next to what was read and declared.
MAPPING = {
    "P1_deriva_layout": {"type": "statistical_confidence", "calibration": True,
                         "spec": {"p_value": "P1.p", "alpha": {"const": ALPHA}, "effect_direction_confirmed": {"const": True},   # P1 affirms only "F drifted"
                                  "stat_value": "P1.mean_diff", "pairs": "P1.pairs"}},
    "P2_persistencia": {"type": "interval_band_claim",
                        "spec": {"estimate": "P2.theta", "ci": "P2.ci95", "ci_level": {"const": 0.95}, "band": {"const": {"low": 0.5, "high": None}},
                                 "band_pre_registered": {"const": True}, "method": {"const": "bootstrap"}, "resamples": {"const": 10000},
                                 "seed": {"const": 20261013}, "n_replicates": {"const": 18}}},
    "P3_decision": {"type": "statistical_confidence",
                    "spec": {"p_value": "P3.p", "alpha": {"const": ALPHA}, "stat_value": "P3.mean_diff", "pairs": "P3.pairs",
                             "gap_s": "P3.gap_s", "corrected_mean_diff": "P3.corrected.mean_diff"},
                    "derived_direction": "gap_s <= 1800 and stat_value < 0 and corrected_mean_diff < 0 (prereg v5: raw and corrected F must agree, same moment)"},
}


def _evidence_from(metric: str, m: dict, r: dict) -> dict:
    """Shape the copied fields into the claim type's evidence contract. Only renaming/nesting happens here."""
    ev, prov = dict(r["evidence"]), r["provenance"]
    if m["type"] == "statistical_confidence":
        out = {"p_value": ev["p_value"], "alpha": ev["alpha"],
               "test_statistic": {"kind": "paired_sign_flip", "value": ev["stat_value"], "pairs": ev["pairs"], "tails": 2}}
        if "effect_direction_confirmed" in ev:
            out["effect_direction_confirmed"] = ev["effect_direction_confirmed"]
        else:
            out["effect_direction_confirmed"] = ing.derived(prov, "effect_direction_confirmed", m["derived_direction"],
                                                            bool(ev["gap_s"] <= 1800 and ev["stat_value"] < 0 and ev["corrected_mean_diff"] < 0))
        return out
    lo, hi = ev["ci"]
    return {"estimate": ev["estimate"], "ci_low": lo, "ci_high": hi, "ci_level": ev["ci_level"], "band": ev["band"],
            "band_pre_registered": ev["band_pre_registered"], "method": ev["method"], "resamples": ev["resamples"], "seed": ev["seed"],
            "n_replicates": ev["n_replicates"]}


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
        r = ing.results(san_p, m["spec"], source_label=san_p.name)
        ev = _evidence_from(metric, m, r)
        if m.get("calibration"):
            ev["invariants"] = {"calibration_snapshot": snap}
        payload = {"schema_version": "capas-claim-payload-v3",
                   "claim": {"id": sk["claim"]["id"], "type": m["type"], "text": sk["claim"]["text"]},
                   "evidence": ev}
        # provenance travels in the ROW (schema v3 allows no `meta` inside the payload); the sealed runner re-hashes it
        row = {"claim_id": payload["claim"]["id"], "contaminado": False, "payload": payload,
               "meta": {"coder": "capas_ingest adapters + declared MAPPING (build_claims_e4b_ingest.py)", "phase": "2c-ingest",
                        "prereg": sk["meta"]["prereg"], "sources": list(sk["meta"]["sources"]),
                        "results_provenance": {k: r["provenance"][k] for k in ("read", "declared", "derived") if k in r["provenance"]}}}
        ing.attach_source(row, san_p.name, adapter="sanitized analysis (Atlas qpu_drift_analysis)", root=san_p.parent)
        ing.attach_source(row, cal_p.name, adapter="atlas qpu_cal_fetch (BackendProperties)", root=cal_p.parent)
        rows.append(row)
    body = "\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows) + "\n"
    out_p.write_text(body, encoding="utf-8")
    print("claims sha256:", hashlib.sha256(body.encode()).hexdigest(), f"({len(rows)} claims)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
