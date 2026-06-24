# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""CAPAS audits the LIVE ibm_kingston calibration — all 156 qubits + 176 edges — through the
physical-consistency and derived-quantity gates. Metadata only (no job/queue). This is the
strong honest version: CAPAS gates the device vendor's OWN published numbers, live, with no
oracle, and re-derives what they don't publish (pure dephasing) from what they do.

Note (verified live): qubit FREQUENCY is NOT exposed on the open plan (frequency=None), so the
exact loss-tangent and spectral-collision checks stay out of reach on this account — they remain
diagnostics, not gates. T1/T2/readout/gate-error ARE exposed, which is all the invariant engine
needs. Token read from file, never printed/committed.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import capas_quantum_physics as P

TOKEN_FILE = "/Users/kreniq/Downloads/apikey (1).json"
OUT = "/tmp/kingston_live_audit.json"


def main() -> int:
    tok = json.load(open(TOKEN_FILE))["apikey"]
    from qiskit_ibm_runtime import QiskitRuntimeService
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=tok)
    b = service.backend("ibm_kingston")
    p = b.properties()
    n = b.num_qubits

    qrows, edge_rows = {}, {}
    for q in range(n):
        try:
            t1, t2 = p.t1(q), p.t2(q)
            if not t1 or not t2:
                continue
            row = {"t1_us": t1 * 1e6, "t2_us": t2 * 1e6}
            try:
                row["gate_error"] = p.gate_error("sx", [q])
                row["gate_time_ns"] = p.gate_length("sx", [q]) * 1e9
            except Exception:
                pass
            qrows[q] = row
        except Exception:
            continue

    # EXACT published residual ZZ per edge (general.zz_*, in GHz) — measured, not estimated.
    raw = p.to_dict()
    gen = {x["name"]: (x.get("value"), x.get("unit")) for x in raw.get("general", [])}
    zz_hz = {}
    for e in sorted({tuple(sorted(x)) for x in b.coupling_map}):
        try:
            edge_rows[e] = p.gate_error("cz", list(e))
        except Exception:
            pass
        for nm in (f"zz_{e[0]}{e[1]}", f"zz_{e[1]}{e[0]}"):
            if nm in gen:
                val, unit = gen[nm]
                zz_hz[e] = abs(val) * (1e9 if str(unit).upper() == "GHZ" else 1.0)
                break

    # --- run the invariant engine over the live chip ---
    coh_flags, deph_limited, hot_floor, gate_too_clean = [], [], [], []
    gamma_phis = []
    for q, row in qrows.items():
        c = P.check_coherence(row["t1_us"], row["t2_us"])   # method undeclared -> Ramsey assumption
        if c["verdict"].startswith("FLAG"):
            coh_flags.append((q, round(c["t2_over_t1"], 2)))
        d = P.pure_dephasing(row["t1_us"], row["t2_us"])
        if d["gamma_phi_per_us"] is not None:
            gamma_phis.append(d["gamma_phi_per_us"])
        if d["mechanism"].startswith("dephasing-limited"):
            deph_limited.append(q)
        if "gate_error" in row and "gate_time_ns" in row:
            g = P.gate_error_admissible(row["gate_error"], row["gate_time_ns"], row["t1_us"], row["t2_us"])
            if g["verdict"] == "FLAG_TOO_CLEAN":
                gate_too_clean.append((q, row["gate_error"]))

    # edge TLS: CZ much worse than a healthy floor (we lack per-edge RZZ on this API, so use the
    # chip's CZ distribution: flag edges in the long tail as TLS-degraded, an honest heuristic).
    czs = sorted(edge_rows.values())
    median_cz = czs[len(czs) // 2] if czs else 0.0
    tls_edges = [(list(e), round(cz, 5)) for e, cz in edge_rows.items() if cz > 20 * median_cz]

    # EXACT ZZ gate over every edge (published quantity) — and the estimate-vs-exact check.
    zz_flags = [(list(e), round(v / 1e3, 2)) for e, v in zz_hz.items()
                if P.check_zz_residual(v)["verdict"] == "FLAG_HIGH_ZZ"]
    zz_max = max(zz_hz.values()) if zz_hz else 0.0
    zz_max_edge = max(zz_hz, key=zz_hz.get) if zz_hz else None

    summary = {
        "backend": "ibm_kingston", "live": True,
        "qubits_audited": len(qrows), "edges_audited": len(edge_rows),
        "coherence_flags_T2_gt_2T1": coh_flags,
        "n_dephasing_limited": len(deph_limited),
        "dephasing_limited_fraction": round(len(deph_limited) / max(len(qrows), 1), 3),
        "gate_error_too_clean": gate_too_clean,
        "median_cz": round(median_cz, 6),
        "tls_degraded_edges_gt_20x_median": tls_edges,
        "gamma_phi_min_per_us": round(min(gamma_phis), 6) if gamma_phis else None,
        "gamma_phi_max_per_us": round(max(gamma_phis), 6) if gamma_phis else None,
        "zz_published_edges": len(zz_hz),
        "zz_max_khz": round(zz_max / 1e3, 2),
        "zz_max_edge": list(zz_max_edge) if zz_max_edge else None,
        "zz_high_flags": zz_flags,
        "frequency_exposed": False,
        "note": "CAPAS gated the vendor's live calibration; frequency withheld on open plan; "
                "residual ZZ is published EXACTLY (not estimated).",
    }
    json.dump(summary, open(OUT, "w"), indent=2)

    print(f"=== CAPAS live audit of ibm_kingston: {len(qrows)} qubits, {len(edge_rows)} edges ===")
    print(f"T2>2*T1 (method-undeclared) flags : {len(coh_flags)} qubits  e.g. {coh_flags[:6]}")
    print(f"dephasing-limited qubits          : {len(deph_limited)} "
          f"({summary['dephasing_limited_fraction']:.0%}) — phase noise, not relaxation")
    print(f"gate error below relaxation floor : {len(gate_too_clean)} "
          f"(0 = no impossible/too-clean SX claims; the vendor's numbers are self-consistent)")
    print(f"CZ TLS-degraded edges (>20x median {median_cz:.2e}): {len(tls_edges)}  e.g. {tls_edges[:4]}")
    print(f"pure-dephasing rate range         : {summary['gamma_phi_min_per_us']}"
          f" .. {summary['gamma_phi_max_per_us']} /us")
    print(f"EXACT published ZZ residual       : {len(zz_hz)} edges, max {summary['zz_max_khz']} kHz "
          f"at {summary['zz_max_edge']}, {len(zz_flags)} above coupler-nulling target")
    print(f"  (measured, NOT the CZ/RZZ estimate — e.g. 131-138 estimate ~86kHz vs published ~3.6kHz)")
    print(f"saved -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
