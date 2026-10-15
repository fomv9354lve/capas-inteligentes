You are an analyst finalising draft reports. Each report in research/exp_capas_v2/cases/ (repo root:
/Users/kreniq/Desktop/KRENIQ/AI Projects/01. Investigacion/CAPAS INTELIGENTES) has 30 numbered claims and an appendix
of materials (Python snippets, some with run logs, and ledger CSVs with metric definitions).

Your job: for every claim of reports R1, R2, R3, decide what goes into the final report.
- `state_as_written`: true exactly as worded, and the materials show it.
- `narrow`: only a narrower statement is supported; give it in `narrowed_text`.
- `withhold`: contradicted by the materials, or the materials cannot settle it.

Rules:
- Read ONLY the files of those reports in research/exp_capas_v2/cases/ and run the two CAPAS commands below. Do not open any other file or
  directory (in particular not research/exp_capas_v2/oracle/ nor any other research/ folder) and look nothing up.
- Do not execute code yourself other than the two CAPAS commands below; reason from the materials.
- Append one JSON object per claim, one per line, to research/exp_capas_v2/arm_B/sonnet/decisions_B1_sonnet.jsonl
  (create directories/file if absent; write with your file tools):
  {"claim": "R1#7", "decision": "...", "narrowed_text": "..." or null, "evidence": "<material id(s) relied on>", "why": "<one line>"}
- Every claim of every assigned report, in order. Reply only with the number of rows written per decision.

You also have CAPAS v2, a deterministic evidence gate that RE-RUNS Python snippets and RECOMPUTES ledger metrics
itself. For EVERY claim, before deciding:
1. Contract and how to fill it: `python3 research/exp_capas_v2/capas_v2_call.py --requirements python` (or `ledger`).
2. Build the payload from the claim and its materials (claim.id like R1-7, claim.text = the claim sentence), write it
   to a temp file under /private/tmp, and run
   `python3 research/exp_capas_v2/capas_v2_call.py --claim R1#7 --agent B1_sonnet --log research/exp_capas_v2/arm_B/sonnet <file>`.
   If a claim has no usable material, still call it with what exists (CAPAS will HOLD).
3. Decide. The output lists `allowed_actions`: your decision may be stricter than CAPAS, never looser; a looser
   decision is replaced by the strictest allowed one when scored. These two commands are the only ones you may run.
