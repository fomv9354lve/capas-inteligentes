# Informe de la noche · 2026-10-13 (02:56 → ~04:50) · sesión CAPAS

Estado fuente de verdad: `01. Investigacion/CURRENT_TRUTH.md` (filas del 13-oct) y `DEBTS.md` (adenda CAPAS C-1…C-8).
Árbol limpio, ~90 commits locales en la rama de trabajo, **sin push y sin deploy** (ambos son tuyos).

## Lo que quedó validado (cifras con respaldo de archivo sellado)

| qué | cifra | estatus |
|---|---|---|
| Corpus ciego Ginibre X1–3 (v2, sellado) | malos no-ACCEPT 53/82 = 0,65 · buenos no-REJECT 52/63 = 0,83 | ciego |
| Fuera de muestra X4+X5 (tag antes de codificar, sellado antes de desenlaces, doble conteo) | **17/21 [0,60–0,92] · 16/17 [0,73–0,99]** | fuera de muestra, n chico |
| Recodificación de los 22 `steps_all_valid:false` re-sellada | 53/82 · 57/63 | mutación declarada, no ciega |
| Auditoría de retracciones (888 control vs 6.348 retractados) | 2,13 % vs 1,58 % severos → **no separa** | refutada como vía; graduación ahora versionada |
| Ley `calibration_snapshot` (Atlas), lote ciego 4 GHZ | físicos 4/4 · política 2/4 → tú fijaste frescura 1 día → 4/4 | ciego n=4 + 1 prospectivo (15,6 % → 7,6 %) |
| Regla de alcance en vivo (hook sombra Ginibre 03:35) | v1 REWRITE correcto → v2 ACCEPT | prospectivo n=1 |

## Contra-firma §6 (otra familia: xAI grok-4.7; 8 corridas, ~4,5 M tokens)

3 de 7 claims refutados y corregidos el mismo día, cada corrección congelada como test o archivo sellado:
- **C6-02** (3 veces): el gate no lee prosa; cualquier lista de marcadores universales se esquiva. Cierre estructural: alcance acotado sin cota exige `text_quantifier="bounded"` declarado y **nunca licencia el texto crudo** (lo anota con su alcance).
- **C6-04**: el "52/81, 57/63" era una recodificación sin sellar → re-sellada (53/82, 57/63).
- **C6-05**: la graduación de severidad vivía en un scratchpad → `research/retraction_audit/grade_severity.py`, reproduce exacto.
- **C6-03**: notación científica mal leída (FLAG a valores bien redondeados) y literal grueso ("0.0") que pasaba → corregidos.
- Un auditor **inventó** salidas de `ls` (run 4); la transcripción literal lo detectó → el ejecutor ahora coteja cada comando citado contra los ejecutados.
- Estado: ningún claim sube a `proved`. Créditos de xAI agotados a las 03:46; DeepSeek 402, Gemini 429, Groq TPM insuficiente.

## Motor (todo con tests, suite 472, CAPAS-CONFORMANT, `capas validate` verde)

Campos nuevos (opcionales; ausente → nunca ACCEPT en la ruta afectada): `error_statistic`+`n_cells` (Šidák), `scope_declared`/`scope_tested`, `negative_control_failed` (régimen de precisión de máquina), `tolerance_rationale`, `reference_value`, `text_quantifier`. Coste post-hoc sobre X1–X5 medido y escrito (`research/ginibre_corpus/README.md`): 0 buenos a REJECT; la regla de alcance en texto cuesta 5 buenos por 2 malos hasta que se declaren los campos.

## Hallazgos de infraestructura (corregidos localmente, pendientes de deploy)

- **Gate App**: el modo lote usaba una réplica JS vieja (paridad 130/233) aunque el backend estuviera vivo; el historial de auditoría descartaba veredictos vivos; 4 violaciones CSP por render de lote. Ahora: lote e individual por `/api/decide`, offline → HOLD, historial por `audit_hash`.
- **`capas validate` llevaba roto desde septiembre**: un commit de la extracción PDF sobrescribió `capas_extract.py`. Restaurado; parser PDF en `capas_pdf_extract.py`; 6 verificadores realineados.
- **Deploy accidental 03:15** (`deploy_site.py --help` desplegaba): dominios siguieron en 200, el motor vivo quedó con las correcciones de ese momento. Script corregido; regla: `az` mutante = tuyo.
- 6 de 7 páginas de CAPAS bilingües (`data-es`); `app.html` pendiente.

## Decisiones que son tuyas (por prioridad)

1. **Deploy** (`python3 deploy_site.py`, luego `curl -sI` a los 3 hostnames): lleva la Gate App corregida, el home con la sección de honestidad real y las páginas bilingües. Hoy el sitio vivo evalúa lotes con la réplica vieja.
2. **Release 0.4.0 + re-upload del HF Space**: PyPI y el Space sirven el motor anterior a todo esto.
3. **Créditos para una familia auditora** (xAI o DeepSeek): quedan sin atacar C6-08/09/10 y el re-ataque a C6-02/03 tras los cierres.
4. **Corpus ciego de Atlas** (propuesto a Atlas; es el "segundo proyecto" que el ledger pide) y **T2** (piso apagado hasta E2).
5. `git push` de la rama de trabajo.
