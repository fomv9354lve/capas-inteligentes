# CAPAS — Moat and Certification Stack

> The consolidated, corrected, defensible statement of what CAPAS's moat is, what it
> is **not**, and the certification stack that constitutes it. Every claim below is
> BACKED, SCOPED, REWRITTEN, or DELETED against a named, re-derivable repo artifact
> (REGLA CERO). Honest scope is carried inline, not as a footnote.

---

## 1. What the moat is NOT (the copyable rungs, stated honestly)

CAPAS is **open core under Apache-2.0** (`LICENSE`, `NOTICE`, `GOVERNANCE.md` §1). That
is deliberate, and it means the parts most people would assume are "the moat" are
freely copyable. Stated plainly:

- **The engine is copyable.** Apache-2.0 lets anyone fork the gate, schema, calculus,
  CLI, and benchmark corpus. The page itself concedes this: *"Any one gate is
  copyable."* (`docs/index.html:604`).
- **The individual gates are copyable.** A quantum routing dispatcher
  (Clifford→Stim, non-Clifford→tensor/dense, `benchmarks/verify_route.py`) is a
  structure switch a consultancy reproduces in under a week. The ~35-line
  `gate_quantum_advantage_claim` (`capas_quantum_physics.py:282-317`) is an
  afternoon's work.
- **The self-gating discipline is copyable.** A registry that fails a release on bare
  claims (`benchmarks/generate_proof_ledger.py`) is ~150 lines of subprocess +
  dict-counting CI. An equivalent `proof_ledger.py` is a week's work for any
  competent team.
- **The self-run / deterministic harness is a commodity pattern.** It is explicitly
  *"modeled on Certified Kubernetes / Sonobuoy"* (`benchmarks/conformance.py:1-4`,
  `GOVERNANCE.md` §5). Selling "deterministic + self-runnable" as the differentiator
  sells a published distribution mechanic.
- **The governance template is copyable.** The charter itself names
  *"the Certified-Kubernetes pattern"* and cites CNCF / Styra-OPA as *"the model this
  charter copies"* (`GOVERNANCE.md` §8). A law firm reproduces the legal template in
  under a week.
- **The error-budget arithmetic is textbook.** Every term in `complete_error_budget`
  (`capas_quantum_physics.py:468-516`) — the dephasing identity, ZZ→infidelity, the
  Proctor 3–10× band — is textbook; IBM/Qiskit could rewrite the 50-line function in
  an afternoon.

If the moat were any one of these, it would not be a moat.

---

## 2. What it IS — certification-as-standard

The moat is **trust you can audit**: a certification stack a regulated buyer can
reproduce without trusting us, and a third party can try to refute. Four load-bearing
pieces, each BACKED:

### 2.1 Self-run conformance (re-derivable hash)

`python3 benchmarks/conformance.py` runs the **exact suite the certifier runs** and
returns the same verdict and the same result hash on re-run: verified here as
`sha256:3d3b5cf39aaffef23fa8562b`, byte-identical against the committed
`outputs/conformance_result.json`. The hash is taken over the load-bearing pass/fail
set — fail-closed, robustness, no-LLM-in-verdict, quantum-defeater,
pharma-admissibility, proof-ledger, hold-has-resolution, audit-hash-reproduces
(`benchmarks/conformance.py:25-34`).

**Honest scope:** the hash is reproducible **on re-run for the same suite-pass
profile**, not guaranteed across arbitrary environments — no pinned interpreter or
lockfile is asserted (`conformance.py:50-51`). What is proven is re-run determinism,
not cross-machine determinism.

### 2.2 The signed, re-derivable certificate

`capas_certstore.py` issues a **signed, persisted, content-addressed** admissibility
certificate: `cert_id = sha256(canonical(certificate) + nonce)`, with an HMAC-SHA256
signature over a canonical body that includes `capas_version`
(`capas_certstore.py:45-80`). `POST /api/certificate/verify` (and `/api/gate/verify` →
`capas.verify_audit_hash`, `capas_api.py:100`) recompute over the identical tuple:
alter `capas_version` or the certificate body and `verify()` returns `valid:false`.

**Honest scope on signature reach:** the HMAC binds the certificate **content** —
tamper-evidence + engine-version binding, non-repudiable. It does **not** certify the
claim is true (the GIGO ceiling), and it does **not**, on its own, prove the verdict
was produced deterministically. A key-holder could sign a non-deterministically
produced verdict and `verify()` would still pass. The determinism guarantee lives in
the **engine** (`capas_verify.py`: `"decision_path": "deterministic; no LLM"`) and is
independently re-checkable via the self-run conformance mark (`no_llm_verdict` must
PASS in `outputs/conformance_result.json`) — not in the certstore.

### 2.3 The reserved mark under a binding, irrevocable charter — as DISCLOSED

`GOVERNANCE.md` pre-commits the CAPAS name and certification/conformance mark to
neutral governance **before** CAPAS is promoted for adoption, on the trustee-escrow
model that let Open Policy Agent's standard outlast its sponsor's acquisition
(`GOVERNANCE.md` §3, §8: *"the standard survived because CNCF, not Styra, held the
mark"*).

**Honest scope — this is intent made binding-by-instrument, not yet executed.** The
charter's own status block self-discloses the open items: the trustee is the literal
placeholder `[TRUSTEE — to be named]`, the escrow is *"operative once"* executed, and
the open items are *"(1) name the trustee; (2) execute the escrow/assignment with
counsel"* (`GOVERNANCE.md` lines 22-23, 100-107). `NOTICE` backs **authorship +
Apache-2.0 only** — a grep for `reserv/trademark/mark/certification` returns zero; no
trademark registration is filed, no escrow instrument is in the repo. So §1/§2/§4/§5
are a public, binding statement of direction **to be made legally irrevocable by an
executed instrument** — not yet a running legal ratchet. The asset operative *today*
is the self-runnable mark (§2.1), not the legal reservation.

### 2.4 The IBM consilience (independent architectural validation)

A frontier quantum-hardware vendor's production stack already runs the CAPAS
architecture. IBM will not run a circuit until it clears a calibration gate — every
job checked against frozen, re-derived device invariants, fail-closed, no
model-of-the-day in the decision. That is exactly the CAPAS mechanism: re-derive from
declared evidence, refuse on violation, keep the verdict deterministic
(`examples/kingston_live_audit.py`; `docs/capas_vs_sota_and_ibm.md:11-23` —
*"(Fact)"* architectural convergence). Two independent systems converging on the same
admissibility mechanism is **consilience**: evidence the design is structural, not a
pitch.

**Honest scope:** the identities CAPAS checks are **textbook** and the convergence is
**architectural, not a partnership claim**. The mechanism is the open Apache-2.0
engine — re-derivable, therefore copyable — so the consilience **validates the design
but is not the moat**. On frozen calibration, CAPAS is in fact the **stricter** of the
two. The cross-domain reach is two counts, not one: `docs/proof_ledger.json:40` backs
26 gates / 10 domains, while the single fail-closed invariant filter
(`capas_invariants`) is demonstrated end-to-end on finance, psychology, and quantum
(`docs/capas_vs_sota_and_ibm.md:65`).

### The moat, in one line

A competitor can copy a gate in a week. It **cannot** retroactively copy a
self-runnable conformance mark, a signed-certificate audit trail, and a
renounced-in-writing relicensing posture, all attesting a verdict a third party can
reproduce and try to refute. **The moat is the auditable standard around the tool, not
the tool** — and, honestly scoped, it is a *design and audit surface*, not yet an
adoption claim: no external party has yet certified against the mark.

---

## 3. Final verdict on every moat claim

Each row: the original claim → its final verdict → the corrected, defensible wording →
the artifact that re-derives it. **No universal-negative survives** (REGLA CERO): an
absence claim is at most survey-scoped to a named set.

### 3.1 "The standard, not the tool, is the moat" — `docs/index.html:603-604`

**Verdict: REWRITE.** Aspirational-stated-as-fact + phantom artifact.

- DROPPED — *"becoming the standard claims are checked against"* / *"the reference that
  keeps surviving refutation becomes the standard"*: a standard is constituted by third
  parties checking against it, and **no artifact re-derives a single external
  adoption** — `docs/reviewer_registry.json` holds one self-labeled
  `"local_registry_fixture"`, `docs/witness_registry.json` one `"analytic_no_solver"`
  math anchor, and `docs/CLAIMS_REGISTRY.md` / `docs/proof_ledger.json` enumerate CAPAS
  gating its **own** claims (self-reference, not external reference).
- DROPPED universal-negative — *"THE standard"* presumes no incumbent, yet
  `docs/index.html:621` names **Pinnacle 21** as the entrenched CDISC conformance
  reference in the pharma beachhead.
- DROPPED phantom — *"a survive-refutation ledger anyone can challenge"* implies a
  persisted, logged external-challenge ledger; `benchmarks/demo_survive_refutation.py`
  writes only an **ephemeral** `/tmp/capas_ledger_demo/ledger.json` wiped on every run.
  The mechanism (`capas_ledger.py` / `capas_sdk.standing/resolve`) is real and BACKED;
  the *populated, externally-challenged* ledger is not.

**Corrected:** *"The moat isn't any single gate. It's the audit surface a standard is
made of: self-runnable, deterministic, irrevocably governed. Conformance is
self-runnable and deterministic (`python3 benchmarks/conformance.py` → same verdict +
same result hash). Each certificate is signed, persisted, content-addressed
(`capas_certstore.py`). The mark is pre-committed to neutral governance in writing,
irrevocably, before adoption (`GOVERNANCE.md` §3). That is the moat — the auditable
standard around it, not the tool. Honest scope: this is the design and the audit
surface, not an adoption claim; no external party has yet certified against the mark."*

**Re-derive:** `benchmarks/conformance.py`, `capas_certstore.py`, `GOVERNANCE.md` §3/§8,
`docs/CLAIMS_REGISTRY.md`.

### 3.2 "What compounds is trust you can audit" — `docs/index.html:604`

**Verdict: REWRITE.** Compound: the audit/re-derive sub-clauses are BACKED; the
present-tense *"becomes the standard … is the moat"* is aspirational-as-fact + latent
universal-negative.

- SURVIVES — deterministic, re-derivable, fail-closed, third-party-refutable verdict
  (`benchmarks/verify_audit_hash_reproduces.py`, `verify_fail_closed.py`,
  `verify_cara_decoupling.py`, all CLOSED).
- SURVIVES — every headline claim CLOSED/BACKED/SCOPED
  (`docs/CLAIMS_REGISTRY.md`, regenerated by `benchmarks/generate_claims_registry.py`).
- DROPPED — *"becomes the standard / is that reference / the standard is the moat"*:
  no external-adoption artifact; Pinnacle 21 incumbent at `index.html:621`.

**Corrected:** trust is **earnable, not asserted** — every verdict re-derives to a hash
an independent party reproduces; every headline claim is CLOSED/BACKED/SCOPED in a
public ledger disclosing which numbers are synthetic; the mark attests only that an
artifact passed a suite *you run yourself*. *"Whether it becomes the reference standard
depends on third parties actually challenging it; that adjudication is open, not yet
run."*

**Re-derive:** `benchmarks/verify_audit_hash_reproduces.py`, `docs/CLAIMS_REGISTRY.md`,
`benchmarks/conformance.py`, `capas_certstore.py`,
`benchmarks/demo_survive_refutation.py`.

### 3.3 "Open engine: the method is inspectable; the standard is the asset." — `docs/index.html:596`

**Verdict: REWRITE.** Inverted-moat: *"method is inspectable"* is BACKED but is the
**fully copyable** half (Apache-2.0); *"the standard is the asset"* is **not** a
present-tense fact — `GOVERNANCE.md` (lines 22-23, 100-101, 106) flags trustee/escrow
as open items.

**Corrected:** *"Open engine, Apache-2.0 (`LICENSE`): the method is fully inspectable
and the verdict re-derivable by anyone. The defensible asset isn't the copyable engine
— it's the self-runnable conformance mark, pre-committed to neutral trustee-escrow in a
binding, irrevocable charter (`GOVERNANCE.md`), with the trustee and escrow named as
open items before it is operative."*

**Re-derive:** `benchmarks/conformance.py`, `capas_certstore.py`, `LICENSE` + `NOTICE`,
`GOVERNANCE.md` §1/§2.

### 3.4 Quantum oracle "no published competitor" — `docs/MOTOR_INGEST_LOG.md:25` (row #7)

**Verdict: REWRITE → positioning hypothesis (not a measured moat).** Three hits: (1)
the 10-tool competitor set occurs in **exactly one file**
(`grep -rln "QuAntiL|QProv"` → `docs/MOTOR_INGEST_LOG.md` only) — no per-competitor
capability matrix exists, so the comparative-negative is cited-not-verified hearsay;
(2) the device-calibrated frontier is *"same-device validated, cross-device pending"*
(`docs/CLAIMS_REGISTRY.md`); (3) the backed routing half is copyable
(`benchmarks/verify_route.py`).

**Corrected:** On the motor's *cited, not independently re-verified* reading of the
surveyed set (Stim, quimb, cotengra, Cirq-qsim, Pan-Zhang, Tindall, AGLLV,
Begušić-Chan, IBM QProv, QuAntiL), none is *documented* to combine device-calibrated
routing with frontier prediction. Two debts: no competitor matrix; frontier
same-device-only. The moat is **not** "no competitor does X" — it is the self-run
conformance mark + signed audit-hashed certificate.

**Re-derive:** `grep -rln "QuAntiL|QProv"` (single hit), `docs/CLAIMS_REGISTRY.md`,
`benchmarks/verify_quantum_commitment.py`, `benchmarks/verify_route.py`,
`benchmarks/conformance.py` + `capas_certstore.py`, `docs/MOTOR_INGEST_LOG.md` row #6.

### 3.5 `commitment_depth` predicts the quantum→classical crossover — `docs/MOTOR_INGEST_LOG.md:26` (row #8)

**Verdict: REWRITE — CLOSED (gate contract) · SCOPED·FLAG (frontier evidence).** The
gate is CLOSED (`benchmarks/verify_quantum_commitment.py`, 5/5, exit 0 — locks the `<`
defeater, `capas_quantum_physics.py:282-317`, scope at `:295-297`). The **frontier** is
supplied evidence, NOT re-derivable here: the commitment_depth→crossover mapping is
cited to upstream `physics-magnitude-lab` and returns **zero grep hits** in this repo.
CAPAS *gates* a supplied same-device commitment depth; it does not *measure* the
frontier. The defensible asset is not the ~35-line gate but the conformance mark +
signed certificate.

**Re-derive:** `benchmarks/verify_quantum_commitment.py`,
`capas_quantum_physics.py:282-317/:295-297`, `docs/CLAIMS_REGISTRY.md:15`;
frontier leg NONE re-derivable (`../physics-magnitude-lab` = 0 hits).

### 3.6 "CAPAS fills a gap that existing tools leave open" — `docs/index.html:360`

**Verdict: REWRITE.** Universal-negative + aspirational-as-fact. *"Fills a gap that
existing tools leave open"* asserts absence across **all** tools; the only on-point
artifact (`docs/GLOBAL_SOTA_MARKET_AUDIT.md`) labels the slot only *"Partially
adjacent, no exact dominant incumbent found"* (line 47) and files current status as
**HOLD / awaiting practitioner validation** (lines 321-323, 336);
`docs/sota_positioning_matrix.json` *forbids* the "new standard" framing. Only
*"structured, deterministic admissibility gating"* is BACKED (`CLAIMS_REGISTRY.md`
line 14, CLOSED).

**Corrected:** survey-scope the negative to the named set (RO-Crate / Workflow Run
RO-Crate, SciAgentGym, QMB100/PhysVEC, AiiDA, OpenKIM/VVUQ, C2PA, ClaimCheck-class)
and anchor on determinism (*same input → same `audit_hash`, no LLM in the verdict*) +
the self-run conformance mark (`python3 benchmarks/conformance.py`) + signed
certificate. *"That self-checkable mark, not the individual checks, is the moat."*

**Re-derive:** `docs/CLAIMS_REGISTRY.md` line 14 (`verify_cara_decoupling.py`),
`docs/GLOBAL_SOTA_MARKET_AUDIT.md`, `docs/sota_positioning_matrix.json`,
`benchmarks/conformance.py`, `capas_certstore.py`.

### 3.7 "None of them gate … that side of the stack is empty" — `docs/index.html:384`

**Verdict: REWRITE.** Universal-negative-as-fact. *"None of them gate"* / *"empty"*
quantifies over every system with no surveyed set named — and CAPAS's own strongest
validation artifact (`docs/capas_vs_sota_and_ibm.md`) refutes "empty" by showing IBM's
calibration system **is** a production admissibility engine. The page's own vs-table
two lines below lists LLM-as-judge / fact-checkers as partially gating.

**Corrected:** name the slices each adjacent system gates (LLM-as-judge stochastic,
fact-checkers truth-not-boundary, Pinnacle 21 / statcheck single-domain, IBM
single-domain physical-qubit), then: *"Across the systems we surveyed we found no
general-purpose, deterministic, replayable gate that decides whether a claim is
licensed by its evidence before reuse — and proves it the same way twice."* Anchor on
fail-closed + re-derivable certificate + conformance hash.

**Re-derive:** `benchmarks/verify_fail_closed.py`, `benchmarks/verify_cara_decoupling.py`,
`benchmarks/conformance.py` → `outputs/conformance_result.json`, `capas_certstore.py`,
`docs/capas_vs_sota_and_ibm.md`, `benchmarks/head_to_head_sota.py` (SCOPED 10-claim).

### 3.8 The IBM consilience block — `docs/index.html:583-585`

**Verdict: REWRITE.** Three legitimate hits, none fatal (block carries its own scope
lines): (1) unbacked superlative *"the most demanding hardware stack in the world"* —
ranked by no artifact; (2) reach overstatement — *"generalizes across ten domains"*
conflates 26 gates / 10 domains (`proof_ledger.json:40`) with the single invariant
filter shown on ~3 (`capas_vs_sota_and_ibm.md:65`); (3) consilience validates a
**copyable** Apache-2.0 mechanism, so it is not itself the moat.

**Corrected:** *"a frontier quantum-hardware vendor's production stack already runs
it"* (drop the superlative); IBM gates fail-closed against frozen invariants = exactly
the CAPAS architecture; CAPAS runs 26 gates / 10 domains, the single invariant filter
demonstrated on finance/psychology/quantum. *"The mechanism is the open Apache-2.0
engine — re-derivable, therefore copyable — so the consilience validates the design but
is not the moat. What is defensible is the cross-domain composition plus the self-run
conformance mark and signed certificate."* On frozen calibration CAPAS is the stricter.

**Re-derive:** `examples/kingston_live_audit.py`,
`docs/capas_vs_sota_and_ibm.md:11-23,65`, `docs/proof_ledger.json:40` +
`docs/capability_matrix.md`, `benchmarks/conformance.py`, `capas_certstore.py`,
`benchmarks/kingston_real_bell_verdict.json` (coarse-grained, order-of-magnitude).

### 3.9 The generate-vs-gate vs-table — `docs/index.html:383-394`

**Verdict: REWRITE.** Universal-negative at `:384` (*"None of them gate … empty"*);
`benchmarks/head_to_head_sota.py` only surveys a **named modeled set** (LLM-as-judge,
optimistic-oracle/UMA, peer-prediction/BTS, reputation/EigenTrust). The table is a
copyable category frame; the LLM-judge *"not replayable"* cell is non-replay **by
design** (single `h2h_llm_judge_run.json`), not measured.

**Corrected:** bound the negative to the named surveyed set; soften the LLM-judge cell
to *"stochastic by construction · no replay guarantee"*; tighten *"(test-proven)"* to
*"(conformance-test-proven)"*; re-anchor the CAPAS row on the self-run conformance mark
(`benchmarks/attest_conformance.py`, `conformance.py`, `GOVERNANCE.md` §5/§6) as the
non-copyable distinction.

**Re-derive:** `benchmarks/head_to_head_sota.py`, `benchmarks/verify_fail_closed.py` +
`outputs/conformance_result.json`, `benchmarks/conformance.py`,
`benchmarks/verify_audit_hash_reproduces.py`, `benchmarks/attest_conformance.py`,
`benchmarks/h2h_llm_judge_run.json`.

### 3.10 "We beat a vendor benchmark with the vendor's own numbers" — `docs/index.html:568-576`

**Verdict: SCOPE.** Survives as a truth; the device conflation must be scoped. The
displayed `1.9e-2` / 11× headline is **`ibm_fez` q9-q10** (`BEATING_THE_BENCHMARK.md:26-37`),
but the live-validation prose reads as **`ibm_kingston` Q121** — two devices conflated;
no committed artifact runs `complete_error_budget` on Q121. The XEB *"2.53× direct"*
leg cites `/tmp/xeb_results.json` (**not** in `git ls-files`) — not currently
re-derivable.

**Corrected scope:** the `1.9e-2` worst case is `ibm_fez` q9-q10, re-derived
term-by-term (each term marked EXACT vs literature-estimate; the 3–10× band is a cited
Proctor range, not our finding). The live leg is a **separate** device:
`ibm_kingston` Q121 re-found from calibration alone, Bell measured 0.045 vs re-derived
floor 0.020 ≈ 2.2×, ADMISSIBLE under two oracles. The arithmetic is copyable; the
fail-closed conformance discipline that refuses the optimistic headline is not.

**Re-derive:** `capas_quantum_physics.complete_error_budget` (`:468-516`) on
`ibm_fez` q9-q10 (`docs/BEATING_THE_BENCHMARK.md:26-37`),
`benchmarks/kingston_real_bell_verdict.json` (2.2× live leg),
`docs/CLAIMS_REGISTRY.md:19` (BACKED). **NOTE:** the XEB 2.53× leg is NOT re-derivable
(`/tmp/xeb_results.json` uncommitted) — commit under `benchmarks/` or drop the leg.

### 3.11 "Conformance is self-runnable and deterministic" — `GOVERNANCE.md:51-58` (§5)

**Verdict: REWRITE.** (1) the determinism/self-run mechanic is a commodity
*"Sonobuoy"* pattern — the non-copyable part is **this specific 8-invariant set** +
the mark + the signed certificate; (2) present-tense *"the certifier runs"* / *"yearly
re-certification"* describe a governance process with **no shipping artifact**; (3)
*"reproduces on any machine"* over-claims — the hash covers a boolean pass-set with no
pinned interpreter/lockfile, so it is **re-run** determinism, not cross-machine.

**Corrected:** scope to *"same suite-pass profile → same hash, reproducible on re-run,
not guaranteed across arbitrary environments"*; name the non-copyable trio (the
load-bearing invariant set, the mark, the signed certificate); isolate the certifier /
PR-pipeline / annual cycle as **governance design, not an operating service**. The
conformance right is irrevocable under §3.

**Re-derive:** `benchmarks/conformance.py` (`--json` → `result_hash
sha256:3d3b5cf39aaffef23fa8562b`, suite at `:25-34`, hash at `:50-51`),
`capas_api.py:100` (`/api/gate/verify`), `capas_certstore.py:45-57`. **Also align**
`conformance.py:67` print string to *"deterministic on re-run — same suite-pass
profile → same hash"*.

### 3.12 Certificate signature scope — `capas_certstore.py:4-8`

**Verdict: REWRITE.** *"it certifies that THIS verdict was deterministically
produced"* credits the HMAC with a guarantee it cannot deliver — an HMAC over content
proves only that this exact record was signed by this key and unaltered; it does **not**
establish the verdict's production was deterministic. The determinism lives in the
engine (`capas_verify.py`: `"decision_path": "deterministic; no LLM"`), independently
re-checkable via the conformance mark (`no_llm_verdict` PASS).

**Corrected:** the signature binds content (tamper-evident, non-repudiable, includes
`capas_version`); it does NOT certify truth (GIGO) and does NOT on its own prove
determinism — that comes from the no-LLM decision path and is re-checkable via
`python3 benchmarks/conformance.py`.

**Re-derive:** `capas_certstore.py:45-46/49-58/71-80`, `capas_verify.py` decision_path,
`benchmarks/conformance.py` (`no_llm_verdict` pass in
`outputs/conformance_result.json`).

### 3.13 Reserved mark / irrevocable charter — `GOVERNANCE.md:9-35` (§1/§2/§3)

**Verdict: REWRITE.** Four hits: (1) §2 cites `NOTICE` to prove the mark *"is
reserved"* — `NOTICE` is a bare Apache-2.0 notice, grep for
`reserv/trademark/mark/certification` = **zero**; (2) escrow *"effective now"* is
contradicted by the status block placeholder `[TRUSTEE — to be named]` + open items
(lines 23, 101, 106); (3) *"IRREVOCABLE … void"* is legal effect the document does not
yet have (line 102 concedes terms *"are to be finalized in an executed legal
instrument"*); (4) the legal template is copyable by the charter's own admission
(*"the model this charter copies"*, §8). Soft universal-negative in §7 generalizes a
5-row table into a causal law.

**Corrected:** §1 backed; §2/§3 rewritten to **intent-to-be-made-irrevocable-by-executed-instrument**,
trustee/escrow/registration as open items, the **self-run conformance mark** named as
the asset operative today; §7 scoped to *"in the surveyed set below, every project
that relicensed … triggered a neutral-foundation fork"*.

**Re-derive:** BACKED rung = self-run conformance (`benchmarks/conformance.py`,
`/api/gate/verify` → `capas_api.py:100`, `capas_certstore.py`). NO artifact backs
"reserved"/"irrevocable"/"escrow effective now" — `GOVERNANCE.md` status block
(100-107) self-refutes; `NOTICE` grep = empty; no `TRADEMARKS.md`, no filing. §7 = named
5-row survey only. **Fix:** either add reservation text to `NOTICE` / create
`TRADEMARKS.md`, or drop the *"(see NOTICE)"* citation.

### 3.14 "CAPAS gates its own claims" / ledger 4·5·3·0 — `docs/CLAIMS_REGISTRY.md:3-6,25`

**Verdict: REWRITE.** (1) *"every public number on this site"* over-claims — the
release gate governs only the 12 enumerated rows; the registry concedes leakage
(§27-29: the capacity/savings widget and 1,238/78.4% grid are illustrative, **not**
gated). (2) the self-status-checking registry is a copyable ~150-line CI discipline.
The count **is** BACKED (`generate_proof_ledger.py` ran green, exit 0, {CLOSED:4,
BACKED:5, SCOPED:3}, bare:0).

**Corrected:** *"Every headline claim **in this registry** carries a machine-checked
admissibility status"* (not "every public number on this site"); scope `admissible` =
*"carries a re-derivation command, not measured/true"* (§32 GIGO); note UI numbers
outside the registry are illustrative (§27-29); demote the copyable self-gating wrapper
and point the moat at the evidence the rows cite (conformance mark + signed
certificate).

**Re-derive:** `benchmarks/generate_proof_ledger.py` (release gate, exit 0,
{CLOSED:4,BACKED:5,SCOPED:3}, bare:0), `benchmarks/conformance.py` +
`benchmarks/attest_conformance.py`, `capas_certstore.py:sign`,
`docs/CLAIMS_REGISTRY.md` §27-29 / §31-32.

---

## Verdict tally

| Verdict | Count | Claims |
|---|---|---|
| BACKED (survives as worded) | 0 | — |
| SCOPE | 1 | 3.10 (vendor benchmark — device conflation scoped) |
| REWRITE | 13 | 3.1–3.9, 3.11–3.14 |
| DELETE | 0 | — |

**Pattern:** every refutation hit was one of three shapes — a **universal-negative**
(no surveyed set; 3.1, 3.6, 3.7, 3.9, and the §7 / row-#7 negatives), an
**aspirational-as-fact** adoption/legal claim where no external oracle exists (3.1,
3.2, 3.3, 3.13 — the generative-fail-open invariant), or a **copyable-rung
conflation** that mistook an open, reproducible mechanism for the moat (every row).
The corrected wording, throughout, re-anchors the moat on the one thing that is both
BACKED and not freely copyable: **a self-run conformance mark + a signed, re-derivable
certificate, under a charter committed in writing to neutral governance** — a verdict a
regulated buyer can reproduce and a third party can try to refute. Honest scope is
carried in every claim: this is the design and audit surface, **not** an adoption claim.
