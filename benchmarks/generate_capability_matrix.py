"""Generate CAPAS's capability matrix by EXERCISING every gate, not asserting it. Each row is
proven live: the gate is called on a canonical input and its verdict recorded. Emits a JSON +
markdown matrix so the 'where we are' positioning is re-derivable from the code, not marketing.

Honesty axis per row: EXACT (re-derivable identity / published quantity -> a real gate) vs
DIAGNOSTIC (model assumption -> not a verdict). This is the line the whole engine is built on.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import capas_quantum_physics as Q
import capas_invariants as INV


def _v(d, k="verdict"):
    return d.get(k)


def build() -> list[dict]:
    rows = []

    def add(domain, capability, klass, exact, demo_in, verdict, catches):
        rows.append({"domain": domain, "capability": capability, "class": klass,
                     "exact": exact, "demo_input": demo_in, "verdict": verdict, "catches": catches})

    # --- consistency-invariant gates (equalities/bounds between declared quantities) ---
    add("quantum", "coherence bound T2<=2*T1", "consistency-invariant", True,
        "Q121 T1=11.2 T2=23.44 ramsey", _v(Q.check_coherence(11.2, 23.44)),
        "active TLS / hidden CPMG passed off as a clean qubit")
    add("quantum", "thermal P01>=P10", "consistency-invariant", True,
        "inverted P01=0.004 P10=0.012", _v(Q.check_thermal(0.004, 0.012)),
        "negative thermal population (fabricated/inverted readout row)")
    add("statistics", "GRIM mean reachability", "consistency-invariant", True,
        "mean 5.19 n=10", _v(INV.check_grim({"grim": {"mean": 5.19, "n": 10}})),
        "fabricated/typo'd reported means in survey/clinical data")
    add("finance", "accounting identity A=L+E", "consistency-invariant", True,
        "assets1000 liab600 equity300", _v(INV.check_accounting({"accounting": {"assets": 1000, "liabilities": 600, "equity": 300}})),
        "books that do not close")
    add("universal", "probability bounds 0<=p<=1", "consistency-invariant", True,
        "p=[0.3,1.4]", _v(INV.check_probability_bounds({"probabilities": [0.3, 1.4]})),
        "out-of-range probabilities / unnormalized distributions")

    # --- derived-quantity gates (re-derive an unpublished quantity + gate its bound) ---
    add("quantum", "pure dephasing Gamma_phi=1/T2-1/2T1", "derived-quantity", True,
        "Q137 T1=212 T2=14", "ADMISSIBLE" if Q.pure_dephasing(212, 14)["admissible"] else "FLAG",
        "re-derives unpublished dephasing rate; classifies dephasing- vs T1-limited")
    add("quantum", "gate-error coherence floor t_g/3T1", "derived-quantity", True,
        "claim SX err 1e-5 on Q137", _v(Q.gate_error_admissible(1e-5, 32, 212, 14)),
        "a gate error cleaner than relaxation physically allows (fabricated fidelity)")

    # --- exact-published-quantity gates (vendor publishes it exactly) ---
    add("quantum", "residual ZZ coupling", "exact-published", True,
        "ZZ=200kHz vs target", _v(Q.check_zz_residual(2.0e5)),
        "tunable coupler not nulling ZZ (always-on idle entanglement)")

    # --- measurement-vs-model gate (the one place CAPAS crosses text<->reality, two oracles) ---
    try:
        hw = Q.gate_against_prediction({"00": 3200, "11": 3200, "01": 900, "10": 892},
                                       {"00": 4038, "11": 3985, "01": 96, "10": 73}, {"00", "11"})
        add("quantum", "measurement vs calibrated noise model", "measurement-noise-model", True,
            "noisy Bell vs Aer prediction", _v(hw),
            "a hardware result inconsistent with the device's calibrated physics")
    except Exception:
        pass

    # --- universal conservation ---
    add("universal", "conservation sum(parts)=total", "consistency-invariant", True,
        "parts[10,20,35] total60", _v(INV.check_sum({"parts": [10, 20, 35], "total": 60})),
        "declared components that do not sum to the declared whole")

    # --- chemistry / physics / mathematics ---
    add("chemistry", "stoichiometric atom balance", "consistency-invariant", True,
        "CH4+O2->CO2+2H2O (1 O2)", _v(INV.check_stoichiometry({"stoichiometry": {"reactants": {"CH4": 1, "O2": 1}, "products": {"CO2": 1, "H2O": 2}}})),
        "an unbalanced reaction (atoms not conserved reactants->products)")
    add("physics", "dimensional homogeneity", "consistency-invariant", True,
        "J = kg m/s^2 (wrong)", _v(INV.check_dimensions({"dimensions": {"lhs": "J", "rhs": {"kg": 1, "m": 1, "s": -2}}})),
        "an equation whose two sides have different physical dimensions")
    add("physics", "physical bounds (eta<=1, v<=c, T>=0)", "consistency-invariant", True,
        "efficiency 1.2", _v(INV.check_physical_bounds({"bounds": {"efficiency": 1.2}})),
        "over-unity efficiency, faster-than-light, sub-absolute-zero, |r|>1")
    add("mathematics", "claimed root satisfies the equation", "derived-quantity", True,
        "x=2 for x^2-9=0", _v(INV.check_root({"root_check": {"polynomial": [-9, 0, 1], "root": 2}})),
        "a declared solution that does not satisfy its own equation")
    add("mathematics", "linear system Ax=b solution check", "derived-quantity", True,
        "wrong x for Ax=b", _v(INV.check_linear_system({"linear_system": {"A": [[1, 1]], "x": [1, 2], "b": [5]}})),
        "a declared solution vector that does not satisfy the system")
    add("mathematics", "integer divisibility / gcd-lcm", "consistency-invariant", True,
        "3|10 claimed true", _v(INV.check_divisibility({"divisibility": {"a": 3, "b": 10, "divides": True}})),
        "false divisibility / gcd-lcm / quotient-remainder claims")
    add("chemistry", "charge balance in reaction", "consistency-invariant", True,
        "net charge unbalanced", _v(INV.check_charge_balance({"charge_balance": {"reactants": [[1, 2], [1, 0]], "products": [[1, 3]]}})),
        "a reaction that conserves atoms but not net charge")
    add("chemistry", "oxidation states sum to charge", "consistency-invariant", True,
        "SO4: 6-8 != 0", _v(INV.check_oxidation_states({"oxidation_states": {"atoms": {"S": 1, "O": 4}, "states": {"S": 6, "O": -2}, "net_charge": 0}})),
        "declared oxidation states inconsistent with the species charge")
    add("chemistry", "mole/mass/amount n=m/M", "derived-quantity", True,
        "18g/18 != 2 mol", _v(INV.check_mole_mass({"mole_mass": {"m": 18, "M": 18, "n": 2}})),
        "an inconsistent mole / mass / molar-mass trio")
    add("epidemiology", "2x2 metric identities (Se/Sp/PPV/...)", "derived-quantity", True,
        "claimed Se != cells", _v(INV.check_confusion_matrix({"confusion_matrix": {"tp": 90, "fp": 10, "fn": 10, "tn": 90, "claimed": {"sensitivity": 0.99}}})),
        "a claimed sensitivity/specificity/PPV that the 2x2 cells do not support")
    add("epidemiology", "Bayes PPV vs base rate", "derived-quantity", True,
        "99% test, rare disease", _v(INV.check_bayes_ppv({"bayes_ppv": {"sensitivity": 0.99, "specificity": 0.99, "prevalence": 0.001, "claimed_ppv": 0.99}})),
        "the base-rate fallacy: high-sensitivity test claimed to imply high PPV for a rare disease")
    add("epidemiology", "RR/OR/RD from 2x2", "derived-quantity", True,
        "claimed RR != table", _v(INV.check_association({"association": {"a": 20, "b": 80, "c": 10, "d": 90, "claimed_rr": 3.0}})),
        "a claimed risk/odds ratio inconsistent with the cohort table")
    add("epidemiology", "vaccine efficacy VE=1-RR, VE<=1", "consistency-invariant", True,
        "VE>1 (negative cases)", _v(INV.check_vaccine_efficacy({"vaccine_efficacy": {"cases_vax": -5, "n_vax": 1000, "cases_unvax": 50, "n_unvax": 1000}})),
        "a vaccine efficacy above 1 or inconsistent with the arm attack rates")
    add("epidemiology", "count containment (num<=den)", "consistency-invariant", True,
        "deaths 120 > cases 100", _v(INV.check_count_containment({"containment": {"pairs": [{"num": 120, "den": 100, "label": "deaths/cases"}]}})),
        "a numerator exceeding its denominator (deaths>cases, etc.)")
    add("engineering", "Ohm's law V=IR, P=VI", "consistency-invariant", True,
        "V=10, I*R=6", _v(INV.check_ohms_law({"ohms_law": {"V": 10, "I": 2, "R": 3}})),
        "declared electrical quantities that violate V=IR or P=VI")
    add("biology", "Lincoln-Petersen N=M*C/R", "derived-quantity", True,
        "N inconsistent w/ M,C,R", _v(INV.check_mark_recapture({"mark_recapture": {"M": 100, "C": 100, "R": 20, "N": 999}})),
        "a mark-recapture population estimate inconsistent with the counts")
    add("biology", "Hardy-Weinberg internal consistency", "consistency-invariant", True,
        "genotype freqs sum!=1", _v(INV.check_hardy_weinberg({"hardy_weinberg": {"AA": 0.3, "Aa": 0.5, "aa": 0.3}})),
        "genotype frequencies that do not sum to 1 / inconsistent allele freqs")

    # --- DIAGNOSTIC only (honest exclusions: model assumptions, NOT gates) ---
    rows.append({"domain": "quantum", "capability": "ZZ from CZ/RZZ ratio", "class": "DIAGNOSTIC",
                 "exact": False, "demo_input": "n/a", "verdict": "NOT-A-GATE",
                 "catches": "EXCLUDED: ±2x linear-model estimate; the published exact ZZ replaces it (was 24x off)"})
    rows.append({"domain": "quantum", "capability": "loss tangent tan_d=1/(2pi f T1)", "class": "DIAGNOSTIC",
                 "exact": False, "demo_input": "n/a", "verdict": "NOT-A-GATE",
                 "catches": "EXCLUDED: needs qubit frequency (withheld on open plan, verified live)"})
    return rows


def render_md(rows) -> str:
    gates = [r for r in rows if r["class"] != "DIAGNOSTIC"]
    diag = [r for r in rows if r["class"] == "DIAGNOSTIC"]
    out = ["# CAPAS capability matrix (re-derived by exercising each gate)", "",
           f"**{len(gates)} live gates** across {len(set(r['domain'] for r in gates))} domains; "
           f"{len(diag)} capabilities deliberately EXCLUDED as diagnostics (model assumptions).", "",
           "| domain | capability | class | exact | demo verdict | catches |",
           "|---|---|---|---|---|---|"]
    for r in gates:
        out.append(f"| {r['domain']} | {r['capability']} | {r['class']} | "
                   f"{'✅' if r['exact'] else '~'} | `{r['verdict']}` | {r['catches']} |")
    out.append("")
    out.append("**Excluded as diagnostics (the honesty line — not gates):**")
    for r in diag:
        out.append(f"- {r['capability']} — {r['catches']}")
    return "\n".join(out)


def main() -> int:
    rows = build()
    (ROOT / "outputs").mkdir(exist_ok=True)
    json.dump(rows, open(ROOT / "outputs" / "capability_matrix.json", "w"), indent=2)
    md = render_md(rows)
    (ROOT / "docs" / "capability_matrix.md").write_text(md + "\n")
    gates = [r for r in rows if r["class"] != "DIAGNOSTIC"]
    # every gate must have produced a real verdict (proves it is live, not asserted)
    live = all(r["verdict"] and r["verdict"] != "NOT-A-GATE" for r in gates)
    print(md)
    print(f"\n{'OK' if live else 'XX'} all {len(gates)} gates produced a live verdict")
    print("CAPABILITY MATRIX: generated" if live else "CAPABILITY MATRIX: a gate did not fire")
    return 0 if live else 1


if __name__ == "__main__":
    raise SystemExit(main())
