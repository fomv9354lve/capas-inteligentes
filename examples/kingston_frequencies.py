# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Pull ibm_kingston per-qubit FREQUENCIES (and anharmonicity) via the Qiskit API — metadata
only, NO job/queue — and convert the assumed-5GHz loss-tangent BOUND into an EXACT number, plus
test the Q121 spectral-collision hypothesis against the real frequency map.

Token is read from the file only, used in-memory, never printed/committed. Saves results to
/tmp/kingston_frequencies.json for CAPAS to gate against.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

TOKEN_FILE = "/Users/kreniq/Downloads/apikey (1).json"
OUT = "/tmp/kingston_frequencies.json"


def main() -> int:
    tok = json.load(open(TOKEN_FILE))["apikey"]
    from qiskit_ibm_runtime import QiskitRuntimeService
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=tok)
    backend = service.backend("ibm_kingston")
    props = backend.properties()
    n = backend.num_qubits

    qubits = {}
    for q in range(n):
        try:
            f = props.frequency(q)          # Hz
            t1 = props.t1(q)                # s
            t2 = props.t2(q)
        except Exception:
            continue
        if not f or not t1:
            continue
        # EXACT loss tangent: tan_delta = 1 / (2*pi*f*T1)
        tan_delta = 1.0 / (2.0 * math.pi * f * t1)
        anh = None
        try:
            anh = props.qubit_property(q, "anharmonicity")[0]
        except Exception:
            pass
        qubits[q] = {"freq_hz": f, "t1_s": t1, "t2_s": t2,
                     "tan_delta": tan_delta, "anharmonicity_hz": anh}

    # spectral-collision scan over the coupling map: small |df| between coupled qubits, or a
    # neighbor sitting near this qubit's f+anharmonicity (the |1>-|2> transition) -> collision.
    cmap = backend.coupling_map
    edges = sorted({tuple(sorted(e)) for e in cmap}) if cmap else []
    collisions = []
    for a, b in edges:
        if a not in qubits or b not in qubits:
            continue
        fa, fb = qubits[a]["freq_hz"], qubits[b]["freq_hz"]
        df = abs(fa - fb)
        try:
            cz = props.gate_error("cz", [a, b])
        except Exception:
            try:
                cz = props.gate_error("ecr", [a, b])
            except Exception:
                cz = None
        # collision classes (MHz): straddling (|df|<17MHz) or near-anharmonic
        anh_a = qubits[a].get("anharmonicity_hz") or -310e6
        near_anh = abs(df - abs(anh_a)) < 30e6
        straddle = df < 17e6
        if straddle or near_anh:
            collisions.append({"edge": [a, b], "df_mhz": round(df / 1e6, 2),
                               "type": "straddle" if straddle else "near_anharmonic",
                               "cz_error": cz})

    # Q121 focus
    q121 = qubits.get(121)
    out = {
        "backend": "ibm_kingston", "n_qubits": n,
        "qubits": {str(k): v for k, v in qubits.items()},
        "spectral_collisions": collisions,
        "q121": q121,
        "tan_delta_stats": {
            "min": min((v["tan_delta"] for v in qubits.values()), default=None),
            "max": max((v["tan_delta"] for v in qubits.values()), default=None),
        },
    }
    json.dump(out, open(OUT, "w"), indent=2)
    print(f"pulled {len(qubits)} qubit frequencies; {len(collisions)} spectral-collision edges flagged")
    # report the extremes without dumping everything
    by_tan = sorted(qubits.items(), key=lambda kv: kv[1]["tan_delta"])
    best = by_tan[0]; worst = by_tan[-1]
    print(f"best material quality:  Q{best[0]} tan_d={best[1]['tan_delta']:.2e} "
          f"(f={best[1]['freq_hz']/1e9:.4f} GHz, T1={best[1]['t1_s']*1e6:.0f}us)")
    print(f"worst material quality: Q{worst[0]} tan_d={worst[1]['tan_delta']:.2e} "
          f"(f={worst[1]['freq_hz']/1e9:.4f} GHz, T1={worst[1]['t1_s']*1e6:.0f}us)")
    if q121:
        print(f"Q121: f={q121['freq_hz']/1e9:.4f} GHz, T1={q121['t1_s']*1e6:.1f}us, "
              f"tan_d={q121['tan_delta']:.2e}")
    print(f"saved -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
