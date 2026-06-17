# Minimal Review Crate

Use `benchmarks/ro_crates/trace_027/` as the current review crate.

Why this one:

- it is RO-Crate / Workflow Run shape-compatible,
- it contains a sealed `runtrace.json`,
- it contains a PROV-shaped `runtrace.prov.json`,
- it contains `capas:PhysicalEvidence`,
- it exercises experimental truth, model/reference-definition correction,
  robust versus marginal threshold semantics, and a convergence curve.

Validation commands:

```bash
python3 benchmarks/validate_ro_crates.py
python3 benchmarks/validate_capas_profile.py
python3 benchmarks/validate_ro_crates_external.py
```

Current known limitation:

- external ResearchObject RO-Crate validation reports `valid_with_warning`
  because `.py` is not in its recognized workflow-extension list.

What this crate is not:

- not an officially registered CAPAS profile crate,
- not an official Workflow Run RO-Crate profile validation certificate,
- not a claim that CAPAS is a new provenance standard.
