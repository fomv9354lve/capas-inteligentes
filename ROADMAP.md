# CAPAS roadmap

Honest, ≥1-year horizon. The roadmap is governed by the project's spine: *a claim is admissible only if it
carries a re-derivation command.* It separates what is built from what is owed, and states the structural
ceilings rather than implying they are solved.

## Now / next — the real open debts

- **Gap-1: blind cross-domain adjudication study (n ≥ 500).** The registry, receipts, and SCOPED gating are
  built and pass (`python3 benchmarks/study_assembly.py`); the human-adjudicated study has **not been run**.
  This is the single item that converts self-assertion into an externally-verified rate. Highest priority.
- **CAPAS-gate backing/pointer verification fix.** The pedagogy-governance sprint surfaced a false-admit and an
  over-block traced to backing verification. Fix before publishing any 0-harm rate.
- **PyPI 0.4.0 release.** `pyproject.toml` is at 0.4.0; PyPI live is 0.3.0.

## Security & supply chain

- Pin all GitHub Actions by commit SHA (OpenSSF Scorecard: Pinned-Dependencies).
- Per-file SPDX `SPDX-License-Identifier: Apache-2.0` headers (OpenSSF Gold: copyright/license per file).
- Maintain the threat model ([THREAT_MODEL.md](THREAT_MODEL.md)); periodic security review.
- Dependency policy: minimal runtime deps in `pyproject.toml`, monitored by Dependabot (pip + actions);
  add `pip-audit` to CI.

## Governance

- Name a neutral trustee and execute the mark/escrow — the governance charter is drafted, **not yet executed**.
- Add a **second independent maintainer** (`bus_factor ≥ 2`). This is the honest structural ceiling for
  OpenSSF Silver/Gold and Baseline; no certification sorts it declaratively with a single author.
- DCO sign-off on all commits.

## Engine (research)

- Bridge compiler; closed RLVR loop; conformal calibration of the HOLD threshold.
- Ingest best-of-breed SOTA as substrate (PCN proof-carrying numbers, Mündler-2023 cross-position
  contradiction detection, conformal abstention) — see the internal ingest ledger.

This roadmap is deliberately explicit about what is **not** done; it mirrors the on-site
"what is NOT validated" footer and the validation traceability.
