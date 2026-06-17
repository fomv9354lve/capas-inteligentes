# CAPAS INTELIGENTES

CAPAS is a small evidence-tracing prototype for scientific computation.

It is not a new provenance standard, benchmark suite, workflow engine, or VVUQ
methodology. CAPAS is a profile/costurero over existing standards:

> RO-Crate/PROV packaging + sealed route/result trace + VVUQ-style physical
> evidence + witness independence + honest no-evidence/failure/rejection states.

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

The important distinction is that not all traces are training gold. Some traces
exist to prove the format can honestly represent uncertainty, failure, or
rejection.

## Build The Evidence Corpus

Use the Python environment that has the scientific stack available. In this
workspace, the most reliable environment is the `physics-magnitude-lab` pixi
environment. The current corpus also requires the quantum-chemistry loader stack
used by `trace_021`: `pyscf`, `openfermion`, and `openfermionpyscf`.

```bash
cd "/Users/kreniq/Desktop/KRENIQ/AI Projects/01. Investigacion/physics_quantum/physics-magnitude-lab"
/Users/kreniq/.pixi/bin/pixi run python "/Users/kreniq/Desktop/KRENIQ/AI Projects/01. Investigacion/CAPAS INTELIGENTES/scripts/build_evidence_corpus.py"
```

The command runs:

1. trace generation
2. PROV export
3. RO-Crate export
4. RO-Crate validation
5. witness independence validation
6. audit summary

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

## External RO-Crate Validation

```bash
python3 -m pip install -r requirements-validation.txt
python3 benchmarks/validate_ro_crates_external.py
```

This uses the ResearchObject `rocrateValidator` package and writes
`benchmarks/ro_crates/official_validation_report.json`. Current crates validate
as RO-Crates with one warning: the CAPAS workflow descriptor is a Python file,
and that validator only recognizes a fixed list of workflow file extensions.

## Positioning

See:

- `docs/PROJECT_DASHBOARD.md`
- `docs/SOTA_POSITIONING.md`
- `docs/WORKFLOW_RUN_RO_CRATE_ALIGNMENT.md`
- `docs/FORMAL_BOUND_AXIS.md`
- `docs/WITNESS_INDEPENDENCE_AXIS.md`
- `docs/OPTIMIZATION_BRIDGE.md`
- `docs/EXPERIMENTAL_EVIDENCE_AXIS.md`
- `docs/SCIAGENTGYM_AUDIT.md`
- `docs/QMB100_AUDIT.md`
- `docs/VVUQ_QUANTUM_AUDIT.md`
- `docs/COVERAGE.md`

Short defensible claim:

> CAPAS packages VVUQ-style physical evidence into sealed RO-Crate/PROV
> scientific traces.
