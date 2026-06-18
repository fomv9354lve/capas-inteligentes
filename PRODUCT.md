# CAPAS Claim Gate

CAPAS is a productized evidence gate for scientific-computation claims.

It takes sealed computation traces and produces claim decisions:

- `ACCEPT`: the trace licenses the claim as written.
- `REWRITE`: the trace supports a narrower claim, not the submitted overclaim.
- `REJECT`: the trace contradicts the claim or lacks required evidence.
- `HOLD`: the trace is missing the fields needed to judge the claim.

## Product Claim

CAPAS turns scientific computation traces into evidence-typed claim decisions,
while preserving provenance, physical evidence level, witness independence,
failure/rejection states, and explicit claim scope.

## Non-Claims

CAPAS does not claim to:

- prove AGI or broad reliable LLM reasoning,
- replace Metamorphic Testing, VVUQ, RO-Crate, PROV, or workflow provenance,
- certify physical truth when the evidence level is `none`, `estimated`, failed,
  or rejected,
- make fine-tune data ready without blind inference review,
- outperform scientific simulators or routers.

## One-Command Demo

```bash
python3 capas.py demo
```

This writes:

- `outputs/capas_product_demo_report.json`
- `outputs/capas_product_demo_report.md`

The demo proves the product surface by reading the versioned evidence reports
and showing:

- all claim-gate checks pass,
- the product emits examples of `ACCEPT`, `REWRITE`, `REJECT`, and `HOLD`,
- D11 universal-anchor evidence licenses complementarity, not dominance,
- `trace_039` is a motor-backed positive control,
- `fine_tune_ready` remains `False`.

## Product Validation

```bash
python3 capas.py validate
python3 benchmarks/verify_capas_product_demo.py
```

`capas.py validate` runs the core product gates:

1. evidence claim gate,
2. universal anchor matrix,
3. CAPAS physical-evidence profile,
4. RO-Crate coverage validation.

`verify_capas_product_demo.py` is the product acceptance test. It fails if the
demo does not expose the four claim decisions, the D11 matrix, the motor-backed
trace, or the `fine_tune_ready=False` safety state.

## Inspect a Trace

```bash
python3 capas.py inspect trace_039
```

This prints the product-relevant evidence summary for a trace: coverage case,
evidence level, witness independence, anchor mode, local/universal checks, and
claim scope.

## Current Demonstrated State

Current versioned evidence supports:

- 39 RO-Crate/PROV trace packages,
- 69/69 claim-gate checks passing,
- 39/39 CAPAS profile checks passing,
- D11 matrix passing with claim `complementarity_not_dominance`,
- motor-backed `trace_039` accepting only a bounded scientific-reasoning claim.

The strongest honest product statement is:

> CAPAS prevents scientific computation traces from licensing claims larger
> than their evidence type supports.

## What Would Make It a Larger Product

The current product is a local CLI/MVP. The next product step is not a larger
claim; it is a stronger interface:

1. JSON input schema for new external traces.
2. A stable claim-rule registry.
3. A packaged RO-Crate profile URI.
4. A small web UI for reviewing `ACCEPT` / `REWRITE` / `REJECT` / `HOLD`.
5. External user validation from a scientific-computation practitioner.
