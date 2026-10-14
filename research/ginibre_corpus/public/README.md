# Blind corpus: public redacted files

Published 2026-10-14 by owner decision: the sealed verdict files and the outcome labels are public, and each claim
text appears as a hash only. The claim texts and outcome notes quote an unpublished paper.

## Contents per set (X1-3 v1, X1-3 v2, X4, X5)

| File | Content |
|---|---|
| `claims_<set>.jsonl` | claim_id, contaminado, claim type, `text_sha256`, and the evidence fields the engine read. Free-text evidence values appear as `sha256:<hex>`. Numbers, booleans and enum tokens are kept. |
| `verdicts_<set>.jsonl` | Unchanged sealed header, plus per claim: verdict, ceiling, reason (redacted strings replaced by a 16-hex hash prefix) and `licensed_claim_sha256`. |
| `outcomes_<set>.jsonl` | claim_id, outcome label (`bueno` / `malo`) and outcome_type. The outcome note is withheld. |
| `MANIFEST.json` | sha256 of every original sealed file and of every public file. |

Hashes are sha256 of the exact UTF-8 string.

## Checks

    python3 research/ginibre_corpus/score_public.py            # integrity + figures
    python3 research/ginibre_corpus/score_public.py --replay   # + engine at each frozen tag

Result on 2026-10-14:
- **Figures.** All match the site: X1-3 v1 53/82 and 51/63; X4 11/13 and 6/7; X5 6/8 and 10/10. Pooled, 183 claims were scored and 50 contaminated ones were excluded.
- **Replay.** 232 of 233 sealed verdicts were reproduced from the redacted payloads.
- **The one mismatch.** X4-014 does not reproduce because its REWRITE came from the convergence-wording rule, which reads the claim text. It is contaminated and appears in no figure.

## Limits

- **Sealing order.** No third party can check that the verdicts were sealed before the outcomes were opened. The flag, the timestamps and the tag dates are self-recorded.
- **Outcomes.** They are the project's own later corrections, not an external oracle.
- **Claim texts.** They can be matched to their hashes once the paper is public.
- **Short free-text values.** These could be guessed from their hashes. The hashes are not salted, so that they stay checkable later.

Author-side generator: `research/ginibre_corpus/publish_redacted.py`, which needs the private corpus.
