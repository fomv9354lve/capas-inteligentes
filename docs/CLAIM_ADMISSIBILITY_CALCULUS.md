# CAPAS Claim Admissibility Calculus v1

CAPAS is not a scientific truth oracle. It is a deterministic admissibility
compiler for structured claim/evidence records. Its output answers a narrower
question:

> Given this supplied evidence packet and this registered evidence contract,
> what reuse boundary is licensed for this claim?

This document defines the formal layer implemented by
`admissibility_certificate` in CAPAS schema v3 outputs.

## 1. Problem Class

Neighboring systems usually operate at different levels:

- Dataset governance controls records, source summaries, licenses, and splits.
- Provenance systems such as W3C PROV and RO-Crate describe entities,
  activities, agents, and packaged research objects.
- Scientific fact-checking systems retrieve literature and estimate whether
  a natural-language claim is supported, contradicted, or uncertain.
- Model governance frameworks manage lifecycle risks and documentation duties.

CAPAS occupies the gap between those layers: claim-level admissibility. It
does not ask whether a statement is broadly true. It asks whether supplied,
typed evidence licenses a specific claim boundary for controlled reuse.

This is the operational failure mode CAPAS is designed to catch:

```text
paper sentence:      association observed under limited conditions
dataset sentence:    treatment causes improvement
downstream artifact: governed training example
```

The drift is not only a provenance problem. The source can be known and still
fail to license the rewritten claim boundary.

## 2. Evidence Contracts

Each supported claim type has a registered evidence contract:

```text
C_t = (required_fields, optional_fields, decision_rule, admissible_bounds)
```

For a payload `P = (claim, evidence, training_evidence)`, CAPAS first resolves
the claim type `t = claim.type`. If `t` has no registered contract, CAPAS does
not decide the scientific claim. It emits a HOLD with a proof obligation to
register the claim type and evidence contract.

This is why universal coverage is not achieved by relaxing validation. It is
achieved by making contract registration explicit. Unknown scientific domains
can be added without weakening existing domains.

## 3. Admissibility Lattice

CAPAS assigns each decision to a finite product lattice:

```text
A = Contract x Evidence x Boundary x Provenance x Defeaters
```

Each axis is totally ordered from weakest to strongest.

### Contract Axis

```text
unregistered < registered < schema_clean < contract_complete
```

This axis measures whether CAPAS has a known contract and whether the payload
conforms to it.

### Evidence Axis

```text
none < declared < complete < supports_bounded_claim < supports_claim_boundary
```

This axis measures whether the evidence packet is merely present, complete, or
strong enough for the specific claim boundary.

### Boundary Axis

```text
none < schema_blocked < claim_excluded < bounded_rewrite < claim_licensed < training_ready
```

This is the main reuse boundary. It maps to the operational decision:

- `schema_blocked`: payload cannot be evaluated yet.
- `claim_excluded`: evidence contradicts or fails the claim.
- `bounded_rewrite`: weaker claim boundary is licensed.
- `claim_licensed`: claim is accepted for controlled reuse.
- `training_ready`: claim is accepted and external provenance gates pass.

### Provenance Axis

```text
none < declared < source_backed < externally_reviewed < externally_verified
```

Browser decisions can preview this axis. Full external verification requires
CLI/API operations: URL hashing, review hash checks, witness registry
resolution, RO-Crate validation, and reviewer attestation verification.

### Defeaters Axis

```text
open_defeaters < schema_undercut < burden_gap < bounded_defeater < no_active_defeater
```

Defeaters encode what blocks reuse. A schema undercutter blocks all domain
reasoning. A burden gap means the evidence contract is incomplete. A bounded
defeater supports REWRITE rather than ACCEPT.

## 4. Meet Operations

CAPAS computes two conservative meet values:

```text
controlled_reuse_meet = min(contract, evidence, boundary, defeaters)
training_reuse_meet   = min(controlled_reuse_meet, provenance)
```

The meet prevents a strong result on one axis from hiding a weak result on
another. For example, an ACCEPT verdict with weak provenance can license a
claim boundary for controlled review, but it cannot become `training_ready`
until external provenance verification passes.

## 5. Dialectical Certificate

Each `admissibility_certificate` also includes a dialectical tuple:

```text
D = (thesis, licensed_thesis, warrant, supports, undercutters, rebuttals, obligations)
```

- `thesis`: the original claim text.
- `licensed_thesis`: the accepted or rewritten claim boundary.
- `warrant`: the deterministic reason reported by the rule engine.
- `supports`: supplied evidence fields used in the contract.
- `undercutters`: schema errors and missing fields that block reasoning.
- `rebuttals`: rule-level reasons that reject or weaken the claim.
- `obligations`: concrete proof obligations required for reuse.

This makes CAPAS more like a compiler than a scorer. It produces an artifact
that can be reviewed, queued, exported, and re-run.

## 6. Exception Queue

Batch mode aggregates per-claim certificates into:

```json
{
  "admissibility_summary": {
    "reuse_boundaries": {
      "claim_licensed": 12,
      "bounded_rewrite": 7,
      "schema_blocked": 3
    },
    "next_actions": {
      "verify_provenance_for_training": 12,
      "edit_and_resubmit": 7,
      "repair_schema": 3
    }
  },
  "exception_queue": []
}
```

The queue is not a generic task list. It is routed by formal boundary and next
action:

- `repair_schema`: the record has structural defects.
- `register_claim_type`: no contract exists for this claim type.
- `supply_evidence`: required evidence fields are missing.
- `edit_and_resubmit`: the weaker licensed claim should replace the original.
- `exclude_or_replace_evidence`: the claim is not licensed by current evidence.
- `verify_provenance_for_training`: the claim boundary is licensed, but
  training-data reuse still requires active provenance verification.

## 7. Universalization Strategy

CAPAS should not become universal by accepting arbitrary fields. That would
turn it into a weak form validator. It scales by adding explicit contracts:

```text
new claim family -> evidence contract -> validation rules -> boundary rule
```

For unsupported types, the correct result is HOLD with a contract-registration
obligation. This preserves auditability while giving the system a path to
expand into causality, systematic reviews, multimodal evidence, theorem
claims, biomedical claims, and organization-specific evidence contracts.

## 8. SOTA Positioning

The hard distinction is:

```text
Fact-checking asks: Is this statement true?
Provenance asks: Where did this artifact come from?
Dataset governance asks: What records are in this dataset?
CAPAS asks: Does this evidence packet license this claim boundary for reuse?
```

That last question is narrower than truth and stricter than metadata. It is
also where claim drift enters training data.

Relevant external anchors:

- NIST AI RMF defines governance-oriented risk management for AI systems:
  https://www.nist.gov/itl/ai-risk-management-framework
- EU AI Act Article 10 requires data governance practices for high-risk AI
  training, validation, and testing data:
  https://artificialintelligenceact.eu/article/10/
- W3C PROV defines provenance concepts for entities, activities, and agents:
  https://www.w3.org/TR/prov-overview/
- RO-Crate packages research objects with metadata and contextual entities:
  https://www.researchobject.org/ro-crate/
- Data Provenance Initiative audits dataset lineage, licensing, and
  attribution across large-scale AI datasets:
  https://www.dataprovenance.org/

CAPAS does not replace those layers. It consumes and complements them by
compiling claim-level admissibility certificates.

## 9. Scope Limits

CAPAS is intentionally strict:

- It does not infer hidden evidence.
- It does not certify broad scientific truth.
- It does not replace external expert review.
- It does not make unsupported claim types pass by default.
- It does not make `fine_tune_ready` true from browser-only self-reporting.

These limits are part of the product boundary, not missing features. The
system is useful because it is explicit about what it can and cannot license.
