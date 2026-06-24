# CAPAS Certification — what the mark means, and how anyone re-derives it

CAPAS's defensible asset is not the code (it's open, Apache-2.0) — it's the **certification mark**, and a
mark is only worth trusting if you never have to trust *us* to check it. So CAPAS certification is
**self-run and re-derivable**: you run the same open suite the certifier runs and get the **same verdict
and the same hash**. The mark attests that a verified artifact passed exactly that — no private process.

## The history (the model this copies)

This is deliberately the **Certified Kubernetes / Sonobuoy** mechanic, not an invented one:

- **Certified Kubernetes (CNCF, 2017–)** — a distribution may use the "Certified Kubernetes" mark only by
  passing a **conformance test the user runs themselves** (the open Sonobuoy tool), submitted by PR, with
  **yearly re-certification** to stop stale forks. The mark is held by a **neutral body (CNCF)**, not the
  vendor — which is why the standard survived every sponsor change. CAPAS copies this directly.
- **SOC 2 (AICPA)** — open criteria, but the right-to-attest is restricted to accredited human auditors.
  CAPAS's determinism makes self-runnable conformance **cheaper than SOC 2's human audit** — the verdict is
  a re-derivable hash, not a firm's opinion. That is an advantage, not a gap.

Lineage in one line: **open criteria (SOC 2) + run-it-yourself conformance + neutral-held mark + yearly
re-cert (Certified Kubernetes) + a deterministic, re-derivable verdict (CAPAS's own twist).**

## The certifications — shown, live, re-derivable

### 1. Self-run conformance — the mark (`CAPAS-CONFORMANT`)

Run it yourself; you get the same result hash on any machine:

```
python3 benchmarks/conformance.py
```

Current result — **8/8 load-bearing invariants pass**, `CAPAS-CONFORMANT`:

| Check | Attests |
|---|---|
| `fail_closed` | a structurally-deficient claim is never accepted |
| `robustness` | survives hostile input; no crash, no false-accept |
| `no_llm_verdict` | no language model in the verdict |
| `quantum_commitment` | the quantum-advantage defeater contract holds |
| `pharma_admissibility` | pharma statistical-admissibility, fail-closed |
| `proof_ledger` | every public claim is CLOSED/BACKED/SCOPED, none bare |
| `hold_has_resolution` | no HOLD is a dead end; each ships a constructive way out |
| `audit_hash_reproduces` | every verdict's audit_hash re-derives + is tamper-evident |

**Re-derivable conformance hash:** `sha256:3d3b5cf39aaffef23fa8562b` — deterministic over the (check, pass)
pairs; the same suite on any machine reproduces it. The hash *is* the attestation, not an opinion.

### 2. Signed, re-derivable admissibility certificate

`capas_certstore.py` issues a **signed, persisted, content-addressed** certificate (the audit artifact a
regulated buyer keeps): `POST /api/certificate`. Anyone checks tamper-evidence with no trust in us:

```
POST /api/certificate/verify      # is this certificate record intact and ours?
POST /api/gate/verify             # re-derive a verdict's audit_hash from the result itself
```

### 3. The mark under binding, neutral governance

The mark is **reserved and pre-committed to neutral governance before adoption** — now a *binding,
irrevocable* instrument (`GOVERNANCE.md`): a one-way ratchet (amendable only toward more neutrality), the
mark in trustee-escrow, transfer-on-trigger if the entity is acquired / relicenses / abandons. This is what
makes the open standard a moat instead of a commodity — the lesson MongoDB/Elastic/HashiCorp/Redis paid for.

### 4. Independent architectural validation (IBM consilience)

IBM's production quantum-calibration stack is, structurally, the same admissibility engine — invariant
checks + threshold gates + fail-closed verdict + a served/withheld data tier. CAPAS run live over the real
155-qubit `ibm_kingston` calibration re-found only the genuine anomalies with **0 false flags**, and its
exact-only discipline caught a residual-ZZ estimate **24× off** IBM's published value. Re-derive:
`examples/kingston_live_audit.py`, `benchmarks/kingston_real_bell_verdict.json`. (Architectural
consilience, not an IBM partnership or endorsement — see `docs/capas_vs_sota_and_ibm.md`.)

## How an artifact gets certified

1. Run `python3 benchmarks/conformance.py` against your CAPAS integration → get the verdict + hash.
2. Issue a signed certificate for your gated claims (`/api/certificate`).
3. The mark attests that artifact passed the *same open suite*; anyone re-runs it and re-derives the hash.
4. Re-certify yearly (the Certified-Kubernetes anti-stale-fork rule).

## What the mark does NOT claim

CAPAS does not determine truth. A conformant verdict means the supplied evidence was checked to *license*
(or not) a specific claim under a declared admissibility contract — deterministically and re-derivably. It
is not a guarantee of correctness, safety, or fitness, and does not replace expert/legal/medical/regulatory
review. A self-consistent fabrication can still pass (the **GIGO ceiling**). See `GOVERNANCE.md`,
`docs/CLAIMS_REGISTRY.md`, `LICENSE` §7–8.
