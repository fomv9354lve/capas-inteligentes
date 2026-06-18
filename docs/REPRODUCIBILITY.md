# Reproducibility

CAPAS is auditable only if the shipped corpus can be validated from a declared
environment. Full exploratory regeneration from private/local scientific engines
is outside the public package boundary.

## Required Runtime

The public validation stack currently requires:

- Python 3.12 or newer
- `numpy`
- `scipy`
- `pyscf`
- `quimb`
- `cotengra`
- `stim`

Install Python packages from:

```bash
python3 -m pip install -r requirements-corpus.txt
```

Private/local engine adapters are intentionally not packaged in this public
repository. The public validation path checks the shipped traces and crates.

## Environment Check

Run:

```bash
python3 scripts/check_reproducibility_env.py
```

The corpus builder runs this check automatically before generating traces.

## Validate Published Corpus

Run:

```bash
python3 scripts/build_evidence_corpus.py
```

Expected result:

```text
coverage_ready: True
fine_tune_ready: False
```

`fine_tune_ready=False` is intentional until blind inference review is done.

## External RO-Crate Validation

Run:

```bash
python3 -m pip install -r requirements-validation.txt
python3 benchmarks/validate_ro_crates_external.py
```

Expected result:

```text
external RO-Crate validation passed
```

The external validator currently reports no warnings for generated crates.

## Current Debt

Public validation is portable; full corpus regeneration is not yet a public
contract.

Before claiming public full-regeneration support, choose one of:

- publish public engine adapters that can regenerate the traces without private
  dependencies;
- or declare the shipped trace corpus as the public reproducibility artifact and
  keep private engines outside release assets.

Until then, CAPAS is portable as a validator/claim gate over shipped traces, not
as a full scientific-engine regeneration package.
