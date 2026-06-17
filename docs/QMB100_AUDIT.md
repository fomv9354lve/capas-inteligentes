# QMB100 / PhysVEC Audit Against CAPAS

Status: paper-level audit.

Primary source:

- Towards Verifiable and Self-Correcting AI Physicists for Quantum Many-Body
  Simulations, arXiv:2604.00149, https://arxiv.org/abs/2604.00149

## What QMB100 / PhysVEC Clearly Covers

QMB100/PhysVEC is close SotA for the CAPAS domain. It is not generic workflow
provenance; it is quantum many-body simulation.

From the paper:

- QMB100 / QMP-Bench contains 100 end-to-end research-level quantum many-body
  tasks from 21 high-impact articles.
- Task categories include tensor-network/DMRG with ITensors, neural-network
  ansatz with NetKet, quantum circuits with Qiskit, and DFT with ORCA.
- PhysVEC includes a programming verifier and scientific verifier.
- The scientific verifier uses rubric tests, physical assertion tests, and
  convergence tests.
- Physical assertions include limiting-case, symmetry, and analytical tests.
- The system provides human-auditable evidence at each stage.

This means CAPAS must not claim novelty for:

- quantum-many-body benchmark tasks,
- verification/error-correction for AI physicists,
- physical assertions,
- convergence testing,
- end-to-end reproduction of paper figures,
- human-auditable evidence in quantum many-body agent workflows.

## What Was Not Found In The Paper

The paper does not show, at least at paper level:

- RO-Crate export per run,
- W3C PROV export per run,
- a first-class physical evidence entity in a provenance package,
- an explicit `physical_evidence_level` taxonomy matching analytic/cross_sim/none/failed/rejected,
- explicit `verification_independence` metadata,
- explicit `evidenceStatus` for no-evidence, failed, and rejected states.

The paper's evidence appears workflow/verifier-centered: it supports scientific
validity through rubrics, assertions, and convergence checks. CAPAS is artifact-
centered: it packages each run as a trace/crate with explicit evidence metadata.

This is not proof of absence in code or data. It is the current finding from the
public arXiv paper.

## Direct Comparison

| Capability | QMB100 / PhysVEC | CAPAS |
|---|---|---|
| Quantum many-body benchmark | yes | not claimed |
| End-to-end paper reproduction | yes | not claimed |
| Programming verifier | yes | no |
| Scientific verifier | yes | partial via evidence fields |
| Physical assertions | yes | represented as evidence/invariant when present |
| Convergence testing | yes | not currently implemented |
| Human-auditable evidence | yes | yes |
| RO-Crate per run | not found in paper | yes |
| PROV per run | not found in paper | yes |
| First-class physical evidence entity | not found in paper | yes |
| Evidence status for failed/rejected/no-evidence | not found in paper | yes |
| Witness independence metadata | not found in paper | yes |

## Positioning Impact

QMB100 is the closest known work to CAPAS in the target domain. It narrows CAPAS
more than SciAgentGym does because it targets quantum many-body directly.

The remaining CAPAS position is complementary:

> QMB100/PhysVEC verifies and corrects AI-driven quantum many-body research
> workflows. CAPAS packages the evidence state of a run into RO-Crate/PROV with
> explicit physical evidence, witness independence, and honest no-evidence,
> failure, and rejection states.

Potential integration:

- Use QMB100 tasks as benchmark workload sources.
- Use PhysVEC-style verifier outputs as evidence inputs.
- Emit CAPAS RO-Crates for each task attempt.

## Falsation Condition

Revise CAPAS positioning if QMB100/PhysVEC releases traces or code that include
per-run RO-Crate/PROV exports with first-class physical evidence entities,
witness-independence metadata, and explicit no-evidence/failed/rejected states.
