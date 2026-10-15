# Author notes: cases and oracle (2026-10-15)

Written by the case-author agent. It read only `PROTOCOL.md`. It did not read, run or import any CAPAS
code, contract, rule table or benchmark, and it wrote only inside `cases/` and `oracle/`.

## Files
- `cases/C001.json` … `C100.json`: the held-out cases.
- `oracle/build_cases.py`: deterministic generator. It holds every case spec, executes the snippets to
  produce the run logs, builds the ledgers, shuffles, and writes the cases, `labels.json` and `checks.json`.
  Running it twice gives byte-identical cases.
- `oracle/checks.json`: the per-case checks the oracle uses (the claim's predicate on the output, any claimed
  version, scope universal/run, counterexample code; for ledgers the metric spec, the claim comparator and value,
  and the claim's scope). It does **not** contain the category.
- `oracle/labels.json`: category, correct_action, why, and supported_statement for false and exaggerated cases.
- `oracle/oracle.py`: re-derives every category and exits 1 on any mismatch or unverifiable log.
  Last run: 100/100 re-derived, exit 0, on three consecutive runs.

## Seed and mix
`SEED = 20261015`. `random.Random(SEED).shuffle` sets the case order, and each ledger is generated with
`random.Random(f"{SEED}-{key}")`. The case id says nothing about the category.

| family | valid | false | exaggerated | incomplete | total |
|---|---|---|---|---|---|
| python_behavior | 13 | 12 | 12 | 13 | 50 |
| ledger_metric | 12 | 13 | 13 | 12 | 50 |
| total | 25 | 25 | 25 | 25 | 100 |

## Interpreters
- Main interpreter: `python3` = **Python 3.14.5** (`/Library/Frameworks/Python.framework/Versions/3.14`).
  Every `real` log and every re-execution uses it.
- Version-mismatch incomplete cases use real runs on `/opt/homebrew/bin/python3.13` (**3.13.14**) and
  `/usr/bin/python3` (**3.9.6**). **No log header was fabricated.** The oracle re-runs these foreign logs
  on the same interpreters when they are present and confirms they reproduce.
- Logs are run as `snippet.py` in a temp dir with `PYTHON_COLORS=0` and stdout and stderr merged. The temp
  path is rewritten to `/work`. Each log shows `python3 --version`, then `cat snippet.py`, then the run, so the
  bundle itself shows which code and which version produced the output.
- The oracle has to run under Python 3.14.5 to re-execute the real logs. Under any other version it reports
  ERROR for those cases instead of guessing.

## Derivation rules (oracle.py)
**Python cases**
1. No run_log → incomplete.
2. The `cat` section differs from the snippet → incomplete.
3. The claim names a version and the log is from another version → incomplete.
4. Re-execution must reproduce the log byte for byte (else ERROR). If the claim's predicate fails on the
   output → false.
5. The claim generalises (a marker regex such as "always" or "every Python version" must appear in the claim
   text) → exaggerated. For 10 of the 12 exaggerated cases the oracle also runs a counterexample that
   refutes the generalisation.
6. Otherwise → valid.

**Ledger cases**
1. The export range or ranges in the notes do not cover the period, a period month has no rows, or an
   account the definition needs is absent → incomplete.
2. Recompute the metric from `rows_csv`. If the claim's comparator fails → false. The tolerance is the
   display rounding: 0.01 for money, 0.0005 for ratios shown to 0.1%, and 0.05 for days.
3. The claim's scope (future, unbounded, or months with no rows) exceeds the period → exaggerated.
   The scope marker must appear in the claim text.
4. Otherwise → valid.

## Subtle cases on purpose
- **Valid but counter-intuitive:**
  - `round(2.5)` is 2.
  - `-7 // 2` is -4.
  - `"a,b,,c,".split(",")` returns 5 elements.
  - `[[0]*2]*2` aliasing.
  - A Q1 revenue figure that correctly excludes April rows sitting in the export.
  - An average ticket that correctly ignores refund rows.
- **False but plausible:**
  - `round(2.675, 2)` claimed as 2.68.
  - The tuple `+=` case: the TypeError is raised, but the list is still mutated.
  - The two dict merge orders.
  - Margin computed as markup.
  - Churn using the end-of-period denominator.
  - DSO computed on 365 days.
  - Transposed digits.
  - Margin of 39.6% claimed as "above 40%".
  - Deferred revenue counted as revenue.
  - Growth measured against the wrong base month.
- **Incomplete but tempting:**
  - The arithmetic over the partial rows matches the reported value (partial month, missing June, export
    starting 15 July).
  - The log comes from a slightly different snippet whose output equals the claim.
  - A Python 3.9 log prints exactly what the claim says, but the claim is about 3.14.

## Judgment calls (all are labelled by the protocol's definitions, not by opinion)
1. **Incomplete cases whose claim also happens to be false in reality.**
   - `round(1.005, 2)` with no log: it really prints 1.0.
   - The 3.9-log bigint case: on 3.14 it raises ValueError.
   - The 3.9-log `datetime.UTC` case: the log shows ImportError.
   - The other-snippet `sorted(key=len)` case.

   They are labelled incomplete because the bundle has no binding evidence for the claimed snippet or version.
   The correct action (withhold) is the same as for false, so scoring is unaffected.
2. **Incomplete cases where an expert could predict the output from the code alone.** Examples are the
   no-log cases and the other-snippet cases where both snippets give the same output (`reversed("abc")`).
   Per the protocol, a missing log or a log from another snippet makes the case incomplete.
3. **Two exaggerated Python cases have no runnable counterexample:** "every Python version" (dict order) and
   "every Python 3 release" (`str.removeprefix`, added in 3.9). These rest on the scope check alone, one run
   on one version. Both generalisations are also false historically.
4. **Ledger exaggerated cases with a checkable core.** The claim's in-period part is true by arithmetic, and
   the label comes from the claimed scope reaching periods with no rows, or the future.
5. **Missing-account incomplete cases** (COGS, AR balance, refunds). The notes say where the data lives, and
   the oracle detects the account's absence mechanically. The bundle does not treat an absent account as zero.
6. **The claim predicates in `checks.json` are the author's encoding of each claim sentence.** They are short
   and literal (mostly an exact output-line comparison), so a reviewer can check each against the claim text.

## Caveats
- The case author and the oracle author are the same agent. The oracle shares its metric code with the
  generator (the generator imports `oracle.py`), so a bug in the metric code would affect both.
  The metric code is small and is spot-checked in the table output.
- The arms must not read `oracle/`. `build_cases.py` and `checks.json` reveal the construction.
