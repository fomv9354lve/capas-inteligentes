# CAPAS Hybrid Pipeline Positioning

Status: current product positioning after 2026 scientific-claim-verification
SotA review.

## One-Sentence Position

CAPAS is the deterministic claim gate in a hybrid AI-for-science verification
pipeline.

It does not retrieve remote evidence, parse PDFs, or semantically interpret
arbitrary scientific prose. It now includes a small local upstream MVP that can
extract explicit evidence assignments from text/log snippets and run a
deterministic claim-text scope guard. The core claim decision still assumes
structured claim/evidence JSON and then decides, deterministically, what claim
the evidence licenses:

```text
ACCEPT / REWRITE / REJECT / HOLD
```

## Pipeline Shape

```text
LLM / extractor / scientific verifier upstream
or CAPAS local explicit extractor
        |
        v
claim + evidence JSON
        |
        v
optional deterministic claim-text alignment
        |
        v
CAPAS deterministic claim gate
        |
        v
ACCEPT / REWRITE / REJECT / HOLD
        |
        v
corpus, paper, dashboard, audit trail, or fine-tune queue
```

CAPAS owns the middle deterministic gate. The first upstream slice is now
available locally as `capas extract`, `capas align`, and `capas pipeline`.
That slice is explicit-only and deterministic; it is not broad scientific
reasoning.

## Why This Exists

Recent scientific-claim-verification work identifies a structural problem:
AI systems can generate plausible scientific artifacts faster than existing
review systems can verify them.

The relevant failure mode for CAPAS is not only hallucination. It is over-strong
claim licensing:

- evidence supports a weaker claim,
- one required constraint is missing,
- local checks pass but a universal or physical anchor fails,
- a result is exact for a model but not accurate against experiment,
- a witness is not independent enough for the proposed claim.

CAPAS makes those transitions explicit and deterministic.

## What CAPAS Covers

CAPAS covers structured, local, decidable checks:

- numeric thresholds such as `abs_error <= tolerance`,
- typed evidence states,
- required-field presence,
- physical evidence levels,
- witness independence labels,
- claim transitions such as `ACCEPT -> REWRITE`.

Given the same JSON, CAPAS returns the same verdict.

## What CAPAS Does Not Cover Yet

CAPAS now includes a minimal deterministic scope check for free-text
`claim.text`, but it does not solve general semantic verification.

For example, if an upstream system supplies a nonsensical claim text with
otherwise valid evidence fields, CAPAS can validate the structured evidence but
does not understand the prose.

The current executable form is:

```text
capas extract:
local text/log/code -> explicit evidence assignments

capas align:
claim.text <-> claim.type <-> evidence scope

capas pipeline:
extract -> align -> deterministic gate
```

Future semantic checkers can be neural, symbolic, or hybrid, but they should sit
upstream or beside CAPAS. CAPAS should remain the deterministic final gate.

## Standalone Product Direction

The current public product is a component, not a complete standalone platform.

A larger standalone CAPAS product still needs:

1. stronger evidence extraction from papers, code, solver logs, or agent runs,
2. deeper semantic alignment between `claim.text` and structured evidence,
3. a claim-type registry,
4. adapters for scientific-agent benchmark outputs,
5. reviewer dashboards and audit storage,
6. optional integration with RO-Crate/PROV workflow provenance.

That larger product should preserve the current invariant:

> the final claim decision remains deterministic and auditable.

## Non-Claims

CAPAS does not claim:

- to replace LLM-based scientific claim verification,
- to perform retrieval,
- to solve arbitrary text entailment,
- to prove broad LLM scientific reasoning,
- to be fine-tune ready without external review.

The defensible current claim is narrower:

> CAPAS is the deterministic claim-decision layer for already-structured
> scientific-computation evidence.
