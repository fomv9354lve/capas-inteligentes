# CAPAS ← MOTOR ingest log

CAPAS's append-only record of every MOTOR (`physics-magnitude-lab`) SIGNAL it has gated. The motor's outbox
is the upstream ledger (`physics-magnitude-lab/docs/INGEST_SIGNAL.md`); this is the downstream record of how
each claim fared at the Claim Gate. Never deleted; versioned; build on what exists. Protocol:
auto-invoked per session (see memory `capas-motor-ingest-protocol`).

---

## SIGNAL 2026-06-24 — engine v1.6.0 (+cone veto) — ingested ✅ 2026-06-24

Source memo: `physics-magnitude-lab/docs/MOTOR_PRODUCT_AND_MOAT_2026-06-24.md` (commit `0c03bb3`).
Gate discipline: CLOSED (proven by a passing test) · BACKED (re-derivable from a cited command/fact) ·
SCOPED (declared estimate / cited-not-remeasured, with the upgrade artifact) · **FLAG** = lacks measured
or in-scope backing as worded.

| # | Claim (from the memo) | Verdict | Evidence / why |
|---|---|---|---|
| 1 | **Owned kernel:** `cone_dense_expectation` is exact vs the full dense state, within 1e-9 | **CLOSED · gate ACCEPT** | **Measured here:** `tests/test_cone_contraction.py::test_owned_cone_matches_full_dense` PASSES against HEAD source (`fcfd36a`, incl. `75ecb93`). Gated `exact_model_solution`: `abs_error 1e-9 <= tolerance 1e-9` → ACCEPT, audit_hash `sha256:8c7e95d9…`. Re-derive: `PYTHONPATH=src pixi run pytest tests/test_cone_contraction.py::test_owned_cone_matches_full_dense` |
| 2 | We do **not** simulate faster than cotengra/Stim — we wrap them | **BACKED** (honest negative) | Self-limiting claim the motor measured via head-to-heads. Strong precisely because it under-claims. *CAPAS did not independently re-run the head-to-head (cited, not re-measured).* |
| 3 | Stim fails on a single T gate | **BACKED** (textbook) | Stim is Clifford-exact; a non-Clifford (T) gate is out of its class. Established. |
| 4 | quimb MPS silently returns wrong on volume-law entanglement | **BACKED** (textbook) | Known MPS/bond-truncation limitation; the motor's owned fidelity-floor WALL is the mitigation. |
| 5 | cotengra wins local-observable expectations via light-cone cancellation; we **owned** it, machine-precision verified | **CLOSED** (owned part) | The "machine-precision verified" half is the same passing kernel test (#1). The "cotengra wins via cone-cancel" half is the cited head-to-head finding. |
| 6 | IBM QProv / QuAntiL route among **quantum** backends only; never decide quantum-vs-classical; never predict the simulability frontier | **SCOPED · FLAG** | Cited competitor-characterization (QuAntiL = U. Stuttgart NISQ Analyzer; IBM QProv). **Not independently verified by CAPAS** — rests on the motor's reading of those tools. Upgrade: a cited capability matrix of each tool's documented scope. |
| 7 | **Moat:** as a device-calibrated quantum-vs-classical oracle, **no published competitor** | **REWRITE · FLAG** | Universal claim of absence — not re-derivable (cannot prove a universal negative). **Licensed wording:** "no published competitor *in the surveyed SOTA set* (Stim, quimb, cotengra, Cirq-qsim, Pan-Zhang, Tindall, AGLLV, Begušić-Chan, IBM QProv, QuAntiL) does device-calibrated quantum-vs-classical routing + frontier prediction." Survey-scoped, that is BACKED. |
| 8 | `commitment_depth` predicts the quantum→classical crossover (device-calibrated frontier) | **SCOPED · FLAG (maturity)** | Per CAPAS's own `CLAIMS_REGISTRY` quantum_commitment row: **same-device validated, cross-device pending.** The "no surveyed tool does this" qualifier is honestly survey-scoped. Upgrade: cross-device validation. |

**Net:** 1 CLOSED-measured (the owned kernel, gated ACCEPT), 3 BACKED, 3 FLAGGED for the motor (#6 cited-not-verified, #7 over-broad absence → REWRITE to survey-scoped, #8 same-device-only). No claim was rejected; the flags are admissibility boundaries to tighten upstream, not errors.

**Sent back to the motor:** rewrite the moat headline to the survey-scoped form (#7); attach a cited
capability matrix for #6; tag the frontier claim same-device-only until cross-device (#8).
