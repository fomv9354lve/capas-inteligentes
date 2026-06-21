"""CAPAS — proof-carrying verification layer (Rung 3 re-execution + scope partition + receipt).

Sits ON TOP of the deterministic admissibility gate (``capas.decide_external_claim``)
and raises the bar ABOVE what regulation requires today:

  • A claim is ACCEPTED only when its evidence RE-DERIVES (re-computed, anchor-checked,
    or re-executed) — never on a bare declared field.
  • Evidence that is declared but not re-derivable is HELD, with an explicit ask for a
    re-derivable artifact or a signed provenance attestation. Declared-only ≠ accepted.
  • Non-deterministic / unobservable / GIGO evidence is PARTITIONED to ATTEST scope
    (signed + bound, never marketed as verified) instead of being silently accepted.
  • Every decision emits a portable, hash-bound verification RECEIPT a third party can
    re-check without re-running the gate.

Deterministic and reproducible. No LLM in the decision path. Mirrors the moat:
"gate the deterministic island, attest the ocean, and never conflate the two."
"""
from __future__ import annotations

import ast
import hashlib
import json
import math
import operator
import os
import re
from typing import Any

import capas

try:  # real statistical re-derivation when available
    from scipy import stats as _scipy_stats  # type: ignore
    _HAS_SCIPY = True
except Exception:  # pragma: no cover
    _HAS_SCIPY = False


# ─────────────────────────────────────────────────────────────────────────────
# Anchor registry — known physical / mathematical truths. Deterministic regex
# scan of the claim text; a value that contradicts a known anchor is REJECTED
# regardless of how clean the declared statistics are. Auditable + extensible.
# ─────────────────────────────────────────────────────────────────────────────
# ── Physical laws behind the anchors (real math, used to RE-DERIVE in-domain) ──
# An anchor constant (water boils at 100°C) is only the value of a LAW evaluated
# at a canonical condition (1 atm). Re-aggregating the layer: model the law and
# its domain of validity, so the engine RE-DERIVES the true value when the claim
# pins the condition, and ABSTAINS (does not reject) when the condition is named
# but unquantified. This pushes the determinism frontier honestly instead of
# bolting on brittle per-case regex exceptions.

# Antoine equation for water, P in mmHg, T in °C (valid ~1-100°C):
#   log10(P) = A - B/(C+T)  =>  T_boil(P) = B/(A - log10(P)) - C
_ANTOINE_WATER = (8.07131, 1730.63, 233.426)
_P0_MMHG = 760.0  # 1 atm

# Pressure units -> mmHg.
_PRESSURE_TO_MMHG = {"mmhg": 1.0, "torr": 1.0, "atm": 760.0, "bar": 750.062,
                     "mbar": 0.750062, "kpa": 7.50062, "hpa": 0.750062,
                     "pa": 0.00750062, "psi": 51.7149}
_PRESSURE_RE = re.compile(
    r"(-?\d+(?:\.\d+)?)\s*(mmhg|torr|atm|atmospheres?|mbar|hpa|kpa|bar|psi|pa)\b")
_ALTITUDE_RE = re.compile(r"(-?\d+(?:\.\d+)?)\s*(km|kilomet(?:er|re)s?|m|met(?:er|re)s?|ft|feet)\b")
# Qualitative conditions that move OFF the 1-atm baseline (boiling/freezing) but
# do not pin a number -> domain undefined -> abstain.
_OFF_BASELINE_PT = re.compile(
    r"high\s+altitude|altitude|elevation|mountain|summit|everest|denver|"
    r"thin\s+air|vacuum|reduced\s+pressure|low\s+pressure|high\s+pressure|"
    r"pressure\s+cooker|under\s+pressure")
_BASELINE_PT = re.compile(r"sea\s*level|1\s*atm\b|standard\s+pressure|stp\b")
# Light through a medium is slower than c (v=c/n) -> vacuum anchor does not apply.
_OFF_BASELINE_LIGHT = re.compile(r"\bin\s+(?:water|glass|a?\s*medium|media|fib(?:er|re)|"
                                 r"air|diamond|matter|crystal|liquid)")


def _antoine_boiling_C(p_mmhg: float) -> float:
    A, B, C = _ANTOINE_WATER
    return B / (A - math.log10(p_mmhg)) - C


def _altitude_to_mmHg(value: float, unit: str) -> float:
    h_m = value * 1000.0 if unit.startswith("k") else (value * 0.3048 if unit in ("ft", "feet") else value)
    return _P0_MMHG * (1.0 - 2.25577e-5 * h_m) ** 5.25588  # ISA barometric formula


def _parse_pressure_mmHg(text: str) -> float | None:
    m = _PRESSURE_RE.search(text)
    if not m:
        return None
    unit = m.group(2)
    unit = "atm" if unit.startswith("atm") else unit
    return float(m.group(1)) * _PRESSURE_TO_MMHG.get(unit, 1.0)


ANCHORS: list[dict[str, Any]] = [
    {
        "id": "water_boiling_point_C",
        "truth": 100.0, "tol": 3.0, "tol_law": 5.0, "unit": "°C",
        "pattern": r"water\s+boils?\s+at\s+(-?\d+(?:\.\d+)?)\s*°?\s*c\b",
        "desc": "Boiling point of water (1 atm: 100°C; lower at reduced pressure)",
        "domain": "pressure_temp", "law": "antoine_boiling",
    },
    {
        "id": "speed_of_light_m_s",
        "truth": 299_792_458.0, "tol": 1000.0, "unit": "m/s",
        "pattern": r"speed\s+of\s+light\s+(?:is|=|of)\s*(-?\d+(?:\.\d+)?)\s*m/?s",
        "desc": "Speed of light in vacuum is 299,792,458 m/s (slower in any medium)",
        "domain": "medium_light",
    },
    {
        "id": "water_freezing_point_C",
        "truth": 0.0, "tol": 3.0, "unit": "°C",
        "pattern": r"water\s+freezes?\s+at\s+(-?\d+(?:\.\d+)?)\s*°?\s*c\b",
        "desc": "Freezing point of water at 1 atm is 0°C",
        "domain": "pressure_temp",  # weak P-dependence: abstain off-baseline, no re-derivation
    },
]

# ── Universal bounds: laws that hold in EVERY condition (no domain lifts them) ──
# Distinct from condition-laws above: a condition-law (boiling point) abstains
# off-baseline, but a universal bound has no off-baseline — violating it is
# impossible under any pressure/medium/context, so it REJECTs unconditionally and
# never abstains. This extends the engine's deterministic domain to "hard limit"
# claims that previously fell through to an unhelpful HOLD.
_C_LIGHT = 299_792_458.0
_EPS = 1e-9  # numeric slack for bound comparisons (e.g. Holevo bits ≤ qubits)
UNIVERSAL_BOUNDS: list[dict[str, Any]] = [
    {
        "id": "absolute_zero_floor_C", "direction": "min", "limit": -273.15, "unit": "°C",
        # any temperature reading; the floor only trips on physically-impossible values,
        # so a normal "90°C" never misfires.
        "pattern": r"(-?\d+(?:\.\d+)?)\s*°\s*c\b",
        "desc": "Temperature cannot fall below absolute zero (-273.15°C = 0 K)",
        "basis": "third law of thermodynamics",
    },
    {
        "id": "absolute_zero_floor_K", "direction": "min", "limit": 0.0, "unit": "K",
        "pattern": r"(-?\d+(?:\.\d+)?)\s*k(?:elvin)?\b",
        "desc": "Absolute temperature cannot be negative (0 K is the floor)",
        "basis": "third law of thermodynamics",
    },
    {
        "id": "lightspeed_ceiling_massive", "direction": "max", "limit": _C_LIGHT, "unit": "m/s",
        # a moving object's speed; massive carriers of energy/information cannot reach c.
        "pattern": r"(?:travel(?:s|l?ing)?|mov(?:es|ing)|velocity|going)\D{0,24}?"
                   r"(\d+(?:\.\d+)?(?:e\d+)?)\s*m/?s",
        "desc": "A massive object / signal cannot travel at or above c (299,792,458 m/s)",
        "basis": "special relativity",
    },
    {
        "id": "probability_unit_interval", "direction": "max", "limit": 1.0, "unit": "",
        "pattern": r"probability\s+(?:of\s+[\w\s-]{1,30}?\s+)?(?:is|=|of)\s*(\d+(?:\.\d+)?)\b(?!\s*%)",
        "desc": "A probability must lie in [0, 1]",
        "basis": "Kolmogorov axioms",
    },
]


def universal_bound_violations(claim_text: str) -> list[dict[str, Any]]:
    """Scan for claims that violate a universal bound (true in every condition).
    Always a contradiction (-> REJECT); never an abstention."""
    text = (claim_text or "").lower()
    out: list[dict[str, Any]] = []
    for b in UNIVERSAL_BOUNDS:
        for m in re.finditer(b["pattern"], text):
            val = float(m.group(1))
            violated = (b["direction"] == "min" and val < b["limit"]) or \
                       (b["direction"] == "max" and val > b["limit"])
            if violated:
                out.append({"anchor": b["id"], "kind": "contradiction", "asserted": val,
                            "truth": b["limit"], "unit": b["unit"], "desc": b["desc"],
                            "re_derived_from": b["basis"]})
                break
    return out


# ── Holevo accessible-information bound (a universal bound WITH assumption-gates) ─
# Holevo's theorem (1973) is a PROVEN bound, not a conjecture: from n qubits no
# measurement strategy can recover more than n classical bits of ACCESSIBLE
# information. A qubit carries continuous amplitudes (α,β on the Bloch sphere), so
# its STORAGE is unbounded — but READ-OUT is destructive, and no-cloning (Wootters–
# Zurek / Dieks 1982) forbids manufacturing copies of an unknown state. Reading the
# "shape" (full state) therefore COSTS copies: shadow/tomography lower bounds are
# themselves PROVEN VIA Holevo (e.g. Ω(dr/ε²) copies, arXiv:2207.14438, 2025), and
# general n-qubit reconstruction needs O(4ⁿ) copies (arXiv:2505.14953, 2025).
#
# Unlike a context-free bound (c, absolute zero), Holevo's *applicable* ceiling is
# lifted by two NAMED resources, which become the assumption-gates the engine pins:
#   * prior shared ENTANGLEMENT -> superdense coding sends 2 bits per transmitted
#     qubit, but the protocol consumes 2 qubits total (Bennett–Wiesner 1992), so the
#     "2 bits / 1 qubit" claim is only admissible WITH entanglement and still obeys
#     ≤ n bits per n qubits.
#   * N independent COPIES -> the full state is recoverable by tomography, but the
#     readout spent N qubits; "exceeded 1 bit/qubit" remains false.
# So: a claim to recover >n bits of accessible information from n qubits is REJECTED
# (no off-baseline saves it — it is a proven impossibility); a claim that merely
# *reconstructs the state* is admissible but the engine pins that it cost the copies
# it used; a claim that invokes neither resource and asserts >1 bit/qubit single-shot
# is REJECTED on no-cloning + Holevo.
_HOLEVO_BITS_PER_QUBIT = re.compile(
    r"(?:store|stor(?:e|ing)|encode|encoding|pack(?:ing)?|recover(?:ing)?|read(?:ing)?\s+out|"
    r"retriev(?:e|ing)|extract(?:ing)?|transmit(?:ting)?|send(?:ing)?)\D{0,40}?"
    r"(\d+(?:\.\d+)?)\s*(?:classical\s+)?bits?\b\D{0,40}?(?:per|inside|into|in|from|out\s+of|/)\s+"
    r"(?:just\s+)?(?:an?\s+)?(?:(\d+(?:\.\d+)?)\s*)?(?:single\s+|one\s+|1\s+)?qu?[\s-]*bits?\b")
# Resources that legitimately appear when >1 bit/qubit is claimed.
_HOLEVO_ENTANGLEMENT = re.compile(
    r"entangl|superdense|super[\s-]?dense|pre[\s-]?shared|bell\s+pair|epr\s+pair|shared\s+pair")
# Copies named -> claim is about STATE reconstruction (tomography/shadows), not
# beating the accessible-information bound; admissible but pin the copy cost.
_HOLEVO_COPIES = re.compile(
    r"\b(\d+(?:\.\d+)?)\s*(?:identical\s+|fresh\s+)?copies\b|"
    r"tomograph|classical\s+shadows?|shadow\s+tomograph|many\s+copies|multiple\s+copies|n\s+copies")
# Inverted word order: "per/in (a) qubit ... N bits" (e.g. "per qubit we store 5 bits").
_HOLEVO_INVERTED = re.compile(
    r"(?:per|in|into|inside)\s+(?:an?\s+)?(?:single\s+|one\s+|1\s+)?qu?[\s-]*bits?\b\D{0,40}?"
    r"(\d+(?:\.\d+)?)\s*(?:classical\s+)?bits?\b")
# Spelled-out small integers — adversaries write "five bits" to dodge a digit-only regex.
_NUM_WORDS = {"zero": "0", "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
              "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
              "eleven": "11", "twelve": "12", "twenty": "20", "fifty": "50", "hundred": "100"}
_NUM_WORD_RE = re.compile(r"\b(" + "|".join(_NUM_WORDS) + r")\b")


def _normalize_number_words(text: str) -> str:
    """Replace spelled-out integers with digits so the digit-based anchors cannot be
    evaded by writing the number in words ('five bits' -> '5 bits')."""
    return _NUM_WORD_RE.sub(lambda mo: _NUM_WORDS[mo.group(1)], text)


def holevo_information_contradictions(claim_text: str) -> list[dict[str, Any]]:
    """Deterministic Holevo accessible-information anchor (a universal bound whose
    *applicable* ceiling is gated by two named quantum resources: prior entanglement
    and number of copies). Returns the same ``kind`` taxonomy as the other anchors:

      * "contradiction" -> claim asserts > n bits of accessible information out of n
        qubits with NO entanglement and NO copies named (or single-shot): a proven
        impossibility (Holevo + no-cloning) -> verify() REJECT.
      * "abstain"       -> claim names COPIES / tomography / shadows: it is about
        reconstructing the state, not beating the bound. The bound does not refute
        it, but the engine cannot re-derive the copy budget from text alone -> HOLD,
        route up to pin/attest how many copies (qubits) were spent.
    Entanglement-gated 2-bit/qubit (superdense) within ≤ n bits per n qubits is NOT
    flagged. An empty list means no Holevo claim is engaged."""
    text = _normalize_number_words((claim_text or "").lower())
    m = _HOLEVO_BITS_PER_QUBIT.search(text)
    if m:
        bits = float(m.group(1))
        qubits = float(m.group(2)) if m.group(2) else 1.0
    else:
        # Inverted word order ("per qubit we store 5 bits"): qubit count not captured,
        # default to 1 qubit (the bound the inverted phrasing always implies).
        mi = _HOLEVO_INVERTED.search(text)
        if not mi:
            return []
        bits, qubits = float(mi.group(1)), 1.0
    if qubits <= 0:
        return []
    bound = qubits  # Holevo: accessible bits ≤ number of qubits
    if bits <= bound + _EPS:
        return []  # within the bound (incl. 1 bit/1 qubit) -> nothing to flag
    # Over the nominal bound: check which resource the claim invokes.
    if _HOLEVO_ENTANGLEMENT.search(text):
        # Superdense coding: 2 bits per *transmitted* qubit, consuming 2 qubits total.
        # Admissible iff bits ≤ 2·qubits (entanglement at most doubles); else still impossible.
        if bits <= 2.0 * qubits + _EPS:
            return []
        return [{"anchor": "holevo_accessible_information", "kind": "contradiction",
                 "asserted": bits, "truth": 2.0 * qubits, "unit": "bits",
                 "desc": "Holevo bound: even WITH prior entanglement (superdense coding) "
                         f"at most 2 bits per transmitted qubit (≤{2.0 * qubits:g} bits for "
                         f"{qubits:g} qubit(s)), and the protocol still consumes 2 qubits total",
                 "re_derived_from": "Holevo (1973) + superdense coding (Bennett–Wiesner 1992)"}]
    if _HOLEVO_COPIES.search(text):
        # State reconstruction from N copies: not a Holevo violation, but the readout
        # spent N qubits. The text does not let us re-derive N -> abstain (route up).
        return [{"anchor": "holevo_accessible_information", "kind": "abstain",
                 "asserted": bits, "unit": "bits",
                 "desc": "Holevo accessible-information bound",
                 "reason": "claim recovers the full state via copies/tomography/shadows, not "
                           "single-shot accessible information; this does not beat Holevo but the "
                           "copy budget (qubits spent) is not re-derivable from text. Reading the "
                           "'shape' costs copies (tomography lower bounds are proven via Holevo); "
                           "pin or attest the number of copies (= qubits consumed)."}]
    # No entanglement, no copies, claims > bits than qubits: single-shot impossibility.
    return [{"anchor": "holevo_accessible_information", "kind": "contradiction",
             "asserted": bits, "truth": bound, "unit": "bits",
             "desc": f"Holevo bound: at most {bound:g} bit(s) of accessible information can be "
                     f"recovered from {qubits:g} qubit(s); no-cloning forbids manufacturing copies "
                     "of an unknown state, so single-shot read-out cannot exceed the bound",
             "re_derived_from": "Holevo (1973) + no-cloning (Wootters–Zurek / Dieks 1982)"}]


def anchor_contradictions(claim_text: str) -> list[dict[str, Any]]:
    """Deterministic, domain-aware anchor scan.

    Returns findings with ``kind``:
      * "contradiction" -> the claim is INSIDE the anchor's domain and asserts a
        value the law/constant refutes (verify() -> REJECT).
      * "abstain"       -> the claim names a condition outside the anchor's
        canonical domain but does not quantify it, so the constant does not apply
        and the law cannot be evaluated (verify() -> HOLD, route up; never REJECT).
    An empty list means no anchor is engaged (claim flows on normally)."""
    text = (claim_text or "").lower()
    out: list[dict[str, Any]] = []
    for a in ANCHORS:
        m = re.search(a["pattern"], text)
        if not m:
            continue
        asserted = float(m.group(1))

        if a.get("domain") == "medium_light":
            if _OFF_BASELINE_LIGHT.search(text):  # light in a medium: c does not apply
                out.append({"anchor": a["id"], "kind": "abstain", "asserted": asserted,
                            "unit": a["unit"], "desc": a["desc"],
                            "reason": "light through a medium travels at c/n (< c); the vacuum "
                                      "constant does not apply — re-derive needs the refractive index."})
                continue
            if abs(asserted - a["truth"]) > a["tol"]:
                out.append({"anchor": a["id"], "kind": "contradiction", "asserted": asserted,
                            "truth": a["truth"], "unit": a["unit"], "desc": a["desc"]})
            continue

        if a.get("domain") == "pressure_temp":
            # 1) condition numerically pinned -> RE-DERIVE the true value from the law.
            p = _parse_pressure_mmHg(text)
            if p is None:
                alt = _ALTITUDE_RE.search(text)
                if alt and not _BASELINE_PT.search(text):
                    p = _altitude_to_mmHg(float(alt.group(1)), alt.group(2))
            if p is not None and abs(p - _P0_MMHG) > 1.0:
                if a.get("law") == "antoine_boiling":
                    expected = _antoine_boiling_C(p)
                    if abs(asserted - expected) > a.get("tol_law", 5.0):
                        out.append({"anchor": a["id"], "kind": "contradiction", "asserted": asserted,
                                    "truth": round(expected, 1), "unit": a["unit"],
                                    "desc": f"{a['desc']}; at {round(p)} mmHg the law gives {round(expected, 1)}°C",
                                    "re_derived_from": "Antoine equation", "pressure_mmHg": round(p, 1)})
                    # within tol -> claim is physically consistent: no finding.
                    continue
                # law not modelled at this condition (e.g. freezing): abstain.
                out.append({"anchor": a["id"], "kind": "abstain", "asserted": asserted,
                            "unit": a["unit"], "desc": a["desc"],
                            "reason": "condition is off-baseline; this anchor has no re-derivation law for it."})
                continue
            # 2) condition named qualitatively but not quantified -> abstain.
            if _OFF_BASELINE_PT.search(text) and not _BASELINE_PT.search(text):
                out.append({"anchor": a["id"], "kind": "abstain", "asserted": asserted,
                            "unit": a["unit"], "desc": a["desc"],
                            "reason": "claim scopes to a non-standard condition (e.g. altitude/"
                                      "pressure) but does not quantify it; the 1 atm constant does "
                                      "not apply and the law cannot be evaluated."})
                continue
            # 3) baseline (1 atm, explicit or default) -> the constant holds.
            if abs(asserted - a["truth"]) > a["tol"]:
                out.append({"anchor": a["id"], "kind": "contradiction", "asserted": asserted,
                            "truth": a["truth"], "unit": a["unit"], "desc": a["desc"]})
    return out


# ── Structured physical-claim check (robust path; no prose parsing) ───────────
# The anchor scans above read English claim text — convenient but evadable
# (spelled-out numbers, inverted order, other languages). The structured path
# evaluates the SAME laws (Antoine, the c ceiling, absolute zero, Holevo) from
# explicit fields, so a producer states quantity/value/unit/conditions and the
# engine decides deterministically. evidence['physical'] =
#   {quantity, value, unit, conditions:{pressure_mmHg|altitude_m|medium|
#    qubits|copies|entanglement}}. Same contradiction/abstain taxonomy.
_TEMP_C = {"°c", "c", "celsius", "degc", "deg_c"}
_TEMP_K = {"k", "kelvin"}


def check_physical(physical: Any) -> list[dict[str, Any]]:
    if not isinstance(physical, dict):
        return []
    q = str(physical.get("quantity", "")).lower().strip()
    unit = str(physical.get("unit", "")).lower().strip()
    cond = physical.get("conditions") or {}
    try:
        val = float(physical.get("value"))
    except (TypeError, ValueError):
        return []
    out: list[dict[str, Any]] = []

    # Universal temperature floor (absolute zero) — any temperature quantity.
    if unit in _TEMP_C and val < -273.15 - _EPS:
        return [{"anchor": "absolute_zero_floor_C", "kind": "contradiction", "asserted": val,
                 "truth": -273.15, "unit": "°C", "desc": "Temperature below absolute zero is impossible",
                 "re_derived_from": "third law of thermodynamics"}]
    if unit in _TEMP_K and val < -_EPS:
        return [{"anchor": "absolute_zero_floor_K", "kind": "contradiction", "asserted": val,
                 "truth": 0.0, "unit": "K", "desc": "Absolute temperature cannot be negative",
                 "re_derived_from": "third law of thermodynamics"}]

    if q in ("boiling_point", "boiling point") and unit in _TEMP_C:
        p = cond.get("pressure_mmHg")
        if p is None and cond.get("altitude_m") is not None:
            p = _altitude_to_mmHg(float(cond["altitude_m"]), "m")
        if p is not None and abs(float(p) - _P0_MMHG) > 1.0:
            expected = _antoine_boiling_C(float(p))
            if abs(val - expected) > 5.0:
                out.append({"anchor": "water_boiling_point_C", "kind": "contradiction", "asserted": val,
                            "truth": round(expected, 1), "unit": "°C", "pressure_mmHg": round(float(p), 1),
                            "desc": f"At {round(float(p))} mmHg water boils at {round(expected, 1)}°C (Antoine)",
                            "re_derived_from": "Antoine equation"})
        elif cond.get("off_baseline") and p is None:
            out.append({"anchor": "water_boiling_point_C", "kind": "abstain", "asserted": val, "unit": "°C",
                        "desc": "Boiling point off 1 atm", "reason": "a non-standard condition is named but "
                        "no pressure/altitude is quantified; the 1 atm constant does not apply."})
        elif p is None and not cond.get("off_baseline") and abs(val - 100.0) > 3.0:
            out.append({"anchor": "water_boiling_point_C", "kind": "contradiction", "asserted": val,
                        "truth": 100.0, "unit": "°C", "desc": "Boiling point of water at 1 atm is 100°C"})

    if q in ("speed", "velocity") and unit in ("m/s", "m s-1", "ms-1"):
        if cond.get("medium"):
            out.append({"anchor": "speed_of_light_m_s", "kind": "abstain", "asserted": val, "unit": "m/s",
                        "desc": "speed in a medium", "reason": f"in {cond['medium']} light travels at c/n (< c); "
                        "the vacuum ceiling does not directly apply."})
        elif val > _C_LIGHT + 1.0:
            out.append({"anchor": "lightspeed_ceiling_massive", "kind": "contradiction", "asserted": val,
                        "truth": _C_LIGHT, "unit": "m/s", "desc": "Nothing massive travels at or above c",
                        "re_derived_from": "special relativity"})

    if q in ("accessible_information", "information", "info_per_qubit", "bits_per_qubit", "holevo"):
        qubits = float(cond.get("qubits", 1) or 1)
        if qubits > 0:
            if val <= qubits + _EPS:
                pass  # within Holevo
            elif cond.get("entanglement") and val <= 2.0 * qubits + _EPS:
                pass  # superdense, still consumes the qubits it claims
            elif cond.get("copies") and float(cond.get("copies", 0)) > 1:
                out.append({"anchor": "holevo_accessible_information", "kind": "abstain", "asserted": val,
                            "unit": "bits", "desc": "Holevo accessible-information bound",
                            "reason": "state reconstruction via copies/tomography, not single-shot accessible "
                            "information; the copy budget (qubits spent) must be pinned/attested."})
            else:
                truth = 2.0 * qubits if cond.get("entanglement") else qubits
                out.append({"anchor": "holevo_accessible_information", "kind": "contradiction", "asserted": val,
                            "truth": truth, "unit": "bits",
                            "desc": f"Holevo: at most {truth:g} accessible bit(s) from {qubits:g} qubit(s)"
                                    + (" even with entanglement (superdense)" if cond.get("entanglement") else ""),
                            "re_derived_from": "Holevo (1973) + no-cloning"})
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Scope partition (#3): which evidence is RE-DERIVABLE (GATE) vs ATTEST-class.
# Study-design / unobservable booleans cannot be re-derived by computation; they
# require verifiable provenance, otherwise the claim is HELD, not accepted.
# ─────────────────────────────────────────────────────────────────────────────
ATTEST_CLASS_FIELDS = {
    "intervention_or_natural_experiment", "temporal_order_established",
    "confounders_controlled", "mechanism_evidence_present",
    "risk_of_bias_assessed", "conflict_resolution_method",
    "artifact_available", "independent_reproduction_pass",
}
PROVENANCE_KEYS = (
    "provenance", "ro_crate", "registry_id", "signed_attestation",
    "attestation", "c2pa_manifest", "qeaa",
)


def _has_provenance(evidence: dict[str, Any]) -> bool:
    return any(evidence.get(k) for k in PROVENANCE_KEYS)


# ─────────────────────────────────────────────────────────────────────────────
# Re-derivation (#1, Rung 3): actually re-compute, don't trust the declared value.
# ─────────────────────────────────────────────────────────────────────────────
def _welch_p(group_a: list[float], group_b: list[float]) -> float:
    if _HAS_SCIPY:
        _, p = _scipy_stats.ttest_ind(group_a, group_b, equal_var=False)
        return float(p)
    # dependency-free Welch's t + normal approximation (large-sample) fallback
    na, nb = len(group_a), len(group_b)
    ma, mb = sum(group_a) / na, sum(group_b) / nb
    va = sum((x - ma) ** 2 for x in group_a) / (na - 1)
    vb = sum((x - mb) ** 2 for x in group_b) / (nb - 1)
    se = math.sqrt(va / na + vb / nb) or 1e-12
    t = (ma - mb) / se
    # two-sided p via standard normal approximation
    return 2.0 * (1.0 - 0.5 * (1.0 + math.erf(abs(t) / math.sqrt(2.0))))


def rederive_statistical(evidence: dict[str, Any]) -> dict[str, Any] | None:
    """If raw data is supplied, RE-COMPUTE the p-value and compare to declared.
    Returns None when there is nothing re-derivable (declared-only)."""
    raw = evidence.get("raw_data") or evidence.get("raw")
    if not isinstance(raw, dict):
        return None
    a, b = raw.get("group_a"), raw.get("group_b")
    if not (isinstance(a, list) and isinstance(b, list) and len(a) > 1 and len(b) > 1):
        return None
    recomputed = _welch_p([float(x) for x in a], [float(x) for x in b])
    declared = evidence.get("p_value")
    declared_f = float(declared) if isinstance(declared, (int, float)) else None
    # match within a small absolute/relative tolerance
    match = (
        declared_f is not None
        and abs(recomputed - declared_f) <= max(0.01, 0.10 * max(declared_f, 1e-6))
    )
    return {
        "recomputed_p": round(recomputed, 5),
        "declared_p": declared,
        "match": bool(match),
        "engine": "scipy.ttest_ind(Welch)" if _HAS_SCIPY else "welch+normal-approx",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Calculation re-derivation — Passage Point A (pharma CDS / spreadsheet math) and
# the shared primitive behind ADaM derivations: RE-COMPUTE a reported number from
# its raw inputs via a whitelisted deterministic operation. No vendor kernel, no
# arbitrary code: this is exactly the "reported value vs raw data" fraud surface
# the spreadsheet-integrity FDA 483s live on — and what Empower/Pinnacle 21
# structurally do NOT do (they manage trust heuristics / check conformance).
# ─────────────────────────────────────────────────────────────────────────────
_SAFE_BINOPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
                ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod}
_SAFE_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _safe_eval(expr: str, names: dict[str, Any]) -> float:
    """Evaluate a pure arithmetic expression over named numeric inputs. No calls,
    attributes, subscripts, or names outside `inputs` — deterministic and safe."""
    def ev(n: ast.AST) -> float:
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return float(n.value)
        if isinstance(n, ast.Name):
            if n.id in names:
                return float(names[n.id])
            raise ValueError(f"unknown input '{n.id}'")
        if isinstance(n, ast.BinOp) and type(n.op) in _SAFE_BINOPS:
            return _SAFE_BINOPS[type(n.op)](ev(n.left), ev(n.right))
        if isinstance(n, ast.UnaryOp) and type(n.op) in _SAFE_UNARY:
            return _SAFE_UNARY[type(n.op)](ev(n.operand))
        raise ValueError("disallowed expression element")
    return ev(ast.parse(str(expr), mode="eval").body)


def rederive_calculation(evidence: dict[str, Any]) -> dict[str, Any] | None:
    """Re-compute evidence['computation'] = {operation, inputs, reported_value,
    tolerance}. Returns None when no computation artifact is supplied."""
    comp = evidence.get("computation")
    if not isinstance(comp, dict):
        return None
    op = comp.get("operation")
    inp = comp.get("inputs") or {}
    reported = comp.get("reported_value")
    tol = float(comp.get("tolerance", 0) or 0)
    try:
        if op == "linear_calibration":      # concentration from signal: x=(y-b)/m
            val = (float(inp["signal"]) - float(inp["intercept"])) / float(inp["slope"])
        elif op == "mean":
            xs = [float(x) for x in inp["values"]]; val = sum(xs) / len(xs)
        elif op == "sum":
            val = sum(float(x) for x in inp["values"])
        elif op == "ratio":
            val = float(inp["numerator"]) / float(inp["denominator"])
        elif op == "percent_recovery":
            val = float(inp["measured"]) / float(inp["expected"]) * 100.0
        elif op == "expression":
            val = _safe_eval(comp.get("expression", ""), inp)
        else:
            return {"operation": op, "status": "UNSUPPORTED_OP", "match": None}
    except Exception as e:  # malformed artifact -> cannot re-derive
        return {"operation": op, "status": "ERROR", "error": str(e), "match": False}
    reported_f = float(reported) if isinstance(reported, (int, float)) else None
    match = reported_f is not None and abs(val - reported_f) <= max(tol, 1e-9)
    return {"operation": op, "re_derived": round(val, 6), "reported": reported,
            "tolerance": tol, "match": bool(match)}


# ─────────────────────────────────────────────────────────────────────────────
# Dataset re-derivation — Passage Point B (clinical DB-lock -> ADaM/TLF submission).
# Re-derive a SUBMITTED derived dataset (ADaM-style) from its SOURCE (SDTM-style)
# via declared per-column deterministic rules, and DIFF re-derived vs submitted
# within a declared tolerance. A row that does not re-derive is the 74%-discrepancy
# fraud Pinnacle 21 cannot see (it checks conformance, not numbers). Re-derivation
# is only honest inside a PINNED environment, so an unpinned run is ATTEST-only.
# ─────────────────────────────────────────────────────────────────────────────
_REQUIRED_ENV = ("language", "version", "os", "locale")


def environment_pinned(evidence: dict[str, Any]) -> dict[str, Any] | None:
    env = evidence.get("environment")
    if not isinstance(env, dict):
        return None
    missing = [k for k in _REQUIRED_ENV if not env.get(k)]
    return {"pinned": not missing, "missing": missing, "env": env}


def rederive_dataset(evidence: dict[str, Any]) -> dict[str, Any] | None:
    """Re-derive submitted rows from source rows via per-column rules; diff."""
    d = evidence.get("derivation")
    if not isinstance(d, dict):
        return None
    source = d.get("source") or []
    submitted = d.get("submitted") or []
    rules = d.get("rules") or {}
    tol = float(d.get("tolerance", 0) or 0)
    if not (isinstance(source, list) and isinstance(submitted, list) and rules
            and len(source) == len(submitted) and source):
        return {"status": "MALFORMED", "match": False}
    mismatches: list[dict[str, Any]] = []
    checks = 0
    for i, (s, sub) in enumerate(zip(source, submitted)):
        for col, rule in rules.items():
            op = rule.get("operation")
            try:
                if op == "expression":
                    val: Any = _safe_eval(rule.get("expression", ""), s)
                elif op == "ratio":
                    val = float(s[rule["numerator"]]) / float(s[rule["denominator"]])
                elif op == "sum":
                    val = sum(float(s[c]) for c in rule["columns"])
                elif op == "copy":
                    val = s[rule["column"]]
                else:
                    return {"status": "UNSUPPORTED_OP", "op": op, "match": None}
            except Exception as e:
                mismatches.append({"row": i, "col": col, "error": str(e)})
                continue
            checks += 1
            sval = sub.get(col)
            try:
                ok = abs(float(val) - float(sval)) <= max(tol, 1e-9)
            except Exception:
                ok = val == sval
            if not ok:
                mismatches.append({"row": i, "col": col, "re_derived": val, "submitted": sval})
    return {"rows": len(submitted), "checks": checks,
            "mismatches": mismatches[:20], "mismatch_count": len(mismatches),
            "match": len(mismatches) == 0}


def reconcile_registry(evidence: dict[str, Any]) -> dict[str, Any] | None:
    """Compare a public-registry-posted figure against the re-derived value."""
    reg = evidence.get("registry")
    if not isinstance(reg, dict):
        return None
    posted, rederived = reg.get("posted_value"), reg.get("rederived_value")
    tol = float(reg.get("tolerance", 0) or 0)
    try:
        match = abs(float(posted) - float(rederived)) <= max(tol, 1e-9)
    except Exception:
        match = posted == rederived
    return {"posted": posted, "rederived": rederived, "match": bool(match),
            "source_id": reg.get("source_id")}


# ─────────────────────────────────────────────────────────────────────────────
# Passage Point A v2 — parameterized peak integration + manual_override.
# The automatic integration (area under the signal between bounds, minus a linear
# baseline) IS deterministic and re-derivable. A MANUAL re-integration is human
# judgment — the literal data-integrity fraud in FDA 483s (analyst re-integrates a
# peak to pass spec). It is NOT silently reproduced: it is SURFACED, the
# divergence from the automatic result is measured, and it is ATTEST-class —
# requiring a signed analyst+reason, else HELD.
# ─────────────────────────────────────────────────────────────────────────────
def _trapz(times: list[float], resp: list[float]) -> float:
    return sum((resp[i] + resp[i + 1]) / 2.0 * (times[i + 1] - times[i]) for i in range(len(times) - 1))


def rederive_integration(evidence: dict[str, Any]) -> dict[str, Any] | None:
    integ = evidence.get("integration")
    if not isinstance(integ, dict):
        return None
    sig = integ.get("signal")
    if isinstance(sig, dict):
        times, resp = sig.get("time"), sig.get("response")
    elif isinstance(sig, list):
        times = [p[0] for p in sig]; resp = [p[1] for p in sig]
    else:
        return {"status": "MALFORMED", "match": False}
    if not (times and resp and len(times) == len(resp)):
        return {"status": "MALFORMED", "match": False}
    start, end = float(integ["baseline_start"]), float(integ["baseline_end"])
    win = [(float(t), float(y)) for t, y in zip(times, resp) if start <= float(t) <= end]
    if len(win) < 2:
        return {"status": "NO_WINDOW", "match": False}
    wt, wy = [p[0] for p in win], [p[1] for p in win]
    auto_area = _trapz(wt, wy) - (wy[0] + wy[-1]) / 2.0 * (wt[-1] - wt[0])  # gross − linear baseline
    tol = float(integ.get("tolerance", 0) or 0)
    out: dict[str, Any] = {"auto_area": round(auto_area, 6), "tolerance": tol}
    mo = integ.get("manual_override")
    if isinstance(mo, dict):
        out["manual_override"] = True
        out["analyst"], out["reason"] = mo.get("analyst"), mo.get("reason")
        out["manual_area"] = mo.get("area")
        try:
            out["diverges_from_auto"] = abs(float(mo.get("area")) - auto_area) > max(tol, 1e-9)
        except Exception:
            out["diverges_from_auto"] = True
        out["attested"] = bool(mo.get("analyst") and mo.get("reason"))
        out["match"] = None  # human judgment → ATTEST, never a clean re-derivation
        return out
    reported = integ.get("reported_area")
    try:
        out["match"] = reported is not None and abs(float(reported) - auto_area) <= max(tol, 1e-9)
    except Exception:
        out["match"] = False
    out["manual_override"] = False
    out["reported_area"] = reported
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Reproduction policy: bit-exact equality is the WRONG default for floating-point
# science (float addition is non-associative; parallel/GPU reductions reorder it;
# even greedy temperature=0 LLM inference is non-deterministic by batch size). A
# bitwise verifier therefore FALSELY REJECTS correct work. Conversely, a stochastic
# method (MCMC/bootstrap/SGD) re-derived under a producer-CHOSEN recorded seed can
# FALSELY ACCEPT a cherry-picked result (seed-hacking). This policy closes both:
#   * a numeric result is GATE-comparable within a tolerance only if that tolerance
#     carries a recognized BASIS (instrument precision / method acceptance criterion
#     / float epsilon / regulatory limit / measurement uncertainty). An unjustified
#     band cannot gate a value -> ATTEST/HOLD (standard-above).
#   * a stochastic method with NO recorded seed is not reproducible -> HOLD.
#   * a stochastic method WITH a seed is reproducible-under-that-seed only: GATE
#     iff the seed was committed BEFORE the data (pre-registration, seed-hack-proof);
#     otherwise ATTEST and disclose seed-conditionality with the seed pinned, so a
#     reviewer can re-run under other seeds.
# ─────────────────────────────────────────────────────────────────────────────
JUSTIFIED_TOLERANCE_BASES = {
    "instrument_precision", "method_acceptance_criterion", "floating_point_epsilon",
    "regulatory_limit", "measurement_uncertainty", "rounding_half_ulp",
}


def assess_reproduction(evidence: dict[str, Any]) -> dict[str, Any] | None:
    """Evaluate the reproduction discipline of a numeric claim. evidence['reproduction']
    = {mode: 'exact'|'bounded', tolerance, tolerance_basis, stochastic:{method, seed,
    committed_before_data}}."""
    rep = evidence.get("reproduction")
    if not isinstance(rep, dict):
        return None
    out: dict[str, Any] = {"mode": str(rep.get("mode", "bounded")).lower()}
    tol = rep.get("tolerance")
    basis = rep.get("tolerance_basis")
    out["tolerance"] = tol
    out["tolerance_basis"] = basis
    # A nonzero band must be justified; exact mode / no band is fine.
    out["tolerance_justified"] = True if (tol in (None, 0, 0.0) or out["mode"] == "exact") \
        else (basis in JUSTIFIED_TOLERANCE_BASES)
    stoch = rep.get("stochastic")
    if isinstance(stoch, dict):
        out["stochastic_method"] = stoch.get("method")
        out["seed"] = stoch.get("seed")
        out["has_seed"] = stoch.get("seed") is not None
        out["committed_before_data"] = bool(stoch.get("committed_before_data"))
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Domain extension (Tier-1, pure-deterministic): cryptographic verification,
# accounting identities, and dimensional consistency. Each re-derives a claimed
# fact bit-exactly (or within a declared tolerance) from inputs, with zero added
# trust assumptions — the SOTA-ranked highest value × cleanest-checkability slice.
# ─────────────────────────────────────────────────────────────────────────────
def rederive_crypto(evidence: dict[str, Any]) -> dict[str, Any] | None:
    """Gold standard: recompute a digest / Merkle root and compare bit-exactly.
    evidence['crypto'] = {algorithm, preimage|{hex}|leaves, claimed_digest|claimed_root}."""
    c = evidence.get("crypto")
    if not isinstance(c, dict):
        return None
    algo = str(c.get("algorithm", "sha256")).lower().replace("-", "")
    if algo not in hashlib.algorithms_available:
        return {"status": "UNKNOWN_ALGORITHM", "algorithm": algo, "match": False}

    def _h(b: bytes) -> str:
        return hashlib.new(algo, b).hexdigest()

    def _norm(d: Any) -> str:
        return str(d or "").split(":")[-1].strip().lower()

    def _as_bytes(x: Any) -> bytes:
        s = _norm(x)
        if s and len(s) % 2 == 0 and all(ch in "0123456789abcdef" for ch in s):
            return bytes.fromhex(s)
        return str(x).encode()

    if c.get("leaves") is not None:  # Merkle root over ordered leaves (pairwise, dup-last)
        layer = [bytes.fromhex(_h(_as_bytes(x))) for x in c["leaves"]]
        while len(layer) > 1:
            if len(layer) % 2:
                layer.append(layer[-1])
            layer = [bytes.fromhex(_h(layer[i] + layer[i + 1])) for i in range(0, len(layer), 2)]
        root = layer[0].hex()
        return {"primitive": "merkle_root", "algorithm": algo, "re_derived": root,
                "claimed": _norm(c.get("claimed_root")), "match": root == _norm(c.get("claimed_root"))}

    pre = c.get("preimage")
    data = bytes.fromhex(pre["hex"]) if isinstance(pre, dict) and "hex" in pre else str(pre).encode()
    digest = _h(data)
    return {"primitive": "digest", "algorithm": algo, "re_derived": digest,
            "claimed": _norm(c.get("claimed_digest")), "match": digest == _norm(c.get("claimed_digest"))}


def _bounded_tol(raw: Any, scale: float, default: float, cap_frac: float = 0.01) -> float | None:
    """Bound a producer-declared tolerance so it cannot be weaponised: a huge
    tolerance must never let an unbalanced ledger / mis-stated ratio pass. Returns
    None (malformed) for NaN/negative; otherwise min(declared, cap_frac·magnitude)
    — at most cap_frac of the figures compared, regardless of what is declared.
    This is the adversarial-gaming guard for every producer-controlled tolerance."""
    if raw is None:
        raw = default
    try:
        r = float(raw)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(r) or r < 0:
        return None
    return min(r, cap_frac * max(abs(scale), 1.0))


def rederive_accounting(evidence: dict[str, Any]) -> dict[str, Any] | None:
    """Re-derive a fundamental accounting identity. evidence['accounting'] =
    {identity: 'debits_equal_credits'|'balance_sheet'|'cash_flow'|'financial_ratio',
    ...inputs, tolerance}. Every comparison tolerance is BOUNDED (see _bounded_tol)
    so a producer cannot pass a false figure by declaring a giant tolerance."""
    a = evidence.get("accounting")
    if not isinstance(a, dict):
        return None
    ident = str(a.get("identity", "")).lower()
    raw_tol = a.get("tolerance")
    try:
        if ident in ("debits_equal_credits", "double_entry"):
            d, cr = sum(map(float, a.get("debits", []))), sum(map(float, a.get("credits", [])))
            tol = _bounded_tol(raw_tol, max(abs(d), abs(cr)), 0.01)
            if tol is None:
                return {"identity": ident, "status": "MALFORMED", "match": False}
            return {"identity": ident, "lhs": round(d, 6), "rhs": round(cr, 6),
                    "match": abs(d - cr) <= tol}
        if ident in ("balance_sheet", "accounting_equation"):
            assets = float(a["assets"]); le = float(a["liabilities"]) + float(a["equity"])
            tol = _bounded_tol(raw_tol, max(abs(assets), abs(le)), 0.01)
            if tol is None:
                return {"identity": ident, "status": "MALFORMED", "match": False}
            return {"identity": ident, "lhs": round(assets, 6), "rhs": round(le, 6),
                    "match": abs(assets - le) <= tol}
        if ident in ("cash_flow", "cash_reconciliation"):
            end = float(a["beginning"]) + float(a.get("operating", 0)) + float(a.get("investing", 0)) + float(a.get("financing", 0))
            ending = float(a["ending"])
            tol = _bounded_tol(raw_tol, max(abs(end), abs(ending)), 0.01)
            if tol is None:
                return {"identity": ident, "status": "MALFORMED", "match": False}
            return {"identity": ident, "lhs": round(end, 6), "rhs": round(ending, 6),
                    "match": abs(end - ending) <= tol}
        if ident in ("financial_ratio", "ratio"):
            # RE-DERIVE a reported ratio from its raw components — never trust the
            # declared value. The one judgement seam (which line items go in the
            # numerator/denominator) is PINNED by ``ratio`` + the named components,
            # so re-derivation gives a single right answer.
            rname = str(a.get("ratio", "")).lower().replace("-", "_").replace(" ", "_")
            # Relative tolerance, bounded so it cannot be weaponised (cap 5%; ratios
            # are unitless so the magnitude scale is 1). NaN/negative -> malformed.
            rtol = _bounded_tol(raw_tol, 1.0, 0.005, cap_frac=0.05)
            if rtol is None:
                return {"identity": ident, "ratio": rname, "status": "MALFORMED", "match": False}
            # A denominator must be a POSITIVE economic magnitude. Non-positive
            # denominators make the ratio undefined/economically meaningless
            # (negative-equity "debt/equity" is not a clean re-derivation) -> route to
            # attest, do not accept an arithmetically-valid but spurious number.
            _POS = {
                "current_ratio": "current_liabilities", "quick_ratio": "current_liabilities",
                "debt_to_equity": "total_equity", "debt_to_equity_ratio": "total_equity",
                "return_on_equity": "total_equity", "roe": "total_equity",
                "return_on_assets": "total_assets", "roa": "total_assets",
                "gross_margin": "revenue", "net_margin": "revenue",
                "eps": "shares_outstanding", "earnings_per_share": "shares_outstanding",
            }
            f = lambda k: float(a[k])  # noqa: E731 — KeyError -> MALFORMED below
            _RATIOS = {
                "current_ratio":        lambda: f("current_assets") / f("current_liabilities"),
                "quick_ratio":          lambda: (f("current_assets") - float(a.get("inventory", 0))) / f("current_liabilities"),
                "debt_to_equity":       lambda: f("total_debt") / f("total_equity"),
                "debt_to_equity_ratio": lambda: f("total_debt") / f("total_equity"),
                "return_on_equity":     lambda: f("net_income") / f("total_equity"),
                "roe":                  lambda: f("net_income") / f("total_equity"),
                "return_on_assets":     lambda: f("net_income") / f("total_assets"),
                "roa":                  lambda: f("net_income") / f("total_assets"),
                "gross_margin":         lambda: (f("revenue") - f("cogs")) / f("revenue"),
                "net_margin":           lambda: f("net_income") / f("revenue"),
                "eps":                  lambda: (f("net_income") - float(a.get("preferred_dividends", 0))) / f("shares_outstanding"),
                "earnings_per_share":   lambda: (f("net_income") - float(a.get("preferred_dividends", 0))) / f("shares_outstanding"),
            }
            if rname not in _RATIOS:
                return {"identity": ident, "ratio": rname, "status": "UNKNOWN_RATIO", "match": False}
            denom_field = _POS.get(rname)
            if denom_field is not None and float(a[denom_field]) <= 0:
                return {"identity": ident, "ratio": rname, "status": "NONPOSITIVE_DENOMINATOR", "match": False}
            recomputed = _RATIOS[rname]()
            declared = float(a["reported"])
            if not (math.isfinite(recomputed) and math.isfinite(declared)):
                return {"identity": ident, "ratio": rname, "status": "MALFORMED", "match": False}
            # Hybrid relative scale: max(|recomputed|,|declared|) so a near-zero true
            # value cannot let an absolute lie hide as a "small relative error".
            denom = max(abs(recomputed), abs(declared), 1e-9)
            ok = abs(recomputed - declared) / denom <= rtol
            return {"identity": ident, "ratio": rname, "lhs": round(declared, 6),
                    "rhs": round(recomputed, 6), "re_derived": round(recomputed, 6),
                    "match": ok}
    except (KeyError, ValueError, TypeError, ZeroDivisionError):
        return {"identity": ident, "status": "MALFORMED", "match": False}
    return {"identity": ident, "status": "UNKNOWN_IDENTITY", "match": False}


def rederive_xbrl(evidence: dict[str, Any]) -> dict[str, Any] | None:
    """Re-derive a financial ratio whose components are pulled from a filed XBRL
    instance via Arelle (not hand-typed). evidence['xbrl'] = {instance, ratio,
    reported, tolerance?}. Delegates the actual check to rederive_accounting so the
    same bounded-tolerance / GIGO guards apply. Returns match None (-> ATTEST) when
    Arelle is unavailable or the filing lacks the needed concepts: a filing we
    cannot fully extract is not silently accepted."""
    x = evidence.get("xbrl")
    if not isinstance(x, dict):
        return None
    instance = x.get("instance") or x.get("instance_path")
    ratio, reported = x.get("ratio"), x.get("reported")
    if not (instance and ratio and reported is not None):
        return {"status": "MALFORMED", "match": False}
    try:
        import capas_xbrl
    except Exception:
        return {"status": "ARELLE_UNAVAILABLE", "match": None}
    try:
        acc = capas_xbrl.build_accounting_evidence(instance, str(ratio), float(reported), x.get("tolerance"))
    except Exception as e:
        return {"status": "EXTRACTION_ERROR", "detail": repr(e), "match": None}
    if acc.get("status") not in ("OK", None) and "match" not in acc:
        return {"status": acc.get("status"), "ratio": acc.get("ratio"), "match": None,
                "xbrl_extraction": acc.get("xbrl_extraction")}
    r = rederive_accounting({"accounting": acc})
    if isinstance(r, dict):
        r["xbrl_sources"] = acc.get("xbrl_sources")
    return r


# SI base dimensions as exponent vectors [M, L, T, I, Θ, N, J] (kg,m,s,A,K,mol,cd).
_DIM_BASE = ("M", "L", "T", "I", "Θ", "N", "J")
_UNIT_DIM: dict[str, tuple[int, ...]] = {
    "kg": (1, 0, 0, 0, 0, 0, 0), "g": (1, 0, 0, 0, 0, 0, 0), "m": (0, 1, 0, 0, 0, 0, 0),
    "s": (0, 0, 1, 0, 0, 0, 0), "a": (0, 0, 0, 1, 0, 0, 0), "k": (0, 0, 0, 0, 1, 0, 0),
    "mol": (0, 0, 0, 0, 0, 1, 0), "cd": (0, 0, 0, 0, 0, 0, 1),
    "n": (1, 1, -2, 0, 0, 0, 0), "j": (1, 2, -2, 0, 0, 0, 0), "w": (1, 2, -3, 0, 0, 0, 0),
    "pa": (1, -1, -2, 0, 0, 0, 0), "c": (0, 0, 1, 1, 0, 0, 0), "v": (1, 2, -3, -1, 0, 0, 0),
    "hz": (0, 0, -1, 0, 0, 0, 0), "m/s": (0, 1, -1, 0, 0, 0, 0), "m/s2": (0, 1, -2, 0, 0, 0, 0),
    "m/s^2": (0, 1, -2, 0, 0, 0, 0), "m2": (0, 2, 0, 0, 0, 0, 0), "m3": (0, 3, 0, 0, 0, 0, 0),
}
# Physical quantity -> its dimension. The unit a claim attaches must match.
_QUANTITY_DIM: dict[str, tuple[int, ...]] = {
    "force": (1, 1, -2, 0, 0, 0, 0), "energy": (1, 2, -2, 0, 0, 0, 0),
    "work": (1, 2, -2, 0, 0, 0, 0), "power": (1, 2, -3, 0, 0, 0, 0),
    "pressure": (1, -1, -2, 0, 0, 0, 0), "velocity": (0, 1, -1, 0, 0, 0, 0),
    "speed": (0, 1, -1, 0, 0, 0, 0), "acceleration": (0, 1, -2, 0, 0, 0, 0),
    "mass": (1, 0, 0, 0, 0, 0, 0), "length": (0, 1, 0, 0, 0, 0, 0),
    "distance": (0, 1, 0, 0, 0, 0, 0), "time": (0, 0, 1, 0, 0, 0, 0),
    "frequency": (0, 0, -1, 0, 0, 0, 0), "area": (0, 2, 0, 0, 0, 0, 0),
    "volume": (0, 3, 0, 0, 0, 0, 0), "voltage": (1, 2, -3, -1, 0, 0, 0),
}


def rederive_dimensions(evidence: dict[str, Any]) -> dict[str, Any] | None:
    """Dimensional consistency: a claimed physical quantity must carry a unit of
    the matching SI dimension. evidence['dimensions'] = {quantity, unit}."""
    d = evidence.get("dimensions")
    if not isinstance(d, dict):
        return None
    q = str(d.get("quantity", "")).lower().strip()
    u = str(d.get("unit", "")).lower().strip().replace(" ", "")
    if q not in _QUANTITY_DIM:
        return {"status": "UNKNOWN_QUANTITY", "quantity": q, "match": None}
    if u not in _UNIT_DIM:
        return {"status": "UNKNOWN_UNIT", "unit": u, "match": None}
    qd, ud = _QUANTITY_DIM[q], _UNIT_DIM[u]
    match = qd == ud

    def _fmt(vec: tuple[int, ...]) -> str:
        return " ".join(f"{b}^{e}" for b, e in zip(_DIM_BASE, vec) if e) or "dimensionless"

    return {"quantity": q, "unit": u, "expected_dim": _fmt(qd), "unit_dim": _fmt(ud), "match": match}


# Standard atomic weights (g/mol), enough for mass-balance of common reactions.
_ATOMIC_WEIGHT = {
    "H": 1.008, "He": 4.0026, "Li": 6.94, "Be": 9.0122, "B": 10.81, "C": 12.011,
    "N": 14.007, "O": 15.999, "F": 18.998, "Ne": 20.180, "Na": 22.990, "Mg": 24.305,
    "Al": 26.982, "Si": 28.085, "P": 30.974, "S": 32.06, "Cl": 35.45, "Ar": 39.948,
    "K": 39.098, "Ca": 40.078, "Fe": 55.845, "Cu": 63.546, "Zn": 65.38, "Ag": 107.87,
    "I": 126.90, "Ba": 137.33, "Pt": 195.08, "Au": 196.97, "Hg": 200.59, "Pb": 207.2,
    "Mn": 54.938, "Cr": 51.996, "Ni": 58.693, "Br": 79.904, "Sn": 118.71,
}
_FORMULA_TOKEN = re.compile(r"([A-Z][a-z]?|\(|\)|\d+)")


def _parse_formula(formula: str) -> dict[str, float]:
    """Parse a chemical formula into element->count, honouring nested parentheses
    and multipliers (e.g. Ca(OH)2 -> {Ca:1, O:2, H:2})."""
    tokens = _FORMULA_TOKEN.findall(formula or "")

    def parse(i: int) -> tuple[dict[str, float], int]:
        counts: dict[str, float] = {}
        while i < len(tokens):
            t = tokens[i]
            if t == "(":
                sub, i = parse(i + 1)
                mult = 1
                if i < len(tokens) and tokens[i].isdigit():
                    mult = int(tokens[i]); i += 1
                for e, c in sub.items():
                    counts[e] = counts.get(e, 0) + c * mult
            elif t == ")":
                return counts, i + 1
            elif t[0].isalpha():
                el = t; i += 1
                n = 1
                if i < len(tokens) and tokens[i].isdigit():
                    n = int(tokens[i]); i += 1
                if el not in _ATOMIC_WEIGHT:
                    raise ValueError(f"unknown element {el}")
                counts[el] = counts.get(el, 0) + n
            else:
                i += 1
        return counts, i

    counts, _ = parse(0)
    return counts


def rederive_stoichiometry(evidence: dict[str, Any]) -> dict[str, Any] | None:
    """Re-derive that a chemical equation conserves atoms (and mass). evidence
    ['stoichiometry'] = {reactants:[{formula, coeff}], products:[{formula, coeff}]}.
    Atom conservation is exact and deterministic — the equation balances or it does
    not. An unparseable/empty equation is MALFORMED (-> ATTEST), never accepted."""
    st = evidence.get("stoichiometry")
    if not isinstance(st, dict):
        return None
    try:
        sides: dict[str, dict[str, float]] = {"reactants": {}, "products": {}}
        masses = {"reactants": 0.0, "products": 0.0}
        for side in ("reactants", "products"):
            species = st.get(side) or []
            if not species:
                return {"status": "MALFORMED", "match": False, "reason": f"no {side}"}
            for sp in species:
                counts = _parse_formula(sp["formula"])
                coeff = float(sp.get("coeff", 1))
                for e, c in counts.items():
                    sides[side][e] = sides[side].get(e, 0) + c * coeff
                    masses[side] += c * coeff * _ATOMIC_WEIGHT[e]
    except (KeyError, ValueError, TypeError):
        return {"status": "MALFORMED", "match": False}
    elements = set(sides["reactants"]) | set(sides["products"])
    imbalanced = {e: [sides["reactants"].get(e, 0), sides["products"].get(e, 0)]
                  for e in sorted(elements)
                  if abs(sides["reactants"].get(e, 0) - sides["products"].get(e, 0)) > 1e-9}
    return {"reactant_atoms": sides["reactants"], "product_atoms": sides["products"],
            "imbalanced": imbalanced, "reactant_mass": round(masses["reactants"], 4),
            "product_mass": round(masses["products"], 4), "match": not imbalanced}


# ─────────────────────────────────────────────────────────────────────────────
# ZK rung — verify a result over HIDDEN data (PHI / licensed / proprietary) via a
# zero-knowledge proof, extending GATE scope to data that cannot be re-shipped.
# Soundness is delegated to a REGISTERED verifying backend (production: EZKL /
# groth16 / halo2). Ships with a reference commitment-binding backend so the
# protocol is runnable and testable; an UNREGISTERED verifying key is ATTEST-only.
# ─────────────────────────────────────────────────────────────────────────────
def _ref_commitment_backend(proof: dict[str, Any], public_inputs: dict[str, Any], statement: Any) -> bool:
    """Reference backend: verify the public output is bound to a committed input
    (a real, deterministic commitment opening — NOT full SNARK soundness)."""
    opening = proof.get("opening") or {}
    nonce = proof.get("nonce", "")
    recomputed = "sha256:" + hashlib.sha256(
        f"{opening.get('input_hash')}|{opening.get('output')}|{nonce}".encode()).hexdigest()
    if recomputed != public_inputs.get("commitment"):
        return False
    try:
        return abs(float(opening.get("output")) - float(public_inputs.get("claimed_output"))) \
            <= float(public_inputs.get("tolerance", 0) or 0)
    except Exception:
        return False


TRUSTED_ZK_BACKENDS: dict[str, Any] = {"capas-ref-commitment": _ref_commitment_backend}

try:  # real arithmetic-circuit (R1CS) backend — the SNARK front-end made runnable
    from capas_circuits import r1cs_backend as _r1cs_backend
    TRUSTED_ZK_BACKENDS["capas-r1cs"] = _r1cs_backend
except Exception:  # pragma: no cover
    pass

try:  # production succinct/ZK backend via EZKL (KZG/halo2), if installed
    from capas_ezkl import ezkl_backend as _ezkl_backend
    TRUSTED_ZK_BACKENDS["ezkl"] = _ezkl_backend
except Exception:  # pragma: no cover
    pass


def register_zk_backend(vk_id: str, verifier) -> None:
    """Register a production verifying backend (e.g. an EZKL/groth16 verifier)."""
    TRUSTED_ZK_BACKENDS[vk_id] = verifier


def verify_zk_proof(evidence: dict[str, Any]) -> dict[str, Any] | None:
    zk = evidence.get("zk_proof")
    if not isinstance(zk, dict):
        return None
    vk = zk.get("verifying_key_id")
    backend = TRUSTED_ZK_BACKENDS.get(vk)
    if backend is None:
        return {"status": "UNTRUSTED_VK", "verifying_key_id": vk, "verified": None}
    try:
        ok = bool(backend(zk.get("proof") or {}, zk.get("public_inputs") or {}, zk.get("statement")))
    except Exception as e:
        return {"status": "ERROR", "error": str(e), "verified": False, "verifying_key_id": vk}
    return {"status": "VERIFIED" if ok else "FAILED", "verifying_key_id": vk,
            "verified": ok, "scheme": zk.get("scheme"), "statement": zk.get("statement")}


def _artifact_hash(evidence: dict[str, Any]) -> str | None:
    """Bind the re-derivable artifacts into the receipt so a third party can
    re-check against the exact same inputs."""
    keys = ("raw_data", "raw", "computation", "derivation", "environment",
            "registry", "integration", "zk_proof", "quantum_circuit", "quantum_proof",
            "crypto", "accounting", "dimensions", "reproduction", "xbrl", "physical", "stoichiometry")
    artifacts = {k: evidence[k] for k in keys if k in evidence}
    if not artifacts:
        return None
    canonical = json.dumps(artifacts, sort_keys=True, separators=(",", ":"), default=str)
    return "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()


# ─────────────────────────────────────────────────────────────────────────────
# Receipt (#2): portable, hash-bound, re-checkable verdict artifact.
# ─────────────────────────────────────────────────────────────────────────────
# ── Secure receipt: engine pinning + Ed25519 signature (SCITT / VC 2.0 style) ──
# A receipt bound only by a hash proves integrity but not authorship — anyone can
# forge one. Following IETF SCITT (signed statement -> receipt) and W3C VC 2.0
# (Ed25519 Data Integrity), CAPAS signs the canonical receipt with an Ed25519 key
# and pins the exact engine digest, so a verifier checks WHO issued it and WHICH
# engine produced it. Signing degrades gracefully if `cryptography` is absent.
_ENGINE_DIGEST: str | None = None
_SIGNING_KEY = None  # cached Ed25519 private key for this process


def _engine_digest() -> str:
    global _ENGINE_DIGEST
    if _ENGINE_DIGEST is None:
        try:
            src = open(__file__, "rb").read()
            _ENGINE_DIGEST = "sha256:" + hashlib.sha256(src).hexdigest()
        except Exception:
            _ENGINE_DIGEST = "sha256:unknown"
    return _ENGINE_DIGEST


def _get_signing_key():
    """Ed25519 key for this CAPAS instance. From env CAPAS_SIGNING_SEED (64 hex
    chars = 32-byte seed) for a stable, publishable identity; else an ephemeral
    per-process key. Returns None if `cryptography` is unavailable."""
    global _SIGNING_KEY
    if _SIGNING_KEY is not None:
        return _SIGNING_KEY
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        seed = os.environ.get("CAPAS_SIGNING_SEED", "")
        if len(seed) == 64:
            _SIGNING_KEY = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(seed))
        else:
            _SIGNING_KEY = Ed25519PrivateKey.generate()
        return _SIGNING_KEY
    except Exception:
        return None


def _sign_receipt(canonical: str) -> dict[str, Any] | None:
    key = _get_signing_key()
    if key is None:
        return None
    from cryptography.hazmat.primitives import serialization
    pub = key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)
    sig = key.sign(canonical.encode())
    return {"algorithm": "Ed25519", "public_key": pub.hex(), "signature": sig.hex(),
            "standard": "IETF SCITT / W3C VC 2.0 (Data Integrity EdDSA)"}


def verify_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    """Independently verify a CAPAS receipt's signature against its own body.
    Returns {signature_valid, engine_digest_pinned, verdict, ...}."""
    sigblock = receipt.get("signature")
    body = {k: v for k, v in receipt.items() if k not in ("signature", "receipt_id")}
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    out = {"verdict": receipt.get("verified_verdict"), "scope": receipt.get("scope"),
           "engine_digest": receipt.get("engine_digest"), "engine_digest_pinned": bool(receipt.get("engine_digest")),
           "receipt_id_matches": receipt.get("receipt_id") ==
           "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()[:32]}
    if not sigblock:
        out["signature_valid"] = None
        return out
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        pub = Ed25519PublicKey.from_public_bytes(bytes.fromhex(sigblock["public_key"]))
        pub.verify(bytes.fromhex(sigblock["signature"]), canonical.encode())
        out["signature_valid"] = True
    except Exception:
        out["signature_valid"] = False
    return out


# Fail-closed by construction: a verdict may be ACCEPT only if a rung resolved it
# POSITIVELY (re-derived or attested). If re-derivable evidence was supplied but no
# rung returned a positive status, the verdict cannot stay ACCEPT — a forgotten /
# unhandled case can never become a false-accept by architecture, not by discipline.
_POSITIVE_STATUSES = {"VERIFIED", "ATTESTED", "ATTESTED_SURFACED", "PRECOMMITTED_SEED", "RECONCILED"}
_RE_DERIVABLE_KEYS = {"raw_data", "raw", "computation", "derivation", "integration", "registry",
                      "zk_proof", "quantum_circuit", "crypto", "accounting", "dimensions",
                      "xbrl", "physical", "stoichiometry"}


def _fail_closed(final: str, scope: str, checks: list, evidence: dict, rationale: list) -> tuple[str, str]:
    if final != "ACCEPT":
        return final, scope
    if not (set(evidence) & _RE_DERIVABLE_KEYS):
        return final, scope  # no re-derivable artifact supplied -> base-gate accept stands
    if any(c.get("status") in _POSITIVE_STATUSES for c in checks):
        return final, scope  # something resolved it positively -> ACCEPT stands
    rationale.append(
        "Fail-closed: re-derivable evidence was supplied but no rung resolved it (re-derived "
        "or attested). The verdict is held rather than accepted — absence of a passed check is "
        "never treated as a passed check.")
    checks.append({"check": "fail_closed_guard", "status": "UNRESOLVED_EVIDENCE"})
    return "HOLD", "ATTEST"


def _receipt(payload, base_verdict, final, scope, tier, checks, rationale) -> dict[str, Any]:
    claim = payload.get("claim", {}) or {}
    body = {
        "schema": "capas-verification-receipt-v1",
        "claim_id": claim.get("id"),
        "claim_type": claim.get("type"),
        "base_gate_verdict": base_verdict,
        "verified_verdict": final,
        "scope": scope,                 # GATE (re-derivable) | ATTEST (signed only)
        "verification_tier": tier,      # FORM | RE-DERIVED | ATTEST
        "checks": checks,
        "rationale": rationale,
        "residual_disclosure": (
            "CAPAS verifies record-to-evidence RE-DERIVATION, not evidence-to-reality "
            "truth (the GIGO residual is irreducible). ATTEST-scope evidence is signed "
            "and bound, never marketed as verified."
        ),
        "decision_path": "deterministic; no LLM",
        "engine_digest": _engine_digest(),   # pin EXACTLY which engine decided
    }
    artifact_hash = _artifact_hash(payload.get("evidence", {}) or {})
    if artifact_hash:
        body["evidence_artifact_hash"] = artifact_hash
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    body["receipt_id"] = "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()[:32]
    sig = _sign_receipt(canonical)
    if sig is not None:
        body["signature"] = sig            # Ed25519 over the canonical body (SCITT/VC 2.0 style)
    return body


# ─────────────────────────────────────────────────────────────────────────────
# The proof-carrying gate.
# ─────────────────────────────────────────────────────────────────────────────
# Evidence keys that are CAPAS-verify EXTENSIONS (re-derivable artifacts / provenance),
# not part of the base evidence contract. They are stripped before the base gate runs
# (which rejects unknown fields) and consumed by this layer instead.
_EXTENSION_KEYS = {"raw_data", "raw", "computation", "derivation", "environment",
                   "registry", "integration", "zk_proof", "quantum_circuit", "quantum_proof",
                   "crypto", "accounting", "dimensions", "reproduction", "xbrl", "physical", "stoichiometry",
                   *PROVENANCE_KEYS}

try:  # quantum re-derivation rung (needs numpy); deterministic statevector + frontier
    from capas_quantum import rederive_quantum as _rederive_quantum
except Exception:  # pragma: no cover
    _rederive_quantum = None


def _base_payload(payload: dict[str, Any]) -> dict[str, Any]:
    evidence = {k: v for k, v in (payload.get("evidence") or {}).items() if k not in _EXTENSION_KEYS}
    return {**payload, "evidence": evidence}


_VERIFY_CACHE: dict[str, dict[str, Any]] = {}
_VERIFY_CACHE_CAP = 512


def _payload_key(payload: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def verify(payload: dict[str, Any], use_cache: bool = True) -> dict[str, Any]:
    # Memoize by content hash: an identical payload re-derives to an identical
    # verdict, so re-verification is O(1) (idempotent). Disable with use_cache=False.
    cache_key = _payload_key(payload) if use_cache else None
    if cache_key is not None and cache_key in _VERIFY_CACHE:
        return _VERIFY_CACHE[cache_key]

    base = capas.decide_external_claim(_base_payload(payload))
    base_verdict = base.get("verdict") if isinstance(base, dict) else getattr(base, "verdict", "HOLD")

    claim = payload.get("claim", {}) or {}
    evidence = payload.get("evidence", {}) or {}
    ctype = claim.get("type")
    text = claim.get("text", "")

    checks: list[dict[str, Any]] = []
    rationale: list[str] = []
    final = base_verdict
    scope = "GATE"

    # (1) Anchor scan — domain-aware. A known law refutes a claim only INSIDE its
    # domain (REJECT); a claim that names an off-baseline condition without
    # quantifying it leaves the constant inapplicable -> abstain (HOLD, route up).
    # Universal bounds (hold in every condition) are checked first and override:
    # a physical impossibility cannot be saved by any context.
    hits = (universal_bound_violations(text) + anchor_contradictions(text)
            + holevo_information_contradictions(text) + check_physical(evidence.get("physical")))
    contradictions = [h for h in hits if h.get("kind") != "abstain"]
    abstentions = [h for h in hits if h.get("kind") == "abstain"]
    if contradictions:
        h = contradictions[0]
        checks.append({"check": "anchor_contradiction", "status": "FAIL", "detail": contradictions})
        prov = ""
        if h.get("re_derived_from"):
            prov = (f" re-derived via {h['re_derived_from']} at {h['pressure_mmHg']} mmHg"
                    if h.get("pressure_mmHg") is not None else f" ({h['re_derived_from']})")
        detail = f" (asserted {h['asserted']}{h['unit']} vs {h.get('truth')}{h['unit']}{prov})"
        rationale.append(f"Claim contradicts a known anchor: {h['desc']}{detail}. Rejected by re-derivation.")
        final = "REJECT"
    elif abstentions:
        h = abstentions[0]
        checks.append({"check": "anchor_domain_undefined", "status": "ABSTAIN", "detail": abstentions})
        rationale.append(
            f"Anchor '{h['anchor']}' does not apply: {h['reason']} CAPAS does not reject a "
            "possibly-true claim on a context-blind constant, nor accept it without the "
            "condition; held for the condition to be quantified or attested.")
        scope = "ATTEST"
        if final == "ACCEPT":
            final = "HOLD"

    # Reproduction policy: bit-exact vs bounded-error, and stochastic/seed discipline.
    # Closes the two real determinism cracks (false-reject from float/GPU reordering;
    # false-accept from seed-hacking) without abandoning re-derivation.
    if final == "ACCEPT":
        rep = assess_reproduction(evidence)
        if rep is not None:
            if not rep["tolerance_justified"]:
                checks.append({"check": "reproduction_tolerance", "status": "UNJUSTIFIED_BAND", "detail": rep})
                scope = "ATTEST"; final = "HOLD"
                rationale.append(
                    f"A comparison tolerance ({rep['tolerance']}) is declared without a recognized "
                    f"basis (got {rep.get('tolerance_basis')!r}; expected one of "
                    f"{sorted(JUSTIFIED_TOLERANCE_BASES)}). An unjustified band can pass a wrong "
                    "value — held until the tolerance is tied to an instrument/method/regulatory basis.")
            if final == "ACCEPT" and rep.get("stochastic_method"):
                if not rep.get("has_seed"):
                    checks.append({"check": "reproduction_seed", "status": "NO_SEED", "detail": rep})
                    scope = "ATTEST"; final = "HOLD"
                    rationale.append(
                        f"The result is produced by a stochastic method ({rep['stochastic_method']}) "
                        "with NO recorded seed: it is not reproducible. Record the seed to re-derive.")
                elif rep.get("committed_before_data"):
                    checks.append({"check": "reproduction_seed", "status": "PRECOMMITTED_SEED", "detail": rep})
                    rationale.append(
                        f"Stochastic method ({rep['stochastic_method']}) re-derives under a seed "
                        f"committed BEFORE the data (seed={rep.get('seed')!r}); pre-registration "
                        "rules out seed-hacking — GATE-eligible.")
                else:
                    checks.append({"check": "reproduction_seed", "status": "SEED_CONDITIONAL", "detail": rep})
                    scope = "ATTEST"
                    rationale.append(
                        f"Stochastic method ({rep['stochastic_method']}) re-derives ONLY under the "
                        f"producer-chosen seed={rep.get('seed')!r}. Reproducible-under-that-seed is not "
                        "robustness across seeds (seed-hacking risk); the seed is pinned for a reviewer "
                        "to re-run under others — ATTEST, not GATE.")

    # The base gate already rejects/holds the self-failing cases (p>alpha, missing,
    # required-boolean-false). We only ADD scrutiny where the base said ACCEPT.
    if final == "ACCEPT":
        # Passage Point A primitive: re-derive a reported NUMBER from its raw inputs.
        # Applies to any claim type (CDS calibration/assay, ADaM derivations, financial
        # metrics). A reported value that does not re-derive is fabricated -> REJECT.
        calc = rederive_calculation(evidence)
        if calc is not None:
            if calc.get("match") is True:
                checks.append({"check": "calculation_rederivation", "status": "VERIFIED", "detail": calc})
                rationale.append(
                    f"Reported value {calc['reported']} re-derives from its raw inputs via "
                    f"{calc['operation']} (= {calc['re_derived']}). Verified by re-computation, not trusted."
                )
            elif calc.get("match") is False:
                checks.append({"check": "calculation_rederivation", "status": "FAIL", "detail": calc})
                final = "REJECT"
                rationale.append(
                    f"Reported value {calc['reported']} does NOT re-derive from its raw inputs "
                    f"({calc['operation']} gives {calc.get('re_derived')}). The reported number is "
                    "fabricated relative to the raw data — rejected (spreadsheet-integrity pattern)."
                )
            elif calc.get("match") is None:
                # Unsupported operation -> the engine cannot re-derive it; must not pass
                # as GATE-verified. Absence of a check is not a passed check (GIGO guard).
                scope = "ATTEST"; final = "HOLD"
                checks.append({"check": "calculation_rederivation", "status": calc.get("status", "UNRESOLVED"), "detail": calc})
                rationale.append(
                    f"Computation not re-derivable ({calc.get('status', 'unresolved')}: operation "
                    f"{calc.get('operation')!r} is not supported by the engine) — held for a supported "
                    "operation or attestation, not accepted."
                )

    # Passage Point B: re-derive a submitted derived dataset (ADaM) from its source
    # (SDTM) inside a pinned environment, and reconcile against the public registry.
    if final == "ACCEPT" and evidence.get("derivation") is not None:
        env = environment_pinned(evidence)
        if env is not None and not env["pinned"]:
            checks.append({"check": "environment_pinning", "status": "UNPINNED",
                           "detail": {"missing": env["missing"]}})
            scope = "ATTEST"; final = "HOLD"
            rationale.append(
                "Dataset re-derivation requires a fully pinned environment "
                f"(missing: {', '.join(env['missing'])}). Without it the result is not "
                "reproducible — ATTEST only, not gated."
            )
        else:
            ds = rederive_dataset(evidence)
            if ds and ds.get("match") is True:
                checks.append({"check": "dataset_rederivation", "status": "VERIFIED", "detail":
                               {"rows": ds["rows"], "checks": ds["checks"]}})
                rationale.append(
                    f"All {ds['checks']} derived values across {ds['rows']} submitted rows "
                    "re-derive from source within tolerance: the derived dataset is verified, "
                    "not conformance-checked."
                )
            elif ds and ds.get("match") is False and ds.get("status") in ("UNSUPPORTED_OP", "MALFORMED"):
                # Cannot re-derive (unsupported rule op / ill-formed source-submitted) ->
                # not GATE-verifiable. Absence of a check is not a passed check (GIGO guard).
                scope = "ATTEST"; final = "HOLD"
                checks.append({"check": "dataset_rederivation", "status": ds.get("status"), "detail": ds})
                rationale.append(
                    f"Derived dataset not re-derivable ({ds.get('status')}: e.g. rule operation "
                    f"{ds.get('op')!r}); the engine cannot reproduce it — held for supported rules or "
                    "attestation, not accepted."
                )
            elif ds and ds.get("match") is None:
                scope = "ATTEST"; final = "HOLD"
                checks.append({"check": "dataset_rederivation", "status": ds.get("status", "UNRESOLVED"), "detail": ds})
                rationale.append(
                    f"Derived dataset not re-derivable ({ds.get('status', 'unresolved')}); held for "
                    "supported rules or attestation, not accepted."
                )
            elif ds and ds.get("match") is False:
                checks.append({"check": "dataset_rederivation", "status": "FAIL", "detail":
                               {"mismatch_count": ds.get("mismatch_count"), "examples": ds.get("mismatches")}})
                final = "REJECT"
                rationale.append(
                    f"{ds.get('mismatch_count')} submitted value(s) do NOT re-derive from source "
                    "(e.g. " + json.dumps((ds.get("mismatches") or [{}])[0]) + "). The derived "
                    "dataset diverges from its raw data — rejected (the discrepancy Pinnacle 21 misses)."
                )
    # Passage Point A v2: parameterized peak integration + manual_override surfacing.
    if final == "ACCEPT" and evidence.get("integration") is not None:
        ig = rederive_integration(evidence)
        if ig and ig.get("manual_override"):
            scope = "ATTEST"
            if ig.get("diverges_from_auto") and not ig.get("attested"):
                final = "HOLD"
                checks.append({"check": "manual_integration_override", "status": "UNJUSTIFIED_DIVERGENCE", "detail": ig})
                rationale.append(
                    f"A manual re-integration ({ig.get('manual_area')}) diverges from the automatic "
                    f"re-derivation ({ig['auto_area']}) and carries NO signed analyst/reason. This is the "
                    "data-integrity override pattern — held pending signed justification."
                )
            else:
                checks.append({"check": "manual_integration_override", "status": "ATTESTED_SURFACED", "detail": ig})
                rationale.append(
                    f"Manual re-integration surfaced (analyst={ig.get('analyst')}, reason={ig.get('reason')}); "
                    f"diverges from automatic by |{ig.get('manual_area')}−{ig['auto_area']}|. ATTEST: signed human "
                    "judgment, not silently reproduced — the inspector sees exactly what was overridden and why."
                )
        elif ig and ig.get("match") is True:
            checks.append({"check": "peak_integration_rederivation", "status": "VERIFIED", "detail": ig})
            rationale.append(
                f"Reported peak area {ig.get('reported_area')} re-derives from the raw signal by automatic "
                f"integration (= {ig['auto_area']}). Verified, not trusted."
            )
        elif ig and ig.get("match") is False:
            checks.append({"check": "peak_integration_rederivation", "status": "FAIL", "detail": ig})
            final = "REJECT"
            rationale.append(
                f"Reported peak area {ig.get('reported_area')} does NOT re-derive from the raw signal "
                f"(automatic integration gives {ig['auto_area']}) — rejected."
            )

    # Domain extension (Tier-1): cryptographic digest/Merkle, accounting identity,
    # dimensional consistency — bit-exact deterministic re-derivation.
    if final == "ACCEPT" and evidence.get("crypto") is not None:
        cr = rederive_crypto(evidence)
        if cr and cr.get("match") is True:
            checks.append({"check": "crypto_rederivation", "status": "VERIFIED", "detail": cr})
            rationale.append(
                f"{cr['primitive']} re-derives bit-exactly ({cr['algorithm']}): re-computed "
                f"{cr['re_derived'][:16]}… equals the claimed value. Verified by recomputation.")
        elif cr and cr.get("match") is False:
            checks.append({"check": "crypto_rederivation", "status": "FAIL", "detail": cr})
            final = "REJECT"
            rationale.append(
                f"{cr.get('primitive', 'digest')} does NOT match: re-computed "
                f"{str(cr.get('re_derived'))[:16]}… ≠ claimed {str(cr.get('claimed'))[:16]}… — rejected.")

    if final == "ACCEPT" and evidence.get("accounting") is not None:
        ac = rederive_accounting(evidence)
        _is_ratio = ac is not None and ac.get("ratio") is not None
        if ac and ac.get("match") is True:
            checks.append({"check": "accounting_identity", "status": "VERIFIED", "detail": ac})
            if _is_ratio:
                rationale.append(
                    f"Financial ratio '{ac['ratio']}' re-derives from its components: reported "
                    f"{ac['lhs']} = re-computed {ac['rhs']} (re-derived from raw line items, not trusted).")
            else:
                rationale.append(
                    f"Accounting identity '{ac['identity']}' holds: {ac['lhs']} = {ac['rhs']} "
                    "(re-derived, not trusted).")
        elif ac and ac.get("match") is False and ac.get("status") in (
                "UNKNOWN_RATIO", "UNKNOWN_IDENTITY", "MALFORMED", "NONPOSITIVE_DENOMINATOR"):
            # Cannot re-derive (unrecognised/ill-formed) -> do not silently accept; hold to attest.
            scope = "ATTEST"; final = "HOLD"
            checks.append({"check": "accounting_identity", "status": ac.get("status"), "detail": ac})
            rationale.append(
                f"Accounting claim could not be re-derived ({ac.get('status')}); not re-derivable by the "
                "engine — held for a recognised identity/ratio with its raw components, or attestation.")
        elif ac and ac.get("match") is False:
            checks.append({"check": "accounting_identity", "status": "FAIL", "detail": ac})
            final = "REJECT"
            if _is_ratio:
                rationale.append(
                    f"Financial ratio '{ac['ratio']}' does NOT re-derive: reported {ac['lhs']} ≠ "
                    f"re-computed {ac['rhs']} from the raw line items — rejected by re-derivation.")
            else:
                rationale.append(
                    f"Accounting identity '{ac['identity']}' is violated: {ac.get('lhs')} ≠ "
                    f"{ac.get('rhs')} — the books do not balance; rejected.")

    # XBRL loop: components pulled from a filed instance (Arelle), re-derived by the
    # same bounded-tolerance accounting check — no hand-typed numbers.
    if final == "ACCEPT" and evidence.get("xbrl") is not None:
        xb = rederive_xbrl(evidence)
        if xb and xb.get("match") is True:
            checks.append({"check": "xbrl_ratio_rederivation", "status": "VERIFIED", "detail": xb})
            rationale.append(
                f"Financial ratio '{xb.get('ratio')}' re-derives from the XBRL filing's own line "
                f"items ({xb.get('xbrl_sources')}): reported {xb.get('lhs')} = re-computed {xb.get('rhs')}. "
                "Components read from the filing via Arelle, not supplied by the producer.")
        elif xb and xb.get("match") is False:
            checks.append({"check": "xbrl_ratio_rederivation", "status": "FAIL", "detail": xb})
            final = "REJECT"
            rationale.append(
                f"Financial ratio '{xb.get('ratio')}' does NOT re-derive from the XBRL filing "
                f"(reported {xb.get('lhs')} ≠ re-computed {xb.get('rhs')}) — rejected.")
        elif xb and xb.get("match") is None:
            scope = "ATTEST"; final = "HOLD"
            checks.append({"check": "xbrl_ratio_rederivation", "status": xb.get("status", "UNRESOLVED"), "detail": xb})
            rationale.append(
                f"Could not re-derive from the XBRL filing ({xb.get('status')}: e.g. Arelle missing "
                "or the filing lacks the needed concepts). Not silently accepted — held for a complete "
                "filing or attestation.")

    if final == "ACCEPT" and evidence.get("dimensions") is not None:
        dm = rederive_dimensions(evidence)
        if dm and dm.get("match") is True:
            checks.append({"check": "dimensional_consistency", "status": "VERIFIED", "detail": dm})
            rationale.append(
                f"Dimensional check: '{dm['quantity']}' in {dm['unit']} is consistent "
                f"({dm['expected_dim']}). Verified.")
        elif dm and dm.get("match") is False:
            checks.append({"check": "dimensional_consistency", "status": "FAIL", "detail": dm})
            final = "REJECT"
            rationale.append(
                f"Dimensional error: '{dm['quantity']}' requires {dm['expected_dim']} but the unit "
                f"{dm['unit']} is {dm['unit_dim']}. The quantity and its unit are incommensurable — rejected.")
        elif dm and dm.get("match") is None:
            # Unknown quantity/unit (or empty) is NOT re-derivable -> must not pass as
            # GATE-verified. Absence of a check is not a passed check (GIGO guard).
            scope = "ATTEST"; final = "HOLD"
            checks.append({"check": "dimensional_consistency", "status": dm.get("status", "UNRESOLVED"), "detail": dm})
            rationale.append(
                f"Dimensional claim not re-derivable ({dm.get('status', 'unresolved')}: "
                f"quantity={dm.get('quantity')!r}, unit={dm.get('unit')!r}); the engine has no "
                "dimension for it — held for a recognised quantity+unit or attestation, not accepted.")

    # Stoichiometry: a chemical equation conserves atoms (exact, deterministic).
    if final == "ACCEPT" and evidence.get("stoichiometry") is not None:
        sx = rederive_stoichiometry(evidence)
        if sx and sx.get("match") is True:
            checks.append({"check": "stoichiometry_balance", "status": "VERIFIED", "detail": sx})
            rationale.append(
                f"Equation balances: every element is conserved and mass matches "
                f"({sx['reactant_mass']} = {sx['product_mass']} g/mol). Re-derived by atom conservation.")
        elif sx and sx.get("match") is False and sx.get("status") in ("MALFORMED",):
            scope = "ATTEST"; final = "HOLD"
            checks.append({"check": "stoichiometry_balance", "status": "MALFORMED", "detail": sx})
            rationale.append(
                "Chemical equation could not be parsed (unknown element / empty side); not "
                "re-derivable — held, not accepted.")
        elif sx and sx.get("match") is False:
            checks.append({"check": "stoichiometry_balance", "status": "FAIL", "detail": sx})
            final = "REJECT"
            rationale.append(
                f"Equation does NOT balance — atoms not conserved: {sx['imbalanced']} "
                "(reactant vs product counts). Rejected by atom conservation.")

    # ZK rung: verify a result over HIDDEN data via a registered zero-knowledge backend.
    if final == "ACCEPT" and evidence.get("zk_proof") is not None:
        zk = verify_zk_proof(evidence)
        if zk and zk.get("status") == "UNTRUSTED_VK":
            scope = "ATTEST"; final = "HOLD"
            checks.append({"check": "zk_proof", "status": "UNTRUSTED_VK", "detail": zk})
            rationale.append(
                f"A zero-knowledge proof is supplied but its verifying key '{zk.get('verifying_key_id')}' is "
                "not registered/trusted. Register a verifying backend (EZKL/groth16) to GATE; ATTEST only."
            )
        elif zk and zk.get("verified") is True:
            checks.append({"check": "zk_proof", "status": "VERIFIED", "detail": zk})
            rationale.append(
                f"Zero-knowledge proof verified ({zk.get('scheme')}, vk={zk.get('verifying_key_id')}): the result "
                "re-derives over HIDDEN data without exposing it. GATE extended to non-shippable evidence."
            )
        elif zk and zk.get("verified") is False:
            checks.append({"check": "zk_proof", "status": "FAILED", "detail": zk})
            final = "REJECT"
            rationale.append(
                f"Zero-knowledge proof FAILED verification (vk={zk.get('verifying_key_id')}). The claimed result "
                "does not bind to the committed computation — rejected."
            )

    # Quantum rung: re-simulate a quantum-circuit claim below the simulability
    # frontier (Bravyi-Gosset 2^{0.40 t} / Gottesman-Knill / statevector 2^n);
    # beyond it, route to CVQC (Mahadev, LWE) or ATTEST — never fake a simulation.
    if final == "ACCEPT" and evidence.get("quantum_circuit") is not None and _rederive_quantum is not None:
        qr = _rederive_quantum(evidence)
        if qr and qr.get("status") == "BEYOND_FRONTIER":
            scope = "ATTEST"; final = "HOLD"
            checks.append({"check": "quantum_resimulation", "status": "BEYOND_FRONTIER",
                           "detail": {k: qr[k] for k in ("qubits", "t_count", "log2_cost_statevector",
                                                          "log2_cost_stabilizer_rank", "route")}})
            rationale.append(
                f"Quantum claim is beyond the engine's exact-simulability frontier "
                f"(n={qr['qubits']}, t_count={qr['t_count']}, log2-cost≈"
                f"{min(qr['log2_cost_statevector'], qr['log2_cost_stabilizer_rank'])}). "
                f"Route: {qr['route']} — Classical Verification of Quantum Computation (Mahadev/LWE) "
                "if a quantum proof is supplied, else attest a real QC. The engine does not fake a simulation."
            )
        elif qr and qr.get("match") is True:
            checks.append({"check": "quantum_resimulation", "status": "VERIFIED",
                           "detail": {k: qr.get(k) for k in ("claim_type", "re_derived", "declared",
                                                             "qubits", "t_count")}})
            rationale.append(
                f"Quantum claim re-derives by exact classical statevector simulation "
                f"({qr.get('claim_type')} = {qr.get('re_derived')}, n={qr['qubits']}, t={qr['t_count']}). Verified."
            )
        elif qr and qr.get("match") is False:
            checks.append({"check": "quantum_resimulation", "status": "FAIL", "detail":
                           {"claim_type": qr.get("claim_type"), "re_derived": qr.get("re_derived"),
                            "declared": qr.get("declared")}})
            final = "REJECT"
            rationale.append(
                f"Quantum claim does NOT re-derive: re-simulation gives {qr.get('re_derived')} vs declared "
                f"{qr.get('declared')} — rejected."
            )

    # Registry reconciliation (Passage Point B): posted figure vs re-derived figure.
    if final == "ACCEPT" and evidence.get("registry") is not None:
        reg = reconcile_registry(evidence)
        if reg is not None and not reg["match"]:
            checks.append({"check": "registry_reconciliation", "status": "DISCREPANCY", "detail": reg})
            final = "HOLD"
            rationale.append(
                f"Registry-posted value {reg['posted']} diverges from the re-derived value "
                f"{reg['rederived']} (source {reg.get('source_id')}). Reconcile before reuse."
            )
        elif reg is not None:
            checks.append({"check": "registry_reconciliation", "status": "RECONCILED", "detail": reg})
            rationale.append(f"Registry-posted value reconciles with the re-derived value (source {reg.get('source_id')}).")

    if final == "ACCEPT":
        if ctype == "statistical_confidence":
            rd = rederive_statistical(evidence)
            if rd is None:
                checks.append({"check": "statistical_rederivation", "status": "NOT_SUPPLIED",
                               "detail": "no raw_data; p_value is declared, not re-derivable"})
                scope = "ATTEST"
                final = "HOLD"
                rationale.append(
                    "Standard above requirement: the statistical result is DECLARED, not "
                    "re-derivable. Supply raw_data (group_a/group_b) to GATE by re-computation, "
                    "or a signed provenance artifact to ATTEST. Declared-only evidence is held."
                )
            elif rd["match"]:
                checks.append({"check": "statistical_rederivation", "status": "VERIFIED", "detail": rd})
                rationale.append(
                    f"Re-computed p={rd['recomputed_p']} ({rd['engine']}) matches declared "
                    f"p={rd['declared_p']}: evidence re-derives. ACCEPT is verified, not trusted."
                )
            else:
                checks.append({"check": "statistical_rederivation", "status": "FAIL", "detail": rd})
                final = "REJECT"
                rationale.append(
                    f"Re-computed p={rd['recomputed_p']} contradicts declared p={rd['declared_p']}. "
                    "The declared statistic does not survive re-derivation — rejected."
                )
        else:
            # claim types whose key evidence is study-design / unobservable booleans
            attest_fields = sorted(set(evidence) & ATTEST_CLASS_FIELDS)
            if attest_fields:
                if _has_provenance(evidence):
                    checks.append({"check": "design_evidence_provenance", "status": "ATTESTED",
                                   "detail": {"fields": attest_fields, "provenance": True}})
                    scope = "ATTEST"
                    rationale.append(
                        "Study-design evidence carries verifiable provenance: ATTESTED "
                        "(signed/bound), not re-derived. Verdict stands on accountable attestation."
                    )
                else:
                    checks.append({"check": "design_evidence_provenance", "status": "UNBACKED",
                                   "detail": {"fields": attest_fields, "provenance": False}})
                    scope = "ATTEST"
                    final = "HOLD"
                    rationale.append(
                        "Standard above requirement: study-design evidence "
                        f"({', '.join(attest_fields)}) is ATTEST-class — it cannot be re-derived by "
                        "computation. Provide a verifiable provenance artifact (registry ID + signed "
                        "RO-Crate/C2PA). Unbacked declared booleans are not accepted."
                    )

    tier = (
        "RE-DERIVED" if any(c["status"] == "VERIFIED" for c in checks)
        else "ATTEST" if scope == "ATTEST"
        else "FORM"
    )
    # Fail-closed backstop (secure by construction) before sealing the receipt.
    final, scope = _fail_closed(final, scope, checks, evidence, rationale)
    if final != "ACCEPT" and tier == "RE-DERIVED" and not any(
            c.get("status") == "VERIFIED" for c in checks):
        tier = "ATTEST" if scope == "ATTEST" else "FORM"

    receipt = _receipt(payload, base_verdict, final, scope, tier, checks, rationale)
    if cache_key is not None:
        if len(_VERIFY_CACHE) >= _VERIFY_CACHE_CAP:
            _VERIFY_CACHE.clear()
        _VERIFY_CACHE[cache_key] = receipt
    return receipt


if __name__ == "__main__":  # pragma: no cover
    import sys
    payload = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else json.load(sys.stdin)
    print(json.dumps(verify(payload), indent=2))
