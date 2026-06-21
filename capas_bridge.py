"""CAPAS — attacking the autoformalization frontier (the NL->structure bridge).

The wall (Agent 3; survey arXiv 2505.23486): no formal method can CERTIFY informal<->formal
equivalence, because the informal side has no formal semantics — a formalization can compile
yet mean something else (the 'semantic illusion'), and the compiler is BLIND to it (~45%
statement accuracy, failure mode semantic not syntactic).

We do not accept the wall as a stop. We do not certify equivalence either. We ATTACK it three
ways, none of which needs a formal semantics for the NL side:

  1. INDEPENDENT TRIANGULATION. Produce K formalizations of the SAME claim by independent means
     (different model / prompt / decomposition) and RUN them on a battery of PROBE instances. A
     mis-translation is a fabrication; independent fabrications rarely agree on probes. Agreement
     across INDEPENDENT formalizations bounds the semantic residual (consilience, reused) —
     geometric shrink with each independent agreer, never 0.
  2. BACK-TRANSLATION FALSIFIER. Verbalize each formal object back to NL and check semantic
     agreement with the original. Divergence flags mis-translation — the very thing the compiler
     cannot see.
  3. PROBE-DIFFERENTIAL + FAIL-CLOSED. Where formalizations DISAGREE on any probe, the bridge is
     untrusted -> DEFER. Never run the downstream oracle on an unverified formalization.

The frontier is not crossed; it becomes a GRADED, measurable mis-translation residual that
shrinks with independent agreeing formalizations and FAILS CLOSED on disagreement. This catches
exactly the semantic illusion (e.g. 'all x' formalized as 'exists x') that compiles and that a
type checker waves through. Cara 1, deterministic over the SUPPLIED formalizations/probes
(generation of the K formalizations is upstream, like the proposer in capas_falsify).
"""
from __future__ import annotations

from collections import Counter
from typing import Any, Callable


def triangulate(formalizations: list[dict[str, Any]], probes: list[dict[str, Any]],
                back_translation: list[dict[str, Any]] | None = None,
                bt_threshold: float = 0.6) -> dict[str, Any]:
    """Attack the bridge by independent triangulation over probe instances.

    formalizations: [{name, fn, group?}] where fn(probe)->bool is the formal object's truth
      on that instance (in production: the executed Lean/SMT/CAPAS-rung object; here: supplied).
      `group` is the independence id (independently-produced formalizations -> distinct groups).
    probes: list of instance dicts the formal objects are evaluated on.
    back_translation: optional [{name, agreement in [0,1]}] — NL round-trip agreement per formalization.
    """
    if not formalizations or not probes:
        return {"decision": "DEFER", "reason": "no formalizations or no probes to differentiate on",
                "bridge_confidence": 0.0, "semantic_residual": 1.0}

    rows = []
    for f in formalizations:
        fn: Callable[[dict], bool] = f["fn"]
        out = tuple(bool(fn(p)) for p in probes)
        rows.append({"name": f["name"], "group": f.get("group", f["name"]), "out": out})

    vectors = [r["out"] for r in rows]
    # probes on which the formalizations DISAGREE = the differential that exposes mis-translation
    divergent = [i for i in range(len(probes)) if len({v[i] for v in vectors}) > 1]
    # the agreeing cohort = formalizations sharing the modal full output-vector; count INDEPENDENT
    # groups (re-derivations of the same formalization don't add reality-anchoring) -> consilience rule
    modal = Counter(vectors).most_common(1)[0][0]
    agree_groups = sorted({r["group"] for r in rows if r["out"] == modal})
    dissenters = [{"name": r["name"], "group": r["group"]} for r in rows if r["out"] != modal]
    n_indep = len(agree_groups)
    semantic_residual = round(1.0 / (1.0 + n_indep), 4)   # graded; shrinks geometrically, never 0

    # back-translation falsifier (second, independent detector of the illusion)
    bt_failures = [b["name"] for b in (back_translation or []) if float(b.get("agreement", 1.0)) < bt_threshold]

    illusion = bool(divergent) or bool(dissenters) or bool(bt_failures)
    if illusion:
        why = []
        if divergent:
            why.append(f"formalizations disagree on probe(s) {divergent} (probe-differential exposes mis-translation)")
        if bt_failures:
            why.append(f"back-translation diverges from the claim for {bt_failures}")
        decision = "DEFER"
        confidence = 0.0
        headline = ("SEMANTIC-ILLUSION DETECTED — do not run the oracle on this bridge; "
                    "defer to the subject or demand an agreeing independent formalization")
    else:
        decision = "TRUST"
        confidence = round(1.0 - semantic_residual, 4)
        headline = (f"BRIDGE TRUSTED (graded) — {n_indep} independent formalization(s) agree on all "
                    f"{len(probes)} probes; semantic residual {semantic_residual} (never 0 — the subject holds it)")

    return {
        "decision": decision,                              # TRUST | DEFER (fail-closed on disagreement)
        "headline": headline,
        "bridge_confidence": confidence,                   # graded, = 1 - residual when trusted
        "semantic_residual": semantic_residual,            # the measured, shrinkable mis-translation room
        "independent_agreeing_formalizations": agree_groups,
        "dissenting_formalizations": dissenters,           # the caught mis-translations
        "divergent_probes": divergent,                     # where the illusion shows
        "back_translation_failures": bt_failures,
        "attack": "the equivalence wall is unattackable for ONE translation; under independent "
                  "triangulation + back-translation + probe-differential it becomes a graded residual. "
                  "We do not certify NL<->formal equivalence — we DETECT divergence and grade confidence, "
                  "fail-closed. Catches the 'all->exists' illusion a type checker passes.",
    }
