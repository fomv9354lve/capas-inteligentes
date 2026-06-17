# Reproducibility

CAPAS is auditable only if the corpus can be regenerated from a declared
environment.

## Required Runtime

The full corpus currently requires:

- Python 3.12 or newer
- `numpy`
- `scipy`
- `pyscf`
- `quimb`
- `cotengra`
- `stim`
- local `physics_magnitude_lab`

Install Python packages from:

```bash
python3 -m pip install -r requirements-corpus.txt
```

The local `physics_magnitude_lab` dependency must also be importable. In the
current workspace, the most reliable environment is:

```bash
cd /Users/kreniq/physics-magnitude-lab
/Users/kreniq/.pixi/bin/pixi run python "/Users/kreniq/Desktop/KRENIQ/AI Projects/01. Investigacion/CAPAS INTELIGENTES/scripts/build_evidence_corpus.py"
```

## Environment Check

Run:

```bash
python3 scripts/check_reproducibility_env.py
```

The corpus builder runs this check automatically before generating traces.

## Build Corpus

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

The known warning is accepted for now:

```text
.py is not a recognised workflow extension
```

## Current Debt

The `physics-magnitude-lab` environment has local `pixi.toml` and `pixi.lock`
changes because `pyscf` was added there to regenerate the chemistry traces.

Before sharing CAPAS outside this machine, choose one of:

- vendor CAPAS into the `physics-magnitude-lab` environment;
- create a CAPAS-owned `pixi.toml` with `physics-magnitude-lab` as a local path
  dependency;
- or publish/install `physics-magnitude-lab` as a versioned package.

Until then, CAPAS is reproducible on this machine and auditable in git, but not
portable as a standalone project.
