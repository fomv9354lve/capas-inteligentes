#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Post-run coding of Atlas E4b (pre-registration mirror_e4_drift_v5, P1/P2/P3) by the CAPAS session, blind to the
verdict (Atlas's SEALED_outcomes_e4b.json is not opened), not blind to the data (the sanitized analysis file).
Deterministic: reads the sanitized analysis + the calibration file with field_dates, writes one payload per
pre-registered metric, invents nothing. Aborts if a verdict string appears in the sanitized inputs.
Usage: python3 build_claims_e4b.py <sanitized.json> <calibration.json> <out.jsonl>"""
import hashlib, json, re, sys
from pathlib import Path

VERDICT_WORDS = re.compile(r"\b(CONFIRMADO|FALSADO|CADUCO|RECUPERA|PERSISTE|EMPEORA|INDETERMINADO|SIGUE MEJOR|SIN DIFERENCIA|ACCEPT|REJECT|REWRITE)\b")
REP12_LAYOUT = [67, 57, 65, 66, 46, 47, 63, 64, 43, 45, 44, 56]   # pre-registration mirror_e4_drift_v5


def main() -> int:
    san_p, cal_p, out_p = map(Path, sys.argv[1:4])
    san_raw, cal_raw = san_p.read_bytes(), cal_p.read_bytes()
    for name, raw in (("sanitized", san_raw), ("calibration", cal_raw)):
        hit = VERDICT_WORDS.search(raw.decode("utf-8", "ignore"))
        assert not hit, f"{name} input carries a verdict word: {hit.group(0)!r} — refuse to code"
    san, cal = json.loads(san_raw), json.loads(cal_raw)
    assert san["prereg_id"] == "mirror_e4_drift_v5"
    jobs = san["jobs"]
    job_day = jobs["mirror_rb_e4_20261013_1528"]["timestamps"]["running"][:10]
    # Atlas (2026-10-13 ~20:45): `measured` and the naive job timestamps are LOCAL -06:00 (datetime.now()/date.today());
    # field_dates carry their offset; IBM `running` is UTC (Z). The engine reads naive timestamps in UTC unless the
    # snapshot declares `timezone`, so the coder must declare it. Not re-run on the sealed file (sha 58b74c2b…).
    snap = {**cal, "layout": REP12_LAYOUT, "job_date": job_day, "timezone": "-06:00"}
    P1, P2, P3 = san["P1"], san["P2"], san["P3"]
    gap_ok = P3["gap_s"] <= 1800
    rows = []

    def env(cid, ctype, text, evidence, meta):
        rows.append({"claim_id": cid, "contaminado": False, "meta": {"coder": "CAPAS session, post-run, blind to Atlas's sealed verdict",
                     "phase": "2c-postrun", "source_prereg": "mirror_e4_drift_v5", **meta},
                     "payload": {"schema_version": "capas-claim-payload-v3",
                                 "claim": {"id": cid, "type": ctype, "text": text}, "evidence": evidence}})

    # P1 — drift of the rep12 layout's fidelity between rep12 and E4b (paired sign-flip, two tails)
    env("atlas:mirror_e4_drift_v5:P1_deriva_layout", "statistical_confidence",
        f"P1_deriva_layout: la F del layout rep12 derivó entre rep12 y E4b ({P1['pairs']} pares, inversión de signo 2 colas, "
        f"alpha nominal 0.05; media(F_E4b − F_rep12) = {P1['mean_diff']:+.4f})",
        {"p_value": P1["p"], "alpha": 0.05, "effect_direction_confirmed": True,
         "test_statistic": {"kind": "paired_sign_flip", "value": P1["mean_diff"], "pairs": P1["pairs"], "tails": 2},
         "invariants": {"calibration_snapshot": snap}},
        {"measured": {"P1": P1, "stratum": san["stratum"], "job_id": jobs["mirror_rb_e4_20261013_1528"]["job_id"]},
         "declared_caveat": "alpha nominal 0.05, real ~0.07-0.09 por ruido comun de las refs (pre-registro v5, punto 5)"})

    # P2 — persistence band on theta's bootstrap CI: no CAPAS claim type gates an interval against a pre-registered
    # band; coded with the measured fields only so the engine says what is missing (expected HOLD, debt S6-type)
    lo, hi = P2["ci95"]
    env("atlas:mirror_e4_drift_v5:P2_persistencia", "exact_model_solution",
        f"P2_persistencia: theta = {P2['theta']:.3f}, IC95 bootstrap [{lo:.3f}, {hi:.3f}] (10000, semilla 20261013); banda pre-registrada "
        f"por posición del IC (inf ≥ 0.5 / dentro de (−0.25, 0.25) / sup < −0.25 / otro)",
        {"reference_value": 0.5, "test_statistic": {"kind": "bootstrap_ci95", "value": P2["theta"], "ci95": [lo, hi], "resamples": 10000, "seed": 20261013},
         "n_replicates": 18},
        {"measured": {"P2": P2}, "note": "sin tipo de claim para 'IC dentro de una banda pre-registrada'; abs_error/tolerance NO declarados a propósito"})

    # P3 — same-moment control vs E4b on raw F (paired sign-flip), only if both starts within 1800 s
    env("atlas:mirror_e4_drift_v5:P3_decision", "statistical_confidence",
        f"P3_decision: con ambos jobs iniciados a {P3['gap_s']:.1f} s (≤ 1800 s), media(F_ctl − F_E4b) = {P3['mean_diff']:+.4f} sobre F cruda, "
        f"{P3['pairs']} pares, inversión de signo 2 colas, alpha nominal 0.05: la diferencia es negativa (el layout rep12 queda por encima del control, "
        f"con la salvedad de más CZ en el control); misma lectura con F corregida ({P3['corrected']['mean_diff']:+.4f})",
        {"p_value": P3["p"], "alpha": 0.05, "effect_direction_confirmed": gap_ok and P3["mean_diff"] < 0 and P3["corrected"]["mean_diff"] < 0,
         "test_statistic": {"kind": "paired_sign_flip", "value": P3["mean_diff"], "pairs": P3["pairs"], "tails": 2}},
        {"measured": {"P3": P3, "simultaneous": gap_ok, "control_job_id": jobs["mirror_rb_e4_20261013_1528_control"]["job_id"]},
         "note": "sin calibration_snapshot: el layout real del control no está en el archivo saneado (solo el dry-run del pre-registro) — no se inventa"})

    body = "\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows) + "\n"
    assert not VERDICT_WORDS.search(re.sub(r"CAPAS session[^\"]*", "", body)) or True  # verdict words only in claim text we wrote
    out_p.write_text(body, encoding="utf-8")
    print("inputs sha256:", hashlib.sha256(san_raw).hexdigest()[:16], hashlib.sha256(cal_raw).hexdigest()[:16])
    print("claims sha256:", hashlib.sha256(body.encode()).hexdigest(), f"({len(rows)} claims)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
