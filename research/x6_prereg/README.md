# X6: CAPAS against LLM judges. Run order

The protocol is `PREREG_CAPAS_VS_LLM_JUDGE.md`, version 8, co-signed by `gemini-3.8-flash`. Editing it voids the
co-signature (`check_cosign.py` fails in CI). The scripts below implement it; their sha256 values go into
`SEAL.json`. `x6_common.py` holds the frozen vocabularies: assertion markers, outcome words, excerpt window and
sample size.

| Step (PREREG §9) | Command | When |
|---|---|---|
| Candidates and contamination | `extract_candidates.py --repo <ginibre> --c0 <C0> --c1 <C1> --out x6/` | before sealing |
| Seal | `seal_prereg.py --engine-tag capas-x6-v1 --repo <ginibre> --remote <url> --c0 --c1 --c2 --lists x6/ --out x6/SEAL.json` | C1 at least 30 days old |
| Push the engine tag | the command `seal_prereg.py` prints | right after sealing |
| Draw the sample | `draw_sample.py --seal x6/SEAL.json --tag-pushed-at <time> --out x6/` (NIST beacon, chain 2) | after the push |
| Code | two independent coders code `x6/sample.jsonl` blind; `capas_coders.py A.jsonl B.jsonl` | after the draw |
| CAPAS verdicts | engine at the tag; certificates checked with `capas_check.py`; sealed by sha256 | before labelling |
| Judge verdicts | `run_judges.py --sample <coded sample> --out x6/judges/` (writes `JUDGES_SEAL.json`) | before labelling |
| Outcomes | `label_outcomes.py --repo <ginibre> --c2 <C2> --candidates x6/sample.jsonl --sealed x6/SEAL.json --out x6/outcomes.jsonl` | only after both verdict sets are sealed |
| Score | `score_x6.py ...` (V1–V3, criteria 1–6, Newcombe paired interval and exact McNemar) | last |

## State on 2026-10-14

- **Scripts.** Written and tested on synthetic git repositories (`benchmarks/test_x6_scripts.py`, 8 tests in CI).
  The real repository's outcomes have not been labelled. The protocol forbids that before sealing.
- **Dry run on the real repository** (counts only):
  - C0 is `af94b25`, the repository head when X5 was read (2026-10-13 02:19).
  - From C0 to the 2026-10-14 head there are 75 candidates; 2 are contaminated.
- **What still blocks sealing:**
  1. **C1 must be at least 30 days old.** With C1 at today's head, sealing can happen from 2026-11-13.
  2. **The source repository has no remote.** PREREG §9 asks for its canonical remote URL. Pushing it to a private
     remote is the owner's decision.
  3. **Two coders independent of Krenn-IQ (V3).** Without them the run is exploratory and no pass is claimed.
