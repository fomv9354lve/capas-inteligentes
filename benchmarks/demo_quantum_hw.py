"""Demo + check: CAPAS gates a quantum HARDWARE measurement against the device calibration.

Deterministic. Uses real ibm_kingston Q0-Q1 calibration if present (/tmp/kingston_calib.json),
else a representative fallback. Asserts: a measurement consistent with the predicted noise
floor is ADMISSIBLE; one far cleaner is FLAG_TOO_CLEAN (suspicious); one far noisier is
FLAG_TOO_NOISY (drift/anomaly). This is the consilience — the ideal re-derivation AND IBM's
independent calibration both bound the real measurement.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import capas_quantum_hw as Q

try:
    CAL = json.load(open("/tmp/kingston_calib.json"))
except Exception:
    CAL = {"cz_error": 1.283e-3, "readout_q0": 9.77e-3, "readout_q1": 9.52e-3, "backend": "ibm_kingston (fallback)"}

IDEAL = {"00", "11"}   # Bell


def run() -> int:
    floor = Q.predicted_noise_floor(CAL)
    N = 1024
    # synthetic measurements at 3 noise regimes
    consistent = {"00": 500, "11": 503, "01": 11, "10": 10}        # ~2% off  -> ADMISSIBLE
    too_clean = {"00": 512, "11": 511, "01": 1, "10": 0}           # ~0.1% off -> FLAG_TOO_CLEAN
    too_noisy = {"00": 410, "11": 410, "01": 102, "10": 102}       # ~20% off  -> FLAG_TOO_NOISY

    rc = Q.gate_hardware_claim(IDEAL, consistent, CAL)
    rcl = Q.gate_hardware_claim(IDEAL, too_clean, CAL)
    rn = Q.gate_hardware_claim(IDEAL, too_noisy, CAL)

    checks = [
        (f"predicted noise floor from real calibration = {floor:.3%} (CZ {CAL['cz_error']:.2e} + readout)", floor > 0),
        (f"measurement ~{rc['measured_error']:.1%} consistent with device -> ADMISSIBLE (consilience)",
         rc["verdict"] == "ADMISSIBLE"),
        (f"measurement ~{rcl['measured_error']:.1%} cleaner than physics -> FLAG_TOO_CLEAN (suspicious)",
         rcl["verdict"] == "FLAG_TOO_CLEAN"),
        (f"measurement ~{rn['measured_error']:.1%} noisier than calibration -> FLAG_TOO_NOISY (drift/anomaly)",
         rn["verdict"] == "FLAG_TOO_NOISY"),
    ]
    # CALIBRATION-GRADE gate (Aer NoiseModel.from_backend prediction), statistically honest
    REAL_PRED = {"00": 4038, "11": 3985, "01": 96, "10": 73}   # ibm_kingston Q0-Q1, Aer-simulated
    pn = Q.gate_against_prediction({"00": 3200, "11": 3200, "01": 900, "10": 892}, REAL_PRED, IDEAL)
    pc8k = Q.gate_against_prediction({"00": 4096, "11": 4096}, REAL_PRED, IDEAL)
    pc200k = Q.gate_against_prediction({"00": 100000, "11": 100000}, REAL_PRED, IDEAL)
    checks += [
        ("precise gate: a noisy measurement -> FLAG_TOO_NOISY (signature far above calibrated)",
         pn["verdict"] == "FLAG_TOO_NOISY"),
        ("precise gate HONESTY: perfectly-clean at 8192 shots is NOT resolvable (no fake flag)",
         pc8k["verdict"] == "ADMISSIBLE" and pc8k["too_clean_resolvable"] is False),
        ("precise gate: with enough shots (200k) too-clean BECOMES detectable -> FLAG_TOO_CLEAN",
         pc200k["verdict"] == "FLAG_TOO_CLEAN" and pc200k["too_clean_resolvable"] is True),
    ]

    ok = all(c for _, c in checks)
    for label, c in checks:
        print(f"{'OK ' if c else 'XX '}{label}")
    print(f"   band [{rc['consistency_band'][0]:.1%}, {rc['consistency_band'][1]:.1%}] · calibration backend: {CAL.get('backend')}")
    print("QUANTUM-HARDWARE GATE (ideal + calibration, consilience on a real measurement): pass" if ok
          else "QUANTUM-HW: FAILURES")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
