# Test Policy

CAPAS is a fail-closed claim-admissibility engine; its correctness *is* the product. This policy is
mandatory — it states what testing every change must satisfy, and how the project enforces it in
continuous integration. It is the operational form of the invariants in
[`CONTRIBUTING.md`](CONTRIBUTING.md#the-invariants-a-contribution-must-not-break).

## 1. New functionality requires a test

Every change that adds or modifies behavior **must** ship with a test that exercises that behavior. A
PR that changes the engine's behavior without a corresponding test will not be merged.

- New behavior gets a focused check under `benchmarks/verify_*.py`.
- A bug fix gets a regression test that fails before the fix and passes after it.
- If the change touches a **load-bearing invariant** (see §4), wire the new check into the conformance
  suite so a future regression fails CI, not just a local run.

## 2. The suite runs in CI on every push

The test suite runs on every `push` and every `pull_request`, on neutral infrastructure, via the
real CI workflow [`.github/workflows/ci.yml`](.github/workflows/ci.yml) (job `product-gate`). On each
event CI:

- installs the package (`pip install -e .`) and runs the product/acceptance validators
  (`verify_capas_product_demo.py`, `verify_fresh_clone_install.py`, `verify_external_input_schema.py`,
  `verify_claim_gate_ui.py`, `verify_external_user_validation.py`);
- runs the **conformance suite** (`benchmarks/conformance.py`), and re-runs it under `python -W error`
  (warnings-as-errors);
- runs gate-correctness checks (`benchmarks/verify_gate_no_false_admit.py`) and property-based fuzzing
  (`benchmarks/test_dynamic_fuzz.py`, via Hypothesis) so the gate fail-closes and never crashes on any
  generated input;
- enforces lint on the real-error subset (`ruff check .`; E9/F63/F7/F82 per `pyproject.toml`) and runs
  Bandit static analysis (reporting). Semantic analysis runs separately in
  [`.github/workflows/codeql.yml`](.github/workflows/codeql.yml).

A red CI run blocks merge.

> Environment-sensitive validators (browser E2E, `gh`-auth / release-tag checks) are intentionally
> *not* on per-push CI — a runner has no such environment and they flaked red on every commit. They run
> locally (`python capas.py validate`) and in release workflows; the invariants they cover are also
> locked by the conformance suite. See the trailing note in `ci.yml`.

## 3. Coverage is measured

Test coverage is measured against the engine. New functionality is expected to come with the tests
that cover it (§1); contributors should run coverage locally before opening a PR:

```bash
python -m pip install coverage
coverage run -m benchmarks.conformance && coverage report
```

We report the **actual measured** coverage — we do not assert a threshold a change did not hit. If a
contribution lowers coverage on the paths it touches, add tests until the new code is exercised.

## 4. Load-bearing invariants are locked by `verify_*.py`

The invariants CAPAS cannot break are each pinned by a dedicated verifier and aggregated by the
conformance suite ([`benchmarks/conformance.py`](benchmarks/conformance.py)). A real regression in any
of these fails CI:

| Invariant | Locked by |
|-----------|-----------|
| A structurally-deficient claim is never ACCEPTed (fail-closed / downgrade-only) | [`benchmarks/verify_fail_closed.py`](benchmarks/verify_fail_closed.py) |
| Survives hostile input — no crash, no false-accept | [`benchmarks/verify_robustness.py`](benchmarks/verify_robustness.py) |
| No language model in the verdict path | [`benchmarks/verify_cara_decoupling.py`](benchmarks/verify_cara_decoupling.py) |
| Quantum-advantage defeater contract holds | [`benchmarks/verify_quantum_commitment.py`](benchmarks/verify_quantum_commitment.py) |
| No HOLD is a dead end — each ships a constructive way out | [`benchmarks/verify_hold_has_resolution.py`](benchmarks/verify_hold_has_resolution.py) |
| Every verdict's `audit_hash` re-derives and is tamper-evident | [`benchmarks/verify_audit_hash_reproduces.py`](benchmarks/verify_audit_hash_reproduces.py) |
| Gate makes no false-admit and does not over-block | [`benchmarks/verify_gate_no_false_admit.py`](benchmarks/verify_gate_no_false_admit.py) |

There are additional `benchmarks/verify_*.py` checks (batch/API, cost model, provenance export, fresh
clone install, hosted API, pipeline trace, and more); the table above is the load-bearing core that
the conformance suite gates on every push.

## 5. Running the suite locally

```bash
python -m pip install -e .
python benchmarks/conformance.py              # the load-bearing suite — must stay green
python benchmarks/verify_gate_no_false_admit.py
```

For website changes the design gate must also pass: `python3 designlab/check.py`.
