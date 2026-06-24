# Adoption-Gate Readiness Ledger — is governance OPERATIVE before promotion?

*Companion to `GOVERNANCE.md`, `docs/GOVERNANCE_OPERATIONALIZATION.md`, and
`benchmarks/attest_conformance.py`. This ledger records the state of each existing governance commitment as
of the artifacts in the repo today — it invents no new commitment. It answers one question: is the
charter's load-bearing pre-condition — **"neutral, irrevocable governance executed BEFORE adoption"** —
true in fact, or only true in stated direction?*

## 0. What this ledger decides

`GOVERNANCE.md` is, in its own words, a *"binding statement of direction, effective on publication"* whose
*"irrevocability (§3) and trigger/transfer terms (§4) are the load-bearing commitments and are to be
finalized in an executed legal instrument by counsel"* (Status paragraph). Its thesis is the
**before, not after** condition: *"separate the standard/mark from the commercial entity before adoption,
not after"* (opening) and *"pre-commits them to neutral governance before CAPAS is promoted for adoption"*
(§2). This ledger records whether that pre-condition holds. Status vocabulary:

- **SATISFIED** — operative today; re-derivable from a named repo artifact.
- **DRAFT-for-counsel** — substance is written and binding-on-publication, but legal effect requires an
  executed instrument the project cannot self-execute (needs counsel / a third-party signature).
- **OPEN** — neither executed nor self-completable from inside the repo; a named external act is missing.

Per `docs/CLAIMS_REGISTRY.md` discipline (no bare claims), every row cites the grounding artifact; every
DRAFT/OPEN is labeled honestly per CAPAS scope discipline.

## 1. The ledger

| # | Operative precondition | Charter locus | State | Grounding artifact / resolving node | What it would take to flip to SATISFIED |
|---|---|---|---|---|---|
| **P1** | **Trustee named** — an identified independent holder of the mark | §2 (`[TRUSTEE — to be named]`); Open item (1) | **OPEN** | `GOVERNANCE.md` still carries the literal `[TRUSTEE — to be named]`; `NOTICE` names only the author/copyright holder, no trustee. Holder form + criteria resolved in `docs/GOVERNANCE_OPERATIONALIZATION.md` Part A. | A named legal person/body recorded in §2 and `NOTICE`, accepting the role in writing. **Not self-executable** — requires an external party to consent. |
| **P2** | **Escrow / assignment executed** — the transfer-binding instrument is signed | §2; Status paragraph ("executed legal instrument by counsel"); Open item (2) | **OPEN** (counsel-blocked) | No executed escrow/assignment instrument exists in-repo; the charter is explicitly *"draft for counsel … the final wording is to be executed by counsel."* Draft instrument: `docs/GOVERNANCE_OPERATIONALIZATION.md` Part B. | Counsel-drafted, signed escrow deed (trustee-escrow vehicle, §2) vesting the §4 transfer right in P1's trustee. **Counsel-blocked** — cannot be self-executed inside the repo. |
| **P3** | **§3 irrevocability enforceable** — the one-way ratchet binds as instrument, not prose | §3 | **DRAFT-for-counsel** | The substance is complete and binding-on-publication (§3 enumerates the forbidden capture moves and declares contrary amendments *void*), but enforceability rides on P2: a "void amendment" clause has teeth only inside the executed instrument. Part B §B.3. | P2 executed with §3 incorporated by counsel as an enforceable irrevocable covenant. The text exists today; the binding vehicle does not. |
| **P4** | **All four §4 triggers wired** — each trigger has a defined, checkable condition | §4 (the 1–4 list) | **DRAFT-for-counsel** (3 of 4 specified; 1 depends on P5) | §4 item 1 (change of control), item 2 (relicensing-away-from-OSI), item 4 (bad-faith-capture, trustee's reasonable determination) are each defined as conditions. Item 3 (abandonment) references a cure period whose value is unconfirmed — see P5. Part B §B.4. | Counsel confirms the four triggers as operative conditions of the executed instrument (P2), and §4 item-3's cure period (P5) is filled. The conditions are named; only item 3's parameter and the executing vehicle are missing. |
| **P5** | **§4 item-3 cure period confirmed** — the abandonment trigger has a concrete duration | §4 item 3 ("beyond a stated cure period"); Open item (3) | **OPEN** (self-executable) | The charter says *"a stated cure period"* but states no number; Open item (3) lists it. Objective definition (12-month cadence baseline + 90-day cure) drafted in `docs/GOVERNANCE_OPERATIONALIZATION.md` Part C. | A specific duration written into §4 item 3 and the executed instrument. Self-completable as a drafting decision, but it is a governance commitment, so it belongs with P2/counsel to be binding. |
| **P6** | **§5 self-run conformance / §6 mark grant** — an outsider reproduces the same verdict + hash, and a neutral holder grants the mark on a PASS | §5 (self-run conformance) and §6 (mark usage) | **SATISFIED (mechanism) / DRAFT-for-counsel (mark-grant authority)** | The mechanism is operative and **verified 2026-06-24**: `benchmarks/conformance.py --json` returns `conformant: true` with `result_hash: sha256:3d3b5cf39aaffef23fa8562b` (8 load-bearing checks); the new `benchmarks/attest_conformance.py` runner reproduces it end-to-end (CLAIMABLE true; gate verdict ACCEPT; audit_hash verified true; tamper_detected true) using only a clone (degrades to `capas.decide_external_claim` if `capas_sdk` is absent). A posted verdict is re-derivable with no auth via `POST /api/gate/verify` → `capas.verify_audit_hash` (capas_api.py:102). **Caveat:** the *authority to grant the mark on a PASS* (§6) is not yet vested in a neutral holder — that rides on P1/P2. | Mechanism is SATISFIED now. The mark-grant half flips when P1+P2 vest the granting authority in the neutral holder, so passing the suite confers the mark from the trustee, not the entity. |
| **P7** | **Signed attestation on neutral infra** — "passes on my laptop" → cryptographically attested in public | §5 (re-cert mechanic); §8 (Sonobuoy/Certified-Kubernetes) | **DRAFT-for-counsel / wiring-live** | The CI path is committed: `.github/workflows/conformance.yml` runs the suite on `ubuntu-latest` (neutral infra) and signs the result keyless via Sigstore/cosign (`id-token: write`, `cosign sign-blob`). **Honest gap:** `outputs/conformance_result.sig` / `.pem` are **not in the working tree** — confirming, by design, that the signed attestation is produced by the neutral runner (Rekor transparency log), not committed from a laptop; but it means there is **no committed signed exemplar to point an outside reviewer at yet**. | One green signed run whose `.sig`/`.pem` + Rekor entry are published/linked so an outsider can `cosign verify-blob` independently. **Self-executable now (repo-side):** trigger the workflow and publish the resulting transparency-log reference. |
| **P8** | **Yearly re-certification live** — a real cadence, not just a stated one | §5 ("yearly re-certification to prevent stale forks"); §8 | **OPEN** (self-executable) | The *requirement* is stated (§5) and modeled on Certified Kubernetes (§8), but no scheduled re-cert mechanism is wired: `conformance.yml` triggers are `push` / `pull_request` / `workflow_dispatch` only — **no `schedule:` cron in `conformance.yml`**, and no expiry field in `outputs/conformance_result.json`. *(Note: a `schedule:` cron does exist in the unrelated `scorecard.yml` security workflow; this row's claim is specifically about `conformance.yml`.)* | Add an annual `schedule:` trigger (or a dated expiry in the conformance record) so a PASS carries a 12-month validity and auto-re-runs. **Self-executable** — a workflow edit + a validity field. |

## 2. Roll-up by self-executability

**Counsel-blocked (cannot be made SATISFIED from inside the repo today):**
- **P2** escrow/assignment execution — the keystone; P3 and the binding halves of P4/P6 all hang off it.
- **P1** trustee naming — requires an external party's consent (the project can propose, not unilaterally
  execute).
- **P3** enforceability and the §4 triggers' *binding* status — DRAFT until folded into P2 by counsel.

**Self-executable now (no counsel required):**
- **P5** cure-period value — a drafting decision the project can fix now (Part C drafts it), then ratify in P2.
- **P7** publishing one green *signed* conformance run + its Rekor reference — the pipeline is already
  committed; it needs to be fired and linked.
- **P8** wiring the yearly cadence — a `schedule:` trigger and/or a validity/expiry field in the record.
- **P6 mechanism** — already SATISFIED (`conformance.py` + `attest_conformance.py` reproduce verdict +
  `result_hash`; `/api/gate/verify` re-derives the audit hash).

## 3. The explicit go / no-go rule for promotion

The charter's load-bearing condition is **"neutral, irrevocable governance executed BEFORE adoption."**
Translate to a gate:

> **GO for adoption-promotion** *if and only if* the **mark-control chain is neutral and irrevocable in
> fact** — i.e. **P1 = SATISFIED and P2 = SATISFIED** (a named trustee holds the mark under an executed
> transfer-binding instrument), which in turn makes **P3 and the binding half of P4/P6 = SATISFIED** —
> **AND** the mark's attested meaning is independently reproducible by an outsider — i.e. **P6 mechanism
> SATISFIED (already true) and P7 SATISFIED** (at least one signed, transparency-logged conformance run an
> outsider can `cosign verify-blob`). P5 must be filled (so the abandonment trigger is not dead) and P8
> should be live (so the mark cannot go stale), but P5/P8 are **promotion-blocking only to the extent they
> leave a trigger unwired or the mark unbounded in time.**

**Fail-closed framing (matches CAPAS's own engine):** the charter's verdict on its own operativeness should
be **HOLD, not PASS**, until P1+P2 are executed — because the thing the mark attests to neutrality has no
neutral holder yet. Promoting for adoption while P1/P2 are OPEN reproduces the exact
`entity-owns-engine + entity-owns-mark + entity-sells-product` configuration §7 documents as the capture
trigger. That is a self-inflicted **fail-open**: claiming "governance is in place" before the instrument
that makes it neutral is executed. Per CAPAS scope discipline, the honest status is: **direction is binding
and public; operativeness is NOT yet achieved.**

## 4. Current verdict

| Precondition | State |
|---|---|
| P1 trustee named | **OPEN** |
| P2 escrow/assignment executed | **OPEN** (counsel-blocked) |
| P3 §3 irrevocability enforceable | **DRAFT-for-counsel** |
| P4 four §4 triggers wired | **DRAFT-for-counsel** (3/4 specified; item 3 pending P5) |
| P5 §4 item-3 cure period confirmed | **OPEN** (self-executable; drafted in Part C) |
| P6 §5/§6 attestation third-party-runnable | **SATISFIED** (mechanism) / **DRAFT-for-counsel** (mark-grant authority) |
| P7 signed attestation on neutral infra | **DRAFT-for-counsel / wiring-live** (pipeline committed; no published signed exemplar yet) |
| P8 yearly re-certification live | **OPEN** (self-executable) |

**Adoption-gate verdict: NO-GO (HOLD).** The reproducible-conformance half is real and re-derivable today
(P6 mechanism + P7 pipeline + `/api/gate/verify` + the `attest_conformance.py` runner) — the *technical*
substance of what the mark attests. But the **neutral-holder half is not operative**: with P1 and P2 OPEN,
no neutral party holds the mark under an executed instrument, so "governance executed before adoption" is
**true in stated direction but false in fact.** The gate flips to **GO** when P1 and P2 are executed by
counsel (carrying P3 and the binding halves of P4/P6 with them) and at least one signed conformance
attestation (P7) is published for outside verification; P5 and P8 are filled in parallel and are
self-executable now.

**Single keystone: P2 (executed escrow/assignment).** It is the one act that converts the charter from
*"binding statement of direction"* (its current self-description) to *"operative instrument,"* and it is
the one act the repo cannot perform on its own. Everything else is either already SATISFIED (P6 mechanism),
self-executable now repo-side (P5, P7, P8), or downstream of P2 (P1's binding effect, P3, P4).

---

*Grounding: `GOVERNANCE.md` §1–§8 + Status paragraph / Open items (1)–(3); `benchmarks/conformance.py`
(8-check SUITE) and `outputs/conformance_result.json` (`conformant: true`,
`result_hash: sha256:3d3b5cf39aaffef23fa8562b`); `benchmarks/attest_conformance.py` (run-it-yourself packet,
verified CLAIMABLE true on 2026-06-24); `.github/workflows/conformance.yml` (neutral-infra run + Sigstore
keyless signing; no `schedule:` trigger present — distinct from the cron in `scorecard.yml`);
`capas_api.py:100–102` (`POST /api/gate/verify` → `capas.verify_audit_hash`; accepts bare result or
`{"result": ...}`); `NOTICE` (mark reserved, no trustee named); `docs/GOVERNANCE_OPERATIONALIZATION.md`
(holder form, draft instrument, cure period); `docs/CLAIMS_REGISTRY.md` (no-bare-claims discipline).
DRAFT/OPEN labels reflect repo state on 2026-06-24; no new commitments asserted — only the status of
existing ones.*
