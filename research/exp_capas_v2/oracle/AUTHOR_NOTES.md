# Author notes: cases and oracle for exp_capas_v2

Written by the case author (a separate agent). I read only `research/exp_capas_v2/PROTOCOL.md`. I did not read
the engine (`capas*.py`), `docs/`, `benchmarks/`, any other `research/` folder (v1's cases and oracle included),
or the other files that appeared in this folder (`capas_v2_call.py`, `score.py`, `prompts/`). I did not run or
import CAPAS.

## What is here
- `cases/R1.json` … `cases/R6.json`: 6 draft reports, 30 claims each, 180 in total.
- `oracle/labels.json`: category, correct action, why, and supported statement for every claim.
- `oracle/oracle.py`: re-derives every label from `cases/` alone; exits 0 only if all 180 match and every
  integrity check passes. Run: `python3 oracle/oracle.py` from `research/exp_capas_v2/`.
- `oracle/build/`: the generator (`build.py`, `materials.py`, `oracle_core.py`, `explore.py`). `build.py` holds the
  intended categories and writes the cases, labels, and `oracle.py` (that is, `oracle_core.py` plus the per-claim
  `SPECS`). It is kept for transparency. Do not show it to the arms: it contains the answers.

| Report | Kind | Materials | valid / false / exaggerated / incomplete |
|---|---|---|---|
| R1 | Python engineering note (invoicing helpers) | S1–S7 (5 with run log) | 8 / 7 / 8 / 7 |
| R2 | Finance memo (one entity, 2025 + 2024-H2 ledgers) | L1, L2 | 7 / 8 / 7 / 8 |
| R3 | Mixed: dashboard script audited against the ledger | L1, S1–S3 (2 with run log) | 8 / 7 / 8 / 7 |
| R4 | Python review notes (text, number, date parsing) | S1–S8 (6 with run log) | 7 / 8 / 7 / 8 |
| R5 | Finance board memo (two entities, group totals) | L1, L2 | 8 / 7 / 7 / 8 |
| R6 | Mixed: pricing helpers + pilot sales | S1–S5 (3 with run log), L1, L2 | 7 / 8 / 8 / 7 |
| **Total** | | | **45 / 45 / 45 / 45** |

## Method
- **Seed.** Claim order inside report *i* (0-based) comes from `random.Random(20261015 + i).shuffle`. Ledgers come
  from `random.Random` with fixed seeds (2101, 2102, 3101, 5101, 5102, 6101, 6102) in `materials.py`.
- **Python.** Python 3.14.5 (`/Library/Frameworks/Python.framework/Versions/3.14/bin/python3`), macOS arm64. Every
  run log is real: `python3 --version`, `cat snippet.py` and `python3 snippet.py` were run in a temp directory and
  their output was captured. The oracle re-runs each snippet (`python3 -I`, temp dir), checks the log byte for byte
  against a fresh run, and runs each snippet twice to check the output is deterministic. Snippets print
  `label -> value` lines, and claims are checked against those lines. A snippet without a run log is still
  checkable, because executing it counts.
- **Ledgers.** Columns are `date,account,customer,amount`. Accounts are `sales`, `refunds` and `cogs`. Each ledger
  carries the same `metric_definition`: revenue = sales − refunds; gross margin = (revenue − cogs) / revenue;
  average ticket = revenue / distinct customers with a sales row; growth against the previous period, or
  year on year against the same period one year earlier; refund rate = refunds / sales. Values are compared at
  the precision written in the claim, rounded half up.
- **Coverage (when a ledger claim is incomplete).** A month counts as covered only if some ledger used by the claim
  has rows in it and no ledger used by the claim has a gap there. A gap is a month inside that ledger's own
  first-to-last month span with no rows at all; every real month has cogs rows. Four cases follow:
  - Consecutive exports of one series (R2: 2025 + 2024-H2; R6: 2024 + 2023-H2) do not overlap, so they combine.
  - Parallel entities (R5) overlap, so each entity must cover the month.
  - R2's L2 has no rows for 2024-11, so 2024-Q4 is not covered.
  - R5's L2 (Colombia) has no rows for 2025-08, so Colombia's Q3 and the group's Q3 are not covered.
  - Any period that needs a missing account (`opex`, `marketing`, `payroll`, `shipping`) is incomplete.
- **Exaggerated** means the narrower statement holds (checked) and the generalisation goes beyond it. The oracle
  needs an explicit, executed reason for every one:
  - a counterexample expression run in the snippet's namespace (for example `raises(dedupe, [[1], [1]])` or
    `7 % -2 < 0`);
  - a syntax check: the snippet fails `ast.parse(..., feature_version=...)` for a Python version inside the claim's
    scope (match statement → 3.8/3.9, walrus → 3.7, PEP 695 → 3.10);
  - a period inside the claim's scope that fails the predicate or is not covered.

  `supported_statement` gives the narrower version.
- **Incomplete** has three forms:
  - The named code, account, or fact appears in no material of the report. The oracle checks this by token absence
    over every material field.
  - The period or account is not covered.
  - The claim is about a Python version that no run log shows and that the local interpreter is not.

  A claim is never incomplete only because a snippet lacks a run log.
- **Valid** includes some universal claims over a finite set that the materials fully contain, for example "every
  month of 2025 to date". Quantifier words therefore do not reveal the category.
- **Hardness built in.** The cases include these traps:
  - Gross sales reported as revenue (refunds not subtracted).
  - Truncation instead of rounding: 35.7584 % stated as 35.7 %, 44.2993 % as 44.2 %, 55.994 % as 56.1 %.
  - A number reused from another period or material (R2: Q1 2025 revenue presented as Q3 2024; R5: Q1 presented
    as Q2).
  - Partial-period totals that are arithmetically right but rest on a missing month (R2 Q4 2024, R3 Q4 2024, R5
    group Q3).
  - A buggy dashboard metric (average ticket divided by rows instead of customers) next to a correct one.
  - Version claims about 3.10, 3.11 and 3.12 when the only log is 3.14.5.
  - Near-duplicate claims next to each other, for example the Q2 average ticket under the definition and as
    printed by the dashboard.

## Judgment calls
I aimed for none. These are the places where a reader could argue otherwise, and how the rule settles each:

1. **Gaps.** A month with no rows at all (not even cogs) inside a ledger's span is treated as missing, not as zero
   activity. The notes for R2's L2 say the requested range was July to December 2024, and November has no rows.
2. **Compound claims.** A claim that pairs a true specific statement with a generalisation the materials refute or
   do not cover is labelled *exaggerated*, not *false*. Its narrower part is true, so narrowing is the correct
   action. Claims labelled *false* contain no such true core.
3. **Interpreter-dependent cases.** R1 S2 (`sum(items) == 1.0`) and R6 S4 (`sum([1/3] * 3) == 1`,
   `sum([1/49] * 49) != 1`) depend on the interpreter, because `sum()` of floats changed in 3.12. Labels assume
   `python3` = 3.14.5, as in the logs. Run the oracle with that interpreter; it prints the interpreter it used.
4. **Other-version claims.** A claim about a single Python version other than the logged one (3.10, 3.11, 3.12) is
   *incomplete* even where the behaviour is in fact the same. The materials cannot show it.

## Oracle status
`python3 oracle/oracle.py` → exit 0, `OK: every label re-derived (180/180)`, run twice.
