# Debunk 10 More Canonical Overclaims

Date: 2026-06-17

Purpose: extend the executable claim gate across ten additional canonical
top-tier scientific results. Each case preserves the narrow scientific result
that is licensed by the source and rejects or rewrites the inflated claim.

This is not a truth oracle. It is a claim-scope gate: a result can be real,
important, and top-tier while still not licensing the larger story commonly
told around it.

## Result

The executable gate now covers ten more overclaims:

1. Sycamore random-circuit sampling means useful fault-tolerant quantum
   computing exists.
2. Micius satellite QKD means a global untrusted quantum internet exists.
3. GPT-3 few-shot performance means AGI or reliable general reasoning.
4. CRISPR embryo editing research means clinically safe heritable editing.
5. The Human Genome Project solved genetic disease.
6. The Higgs discovery completed physics.
7. Lecanemab cures Alzheimer's disease.
8. Semaglutide SELECT solves cardiovascular disease.
9. JWST early galaxies overturn the Big Bang.
10. Retracted near-room-temperature superconductor claims establish
    superconductivity.

Nine are `REWRITE`: the source licenses a narrower claim. One is `REJECT`: the
room-temperature superconductivity claim is not licensed after retraction and
failed replication.

## Case Matrix

| Case | Licensed Claim | Overclaim Verdict | Source |
|---|---|---:|---|
| Sycamore | Task-specific random-circuit-sampling benchmark advantage | `REWRITE` | https://www.nature.com/articles/s41586-019-1666-5 |
| Micius QKD | Trusted-relay intercontinental satellite QKD demo | `REWRITE` | https://arxiv.org/abs/1801.04418 |
| GPT-3 | Few-shot benchmark gains across many NLP tasks | `REWRITE` | https://arxiv.org/abs/2005.14165 |
| CRISPR embryos | Embryo research reports correction in a fraction of embryos | `REWRITE` | https://www.nature.com/articles/nature23305 |
| Human Genome Project | High-quality euchromatic human reference sequence | `REWRITE` | https://en.wikipedia.org/wiki/Human_Genome_Project |
| Higgs | Higgs-like boson discovered with high significance | `REWRITE` | https://arxiv.org/abs/1207.7214 |
| Lecanemab | Slower decline in early Alzheimer's trial population | `REWRITE` | https://www.nejm.org/doi/full/10.1056/NEJMoa2212948 |
| Semaglutide SELECT | MACE reduction in defined non-diabetic overweight/obesity CVD population | `REWRITE` | https://www.nejm.org/doi/full/10.1056/NEJMoa2307563 |
| JWST early galaxy | Spectroscopically confirmed high-redshift early massive galaxy | `REWRITE` | https://arxiv.org/abs/2303.00306 |
| Room-temperature superconductor | No established claim after retraction/no replication | `REJECT` | https://en.wikipedia.org/wiki/Room-temperature_superconductor |

## Lessons

Top-tier evidence often supports a powerful local statement and a weak global
story. The gate is designed to keep both facts visible:

- It accepts the local statement when the fields are present.
- It rewrites global claims when the source lacks transfer evidence.
- It rejects claims when the evidence record itself is retracted or unreplicated.

The important move is not skepticism for its own sake. It is preserving the
exact scope of the evidence so that a result remains useful without becoming a
myth.

## Executable Hooks

The added checks live in `benchmarks/validate_evidence_claims.py`:

- `DEBUNK_10_TRACES`
- `DEBUNK_10_EXAMPLES`
- claim rules from `quantum_sampling_advantage_supported` through
  `room_temp_superconductor_established`

The expected added behavior is:

```text
accepted narrow claims: 9
rewritten overclaims: 9
rejected overclaims: 1
new executable checks: 19
fine_tune_ready: False
```

