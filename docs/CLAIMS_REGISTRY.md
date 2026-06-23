# CAPAS Claim Registry

**CAPAS gates its own claims.** Every public number on this site is itself an admissible claim:
`CLOSED` (proven by a passing test), `BACKED` (regenerates from a command, value+hash recorded),
or `SCOPED` (a declared estimate stated with its exact corpus and the artifact that would upgrade it).
Nothing is bare. Run the command in the *Re-derive* column to reproduce the claim yourself.

> Regenerate this file: `python3 benchmarks/generate_claims_registry.py` · release gate: `python3 benchmarks/generate_proof_ledger.py`

| Claim | Where shown | Status | Re-derive / evidence | Honest scope |
|---|---|---|---|---|
| Fail-closed: a structurally-deficient claim is never accepted | Home (“fail-closed (proven)”), Security | **CLOSED** | `python3 benchmarks/verify_fail_closed.py` | Structural invariant (proven). Empirical false-accept RATE on real claims is SCOPED below. |
| Survives hostile input: no crash, no false-accept, injection inert, SSRF bounded | Security, Audit | **CLOSED** | `python3 benchmarks/verify_robustness.py` | 20 adversarial payloads + an internal-URL SSRF probe; worst case is HOLD/REJECT. |
| No language model in the verdict (deterministic) | Home (“no language model in the verdict”), Gate App (LLM in gate: NONE) | **CLOSED** | `benchmarks/verify_cara_decoupling.py (+ audit_hash determinism)` | The product loads and decides with the cognitive layer blocked; same input -> same audit_hash. |
| Quantum-advantage claims past the commitment depth are flagged classically-reproducible | Methodology / quantum domain (capas_quantum_physics.gate_quantum_advantage_claim) | **CLOSED** | `python3 benchmarks/verify_quantum_commitment.py` | The gate CONTRACT is test-locked (the defeater fires iff a hardness claim runs past the depth the device stays uncommitted — the association->causation pattern, quantum edition). The empirical commitment_depth frontier is supplied as evidence: same-device validated (physics-magnitude-lab), cross-device pending. |
| 26 deterministic gates across 10 domains | Home stat bar (26 gates / 10 domains), Methodology | **BACKED** | `python3 benchmarks/generate_capability_matrix.py  → sha256:eca067d7a54a1442eda7c8a9e19803d9…` | 26 gates / 10 domains |
| 1,238 decisions, 78.4% hard-gated | Benchmark (1,238 decisions, 78.4% gated) | **BACKED** | `python3 benchmarks/family_decision_mix.py  → sha256:51b4e31c4c15f261a47c77a203fd6edf…` | SYNTHETIC adversarial decision-space grid (contract coverage), NOT a production drift rate. |
| Pharma statistical-claim admissibility: 3,024-case corpus, 0 false-accepts | Pharma beachhead (capas_pharma.gate_pharma_stat_claim) | **BACKED** | `python3 benchmarks/generate_pharma_corpus.py  → sha256:349286ca67a17dfc0a47767cc17be030…` | SYNTHETIC contract coverage of the statistical-admissibility space Pinnacle 21 skips (significance-vs-alpha, multiplicity, CI-excludes-null, direction, endpoint). NOT a production false-accept rate on real submissions. The beachhead gate; see docs/MARKET_VALIDATION.md. |
| Vendor headline under-states real per-layer error by 2-11x | Home (“Proof on real hardware”, 2–11×) | **BACKED** | `capas_quantum_physics.complete_error_budget(published fields)` | Re-derived from the vendor's OWN published calibration. Worst case is a real anomalous qubit; structured-circuit 3-10x band is Proctor (Nat. Phys. 2022), a cited literature range. |
| pip install capas-claim-gate | Home / README install CTA | **BACKED** | `pip install capas-claim-gate (PyPI; published from GitHub via OIDC Trusted Publishing, no token)` | Published via the publish.yml Trusted Publisher on release v0.1.2; the wheel install is now live. |
| Empirical false-accept / false-reject RATE on real claims | Pilot, Home (n=28 retrospective) | **SCOPED** | 0 false-accepts on the n=28 AGENT-CODED retrospective only | NOT an oracle-adjudicated rate. A well-formed but fabricated-consistent payload can pass (GIGO ceiling). **Upgrades with:** independently-adjudicated real-claim corpus + confusion matrix. |
| Separated 28 retracted-vs-replicated claims by structure | Home + Pilot (28 retracted-vs-replicated) | **SCOPED** | 28/28 on an agent-coded, publicly-known retrospective | Illustrative; the papers were already publicly retracted (no blind adjudication). Demonstrates the contract logic, not blind fraud detection. **Upgrades with:** blind-coded frozen corpus + receipts. |
| At par with a frontier LLM-judge on accuracy; ahead on determinism | Benchmark (vs LLM-judge) | **SCOPED** | `python3 benchmarks/head_to_head_sota.py` | 10-claim corpus; modeled mechanism arms labeled as modeled. **Upgrades with:** larger adjudicated corpus + real competitor runs. |

**Ledger:** 4 CLOSED · 5 BACKED · 3 SCOPED · 0 bare.

### Numbers that are illustrative, not measured
- The Gate App **capacity / savings** widget is a **planning model from your own inputs** (claims × minutes saved × rate) — *planning estimate, not booked savings*. Change the inputs, the number changes.
- The benchmark **1,238 / 78.4%** is a **synthetic adversarial decision-space grid** (contract coverage), not a production drift rate — regenerate with `python3 benchmarks/family_decision_mix.py`.

### What CAPAS does NOT claim
CAPAS does not determine truth. It evaluates whether supplied evidence **licenses** a specific claim under a declared admissibility contract. A well-formed but fabricated-consistent payload still passes (the GIGO ceiling). See the footer disclaimer on every page.
