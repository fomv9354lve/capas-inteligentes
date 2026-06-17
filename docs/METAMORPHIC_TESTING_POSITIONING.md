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

## What It Does Not Demonstrate

The current matrix does not demonstrate:

- general superiority over MT,
- general superiority over local PBT/RvLLM-style checks,
- scalability to arbitrary scientific agents,
- effectiveness on scaling laws or finite-size noisy data,
- novelty over scientific software MT as a testing idea.

## Next Non-Degradable Step

Add a scaling-law anchor, such as Ising critical exponent or Kibble-Zurek
scaling, with:

- preregistered tolerance,
- finite-size/error bars,
- local oracle result,
- universal scaling-anchor result,
- noisy/generator-trivial negative control,
- explicit statement whether the result is absolute-value anchoring,
  metamorphic-relation anchoring, or both.

Done when D11 is no longer only exact small-system invariants.
