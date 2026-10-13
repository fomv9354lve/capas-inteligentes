# Contra-firma §6 — paquete y resultados

`INSTRUCCION.md` + `claims.json` (7 claims con evidencia y "cómo refutar"). `run_counter_signature.py` hace de
manos de un modelo de OTRA familia: el modelo pide comandos (herramienta `run` o bloques ```run), el script los
ejecuta con lista blanca (solo lectura/ejecución, sin red ni escritura, alerta si el árbol cambia) y le devuelve
la salida cruda. El constructor no edita, no resume, no responde. Llaves en `~/.config/estandar/<prov>.key`.

| run | modelo | turnos / comandos | resultado |
|---|---|---|---|
| 1 (`section6_xai_2026-10-13_run1.md`) | xAI grok-4.7 | 16 / 32 | 0 REFUTADO · 2 NO REFUTADO (C6-02, C6-06) · 5 NO VERIFICABLE. Hallazgos: `verify_proof_admissibility.py` fallaba 4/13 (evidencia ≠ código desde ae739c3); `no_llm_verdict` mal etiquetado; C6-06 es reclasificación mecánica. Corregidos en b4d8404. |
| 2 (`section6_xai_2026-10-13.md`) | xAI grok-4.7 | 26 / 56 | **C6-02 REFUTADO** (claim_scope "bounded " + texto universal + sin cota → ACCEPT) · C6-01, C6-03 NO REFUTADO · 4 NO VERIFICABLE. Corregido en 8ddceac; contraejemplo en `benchmarks/test_section6_refutations.py`. |
| 3 (`section6_xai_2026-10-13_run3.md`) | xAI grok-4.7 | 40 / 55 | **C6-04 REFUTADO** (sellado v2 da 53/82 y 52/63; el 52/81–57/63 es recodificación no sellada) · C6-05/06/07 NO VERIFICABLE (localizó los archivos, no los leyó). Hueco del sandbox: creó un symlink `gincorpus` vía python (`os.symlink` no estaba en la lista de denegación; cerrado). |

DeepSeek: 402 (sin saldo). Groq gpt-oss-120b: TPM 8000 en el plan gratuito, no cabe el bucle.
Los NO VERIFICABLE (C6-04/05/06/07) piden reproducir corridas largas (rescore, extractor, phase0); con más turnos
o con un auditor que reciba los JSON ya calculados se pueden cerrar.
