# CAPAS — threat model & security assurance case

The security assurance case for CAPAS (OpenSSF Baseline SA-01.01 actors/actions + SA-03.01 assessment;
OpenSSF Best Practices `security_review`, `assurance_case`). It states the trust boundaries, threats, and
how each is mitigated and **tested**. It is re-derivable: every row marked *tested ✓* runs in CI on each push.

## Scope

A deterministic claim-admissibility gate: `claim + structured evidence → ACCEPT / REWRITE / REJECT / HOLD`,
with **no language model in the decision path** and a re-derivable `audit_hash`. Surfaces: a library
(`capas_sdk`), an MCP server, and a hosted API (`POST /api/gate`).

## Actors

- **Claimant** (untrusted) — submits a claim + evidence payload, possibly hostile or fabricated.
- **Reviewer / integrator** (semi-trusted) — runs the gate, reads the verdict + audit trail.
- **Maintainer** (trusted) — merges code, cuts releases.

## Trust boundaries

1. **Payload ingress** (claimant → gate): untrusted JSON.
2. **Gate core**: deterministic rules; no network, no LLM, no eval of payload.
3. **Hosted API** (`/api/gate`): network ingress.
4. **Release / publish** (CI → PyPI via OIDC).

## Threats & mitigations

| Threat | Mitigation | Tested |
|--------|-----------|--------|
| Malformed / hostile payload crashes or false-accepts | Fail-closed gate; schema validation; a structurally-deficient claim is never ACCEPTed | `verify_fail_closed.py`, `test_dynamic_fuzz.py` ✓ |
| Hostile-input battery (None/NaN/inf, oversize, injection) | No crash, no false-accept; injection inert | `verify_robustness.py` (20 payloads) ✓ |
| SSRF via supplied URLs | Bounded; worst case HOLD/REJECT | `verify_robustness.py` (SSRF probe) ✓ |
| Injection via claim text | Gate decides on **structured evidence fields**, not free text; payload is never eval'd/exec'd | `verify_robustness.py` ✓ |
| Tampered verdict | Re-derivable `audit_hash`; any changed load-bearing field diverges the hash | `verify_audit_hash_reproduces.py` ✓ |
| LLM smuggled into the verdict | Cognitive layer decoupled; AST scan asserts no LLM on the decision path; same input → same hash | `verify_cara_decoupling.py` ✓ |
| HOLD as a dead end | Every HOLD ships a machine-readable resolution | `verify_hold_has_resolution.py` ✓ |
| Supply-chain (release) | OIDC Trusted Publishing (no stored token); PEP 740 / SLSA provenance attestations | `publish.yml` |
| Dependency vulnerability | Dependabot (pip + actions); minimal runtime deps | `dependabot.yml` |
| Static-analysis blind spots | CodeQL (`codeql.yml`) + Bandit + Ruff in CI | CI ✓ |

## The irreducible residual (honest)

**The GIGO ceiling stands.** CAPAS gates the *structure* of evidence, not ground truth: a self-consistent,
well-formed, fabricated payload **can pass the gate**. This is a known, disclosed limit — measured by the
fuzz and pedagogy-governance tests, not a defect to patch. CAPAS raises the *cost* of lying; it does not
detect a careful liar. The on-site validation footer states this publicly.

## Review cadence

Last reviewed: 2026-06-24. The *tested ✓* rows re-run in CI on every push (`ci.yml`, `conformance.yml`,
`codeql.yml`); this document is reviewed at each minor release.
