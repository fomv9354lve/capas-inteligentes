"""Analyze the XEB+purity job when it lands: per (edge, depth) compute mean F_XEB and F_purity,
the coherent fraction, the XEB-vs-depth curve, and reconcile it with CAPAS's calibration budget.

Answers the three questions in one pass:
  1. ground-truth XEB curve  (vs the inferred-20%, mean error 0.14)
  2. coherent vs incoherent  (is the hard region recalibratable or fundamental?)
  3. CAPAS cross-validation  (does the good edge beat the bad edge, as CAPAS predicted?)
Token from file, never printed. Saves /tmp/xeb_results.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import capas_quantum_physics as P

TOKEN_FILE = "/Users/kreniq/Downloads/apikey (1).json"
SUBMIT = "/tmp/xeb_submit.json"
OUT = "/tmp/xeb_results.json"


def _counts(pub):
    d = pub.data
    reg = "meas" if hasattr(d, "meas") else ("c" if hasattr(d, "c") else None)
    return getattr(d, reg).get_counts()


def main() -> int:
    sub = json.load(open(SUBMIT))
    tok = json.load(open(TOKEN_FILE))["apikey"]
    from qiskit_ibm_runtime import QiskitRuntimeService
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=tok)
    res = service.job(sub["job_id"]).result()

    # per-circuit F_xeb, F_purity
    rows = []
    for meta, pub in zip(sub["metas"], res):
        counts = _counts(pub)
        rows.append({"edge": tuple(meta["edge"]), "edge_tag": meta["edge_tag"],
                     "edge_cz": meta["edge_cz"], "depth": meta["depth"],
                     "f_xeb": P.xeb_linear_fidelity(meta["ideal_probs"], counts),
                     "f_purity": P.speckle_purity_fidelity(counts, 2)})

    # aggregate by (edge, depth)
    agg = {}
    for r in rows:
        agg.setdefault((r["edge"], r["depth"]), []).append(r)
    curves = {}
    for (edge, depth), rs in sorted(agg.items()):
        fx = sum(r["f_xeb"] for r in rs) / len(rs)
        fp = sum(r["f_purity"] for r in rs) / len(rs)
        v = P.coherent_fraction_verdict(fx, fp, depth)
        curves.setdefault(str(list(edge)), {"tag": rs[0]["edge_tag"], "cz": rs[0]["edge_cz"], "by_depth": []})
        curves[str(list(edge))]["by_depth"].append(
            {"depth": depth, "f_xeb": round(fx, 4), "f_purity": round(fp, 4),
             "coherent_fraction": v["coherent_fraction"], "verdict": v["verdict"]})

    # reconcile each edge's curve with CAPAS's calibration budget (the inference-error question)
    summary = {"job_id": sub["job_id"], "curves": curves, "reconciliation": {}}
    for edge_str, c in curves.items():
        cz = c["cz"] or 1e-3
        layer_f = (1 - cz) * (1 - 2.0e-4) ** 2          # 1 CZ + 2 SX per XEB layer (incoherent budget)
        deepest = max(c["by_depth"], key=lambda d: d["depth"])
        predicted = layer_f ** deepest["depth"]
        measured = deepest["f_xeb"]
        coh = deepest["coherent_fraction"]
        rec = P.reconcile_budget_with_measurement(measured, predicted, coh, deepest["depth"])
        # estimate kappa (correlation discount) from THIS edge's measured curve vs the naive budget
        depths_e = [d["depth"] for d in c["by_depth"]]
        xeb_e = [d["f_xeb"] for d in c["by_depth"]]
        kappa = P.estimate_kappa(depths_e, xeb_e, naive_layer_error=1 - layer_f, leave_one_out=True)
        rec["kappa_estimate"] = kappa
        rec["kappa_vs_user_0_401"] = (None if kappa.get("kappa") is None
                                      else round(abs(kappa["kappa"] - 0.401), 4))
        summary["reconciliation"][edge_str] = rec
        if kappa.get("kappa") is not None:
            print(f"    kappa (correlation discount) = {kappa['kappa']} "
                  f"(user fit 0.401, |diff| {rec['kappa_vs_user_0_401']}) "
                  f"-> depth ceiling {kappa['depth_ceiling_multiplier']}x")
        print(f"edge {edge_str:10s} ({c['tag']}, CZ {cz:.2e}): "
              f"depth {deepest['depth']} measured XEB {measured:.3f} vs budget {predicted:.3f} "
              f"-> {rec['verdict']} (coherent {coh:.0%})")
        for d in c["by_depth"]:
            print(f"    depth {d['depth']:2d}: F_xeb {d['f_xeb']:.3f}  F_purity {d['f_purity']:.3f}  "
                  f"coh {d['coherent_fraction']:.0%}  {d['verdict']}")

    # cross-validation: CAPAS predicts the LOWER-CZ edge (from calibration) should have the higher
    # deep XEB. Derive good/bad from CZ, not the tag string (robust to pinned/user edges).
    deep_by_edge = {e: max(c["by_depth"], key=lambda d: d["depth"])["f_xeb"] for e, c in curves.items()}
    cz_by_edge = {e: (c["cz"] or 1e9) for e, c in curves.items()}
    if len(curves) >= 2:
        good = min(cz_by_edge, key=cz_by_edge.get)   # CAPAS-predicted better (lower CZ)
        bad = max(cz_by_edge, key=cz_by_edge.get)
        ordering_ok = deep_by_edge[good] > deep_by_edge[bad]
        summary["capas_cross_validation"] = {
            "good_edge": good, "good_cz": cz_by_edge[good], "good_edge_deep_xeb": deep_by_edge[good],
            "bad_edge": bad, "bad_cz": cz_by_edge[bad], "bad_edge_deep_xeb": deep_by_edge[bad],
            "ordering_matches_capas_prediction": ordering_ok}
        print(f"\nCAPAS cross-validation: lower-CZ edge {good} (CZ {cz_by_edge[good]:.1e}) XEB "
              f"{deep_by_edge[good]:.3f} {'>' if ordering_ok else '<='} higher-CZ edge {bad} "
              f"(CZ {cz_by_edge[bad]:.1e}) XEB {deep_by_edge[bad]:.3f} "
              f"-> calibration prediction {'CONFIRMED' if ordering_ok else 'NOT confirmed'}")

    json.dump(summary, open(OUT, "w"), indent=2)
    print(f"\nsaved -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
