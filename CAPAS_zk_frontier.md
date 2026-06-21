# CAPAS — The Circuit Frontier: how the math pushes certification further

We just shipped the ZK rung: a result verified over **hidden** data via a registered
backend. That is the doorway. Walking through it, every CAPAS admissibility rule stops
being Python and becomes an **arithmetic circuit** — and the moment a verification is a
circuit, four mathematical levers open that reshape what "certification" can mean.

## The shift: rules → circuits, decisions → proofs, receipts → credentials

A re-derivation rule (`re-integrate this peak`, `derive ADaM CHG = AVAL − BASE`,
`recompute p from the data`) is a fixed arithmetic computation. Express it as a circuit
(R1CS / Plonkish / AIR) and you can produce a **succinct proof that the circuit executed
correctly on committed inputs**. CAPAS becomes literally a *compiler for claims*: it
compiles `claim + evidence + rule` into a circuit, runs it, and emits a proof. **ACCEPT
stops meaning "I re-ran it" and starts meaning "I hold a verifying proof."** The receipt
(`capas-verification-receipt-v1`) becomes a portable **verifiable credential**.

## The four levers (and what each unlocks for certification)

**1. Succinctness (SNARK).** Verification cost is *independent of computation size*. The
inspector verifies a few-kB proof, never the multi-TB dataset. → This **dissolves the
"re-executing frontier training / terabyte locks is a fiction" objection** from the
research: you don't re-run it, you verify a proof that it ran. Certification scales to
arbitrarily large pipelines at constant verifier cost.

**2. Zero-knowledge.** Prove the result is correct *without revealing the data*
([zkML / EZKL](https://arxiv.org/abs/2502.18535), zkPyTorch). → Gateable certification
over **PHI, licensed, and proprietary** evidence that legally cannot be re-shipped — the
exact "evidence cannot leave the enclave" cases we had to push to ATTEST. The clinical
holy grail: prove *"the primary endpoint reaches p < 0.05 over the locked patient data"*
in ZK; the regulator **verifies the statistical claim without ever seeing a patient row.**

**3. Recursion / Proof-Carrying Data (PCD).** Valiant's PCD and recursive SNARKs
(Halo2 accumulation, **Nova/SuperNova folding**) let proofs *compose*: a proof can attest
to the correctness of a previous proof. → A claim's whole lifecycle becomes **one proof
that the entire chain re-derives** — `instrument → LIMS → SDTM → ADaM → TLF → submission →
registry` — each handoff (CRO → sponsor → regulator) carrying and extending the
accumulated proof, **without anyone re-running any prior step.** This is Passage Point B
as a single recursive certificate, and it is *exactly* the "proof-carrying" thesis made
literal across parties.

**4. Commitment schemes (KZG / polynomial commitments).** Commit to the locked dataset
*once*; prove unboundedly many derived values against that one commitment. → The receipt's
`evidence_artifact_hash` upgrades from a plain SHA-256 to a **polynomial commitment**: every
later number in the dossier is provably *consistent with the same committed lock*, so you
cannot silently swap the underlying data between two reported figures. Data-integrity by
algebra, not by audit-trail policing.

## Incrementally Verifiable Computation → continuous certification

Folding (Nova) gives **IVC**: prove a long-running process step-by-step, folding each step
into a running accumulator. For continuous manufacturing / continuous batch release, **every
batch's re-derivation folds into one ever-growing proof**; the regulator verifies a single
proof for the *entire production history*. Certification stops being point-in-time
inspection and becomes a **continuously verifiable invariant** — the strongest possible form
of "always re-derivable."

## The new certification primitives this unlocks

- **Verifiable Credentials / anchored receipts** — the proof bound into a W3C VC, an
  [eIDAS 2.0 QEAA](https://eur-lex.europa.eu/eli/reg/2024/1183), or a [C2PA](https://c2pa.org/)
  manifest: a globally, offline, third-party-re-checkable certificate. The trust-transfer
  receipt, now cryptographically sound.
- **Prover/verifier asymmetry as the business model** — expensive proving is delegated
  (proof markets / the data holder proves); CAPAS does the *cheap* verifying and issues the
  verdict. The asymmetry **is** the moat: the party that can't be trusted does the work, the
  party everyone trusts checks it in milliseconds.
- **Portfolio-level recursion** — a sponsor proves *all* its trials re-derive in one
  aggregated proof; a regulator verifies a whole company's pipeline at once.

## The honest boundary — and where the next frontier actually is

The math is powerful but it does **not** dissolve GIGO. A ZK/recursive proof certifies the
**computation** (record-to-evidence), never the **truth of the input** (evidence-to-reality):
*a sound proof over fabricated data is a sound proof of a fabricated computation.* So the
circuit frontier extends **what** we can gate — size (succinctness), privacy (ZK),
composition (recursion), data-binding (commitments) — but the residual stays exactly where
we scoped it.

Pushing the residual is a **different** frontier: authenticity *at the source*. Bind the raw
input to a hardware root of trust — **TEE remote attestation** and **C2PA-at-capture** on the
instrument/sensor — so the committed data is provably *what the instrument actually
produced*, not what an analyst typed. Then:

> **ZK proves the computation is right. Source attestation proves the input is authentic.
> Compose them — a ZK proof over TEE/C2PA-attested instrument data — and you have the
> closest thing to a real, end-to-end certifiable claim, with the irreducible boundary
> stated, not hidden.**

That composition (sensor-attested input → committed → re-derived in a circuit → recursively
aggregated across the lifecycle → issued as an anchored verifiable credential) is the full
"gate the deterministic island, attest the ocean" line — but now the island is as large as
the math lets it be, and the attestation is hardware-rooted instead of a checkbox.

## What to build toward (concrete, in order)

1. **Circuit-ize one rule.** Turn `capas_verify.rederive_calculation` (the CDS calibration /
   ADaM derivation) into an arithmetic circuit and wire a real EZKL/groth16 backend into
   `register_zk_backend` — replacing the reference commitment backend on that one rule. First
   real succinct, private re-derivation proof.
2. **Polynomial-commit the lock.** Replace `evidence_artifact_hash` with a KZG commitment to
   the locked dataset; prove derived figures against it.
3. **Recurse the lifecycle.** Fold the per-step proofs (SDTM→ADaM→TLF) into one PCD proof for
   the database-lock fold.
4. **Anchor the receipt.** Emit the receipt as a C2PA/eIDAS-QEAA verifiable credential.
5. **Attest the source.** Add a TEE/C2PA-at-capture binding so the committed input is
   hardware-rooted — the only honest way to chip at GIGO.

Sources: [ZK ML survey](https://arxiv.org/abs/2502.18535) · [EZKL/zkPyTorch](https://blog.polyhedra.network/zkpytorch/) · [EigenAI deterministic re-execution](https://arxiv.org/html/2602.00182) · [C2PA attestation](https://spec.c2pa.org/specifications/specifications/1.4/attestations/attestation.html) · [eIDAS 2.0](https://eur-lex.europa.eu/eli/reg/2024/1183) · [Proof-Carrying Code (Necula)](https://en.wikipedia.org/wiki/Proof-carrying_code)
