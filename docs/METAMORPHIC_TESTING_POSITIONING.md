# Metamorphic Testing Positioning

Status: hostile search result captured, not a code change.

## What This Search Changes

D11 universal invariant anchoring must be positioned against Metamorphic Testing
(MT), not presented as a new testing paradigm.

Metamorphic Testing is an established property-based testing technique for the
test-oracle problem. It uses metamorphic relations: necessary properties of the
intended functionality that usually relate multiple executions of the software.
It has been applied to scientific software and, in current work, to LLM
evaluation and scientific ML surrogates.

Therefore CAPAS must not claim:

- it invented invariant/property-based verification,
- it invented oracle-free testing,
- it invented seeded-fault scientific testing,
- it invented the pattern "local tests miss, invariant/property catches",
- it invented applying these ideas to scientific software.

## Closest Known Neighbors

### Metamorphic Testing

Source:

- https://en.wikipedia.org/wiki/Metamorphic_testing

MT addresses the test-oracle problem by checking metamorphic relations across
executions. This is the parent field for much of the D11 idea.

### Scientific Software MT

Source:

- https://eprints.whiterose.ac.uk/id/eprint/172370/

Chen et al. applied MT to thermodynamics/PDE scientific software and showed a
seeded fault missed by special test cases but revealed by one metamorphic
relation. That is structurally close to `trace_028`.

### LLM Metamorphic Testing

Sources:

- https://arxiv.org/abs/2603.24774
- https://arxiv.org/abs/2605.23965

Recent LLM work uses metamorphic testing/logical invariance to expose reasoning
defects without relying only on static reference benchmarks.

### SciML Metamorphic Test Assets

Source:

- https://arxiv.org/abs/2606.17529

Domain-validity-gated MT for scientific ML surrogates is especially close to
CAPAS in discipline: relation validity, numerical floor, typed verdicts, and
claim ledger. CAPAS must not claim that executable, auditable SciML invariant
test assets are absent.

### Physics-Constrained / Invariant-Aware AI

Sources:

- https://arxiv.org/abs/2602.11666
- https://arxiv.org/abs/2603.23861
- https://arxiv.org/abs/2606.08238

These works show active 2026 work on symbolic/physical validation,
invariant-preserving architectures, and thermodynamics/conservation-compliant
LLM-assisted scientific modeling. CAPAS must not claim that "physics invariants
for AI" is empty.

## Narrow CAPAS Difference

The remaining defensible distinction is not "invariant testing". It is:

> CAPAS packages absolute, theory-known physical anchors as first-class
> evidence inside sealed RO-Crate/PROV scientific traces, recording local oracle
> outcome, universal-anchor outcome, witness independence, claim scope, and
> failure/no-anchor controls.

The narrower distinction from classic MT is:

- MT usually checks relations among multiple executions when the expected output
  is unavailable.
- CAPAS D11 currently checks absolute anchors where theory gives a known target:
  `E0 = -3J/4` or Bell entropy `S = ln2`.

This is not stronger in all domains. It is stronger only in the subset where the
physics provides a known value or universal scaling target.

## What Trace 028-032 Demonstrate

The current D11 matrix demonstrates that CAPAS can seal:

- local miss / universal catch,
- local catch / anchor not credited,
- local catch / universal catch,
- non-Heisenberg transfer to Bell entropy,
- no-anchor control without inventing evidence.

That supports complementarity between local oracles and universal anchors, not
dominance.

The executable matrix validator is:

```bash
python3 benchmarks/validate_universal_anchor_matrix.py
```

Current measured cells:

| Cell | Count | Traces | Meaning |
|---|---:|---|---|
| `local_miss_anchor_catch` | 5 | `trace_028`, `trace_031`, `trace_033`, `trace_037`, `trace_038` | Universal anchor adds coverage missed by local checks |
| `local_catch_anchor_not_needed` | 2 | `trace_029`, `trace_035` | Local oracle is sufficient; anchor is not credited |
| `both_catch` | 1 | `trace_030` | Local oracle and universal anchor overlap |
| `both_pass` | 3 | `trace_034`, `trace_036`, `trace_039` | Positive controls pass both gates |
| `no_anchor_control` | 1 | `trace_032` | CAPAS records absence of a universal anchor |

Licensed claim:

> Absolute universal anchors complement local/property/metamorphic checks in
> the current D11 trace set. They add marginal detection in some locally
> plausible failures, but they do not dominate local checks and do not replace
> Metamorphic Testing.

Forbidden claim:

> Universal anchors are generally superior to local/property/metamorphic
> testing.

## What It Does Not Demonstrate

The current matrix does not demonstrate:

- general superiority over MT,
- general superiority over local PBT/RvLLM-style checks,
- scalability to arbitrary scientific agents,
- benchmark-level effectiveness on real agent outputs,
- novelty over scientific software MT as a testing idea.

## Scaling-Law Seed Status

`trace_033` through `trace_038` add an Ising finite-size scaling seed:

- expected exponent: `z = 1`,
- preregistered tolerance: `|z_fit - 1| <= 0.10`,
- local oracle: positive finite gaps strictly decrease with size,
- anchor kind: `absolute_scaling_law`,
- `trace_033`: hand-authored adversarial sequence with wrong exponent `z=0.5`,
- `trace_034`: hand-authored noisy positive control with `z=1.004`,
- `trace_035`: hand-authored constant-sequence local failure,
- `trace_036`: exact-diagonalization TFIM open-chain sequence with `z=0.917`.
- `trace_037`: seeded randomized adversarial family with eight plausible
  decreasing sequences; all fitted exponents miss `z=1` beyond the
  preregistered tolerance.
- `trace_038`: deterministic scripted-agent transcript that emits a plausible
  `L^-1/2` table; local checks pass and the absolute scaling anchor catches it.
- `trace_039`: motor-backed scripted exact-diagonalization TFIM sequence that
  passes both local checks and the absolute `z=1` scaling anchor, licensing only
  a bounded positive transition control.

This closes the first "not only exact small-system values" debt and adds one
non-synthetic simulation-generated scaling sequence plus one randomized
adversarial seed plus one scripted-agent seed. It still does not prove
benchmark-level utility on LLM-agent outputs.

## Next Non-Degradable Step

The remaining hardening path is to replace the scripted-agent seed with a real
LLM-agent failure corpus if a generator source is explicitly available, still
carrying:

- preregistered tolerance,
- finite-size/error bars,
- local oracle result,
- universal scaling-anchor result,
- noisy/generator-trivial negative control,
- explicit `anchor_mode` statement: `absolute_anchor`,
  `metamorphic_relation`, `mixed`, or `none`.

The current D11 closure uses an embedded scripted agent, not an LLM. Do not
claim LLM-agent utility until a real LLM-generated failure corpus is present.
