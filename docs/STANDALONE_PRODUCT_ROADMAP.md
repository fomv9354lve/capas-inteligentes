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
capas retrieve --input examples/standalone_pipeline_multisource.json
capas retrieve --input examples/standalone_pipeline_web_source.json --allow-web
capas extract --input examples/standalone_pipeline_accept.json
capas extract --input examples/standalone_pipeline_pdf_source.json
capas align --input examples/standalone_pipeline_semantic_hold.json
capas reason --input examples/standalone_pipeline_semantic_hold.json
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

The extractor also records `evidence_spans`:

```json
{
  "anchor_mode": {
    "source_id": "paper_excerpt",
    "source_kind": "paper_excerpt",
    "line": 1,
    "snippet": "The scaling benchmark declares anchor_mode = absolute_anchor.",
    "parser": "string"
  }
}
```

This makes the local evidence auditable instead of just extracted.

### `capas retrieve`

Retrieves local source lines likely relevant to the required evidence fields for
the claim type. It is field-driven and can read local sources by default:

```bash
capas retrieve --input examples/standalone_pipeline_multisource.json
```

Web retrieval is explicit:

```bash
capas retrieve --input examples/standalone_pipeline_web_source.json --allow-web
```

Without `--allow-web`, declared URLs produce a `not_retrieved` snippet with a
note. This avoids accidental network access during audits.

### PDF Sources

Local PDF parsing is optional:

```bash
python -m pip install -e ".[standalone]"
capas extract --input examples/standalone_pipeline_pdf_source.json
```

If the optional parser is missing or the PDF cannot be parsed, CAPAS records the
parser failure as an extraction note. It does not infer evidence from a failed
parse.

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

This is now a narrow end-to-end standalone product surface. It still does not:

- understand arbitrary scientific prose,
- perform broad scientific reasoning,
- replace domain-specific scientific verifiers.

It now has deterministic local corpus retrieval plus first-pass web retrieval
and PDF parsing hooks, but they are narrow: field-driven retrieval, optional
dependencies, and explicit failure notes.

### `capas reason`

Runs a deterministic scientific evidence/scope checklist over the extracted
evidence, semantic alignment, and CAPAS gate decision.

It flags risks such as:

- missing source spans for required fields,
- model truth being stated as experimental truth,
- weak or undeclared witness independence,
- universal-anchor claims without `absolute_anchor`.

Non-claim: this is not general scientific reasoning. It is a transparent
checklist that names obvious evidence/scope risks.

## Product Expansion Path

1. File and evidence intake:
   - Markdown/text/log/code snippets first,
   - local JSON/JSONL/text corpus adapters now,
   - PDF parsing now, notebook parsing later,
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
   - causal mechanism,
   - systematic review,
   - evidence conflict,
   - multimodal evidence,
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
- multsource extraction with auditable field-level spans,
- semantic scope mismatch blocking a false ACCEPT,
- universal-anchor overclaim lowering to REWRITE,
- extractor refusal to infer hidden evidence.

## Defensible Claim

Current:

> CAPAS can run a local explicit-evidence intake, deterministic semantic-scope
> guard, and deterministic claim gate over scientific-computation claims.

Not current:

> CAPAS is a general scientific reasoning engine.
