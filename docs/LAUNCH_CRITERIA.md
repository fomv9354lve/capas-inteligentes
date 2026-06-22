# Launch criteria — how the audit loop terminates

Adversarial audits are unbounded: each one says "reduce / hedge / delete", and optimizing to
survive *any* audit converges to a blank page. That is a failure mode, not rigor. We replace
"survive the next audit" with a **finite, objective bar** — and we resolve findings by
**strengthening or closing**, not reducing.

## The bar: every headline claim is CLOSED, BACKED, or SCOPED — none bare

| Status | Meaning | How it terminates the audit |
|---|---|---|
| **CLOSED** | A structural/mathematical truth locked by a passing test (cannot regress). | A test proves it; an auditor can re-run the test, not demand more. |
| **BACKED** | Regenerates from a command, recorded with its value + sha256 (+ CI). | The number *is* its artifact; "show me the source" is already answered. |
| **SCOPED** | Empirical-pending, stated with its exact corpus **and the artifact that would upgrade it**. | The claim already concedes precisely what it does not prove. |

**The terminator principle:** a claim that names its own evidence *and* its own limit is
audit-complete. A further audit can only repeat what the claim already concedes.

## The release gate (encoded, runs in CI)

`benchmarks/generate_proof_ledger.py` regenerates every claim's backing and **fails the build** if
any claim is bare or any CLOSED/BACKED backing breaks. Rule: **no site metric ships without a
proof-ledger entry.** The ledger is published at `docs/proof_ledger.json`.

## Worked example — the most dangerous claim, strengthened not reduced

"0 false-accepts" read as a general empirical guarantee → an auditor kills it ("I send a
consistent-but-fabricated payload; if it accepts, the claim is dead"). We did **not** delete it.
We split it:

- **Structural part → CLOSED.** `benchmarks/verify_fail_closed.py` proves that a
  structurally-deficient claim (unsupported type, missing evidence, or a domain-invariant
  violation across all 10 domains) is **never** ACCEPTed — 18/18, locked by a test. The site now
  says "fail-closed (proven invariant)", which is *stronger* and unkillable.
- **Empirical part → SCOPED.** The false-accept *rate on real claims* needs an oracle; it is
  stated as pending an independently-adjudicated corpus, with the GIGO ceiling named (a well-formed
  liar can pass). The upgrade artifact is named in the ledger.

Same for the rest: `11×` became `2–11× (BACKED, range, worst-case labeled)`; `28/28` became
`SCOPED (illustrative, agent-coded)`; `1,238` is `BACKED (synthetic grid + hash)`.

## Launch when

1. Proof-ledger release gate is green (every claim CLOSED/BACKED/SCOPED, backings pass).
2. The boundary ("CAPAS checks consistency, not truth") is above the fold.
3. `pip install` is either published or the copy reflects its real state.

When those hold, **launch** — and stop auditing for "less", because every claim is already
complete on its own terms.
