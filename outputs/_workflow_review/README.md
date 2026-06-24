# Workflow review holding — gap-closure artifacts (2026-06-24)

Artifacts produced by the bottom-up nodal gap-closure workflow. Quality was high (per-gap avg 7.83 / 8.20 /
8.90, **0 REJECT** — see `docs/GAP_CLOSURE_DOSSIER.md`), but these are **internal working drafts**
(research protocol, draft-for-counsel legal instruments, pharma sales/integration collateral), **not
public-landing content**. This directory is git-tracked (versioned, nothing lost) but `.dockerignore`d, so
nothing here is served on the live site. Promote an individual file deliberately when it's needed.

## Promoted OUT of holding (verified code, now in the live tree)

These three self-tested cleanly and were moved to their proper locations + committed:

- `capas_pharma_schema.py` (repo root) — pharma contract surface; `selftest` passes (admits the 3,024 grid,
  4 verdicts round-trip, malformed rejected).
- `benchmarks/attest_conformance.py` — third-party-runnable §5/§6 attestation; CLAIMABLE=True,
  reproduces `result_hash sha256:3d3b5cf39aaffef23fa8562b`, gate ACCEPT + tamper-detected.
- `benchmarks/study_assembly.py` — tamper-evident study assembly; self-test OK, deterministic merkle_root,
  the SCOPED→BACKED registry flips stay fail-closed-gated until a real study is run.

## Held here (internal drafts — versioned, NOT published)

`docs/CROSS_DOMAIN_STUDY_PROTOCOL.md`, `CROSS_DOMAIN_STUDY_ANALYSIS_PLAN.md`,
`GOVERNANCE_OPERATIONALIZATION.md`, `ADOPTION_GATE_READINESS_LEDGER.md`, `PHARMA_P21_INTEGRATION_SEAM.md`,
`PHARMA_VALUE_ROI_INSTRUMENT.md`, `PHARMA_CONFORMANCE_ONBOARDING.md`,
`PHARMA_CERTIFICATION_MARK_PRECONDITION.md`, `BEACHHEAD_PHARMA_ONEPAGER.md`, `MOAT_AND_CERTIFICATION.md`,
`GAP_CLOSURE_DOSSIER.md`.

- `MOAT_EDIT_QUEUE.md` — **job done**: its 14 surgical edits were applied to the live site/docs (the moat
  honesty pass). Kept as the audit record.
- **5 nodes were `regla_cero:false`** (locked-analysis-plan, tamper-evident-assembly, independence-positioning,
  escrow-transfer-instrument, p21-evidence-seam): not wrong — they lean on construction-side derivations or
  draft-for-counsel language rather than one executable command (appropriate for their layer). Re-verify the
  citation anchor at execution time before any of these is published or acted on.

## What flips these from draft to real (no agent can do it)

Per the dossier's execution checklist: **P1** name the trustee + execute escrow (counsel); **P2** recruit
blind adjudicators + register the pre-registration on OSF, then collect/adjudicate; **P3** sign a named
pharma design partner; **P4** publish PyPI 0.4.0. No `CLAIMS_REGISTRY` row flips until these run.
