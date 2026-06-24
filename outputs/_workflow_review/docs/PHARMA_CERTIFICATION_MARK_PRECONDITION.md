# The Pharma Certification-Mark Precondition — What a Sponsor/CRO Relies On Before Adoption

*Governance precondition for the CAPAS pharma beachhead. This document does NOT implement governance; it specifies the attestation contract a sponsor or CRO relies on, instantiated for FDA/PMDA statistical-claim admissibility, and states the precondition that must be satisfied BEFORE adoption. It extends the engine-level charter (`GOVERNANCE.md`) to one named vertical certificate.*

*Every quantitative/structural claim below is re-derivable from a named repo artifact, or is explicitly tagged [FACT] / [CONJECTURE] / [DRAFT] consistent with `docs/MARKET_VALIDATION.md` discipline. Provenance: `docs/MARKET_VALIDATION.md` Thread 2 + Synthesis; `GOVERNANCE.md` §1–§8; `capas_pharma.py`; `benchmarks/conformance.py`; `benchmarks/generate_pharma_corpus.py`; `docs/CLAIMS_REGISTRY.md`; `docs/BEACHHEAD_PHARMA_ONEPAGER.md`. Citations use GOVERNANCE.md section numbers and `capas_pharma.py` rule names (the stable anchors) rather than line numbers.*

---

## 0. Why a precondition, not a feature

A sponsor or CRO cannot truthfully tell a reviewer "this submission passed an independent statistical-claim admissibility gate" unless three things are true *before* they ever run the gate:

1. The mark that licenses the word "independent" is not controlled by the same commercial entity that sells the gate — otherwise "independent" is false on its face.
2. The verdict the certificate attests is re-derivable by anyone (the reviewer included) running the same open tool, not the output of a private process.
3. The certificate states precisely, and narrowly, what it does and does not assert — so it cannot be read as a substantive endorsement of the trial result.

Items 1–3 are *governance preconditions*. If they are not in place, the certificate is a marketing claim, not an attestation, and a regulated buyer's counsel will (correctly) refuse to let it appear in a submission cover letter. This document fixes the contract so the precondition is satisfiable on day one.

The market basis for treating this as the highest-leverage de-risking act, not a nicety, is `docs/MARKET_VALIDATION.md` Thread 2 and Synthesis move (2): *"pre-commit the CAPAS mark to neutral governance before adoption — the single cheapest, highest-leverage de-risking act."* The cautionary corpus that forces it is the relicense→fork record in `GOVERNANCE.md §7` (MongoDB, Elastic→OpenSearch, HashiCorp→OpenTofu/OpenBao, Redis→Valkey; Styra→Apple as the one survivor, because CNCF — not Styra — held the mark).

---

## 1. The attestation contract — what the pharma certificate asserts

A **CAPAS Pharma Statistical-Claim Admissibility Certificate** is a per-claim (or per-claim-set) record that asserts exactly the following, and nothing more:

> The supplied structured evidence for claim `C`, evaluated under the declared admissibility contract of `capas_pharma.gate_pharma_stat_claim`, yielded verdict `V ∈ {ACCEPT, REWRITE, REJECT, HOLD}` with finding set `F`, and this verdict is re-derivable: any party running the same open gate on the same evidence obtains the same verdict and (once the engine-level hashing is wrapped around the pharma adapter — see §1.3) the same `audit_hash`.

### 1.1 What ACCEPT means (and the admissibility dimensions it covers)

An ACCEPT verdict asserts that, for the supplied evidence, the gate found no violation across the admissibility space `capas_pharma.py` checks — the space `docs/BEACHHEAD_PHARMA_ONEPAGER.md` positions as the slot Pinnacle 21 skips (P21 owns *structural CDISC conformance*; CAPAS owns *statistical-claim admissibility*):

| Dimension | Violation → verdict | `capas_pharma.py` rule |
|---|---|---|
| Significance vs alpha | claims "significant" but p ≥ alpha → **REJECT** | `significance_vs_alpha` |
| Multiplicity adjustment | >1 confirmatory comparison, unadjusted → **REWRITE** | `multiplicity_unadjusted` |
| CI excludes the null | CI spans the null while asserting an effect → **REJECT** | `ci_includes_null` |
| Effect direction | claimed direction ≠ observed → **REWRITE** | `effect_direction` |
| Endpoint pre-specification | exploratory/secondary licensing a confirmatory claim → **REWRITE** | `endpoint_not_prespecified` |
| Recompute vs declared p | raw data disagrees with reported p → **REJECT** | `pvalue_rederivation` |

Fail-closed ordering is explicit and most-severe-wins: `REJECT > REWRITE > HOLD > ACCEPT` (`capas_pharma.py` `_SEV`). Missing evidence does not silently pass: a significance claim with no p-value is **HOLD** (`missing_pvalue`), and an empty evidence dict is **HOLD** ("no structured evidence supplied"). This is the fail-closed property `benchmarks/generate_pharma_corpus.py` proves across its corpus (re-derives live to n=3024, 0 deficient claims ACCEPTed; `docs/CLAIMS_REGISTRY.md`, "Pharma statistical-claim admissibility").

### 1.2 What the certificate explicitly does NOT assert — the GIGO ceiling, restated for pharma

The certificate inherits, verbatim in spirit, the "What the mark does NOT claim" clause of `GOVERNANCE.md` and the scope discipline of `docs/CLAIMS_REGISTRY.md`:

- ACCEPT means **the evidence licenses the claim, not that the claim is true** (`capas_pharma.py` GIGO docstring line 17; ACCEPT string line 110). It is not a statement that the drug works, the trial was well-conducted, or the SAP was followed.
- A **well-formed but fabricated-consistent payload can still pass** (the GIGO ceiling, `GOVERNANCE.md` "What the mark does NOT claim"). The certificate raises the cost of an inadmissible claim; it does not detect fraud whose evidence is internally consistent.
- The 3,024-case, 0-false-accept result (`benchmarks/generate_pharma_corpus.py`; `docs/CLAIMS_REGISTRY.md`) is **SYNTHETIC contract coverage**, NOT a production false-accept rate on real submissions. The certificate must not be read as carrying that number into a buyer's real claims.
- It **does not replace** the sponsor's statistician, the SAP, Pinnacle 21, or FDA/PMDA review (`docs/BEACHHEAD_PHARMA_ONEPAGER.md`). It runs **beside** P21, not instead of it.

This narrowness is load-bearing. A certificate that overclaims is worse than none: it invites a regulator to treat a deterministic syntactic check as a substantive endorsement, which neither the gate nor counsel can stand behind.

### 1.3 The certificate's machine form

**[DRAFT — certificate schema, not yet emitted by `capas_pharma.decide()`].** The intended certificate is the existing CAPAS external-decision / verified-artifact shape: `capas_pharma.decide()` already returns a CAPAS-style decision (`{verdict, why, findings, licensed_reuse, domain, alpha}`, `capas_pharma.py` lines 116-124), but it returns **no `audit_hash`** today. The full certificate must additionally carry: `claim_id`, the `audit_hash` of the (gate-version, evidence) pair, the gate/standard version, the conformance result hash of the machine that produced it, and the date.

The `audit_hash` / verify contract this relies on is the **engine-level** one defined in `GOVERNANCE.md §5` (self-run conformance → "the same verdict and the same audit hash", checkable via `POST /api/gate/verify`). The pharma adapter must be **wrapped** to produce that hash; the prose above must not be read to imply `capas_pharma.decide()` emits it today — it does not. Until that wrapper exists, the re-derivable property the certificate can honestly assert is **verdict + finding-set reproducibility** (run the gate twice on the same evidence, get the identical verdict/rule/why), with the hash being the engine-level upgrade that makes the record tamper-evident.

**No certificate field is ever produced by a language model** — the verdict is the deterministic gate's output; the LLM's only role upstream is to *propose* evidence fields, which a human confirms before the gate disposes (the no-LLM-in-the-verdict invariant of `docs/PHARMA_P21_INTEGRATION_SEAM.md`; restated here because the certificate is only trustworthy if that invariant holds).

---

## 2. Who may issue / attest it — the right-to-attest, separated from the seller

This is the precondition's core. The right to issue a CAPAS Pharma certificate must be structured as **archetype (b)** from `docs/MARKET_VALIDATION.md` Thread 2 — *open standard + restricted right-to-attest* (the SOC 2 / Certified Kubernetes family) — not archetype (a) free-standard-paid-platform.

### 2.1 The three roles, deliberately separated

| Role | Who | Holds what |
|---|---|---|
| **Standard + mark owner** | Neutral trustee, then independent foundation | The "CAPAS Pharma Certified" mark and the conformance suite definition (`GOVERNANCE.md §2`: trustee-escrow now → foundation as destination) |
| **Conformance producer** | The sponsor/CRO themselves, or any party | Runs the open gate + `benchmarks/conformance.py` on their own claims; produces the re-derivable verdict (and, once wrapped, hash) |
| **Commercial entity** | The CAPAS company | Sells onboarding, the managed API, the integration seam, support — but **does not own the right to define "certified" or the mark** |

The sponsor/CRO can **self-attest**: because conformance is self-runnable and deterministic (`GOVERNANCE.md §5`; `benchmarks/conformance.py` — *"run-it-yourself, get the SAME verdict + hash … No private process to trust"*), the producer of the certificate is whoever runs the suite, and the reviewer can reproduce it. This is structurally cheaper than SOC 2, where only an AICPA-licensed CPA firm may attest and audits run ~$20k–$150k+/yr ([FACT], web-research-grade anchor in `docs/MARKET_VALIDATION.md` Thread 2). For CAPAS pharma there is **no human auditor in the loop** — the determinism *is* the audit.

### 2.2 Mark-usage rules, instantiated for pharma (mirroring `GOVERNANCE.md §6`)

- **A sponsor/CRO MAY say** their submission claims were "checked with CAPAS" or "CAPAS-pharma-schema-compatible" where true, and MAY attach a re-derivable per-claim verdict record — because anyone can verify it.
- **A sponsor/CRO MAY say** "passed an independent CAPAS statistical-claim admissibility gate" **only** for claims that returned ACCEPT under a conformant run (a PASS from `benchmarks/conformance.py` on the producing machine, plus the gate's ACCEPT). "Independent" is true *because the mark and standard are not owned by the seller* (§2.1) and the verdict is reviewer-reproducible.
- **No party MAY** present a fork, a modified gate, or a service as "CAPAS Pharma Certified" / "official CAPAS" without the mark, which is granted only by passing the conformance suite (`GOVERNANCE.md §6`). A relicensed or altered gate cannot borrow the certificate's credibility.

### 2.3 Yearly re-certification

The mark attests conformance of a *dated* gate version. Per the Certified-Kubernetes mechanic (`GOVERNANCE.md §8`, `docs/MARKET_VALIDATION.md` Thread 2: *"yearly re-certification"*), a CAPAS Pharma attestation is bound to a gate version and re-certified yearly, so a stale fork cannot claim current conformance. For pharma specifically this also tracks evolution of the admissibility contract (e.g., updated multiplicity or endpoint rules) without silently grandfathering old verdicts.

---

## 3. The Certified-Kubernetes mechanic mapped onto a pharma certificate

The mechanic `docs/MARKET_VALIDATION.md` calls *"the directly copyable mechanic (verified)"* maps ~1:1 (and is encoded engine-level in `GOVERNANCE.md §8` and `benchmarks/conformance.py`):

| Certified Kubernetes [FACT] | CAPAS Pharma instantiation | Repo anchor |
|---|---|---|
| Code open | Gate open under Apache-2.0 | `capas_pharma.py`, `LICENSE`, `GOVERNANCE.md §1` |
| Mark used only by passing a conformance test | "CAPAS Pharma Certified" granted only on a conformance PASS + ACCEPT | `GOVERNANCE.md §5–§6` |
| Run with the *same open tool users run* (Sonobuoy) | Sponsor runs the same gate + `benchmarks/conformance.py` the certifier runs | `benchmarks/conformance.py` (the Sonobuoy analog) |
| Submitted by PR + community review | Conformance record + gate changes reviewed in the open; the corpus is regenerable | `benchmarks/generate_pharma_corpus.py`, `docs/CLAIMS_REGISTRY.md` |
| Yearly re-certification | Yearly, bound to gate version | §2.3 above |
| Mark owned by a neutral body (Linux Foundation) | Mark in trustee-escrow now → independent foundation as destination | `GOVERNANCE.md §2` |

The pharma certificate is therefore not a new governance regime — it is the engine charter's §5–§6 conformance/mark mechanic, *named to one vertical certificate* and scoped by `capas_pharma.py`'s admissibility contract.

---

## 4. Why separation must precede adoption — the fork record, applied to pharma

The reason this is a *precondition* (must hold before a sponsor adopts) rather than a roadmap item is the failure corpus in `GOVERNANCE.md §7` / `docs/MARKET_VALIDATION.md` Thread 2 [FACT]:

> **entity-owns-engine + entity-owns-mark + entity-sells-product** is the exact configuration that forked every relicensed project (MongoDB, Elastic→OpenSearch, HashiCorp→OpenTofu/OpenBao, Redis→Valkey). Styra is the one survivor of an acquisition (→Apple, 2025) *because CNCF, not Styra, held the mark.*

Applied to pharma: a sponsor that builds a certificate produced by CAPAS into its FDA/PMDA submission motion is taking a multi-year dependency. If the CAPAS company is later acquired, pivots, or relicenses the core to capture value, and it *also* owns the mark, then the sponsor's standing claim — "passed an independent admissibility gate" — collapses retroactively, exactly when a submission is in flight. The whole point of the irrevocable charter (`GOVERNANCE.md §3`, the one-way ratchet; §4 trigger/transfer on acquisition or relicensing without the entity's consent) is that **the standard and its mark do not follow the entity into capture** (`GOVERNANCE.md §4`). A regulated buyer can only rely on the certificate if that ratchet is in place *first*. Hence: **pre-commit, then offer to pharma — never the reverse.**

This is also why the certificate's "independent" wording is only honest once §2.1's separation is executed. Until the trustee is named and the escrow signed (`GOVERNANCE.md §2`, "Vehicle (effective now): trustee-escrow", with open items: *(1) name the trustee; (2) execute the escrow/assignment with counsel; (3) confirm the cure period*), the strongest truthful claim is the binding *statement of direction*, not a fully operative independent mark. A design partner can run the gate and reproduce verdicts today; the word "independent" in a submission-facing attestation is licensed only once the escrow is operative.

---

## 5. The legal-strength honesty clause — CONJECTURE, stated plainly

Per `docs/MARKET_VALIDATION.md` Thread 2, the enforceability of this gatekeeping rests on **certification-mark trademark law** — and this must be stated to a sponsor/CRO without inflation:

> CAPAS's reserved-mark plan is archetype (b)… But CAPAS lacks SOC 2's legal moat (CPA licensure); its gatekeeping rests on certification-mark trademark law — **enforceable but weaker (CONJECTURE).** *(`docs/MARKET_VALIDATION.md` Thread 2.)*

So the honest precondition statement to a buyer is:

- The mark is **enforceable** as a certification mark: a third party who labels a non-conformant gate "CAPAS Pharma Certified" can be challenged on trademark grounds, and the certificate's verdict is reviewer-reproducible (so misuse is detectable).
- But the gatekeeping is **weaker than SOC 2's**: SOC 2's right-to-attest is backstopped by CPA *licensure* (a statutory professional gate); a certification mark is backstopped only by trademark enforcement, which is real but thinner ([CONJECTURE], per the source — CAPAS has not litigated it and the strength is unproven). CAPAS's compensating strength is **determinism**: unlike SOC 2, the verdict can be independently recomputed, so a false "certified" claim is *detectable by anyone*, not just by an auditor — which shifts some of the enforcement burden from law to reproducibility.

No claim is made that this gate carries regulatory force with FDA/PMDA. It does not. It is a deterministic, reproducible second check whose certificate a sponsor *may* cite to evidence diligence — never something a regulator is bound to accept.

---

## 6. The precondition, stated as a checklist (what must be true before a sponsor/CRO adopts)

A sponsor/CRO can rely on "passed an independent CAPAS statistical-claim admissibility gate" **iff all of the following hold** — this is the precondition this document defines:

1. **Mark separated from seller.** The CAPAS Pharma mark is under the trustee-escrow / foundation governance of `GOVERNANCE.md §2`, with the irrevocability ratchet (§3) and acquisition/relicense triggers (§4) executed. *(Open items: `GOVERNANCE.md §2` — name trustee, execute escrow with counsel.)*
2. **Verdict re-derivable.** The certificate carries a verdict (and, once the pharma adapter is wrapped per §1.3, an `audit_hash`) reproducible by the reviewer via the same open gate and `benchmarks/conformance.py`, verifiable through the engine-level `POST /api/gate/verify`. No private process. *(`GOVERNANCE.md §5`.)*
3. **Scope clause attached.** The certificate states it asserts *admissibility licensing, not truth*; acknowledges the GIGO ceiling; and disclaims replacing the statistician, SAP, P21, or regulatory review. *(§1.2; `capas_pharma.py` line 17; `GOVERNANCE.md` "What the mark does NOT claim".)*
4. **No LLM in the verdict.** Every certificate field traces to the deterministic gate; an LLM may only propose evidence a human confirms. *(§1.3.)*
5. **Synthetic-vs-real labeled.** The certificate does not import the 3,024-case 0-false-accept SYNTHETIC figure as a production rate. *(§1.2; `docs/CLAIMS_REGISTRY.md`.)*
6. **Legal-strength disclosed.** The buyer is told the mark rests on certification-mark trademark law (enforceable, weaker than SOC 2's CPA licensure — CONJECTURE), with determinism as the compensating control. *(§5.)*
7. **Yearly re-cert bound to version.** The attestation names the gate version and is re-certifiable yearly. *(§2.3.)*

If 1–7 hold, the certificate is an honest attestation a sponsor's counsel can stand behind beside Pinnacle 21. If any fails, the strongest truthful claim regresses to "checked with the open CAPAS gate; verdict reproducible" — true, useful, but *not* "independent certified."

---

*This document specifies the attestation contract and its precondition only. It does not name the trustee, execute the escrow, or register the mark — those are the open items in `GOVERNANCE.md §2` (counsel-executed) and are out of scope here by design: the precondition is defined so that the pharma certificate becomes citable the moment the engine-level charter is made operative for this vertical, and the `audit_hash` wrapper (§1.3) is built around the pharma adapter.*
