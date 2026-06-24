# CAPAS Governance & Certification-Mark Charter

*This charter exists because the market research was unambiguous: the single highest-leverage move for an
open standard is to **separate the standard/mark from the commercial entity before adoption**, not after.
This document is the **binding, irrevocable instrument** that does it. It is written for legal review
(`draft for counsel` — the structure is the commitment; the final wording is to be executed by counsel),
but it takes effect as a binding statement of direction on publication.*

## 1. Open core (Apache-2.0) — renounced relicensing

The CAPAS engine, schema, calculus, reference gate, CLI, tests, and benchmark corpus are open under
Apache-2.0 (see `LICENSE`, `THIRD_PARTY_NOTICES.md`). They **will not be relicensed** to a
source-available / non-OSI license to capture value. That move is the documented #1 trust-killer (see the
record in §7) and is **irrevocably renounced** by this charter (§3).

## 2. The certification mark — reserved, then placed under neutral governance

The CAPAS name and the official certification/conformance mark are reserved (see `NOTICE`). This charter
pre-commits them to neutral governance **before** CAPAS is promoted for adoption — the one move that lets
the standard survive the commercial entity being acquired, pivoting, or dying.

**Vehicle (effective now): trustee-escrow.** The mark is placed in escrow with an independent trustee
(`[TRUSTEE — to be named]`) who holds the transfer right defined in §4. This is the executable-today
vehicle (the Certified-Kubernetes pattern without waiting on a foundation). **Destination:** assignment
to an independent foundation (Linux Foundation–style) is the migration target; until then the trustee
holds the mark in trust under these terms.

## 3. Irrevocability (the one-way ratchet)

The commitments in §1, §2, §4, and §5 are **irrevocable** and may be amended **only in the direction of
greater neutrality and openness, never less**. Specifically: this charter may not be amended to relicense
the core away from an OSI-approved license, to return the mark to the unconstrained control of the
commercial entity, to remove the self-run conformance right (§6), or to weaken the trigger/transfer terms
(§4). Any purported amendment that does so is void. This is the structural difference from every project
in §7: the capture move is not *discouraged* — it is made *impossible by the instrument*.

## 4. Trigger events and transfer

On any of the following **trigger events**, the trustee transfers the mark to the neutral destination (§2)
or a successor independent trustee, and the transfer is not subject to the commercial entity's consent:

1. **Acquisition / change of control** of the commercial entity that owns the engine.
2. **Relicensing** of the open core away from an OSI-approved license (or any attempt to).
3. **Abandonment** — the engine/standard goes unmaintained beyond a stated cure period.
4. **Bad-faith capture** — any attempt to use the mark to extract value in a way that contradicts §1–§3,
   at the trustee's reasonable determination.

The intent is explicit: **the entity may be sold, pivot, or die; the standard and its mark do not follow
it into capture.**

## 5. Self-run, deterministic conformance

Conformance is self-runnable and deterministic. Anyone may run the same open conformance suite the
certifier runs (`python3 benchmarks/conformance.py`) and obtain the **same verdict and the same audit
hash** — a verified artifact can be checked with `POST /api/gate/verify`. The mark attests that a verified
artifact passed that suite; it never requires trusting a private process. (Mechanic modeled on Certified
Kubernetes / Sonobuoy: open tool, run-it-yourself, PR-submitted, **yearly re-certification** to prevent
stale forks.) This right is irrevocable under §3.

## 6. Mark usage

**You may say** software is "built with CAPAS" or "CAPAS-schema-compatible" where true. **You may not**
present a fork or service as "CAPAS", "CAPAS-certified", or "official CAPAS" without the mark, granted only
by passing §5.

## What the mark does NOT claim

CAPAS does not determine truth. A CAPAS-conformant verdict means the supplied evidence was checked to
**license** (or not license) a specific claim under a declared admissibility contract — deterministically
and re-derivably. It is not a guarantee of correctness, safety, or fitness, and does not replace expert,
legal, medical, scientific, or regulatory review. A well-formed but fabricated-consistent payload can
still pass (the GIGO ceiling). See the disclaimer on every page and `LICENSE` §7–8.

## 7. Why — the open-core fork record (the failure mode this instrument forbids)

Every project that relicensed its open core to capture value triggered a neutral-foundation fork that
stranded the original; reversals did not restore trust. §3 makes this structurally impossible for CAPAS:

| Project | What happened | Result |
|---|---|---|
| **MongoDB** | Apache → SSPL (2018) | OSI ruled it non-open; distros dropped it; reputational hit |
| **Elastic** | Apache → SSPL (2021) | AWS forked **OpenSearch**; Elastic **reverted to AGPL (2024)** |
| **HashiCorp** | MPL → BSL (2023) | Community forked **OpenTofu** / **OpenBao** under the Linux Foundation |
| **Redis** | BSD → SSPL (2024) | Forked as **Valkey** (LF; ~83% of large users testing within a year); Redis reverted 2025 — "bridges burned" |
| **Styra / OPA** | Company acqui-hired by Apple (2025) | **The standard survived — because CNCF, not Styra, held the mark.** The model this charter copies. |

The lesson the evidence forces: **entity-owns-engine + entity-owns-mark + entity-sells-product** is the
exact configuration that forks every project. This charter pre-commits against it — irrevocably, before
adoption, while it is still free to do so.

## 8. Precedents this charter follows

- **Certified Kubernetes** — open code; the mark may be used only by passing a conformance test run with
  the *same open tool users run themselves*; a neutral body owns the mark; yearly re-certification.
- **SOC 2** — open criteria, restricted right-to-attest. CAPAS's determinism makes self-runnable
  conformance cheaper than SOC 2's human audit — an advantage, not a gap.

---

*Status: **binding statement of direction, effective on publication.** Vehicle: trustee-escrow (§2),
operative once `[TRUSTEE — to be named]` is named and the escrow is executed; foundation assignment is the
destination. The irrevocability (§3) and trigger/transfer terms (§4) are the load-bearing commitments and
are to be finalized in an executed legal instrument by counsel. This document is that instrument's
substance and the public, binding pre-commitment in the interim.*

*Open items before this is fully operative: (1) name the trustee; (2) execute the escrow/assignment with
counsel; (3) confirm the cure period for the "abandonment" trigger (§4.3).*
