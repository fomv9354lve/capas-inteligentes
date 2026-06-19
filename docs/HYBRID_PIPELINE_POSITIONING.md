# CAPAS Hybrid Pipeline Positioning

Status: current product positioning after 2026 scientific-claim-verification
SotA review.

## One-Sentence Position

CAPAS is the deterministic claim gate in a hybrid AI-for-science verification
pipeline.

It does not retrieve evidence, parse papers, or semantically interpret arbitrary
claim text. It assumes a prior stage has produced structured claim/evidence JSON
and then decides, deterministically, what claim the evidence licenses:

```text
ACCEPT / REWRITE / REJECT / HOLD
```

## Pipeline Shape

```text
LLM / extractor / scientific verifier upstream
        |
        v
claim + evidence JSON
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

CAPAS owns the middle deterministic gate. It does not currently own the
upstream extraction or semantic-alignment stages.

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

CAPAS does not currently verify that free-text `claim.text` semantically matches
the supplied evidence fields.

For example, if an upstream system supplies a nonsensical claim text with
otherwise valid evidence fields, CAPAS can validate the structured evidence but
does not understand the prose.

That is the next missing module:

```text
semantic alignment checker:
claim.text <-> claim.type <-> evidence fields
```

This checker can be neural, symbolic, or hybrid. It should sit upstream or
beside CAPAS. CAPAS should remain the deterministic final gate.

## Standalone Product Direction

The current public product is a component, not a complete standalone platform.

A larger standalone CAPAS product would need:

1. evidence extraction from papers, code, solver logs, or agent runs,
2. semantic alignment between `claim.text` and structured evidence,
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
