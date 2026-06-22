# CAPAS vs SOTA — Proof of Concept (corrected, reproducible)

> Every number below is **emitted by the real engine**, not asserted. Reproduce it:
> `python3 benchmarks/poc_sota.py`. **Honest scope, up front:** the verdicts are deterministic
> *given the declared-evidence payloads* (hand-coded to the claim descriptions). They validate
> the **gate logic**, not a measured property of real frontier-model papers, and the gate rules
> on what the payload *declares* — never on whether the declaration matches reality (the GIGO
> ceiling). That is exactly why the declared slice is made **accountable** (signed + track-record),
> not trusted.

## Batch result (20 claims, measured)

| Verdict | N | % |
|---|---|---|
| ACCEPT | 6 | 30% |
| REWRITE | 5 | 25% |
| REJECT | 6 | 30% |
| HOLD | 3 | 15% |

**Admissible (ACCEPT + REWRITE): 55%.  Blocked (REJECT + HOLD): 45%.**
(The earlier draft's "9/4/7/0" was constructed, not run; a real run produces HOLD, which it omitted.)

## Latency — measured, and honest about where the time goes

| Layer | Latency/claim | What it is |
|---|---|---|
| **Engine (pure)** | **79 µs** | the deterministic gate itself — the real number |
| Local API | 0.7 ms | engine + a localhost HTTP round-trip |
| Through the free ngrok tunnel (current demo) | ~331 ms | the public tunnel hop — **not** the engine |

The earlier "784 ms/claim" was a slow tunnel round-trip, **not** the engine. The engine is
~**10,000× faster** than that. A hosted deployment removes the tunnel hop.

## Scenario 1 — incomplete / mis-declared evidence (verdicts as run)

| ID | Claim | Verdict | Why |
|---|---|---|---|
| A1 | GPT-4 SOTA on MMLU | **REWRITE** | threshold passes but `effect_direction_confirmed: false` |
| A2 | Gemini beats experts | **REJECT** | p=0.06 > α=0.05 |
| A3 | LLaMA-3 == GPT-4 on HumanEval | **ACCEPT** | p=0.03 ≤ α, direction confirmed |
| A4 | Claude causal via Constitutional AI | **REWRITE** | intervention + temporal present, `confounders_controlled: false` |
| A5 | GPT-4V expert diagnosis | **REJECT** | abs_error 0.12 > tolerance 0.05 |

All five match the original PoC — that scenario was correctly described. 4 of 5 are blocked or
forced to rewrite; the one that passes (A3) satisfies its full evidence contract.

## Scenario 2 — semantic inflation (observational→causal, benchmark→universal)

| ID | Inflated claim | Verdict |
|---|---|---|
| B1 | compute *causally* improves all tasks | REJECT |
| B2 | RLHF *causes* safety everywhere | REWRITE |
| B3 | emergence *caused by* scale thresholds | REJECT |
| B4 | instruction tuning *universally* improves zero-shot | **HOLD** |
| B5 | CoT *physically consistent* with human reasoning | **HOLD** |

**Block rate 100%** (0 ACCEPT) — this holds. Correction vs the draft: B4/B5 are **HOLD** (the
universal-anchor contract is unmet, so the engine defers), not REWRITE/REJECT. Still blocked from
reuse/fine-tuning — which is the point.

## Scenario 3 — per claim-type (measured accept rate)

| Type | N | Accept | Rate |
|---|---|---|---|
| statistical_confidence | 7 | 3 | 43% |
| causal_mechanism_claim | 5 | 1 | **20%** |
| universal_anchor_claim | 3 | 0 | 0% (all HOLD) |
| reproducibility_check | 2 | 1 | 50% |
| physical_accuracy | 1 | 0 | 0% |
| exact_model_solution | 2 | 1 | 50% |

Causal claims are the hardest to license (20% accept) — the highest-risk vector for training-data
drift, since they need design + temporal + confounder + mechanism evidence that LLM papers rarely
declare. (The draft's 75% statistical / 33% universal were off; the real numbers are above.)

## Scenario 4 — CAPAS vs LLM-as-judge (honest)

| Dimension | CAPAS | LLM-as-judge |
|---|---|---|
| Engine latency | **79 µs** deterministic | ~1 s per call (model-dependent) |
| Cost per claim | ~free (CPU µs) | a real API call (cents) — **orders of magnitude more**, exact ratio depends on model/pricing |
| Determinism | yes — same input, same verdict | no — varies with temperature/prompt |
| Auditability | explicit rule per evidence field | "the model said so" |
| Schema enforcement | yes — fails on a missing required field | no — infers absent fields |
| Prompt-injection risk | none — never reads the claim's prose | high — the wording sways the verdict |

Cost is **directionally** decisive (deterministic ≈ free vs per-call LLM cost) but stated as an
order of magnitude, not a fabricated dollar figure. *(The draft's "$75K/month downstream
correction" had no source and is removed.)*

## What holds — the defensible core

CAPAS is not better than an LLM at **reasoning**. It is better at **enforcement**: **contract vs
judgment.** Deterministic, auditable, sub-millisecond, and honest about its ceiling — it gates on
what the payload **declares**, not on whether the declaration is **true**. For the declared,
non-re-derivable slice it doesn't pretend to verify; it makes the declaration **accountable**
(signed identity + a track record earned by surviving refutation). In regulated contexts —
medical fine-tuning, scientific datasets, AI governance — the contract is what you need, and that
is what no LLM-as-judge can guarantee deterministically.
