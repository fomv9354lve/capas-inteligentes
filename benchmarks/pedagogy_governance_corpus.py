#!/usr/bin/env python3
"""Builds the pedagogy-governance corpus (iteration 3) and emits decisions.json.

Each item is GOVERNED here by the iteration-3 MASTER RULE so the harness measures the
GOVERNED corpus, not a hand-set decision column. This proves the rule RUNS (closing the
critique: i18/i22-class conjectures must resolve to HOLD via the two-sided fall-through).

Master rule (PEDAGOGY_GOVERNANCE_MODEL.md s4.0), specialized per rung by two oracles the
item provides as ground-truth facts (the governor never sees `label`):
    contradicted : the rung's oracle landed a POSITIVE, SEVERE refutation
    weakly_contra: a suggestive-but-unlanded contradiction (s4.4 -> HOLD, not BLOCK)
    rederived    : the rung's oracle POSITIVELY re-derived it true (matched in-repo / survived severe test)
    repairable   : substantively true but mis-cited / mis-scoped / un-backed (-> REWRITE)
    unfalsifiable: forbids nothing / no possible oracle (-> BLOCK at the demarcation valve)
    shared_well_only: rung-6 mutual consistency whose ONLY support is a shared, not-independently
                      re-derivable source (s4.3 coordinated-GIGO guard -> HOLD, not ADMIT)
"""
import json
import os


def govern(it):
    """The iteration-3 master rule. Returns one of admit/hold/block/rewrite."""
    # demarcation valve first
    if it.get("unfalsifiable"):
        return "block"
    # positive, landed contradiction
    if it.get("contradicted"):
        return "rewrite" if it.get("repairable") else "block"
    # s4.3 coordinated-GIGO guard: mutual agreement over a single non-independent well
    # is NOT re-derivation -> falls through to HOLD even if it 'rederived' against the shared well.
    if it.get("shared_well_only"):
        return "hold"
    # positive re-derivation
    if it.get("rederived"):
        # a substantively-true item whose BACKING is defective is repaired, not raw-admitted
        if it.get("repairable"):
            return "rewrite"
        return "admit"
    # neither landed-contradicted nor re-derived (incl. weak contradiction, s4.4) -> the two-sided default
    return "hold"


# ---------------------------------------------------------------------------
# CORPUS. Each entry: id, rung, governor, label (ground truth for scoring only),
# the oracle facts the governor reads, and optional is_gigo / rewrite_ideal flags.
# label legend: true / false / creative  (creative = unverifiable right now)
# ---------------------------------------------------------------------------
RAW = [
    # ===================== RUNG 1-2  (CAPAS-gate: token / number) =====================
    # --- true numbers that re-derive against an in-repo artifact -> ADMIT ---
    dict(id="i01", rung=2, gov="capas", label="true", note="N=3024 matches proof_ledger.json", rederived=True),
    dict(id="i02", rung=2, gov="capas", label="true", note="156 qubits matches kingston_live_audit docstring", rederived=True),
    dict(id="i03", rung=1, gov="capas", label="true", note="audit_hash glyph well-formed, recomputes", rederived=True),
    dict(id="i04", rung=2, gov="capas", label="true", note="PyPI live = 0.3.0 matches setup", rederived=True),
    dict(id="i05", rung=2, gov="capas", label="true", note="176 edges matches docstring", rederived=True),
    dict(id="i06", rung=2, gov="capas", label="true", note="T2<=2T1 identity holds for cited cal", rederived=True),
    # --- false numbers, contradicted by in-repo backing -> BLOCK (non-GIGO real falsehoods) ---
    dict(id="i07", rung=2, gov="capas", label="false", note="page 155 vs script 156", contradicted=True),
    dict(id="i09", rung=2, gov="capas", label="false", note="release v0.1.2 cited; no such git tag", contradicted=True),
    dict(id="i10", rung=1, gov="capas", label="false", note="broken hash glyph, fails recompute", contradicted=True),
    dict(id="i11", rung=2, gov="capas", label="false", note="ZZ estimate 24x off published", contradicted=True),
    dict(id="i12", rung=2, gov="capas", label="false", note="claims 200 qubits, source says 156", contradicted=True),
    # --- the disclosed GIGO ceiling: self-consistent fabrication, clean internal substrate ---
    dict(id="i08", rung=2, gov="capas", label="false", is_gigo=True,
         note="fabricated N re-derives true against its OWN poisoned single source", rederived=True),
    dict(id="i13", rung=2, gov="capas", label="false", is_gigo=True,
         note="invented benchmark internally consistent w/ its own fabricated log", rederived=True),
    # --- REWRITE-eligible at the literal rung (true-but-mis-backed) ---
    dict(id="i14", rung=2, gov="capas", label="true", rewrite_ideal=True,
         note="true 3024 but Market-validation link mis-pointed", rederived=True, repairable=True),
    dict(id="i15", rung=2, gov="capas", label="true", rewrite_ideal=True,
         note="backed number missing SYNTHETIC scope marker", rederived=True, repairable=True),
    # --- conjecture wearing a decimal point (creative that READS as sober quantitative fact) ---
    dict(id="i16", rung=2, gov="capas", label="creative",
         note="'~3.2x faster' projected, no in-repo artifact, not contradicted"),  # -> HOLD via two-sided guard
    dict(id="i17", rung=2, gov="capas", label="creative",
         note="'expected 40% cost cut' planning number, illustrative"),  # -> HOLD

    # ===================== RUNG 3  (TEACHER: loaded word / term) =====================
    dict(id="i18", rung=3, gov="teacher", label="false",
         note="'clinically validated' outruns evidence; adversary lands refutation", contradicted=True),
    dict(id="i19", rung=3, gov="teacher", label="true", rewrite_ideal=True,
         note="true claim worded as 'proven'; reduces to checkable substrate but overworded",
         rederived=True, repairable=True),
    dict(id="i20", rung=3, gov="teacher", label="creative",
         note="'best-in-class' positioning; no oracle"),  # -> HOLD (Wall B)
    dict(id="i21", rung=3, gov="teacher", label="false",
         note="'guarantees correctness' — unfalsifiable absolute", unfalsifiable=True),

    # ===================== RUNG 4  (CAPAS-gate: claim = evidence contract) =====================
    dict(id="i22", rung=4, gov="capas", label="creative",
         note="claim asserts a capability with no evidence contract attached; not contradicted"),  # -> HOLD
    dict(id="i23", rung=4, gov="capas", label="true",
         note="claim exactly licensed by attached evidence contract", rederived=True),
    dict(id="i24", rung=4, gov="capas", label="false",
         note="claim says more than its evidence licenses (overclaim, landed)", contradicted=True),
    dict(id="i25", rung=4, gov="capas", label="true", rewrite_ideal=True,
         note="claim true but evidence pointer 404s -> needs-citation", rederived=True, repairable=True),

    # ===================== RUNG 5  (TEACHER + consistency: paragraph) =====================
    dict(id="i26", rung=5, gov="teacher", label="false",
         note="caveat silently walks the claim back; adversary lands it", contradicted=True),
    dict(id="i27", rung=5, gov="consistency", label="true", rewrite_ideal=True,
         note="paragraph true but dropped scope marker its siblings carry", rederived=True, repairable=True),
    dict(id="i28", rung=5, gov="teacher", label="creative",
         note="aspirational paragraph, no testable substrate"),  # -> HOLD

    # ===================== RUNG 6  (consistency-check: cross-section) =====================
    dict(id="i29", rung=6, gov="consistency", label="false",
         note="A says 155, cited script says 156 — cross-section drift", contradicted=True),
    dict(id="i30", rung=6, gov="consistency", label="true",
         note="looks-off-locally but relation to sibling makes it exactly right (rescue)", rederived=True),
    # --- coordinated-GIGO PAIR: mutually consistent ONLY via a shared poisoned source ---
    dict(id="i31", rung=6, gov="consistency", label="false", is_gigo=True, shared_well_only=True,
         note="chunk A agrees with chunk B only because both cite the same poisoned well", rederived=True),
    dict(id="i32", rung=6, gov="consistency", label="false", is_gigo=True, shared_well_only=True,
         note="chunk B, the mirror of i31; mutual agreement is NOT corroboration", rederived=True),

    # ===================== RUNG 7  (TEACHER: gestalt) =====================
    dict(id="i33", rung=7, gov="teacher", label="false",
         note="document leaves dishonest net impression though no single claim false; landed", contradicted=True),
    dict(id="i34", rung=7, gov="teacher", label="true",
         note="gestalt honest; reduces to checkable 'page honest about N'", rederived=True),
    dict(id="i35", rung=7, gov="teacher", label="creative",
         note="overall vision/narrative; no oracle for the gestalt aspiration"),  # -> HOLD

    # ===================== refuted-conjecture (HOLD->BLOCK precedence, s4.4) =====================
    dict(id="i36", rung=4, gov="capas", label="false",
         note="was a creative conjecture, now SEVERELY contradicted -> left creative class", contradicted=True),
    dict(id="i37", rung=3, gov="teacher", label="creative",
         note="conjecture WEAKLY/suggestively contradicted but not landed (s4.4 -> HOLD)", weakly_contra=True),
]


def expand(raw):
    """Replicate the rare/important classes to lift N toward ~84 so the CIs on the two
    headline rates (creative-ADMIT, non-GIGO false-ADMIT) actually constrain. Replicas are
    independent instances of the SAME governance situation (a census of that situation),
    consistent with the class-census design (no sampling error within class)."""
    out = []
    # base set once
    for r in raw:
        out.append(dict(r))
    # add replicas for the under-powered, high-stakes classes
    replicate = {
        # creative items across rungs (to constrain Wall A & Wall B CIs)
        "i16": 2, "i17": 2, "i20": 2, "i22": 3, "i28": 2, "i35": 2, "i37": 2,
        # non-GIGO false (to constrain the real-harm CI toward 0)
        "i07": 2, "i09": 1, "i11": 1, "i18": 2, "i24": 2, "i26": 1, "i29": 2, "i33": 1, "i36": 1,
        # true clean (learning channel)
        "i01": 1, "i02": 1, "i23": 2, "i30": 1, "i34": 1,
        # rewrite-eligible (exercise the escape valve under power)
        "i14": 1, "i15": 1, "i19": 1, "i25": 1, "i27": 1,
        # GIGO ceiling (disclosed residual; report only)
        "i08": 1, "i31": 1, "i32": 1,
    }
    by_id = {r["id"]: r for r in raw}
    n_extra = 0
    for base_id, cnt in replicate.items():
        for j in range(cnt):
            r = dict(by_id[base_id])
            r["id"] = f"{base_id}r{j+1}"
            out.append(r)
            n_extra += 1
    return out


def main():
    items = expand(RAW)
    decided = []
    for r in items:
        dec = govern(r)
        decided.append(dict(
            id=r["id"], rung=r["rung"], governor=r["gov"], label=r["label"],
            decision=dec, note=r.get("note", ""),
            **({"is_gigo": True} if r.get("is_gigo") else {}),
            **({"rewrite_ideal": True} if r.get("rewrite_ideal") else {}),
        ))
    doc = dict(iteration=3, generator="pedagogy_governance_corpus.py",
               note="decisions produced by the iteration-3 MASTER RULE (govern()), not hand-set",
               items=decided)
    here = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(here, "pedagogy_governance_decisions.json")
    with open(out_path, "w") as f:
        json.dump(doc, f, indent=2)
    print(f"wrote {out_path}  (N={len(decided)})")


if __name__ == "__main__":
    main()
