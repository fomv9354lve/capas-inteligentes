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

### Post-mortem X4 → esquema X5 (acordado con Ginibre, 2026-10-13)

Los tres falsos-REJECT se explicaron con evidencia posterior: X4-026 se juzgó por replicación
(los pulls −2,5/−2,8 desaparecen a R=300; decidía χ²/dof 4,23 vs 1027 de los rivales); X4-029
decía «~2σ» y el codificador lo convirtió en 2,0 estricto; X4-031 era error de objeto (celda
declarada ABIERTA, fuera del claim). Reglas para X5: **(a)** si hay χ²/dof con rivales, va en
`test_statistic`, no abs_error = pull máximo; **(b)** si sólo hay pulls, abs_error = máximo sobre
`n_cells` con tolerancia corregida por multiplicidad (Šidák); **(c)** abs_error sólo sobre celdas
que el claim cubre; **(d)** «~kσ» en el texto → tolerancia k, SUPUESTA. (a)(c)(d) son codificación
(ESQUEMA de Ginibre); (b) es motor: tag `ginibre-ciego-v5` (38b1615), campos `error_statistic`
y `n_cells`, Šidák con 2 SE → 2,525 / 2,664 / 2,888 SE para k = 4 / 6 / 12
(`benchmarks/test_multiplicity_tolerance.py`). Sin la declaración el motor juzga celda única:
los 37 payloads de X4 dan **0 cambios de veredicto** entre v4 y v5. X4-026 (2,84 SE, k=6) sigue
REJECT bajo (b) sola; lo habría decidido (a).

## X5 — segundo lote fuera de muestra (2026-10-13), con el esquema corregido

Motor congelado en `ginibre-ciego-v6` (481d5cf, regla (b) Šidák viva) **antes** de codificar; 20 claims
(la lista de exclusión de 228 textos agotó el repo), codificados con (a)–(d) y `error_statistic`/`n_cells`
declarados; veredictos sellados (sha256 `acbe3c2d…`, `outcomes_file_opened: false`) y sólo entonces
abiertos los desenlaces. Análisis pre-especificado: principal = 18 limpios; los 6 `\bibitem` (X5-014–019,
todos buenos y homogéneos) como subgrupo aparte.

| | limpios (18) | sin bibitem (12) | bibitem (6) | todos (20) |
|---|---|---|---|---|
| malos no-ACCEPT | **6/8 = 0,75** [0,41–0,93] | 6/8 | — | 8/10 |
| buenos no-REJECT | **10/10 = 1,00** [0,72–1,00] | 4/4 | 6/6 | 10/10 |
| buenos en ACCEPT | 6/10 | 3/4 | 3/6 | 6/10 |

Cero falsos-REJECT: las reglas (a)(c)(d) de codificación eliminaron la clase de fallo de X4 (tolerancia 2 SE
sobre máximos). Regla (b) disparó en X5-011 (k=2 → 2,273 SE) y X5-012 (k=14 → 2,936 SE), ambos buenos,
ambos ACCEPT; X5-008 (`max` sin `n_cells`) → HOLD, como se esperaba.

Dos falsos-ACCEPT, los dos con nombre de deuda de motor:
- **X5-003** (sobreafirmación de alcance): mismo hueco que X4-002. `exact_model_solution` no juzga alcance
  declarado vs probado. Segunda caída → pasa de deuda a construcción (campo nuevo, no umbral).
- **X5-010** (test sin potencia): abs_error 3e-14 ≤ tolerance 1e-10. El motor no mide la potencia del test:
  una tolerancia 4 órdenes por encima del error acepta cualquier cosa. Deuda nueva: tolerancia absoluta
  debe ser comparable a la escala del objeto o venir con `tolerance_rationale`; si no, HOLD/REWRITE.

**Acumulado fuera de muestra (X4 + X5, limpios): malos no-ACCEPT 17/21 = 0,81 [0,60–0,92]; buenos no-REJECT
16/17 = 0,94 [0,73–0,99].** Sigue siendo n chico; es la primera cifra que no es post-hoc y no es n=20.

### Post-hoc: coste y ganancia de las reglas nuevas del 13-oct sobre X1–X5 (conoce desenlaces; NO es tasa)

Árbol 8ddceac vs veredictos sellados (X1–3 en v2; X4 en v4; X5 en v6). 40 flips en 233 claims, ninguno a
REJECT. Atribuibles SOLO a las tres reglas nuevas de hoy (el resto son palancas §6/A–E ya medidas):

| regla | malos → detectados | buenos pierden ACCEPT (→ REWRITE/HOLD) |
|---|---|---|
| alcance en texto sin `scope_declared/tested` (exact_model) | 2 (X4-001, X4-002) | **5** (X3-010, X3-039, X3-045, X4-030 C, X4-035 C) |
| alcance declarado acotado + texto universal (C6-02 fix, proofs) | 3 (X1-008, X2-008, X3-041) | 0 |
| precisión de máquina sin control negativo | 3 (X1-005, X5-010, X4-014 REWRITE→HOLD) | 1 (X1-054) |

Lectura: el fix de C6-02 es ganancia neta; el control negativo casi; **la regla de alcance en texto cuesta 5
buenos por 2 malos** porque nadie declaró `scope_declared/scope_tested` (no existían al codificar) — sólo
dispara por prosa. Es lo mismo que pasó con A–E: la regla sirve cuando el codificador declara; sin
declaración, degrada a REWRITE (nunca REJECT) y el coste es ese. Se deja como está: lo que pide es un campo,
y el campo ahora existe.
