# Task for Codex: run the AI vs AI+CAPAS experiment with a second model family

Repo root: /Users/kreniq/Desktop/KRENIQ/AI Projects/01. Investigacion/CAPAS INTELIGENTES. The Claude session (CAPAS)
already ran this experiment with Claude Sonnet; you are the replication with an OpenAI model. Protocol:
research/exp_capas_addon/PROTOCOL.md (read it). You are the ORCHESTRATOR only: you do not decide any case yourself.

## Rules
- Do NOT read the cases' answers: there is no oracle in the repo now; do not look for one (not in git history, not on
  GitHub, not in /private/tmp). Do not read RESULTS.md, result_sealed_scorer.json, arm_A/ or arm_B/ (Claude's run):
  knowing Claude's results would bias nothing you decide, but the arms you launch must stay blind, and so should you.
- Do not edit anything outside research/exp_capas_addon/codex/. Do not edit capas.py or any engine file.
- Do not commit, push or deploy. The Claude session scores and publishes.

## What to run
Four fresh, independent `codex exec` runs, one per prompt file, each with a clean context (they must not see each
other or this file). Same model for all four; use your default model and write its exact name in RUN.md.

```bash
cd "/Users/kreniq/Desktop/KRENIQ/AI Projects/01. Investigacion/CAPAS INTELIGENTES"
for a in CA1 CA2 CB1 CB2; do
  codex exec --sandbox workspace-write -C . "$(cat research/exp_capas_addon/codex/prompt_$a.md)" \
    > research/exp_capas_addon/codex/run_$a.log 2>&1 &
done; wait
```
- CA1/CA2 = AI alone (cases C001-C050 / C051-C100). CB1/CB2 = AI + CAPAS (they call capas_call.py).
- If a run cannot write its decisions file or stops early, rerun only that run, and say so in RUN.md.
- Check each decisions file has 50 lines of valid JSON with case_id C001-C050 or C051-C100.

## What to report back (write research/exp_capas_addon/codex/RUN.md, and reply with the same in a few lines)
- model name and version, codex-cli version, start and end time of each run;
- tokens per run if codex reports them (else "not reported"), wall time per run, number of tool calls if visible;
- lines written per decisions file and any rerun;
- anything that went wrong (a run reading files outside cases/, a CAPAS call that failed, a sandbox denial).
Nothing else: no analysis of the decisions. Tell Osvaldo "listo para que Claude puntúe".
