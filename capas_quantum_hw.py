"""CAPAS — quantum HARDWARE claim verifier (the real integration of real hardware).

The classical re-derivation gives the IDEAL output (GATE) but cannot judge a NOISY hardware
result. With the device's PUBLISHED CALIBRATION (CZ error, readout errors — measured daily by
IBM via randomized benchmarking), CAPAS gains a noise MODEL and can verify a hardware claim:

  - re-derive the ideal support (GATE, exact classical simulation), and
  - PREDICT the noise floor from the calibration (a first-order model), and
  - check the MEASURED distribution (ATTEST, the world's response) for CONSISTENCY:
      ADMISSIBLE      — measured error is the same order as the device physically allows
      FLAG_TOO_CLEAN  — cleaner than the calibration permits -> suspicious (fabricated/cherry-picked)
      FLAG_TOO_NOISY  — noisier than predicted -> device drift / TLS / a real anomaly to investigate

This is a CONSILIENCE on a physical measurement: the IDEAL simulation and IBM's INDEPENDENT
calibration are two oracles; the measurement is admissible when it agrees with both. It is the
one domain where CAPAS crosses text<->reality with independent corroboration — and it feeds the
survive-refutation ledger with a REAL physical world-response, not a simulated one.

Honest: the noise model is FIRST-ORDER (gate + SPAM errors, multiplicative); it bounds the
expected error to an order of magnitude, not exactly. The verdict is order-of-magnitude
consistency, not a precise fidelity claim.
"""
from __future__ import annotations

from typing import Any


def predicted_noise_floor(calibration: dict[str, float]) -> float:
    """First-order expected fraction of shots OUTSIDE the ideal support, from the device
    calibration: 1 - (1-cz)(1-ro0)(1-ro1). Captures the dominant 2-qubit-gate + readout SPAM
    error for a 2-qubit (e.g. Bell) circuit."""
    cz = float(calibration.get("cz_error", 0.0))
    ro0 = float(calibration.get("readout_q0", 0.0))
    ro1 = float(calibration.get("readout_q1", 0.0))
    return round(1.0 - (1 - cz) * (1 - ro0) * (1 - ro1), 6)


def _normalize(counts: dict[str, Any]) -> dict[str, float]:
    t = sum(counts.values()) or 1
    return {str(k).replace(" ", ""): v / t for k, v in counts.items()}


def tvd(p: dict[str, float], q: dict[str, float]) -> float:
    """Total-variation distance between two distributions: 0.5 * sum |p-q| in [0,1]."""
    keys = set(p) | set(q)
    return round(0.5 * sum(abs(p.get(k, 0.0) - q.get(k, 0.0)) for k in keys), 4)


def gate_against_prediction(measured_counts: dict[str, int], predicted_distribution: dict[str, float],
                            ideal_support: set[str], sigma_k: float = 3.0) -> dict[str, Any]:
    """CALIBRATION-GRADE gate, statistically honest. Compares the measurement's NOISE SIGNATURE
    (its TVD to the perfect ideal) against the device's EXPECTED signature (the Aer
    NoiseModel.from_backend prediction's TVD to the ideal). The decision margin is the SHOT-NOISE
    resolution (~sigma_k / sqrt(shots)), so the gate only flags what it can statistically resolve.

    Crucial honesty: on a LOW-NOISE device the suspicious-'too clean' signal is the same size as
    the noise itself, so it is UNRESOLVABLE without many shots. `too_clean_resolvable` says whether
    the shot count can even detect it — the gate never fakes a verdict it cannot support."""
    m = _normalize(measured_counts)
    shots = sum(measured_counts.values()) or 1
    pred = _normalize(predicted_distribution) if any(v > 1 for v in predicted_distribution.values()) else dict(predicted_distribution)
    ideal = {k: 1.0 / len(ideal_support) for k in ideal_support}

    expected_sig = tvd(pred, ideal)          # the device's noise signature (from calibration)
    measured_sig = tvd(m, ideal)             # the measurement's noise signature
    margin = round(sigma_k / (shots ** 0.5), 4)
    too_clean_resolvable = expected_sig > margin

    if measured_sig > expected_sig + margin:
        verdict, why = "FLAG_TOO_NOISY", "noise signature above the calibrated expectation — drift / TLS / anomaly"
    elif measured_sig < expected_sig - margin and too_clean_resolvable:
        verdict, why = "FLAG_TOO_CLEAN", "cleaner than the device physically allows — suspicious (fabricated/post-selected)"
    else:
        verdict, why = "ADMISSIBLE", "noise signature consistent with the device's calibrated physics"

    return {
        "verdict": verdict, "why": why,
        "measured_noise_signature": measured_sig,
        "expected_noise_signature": expected_sig,     # from Aer NoiseModel.from_backend
        "shot_noise_margin": margin, "shots": shots,
        "too_clean_resolvable": too_clean_resolvable,
        "resolution_note": (f"with {shots} shots, 'too clean' on this device is "
                            f"{'detectable' if too_clean_resolvable else 'NOT statistically resolvable — needs more shots'}"),
        "method": "noise-signature TVD vs Aer NoiseModel.from_backend, shot-noise-aware margin",
        "consilience": ("ideal re-derivation AND IBM's full calibrated noise model both bound this measurement"
                        if verdict == "ADMISSIBLE" else "the measurement disagrees with the calibrated noise model"),
    }


def gate_hardware_claim(ideal_support: set[str], measured_counts: dict[str, int],
                        calibration: dict[str, float]) -> dict[str, Any]:
    """Gate a quantum HARDWARE measurement against the ideal (GATE) + the device's calibrated
    noise model. ideal_support: bitstrings the ideal circuit produces (e.g. {'00','11'})."""
    total = sum(measured_counts.values()) or 1
    off = sum(v for k, v in measured_counts.items() if k.replace(" ", "") not in ideal_support)
    measured = off / total
    predicted = predicted_noise_floor(calibration)

    # order-of-magnitude consistency band around the predicted floor (model is first-order)
    lo, hi = 0.3 * predicted, 3.0 * predicted
    if measured < lo:
        verdict, why = "FLAG_TOO_CLEAN", ("measured error below what the device physically allows — "
                                          "suspicious (fabricated / cherry-picked / wrong device claimed)")
    elif measured > hi:
        verdict, why = "FLAG_TOO_NOISY", ("measured error far above the calibration — device drift / TLS "
                                          "activity / an anomaly worth investigating")
    else:
        verdict, why = "ADMISSIBLE", "measured error is consistent with the device's published physics"

    return {
        "ideal_support": sorted(ideal_support),
        "measured_error": round(measured, 4),            # ATTEST: the world's response
        "predicted_floor": predicted,                    # from IBM's independent calibration
        "consistency_band": [round(lo, 4), round(hi, 4)],
        "verdict": verdict,
        "why": why,
        "consilience": ("two independent oracles agree: the ideal re-derivation AND IBM's daily-benchmarked "
                        "calibration both bound this measurement — corroboration on a physical result"
                        if verdict == "ADMISSIBLE" else
                        "the measurement disagrees with the device's known physics — a flag, not a pass"),
        "note": "GATE = ideal (re-derived). ATTEST = hardware measurement (the world). The calibration noise "
                "model gates whether the measurement is physically admissible. First-order model: "
                "order-of-magnitude consistency, not an exact fidelity claim.",
    }
