# World sweep 2026 — brief handed to every wave agent (identical for all waves)

## The project being positioned (CAPAS, Krenn·IQ, Mexico)
A deterministic, fail-closed **claim-admissibility gate**: a scientific or AI-generated claim is turned into structured
evidence fields (p-values, CIs, pre-registered bands, instrument calibration snapshots with per-parameter dates,
reproducibility artifacts, declared scope) and the engine returns exactly one of ACCEPT / REWRITE / REJECT / HOLD with a
re-derivable audit hash. **No language model in the verdict.** What is not declared is never accepted (HOLD/REWRITE).
Distinctive practices: (1) sealed blind evaluation — engine frozen at a git tag BEFORE claims are coded, verdicts sealed
by hash BEFORE outcomes are opened, measured blind: 53/82 bad claims stopped, 52/63 good kept, out-of-sample 17/21 and
16/17; (2) a public proof ledger where every number the project publishes is CLOSED (locked test) / BACKED (regenerates
with hash) / SCOPED (declared estimate), release blocked if a number is orphaned; (3) §6 counter-signature — a model of
ANOTHER company attacks the project's claims with real commands (3 of 7 refuted and fixed); (4) machine-context
ingestion — evidence fields come from instrument files (Qiskit BackendProperties), pre-registration files and results
files with sha256, not from a person/LLM typing numbers (GIGO reduction); (5) leakage discipline — rules written from
failures make sealed claims training data; blind rates belong to the frozen engine; credit only on the next sealed batch;
(6) measured limits stated: NOT a fraud detector (888 clean vs 6,348 retracted papers: no separation), does not read prose,
GIGO ceiling (a consistent fabrication passes). Beachhead: regulated statistical submissions (pharma). Sister project
Atlas runs quantum-hardware experiments (IBM Heron) and uses CAPAS as judge.

## What to look for, per country (2025–2026 first, then 2023–2024 if that is all there is)
1. DIRECT: any system/paper/tool/policy on deterministic or fail-closed verification/gating of scientific claims or of
   AI-generated research claims; LLM-as-judge vs deterministic verifiers; neuro-symbolic/autoformalization of claims;
   claim-evidence admissibility; "no model in the loop" verification; sealed/blind evaluation protocols; proof ledgers.
2. ADJACENT: metascience & reproducibility infrastructure; pre-registration / registered reports; automated statistics
   checks (statcheck, GRIM, SPRITE, p-curve); research-integrity tech (paper mills, image forensics); AI-for-science
   programs and their verification stance; evidence standards for regulated submissions (pharma, medical devices, AI
   regulation); uncertainty quantification / VVUQ / credibility assessment; quantum benchmarking/calibration admissibility.
3. EPISTEMICS: how does this country's community or policy frame "what we know / what we don't" (known unknowns,
   confidence levels, evidence grading, honest-limits reporting, fail-closed vs fail-open defaults)?
4. INSTITUTIONS & PEOPLE: labs, agencies, standards bodies, named researchers (with URLs).
5. ONE LINE each: "what CAPAS could take from here" and "where CAPAS is ahead".

## Rules
- Search per country. Large research nations (US, China, UK, Germany, Japan, France, Canada, South Korea, India,
  Australia, Netherlands, Switzerland, Israel, Singapore, Spain, Italy, Brazil, Sweden, Russia…): 4–8 searches, go deep.
  Small states: 1–2 searches; if nothing relevant, write "NOTHING FOUND (queries: …)" — that is a valid, honest result.
- Never fabricate. Every claim about a paper/tool carries a URL. Mark confidence (high/medium/low). Prefer primary sources.
- Date everything. Distinguish 2026 SOTA from older work.
- Per-country entry ≤ 180 words unless the country is rich (then ≤ 400). Use this exact template:

### <Country>
- Direct (2026 SOTA): …
- Adjacent: …
- Epistemics / gap framing: …
- Institutions & people: …
- Take / Ahead: take: … | ahead: …
- Confidence: … | Queries: …

End the wave file with: `## Wave summary` — top 5 findings for CAPAS, the 3 countries with the strongest direct work,
and the list of countries with NOTHING FOUND.
