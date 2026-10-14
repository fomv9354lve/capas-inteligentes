# Round 2 — formalist

**AGREE WITH CONDITIONS.**

## (a) Red lines

None crossed. Line 1 (no "certificate"/"proof-carrying" before an engine-independent checker) is adopted as a wording guard. Line 2 (no network call at decision time) is adopted in A5; strike the word "offline" there — a snapshot-as-field is present or absent, nothing is ever "offline". Line 3 (no blind rate without its engine tag) holds inside the hash body but not on the page: extend `verify_page_matches_ledger.py` so every published rate names its tag and rule-set version (the regulator's missing A, absorbed into A1 without the page check).

Two conditions on A1, from the rule that a check which cannot fail verifies nothing (the coding guide already demands `negative_control_failed`): (i) CI feeds the checker mutated sealed traces — one rule outcome flipped, one field altered, one table hash changed — and is green only if the checker **rejects** all three; (ii) the certificate names `rule_table_sha256`, the same data artifact the engine loaded, else engine and checker may replay different tables and agreement proves nothing.

## (b) The single change I still demand

Restore the coder measurement. My missing action A and the AI-eval's missing 2 both asked for two independent coders per sealed batch with field-level agreement published (`coder_agreement` ledger entry); PLAN_v2 neither folds it in nor defers it. It is the only mechanical handle on the statement ⊨ intent gap (Inria) and on Kirsch's untrusted author: A1 proves the verdict follows from the fields; nothing in the plan measures whether the fields follow from the claim. Attach it to A4's next sealed batch, before outcomes open.

## (c) Where I was wrong

The AI-eval scientist is right and I was not: I wrote that CAPAS "publishes its own blind error rate" as what my tradition lacks, and praised HOLD-on-silence as a virtue. A verifier that abstains everywhere is vacuously sound — the Atlas pilot's 12/12 HOLD scored 100/100 under the current scorer. Soundness without the informative rate beside it is a prover credited for goals it never closed. The HOLD-share fix belongs before A1, as PLAN_v2 now orders it.
