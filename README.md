# CAPAS INTELIGENTES

[![CAPAS CI](https://github.com/fomv9354lve/capas-inteligentes/actions/workflows/ci.yml/badge.svg)](https://github.com/fomv9354lve/capas-inteligentes/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/fomv9354lve/capas-inteligentes)](https://github.com/fomv9354lve/capas-inteligentes/releases/tag/v0.1.1)

CAPAS is a small evidence-typed claim gate for scientific computation.

It is not a new provenance standard, benchmark suite, workflow engine, or VVUQ
methodology. CAPAS is a profile/costurero over existing standards:

> RO-Crate/PROV packaging + sealed route/result trace + VVUQ-style physical
> evidence + witness independence + honest no-evidence/failure/rejection states.

## Who This Is For

CAPAS is for people auditing AI-generated scientific-computation outputs:

- AI-for-science agent benchmark builders,
- scientific workflow provenance / RO-Crate users,
- quantum many-body verification and benchmark users,
- teams deciding whether a computation supports a strong claim, a weaker
  rewrite, rejection, or hold.

CAPAS is not for users who only need a faster simulator or generic workflow
lineage.

## External Review Packet

For reviewers and potential users:

- Technical note: `docs/CAPAS_TECHNICAL_NOTE.md`
- Request for feedback: `docs/REQUEST_FOR_FEEDBACK.md`
- QMB100 / PhysVEC one-pager: `docs/CAPAS_ONE_PAGER_QMB100.md`
- Global SotA / market audit: `docs/GLOBAL_SOTA_MARKET_AUDIT.md`
- Public demo: `https://fomv9354lve.github.io/capas-inteligentes/`
- Current release: `https://github.com/fomv9354lve/capas-inteligentes/releases/tag/v0.1.1`
- Public feedback issue: `https://github.com/fomv9354lve/capas-inteligentes/issues/1`

The current validation question is not "is CAPAS broadly useful?" It is narrower:
do the explicit evidence fields help audit or exchange one scientific-agent
computation result, or are they already covered by existing artifacts?

## Try In 60 Seconds

```bash
python -m pip install -e .
capas decide --input examples/external_claim_rewrite.json
capas inspect trace_039
capas validate
```

Expected behavior:

- `decide` returns `REWRITE` when local checks pass but a universal anchor fails.
- `inspect trace_039` shows a motor-backed claim-transition trace.
- `validate` runs the product gates and profile/RO-Crate checks.

Release assets:

```text
https://github.com/fomv9354lve/capas-inteligentes/releases/tag/v0.1.1
```

## Product Demo

Install the local package entrypoint:

```bash
python -m pip install -e .
```

Run the product surface:

```bash
capas demo
python3 benchmarks/verify_capas_product_demo.py
```

The demo writes:

- `outputs/capas_product_demo_report.json`
- `outputs/capas_product_demo_report.md`

It demonstrates the current product contract: CAPAS reads sealed scientific
computation traces and emits evidence-typed claim decisions
(`ACCEPT`, `REWRITE`, `REJECT`, `HOLD`) without marking the corpus as
fine-tune-ready.

Run the core product validators:

```bash
capas validate
```

Inspect a trace:

```bash
capas inspect trace_039
```

Decide an external claim/evidence JSON:

```bash
capas schema
capas check-input --input examples/external_claim_accept.json
capas decide --input examples/external_claim_accept.json
capas decide --input examples/external_claim_rewrite.json
capas decide --input examples/external_claim_hold.json
```

The published MVP input contract is
`docs/schema/capas_claim_payload.schema.json`. `check-input` validates the
payload shape; `decide` then checks whether the supplied evidence licenses the
claim, needs a rewrite, contradicts it, or must hold.

Generate the static local UI:

```bash
capas ui
python3 benchmarks/verify_claim_gate_ui.py
```

The UI exposes ACCEPT, REWRITE, HOLD, and INVALID samples. Structurally invalid
payloads are shown as `HOLD` with `schema_errors`, matching `capas decide`.

Prepare a non-mutating GitHub release plan:

```bash
python3 scripts/publish_github_release.py
```

Publishing a new release still requires a GitHub remote, valid `gh auth`, a
pushed tag, a passing external CI run, and a GitHub release URL.

The public v0.1.1 release is available at:

```text
https://github.com/fomv9354lve/capas-inteligentes/releases/tag/v0.1.1
```

Prepare/check external reviewer feedback:

```bash
python3 benchmarks/verify_external_user_validation.py
```

The feedback template is `examples/external_reviewer_feedback_template.json`.
Completed external feedback belongs under `outputs/external_validation/`.

## What It Produces

The corpus builder emits:

- sealed JSON traces: `benchmarks/gold_traces/*.json`
- W3C PROV-shaped exports: `benchmarks/gold_traces/*.prov.json`
- RO-Crate metadata: `benchmarks/ro_crates/*/ro-crate-metadata.json`
- audit table: `audits/gold_trace_audit_template.csv`

## Evidence Fields

CAPAS adds domain evidence fields over standard provenance:

- `physical_evidence_level`
- `verification_independence`
- `witness_stack`
- `reference_truth`
- `evidenceStatus`
- `abs_error`
- `expected`
- `value`
- `observable`
- `local_property_tests`
- `universal_anchor`
- `invariant_caught`
- `claim_scope`

The important distinction is that not all traces are training gold. Some traces
exist to prove the format can honestly represent uncertainty, failure, or
rejection.

## Validate The Published Evidence Corpus

Use a Python environment that has the declared public corpus stack available.
Check it first:

```bash
python3 scripts/check_reproducibility_env.py
```

The public repository ships the evidence traces and validators. Private/local
scientific engines used during exploratory corpus generation are intentionally
not packaged in the public release. The public command runs:

1. RO-Crate validation
2. CAPAS physical-evidence profile validation
3. witness independence validation
4. evidence claim validation
5. universal anchor matrix validation
6. audit summary

```bash
python3 scripts/build_evidence_corpus.py
```

`coverage_ready=True` is expected. `fine_tune_ready=False` is also expected until
blind inference review is completed.

## Validate RO-Crate Coverage

```bash
python3 benchmarks/validate_ro_crates.py
```

The validator checks that evidence is present where it should be and absent where
it would be dishonest:

- analytic success: `present`
- cross-sim success: `present`
- no-evidence success: `none_declared`
- backend failure: `not_applicable_failed`
- router rejection: `not_applicable_rejected`

## Validate CAPAS Physical Evidence Profile

```bash
python3 benchmarks/validate_capas_profile.py
```

This checks the local CAPAS profile over Workflow Run RO-Crate-style crates:
WRROC profile URIs, `ComputationalWorkflow`, top-level `CreateAction`, parameter
realization, `capas:evidenceStatus`, and `capas:PhysicalEvidence` semantics.
This is a local profile validator, not official profile registration.

## External RO-Crate Validation

```bash
python3 -m pip install -r requirements-validation.txt
python3 benchmarks/validate_ro_crates_external.py
```

This uses the ResearchObject `rocrateValidator` package and writes
`benchmarks/ro_crates/official_validation_report.json`. Current crates validate
as RO-Crates without warnings. CAPAS emits a recognized `.cwl` workflow
descriptor for packaging and records Python as the implementation language for
the costurero.

## Positioning

See:

- `docs/PROJECT_DASHBOARD.md`
- `docs/REPRODUCIBILITY.md`
- `docs/SOTA_POSITIONING.md`
- `docs/WORKFLOW_RUN_RO_CRATE_ALIGNMENT.md`
- `docs/profile/CAPAS_PHYSICAL_EVIDENCE_PROFILE.md`
- `docs/FORMAL_BOUND_AXIS.md`
- `docs/WITNESS_INDEPENDENCE_AXIS.md`
- `docs/OPTIMIZATION_BRIDGE.md`
- `docs/EXPERIMENTAL_EVIDENCE_AXIS.md`
- `docs/UNIVERSAL_INVARIANT_ANCHORING.md`
- `docs/METAMORPHIC_TESTING_POSITIONING.md`
- `docs/SCIAGENTGYM_AUDIT.md`
- `docs/QMB100_AUDIT.md`
- `docs/VVUQ_QUANTUM_AUDIT.md`
- `docs/COVERAGE.md`
- `docs/EXTERNAL_MVP_LAUNCH_PLAN.md`

Short defensible claim:

> CAPAS is an evidence-typed claim gate over scientific-computation traces: it
> reads or packages provenance-aligned evidence and decides whether that evidence
> licenses ACCEPT, REWRITE, REJECT, or HOLD.
