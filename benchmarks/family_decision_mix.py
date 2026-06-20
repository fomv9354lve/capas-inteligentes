#!/usr/bin/env python3
"""Per-family decision-mix over the evidence-contract decision space (relevant N).

For each of the 12 claim families this enumerates a realistic grid of evidence
values (booleans flipped, numerics swept across their tolerance boundary, anchor
modes, plus a missing-field variant per required field) and runs every payload
through the REAL engine (capas.decide_external_claim). It then reports the
ACCEPT / REWRITE / REJECT / HOLD distribution per family.

HONESTY: this is a contract-coverage / decision-space benchmark over SYNTHETIC
payloads. It demonstrates that each family's contract is deterministic and
exercises the full verdict space at scale. It is NOT a real-world drift rate —
a defensible market figure needs an independently adjudicated corpus with
interrater agreement. The percentages here are a function of the synthetic grid.

Outputs:
  outputs/family_decision_mix.json
  outputs/family_decision_mix.md
"""
from __future__ import annotations

import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

import capas

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = capas.CAPAS_CLAIM_SCHEMA_VERSION


def frange(start: float, step: float, count: int) -> list[float]:
    return [round(start + step * i, 6) for i in range(count)]


# Realistic, research-level value grids per family (non-trivial: includes
# boundary cases — p just above/below alpha, error just above/below tolerance).
POOLS: dict[str, dict[str, list]] = {
    "exact_model_solution": {
        "abs_error": frange(0.0, 0.00035, 60),         # fine sweep across the tolerance band
        "tolerance": [0.005, 0.01, 0.05],
    },
    "physical_accuracy": {
        "within_chemical_accuracy": [True, False],
    },
    "statistical_confidence": {
        "p_value": frange(0.001, 0.0022, 90),           # fine straddle of common alphas
        "alpha": [0.01, 0.05, 0.1],
        "effect_direction_confirmed": [True, False],
    },
    "reproducibility_check": {
        "artifact_available": [True, False],
        "independent_reproduction_pass": [True, False],
    },
    "financial_metric_claim": {
        "reported_value": frange(100.0, 0.25, 60),      # vs reference 100 within/outside tolerance
        "reference_value": [100.0],
        "tolerance": [0.5, 1.0, 5.0],
        "metric_period_match": [True, False],
    },
    "causal_mechanism_claim": {
        "intervention_or_natural_experiment": [True, False],
        "temporal_order_established": [True, False],
        "confounders_controlled": [True, False],
        "mechanism_evidence_present": [True, False],
    },
    "systematic_review_claim": {
        "protocol_registered": [True, False],
        "inclusion_criteria_declared": [True, False],
        "risk_of_bias_assessed": [True, False],
        "effect_consistency": [True, False],
    },
    "evidence_conflict_claim": {
        "supporting_sources": [["source_a"], []],
        "contradicting_sources": [["source_b"], []],
        "conflict_resolution_method": ["pre-registered hierarchy", ""],
        "resolution_pre_registered": [True, False],
    },
    "multimodal_evidence_claim": {
        "modality": ["table", "figure"],
        "source_hashes_verified": [True, False],
        "cross_modal_alignment": [True, False],
        "extraction_method_declared": [True, False],
    },
    "programming_language_behavior_claim": {
        "language": ["python"],
        "language_version": ["3.11"],
        "claim_api": ["sorted"],
        "code_snippet": ["sorted([3, 1, 2])"],
        "expected_output": ["[1, 2, 3]"],
        "observed_output": ["[1, 2, 3]", "[3, 1, 2]"],
        "execution_observed": [True, False],
        "runtime_environment_declared": [True, False],
    },
    "claim_transition": {
        "upgrade_evidence_present": [True, False],
    },
}

# universal_anchor_claim is contract-versioned by anchor_mode → built separately.
ANCHOR_POOLS = {
    "absolute_anchor": {
        "local_property_tests_pass": [True, False],
        "universal_anchor_pass": [True, False],
    },
    "relative_anchor": {
        "local_property_tests_pass": [True, False],
        "relative_anchor_reference": ["DMRG reference L=64"],
        "relative_anchor_comparison_pass": [True, False],
    },
    "empirical_anchor": {
        "local_property_tests_pass": [True, False],
        "empirical_reference_present": [True, False],
        "empirical_tolerance": [0.05, 0.1],
        "empirical_anchor_pass": [True, False],
    },
    "benchmark_anchor": {
        "local_property_tests_pass": [True, False],
        "benchmark_name": ["GW150914"],
        "benchmark_metric": ["false_alarm_rate"],
        "benchmark_pass": [True, False],
    },
}

CLAIM_TEXT = {
    "exact_model_solution": "The solver result is exact within the declared tolerance.",
    "physical_accuracy": "The model is accurate against the physical reference.",
    "statistical_confidence": "The reported effect is statistically supported at the declared alpha.",
    "reproducibility_check": "The result reproduces from the supplied artifact.",
    "financial_metric_claim": "The reported metric reconciles to the reference within tolerance.",
    "causal_mechanism_claim": "The intervention causally changes the measured outcome.",
    "systematic_review_claim": "The review supports the reported effect across included studies.",
    "evidence_conflict_claim": "The disclosed conflicting evidence is resolved by the declared method.",
    "multimodal_evidence_claim": "The multimodal evidence supports the extracted claim.",
    "programming_language_behavior_claim": "The function produces the expected output for the API.",
    "claim_transition": "The stronger claim is licensed by the supplied upgrade evidence.",
    "universal_anchor_claim": "The result is physically consistent with the universal anchor.",
}


def grid_payloads(ct: str) -> list[dict]:
    pools = POOLS[ct]
    fields = sorted(pools)
    out = []
    for combo in itertools.product(*[pools[f] for f in fields]):
        ev = dict(zip(fields, combo))
        out.append({"claim": {"id": f"{ct}_grid", "text": CLAIM_TEXT[ct], "type": ct},
                    "evidence": ev, "schema_version": SCHEMA})
    base = {f: pools[f][0] for f in fields}
    for f in fields:
        ev = {k: v for k, v in base.items() if k != f}
        out.append({"claim": {"id": f"{ct}_missing_{f}", "text": CLAIM_TEXT[ct], "type": ct},
                    "evidence": ev, "schema_version": SCHEMA})
    return out


def universal_payloads() -> list[dict]:
    out = []
    for mode, pools in ANCHOR_POOLS.items():
        fields = sorted(pools)
        for combo in itertools.product(*[pools[f] for f in fields]):
            ev = {"anchor_mode": mode}
            ev.update(dict(zip(fields, combo)))
            out.append({"claim": {"id": f"ua_{mode}", "text": CLAIM_TEXT["universal_anchor_claim"],
                                  "type": "universal_anchor_claim"}, "evidence": ev, "schema_version": SCHEMA})
        base = {"anchor_mode": mode}
        base.update({f: pools[f][0] for f in fields})
        for f in fields:
            ev = {k: v for k, v in base.items() if k != f}
            out.append({"claim": {"id": f"ua_{mode}_missing_{f}", "text": CLAIM_TEXT["universal_anchor_claim"],
                                  "type": "universal_anchor_claim"}, "evidence": ev, "schema_version": SCHEMA})
    return out


def main() -> int:
    per_family: dict[str, Counter] = defaultdict(Counter)
    total = Counter()
    n = 0

    families = list(POOLS) + ["universal_anchor_claim"]
    for ct in POOLS:
        for p in grid_payloads(ct):
            v = capas.decide_external_claim(p)["verdict"]
            per_family[ct][v] += 1
            total[v] += 1
            n += 1
    for p in universal_payloads():
        v = capas.decide_external_claim(p)["verdict"]
        per_family["universal_anchor_claim"][v] += 1
        total[v] += 1
        n += 1

    order = ["ACCEPT", "REWRITE", "REJECT", "HOLD"]
    report = {
        "disclaimer": "Contract-coverage / decision-space benchmark over synthetic payloads. "
                      "Demonstrates deterministic, full-verdict-space coverage per family at scale. "
                      "NOT a real-world drift rate (that needs an independently adjudicated corpus "
                      "with interrater agreement). Percentages reflect the synthetic grid.",
        "schema_version": SCHEMA,
        "total_payloads": n,
        "overall_mix": {v: total.get(v, 0) for v in order},
        "families": {},
    }
    for ct in families:
        c = per_family[ct]
        fam_n = sum(c.values())
        report["families"][ct] = {
            "n": fam_n,
            "counts": {v: c.get(v, 0) for v in order},
            "pct": {v: round(100.0 * c.get(v, 0) / fam_n, 1) if fam_n else 0.0 for v in order},
            "verdicts_reached": sorted([v for v in order if c.get(v, 0)]),
        }

    out_dir = ROOT / "outputs"
    (out_dir / "family_decision_mix.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "# CAPAS per-family decision-mix (decision-space coverage)",
        "",
        f"Total synthetic payloads: **{n}** · run through `capas.decide_external_claim` (the real engine).",
        "",
        "> " + report["disclaimer"],
        "",
        "| Claim family | N | ACCEPT | REWRITE | REJECT | HOLD | verdicts reached |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for ct in families:
        f = report["families"][ct]
        p = f["pct"]
        lines.append(
            f"| `{ct}` | {f['n']} | {p['ACCEPT']}% | {p['REWRITE']}% | {p['REJECT']}% | {p['HOLD']}% | "
            f"{'/'.join(f['verdicts_reached'])} |"
        )
    om = report["overall_mix"]
    lines.append("")
    lines.append(f"Overall: ACCEPT {om['ACCEPT']} · REWRITE {om['REWRITE']} · REJECT {om['REJECT']} · HOLD {om['HOLD']}")
    lines.append("")
    (out_dir / "family_decision_mix.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"family_decision_mix: N={n} across {len(families)} families")
    print("overall:", dict(report["overall_mix"]))
    incomplete = [ct for ct in families if len(report["families"][ct]["verdicts_reached"]) < 2]
    print("families exercising <2 verdicts:", incomplete or "none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
