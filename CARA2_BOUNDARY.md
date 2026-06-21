# Cara 1 / Cara 2 boundary

CAPAS has two layers with **one dependency arrow that never reverses**.

## Cara 1 — the product (deterministic verification engine)
Modules: `capas_verify` (spine, 18 evidence domains), `capas_route`, `capas_rcc`
(the signed self-bounding certificate), `capas_admissibility`, `capas_conformal`,
`capas_braid` (relational network), `capas_extract` (prose→verdict), backends
`capas_sql` / `capas_xbrl` / `capas_quantum` / `capas_circuits` / `capas_ezkl`.

- **Product-grade.** Ships. Deterministic verdict; no LLM in the decision path.
- Gate: `benchmarks/cara1_acceptance.py` (24 checks) + `benchmarks/verify_cara_decoupling.py`,
  both in `capas validate`.
- The product never imports Cara 2 and ships without it installed.

## Cara 2 — the research/cognitive layer
Modules: `capas_conjecture` (bridge compiler), `capas_loop` (open-forward spiral),
`capas_hierarchy` (layered triad), `capas_think` (settling dynamics), `capas_integration`
(Φ-**proxy** = spectral algebraic connectivity, a heuristic — NOT integrated
information), `capas_value` (learned guide), `capas_process` (process reward),
`capas_mind` (orchestrator).

- **Research-grade. Not shipped.** Imports Cara 1; Cara 1 never imports it.
- Measured advantage over flat verification: `benchmarks/cara2_advantage.py`
  (multi-hop catches lies-in-support flat verification false-accepts; the braid
  catches cross-inconsistency; value-guidance beats random). Live (LLM) experiment:
  `benchmarks/cara2_live_experiment.py` — never blocks a ship.

## What Cara 2 does and does NOT claim
It adds **measurable verification power** (composition, cross-check, guidance). It does
**NOT** claim machine consciousness; "Φ" is always a **proxy** (a spectral heuristic);
the consciousness/predictive-coding framing is design scaffolding, confined to Cara 2
internals and research notes. The product certificate surface carries none of it (enforced
by `verify_cara_decoupling.py`).

## Decision: imports for testing are allowed; runtime product coupling is not

The decoupling rule governs **product source modules at runtime**, NOT tests. Concretely:
- **Product modules** (`capas_*.py` in Cara 1) must not import Cara 2, and the product must
  LOAD with every Cara-2 module blocked — both enforced by `verify_cara_decoupling.py`
  (a static scan AND a runtime "import the product with Cara 2 blocked" proof).
- **Test / benchmark files MAY import BOTH layers** to cross-validate — e.g. using the
  Cara-2 braid to catch a cross-inconsistency among Cara-1 verdicts, or the multi-hop
  compiler to stress Cara-1's rungs. That is legitimate "test and check", not overclaim.
- The only hard constraints are therefore: (1) the product runs without Cara 2, and
  (2) no overclaim on the product surface. A cross-layer test must live **outside** the
  product gate (`capas validate` stays Cara-2-free) so the product still ships
  independently. The concern was never test-time imports — it is runtime dependency and
  the "verified"/consciousness overclaim.

## The standing risk
Semantic coupling: Cara 1 interfaces shaped around Cara 2's needs. Rule — every Cara 1
interface must be justifiable from the product alone; Cara 2 adapts to Cara 1, never the
reverse. The "Cara 1 imports no Cara 2" test is the canary.
