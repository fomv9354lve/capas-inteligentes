# Corpus ciego de Ginibre — evaluación y palancas (2026-10-13)

Corpus: 176 claims (110 malos / 66 buenos) del repo de Ginibre, evidencia codificada **a ciegas** por
dos agentes; ficheros y hashes en `Paper - Inverse Ginibre Overlap/CAPAS_CORPUS_2026-10-12/`.

## Cifra ciega (vale como tasa)
Motor congelado `ginibre-ciego-v2` (317ce90), veredictos devueltos sin abrir desenlaces, reproducidos
176/176 entre sesiones. Sin contaminar: **detección 52/81 = 0,64 [0,53–0,74]; buenos no rechazados
57/63 = 0,90 [0,81–0,96]** (tras recodificación ciega de 22 `steps_all_valid`).

## Palancas (post-hoc: medidas con desenlaces conocidos, misma muestra — NO es una tasa)
`rescore.py` re-evalúa el corpus contra el árbol actual. Sobre la codificación original (baseline
0,65 / 0,83):

| cambio (commit ae739c3) | detección | buenos | efecto |
|---|---|---|---|
| 2. texto cita → `citation_hypotheses_checked` obligatorio | — | — | 0 aquí: sólo 2/176 textos citan |
| 3. `proof_admissibility` ACCEPT exige `independent_reproduction_pass` (§6) | 12/23 → **23/23** | 11/19 → 11/19 | toda la ganancia |
| 4. `statistical_confidence` con `test_statistic` → p recomputado | — | — | 0 aquí: ningún claim lo lleva |
| **total** | **64/82 = 0,78** | 52/63 = 0,83 | |

**Lectura honesta de la palanca 3.** No "detecta" nada nuevo: convierte en REWRITE toda prueba que no
declare una re-derivación independiente. Atrapa 23/23 porque ninguno de los malos la tenía — pero
tampoco la tenía ningún bueno, que pasan de ACCEPT a REWRITE (no cuentan como rechazados). Es la §6 de
GOVERNANCE metida en el motor: ninguna prueba sale ACCEPT con la sola palabra de quien la construyó.
El coste práctico es que, hasta que el proyecto practique la re-derivación independiente, `proof_admissibility`
no produce ACCEPT. Eso es una decisión de gobierno, no un ajuste de precisión.

**Para que 0,78 sea una tasa:** un lote ciego nuevo (no visto al diseñar las palancas), evaluado contra
un tag congelado posterior a ae739c3.
