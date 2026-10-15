# Task for Codex: experiment v2, GPT arms (orchestrator only)

Same rules as the v1 replication (research/exp_capas_addon/codex/CODEX_TASK.md and CHANNEL.md): you only orchestrate,
you decide nothing, you do not read results, labels or other arms, you write only in research/exp_capas_v2/codex/,
no commit/push/deploy. Protocol: research/exp_capas_v2/PROTOCOL.md. The oracle is not in the repo; do not look for it.

Run four fresh, independent `codex exec` contexts, same model for all (write its name in RUN.md):
  for a in A1_gpt A2_gpt B1_gpt B2_gpt; do codex exec --sandbox workspace-write -C . \
    "$(cat research/exp_capas_v2/prompts/prompt_$a.md)" > research/exp_capas_v2/codex/run_$a.log 2>&1 & done; wait
The prompts write their decisions to research/exp_capas_v2/arm_A/gpt/ and arm_B/gpt/ (and B's calls.jsonl there);
those two paths are part of your lane for this task.
Rerun policy (fixed in advance): rerun a run only if the process fails or writes fewer than half its 90 rows; never
for a malformed row; keep every attempt and say which one is primary (the first complete one).
Report in research/exp_capas_v2/codex/RUN.md and in research/exp_capas_addon/codex/CODEX_TO_CLAUDE.md (the channel):
model, times, tokens, rows per file, any incident. Then tell Osvaldo "listo para que Claude puntúe".
