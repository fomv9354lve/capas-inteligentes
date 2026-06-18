# CAPAS Project Dashboard

Last updated: 2026-06-17

This dashboard is the non-degradable control surface for CAPAS. If future work
changes a claim, a coverage case, or a validation status, update this file in the
same commit.

## Current Position

CAPAS is a RO-Crate/PROV evidence profile for scientific computation traces.

Conceptual reframing now under test:

> CAPAS is an evidence type system for scientific computation.

This means CAPAS should not only package traces; it should reject claims that
exceed the evidence type attached to a result.

It does not claim to invent:

- scientific workflow provenance
- structured scientific traces
- golden traces
- RO-Crate/PROV packaging
- verification against reference
- VVUQ
- automatic backend routing
- metamorphic testing / oracle-free property-based testing

Defensible claim:

> CAPAS packages graduated physical evidence into sealed RO-Crate/PROV workflow
> run traces, explicitly recording evidence strength, witness independence,
> route/result provenance, and honest failure/rejection/no-evidence states.

Extended defensible claim under active validation:

> CAPAS represents scientific results as evidence-typed objects and can reject
> selected overclaims that are not licensed by the attached evidence.

## Latest Auditable State

Repository head:

```text
See git log. This dashboard is updated in the same commit as state changes.
```

Recent commits:

```text
Latest: Add box 3 boil-the-ocean SotA audit (see git log for hash)
b60ef3d Add evidence type system claim checker
50de930 Add D11 scripted-agent scaling adversarial trace
b08757b Add D11 randomized scaling variants and anchor modes
5d6b4c2 Add D11 simulation-generated scaling anchor
```

Current validation status:

```text
coverage_ready: True
fine_tune_ready: False
local RO-Crate validation: passed
local CAPAS physical-evidence profile validation: passed for 38/38 crates
local Workflow Run Crate shape check: passed through CAPAS profile validator
external ResearchObject RO-Crate validation: valid for 38/38 crates
external warning: none
witness independence validation: passed
evidence claim type validation: passed
box 3 SotA status: broad claim-safety/provenance space is taken; narrow
  evidence-type checking for scientific computation claims survives
reproducibility environment check: passed in local physics-magnitude-lab pixi env
```

CAPAS emits a recognized `.cwl` Workflow Run RO-Crate descriptor while recording
Python as the implementation language for the costurero workflow. This avoids
validator warnings without claiming that the implementation is a native CWL
engine.

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
| `quantum_chemistry_basis_convergence_to_experiment` | 1 | covered | H2 basis ladder converges to experiment with robust threshold crossing |
| `universal_invariant_adversarial_failure` | 1 | covered | wrong-sign generator output passes local properties but fails analytic universal invariant |
| `universal_invariant_local_catches_anchor_not_needed` | 1 | covered | local oracle catches before universal anchor is needed |
| `universal_invariant_both_oracles_catch` | 1 | covered | local oracle and universal anchor both catch |
| `universal_invariant_non_heisenberg_adversarial_failure` | 1 | covered | valid product state fails Bell entropy invariant |
| `universal_invariant_no_anchor_control` | 1 | covered | locally valid arbitrary state with no claimed universal anchor |
| `universal_invariant_scaling_law_adversarial_failure` | 1 | covered | plausible decreasing Ising gaps violate universal exponent |
| `universal_invariant_scaling_law_positive_control` | 1 | covered | noisy Ising gaps satisfy universal exponent tolerance |
| `universal_invariant_scaling_law_local_catches` | 1 | covered | constant gaps rejected locally before scaling anchor is credited |
| `universal_invariant_scaling_law_simulation_generated` | 1 | covered | exact diagonalization TFIM gaps satisfy universal exponent tolerance |
| `universal_invariant_scaling_law_randomized_adversarial` | 1 | covered | randomized plausible decreasing Ising gaps all violate universal exponent beyond preregistered tolerance |
| `universal_invariant_scaling_law_agent_generated_adversarial` | 1 | covered | scripted-agent Ising gaps pass local checks but violate universal exponent |
| `formal_bound_success` | 1 | covered | formal single-cut Schmidt truncation certificate |
| `formal_bound_composition_success` | 1 | covered | formal multi-step state truncation bound |
| `estimated_bound_candidate` | 1 | covered | useful estimator, not formal |
| `no_evidence_success` | 1 | covered | successful result with no witness |
| `backend_failed` | 1 | covered | backend failure sealed honestly |
| `rejected_by_router` | 1 | covered | non-execution/rejection sealed honestly |

Current evidence levels:

```text
analytic: 16
cross_sim: 2
experimental: 7
formal_bound: 2
estimated_bound: 1
none: 3
no_universal_anchor_control: 1
scaling_law_anchor: 6
```

## What Works

1. Sealed RunTrace generation.
2. PROV-shaped export.
3. RO-Crate export.
4. Workflow Run RO-Crate-compatible shape.
5. External RO-Crate validation through ResearchObject `rocrateValidator`.
6. CAPAS `PhysicalEvidence` entity in RO-Crate and PROV exports.
7. Local CAPAS physical-evidence profile validation over all 38 crates.
8. Honest distinction between:
   - analytic truth
   - cross-sim witness
   - formal bounded evidence
   - estimated bounded evidence
   - no evidence
   - failed execution
   - rejected execution
   - claims licensed by evidence
   - claims rejected by evidence type
9. Formal-bound seed case:
   - single-cut Schmidt truncation
   - discarded weight equals squared state error
   - not claimed as global DMRG certificate
10. Multi-step formal-bound composition seed case:
   - sequential non-renormalized Schmidt truncations
   - triangle-composed state-error bound
   - not claimed as DMRG/observable certificate
11. Optimization bridge seed case:
   - N=8, K=2 assignment problem
   - explicit Ising mapping with affinity, balance, and conflict terms
   - exact diagonalization checked against brute force over 256 assignments
   - not claimed as optimization speedup
12. Degenerate optimization bridge seed case:
   - N=8, K=2 assignment problem with symmetric neutral tasks
   - exact optimum set contains 2 assignments
   - trace records that the final choice among equivalent optima needs an external criterion
13. Experimental chemistry evidence seed case:
   - H2/STO-3G at R=0.7414 Angstrom
   - PySCF FCI total energy: `-1.137270174660904` Hartree
   - model binding energy: `0.20410647554635353` Hartree
   - measured D0 reference: `0.1640261683512219` Hartree
   - solver error: `0.0`
   - model error: `0.040080307195131615`
   - within chemical accuracy: `False`
14. Improved-basis chemistry evidence seed case:
   - H2/cc-pVDZ at R=0.7414 Angstrom
   - PySCF FCI total energy: `-1.1634139335373228` Hartree
   - model binding energy: `0.16485712669815622` Hartree
   - measured D0 reference: `0.1640261683512219` Hartree
   - solver error: `0.0`
   - model error: `0.0008309583469343074`
   - within chemical accuracy: `True`
15. Larger-basis chemistry stress case:
   - H2/cc-pVTZ at R=0.7414 Angstrom
   - basis orbitals: `28`
   - model binding energy: `0.17271607159149482` Hartree
   - measured D0 reference: `0.1640261683512219` Hartree
   - solver error: `0.0`
   - model error: `0.008689903240272911`
   - within chemical accuracy: `False`
   - lesson: larger basis alone is not a monotonic guarantee against the chosen measured reference
16. Reference-definition corrected chemistry case:
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
17. Polyatomic electronic/vibrational chemistry case:
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
18. Larger polyatomic electronic/vibrational chemistry case:
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
19. H2 basis convergence to experiment:
   - basis ladder: `STO-3G -> cc-pVDZ -> cc-pVTZ -> cc-pVQZ -> cc-pV5Z`
   - corrected errors: `[0.028646971371818652, 0.009825356013931502, 0.0015326709489749402, 0.0003112863147403111, 0.00002049610541435265]`
   - monotonic non-increasing error: `True`
   - first within chemical accuracy: `cc-pVTZ`
   - first robust chemical accuracy: `cc-pVQZ`
   - best basis: `cc-pV5Z`
   - local ceiling solved: `cc-pV5Z`, `110` orbitals
   - lesson: CAPAS can certify a robust True, not only honest False cases
20. Closest-SotA / PCM audit:
   - targeted search did not identify a single dominant `PCM` project occupying
     the full CAPAS position
   - closest neighbors are Workflow Run RO-Crate, HyProv, FAIR Data Pipeline,
     SciAgentGym/SciAgentBench, QMB100/PhysVEC, and SciMLBenchmarks
   - lesson: CAPAS must not claim provenance, workflow tracing, golden traces,
     or reference-error benchmarking as new; its defensible position is a
     physical-evidence profile over existing trace/provenance systems
21. Xing et al. 2606.11620 audit:
   - artifact: `docs/XING_2606_11620_AUDIT.md`
   - source: https://arxiv.org/abs/2606.11620
   - finding: family-aware quantum circuit simulation threshold/runtime
     prediction is occupied SotA
   - lesson: CAPAS must not compete as a cost predictor; it can wrap such
     predictors as an evidence/profile layer
22. Universal invariant anchoring matrix:
   - artifacts: `trace_028` through `trace_038`
   - doc: `docs/UNIVERSAL_INVARIANT_ANCHORING.md`
   - `trace_028`: local misses, Heisenberg energy anchor catches
   - `trace_029`: local catches, anchor not needed
   - `trace_030`: local catches, anchor catches too
   - `trace_031`: local misses, Bell entropy anchor catches
   - `trace_032`: local passes, no universal anchor claimed
   - `trace_033`: local misses, Ising scaling-law anchor catches wrong exponent
   - `trace_034`: local misses, Ising scaling-law positive control passes tolerance
   - `trace_035`: local catches constant gaps before scaling anchor is credited
   - `trace_036`: simulation-generated TFIM gaps pass scaling-law anchor
   - `trace_037`: randomized decreasing Ising gap variants all fail scaling-law
     anchor beyond the preregistered tolerance
   - `trace_038`: scripted-agent generated Ising gap sequence passes local
     monotonicity checks but fails the scaling-law anchor
   - audit decision: all eleven are `reject`, because adversarial/control traces
     must not become fine-tune gold
   - lesson: the current evidence supports complementarity, not domination;
     universal anchors add coverage in some cells and are redundant or
     inapplicable in others

## Non-Degradation Rules

These are hard guardrails.

1. Do not rename `estimated_bound` to `formal_bound`.
2. Do not call quimb `CircuitMPS.fidelity_estimate()` a formal certificate.
3. Do not claim CAPAS invented provenance, RO-Crate, PROV, golden traces, VVUQ,
   or workflow tracing.
4. Do not claim CAPAS invented family-aware simulation cost prediction,
   OpenQASM-to-runtime prediction, or tensor-network threshold selection.
5. Do not mark `fine_tune_ready=True` without blind inference review.
6. Do not remove failed/rejected/no-evidence coverage cases.
7. Do not treat same-runtime certificates as independent witnesses.
8. Do not claim DMRG global error bounds until the assumptions and accumulation
   rule are explicit and tested.
9. Do not claim official CAPAS profile registration until a profile URI is
   actually registered externally.
10. Do not reintroduce unrecognized workflow descriptor extensions in generated
   RO-Crates.
11. Any new evidence level must include:
    - scope
    - witness independence
    - failure mode
    - validation command
12. Do not compare electronic `D_e`-like quantities against experimental `D0`
    without recording `reference_definition_match` and any correction.
13. Do not treat same-model harmonic ZPE as anharmonic spectroscopy.
14. Do not claim universal invariant anchoring is generally useful from the
    current eight-trace matrix.
15. Any universal-invariant claim must record:
    - local oracle and result
    - universal anchor and result
    - pre-registered success criterion
    - structure mapping
    - claim scope
    - audit decision separating failed generated output from training gold
16. Do not present D11 as a new testing paradigm. It must be positioned against
    Metamorphic Testing and scientific-software MT.

## Debt Register

### D0. Reproducibility / Portability

Status: local reproducibility gated, portability incomplete.

What exists:

- `requirements-corpus.txt`
- `scripts/check_reproducibility_env.py`
- `docs/REPRODUCIBILITY.md`
- corpus builder runs the environment check before generating traces

Current state:

```text
local CAPAS corpus: reproducible in the physics-magnitude-lab pixi environment
standalone CAPAS portability: not complete
```

Debt:

- `physics_magnitude_lab` is a local dependency, not owned by CAPAS
- `physics-magnitude-lab/pixi.toml` and `pixi.lock` are modified by the PySCF addition
- no CAPAS-owned `pixi.toml` yet

Done when:

- a fresh clone can regenerate the 38 traces with one documented command
- `physics_magnitude_lab` is installed from a pinned local path, package version,
  or declared workspace dependency

Validation:

```bash
python3 scripts/check_reproducibility_env.py
python3 scripts/build_evidence_corpus.py
```

### D1. Fine-Tune Readiness

Status: in progress.

Current state:

```text
fine_tune_ready: False
hold: 24
reject: 12
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
  - `analytic_no_solver`: 14
  - `different_library_same_runtime`: 1
  - `different_method_same_runtime`: 2
  - `same_runtime_exact_fci_with_external_experimental_reference`: 7
  - `different_algorithm_same_runtime`: 1
  - `algorithmic_certificate_exact_svd_same_runtime`: 2
  - `algorithmic_error_certificate_same_runtime`: 1
  - `none`: 4
  - `theory_scaling_law_no_solver`: 3

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
- `trace_027`
- `coverage_case=quantum_chemistry_experimental_reference`
- `coverage_case=quantum_chemistry_experimental_reference_improved_basis`
- `coverage_case=quantum_chemistry_experimental_reference_larger_basis`
- `coverage_case=quantum_chemistry_reference_definition_corrected`
- `coverage_case=quantum_chemistry_polyatomic_electronic_vibrational`
- `coverage_case=quantum_chemistry_larger_polyatomic_electronic_vibrational`
- `coverage_case=quantum_chemistry_basis_convergence_to_experiment`
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
- H2 convergence first within chemical accuracy: `cc-pVTZ`
- H2 convergence first robust basis: `cc-pVQZ`
- H2 convergence best/local ceiling basis: `cc-pV5Z`
- H2 convergence best error: `0.00002049610541435265`

Scope:

- H2, H2O, and CH4 only
- STO-3G, cc-pVDZ, and cc-pVTZ finite bases
- H2 convergence through cc-pV5Z exact FCI
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

Status: locally shape-validated, externally RO-Crate-valid without warnings,
not externally profile-registered.

What exists:

- root `Dataset`
- `ComputationalWorkflow` with a recognized `.cwl` descriptor
- `CreateAction`
- `mainEntity` from root dataset to workflow
- `mentions` from root dataset to run action
- `instrument` from run action to workflow
- input/output formal parameters
- `exampleOfWork` links for workload/result parameters
- PROV export
- CAPAS physical evidence entity
- official WRROC profile URIs:
  - `https://w3id.org/ro/wfrun/process/0.5`
  - `https://w3id.org/ro/wfrun/workflow/0.5`
  - `https://w3id.org/workflowhub/workflow-ro-crate/1.0`
- local CAPAS draft profile:
  - `docs/profile/CAPAS_PHYSICAL_EVIDENCE_PROFILE.md`
  - `docs/profile/capas-physical-evidence-context.jsonld`
- minimal review crate pointer:
  - `docs/profile/MINIMAL_REVIEW_CRATE.md`

Debt:

- CAPAS profile URI is provisional
- CAPAS profile is not registered
- no external Workflow Run RO-Crate community review yet

Next step:

- ask the Workflow Run RO-Crate community which SPARQL/profile checks they
  prefer for CAPAS as an extension
- decide whether to submit/register the CAPAS physical evidence profile

Done when:

- current local status can distinguish:
  - RO-Crate valid: yes, externally `valid`
  - Workflow Run Crate shape-compatible: yes, local CAPAS profile validator
  - CAPAS physical-evidence-profile valid: yes, local CAPAS profile validator
  - CAPAS profile registered: no

### D8. PCM / Closest-SotA Audit

Status: paper-level audit complete; interop/profile packaging implemented
locally; code/API-level audit of every neighbor not complete.

What exists:

- `docs/PCM_SOTA_AUDIT.md`
- `docs/profile/CAPAS_PHYSICAL_EVIDENCE_PROFILE.md`
- `benchmarks/validate_capas_profile.py`
- targeted search across provenance/correctness/RO-Crate/physical-evidence
  neighbors
- capability matrix covering Workflow Run RO-Crate, HyProv, FAIR Data Pipeline,
  SciAgentGym/SciAgentBench, QMB100/PhysVEC, SciMLBenchmarks, and CAPAS

Current result:

```text
No single dominant PCM-style system was found occupying the full CAPAS position.
Closest neighbors cover provenance, workflow traces, or reference correctness,
but not the complete CAPAS combination as currently documented.
```

CAPAS position after audit:

```text
physical-evidence profile over RO-Crate/PROV-style scientific traces,
with explicit reference truth, witness independence, evidence status,
and robust/marginal correctness semantics
```

Debt:

- this is not an exhaustive proof of absence
- no code-level audit of every neighbor's repository/API
- no external community confirmation
- no registered external profile URI

Next step:

- prepare external review issue/email with:
  - minimal crate: `benchmarks/ro_crates/trace_027/`
  - profile draft: `docs/profile/CAPAS_PHYSICAL_EVIDENCE_PROFILE.md`
  - local validation command: `python3 benchmarks/validate_capas_profile.py`

Done when:

- one relevant external reviewer confirms, rejects, or changes the CAPAS profile
  shape

### D9. QMB100 / Quantum Many-Body Applicability

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

### D10. Public Usefulness

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

### D11. Universal Invariant Anchoring

Status: seed falsation matrix plus synthetic, simulation-generated,
randomized adversarial, and scripted-agent scaling-law anchors complete;
positioned against Metamorphic Testing.

What exists:

- `docs/UNIVERSAL_INVARIANT_ANCHORING.md`
- `docs/METAMORPHIC_TESTING_POSITIONING.md`
- `trace_028`: local misses, Heisenberg energy anchor catches
- `trace_029`: local catches, anchor not evaluated
- `trace_030`: local catches, Heisenberg energy anchor catches too
- `trace_031`: local misses, Bell entropy anchor catches
- `trace_032`: local passes, no universal anchor is claimed
- `trace_033`: local passes, Ising scaling-law anchor catches wrong exponent
- `trace_034`: local passes, Ising scaling-law anchor passes noisy positive control
- `trace_035`: local catches constant gaps before scaling anchor is credited
- `trace_036`: exact-diagonalization TFIM gaps pass the scaling-law anchor
- `trace_037`: eight randomized plausible decreasing Ising gap sequences fail
  the scaling-law anchor beyond the preregistered tolerance
- `trace_038`: scripted-agent generated Ising gap sequence fails the
  scaling-law anchor after passing local monotonicity checks
- coverage cases:
  - `universal_invariant_adversarial_failure`
  - `universal_invariant_local_catches_anchor_not_needed`
  - `universal_invariant_both_oracles_catch`
  - `universal_invariant_non_heisenberg_adversarial_failure`
  - `universal_invariant_no_anchor_control`
  - `universal_invariant_scaling_law_adversarial_failure`
  - `universal_invariant_scaling_law_positive_control`
  - `universal_invariant_scaling_law_local_catches`
  - `universal_invariant_scaling_law_simulation_generated`
  - `universal_invariant_scaling_law_randomized_adversarial`
  - `universal_invariant_scaling_law_agent_generated_adversarial`
- evidence levels:
  - `analytic`
  - `no_universal_anchor_control`
  - `scaling_law_anchor`
- structural anchor modes:
  - `absolute_anchor`
  - `none`
- audit decision: all eleven D11 traces are `reject`

Scope:

- minimal matrix plus synthetic, simulation-generated, randomized, and
  scripted-agent scaling-law seeds, not a benchmark suite or LLM corpus
- three invariant types: Heisenberg energy, Bell entropy, and Ising gap scaling
- one no-anchor control
- supports complementarity of local oracles and universal anchors
- does not prove general superiority over PBT/RvLLM-style local properties
- does not claim novelty over Metamorphic Testing as a testing idea
- defensible distinction is absolute theory-known physical anchors packaged as
  first-class evidence in sealed RO-Crate/PROV traces

Next step:

- optional hardening: replace the scripted-agent seed with a real LLM-agent
  failure corpus if a local or external agent source is explicitly available
- add an actual `metamorphic_relation` or `mixed` case only when a future trace
  is structurally relational rather than an absolute anchor

Next closure criteria:

- at least one scaling-law adversarial case comes from an agent-labeled
  generator output rather than the randomized adversarial generator
- controls continue to include local-only, redundant, no-anchor,
  noisy/generator-trivial, and simulation-generated cases
- every D11 trace records `anchor_mode` (`absolute_anchor`, `none`, or future
  `metamorphic_relation`/`mixed`)
- validators reject missing `claim_scope` or missing local/universal oracle
  fields for this coverage family

## Roadmap

### Phase 0: Freeze Current Floor

Goal: preserve what already works.

Tasks:

- keep `coverage_ready=True`
- keep local and external RO-Crate validation passing
- keep `fine_tune_ready=False` until blind review
- keep all current coverage cases
- keep adversarial universal-invariant failure coverage marked reject for
  fine-tune

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
cd /Users/kreniq/physics-magnitude-lab
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
