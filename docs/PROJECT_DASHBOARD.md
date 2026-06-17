# CAPAS Project Dashboard

Last updated: 2026-06-17

This dashboard is the non-degradable control surface for CAPAS. If future work
changes a claim, a coverage case, or a validation status, update this file in the
same commit.

## Current Position

CAPAS is a RO-Crate/PROV evidence profile for scientific computation traces.

It does not claim to invent:

- scientific workflow provenance
- structured scientific traces
- golden traces
- RO-Crate/PROV packaging
- verification against reference
- VVUQ
- automatic backend routing

Defensible claim:

> CAPAS packages graduated physical evidence into sealed RO-Crate/PROV workflow
> run traces, explicitly recording evidence strength, witness independence,
> route/result provenance, and honest failure/rejection/no-evidence states.

## Latest Auditable State

Repository head:

```text
See git log. This dashboard is updated in the same commit as state changes.
```

Recent commits:

```text
HEAD Add methane electronic/vibrational chemistry trace
65c1e5b Add electronic/vibrational chemistry protocol
a7447b0 Add reference-definition corrected chemistry trace
e80a598 Add larger-basis chemistry stress trace
1de6e14 Add improved-basis chemistry evidence trace
```

Current validation status:

```text
coverage_ready: True
fine_tune_ready: False
local RO-Crate validation: passed
external ResearchObject RO-Crate validation: valid_with_warning for 26/26 crates
external warning: .py is not a recognised workflow extension
witness independence validation: passed
```

The external warning is known and currently accepted: CAPAS emits a Python
workflow descriptor because the costurero is implemented in Python. The
ResearchObject validator recognizes a fixed workflow-extension list.

## Evidence Coverage

| Case | Count | Status | Meaning |
|---|---:|---|---|
| `analytic_success` | 10 | covered | closed-form truth |
| `cross_sim_success` | 1 | covered | independent algorithmic witness |
| `cross_library_success` | 1 | covered | different-library same-runtime witness |
| `combinatorial_optimization_function_level` | 1 | covered | assignment-to-Ising optimum verified by brute force |
| `combinatorial_optimization_degenerate_function_level` | 1 | covered | assignment-to-Ising optimum set verified by brute force |
| `quantum_chemistry_experimental_reference` | 1 | covered | H2/STO-3G FCI compared with measured dissociation energy |
| `quantum_chemistry_experimental_reference_improved_basis` | 1 | covered | H2/cc-pVDZ FCI compared with measured dissociation energy |
| `quantum_chemistry_experimental_reference_larger_basis` | 1 | covered | H2/cc-pVTZ FCI compared with measured dissociation energy |
| `quantum_chemistry_reference_definition_corrected` | 1 | covered | H2/cc-pVTZ compared with D0 plus same-model harmonic ZPE |
| `quantum_chemistry_polyatomic_electronic_vibrational` | 1 | covered | H2O/STO-3G electronic/vibrational split against atomization reference |
| `quantum_chemistry_larger_polyatomic_electronic_vibrational` | 1 | covered | CH4/STO-3G electronic/vibrational split against atomization reference |
| `formal_bound_success` | 1 | covered | formal single-cut Schmidt truncation certificate |
| `formal_bound_composition_success` | 1 | covered | formal multi-step state truncation bound |
| `estimated_bound_candidate` | 1 | covered | useful estimator, not formal |
| `no_evidence_success` | 1 | covered | successful result with no witness |
| `backend_failed` | 1 | covered | backend failure sealed honestly |
| `rejected_by_router` | 1 | covered | non-execution/rejection sealed honestly |

Current evidence levels:

```text
analytic: 12
cross_sim: 2
experimental: 6
formal_bound: 2
estimated_bound: 1
none: 3
```

## What Works

1. Sealed RunTrace generation.
2. PROV-shaped export.
3. RO-Crate export.
4. Workflow Run RO-Crate-compatible shape.
5. External RO-Crate validation through ResearchObject `rocrateValidator`.
6. CAPAS `PhysicalEvidence` entity in RO-Crate and PROV exports.
7. Honest distinction between:
   - analytic truth
   - cross-sim witness
   - formal bounded evidence
   - estimated bounded evidence
   - no evidence
   - failed execution
   - rejected execution
8. Formal-bound seed case:
   - single-cut Schmidt truncation
   - discarded weight equals squared state error
   - not claimed as global DMRG certificate
9. Multi-step formal-bound composition seed case:
   - sequential non-renormalized Schmidt truncations
   - triangle-composed state-error bound
   - not claimed as DMRG/observable certificate
10. Optimization bridge seed case:
   - N=8, K=2 assignment problem
   - explicit Ising mapping with affinity, balance, and conflict terms
   - exact diagonalization checked against brute force over 256 assignments
   - not claimed as optimization speedup
11. Degenerate optimization bridge seed case:
   - N=8, K=2 assignment problem with symmetric neutral tasks
   - exact optimum set contains 2 assignments
   - trace records that the final choice among equivalent optima needs an external criterion
12. Experimental chemistry evidence seed case:
   - H2/STO-3G at R=0.7414 Angstrom
   - PySCF FCI total energy: `-1.137270174660904` Hartree
   - model binding energy: `0.20410647554635353` Hartree
   - measured D0 reference: `0.1640261683512219` Hartree
   - solver error: `0.0`
   - model error: `0.040080307195131615`
   - within chemical accuracy: `False`
13. Improved-basis chemistry evidence seed case:
   - H2/cc-pVDZ at R=0.7414 Angstrom
   - PySCF FCI total energy: `-1.1634139335373228` Hartree
   - model binding energy: `0.16485712669815622` Hartree
   - measured D0 reference: `0.1640261683512219` Hartree
   - solver error: `0.0`
   - model error: `0.0008309583469343074`
   - within chemical accuracy: `True`
14. Larger-basis chemistry stress case:
   - H2/cc-pVTZ at R=0.7414 Angstrom
   - basis orbitals: `28`
   - model binding energy: `0.17271607159149482` Hartree
   - measured D0 reference: `0.1640261683512219` Hartree
   - solver error: `0.0`
   - model error: `0.008689903240272911`
   - within chemical accuracy: `False`
   - lesson: larger basis alone is not a monotonic guarantee against the chosen measured reference
15. Reference-definition corrected chemistry case:
   - H2/cc-pVTZ at R=0.7414 Angstrom
   - basis orbitals: `28`
   - model binding energy: `0.1727160715914744` Hartree
   - raw measured D0 reference: `0.1640261683512219` Hartree
   - same-model harmonic ZPE correction: `0.010222574189245201` Hartree
   - corrected De-like reference: `0.17424874254046713` Hartree
   - raw D0/reference-definition error: `0.008689903240252483`
   - corrected error: `0.0015326709489927315`
   - within chemical accuracy after definition correction: `True`
   - lesson: `trace_023` was not a solver failure; it mixed electronic De-like energy with experimental D0
16. Polyatomic electronic/vibrational chemistry case:
   - H2O/STO-3G demo geometry
   - PySCF FCI total energy: `-75.01264711899171` Hartree
   - electronic atomization energy: `0.2753331866212392` Hartree
   - harmonic frequencies: `[2044.5504790587445, 4486.6568066119635, 4788.270182239422] cm^-1`
   - same-model harmonic ZPE: `0.025787667114932907` Hartree
   - ZPE-corrected atomization energy: `0.24954551950630627` Hartree
   - tabulated atomization reference: `0.35154847714349774` Hartree
   - corrected error: `0.10200295763719147`
   - within chemical accuracy: `False`
   - lesson: CAPAS can seal a polyatomic electronic/vibrational split even when the model remains poor
17. Larger polyatomic electronic/vibrational chemistry case:
   - CH4/STO-3G tetrahedral demo geometry
   - PySCF FCI total energy: `-39.80599835127127` Hartree
   - electronic atomization energy: `0.7209374024057098` Hartree
   - harmonic frequencies: `[1689.8745762074116, 1689.8745762074573, 1689.8745762074593, 1908.0111834277131, 1908.011183427716, 3470.156201716289, 3726.74135851723, 3726.74135851724, 3726.741358517245] cm^-1`
   - same-model harmonic ZPE: `0.05361901333601985` Hartree
   - ZPE-corrected atomization energy: `0.66731838906969` Hartree
   - tabulated atomization reference: `0.6326597707432847` Hartree
   - corrected error: `0.034658618326405266`
   - within chemical accuracy: `False`
   - lesson: adding vibrational correction can reduce the mismatch without making a poor finite-basis model chemically accurate

## Non-Degradation Rules

These are hard guardrails.

1. Do not rename `estimated_bound` to `formal_bound`.
2. Do not call quimb `CircuitMPS.fidelity_estimate()` a formal certificate.
3. Do not claim CAPAS invented provenance, RO-Crate, PROV, golden traces, VVUQ,
   or workflow tracing.
4. Do not mark `fine_tune_ready=True` without blind inference review.
5. Do not remove failed/rejected/no-evidence coverage cases.
6. Do not treat same-runtime certificates as independent witnesses.
7. Do not claim DMRG global error bounds until the assumptions and accumulation
   rule are explicit and tested.
8. Do not claim official CAPAS profile registration until a profile URI is
   actually registered externally.
9. Do not treat external RO-Crate `valid_with_warning` as warning-free
   validation.
10. Any new evidence level must include:
    - scope
    - witness independence
    - failure mode
    - validation command
11. Do not compare electronic `D_e`-like quantities against experimental `D0`
    without recording `reference_definition_match` and any correction.
12. Do not treat same-model harmonic ZPE as anharmonic spectroscopy.

## Debt Register

### D1. Fine-Tune Readiness

Status: in progress.

Current state:

```text
fine_tune_ready: False
hold: 23
reject: 3
blank: 0
```

Debt:

- blind inference review is not done
- accepted rows are not selected
- audit has no blank trace slots

Done when:

- each accepted trace has blind inference judgment
- each accepted trace has acceptable physical evidence
- enough accepted traces exist to justify training

Validation:

```bash
python3 audits/summarize_gold_trace_audit.py
```

### D2. Formal Bound Beyond Single-Cut SVD

Status: partially complete.

What exists:

- `trace_016`
- `physical_evidence_level=formal_bound`
- `bound_scope=single_bipartition_state_truncation`
- `trace_017`
- `bound_scope=multi_step_state_truncation`
- `actual_error_squared=0.5946588973100263`
- `composed_state_error_bound=1.472341209732678`
- `bound_slack=0.8776823124226517`

Debt:

- no global DMRG state certificate
- no observable-error transfer bound
- controlled multi-step truncation composition exists outside DMRG
- no truncation accumulation rule across DMRG sweeps

Next step:

- instrument `physics-magnitude-lab` DMRG to return local discarded weights
- document canonical-form and normalization assumptions
- decide whether the accumulated quantity is formal, estimated, or candidate

Done when:

- a DMRG trace can emit `formal_bound` or `formal_bound_candidate` with explicit
  scope and assumptions
- no observable bound is implied unless actually derived

### D3. Witness Independence Axis

Status: in progress.

Seed fact:

- CAPAS already records `verification_independence`
- current levels include `analytic_no_solver`, `different_library_same_runtime`,
  `different_method_same_runtime`,
  `same_runtime_exact_fci_with_external_experimental_reference`,
  `different_algorithm_same_runtime`,
  `algorithmic_certificate_exact_svd_same_runtime`,
  `algorithmic_error_certificate_same_runtime`, and `none`

What exists:

- `docs/WITNESS_INDEPENDENCE_AXIS.md`
- `benchmarks/validate_witness_independence.py`
- `trace_018` as a SciPy cross-library same-runtime witness
- eight current levels covered:
  - `analytic_no_solver`: 10
  - `different_library_same_runtime`: 1
  - `different_method_same_runtime`: 2
  - `same_runtime_exact_fci_with_external_experimental_reference`: 4
  - `different_algorithm_same_runtime`: 1
  - `algorithmic_certificate_exact_svd_same_runtime`: 2
  - `algorithmic_error_certificate_same_runtime`: 1
  - `none`: 3

Next step:

- add a future cross-BLAS or cross-runtime witness trace
- keep same-runtime formal certificates separate from independent witnesses

Validation:

```bash
python3 benchmarks/validate_witness_independence.py
```

Done when:

- audit criteria uses the taxonomy
- RO-Crate/PROV exports preserve the level
- tests reject missing/ambiguous independence for accepted traces

### D4. Execution Context / Hardware Topology Axis

Status: partially explored, not productized.

What exists:

- runtime context is captured
- Apple Silicon thermal benchmark script exists
- external validation records workflow shape

Debt:

- no stable hardware/topology evidence schema
- no thermal state in default RunTrace
- no routing decision based on thermal state
- no distributed provenance/topology support

Next step:

- define `execution_context_level`
- decide minimal fields:
  - CPU/GPU/Metal/AMX/BLAS
  - thermal state
  - memory pressure
  - backend selected
  - backend rejected

Done when:

- one trace records meaningful hardware context beyond library versions
- one benchmark shows whether thermal state changes backend choice

### D5. Optimization Bridge

Status: seed case complete.

What exists:

- `docs/OPTIMIZATION_BRIDGE.md`
- `trace_019`
- `trace_020`
- `coverage_case=combinatorial_optimization_function_level`
- `coverage_case=combinatorial_optimization_degenerate_function_level`
- `physical_evidence_level=analytic`
- `verification_independence=different_method_same_runtime`
- `bound_scope=exact_small_instance_brute_force_verified`
- solver energy: `13.4`
- brute-force energy: `13.4`
- abs error: `0.0`
- unique-case degeneracy count: `1`
- degenerate-case solver energy: `10.999999999999998`
- degenerate-case brute-force energy: `10.999999999999998`
- degenerate-case abs error: `0.0`
- degenerate-case degeneracy count: `2`

Scope:

- N=8, K=2 assignment only
- brute force over 256 assignments gives exact truth
- no performance/speedup claim

Next step:

- add a larger non-analytic instance marked `none` or `cross_sim`, not `analytic`

### D6. Experimental Evidence Axis

Status: seed case complete.

What exists:

- `docs/EXPERIMENTAL_EVIDENCE_AXIS.md`
- `trace_021`
- `trace_022`
- `trace_023`
- `trace_024`
- `trace_025`
- `trace_026`
- `coverage_case=quantum_chemistry_experimental_reference`
- `coverage_case=quantum_chemistry_experimental_reference_improved_basis`
- `coverage_case=quantum_chemistry_experimental_reference_larger_basis`
- `coverage_case=quantum_chemistry_reference_definition_corrected`
- `coverage_case=quantum_chemistry_polyatomic_electronic_vibrational`
- `coverage_case=quantum_chemistry_larger_polyatomic_electronic_vibrational`
- `physical_evidence_level=experimental`
- `verification_independence=same_runtime_exact_fci_with_external_experimental_reference`
- `bound_scope=single_molecule_minimal_basis_equilibrium_geometry`
- `solver_error_hartree=0.0`
- `model_error_hartree=0.040080307195131615`
- `within_chemical_accuracy=False`
- cc-pVDZ model error: `0.0008309583469343074`
- cc-pVDZ within chemical accuracy: `True`
- cc-pVTZ model error: `0.008689903240272911`
- cc-pVTZ within chemical accuracy: `False`
- cc-pVTZ raw D0/reference-definition error: `0.008689903240252483`
- cc-pVTZ same-model harmonic ZPE correction: `0.010222574189245201`
- cc-pVTZ corrected De-like reference error: `0.0015326709489927315`
- cc-pVTZ after reference-definition correction within chemical accuracy: `True`
- H2O electronic atomization error before ZPE correction: `0.07621529052225856`
- H2O same-model harmonic ZPE: `0.025787667114932907`
- H2O corrected atomization error after ZPE correction: `0.10200295763719147`
- H2O within chemical accuracy: `False`
- CH4 raw electronic atomization error before ZPE correction: `0.08827763166242508`
- CH4 same-model harmonic ZPE: `0.05361901333601985`
- CH4 corrected atomization error after ZPE correction: `0.034658618326405266`
- CH4 within chemical accuracy: `False`

Scope:

- H2, H2O, and CH4 only
- STO-3G, cc-pVDZ, and cc-pVTZ finite bases
- R(H-H) = 0.7414 Angstrom
- PySCF FCI exact model solve
- measured D0 reference from Holsch et al. 2019
- same-model harmonic ZPE corrections, not full anharmonic spectroscopy
- H2O and CH4 experimental atomization references assembled from tabulated
  dissociation values, weaker provenance than the precision H2 D0 trace

Next step:

- keep solver error, basis/model error, and reference-definition error separate
- add a higher-quality polyatomic model or an external benchmark reference if
  this axis needs publication-grade chemistry

### D7. Workflow Run RO-Crate Alignment

Status: shape-compatible, externally RO-Crate-valid with warning.

What exists:

- root `Dataset`
- `ComputationalWorkflow`
- `CreateAction`
- input/output formal parameters
- PROV export
- CAPAS physical evidence entity

Debt:

- no external Workflow Run RO-Crate profile-specific validator run
- CAPAS profile URI is provisional
- CAPAS profile is not registered

Next step:

- locate or ask the Workflow Run RO-Crate community for the preferred profile
  validation path
- decide whether to submit/register a CAPAS physical evidence profile

Done when:

- validation status can distinguish:
  - RO-Crate valid
  - Workflow Run RO-Crate profile valid
  - CAPAS profile registered

### D6. QMB100 / Quantum Many-Body Applicability

Status: blocked on dataset/access.

What exists:

- paper-level audit
- integration plan
- CAPAS traces on local quantum/many-body-adjacent examples

Debt:

- no QMB100 task wrapped
- no real QMB100 output emitted as CAPAS RO-Crate
- no author/community feedback

Next step:

- contact QMB100 authors for dataset/tasks
- meanwhile wrap local DMRG/Heisenberg tasks with CAPAS evidence levels

Done when:

- one external QMB100-style task emits a CAPAS trace
- comparison shows what QMB100 emits vs what CAPAS adds

### D7. Public Usefulness

Status: unvalidated.

Debt:

- no external user has confirmed usefulness
- no community review from RO-Crate, Workflow Run RO-Crate, QMB100, SciML, or
  quantum many-body practitioners

Next step:

- prepare one minimal trace bundle:
  - analytic trace
  - formal-bound trace
  - estimated-bound trace
  - failed trace
  - rejected trace
- ask one relevant practitioner whether `PhysicalEvidence` and witness
  independence would help their audit process

Done when:

- feedback changes the schema or confirms the profile solves a real problem

## Roadmap

### Phase 0: Freeze Current Floor

Goal: preserve what already works.

Tasks:

- keep `coverage_ready=True`
- keep local and external RO-Crate validation passing
- keep `fine_tune_ready=False` until blind review
- keep all seven coverage cases

Exit criteria:

```bash
/Users/kreniq/.pixi/bin/pixi run python scripts/build_evidence_corpus.py
python3 benchmarks/validate_ro_crates.py
python3 benchmarks/validate_ro_crates_external.py
python3 audits/summarize_gold_trace_audit.py
```

### Phase 1: Complete Evidence Axis 1 - Correctness

Goal: make the correctness axis explicit and non-degradable.

Tasks:

- document `analytic`, `formal_bound`, `cross_sim`, `estimated_bound`, `none`
- add tests that forbid `estimated_bound` being accepted as formal
- extend `formal_bound` only when a theorem/scope is explicit

Exit criteria:

- `trace_016` remains formal and narrow
- quimb trace remains estimated
- docs reflect both

### Phase 2: Build Evidence Axis 2 - Witness Independence

Goal: stop treating all witnesses as equal.

Tasks:

- write independence taxonomy
- encode levels in audit criteria
- add at least two new traces with different independence levels

Exit criteria:

- audit can fail a trace with ambiguous witness independence

### Phase 3: Build Evidence Axis 3 - Execution Context

Goal: distinguish evidence produced under different hardware/runtime contexts.

Tasks:

- stabilize runtime/hardware schema
- run Apple Silicon thermal crossover benchmark
- decide whether thermal state affects routing

Exit criteria:

- one trace carries hardware context as first-class evidence metadata
- if thermal routing has no crossover, document it and do not claim it

### Phase 4: Interop And Community

Goal: make CAPAS a profile candidate, not a private dialect.

Tasks:

- validate against the strongest available Workflow Run RO-Crate path
- prepare profile description
- ask RO-Crate/Workflow Run RO-Crate community where CAPAS should fit
- ask QMB100/SciML-adjacent users whether `PhysicalEvidence` is useful

Exit criteria:

- one external compatibility issue or review thread exists
- dashboard records outcome

## Command Dashboard

Build corpus:

```bash
cd "/Users/kreniq/Desktop/KRENIQ/AI Projects/01. Investigacion/physics_quantum/physics-magnitude-lab"
/Users/kreniq/.pixi/bin/pixi run python "/Users/kreniq/Desktop/KRENIQ/AI Projects/01. Investigacion/CAPAS INTELIGENTES/scripts/build_evidence_corpus.py"
```

Local validation:

```bash
python3 benchmarks/validate_ro_crates.py
```

External RO-Crate validation:

```bash
python3 -m pip install -r requirements-validation.txt
python3 benchmarks/validate_ro_crates_external.py
```

Audit summary:

```bash
python3 audits/summarize_gold_trace_audit.py
```

Git state:

```bash
git status --short
git log --oneline --decorate -5
```

## Dashboard Update Rule

Update this file whenever any of these changes:

- evidence level taxonomy
- coverage cases
- external validation result
- fine-tune readiness
- SotA positioning
- public usefulness status
- profile registration status
- claims CAPAS is allowed or forbidden to make
