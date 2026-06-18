# CAPAS Evidence Type System

CAPAS is not only a provenance profile. The stronger framing that emerged from
the corpus is:

```text
CAPAS is an evidence type system for scientific computation.
```

The purpose is not to decide whether a number "looks right". The purpose is to
decide which claims a result is allowed to support, given the evidence attached
to it.

## Core Idea

A scientific result is not just a value:

```text
result = value
```

In CAPAS, the usable object is:

```text
typed_result =
  value
  + provenance
  + physical_evidence_level
  + evidence_scope
  + verification_independence
  + evidence_status
  + ambiguity/error structure
```

The type checker rejects claims that exceed those fields.

## Type Errors CAPAS Must Catch

| Invalid collapse | Why it is invalid | Corpus example |
|---|---|---|
| exact-for-model => physically accurate | A model can be solved exactly and still model the wrong physics. | `trace_021` |
| same-runtime certificate => independent witness | A formal certificate can be strong without being independent. | `trace_016`, `trace_017` |
| local formal bound => global DMRG/observable bound | Bound scope matters; a single-cut state bound is not a global observable certificate. | `trace_016` |
| one optimum => unique decision | Degenerate optima need an external criterion. | `trace_020` |
| local property pass => universal law satisfied | A locally plausible sequence can violate a universal scaling exponent. | `trace_038` |
| within threshold barely => robust success | Passing a threshold with tiny margin is weaker than a robust pass. | `trace_027` |
| experimental comparison => physical correctness | Experimental evidence means the distance to measurement is recorded, not necessarily small. | `trace_021`, `trace_025`, `trace_026` |

## Evidence Types In Current Corpus

Current base evidence levels:

- `analytic`
- `cross_sim`
- `experimental`
- `formal_bound`
- `estimated_bound`
- `none`
- `no_universal_anchor_control`
- `scaling_law_anchor`

Current witness-independence levels are defined in
[`docs/WITNESS_INDEPENDENCE_AXIS.md`](WITNESS_INDEPENDENCE_AXIS.md).

The important rule is that evidence strength and witness independence are
separate axes. For example:

```text
formal_bound + algorithmic_certificate_exact_svd_same_runtime
```

is a strong mathematical certificate, but not an independent witness.

## First Claim Checker

The first executable sketch is:

```text
python3 benchmarks/validate_evidence_claims.py
```

It checks a small preregistered set of claims against existing traces. The goal
is not to cover every possible scientific claim. The goal is to prove that CAPAS
can reject common overclaims mechanically.

Examples:

- reject "exact model solve implies physical chemistry accuracy" for `trace_021`
- accept "exact model solve for declared Hamiltonian" for `trace_021`
- reject "unique optimum" for `trace_020`
- accept "exact optimum set is verified" for `trace_020`
- reject "single-cut formal bound is a global DMRG certificate" for `trace_016`
- accept "single-cut state truncation bound" for `trace_016`
- reject "local properties imply universal scaling" for `trace_038`
- accept "universal anchor caught the scaling violation" for `trace_038`

## Non-Degradation Rule

Do not turn this into an LLM judge.

The current type checker is deliberately rule-based and trace-field based. It
should fail when the evidence field is missing or too weak. The value of CAPAS
is that it refuses to infer a stronger claim from fluent text, provenance, or a
passing local check.

## Scope

This is an initial type-system sketch, not a complete formal logic.

Defensible claim:

```text
CAPAS can represent scientific results as evidence-typed objects and reject
selected overclaims that are not licensed by the attached evidence.
```

Not claimed:

- complete scientific truth validation
- automatic theorem proving
- general LLM honesty detection
- replacement for VVUQ, PROV, RO-Crate, or metamorphic testing

