# Round 2 — rule-based verification / RLVR tradition (China)

**Verdict: AGREE WITH CONDITIONS.**

## (a) Red lines still crossed

None. All three hold: no model output in a verdict path (A4 judge outputs outside the verdict; "no ACCEPT by reliance"); no network call at decision time (A5 hashed, dated snapshot, absent → HOLD); no GB/T 47468-2026 conformance sentence before the text is read. My two missing actions are deferred past day 90 with a reason; accepted.

## (b) The single change I still demand

**A1 must test that the checker can say no.** The plan's acceptance test is "replay is green on every sealed verdict". A checker that only ever agrees is a reward model trained without negatives — what Tencent's "One Token" showed fails (https://arxiv.org/abs/2507.08794) and Master-RM fixed with adversarial negatives. The Lean kernel earns trust by rejecting wrong proofs.

Condition, concrete: CI for `capas_check.py` carries a **mutated-trace suite** — for each sealed verdict, k mutations (a rule removed from `rules_fired`, one outcome flipped, `engine_tag` altered, an input hash changed, a rule version bumped) — and the build fails unless the checker rejects every mutation (checker false-accept = 0/k·n). The checker's own sha256 is sealed in the X6 pre-registration beside the engine tag, so A4 cannot quietly move the checker. Ledger entry `checker_rejects_mutations`, CLOSED, before `attest_conformance` is promoted. Without this, A1 closes a SCOPED entry on agreement alone, which my tradition does not count.

## (c) Where I was wrong

The AI-eval member: "CAPAS moved the judge from the verdict to the coding step, not out." I wrote as if "no model in the verdict" settled reward hacking. It does not: the session that writes the MAPPING (prereg metric → claim type → fields) is the autograder, and the master-key attack surface moved with it. Two independent coders with published field-level agreement, and HOLD on a required-field disagreement (AI-eval, formalist), is the measurement I omitted and DeepSeek-R1's rule-based rewards never needed, because their answer keys were not typed by a model. I support folding `coder_agreement` into A2 or A7 rather than leaving it to a future batch.
