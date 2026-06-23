# Security Policy

## Reporting a vulnerability

**Please report privately — do not open a public issue for a security problem.**

Use **GitHub private vulnerability reporting**: the repository's **Security** tab → **Report a
vulnerability**. This opens a private advisory visible only to the maintainers.

We aim to **acknowledge within 5 business days** and to agree on a disclosure timeline with you. Credit
is given to reporters who want it. If GitHub private reporting is unavailable to you, open a minimal
public issue asking for a private contact channel (without details) and we will follow up.

## What is in scope

CAPAS is a deterministic gate; its security properties are testable and we treat regressions in them as
vulnerabilities:

- **Fail-closed break** — any input that causes a structurally-deficient claim to be **ACCEPTed**
  (the core invariant; covered by `benchmarks/verify_fail_closed.py`).
- **Crash / unhandled exception** on hostile input instead of a verdict
  (`benchmarks/verify_robustness.py`).
- **Code execution / injection** — a claim/evidence string that executes instead of being stored inert.
- **SSRF / unbounded fetch** — the optional provenance-URL fetch reaching internal addresses or hanging.
- **Determinism break** — the same input yielding a different verdict or a different `audit_hash`, or any
  path that lets a language model influence the verdict.
- **Supply chain** — tampering with the published wheel, the conformance result, or its Sigstore signature.

## What is NOT a vulnerability (by design, documented)

- A **well-formed but fabricated-consistent** payload passing the gate. CAPAS checks whether evidence
  *licenses* a claim, not whether the claim is true — this is the **GIGO ceiling**, stated openly on every
  surface. It is a known, documented limit, not a flaw.
- ACCEPT meaning "the evidence licenses the claim." It is never a guarantee of truth, safety, or fitness.

## Supported versions

The latest release on `main` is supported. CAPAS is research software provided under Apache-2.0 with no
warranty (see `LICENSE` §7–8); operators are responsible for their use of the verdicts.
