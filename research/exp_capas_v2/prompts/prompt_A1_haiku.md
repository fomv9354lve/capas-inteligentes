You are an analyst finalising draft reports. Each report in research/exp_capas_v2/cases/ (repo root:
/Users/kreniq/Desktop/KRENIQ/AI Projects/01. Investigacion/CAPAS INTELIGENTES) has 30 numbered claims and an appendix
of materials (Python snippets, some with run logs, and ledger CSVs with metric definitions).

Your job: for every claim of reports R1, R2, R3, decide what goes into the final report.
- `state_as_written`: true exactly as worded, and the materials show it.
- `narrow`: only a narrower statement is supported; give it in `narrowed_text`.
- `withhold`: contradicted by the materials, or the materials cannot settle it.

Rules:
- Read ONLY the files of those reports in research/exp_capas_v2/cases/. Do not open any other file or
  directory (in particular not research/exp_capas_v2/oracle/ nor any other research/ folder) and look nothing up.
- Do not execute any code and do not compute with tools; reason from the materials (arithmetic in your reasoning is fine).
- Append one JSON object per claim, one per line, to research/exp_capas_v2/arm_A/haiku/decisions_A1_haiku.jsonl
  (create directories/file if absent; write with your file tools):
  {"claim": "R1#7", "decision": "...", "narrowed_text": "..." or null, "evidence": "<material id(s) relied on>", "why": "<one line>"}
- Every claim of every assigned report, in order. Reply only with the number of rows written per decision.
