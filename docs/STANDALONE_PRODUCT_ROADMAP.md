# CAPAS Standalone Product Roadmap

Status: first executable standalone slice.

CAPAS started as a deterministic claim gate over already-structured scientific
evidence. The standalone direction adds upstream modules, but keeps one invariant:

> the final claim decision must remain deterministic, auditable, and reproducible.

## Current Executable Slice

The repo now exposes a local three-stage MVP:

```text
local text / solver log / code excerpt
        -> capas extract
        -> capas align
        -> capas pipeline
        -> final ACCEPT / REWRITE / REJECT / HOLD
```

Run it:

```bash
capas extract --input examples/standalone_pipeline_accept.json
capas align --input examples/standalone_pipeline_semantic_hold.json
capas pipeline --input examples/standalone_pipeline_semantic_hold.json
python3 benchmarks/verify_standalone_pipeline.py
```

## What Each Stage Does

### `capas extract`

Extracts explicit evidence assignments from local text, code, or solver logs.

Examples:

```text
abs_error = 0.0
tolerance = 0.0
local_property_tests_pass = true
universal_anchor_pass = false
anchor_mode = absolute_anchor
```

Non-claim: this is not literature retrieval and not hidden inference. If a value
is not explicitly present, the extractor leaves it missing.

### `capas align`

Checks whether `claim.text` is aligned with `claim.type` and supplied evidence
scope.

The first useful guard is model-vs-physical scope:

- `exact_model_solution` can license truth inside a declared model,
- it cannot by itself license "experimentally accurate for the real molecule."

If the numeric evidence passes but the text overclaims, the standalone pipeline
blocks the ACCEPT and returns HOLD.

### `capas pipeline`

Runs extraction, semantic alignment, and the deterministic CAPAS claim gate.

The pipeline may produce a stricter final decision than the gate alone:

- gate alone: `ACCEPT` because `abs_error <= tolerance`,
- pipeline: `HOLD` because the prose claims experimental accuracy while the
  evidence only supports exact model correctness.

## What This Still Does Not Do

This is not yet the large standalone product. It does not:

- retrieve evidence from the web,
- parse PDF structure,
- understand arbitrary scientific prose,
- perform broad scientific reasoning,
- replace domain-specific scientific verifiers.

It is the first safe local bridge toward those modules.

## Product Expansion Path

1. File and evidence intake:
   - Markdown/text/log/code snippets first,
   - PDF and notebook parsing later,
   - optional external retrievers only after provenance is sealed.

2. Semantic alignment:
   - deterministic lexical/scope guards now,
   - claim-type-specific semantic validators next,
   - optional LLM verifier only as an upstream proposer, never as the final gate.

3. Claim-type registry:
   - each claim type declares required fields,
   - expected semantic scope,
   - allowed evidence levels,
   - accepted witness independence levels.

4. Scientific reasoning adapters:
   - exact model solution,
   - physical accuracy,
   - universal anchor,
   - claim transition,
   - future domain modules such as convergence, uncertainty, and reference
     definition match.

5. Reviewer surface:
   - dashboard of accepted, rewritten, rejected, held claims,
   - evidence snippets and source locations,
   - export to RO-Crate/PROV profile.

## Validation

The current standalone slice is validated by:

```bash
python3 benchmarks/verify_standalone_pipeline.py
capas validate
```

The validator checks:

- explicit extraction from a solver log,
- semantic scope mismatch blocking a false ACCEPT,
- universal-anchor overclaim lowering to REWRITE,
- extractor refusal to infer hidden evidence.

## Defensible Claim

Current:

> CAPAS can run a local explicit-evidence intake, deterministic semantic-scope
> guard, and deterministic claim gate over scientific-computation claims.

Not current:

> CAPAS is a general scientific reasoning engine.

