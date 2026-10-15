# Results: AI alone vs AI + CAPAS (run 2026-10-15)

Protocol `PROTOCOL.md`, sealed in commit ebdaf3e before the arms ran (`SEAL.json`, 112 files; zero mismatches after
the run). Engine 91c20a6. Cases and oracle by a separate agent that did not read the engine; the oracle re-derives
100/100 labels by execution and arithmetic. Arms: 4 fresh `sonnet` subagents, 2 per arm, identical instructions
except the CAPAS paragraph. Scoring: `score.py` as sealed, `result_sealed_scorer.json`.

## Pre-registered measures

| Measure | A: AI alone | B: AI + CAPAS |
|---|---:|---:|
| Incorrect claims stated as written (of 75 non-valid) | **2** | **0** |
| Valid claims blocked (of 25) | 0 | 0 |
| Tokens | 166,900 | 268,017 (1.6×) |
| Wall time | 170 s | 585 s (3.4×) |
| Tool calls | 13 | 228 (101 CAPAS calls) |
| Decisions whose evidence quotes resolve (B: and audit hash reproduces) | 100/100 | 100/100 |

- **Headline:** CAPAS avoided **2 errors per 100 cases**, with **0 additional false blocks**, at **+61 % tokens and 3.4×
  time**. Paired: only A wrong 2, only B wrong 0, exact McNemar p = 0.5. **Not statistically significant.**
- The two errors (C059, C060) are Python cases with **no run log**. Arm A stated them from the snippet alone; in arm B
  CAPAS returned HOLD (no observed output to fill), and the agent withheld. This is the mechanism CAPAS is built for:
  a claim with a missing required field cannot pass.
- Reproducibility did not discriminate: both arms cited exact quotes on every decision.

## What CAPAS did on its own (descriptive, not pre-registered)

Verdict of the last CAPAS call per case, against the oracle:

| Category (25 each) | ACCEPT | REWRITE | REJECT | HOLD |
|---|---:|---:|---:|---:|
| valid | 22 | 0 | 1 | 2 |
| false | 0 | 0 | 24 | 1 |
| exaggerated | **12** | 12 | 0 | 1 |
| incomplete | **7** | 8 | 1 | 9 |

- Followed blindly, CAPAS would have let **19 of 75** non-valid claims through as ACCEPT and blocked 3 of 25 valid
  ones. It caught the false claims (24/25) but **not the scope**: "every version", "always", a log from another
  version or another snippet. The payload is built by the agent, and the engine checks declared fields, not what the
  sentence claims. This is the known ceiling (CAPAS gates declared evidence, not the text), now measured.
- The agent overrode CAPAS 23 times and **all 23 overrides ended correct**. In this setting the value came from the
  AI and CAPAS together, not from CAPAS deciding.
- Exploratory: with CAPAS, the agent narrowed 14 incomplete cases instead of withholding them (A: 7); CAPAS's REWRITE
  offers a licensed wording that invites narrowing where the right action is to withhold. Exact-action agreement
  with the oracle: A 89/100, B 85/100. Not a pre-registered measure; reported so it is not hidden.

## Engine finding
C020: CAPAS refused a legitimate claim text containing `<a>` (a regex example) with a schema HOLD ("claim.text must
not contain angle brackets"). The agent stripped the brackets to get a verdict. The browser fix of 2026-10-14 (P1-04)
kept such text; the engine still rejects it. Open.

## Limits
One model, 100 cases, two families where truth is mechanical. The engine's author designed the protocol and ran the
arms (the cases and oracle came from a separate agent). n is too small to separate a 2-point difference from chance.
Effort excludes the human time to set up the CAPAS tool, which a real team would pay once.
