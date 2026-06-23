# CAPAS Governance & Certification-Mark Charter

*This charter exists because the market research was unambiguous: the single highest-leverage move for an
open-standard is to **separate the standard/mark from the commercial entity before adoption**, not after.
Below is the commitment, and the evidence that forced it.*

## The commitment (binding intent)

1. **The CAPAS engine, schema, calculus, reference gate, CLI, tests, and benchmark corpus are open**
   under Apache-2.0 (see `LICENSE`). They will not be relicensed to a source-available / non-OSI license
   to capture value. That move is the documented #1 trust-killer (see the record below) and is renounced.

2. **The CAPAS name and the official certification/conformance mark are reserved** (see `NOTICE`) and
   are intended to be **placed under neutral governance** (an independent foundation or a published,
   **irrevocable** certification-mark charter) **before** CAPAS is promoted for adoption — not after.
   Neutrality is what lets the standard survive the commercial entity being acquired, pivoting, or dying.

3. **Conformance is self-runnable and deterministic.** Anyone may run the same open conformance suite the
   certifier runs and obtain the **same verdict and the same audit hash**. The mark attests that a
   verified artifact passed that suite — it never requires trusting a private process. (Mechanic modeled
   on Certified Kubernetes / Sonobuoy: open tool, run-it-yourself, PR-submitted, **yearly
   re-certification** to prevent stale forks.)

4. **You may say** software is "built with CAPAS" or "CAPAS-schema-compatible" where true. **You may not**
   present a fork or service as "CAPAS", "CAPAS-certified", or "official CAPAS" without the mark.

## What the mark does NOT claim

CAPAS does not determine truth. A CAPAS-conformant verdict means the supplied evidence was checked to
**license** (or not license) a specific claim under a declared admissibility contract — deterministically
and re-derivably. It is not a guarantee of correctness, safety, or fitness, and does not replace expert,
legal, medical, scientific, or regulatory review. A well-formed but fabricated-consistent payload can
still pass (the GIGO ceiling). See the disclaimer on every page and `LICENSE` §7–8.

## Why — the open-core fork record (the disclaimer, hardened)

Every project that relicensed its open core to capture value triggered a neutral-foundation fork that
stranded the original; reversals did not restore trust. This is the failure mode this charter exists to
make structurally impossible for CAPAS:

| Project | What happened | Result |
|---|---|---|
| **MongoDB** | Apache → SSPL (2018) | OSI ruled it non-open; distros dropped it; reputational hit |
| **Elastic** | Apache → SSPL (2021) | AWS forked **OpenSearch**; Elastic **reverted to AGPL (2024)** |
| **HashiCorp** | MPL → BSL (2023) | Community forked **OpenTofu** / **OpenBao** under the Linux Foundation |
| **Redis** | BSD → SSPL (2024) | Forked as **Valkey** (LF; ~83% of large users testing within a year); Redis reverted 2025 — "bridges burned" |
| **Styra / OPA** | Company acqui-hired by Apple (2025) | **The standard survived — because CNCF, not Styra, held the mark.** The model to copy. |

The lesson the evidence forces: **entity-owns-engine + entity-owns-mark + entity-sells-product** is the
exact configuration that forks every project. CAPAS pre-commits against it.

## Precedents this charter follows

- **Certified Kubernetes** — open code; the mark may be used only by passing a conformance test run with
  the *same open tool users run themselves*; LF owns the mark; yearly re-certification. (Directly copied.)
- **SOC 2** — open criteria, restricted right-to-attest (only accredited firms issue). CAPAS's
  determinism makes self-runnable conformance cheaper than SOC 2's human audit — an advantage, not a gap.

---

*Status: intent charter. The neutral-governance vehicle (foundation vs. irrevocable charter + trustee)
is to be selected before public launch. Until then this document is the binding statement of direction.*
