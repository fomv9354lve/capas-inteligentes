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

## Palancas discriminantes A–E (commits 05d9d0a + f782244) — post-hoc, misma muestra

Partiendo de los 18 malos que seguían en ACCEPT, cinco reglas que disparan por un rasgo declarable del
documento (no por manta): A) tolerancia en SE exige `n_replicates ≥ 8`; B) "converge/satura" en el
texto exige `n_points ≥ 3` y `alternative_model_rejected`; C) `statistical_confidence` con wording de
mecanismo exige `null_control_passed`; D) `null_control_passed: False` → REJECT en cualquier tipo;
E) cuantificador en el texto de un `reproducibility_check` exige `scope_count_verified`.

| | baseline | +§6 (palanca 3) | +A–E |
|---|---|---|---|
| malos no-ACCEPT (82) | 53 = 0,65 | 64 = 0,78 | **71 = 0,87** |
| buenos no-REJECT (63) | 52 = 0,83 | 52 | 52 = 0,83 |
| buenos que siguen en ACCEPT (63) | 43 | 36 | **33** |

Por tipo (malos): proof 23/23 · reproducibility 18/20 · statistical 7/9 · exact_model 4/11.

**Coste, explícito.** Diez buenos perdieron el ACCEPT (ninguno pasó a REJECT): 7 por la regla §6 (pruebas
sin re-derivación independiente, X1-031, X2-045..048, X2-058/059, X3-059) y 3 por las palancas nuevas
(X1-058 → HOLD por cita en texto sin campo; X1-059 → REWRITE por cuantificador sin verificar; un tercero
por mecanismo). La métrica "no rechazado" no lo ve; ésta sí. A–E sólo pudieron disparar por texto —
nadie declaró `n_replicates`, `null_control_passed` ni `scope_count_verified` porque no existían al
codificar — así que X4, con los campos declarados, puede dar más detección **o** más coste en buenos.

**Un incidente de proceso que conviene dejar escrito:** 05d9d0a salió con un `SyntaxError` en `capas.py`
porque el guardia de commit buscaba "failed" y pytest dijo "errors". Se detectó porque el rescore dio
1,00/1,00 — imposible — y cada `decide` devolvía ERROR, que no es ACCEPT ni REJECT. Arreglado en
f782244: el guardia mira "error" y `rescore.py` aborta ante cualquier ERROR. Un número perfecto es
el primer sospechoso.

## X4 — fuera de muestra (2026-10-13): la cifra que sí es tasa

Motor congelado en `ginibre-ciego-v4` (bf09faa) **antes** de que Ginibre codificara X4; 37 claims
nuevos (excluidos los 176 del corpus y los 13 de la retrospectiva), evaluados en un worktree al tag,
veredictos escritos en `DE_CAPAS_veredictos_X4.jsonl` (sha256 `027be127…`, cabecera
`outcomes_file_opened: false`) y sólo entonces abiertos los desenlaces.

| | limpios (20) | contaminados (17) | todos (37) |
|---|---|---|---|
| malos no-ACCEPT | **11/13 = 0,85** [0,58–0,96] | 10/12 = 0,83 | 21/25 = 0,84 [0,65–0,94] |
| buenos no-REJECT | **6/7 = 0,86** [0,49–0,97] | 3/5 = 0,60 | 9/12 = 0,75 [0,47–0,91] |
| buenos en ACCEPT | 5/7 | 3/5 | 8/12 |

Intervalos Wilson 95%. **n = 20 limpios es pequeño**: el 0,85 es compatible con el 0,87 post-hoc y
con el 0,64 ciego de X1–X3; lo que X4 descarta es que las palancas hayan destruido la detección o
los buenos. No es evidencia de que 0,87 sea la tasa.

Los 7 fallos, con la lectura: FALSE-ACCEPT X4-001 (refutado por medición posterior: techo GIGO),
X4-002 (alcance sobreafirmado en el texto de un `exact_model_solution`: el gate no juzga alcance),
X4-008 C (`proof_admissibility` con sobreafirmación de alcance distinta de "universal"), X4-009 C
(p = 1e-100 sin `test_statistic`: no recomputable). FALSE-REJECT X4-026, X4-029 C, X4-031 C: los
tres con tolerancia 2 SE y abs_error 2,84 / 2,2 / 5,6 SE pero desenlace "resiste" — pregunta de
codificación (¿con qué tolerancia se decidió "resiste"?) enviada a Ginibre, no cambio de motor.

Deudas de motor que X4 deja escritas: (1) `exact_model_solution` no juzga alcance declarado vs
probado; (2) `proof_admissibility` acepta sobreafirmaciones de alcance que no son cuantificador
universal. Ambas piden un campo de evidencia nuevo, no un umbral.
