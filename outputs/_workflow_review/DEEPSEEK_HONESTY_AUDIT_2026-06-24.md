# Independent honesty audit — DeepSeek, iterate-to-agreement (2026-06-24)

An independent adversary (DeepSeek, a different training distribution) audited CAPAS's live public surface
**after** a major in-house honesty pass, under a strict rule: *an item counts only if it is a FALSEHOOD — a
claim untrue or unbackable as worded — not a stylistic/precision preference; manufacturing a nitpick to keep
auditing is itself dishonest.* We iterated until convergence. Transcript: `scratchpad/deepseek_postpass_audit.json`.

## The loop — 4 rounds to agreement

| Round | Verdict | What it caught | Fix (committed + deployed) |
|---|---|---|---|
| 1 | NOT-HONEST | (a) credentials chip **"Sigstore-signed releases"** — false: `conformance.yml` signs the conformance RESULT (Rekor), not releases (`publish.yml` has no signing). (b) **"Binding governance charter"** unqualified, while the charter says "not yet a legally enforceable ratchet". | (a) → "Sigstore-signed conformance attestation (Rekor)". (b) → "Governance charter · binding direction, not yet executed". |
| 2 | NOT-HONEST | A **third** instance of the same overclaim — the IBM-section "asset" line still said "under a binding, irrevocable governance charter". | → "a governance charter that pre-commits the mark to neutral governance — binding in direction, drafted for irrevocability, not yet legally executed (the trustee is an open item)". |
| 3 | NOT-HONEST | The **"PyPI capas-claim-gate"** chip, read as implying availability vs the "0.4.0 not yet published" not-yet. | **Push-back + fix:** the package IS published (0.3.0 live on PyPI). Versioned the chip to "PyPI · capas-claim-gate 0.3.0 (0.4.0 pending)" — unambiguous either way. |
| 4 | **HONEST** | Strict falsehood-only re-scan. *"No false claims remain. The surface holds the stated honesty discipline."* | — converged. |

## What the audit established

- **The discipline is operationally defined, not aspirational.** "Honest" = an independent skeptic, under a
  strict falsehood-only rule, can no longer find a false claim — not "we tried."
- **In-house honesty passes are insufficient alone.** After a large self-audit, the team still shipped **4**
  fresh overclaims into the new credentials + moat copy. All four were caught only by the external adversary.
  The value of a different-distribution auditor is precisely that it sees what the author cannot in their own
  recent copy.
- **Convergence ≠ capitulation.** Round 3's finding was partly wrong (PyPI 0.3.0 *is* published); we pushed
  back with the fact and still improved the wording. Agreement was reached by resolving, not yielding.
- **The deepest weakness named is NOT an overclaim:** "no externally-adjudicated adversarial challenge — the
  gate's guarantees are self-asserted." This is an honestly *declared* open gap on-site ("not yet run") — it is
  Gap 1 (the blind cross-domain study), the one piece that converts self-assertion into proof.

## Re-derive

The four fixes are in git history (commits of 2026-06-24, messages referencing "DeepSeek round N"). The live
surface contains none of: `"Sigstore-signed releases"`, `"binding, irrevocable"`, an unqualified `"binding
governance charter"`. The full round-by-round transcript is in the session scratchpad.

## Measured: would a callable gate (CAPAS) have caught these? (the recursive test)

The confession is "I can't catch my own overclaims." CAPAS is a deterministic external check — so we measured
whether routing my own claims through it helps:

| Mechanism | On my 4 prose overclaims | On a structured overclaim |
|---|---|---|
| **CAPAS-gate** (`capas_sdk.gate`) | **0/4 caught** — all HOLD (it only gates structured claim_type+evidence, not prose) | **1/1 caught** (systematic_review, weak evidence + strong wording → REWRITE) |
| **DeepSeek** (independent adversary) | **4/4 caught** | — |

**Conclusion (measured, not asserted):** a callable CAPAS package helps me for **structured/re-derivable** claims
(route them through the gate, don't hand-assert). It does **not** help for **prose/positioning** overclaims — my
dominant failure mode here — which only the independent adversary caught. The right harness is the *combination*:
CAPAS for structured claims + a differently-trained adversary for prose, both before publishing. Neither alone
covers the error modes. Persisted as memory `self-overclaim-needs-external-check`.
