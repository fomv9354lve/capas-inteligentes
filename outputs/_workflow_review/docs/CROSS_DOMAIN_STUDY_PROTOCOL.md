# CAPAS — Cross-domain blind-adjudicated study: construction & ground-truth protocol

**Companion to `docs/PREREGISTRATION_CROSS_DOMAIN_ADJUDICATION.md`.** That pre-registration fixes the
*hypotheses, design, and success criteria* (n=500, adjudication sub-sample 100, H1/H2/H3, the two
adjudication tracks, blinding). This document fixes the *construction and ground-truth procedure*: how the
corpus is sourced and frozen, how ground-truth is fixed on each of the two tracks, and how this study's
independence relates to the IBM kingston hardware validation already in the repo. It **collects nothing,
runs nothing, and reports no result** — it is the freeze-target specification that is hashed into the
registry before claim #1.

Three sibling artifacts complete the gap:
- this protocol (corpus + two-track ground-truth + independence framing),
- `docs/CROSS_DOMAIN_STUDY_ANALYSIS_PLAN.md` (the pre-locked single-shot statistics, H1/H2/H3),
- `benchmarks/study_assembly.py` (the tamper-evident assembly + SCOPED→BACKED flip gate).

**REGLA CERO.** Every numeric stratum is re-derivable from `docs/PREREGISTRATION_CROSS_DOMAIN_ADJUDICATION.md`
§2–§8 and `outputs/pilot_metrics.json → pilot_design` (`recommended_claim_count: 500`,
`adjudication_sample: 100`, and the success metrics). The domain/gate inventory is `docs/capability_matrix.md`
(26 live gates / 10 domains). The real-claim sourcing precedent (Retraction Watch ↔ retracted;
replication/meta-analysis ↔ valid) and the evidence contracts are `benchmarks/pilot_real.py`. The schema is
`docs/schema/v3/capas_claim_payload.schema.json` (`capas-claim-payload-v3`). The IBM evidence is
`docs/capas_vs_sota_and_ibm.md` and `examples/kingston_live_audit.py`. No number here is invented; any
forward-looking quantity is tagged `[ASSUMPTION]` / `[ESTIMATE]`.

---

# PART I — Frozen corpus construction protocol (n=500, real artifacts only)

This part specifies the exact, hash-lockable procedure for assembling the n=500 real-claim corpus required
by the pre-registration §3–§6 / §8. It does not collect, code, or adjudicate any claim. It defines *how* the
corpus is built so the build is reproducible, auditable, and immune to post-hoc tuning.

## I.0 Scope and non-goals

**This part produces:** (1) a per-domain public-source sourcing table; (2) a per-claim citation + retrieval-hash
requirement; (3) the point-in-time evidence rule for Track-B payloads; (4) schema-v3 payload-construction
rules; (5) the freeze/hash manifest format; (6) the corpus-coder blinding rule.

**Out of scope (other parts/artifacts own these):** running CAPAS; the adjudication rubric and κ procedure
(Part II); the plausibility-baseline (LLM-judge) arm (analysis plan §3); the locked statistical analysis
(analysis plan); the assembled tamper-evident artifact (`benchmarks/study_assembly.py`).

## I.1 Stratification target (frozen, copied from the registered design)

Re-stated from the pre-registration §3 so the freeze manifest can hash a single self-contained target.
**If this table and the pre-registration ever disagree, the pre-registration governs and this part is void**
(recorded as a freeze deviation).

| # | Domain | n (target) | Track | CAPAS gates exercised (`capability_matrix.md`) |
|---|---|---|---|---|
| 1 | statistics / inference | 80 | B | GRIM mean reachability; statistical confidence (p-vs-α, direction, multiplicity) |
| 2 | epidemiology | 70 | A+B | 2×2 identities (Se/Sp/PPV); Bayes PPV vs base rate; RR/OR/RD; VE=1−RR; count containment |
| 3 | biology / medicine | 60 | B | Lincoln-Petersen; Hardy-Weinberg; reproducibility; causal mechanism |
| 4 | quantum | 50 | A | T2≤2T1; thermal P01≥P10; Γφ=1/T2−1/2T1; gate floor t_g/3T1; exact ZZ |
| 5 | chemistry | 45 | A | atom balance; charge balance; oxidation-state sum; n=m/M |
| 6 | physics | 45 | A | dimensional homogeneity; physical bounds (η≤1, v≤c, T≥0) |
| 7 | finance | 40 | A+B | accounting identity A=L+E; financial metric (reported-vs-reference) |
| 8 | mathematics | 40 | A | claimed root satisfies equation; Ax=b check; divisibility / gcd-lcm |
| 9 | engineering | 40 | A | Ohm V=IR, P=VI |
| 10 | universal | 30 | A | probability bounds 0≤p≤1; conservation Σparts=total |
| | **Total** | **500** | | |

Floor = 40/domain (universal = 30 is the single sanctioned exception inherited from the registered table; it is
a deterministic Track-A domain where a per-domain CI at n=30 is acceptable and the budget is reallocated to
judgment-heavy Track-B). Adjudication sub-sample = 100, drawn disproportionately from Track-B per
pre-registration §4. The disproportionate-draw rule is owned by the analysis/sampling plan; this part only
guarantees each Track-B domain supplies enough sourced claims to *support* that draw.

**Track-B claim floor (construction-side derivation, not a pre-reg requirement).** The pure-Track-B domains
(statistics 80, biology/medicine 60) plus the Track-B portion of the A+B domains (epidemiology, finance) must
collectively supply ≥ 100 claims so the n=100 adjudication sub-sample can be drawn entirely or near-entirely
from Track-B without exhausting any single domain. Pure-B floor alone = 80 + 60 = 140 ≥ 100, so this is
satisfied by construction (this floor and its 80+60=140 satisfaction are this protocol's construction-side
derivation from the frozen prereg counts, not a prereg requirement); A+B Track-B claims are additive headroom.

## I.2 Per-domain sourcing table (frozen)

For each domain: the **public source class**, **inclusion criteria**, **exclusion criteria**, **Track**, and the
**ground-truth handle**. "Public" means open or institutionally-accessible published artifacts only — no
private data, no synthetic generation, no claim authored by the corpus team. This operationalizes
pre-registration §5 ("each claim is sourced from a real published artifact … no synthetic claims") and follows
the `pilot_real.py` precedent.

### Track A — computable-truth domains (quantum, chemistry, physics, mathematics, engineering, universal, finance-identity)

For Track-A claims the "ground truth" is the **invariant itself** and is computed, not judged. The corpus team
sources *real published statements of the quantity* and, for the inadmissible arm, *published-but-known-wrong
rows or seeded violations of a published equation*. A seeded violation is permitted in Track A **only** because
the invariant is deterministic and the seeding is auditable from the cited source; it is **never** permitted in
Track B.

| Domain | Public source class | Inclusion | Exclusion | GT handle |
|---|---|---|---|---|
| quantum | Published device calibration tables / coherence reports (vendor calibration dumps, hardware papers; cf. `docs/capas_vs_sota_and_ibm.md`) | Row reports the quantities a gate consumes (T1,T2; readout P01/P10; gate error; ZZ) with units; citable by DOI/URL | Rows missing a needed quantity; aggregated rows where per-qubit values are unrecoverable | T2≤2T1 etc. computed from the cited row; inadmissible arm = published row with one quantity inverted/fabricated, the alteration logged against the source |
| chemistry | Textbook / published reactions and stoichiometry tables | Reaction or n=m/M trio stated with all species/coefficients | Ambiguous/implicit species; non-integer fabricated coefficients with no source | atom/charge/oxidation/mole identity computed; inadmissible = published reaction with a coefficient/mass altered, logged |
| physics | Published equations / reported physical quantities | Equation with declared dimensions, or a reported η/v/T/r value | Order-of-magnitude-only statements; quantities without units | dimensional homogeneity / bound computed; inadmissible = seeded dimensional break or over-unity value vs the cited equation |
| mathematics | Published worked solutions, linear systems, number-theory statements | Declared root/solution-vector/divisibility claim with its equation/system | Claims whose equation is not fully specified | substitution check computed; inadmissible = a declared root that fails its own (cited) equation |
| engineering | Published circuit examples / datasheet electrical quantities | V,I,R or P,V,I triple stated together | Triples with a missing value | V=IR / P=VI computed; inadmissible = a published triple with one value altered |
| universal | Published probability / conservation statements | A probability or part/total decomposition stated numerically | Qualitative-only statements | 0≤p≤1 / Σparts=total computed; inadmissible = seeded out-of-range/non-summing value |
| finance (identity, Track-A) | Public filings (10-K/10-Q balance sheets), audited statements | A,L,E (or reported-vs-reference metric) present from one filing | Pro-forma / non-GAAP without underlying figures | A=L+E computed from the cited filing; inadmissible = a published line with one figure altered, logged |

### Track B — judgment-truth domains (statistics, biology/medicine, epidemiology-judgment, finance-judgment)

For Track-B claims the ground truth is a **human/world judgment** and is fixed downstream by blind external
adjudicators (Part II). This part fixes only **what is sourced** and **how the payload is built so the judgment
is fair**. **No seeding, no alteration, no synthetic claim in Track B** — every Track-B claim is a real
published claim presented as published.

| Domain | Public source class | Inclusion | Exclusion | GT handle (set downstream) |
|---|---|---|---|---|
| statistics / inference | Published result tables + Retraction Watch (statistical-misconduct / p-hacking retractions) and replication records | Claim makes a specific inferential assertion (significance/direction/multiplicity) traceable to a table or notice | Claims where the statistical assertion cannot be tied to a specific reported result | adjudicator consensus (admissible / rewrite-only / inadmissible) |
| biology / medicine | Retraction Watch (retracted ↔ inadmissible anchor) vs replication / meta-analysis records (replicated ↔ admissible anchor) — the `pilot_real.py` precedent | Famous enough to have a public retraction notice OR a public replication/meta record; both arms balanced | Disputed/ambiguous retraction status; partial retractions where the specific claim is unaffected | adjudicator consensus |
| epidemiology (judgment) | Published 2×2 / VE / RR / OR studies whose *interpretive* claim (not just arithmetic) is at issue; retracted vs replicated | The contested element is a judgment (mechanism, confounding, review quality), not pure arithmetic | Claims fully resolved by the 2×2 identity alone (those are Track-A) | adjudicator consensus |
| finance (judgment) | Public filings + enforcement actions (e.g. SEC litigation releases) vs clean audited filings | The contested element is a reporting-judgment claim, not the closing identity | Pure identity violations (Track-A) | adjudicator consensus |

**Balance rule (both tracks).** Within each domain the corpus targets an *approximately balanced*
admissible/inadmissible split (target 50/50 ± 10 pp), so neither false-accept (H1) nor false-reject is
estimable only at the extremes. The realized split is recorded but **not** post-hoc rebalanced after any verdict
is seen. Where a natural source is imbalanced, the limiting arm sets the per-domain n and the surplus arm is
down-sampled by the pre-registered random seed (I.4), never hand-picked.

## I.3 Per-claim citation and retrieval-hash requirement

Every claim (both tracks) carries a **provenance record** frozen with the claim and hashed into the manifest
(I.4). A claim without a complete provenance record is excluded (recorded as a drop).

```
claim_id              # stable slug, schema-v3-legal (no angle brackets / homoglyphs)
domain                # one of the 10
track                 # "A" | "B"
arm                   # "admissible" | "inadmissible"  (source-anchored expectation, NOT a verdict)
source_citation       # DOI or stable URL of the published artifact
source_class          # the I.2 source class this came from
retrieved_at          # ISO-8601 UTC timestamp of retrieval
retrieval_sha256      # sha256 of the retrieved artifact bytes (PDF/HTML/CSV as fetched)
publication_date      # ISO-8601 date of the claim's original publication (drives I.4 evidence cutoff)
alteration_log        # Track-A inadmissible only: field altered + original value + cited source loc.
                      #   Track-B: MUST be the literal "none" (any other value voids the claim)
coder_id              # corpus coder who assembled it (blinding audit, I.6)
notes                 # free text; never used by the engine
```

- **`retrieval_sha256`** is sha256 over the exact retrieved bytes, computed with the same primitive as the
  registry (`hashlib.sha256`, mirroring `capas_registry.py:_sha`). It pins *what was read* so a third party can
  confirm the source was not swapped after coding. (`retrieval_sha256` and `random_seed`/`coercion_table`/
  `engine_digest` in I.6 are construction-side fields introduced by this protocol — coercion grounded in
  `pilot_real.py`, engine_digest in `capas_registry.py`/`capas_verify.py` — and are not in the pre-registration
  because they govern the build, not the hypotheses.)
- **`arm` is a source-anchored expectation, not a CAPAS verdict and not the ground truth.** For Track A it is the
  computable expectation; for Track B it is the *anchor* the claim was sourced under (retracted vs replicated).
  The actual Track-B ground truth is the downstream adjudicator consensus, which may differ from `arm` — and
  that difference is itself a finding, not an error to be tuned away.
- **No claim is admitted without `source_citation` + `retrieval_sha256`.** This is the "real artifacts only, no
  synthetic" guarantee made mechanical.

## I.4 Point-in-time evidence rule for Track-B payloads (no post-hoc evidence)

Operationalizes pre-registration §5 ("the evidence payload is built from what was available at the claim's
publication time — no post-hoc evidence"). This is the rule that keeps CAPAS honest — it must be tested under
the information state a real reviewer had, not with hindsight.

**Cutoff.** For every Track-B claim, the evidence-construction cutoff = the claim's `publication_date`. Any
evidence field in the schema-v3 payload (I.5) must be supportable from artifacts dated **on or before** that
cutoff.

- `independent_reproduction_pass`, `artifact_available`, replication status, meta-analytic agreement, retraction
  status: set **only** from what was knowable at publication time. A claim later retracted is **not** coded as
  `inadmissible` via its retraction notice — the retraction is post-hoc evidence and is forbidden in the
  payload. The retraction is provenance/anchor metadata (`arm`), never an evidence field.
- If at publication time the artifact was unavailable and unreproduced, the payload says so (the honest
  weak-evidence state), and CAPAS's HOLD/REJECT on weak structure is the correct behavior under test.
- **Why this matters:** without this rule, Track-B degenerates into "did it get retracted?", which CAPAS does
  not and should not read. The rule forces the test onto *structure available at the time*, which is exactly
  what CAPAS gates.

**Track A is exempt** from the cutoff (an invariant is timeless), but Track-A `alteration_log` must still cite
the source location of every altered value. A coder finding a required contemporaneous evidence field
*unrecoverable* drops the claim (recorded) rather than guessing.

## I.5 Schema-v3 payload-construction rules

Each sourced claim becomes exactly one `capas-claim-payload-v3` object validating against
`docs/schema/v3/capas_claim_payload.schema.json`. One claim → one payload → one single-gate CAPAS decision.

1. **`claim.type`** must be a schema-v3 enum value. The domain→type mapping is fixed per the `pilot_real.py`
   precedent (retracted-bio causal → `causal_mechanism_claim`; reproducibility → `reproducibility_check`; stats
   → `statistical_confidence`; reviews → `systematic_review_claim`) and frozen in the manifest; **a coder may
   not pick `claim.type` to steer the verdict** — type is determined by structure, not by desired outcome.
2. **`claim.id`** = provenance `claim_id`; **`claim.text`** = a faithful, verbatim-where-possible restatement of
   the published claim. Both satisfy the schema's no-angle-bracket / no-homoglyph pattern and length bounds. No
   editorializing in `claim.text`.
3. **`evidence`** is populated **only** from I.4-admissible sources, using **only** the registered evidence
   fields for that claim type (the schema is `additionalProperties: false`; unknown/misplaced fields yield HOLD
   by design — acceptable and recorded, never patched around).
4. **Uniform, pre-declared coercion only.** Any normalization of evidence values is transparent and identical
   across all claims — the `pilot_real.py` discipline ("no per-case tuning"): e.g. a reported significant result
   → `{p_value: 0.001, alpha: 0.05}`, a non-significant/absent → `{p_value: 1.0, alpha: 0.05}`. The full
   coercion table is frozen in the manifest before claim #1. **No per-claim coercion decisions.**
5. **`schema_version` = `"capas-claim-payload-v3"`** on every payload.
6. **The coder never runs CAPAS and never sees a verdict** (I.6).
7. Every constructed payload is schema-validated at build time; a payload that fails validation is fixed to
   match the source faithfully or dropped (recorded) — **never** mutated to change the verdict.

## I.6 Freeze / hash manifest format (locked before claim #1)

The manifest is the tamper-evident anchor of corpus construction. It is assembled, hashed, and registered (via
`capas_registry.py`, the same append-only hash-chained log used for decisions — pre-registration §10) **before
a single claim is sourced**. Anything not in the frozen manifest cannot silently influence the corpus; any
change after the freeze is a logged, dated deviation.

```
freeze_manifest:
  manifest_version:        "capas-corpus-freeze-v1"
  frozen_at:               <ISO-8601 UTC, before claim #1>
  governs:                 "docs/PREREGISTRATION_CROSS_DOMAIN_ADJUDICATION.md"   # pre-reg governs on conflict
  schema_ref:              "docs/schema/v3/capas_claim_payload.schema.json"
  schema_sha256:           sha256(schema bytes)
  stratification_target:   <I.1 table, verbatim>           # 10 domains, n, track, floor=40, total=500
  adjudication_subsample:  100
  sourcing_table_sha256:   sha256(I.2 table bytes)
  per_claim_provenance_fields: <I.3 field list, verbatim>
  pointintime_rule_sha256: sha256(I.4 text bytes)
  payload_construction_rules_sha256: sha256(I.5 text bytes)
  domain_type_map:         <frozen domain→claim.type mapping>
  coercion_table:          <frozen uniform coercion rules, I.5.4>
  random_seed:             <integer>                       # governs any down-sampling / draws
  blinding_rule_sha256:    sha256(I.6.1 text bytes)
  engine_digest:           <CAPAS engine version digest>   # which engine the frozen corpus replays against
  manifest_sha256:         sha256(canonical(all of the above EXCEPT manifest_sha256))
```

- **Hashing primitive:** `sha256`; canonicalization mirrors `capas_registry.py:_canonical` (sorted-key,
  separatorless JSON) so the manifest digest is recomputable by anyone with the file. `manifest_sha256` is
  computed over the canonical form of every field except itself (the `_body_digest` exclusion pattern in
  `capas_registry.py`).
- **Registration (genesis-entry wrapper, [ASSUMPTION] resolved by `study_assembly.py`):** the manifest is
  wrapped in a certificate-shaped body and appended as the **genesis entry** of the study's hash-chained
  registry (`capas_registry.append`). Because `append` is decision-shaped — it reads `claim_id` / `verdict` /
  `scope` / `engine_digest` / `certificate_id` / `signature` — the manifest carries those fields as
  manifest-markers (e.g. `verdict: "FROZEN"`, `scope: "CORPUS_MANIFEST"`, `certificate_id` = the manifest
  digest, `signature: null`). It is therefore sequenced *before* any decision or adjudication entry and cannot
  be back-dated; the published artifact later includes the manifest digest and the Merkle root over the whole
  log. This genesis-wrapper assumption is the one verified by `benchmarks/study_assembly.py`
  (`assemble_corpus_record` content-addresses the manifest the same way).
- **Order matters:** the criteria + rubric-ref + construction rules are hashed **before claim #1**, satisfying
  pre-registration §5.

### I.6.1 Blinding rule (corpus coders)

- Corpus coders assemble claims and build payloads **without ever invoking CAPAS and without ever seeing any
  CAPAS verdict, reason_code, or audit_hash.** The engine is not available in the coding environment.
- `claim.type`, the evidence fields, and the `arm` are determined **only** from the cited source under the
  frozen domain→type map and coercion table — never from the engine's reaction.
- Coder identity is recorded per claim (`coder_id`) so the disjoint-roles property (pre-registration §6) is
  auditable on the construction side too.
- For Track-B, coders are additionally blind to the downstream adjudicators and vice versa (Part II owns
  adjudicator blinding; this rule only guarantees coders inject no adjudicative judgment).

## I.7 Outputs of Part I (handoff)

Three frozen artifacts that downstream parts consume but never the corpus team alters: (1) the freeze manifest
(I.6), registered as the genesis registry entry; (2) the per-domain sourcing table (I.2), hashed into the
manifest; (3) the per-claim provenance schema (I.3) every sourced claim must populate. It produces **no claims,
no payloads, no verdicts, no adjudications.**

---

# PART II — Two-track ground-truth procedure (computable A vs blind human B)

This part expands pre-registration §4 (two tracks), §6 (blinding & independence), and §12 (separate-reporting
caveat) into an operational protocol. It defines *how ground-truth is fixed*; it runs no adjudication and
contains no results. It is frozen and hashed into `capas_registry.py` before claim #1.

## II.0 The single design idea this protocol protects

CAPAS spans domains carrying **two structurally different kinds of ground-truth**, and the credibility of the
whole study rests on never conflating them. A reviewer who saw *"V=IR"* or *"T2 ≤ 2·T1"* listed as a
"human-adjudicated" claim would correctly dismiss the study — blind-adjudicating a computable identity is
theater, not evidence. Symmetrically, treating a retraction-status or causal-mechanism judgment as if it were
computable would smuggle the authors' opinion in as "truth." So:

- **Track A (computable truth)** — ground-truth *is the named invariant*; the human role is **verifying that
  ground-truth was computed correctly**, not judging CAPAS.
- **Track B (judgment truth)** — ground-truth is a **human/world judgment fixed by external adjudicators blind
  to CAPAS**; the human role *is* the ground-truth.

The two tracks use **different procedures, different personnel roles, different reliability statistics, and are
reported on separate confusion matrices that are NEVER averaged** (pre-registration §12).

## II.1 Track assignment is rule-bound, not ad hoc (frozen)

A claim's track is determined by the **gate class in `docs/capability_matrix.md`** — `consistency-invariant` and
`derived-quantity` gates → Track A; judgment gates → Track B. This is **mechanical for single-track domains**
(quantum, chemistry, physics, mathematics, engineering, universal → A; statistics, biology/medicine → B) and
**rule-bound for the A+B mixed domains** (epidemiology, finance), where the per-claim split is a discretionary
routing judgment. The mitigation is stated honestly: the split rule routes any claim with *both* an identity
defect and a judgment defect to **Track B (the harder ground-truth governs)**, so any misroute can only make a
claim *easier to ground-truth conservatively* and **cannot lower H1's bar** — a claim wrongly sent to A is
deterministically checked; a claim wrongly sent to B is blind-adjudicated and, on a tie, defaults to
inadmissible (II.3.3), which can only count an ACCEPT against CAPAS, never for it.

| Domain | Track | Track-A gates (named invariant) / Track-B judgment |
|---|---|---|
| quantum | A | T2 ≤ 2·T1; thermal P01≥P10; Γφ = 1/T2 − 1/2T1; gate floor t_g/3T1; residual ZZ (exact-published) |
| chemistry | A | atom balance; charge balance; oxidation states sum to charge; n=m/M |
| physics | A | dimensional homogeneity; physical bounds (η≤1, v≤c, T≥0, \|r\|≤1) |
| mathematics | A | claimed root satisfies equation; Ax=b solution check; integer divisibility / gcd-lcm |
| engineering | A | Ohm's law V=IR, P=VI |
| universal | A | probability bounds 0≤p≤1; conservation Σparts=total |
| epidemiology | A (identity) | 2×2 identities (Se/Sp/PPV); RR/OR/RD; VE = 1−RR; count containment; Bayes PPV vs base rate |
| biology / medicine | A (identity) | Lincoln-Petersen N=M·C/R; Hardy-Weinberg internal consistency |
| statistics / inference | B | p-vs-α / multiplicity / direction overreach (judgment) |
| epidemiology, biology, finance | B (judgment) | causal mechanism; reproducibility; evidence conflict; systematic review; retraction status |
| finance | A (identity) + B (judgment) | A = L + E (identity, A) vs reporting-judgment claims (B) |

**Mixed-domain split rule (frozen).** Per-claim, by *what fixes the verdict*: identity/arithmetic only → Track A;
judgment about evidence state → Track B; *both* defects → Track B (harder ground-truth governs), with the
identity defect recorded as a secondary annotation. Fixed before collection so it cannot be tuned per claim.

The track of every one of the 500 claims is written into the frozen corpus manifest **before** any verdict or
adjudication is computed (see the Track-assigner role, II.6), and the manifest hash is committed to the
registry.

## II.2 Track A — dual-analyst computable-verification protocol

In Track A the law *is* the ground-truth and it is computable, so "adjudication" means **independent
verification that the ground-truth label was computed correctly** — a coding-correctness control, explicitly
*not* a judgment of CAPAS and *not* averaged into Track B's human-adjudicated numbers.

**Procedure.** For each Track-A claim: (1) two analysts, independently and offline from each other, compute
whether the claim **violates the named invariant** — a label in `{violates, satisfies}` plus the worked
derivation; (2) both are **blind to the CAPAS verdict, reason_code, and audit_hash** for that claim; (3) the two
labels are compared — **agreement fixes the ground-truth label**; **disagreement is a coding error, not a
difference of opinion** (the invariant is deterministic; exactly one derivation is arithmetically wrong),
resolved by **re-derivation** (plus a third numerate checker where needed) until the discrepancy is located,
logged to the registry. **No "majority vote" / "consensus" in Track A** — a tie is a bug to be fixed, not an
opinion to be polled. (4) The fixed label, both derivations, the source citation (DOI/URL + retrieval hash), and
any resolution note are appended to the hash-chained registry.

**What Track A measures.** CAPAS verdict vs computed truth → accuracy + false-accept (a Track-A false-accept =
CAPAS ACCEPT on a claim the analysts computed to *violate* its invariant). Reliability = the **inter-analyst
coding-error rate** (fraction with an initial disagreement), reported as a data-quality figure. It is **not**
Cohen's κ — κ measures agreement under genuine judgment uncertainty, which by construction does not exist here;
reporting κ on Track A would falsely imply the truth was a judgment call. Track A is reported on its **own**
confusion matrix, labelled "computable-truth verification," and **never folded** into a single
'human-adjudicated accuracy' with Track B.

**Honesty line.** Track A shows only that CAPAS correctly applies the invariant it claims to apply — not that it
"understands physics/chemistry." The two `capability_matrix.md` excluded diagnostics (ZZ-from-ratio linear
estimate; loss tangent needing withheld frequency) are **out of scope** for Track A because their ground-truth
is not exactly computable from the open payload.

## II.3 Track B — blind external-adjudicator protocol

In Track B the ground-truth *is* a human/world judgment, fixed by **independent experts external to the CAPAS
authors, blind to CAPAS's verdict and to each other**, on a pre-registered rubric. This is the layer
`pilot_real.py` names as the missing "next step."

**II.3.1 Adjudicators.** 2–3 domain adjudicators per Track-B claim, external to the CAPAS authors, recruited
from the relevant field (meta-science / replication experts for biology-medicine and statistics; subject experts
for epidemiology and finance judgment claims). Disjoint from the CAPAS runner and the Track-A analysts (II.6).
Each adjudicator's field, affiliation-independence, and role are recorded in the registry before adjudication.

**II.3.2 What each adjudicator sees / never sees.** Sees: the claim statement as published; the evidence payload
built from publication-time information (no post-hoc evidence); the source citation (DOI/URL + retrieval hash);
the frozen rubric (II.4). Never sees (before submitting): CAPAS's verdict / reason_code / audit_hash; the other
adjudicators' rulings; the plausibility-baseline (LLM-judge) score.

**II.3.3 Ruling, consensus, fail-closed tie rule.** Each adjudicator independently rules into exactly one of
`{ admissible , rewrite-only , inadmissible }` (mirroring CAPAS's ACCEPT / REWRITE / REJECT-or-HOLD so the
confusion matrix is well-defined). **Ground-truth = majority consensus.** **Ties → `inadmissible`
(fail-closed)** — under genuine ground-truth uncertainty the safe default is *not admissible*. This makes H1
(false-accept ≤ 5%) **harder** for CAPAS, not easier (a tie counts an ACCEPT as a false-accept), the correct
direction for a load-bearing safety claim. The per-claim ruling vector and the derived consensus are appended to
the registry **before** any confusion matrix is computed.

**II.3.4 What Track B measures.** CAPAS verdict vs adjudicator-consensus confusion matrix + κ. Reliability =
**inter-adjudicator agreement** (Cohen's κ for 2, Fleiss' κ for 3) supporting **H3 (κ ≥ 0.6)**. **κ caveat
(prevalence/base-rate):** on a retraction-heavy Track-B corpus one pole (inadmissible) can dominate, deflating κ
even at high raw agreement. So we pre-register reporting **raw percent-agreement alongside κ** and an
**agreement-adjusted index (PABAK or Gwet's AC1)** so H3 cannot mechanically fail a domain for a prevalence
artifact — grounding pre-registration §8's pairing of "≥ 80% pole-agreement (κ ≥ 0.6)." If H3 fails (κ < 0.6 and
the agreement-adjusted index is also low) on a domain, that domain's ground-truth is declared **unreliable** and
its CAPAS results are reported as inconclusive rather than as evidence.

## II.4 Track-B rubric scaffold (frozen before collection)

The rubric is **frozen and hashed before claim #1** (pre-registration §5). It is deliberately about **structural
admissibility, not ultimate truth** (GIGO ceiling, §12). An adjudicator is asked *"is this claim structurally
admissible on the evidence a contemporaneous reviewer had?"*, **not** *"is this claim true?"*. The per-domain
anchors below are a scaffold to be finalized with the recruited external adjudicators before freezing; the
three-pole definitions, the blinding instruction, and the fail-closed tie rule are **fixed and not revisable**.

**Standing instructions (fixed, every claim):** (1) rule on structural admissibility given the publication-time
evidence shown, not on personal belief, not on hindsight; (2) you are fixing ground-truth — no automated verdict
is shown to you and none should be inferred; (3) rule independently; (4) if undecided between two poles, choose
the more conservative (toward `inadmissible`); do not leave a claim blank.

| Pole | Definition (structural, evidence-relative) |
|---|---|
| **admissible** | The claim's structure is sound given publication-time evidence: the asserted relationship is supported by the evidence contract its claim-type requires, with no structural overreach. |
| **rewrite-only** | The observation may stand, but the **claim as stated overreaches its evidence** (e.g. correlational stated as causal; single study stated as established; directional claim from a non-significant result). Admissible *only if rewritten*. |
| **inadmissible** | The claim is structurally unsupportable on its evidence (e.g. asserts a result later retracted for the very basis claimed; asserts an effect a non-significant/underpowered/unreproduced result cannot bear; conclusion contradicts the cited evidence). |

| Track-B domain | Structural question (admissible / rewrite-only / inadmissible) |
|---|---|
| statistical inference | Does the claim respect p-vs-α, declared α, direction, multiplicity — or overreach (significance from p>α; direction from a non-significant/two-sided result; one "hit" of many asserted as confirmatory)? |
| causal mechanism | Is "X causes Y" supported by the causal contract (intervention/natural experiment, temporal order, controlled confounders, mechanism) — or asserted from association alone? |
| reproducibility | Is reproducibility appropriately stated given artifact availability and independent reproduction status — or asserted as robust without either? |
| evidence conflict | When the cited evidence conflicts, does the claim acknowledge it, or cherry-pick one side and assert consensus? |
| systematic review | Does the review claim meet the review contract (registered protocol, declared inclusion, risk-of-bias, effect consistency) — or is it presented as systematic without them? |
| retraction status | Given the claim relies on a result retracted **for the basis it asserts**, is it admissible? (retracted-for-fraud/error on the very point → inadmissible; cited support retracted for an unrelated reason → possibly rewrite-only) |

Adjudicators record a **one-line written basis** per ruling (which structural element failed), appended to the
registry — the audit trail for H3 and the Deviations log.

## II.5 The n=100 adjudication sub-sample (drawn disproportionately from Track B)

The full corpus is n=500; the full human-adjudication sub-sample is n=100, drawn disproportionately from Track B
(where human adjudication is load-bearing). **Selection function (frozen):** "eligible" = a Track-B claim with a
complete provenance record (I.3) and ≥ 2 recruited adjudicators in its domain. The n=100 is the output of a
frozen rule, not a frozen ad hoc list: **fixed priority order over Track-B domains** (statistics →
biology/medicine → epidemiology-B → finance-B), filling each domain's eligible claims in ascending `claim_id`
order (deterministic tie-break), until the cap of 100 is reached; Track-A claims enter only if capacity remains
after Track-B coverage, serving as a computable-truth control band. Track-A claims outside the n=100 are still
**fully ground-truthed** by the dual-analyst protocol (II.2) — computably verified, the complete ground-truth
for a Track-A claim. The exact claim IDs in the n=100 and their track tags are written into the frozen manifest
**before** adjudication and committed to the registry.

## II.6 Disjoint-roles and blinding controls (non-negotiable; pre-registration §6)

Four roles are **disjoint** and recorded in the registry before the study runs. The same person may never hold
two for the same claim:

| Role | Does | Must NOT |
|---|---|---|
| **Track-assigner** | Assigns each claim's track (A/B) from the II.1 gate-class rule + mixed-domain split, **before** payloads are run through CAPAS and **blind to CAPAS verdict / reason_code / audit_hash**; commits the per-claim track tag to the frozen manifest before any verdict entry. | See any CAPAS verdict before the track tag is committed; run CAPAS; adjudicate. |
| **Runner** | Assembles each claim's payload from cited sources; submits it to the open CAPAS engine; records verdict/reason_code/audit_hash. | Adjudicate; verify Track-A ground-truth; reveal any verdict to an analyst/adjudicator. |
| **Track-A analyst** (×2, +checker) | Independently computes the invariant violation; resolves disagreements by re-derivation. | Run CAPAS; see the CAPAS verdict before fixing the label. |
| **Track-B adjudicator** (×2–3, external) | Independently rules Track-B claims on the frozen rubric, blind. | Run CAPAS; see CAPAS's verdict/reason_code/audit_hash; see other adjudicators' rulings; see the plausibility baseline. |

The Track-assigner is its own role so the II.1 split is auditable on the same hash-chain as everything else and
the "you routed the easy ones to A" attack is removed: the track tag is committed to the frozen manifest
*before* any verdict entry exists.

**Enforced controls:** (1) runner ≠ adjudicator, runner ≠ analyst, assigner ≠ runner/adjudicator. (2) **The
verdict wall:** no CAPAS verdict/reason_code/audit_hash is exposed to any assigner/analyst/adjudicator until
*after* their label/tag is appended to the registry; order is enforced by the append-only hash chain (the
ground-truth/tag entry is committed before the verdict-comparison entry). (3) Mutual blinding among
adjudicators. (4) No mid-study verdict reveal / no peeking — the matrix is computed **once**, after all 500
decisions and all 100 adjudications are locked. (5) Tamper-evidence — every decision and every ground-truth
entry is appended to the append-only, hash-chained, Merkle-rooted signed registry; the published artifact
includes the Merkle root, and any verdict's audit_hash is re-derivable via `POST /api/gate/verify`.

## II.7 Separate reporting rule (pre-registration §12) — the line that must hold

Track A and Track B produce **two confusion matrices, two false-accept figures, two reliability statistics**,
reported side by side, **never averaged**. Track A → "computable-truth verification" (accuracy + false-accept
vs computed law; reliability = inter-analyst coding-error rate, not κ). Track B → "blind human adjudication"
(confusion matrix + false-accept vs consensus; reliability = inter-adjudicator κ, H3). The primary safety claim
H1 (false-accept ≤ 5%) is reported pooled and per-domain, but the report states plainly which domains'
ground-truth came from Track A (computed) vs Track B (adjudicated). Any headline number blending a
trivially-computable Track-A pass-rate into a "human-adjudicated accuracy" is a forbidden reporting deviation.

---

# PART III — Independence framing (this study vs the IBM kingston validation)

The repo already contains *one* genuinely independent validation of CAPAS (the IBM kingston hardware audit,
`docs/capas_vs_sota_and_ibm.md`). This study adds a *second, different kind*. The two are easy to conflate and
easy to overclaim. This part fixes the boundary; it makes no new empirical claim.

## III.1 Two independent validations, two different objects

| | **IBM kingston validation** (already in repo) | **This pre-registered study** (the missing layer) |
|---|---|---|
| **Object validated** | The *architecture* — invariant checks + threshold gates + fail-closed verdict + served/withheld data tier | The *empirical false-accept rate* — does a real ACCEPT survive blind human adjudication of admissibility |
| **Kind of independence** | A production system, built by others, at industrial scale, for a domain CAPAS did not design for, *converged on the same pattern* (consilience); CAPAS re-found its atlas live | *External human adjudicators*, blind to CAPAS's verdict, fix ground-truth across domains; CAPAS is scored against their consensus |
| **Source artifact** | `docs/capas_vs_sota_and_ibm.md` §1 (consilience), §3 (live kingston proof: `examples/kingston_live_audit.py`) | `docs/PREREGISTRATION_CROSS_DOMAIN_ADJUDICATION.md` §1, §4, §7 |
| **Registry status it speaks to** | The *structural* claim: `CLOSED` (row 12 — fail-closed proven by `benchmarks/verify_fail_closed.py`) | The *rate* claims: `SCOPED` → `BACKED` (rows 21–23) on completion |

The registry already encodes this split: **row 12 ("Fail-closed: a structurally-deficient claim is never
accepted") is `CLOSED`** — a proven structural invariant — while its own note says *"Empirical false-accept
RATE on real claims is SCOPED below."* Rows 21–23 are exactly that SCOPED rate. The IBM result strengthens the
*architecture* behind row 12; it does **not** touch rows 21–23. Only this study does.

## III.2 What the IBM kingston result establishes — and does NOT

**Establishes (per `docs/capas_vs_sota_and_ibm.md`):** (1) **Independent architectural validation
(consilience, not analogy)** — IBM's calibration system is structurally a production admissibility engine
(measures physical quantities, checks invariants/thresholds, emits a fail-closed `Operational: Yes/No`, manages
a disclosure boundary); a system built independently for a domain CAPAS did not design for converged on the
exact pattern. (2) **A live, reproducible audit of real hardware** — `examples/kingston_live_audit.py` ran the
gates over the live ibm_kingston calibration (155 qubits, 176 edges, open-plan, metadata only) and independently
re-found the atlas: exactly one T2 > 2·T1 anomaly (Q121), 0 gate errors below the relaxation floor — i.e. no
false-positive on this one honest device — the TLS edge cluster, and all residual ZZ < 10 kHz. (3) **One axis
where CAPAS is stricter** than the industrial engine (silent frozen-calibration reported `Operational`).

**Does NOT establish:** (1) It is not a blind-adjudicated false-accept rate — the kingston audit checks CAPAS
against *computable physical invariants* (Track-A–style ground-truth), not a human judgment of contestable
admissibility. (2) It is single-device and single-domain — says nothing about statistics, epidemiology, biology,
finance, or the judgment-heavy domains where H1/H2 are most at risk. (3) The "DEFER" and "fail-open leak"
readings are CAPAS's interpretation, not IBM doctrine.

## III.3 What this study establishes — and does NOT

**Establishes (on completion):** (1) the missing layer — independent **human** adjudication of admissibility,
across domains, blind to CAPAS (Track B); (2) pooled and per-domain confirmed false-accept rate with CIs (H1),
separation vs an LLM-judge plausibility baseline (H2), inter-adjudicator κ (H3) — computed once, on real claims
from public artifacts with no synthetic claims; (3) the tamper-evident artifact that flips rows 21–23
SCOPED → BACKED.

**Does NOT establish:** (1) it does not validate the architecture independently of CAPAS's authors — that is
what IBM supplies; the two are complementary, not substitutes; (2) it does not measure prospective field
performance (retrospective) or truth (it measures false-accept against *adjudicated structural admissibility*);
(3) it draws no support from IBM.

## III.4 Standing limitations that bound BOTH

- **Retrospective, not prospective.** The kingston audit reads a published calibration snapshot; the study uses
  historical claims. Both measure separation/admissibility, not deployed prospective performance.
- **The GIGO ceiling is intact for both.** A fully self-consistent fabrication can pass: the kingston gate
  cleared the vendor's numbers only because they were self-consistent; the study explicitly measures
  false-accept against *adjudicated structural admissibility, not ultimate truth*. CAPAS raises the *cost* of
  lying — "fabricate a globally-consistent world" — it does not abolish it.
- **Structure, not ultimate truth.** Both validate that CAPAS gates *structure* (physical invariants in one
  case, adjudicated admissibility in the other). Neither establishes that an accepted claim is *true* — the
  same scope discipline the registry encodes as CLOSED-structural (row 12) vs SCOPED-empirical (rows 21–23).

## III.5 No implied IBM endorsement (explicit)

- **IBM did not design, review, adjudicate, fund, or endorse CAPAS or this study.** The kingston evidence is a
  third-party-independent audit of public calibration metadata (open-plan, metadata only) plus an observation of
  architectural convergence — consilience, not a partnership, certification, or statement by IBM.
- **The interpretive framings are CAPAS's, flagged as conjecture** in the source: "DEFER = disclosure boundary"
  and "silent-frozen-calibration = fail-open leak" are CAPAS's reading of IBM's observed behavior, not IBM's
  stated design.
- **This study's independence comes from its external adjudicators, not from IBM.** For *this study*,
  "independent" = the blind external human adjudicators; for the *IBM result*, "independent" = architectural
  convergence + a re-found atlas. The two senses must not be merged into "IBM-validated false-accept rate" — no
  such object exists.

## III.6 One-line position (citation-safe)

> CAPAS has **independent architectural validation** — IBM's production calibration engine converged on its
> invariant + threshold + fail-closed pattern, and CAPAS re-found the kingston atlas live
> (`docs/capas_vs_sota_and_ibm.md`, `examples/kingston_live_audit.py`) — and this pre-registered study supplies
> the **independent human-adjudication layer** that the IBM result cannot: a blind, cross-domain false-accept
> rate. The first validates the *structure* (registry row 12, `CLOSED`); the second is what moves the
> *empirical rate* (registry rows 21–23) from `SCOPED` to `BACKED`. Both remain bounded by the retrospective
> scope and the GIGO ceiling, and neither carries any IBM endorsement.

---

# Limitations of this protocol (stated up front)

- **Source availability bounds balance.** Some domains have far more public admissible than inadmissible
  artifacts (or vice versa); the I.2 balance rule caps the per-domain n at the limiting arm and down-samples the
  surplus by the frozen seed. Realized splits are reported, not engineered.
- **Track-A seeding is a controlled artifact, not a found error.** The inadmissible Track-A arm uses auditable
  alterations of published rows/equations (logged in `alteration_log`); it tests the invariant under a known
  violation and is never presented as a found-in-the-wild fraud. **Track B has zero seeding.**
- **Mixed-domain routing is discretionary.** The epidemiology/finance A-vs-B split is a judgment; the
  Track-B-governs-ties rule (II.1) means any misroute can only make a claim easier to ground-truth
  conservatively, never lower H1's bar, and the Track-assigner role (II.6) puts the routing on the audit chain.
- **Point-in-time reconstruction is best-effort.** Establishing the exact contemporaneous evidence state (I.4)
  can be imperfect for older claims; unrecoverable cases are dropped (recorded), not guessed.
- **The GIGO ceiling stands** (pre-registration §12): a self-consistent fabrication can still pass; this corpus
  measures false-accept against *adjudicated / computed structural admissibility*, not ultimate truth.

---

*Grounding: `docs/PREREGISTRATION_CROSS_DOMAIN_ADJUDICATION.md` (§2 hypotheses, §3 stratification, §4 two
tracks, §5 sampling/freeze, §6 blinding/independence, §7 outcomes, §8 success criteria, §10 tamper-evidence,
§12 limitations); `outputs/pilot_metrics.json → pilot_design` (n=500, adjudication 100, success metrics);
`docs/capability_matrix.md` (10-domain / 26-gate track frame); `benchmarks/pilot_real.py` (real-claim sourcing
precedent, evidence contracts, "human adjudication is the next step"); `capas_registry.py` (hash-chained log,
verdict wall, ordering); `docs/schema/v3/capas_claim_payload.schema.json` (`capas-claim-payload-v3`);
`docs/capas_vs_sota_and_ibm.md` + `examples/kingston_live_audit.py` (IBM kingston independence);
`docs/CLAIMS_REGISTRY.md` rows 12 (CLOSED) and 21–23 (SCOPED → BACKED target). No empirical claim beyond these
artifacts; interpretive IBM framings are flagged as conjecture per the source. This protocol collects and
adjudicates nothing — it is the frozen construction + ground-truth + framing specification only.*
