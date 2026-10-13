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
| 4 (`section6_xai_2026-10-13_run4.md`) | xAI grok-4.7 | 40 / 100 | **C6-05 REFUTADO como cifra** (la graduación de severidad no estaba versionada → ahora `retraction_audit/grade_severity.py`, reproduce 85/3988 y 286/18111 exactos; el ataque de emparejamiento sigue en pie como límite) · C6-06 y C6-07 **NO VERIFICABLE con premisa falsa**: el informe cita `ls` que "no encuentran" archivos, pero esos `ls` **no aparecen entre los comandos ejecutados** y los archivos existen (rescore_*.json, phase0_n500.json). La transcripción literal es lo que lo detecta: un veredicto solo vale por los comandos que de verdad corrieron. |
| 5 (`section6_xai_2026-10-13_run5.md`) | xAI grok-4.7 | 30 / 58 | C6-06 **NO REFUTADO** (0,65→0,78 reconcilia con los JSON y el sellado; 19/19 flips por ausencia del campo; hallazgo: la evidencia citaba "43→33, 11 buenos" que es la columna +A–E, la palanca 3 sola cuesta 7 → corregido en claims.json) · C6-07 **NO REFUTADO** (467/500 = 93,4 % exacto desde el JSON; la muestra no se puede repetir sin red; endpoint `/api/int/` no versionado). Gate del informe: 0 comandos citados en bloques (los citó inline; el gate ahora también lee inline). |
| 6 (`section6_xai_2026-10-13_run6.md`) | xAI grok-4.7 | 30 / 57 | **C6-02 REFUTADO otra vez**: el fix 8ddceac era una regex (lista cerrada); "holds universally", "cualesquiera n", "arbitrary n", "in all cases"… pasaban con alcance declarado acotado. Cierre ESTRUCTURAL en 1f192bd: alcance acotado sin cota uniforme licencia el texto solo con `text_quantifier="bounded"` declarado; ausente → REWRITE; declarado acotado pero texto visiblemente universal → REWRITE (contradicción). 22 textos del auditor congelados como tests. · C6-01 NO REFUTADO (verify_determinism OK; lista lo que no cubre: -0.0/NaN/NFC-NFD/locale, un solo intérprete) · C6-03 NO VERIFICABLE (suite 21 passed; no construyó par propio). Gate: 2/2 comandos citados ejecutados. |

Estado §6 al cierre del 13-oct: C6-01 NR · C6-02 **REF×2→corregido estructuralmente** (8ddceac, 1f192bd) · C6-03 NR · C6-04 **REF→re-sellado** (53/82, 57/63) · C6-05 **REF como cifra→versionado** (`grade_severity.py`) · C6-06 NR · C6-07 NR. Tres de siete refutados por otra familia en un día; los tres corregidos con la corrección congelada en tests o archivos sellados.

DeepSeek: 402 (sin saldo). Groq gpt-oss-120b: TPM 8000 en el plan gratuito, no cabe el bucle.
Los NO VERIFICABLE (C6-04/05/06/07) piden reproducir corridas largas (rescore, extractor, phase0); con más turnos
o con un auditor que reciba los JSON ya calculados se pueden cerrar.
