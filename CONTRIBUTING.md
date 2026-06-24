# Contributing to CAPAS

Thanks for helping. CAPAS is an open-core reference implementation of a deterministic claim-admissibility
engine; contributions are welcome under the rules that keep it trustworthy.

## The invariants a contribution must not break

These are not style preferences — they are what CAPAS *is*. A PR that breaks one will not be merged:

1. **No language model in the verdict path.** LLMs may draft or extract candidate evidence *outside* the
   gate; the verdict is deterministic and re-derivable. Same input → same verdict → same `audit_hash`.
2. **Fail-closed / downgrade-only.** A structurally-deficient claim is never ACCEPTed. New gates may only
   downgrade (ACCEPT→REWRITE/REJECT/HOLD), never upgrade.
3. **Every public claim is admissible.** If you add a headline claim or a number, it must be `CLOSED`
   (proven by a test), `BACKED` (regenerates from a command), or `SCOPED` (a declared estimate with its
   corpus) — never bare. Add it to `benchmarks/generate_proof_ledger.py`; the registry regenerates.
4. **No network calls in the browser gate;** the CLI/API is the provenance-verification path.

## Setup, test, and the bar to merge

```bash
python -m pip install -e .
python benchmarks/conformance.py     # the load-bearing suite — must stay green (6/6)
```

- **Add a test for new behavior** (`benchmarks/verify_*.py`), and wire it into the conformance suite if it
  is load-bearing.
- **Run the conformance suite locally** before opening a PR; CI re-runs it on neutral infra and
  Sigstore-signs the result.
- For website changes, the design gate must pass: `python3 designlab/check.py`.
- Keep `docs/CLAIMS_REGISTRY.md` and `docs/proof_ledger.json` regenerated if you touched a claim.

## Sign your commits (DCO)

CAPAS uses the [Developer Certificate of Origin](https://developercertificate.org) (DCO 1.1) as a
lightweight, per-commit attestation of provenance — the same model the Linux kernel and the CNCF use. It
fits the project's spine: every contribution carries an explicit, auditable claim about where it came from.

Every commit must be **signed off**. The sign-off is a single trailer line added by `-s`:

```bash
git commit -s -m "Your message"
```

This appends a `Signed-off-by` trailer using your `user.name` / `user.email` from git config:

```
Signed-off-by: Jane Doe <jane@example.com>
```

By adding that line you certify the four points of the DCO — that you wrote the work or otherwise have the
right to submit it under the project's open-source license. The full text is in [`DCO.md`](DCO.md) and at
<https://developercertificate.org>.

Notes:

- Use a real name and a reachable email; they must match the commit author.
- Forgot to sign off the last commit? `git commit --amend -s --no-edit`. For an existing branch:
  `git rebase --signoff <base>`.
- A PR with unsigned commits will be asked to re-sign before merge.

## Pull requests

- Branch from `main`, keep PRs focused, describe what invariant your change touches and how you verified it.
- **Sign off every commit (DCO):** `git commit -s` — see [Sign your commits (DCO)](#sign-your-commits-dco)
  above. This certifies you have the right to submit the work under the project license.
- **Add a test for new functionality** and keep the suite green — see [`TEST_POLICY.md`](TEST_POLICY.md).
- By contributing you agree your contribution is licensed under **Apache-2.0** (see `LICENSE`). The CAPAS
  name and certification mark are reserved under neutral governance (see `GOVERNANCE.md`); contributions do
  not grant rights to the mark.

## Reporting problems

- Bugs / features: open a GitHub issue.
- **Security vulnerabilities: do NOT open a public issue** — see [`SECURITY.md`](SECURITY.md).
- Be respectful; see [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).
