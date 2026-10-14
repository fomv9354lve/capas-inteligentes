# Coding guide — which evidence field to declare, and what happens if you don't (2026-10-13)

CAPAS never reads prose. Every rule below fires on a **declared field**; when the field is missing, the
engine does not guess — it refuses to ACCEPT (REWRITE or HOLD) and says which field to declare. A false
declaration is the coder's responsibility (declared GIGO), not a gate hole. All fields are optional unless
the claim type lists them as required.

## The envelope (every payload)

```json
{"schema_version": "capas-claim-payload-v3",
 "claim": {"id": "<stable id>", "type": "<claim type>", "text": "<the sentence as the document states it>"},
 "evidence": {"<fields of the claim type>": "...", "invariants": {"calibration_snapshot": {...}, "rmt_G": {...}}}}
```
Batches: one JSON object per line, `{"claim_id", "contaminado", "payload"}`. Cross-domain laws (RMT identities,
calibration snapshots, GRIM, sums…) go under `evidence.invariants`.

## Pre-registration vs. result: two moments, two claims (Atlas pilot, 2026-10-13)

A **pre-registration** has no measured fields yet. Code it as `claim_transition` (`current_claim` = the strong
statement, `upgrade_evidence_present: false`) → REWRITE "not licensed yet". The **measurable claim** is coded
after the run by someone who reads only the results file (blind to the verdict, not to the data): then the
type is `exact_model_solution` / `statistical_confidence` / … with its measured fields. Coding a
pre-registration as a measured type yields HOLD "missing required evidence fields" — correct, and vacuous.

## claim_transition (current_claim, upgrade_evidence_present required)

| situation | declare | if you don't |
|---|---|---|
| a stronger claim replaces a weaker one and the upgrade is backed | `upgrade_evidence_present: true` + the evidence of the stronger type in the same payload | REWRITE: the stronger claim is not licensed |
| the upgrade is pending (pre-registration) | `upgrade_evidence_present: false` | — (REWRITE is the right verdict) |

## exact_model_solution (abs_error, tolerance required)

| situation in the source | declare | if you don't |
|---|---|---|
| tolerance is in standard errors ("within 2 SE") | `tolerance_unit: "SE"` and `n_replicates` (≥ 8) — **the number of independent draws behind the SE** (for a Monte Carlo, N; one seed with N iid matrices counts as N) | REWRITE: an SE from fewer than 8 draws is not validated |
| a joint χ² criterion (one test over k cells, no per-cell tolerance) | `test_statistic: {kind: "chi2", value: <total χ²>, dof}` (+ `rivals` if any) and a nominal `abs_error`/`tolerance` only if the document gives them — otherwise HOLD is correct, not an error | HOLD |
| the closed form is sustained by a goodness-of-fit **and** a comparison with rival forms — **the χ² of `value` and of every rival is the fit WITH the claim's constraint imposed** (no free parameter absorbing the difference); if the document only gives free fits, give `rivals: [{chi2_dof, z_constraint}]` and `z_constraint` for the claim: a rival at \|z\| > 4 is self-refuting and does not count; the claim at \|z\| > 4 is REJECTed; a free fit without z → HOLD | `test_statistic: {kind: "chi2_dof", value, dof, rivals: [chi2/dof of each rival], alpha?}` | the fit is not judged; with it: a rival that fits better → REJECT; best of the rivals but p < alpha in absolute terms → REWRITE (best of the rivals, not an exact fit); consistent → ACCEPT; missing dof → HOLD |
| abs_error is the **maximum** pull over k cells | `error_statistic: "max"`, `n_cells: k` | judged as a single cell (2 SE on a max of 6 cells is a 24 % false-fail test); `max` without `n_cells` → HOLD |
| abs_error is an RMS or a single cell | `error_statistic: "rms"` / `"single"` | judged as single cell (no correction) |
| the text claims a window / regime / "for all" | `scope_declared: [...]`, `scope_tested: [...]` (lists of cells or regimes) | REWRITE: the gate cannot license a scope it cannot see; declared ⊄ tested → REWRITE; ACCEPT licenses the text **annotated** with the declared scope |
| the text claims convergence / saturation | `n_points` (≥ 3) and `alternative_model_rejected: true` | REWRITE |
| abs_error is at machine precision (≤ 1e-12 · max(1, \|reference_value\|)) | `negative_control_failed: true` (a false variant was seen to fail) | HOLD: a check that cannot fail verifies nothing; `false` → REWRITE |
| the tolerance is unusually wide | `tolerance_rationale` (string) and `reference_value` | tolerance > 50 % of the object → HOLD |
| the number is the model's own value | `reference_value` | enables the machine-precision scale and the "order of the object" check |

## proof_admissibility (claim_scope, steps_all_valid, load_bearing_step_identified, uniform_bound_proven required)

| situation | declare | if you don't |
|---|---|---|
| the proof was re-derived by someone else | `independent_reproduction_pass: true` | REWRITE (GOVERNANCE §6: constructor ≠ verifier) |
| declared scope is bounded (finite / local / leading-order) and no uniform bound | `text_quantifier: "bounded"` | REWRITE; with the field, ACCEPT licenses the text annotated with its scope, never raw |
| the text visibly quantifies universally | prove `uniform_bound_proven: true` or restrict the text | REWRITE (contradiction with a bounded declaration) |
| the proof has a gap you know of | `steps_all_valid: false` | — (REJECT is the right verdict) |

## statistical_confidence (p_value, alpha, effect_direction_confirmed required)

| situation | declare | if you don't |
|---|---|---|
| the paper reports the test statistic | `test_statistic: {kind, value, df...}` | p is taken as declared (not recomputed) |
| the text attributes a mechanism | `null_control_passed: true` | REWRITE: a significant p licenses the association, not its cause |

## interval_band_claim (estimate, ci_low, ci_high, ci_level, band, band_pre_registered required)

An estimate with an interval judged against a **pre-registered band** (Atlas E4b P2: θ with a bootstrap IC95 and bands
RECUPERA / PERSISTE / EMPEORA). `band = {"low": x, "high": y}` with either bound omitted for a one-sided band.

| situation | declare | if you don't |
|---|---|---|
| the whole interval lies inside the band | `band_pre_registered: true` | — ACCEPT |
| the whole interval lies outside the band | — | REJECT |
| the interval straddles a band edge | — | REWRITE: the interval is licensed, the band is not |
| the band was chosen after seeing the estimate | `band_pre_registered: false` | REWRITE (only the interval is licensed); missing → HOLD |
| the band has no numeric bound, or `ci_low ≤ estimate ≤ ci_high` fails, or `ci_level` ∉ (0,1) | fix the declaration | HOLD |

Optional: `method` ("bootstrap"), `resamples`, `seed`, `n_replicates`.

## reproducibility_check (artifact_available, independent_reproduction_pass required)

| situation | declare | if you don't |
|---|---|---|
| the text states a count / scope ("all 12 cases") | `scope_count_verified: true` | REWRITE |
| a citation carries the claim | `load_bearing_citation_read: true`, `citation_hypotheses_checked: true` | HOLD |

## RMT identities (evidence.invariants.rmt_closed_form / rmt_F / rmt_G)

- Declare every input the identity needs (`x`, `d` for C/A; `a`, `b`, `gamma` for F/G). A declared value with
  an incomplete input is **HOLD**, never a silent pass.
- Declare values to their working precision (a literal coarser than the identity's magnitude → HOLD).
- `rmt_G` with `gamma > 1` is judged by G-CLOSED (state `reduced`, **gaussian design and response only**):
  declare `design_response: "gaussian"`; a non-gaussian response adds κ₄·J_y and is not judged.
- Measured quantities carry `*_se`; without it → HOLD.

## calibration_snapshot (quantum hardware, Atlas)

Pass the **whole-device** snapshot with `layout` inside (medians are device medians), `measured` and
`job_date`. Two shapes are read: canonical `{qubits{id:{t1_us,t2_us,readout}}, edges{id:error}, layout{qubits,edges}}`
and the raw IBM device file copied verbatim `{t1_us{}, readout{}, t2_us{}, cz{} (or ecr{}), edges[[a,b]], layout[q…]}`
(a qubit-list layout selects the edges with both ends in it). A declared snapshot in any other shape is **HOLD**
(the law never answers "not applicable" to a declared field — Atlas E4, 2026-10-13).

**Per-field freshness (rule v2, 2026-10-13).** A fresh file can carry stale parameters (E4: T1/readout/sx identical between
02:16 and 11:51, only CZ re-measured). Declare `field_dates` = `{t1_us: {q: iso}, readout: {...}, sx: {...}, cz: {"a_b": iso}}`
(IBM `BackendProperties` dates; Atlas's fetcher keeps them) — the primary source: each layout element's date is judged
with the same `max_age_days` policy and a stale one is a **HOLD** `stale_field` (the context is unverified; it never REJECTs — decision with Atlas, 2026-10-13). Without it, declare `previous_snapshot`
(same shape, earlier `measured`) and the law **infers** staleness by identity: element by element for continuous fields
(t1_us, t2_us, edges), whole field for quantized ones (readout, sx — two real measurements can coincide exactly); the
inferred age is a **lower bound** ("measured at the latest at measured_prev"). With neither, the result carries
`field_freshness.status = "not evaluable"` — a notice, never silence, never HOLD. `field_dates` take precedence. Timestamps without a zone are read in **UTC** unless the snapshot declares `timezone` ("UTC", "±HH:MM" or an IANA name); calendar days are counted in that zone, never in the machine's. Defaults: edge > 1e-2 or > 5× median → FLAG; T1 < 60 µs or < median/3 → FLAG; freshness ≤ 1
calendar day; T2 floor off (`t2_min_frac_median` / `t2_min_us` to enable). Override anything in `thresholds`.

## The rule behind all of this

If a judgement would require reading the text, the engine asks for a field instead. Declare it and the
sentence that gets licensed carries its own limit; leave it out and the sentence is not licensed as written.

## Machine ingestion (2026-10-14): fields come from artifacts, not from hands

`capas_ingest.py` turns machine-produced artifacts into evidence, deterministically, with the source sha256 recorded:

| adapter | input | output |
|---|---|---|
| `backend_properties` | Qiskit `BackendProperties` (object, `.to_dict()`, or its JSON) | `calibration_snapshot` in the shape the law reads: `t1_us/t2_us/readout/sx/cz` tables, `edges`, `field_dates` per parameter, declared `timezone` (from the dates' offset), `source.input_sha256`. A qubit without T1 stays absent. |
| `prereg` | `atlas_prereg/v1` file | one claim skeleton per `metric_definitions` entry: `claim.id = atlas:<prereg id>:<metric>`, verbatim definition as text, `type: null`, empty evidence, prereg id/time/sha/supersedes. Refuses a prereg that carries results. |
| `verify_sources` | a claims `.jsonl` | re-hashes every `meta.sources[{path, sha256}]`; a mismatch or a missing file is reported. |

What a coder still declares, and nothing else: the **mapping** (which prereg metric feeds which claim type, and which
fields of the results file fill it). See `research/atlas_corpus/phase2c/build_claims_e4b_ingest.py`. Provenance travels
in the **row** (`meta.sources`), not inside the payload: schema v3 allows no `meta` in the payload.

Measured on Atlas E4b (post hoc, outcome known, engine HEAD): adapter-coded == hand-coded on P1 (HOLD) and P3
(ACCEPT); P2 goes from HOLD (hand-coded before `interval_band_claim` existed) to ACCEPT (the whole CI95 [1.259, 1.550]
inside the pre-registered one-sided band [0.5, +inf)), which matches Atlas's sealed outcome RECUPERA. The next clean
claim will be coded through the adapters first, sealed, then opened.

```bash
python3 capas_ingest.py backend-properties props.json --layout 67,57,65 --job-date 2026-10-13 -o snap.json
python3 capas_ingest.py prereg mirror_e4_drift_v5.json -o skeletons.jsonl
python3 capas_ingest.py verify-sources claims.jsonl --root <dir of the sources>
```

