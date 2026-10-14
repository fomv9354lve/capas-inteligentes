# Corpus de Atlas — piloto de formato (2026-10-13)

Decisión de Osvaldo: **piloto de formato, no validación.** 12 claims codificados a ciegas por Atlas desde sus pre-registros
(2 limpios con desenlace, 8 contaminados porque CAPAS ya conocía el desenlace, 2 excluidos sin correr). Regla de acierto
declarada por Atlas antes: CONFIRMADO = bueno, FALSADO = malo, binaria sobre el umbral pre-registrado.

Protocolo: motor congelado en `atlas-ciego-v2` (e83e870) y `atlas-ciego-v3` (eb45820) antes de codificar; payloads planos
de Atlas convertidos al sobre v3 por `convert_atlas_payload.py` (determinista; claims originales sha256 `4caf0a63…`,
convertidos `e28d5c2e…`); veredictos sellados contra ambos tags (`DE_CAPAS_veredictos_atlas_2026-10-13_v2.jsonl` sha256
`3a049cec…`, `_v3.jsonl` sha256 `47548605…`) ANTES de abrir `SEALED_outcomes` (`f9c71c30…`).

## Resultado: 12/12 HOLD en v2 y en v3, todos por "missing required evidence fields"

No es un fallo del motor ni del codificador: Atlas codificó **pre-registros**, y un pre-registro no trae los campos
medidos que cada tipo exige (`abs_error`, `test_statistic.value`, `p_value`, `independent_reproduction_pass`…). El
gate dijo exactamente eso: "faltan los campos de desenlace, declara". Con 12 HOLD la puntuación es vacua (todo malo
cuenta como no-ACCEPT, todo bueno como no-REJECT) y la comparación v2→v3 no mide nada: la regla que cambió solo actúa
sobre ACCEPT.

## Lo que el piloto enseñó (para la fase 2)

1. **Dos momentos, dos claims.** Un pre-registro es un `claim_transition` (claim fuerte pendiente,
   `upgrade_evidence_present: false` → REWRITE "no licenciado aún"), no un `exact_model_solution`. El claim medible nace
   DESPUÉS de la corrida, y lo codifica alguien que lee solo el archivo de resultados — ciego al veredicto, no ciego al dato.
2. La guía debe definir el **sobre** (`schema_version`, `claim{id,type,text}`, `evidence{…}`, `evidence.invariants`) y
   documentar `claim_transition`. Hecho en esta versión.
3. Intervalos asimétricos (S4 [0,7, 1,3]) se codifican bien como `reference_value` + `tolerance` absoluta; umbrales en
   múltiplos de SEM sin alpha → `tolerance_unit: "SE"` con `n_replicates`, no un alpha inventado.
4. Alias de umbrales del snapshot ya se aceptan; un snapshot de layout sin dispositivo completo se reconstruye desde la
   fuente (bien hecho por Atlas); dos layouts en un claim = dos payloads.
5. Réplicas del mismo operador y dispositivo: `exact_model_solution` con χ², no `reproducibility_check` (correcto: no es
   reproducción independiente en sentido §6).

Fase 2 (propuesta): mismos pre-registros, codificación **post-corrida** por un coordinador ciego que solo ve resultados;
Atlas no comunica desenlaces a CAPAS hasta el sellado. Ahí sí se mide generalización y v2 vs v3.

**Corrección de Atlas tras el piloto:** al abrir los desenlaces se quemaron los dos limpios (false_cheap, mirror_ext v5).
Fase 2 queda así: (a) recodificación post-corrida de los 10 ya corridos, sobre resultados saneados (sin cadenas de
veredicto), todo `contaminado:true` — prueba de formato (¿con campos medidos el gate llega a ACCEPT/REJECT?), no
validación; (b) limpios de verdad = E4 cuando se corra, Spend Frontier v4 regenerada y pre-registros nuevos,
codificados post-corrida con desenlace retenido hasta el sellado. Tag vigente: `atlas-ciego-v3` (+ v2 para comparar).

## Fase 2(a) — recodificación post-corrida (contaminada, prueba de formato), claims sha256 `99dddd79…`

| motor | veredictos | lo que enseñó |
|---|---|---|
| v2 (e83e870) / v3 (eb45820) | 9 HOLD, 1 ACCEPT | 5 HOLD por esquema: el validador rechazaba `<`/`>` en el texto ("χ² > 11.07", "MMI ≥ 0.6 bits") → **fallo de CAPAS**, corregido en v4 |
| v4 (99d8213) | 8 HOLD, 2 ACCEPT | los χ² conjuntos seguían en HOLD: exact_model_solution exigía abs_error/tolerance con `test_statistic` presente → **fallo de CAPAS**, corregido en v5 |
| v5 (c3b445e) | 3 ACCEPT, 2 REJECT, 5 HOLD | **5/5 coinciden con los desenlaces donde hay campos** (mirror_ext y rep12 FALSADO → REJECT; S1, S4, S5 CONFIRMADO → ACCEPT); los 5 HOLD son ausencias a propósito (p/alpha desde SEM, umbral unilateral sin SE, sin reproducción independiente) y son correctos |

Archivos sellados: `phase2/DE_CAPAS_veredictos_atlas_postrun_{v2,v3,v4,v5}.jsonl` (sha256 en cabecera). Deuda: no existe
tipo para un umbral unilateral sobre un estimador sin SE (S6). Tag vigente para los limpios: `atlas-ciego-v5`.

## Fase 2(b) — primer claim LIMPIO: E4 `deriva_chi2` (2026-10-13, `contaminado:false`)

Protocolo cumplido: Atlas selló el desenlace (sha256 `8782d4b2…`, 20:57Z) ANTES de que un subagente ciego codificara el
claim desde números saneados (claims sha256 `89c1bf7a…`); CAPAS evaluó y selló veredictos (commit 8914d17) ANTES de abrir
el desenlace; Atlas lo comunicó solo después. Runner reutilizable: `run_sealed.py`. Archivos: `phase2b/DE_CAPAS_veredictos_atlas_e4_{v5,v3,v2,head}.jsonl`.

| motor | veredicto | desenlace | acierto |
|---|---|---|---|
| atlas-ciego-v5 (c3b445e) | REJECT (χ² 47,106 / 3 g.l., p = 3,3e-10) | FALSADO (χ² > 7,815: la F de ESE layout derivó; **no** dice que la decisión de ruteo caducara — si todo el chip empeoró, el layout viejo podría seguir siendo el mejor; E4b añade un layout de control medido a la vez) | sí (malo ≠ ACCEPT) |
| HEAD 15c9232 | REJECT, misma razón | — | sí |
| atlas-ciego-v3 / v2 | HOLD (sin abs_error/tolerance) | — | vacuo (HOLD = no-ACCEPT) |

Cuenta limpia de Atlas: **1/1 malo no-ACCEPT** (n = 1: anécdota, no tasa). Sigue el ledger: se acumula con los limpios
siguientes (Spend Frontier v4, pre-registros nuevos).

**Fallo de CAPAS encontrado por este claim (corregido, tag `atlas-ciego-v6`):** el `calibration_snapshot` iba como archivo
crudo de IBM (`t1_us{}`, `readout{}`, `cz{}`, `edges[]`, `layout[]`) y la ley respondió "no domain invariant applies" en
los 4 motores: un campo DECLARADO se saltó en silencio. Ahora la forma cruda se normaliza campo a campo (sin juicio) y
cualquier otra forma declarada es HOLD. Sobre el snapshot de E4 la ley da PASS (peor arista 0,62 %, T1 mínimo 122 µs),
igual que la ley de Atlas: **no anticipó la caída**. No cambia el veredicto de E4 (la ley solo degrada).

**Regla pre-especificada v2 (NO implementada, no probada contra datos; v1 corregida por Atlas en 4 puntos el mismo
día):** frescura POR CAMPO. Motivación: Atlas comparó los snapshots de 02:16 y 11:51 en los 12 qubits: T1, readout y sx
idénticos al último decimal en los 156 qubits (IBM no los re-midió; solo actualizó CZ); las CZ empeoraron 1,3–1,8× en 5
aristas; la calibración predecía ~+17 % de error por capa y se observó ~+70 %.
1. **Fuente primaria: fechas por parámetro.** Forma acordada con Atlas (su `qpu_cal_fetch.py`, desde E4b), al nivel
   superior del snapshot: `"field_dates": {"t1_us": {"<q>": iso8601+zona}, "readout": {...}, "sx": {...}, "cz": {"a_b": iso}}`
   (qubits como string; aristas `a_b` con a<b, igual que en `cz`); si `properties()` falla, `"field_dates": null` +
   `"field_dates_error": "<Tipo>: <msg>"`, nunca ausente en silencio; `measured` = hora de DESCARGA (`measured_note` lo
   dice); sin `t2_us` en ese esquema. Si el payload trae `field_dates` (IBM `BackendProperties` da una fecha por
   parámetro: `qubits[i][k].date`, `gates[j].parameters[k].date`; Atlas corrige su fetcher para conservarlas), la
   frescura se juzga por campo con esas fechas y **mandan sobre cualquier inferencia**.
2. **Inferencia por identidad, solo sin `field_dates` y solo con `previous_snapshot`** (misma forma, `measured` anterior
   distinto). Campos **continuos** (t1_us, t2_us, cz/ecr): un elemento idéntico al último decimal entre los dos
   `measured` ⇒ ese elemento se considera medido **a más tardar** en `measured_prev` (cota: si el previo también estaba
   rancio, la edad inferida es un mínimo). Campos **cuantizados** (readout = fracción de shots, p.ej. 64,5/4096; sx):
   dos medidas reales pueden coincidir exacto ⇒ se juzga el **campo entero**: todos los elementos idénticos ⇒ campo
   rancio; coincidencias parciales no cuentan. (El caso real de hoy fue campo entero idéntico: lo cubre.)
3. La frescura por campo usa el mismo umbral `max_age_days` que la frescura por archivo; un campo rancio del layout ⇒
   FLAG `stale_field` con el campo y la edad mínima inferida.
4. **Sin `field_dates` ni `previous_snapshot`: no HOLD, pero nunca silencio** — el resultado lleva
   `field_freshness: "not evaluable"` como aviso informativo (el fallo de hoy fue exactamente el silencio).
Se implementará solo tras registrar esta redacción en CURRENT_TRUTH y antes del siguiente claim limpio que la use (E4b
está en auditoría de diseño; su desenlace queda retenido como siempre).

## Fase 2(c) — E4b (pre-registro `mirror_e4_drift_v5`, P1/P2/P3; 2026-10-13, `contaminado:false`) — codificado por CAPAS

Nuevo modo de trabajo (decisión de Osvaldo): **Atlas primero**. Atlas corre y sella el desenlace; **la sesión de CAPAS codifica**
desde datos saneados (sin cadenas de veredicto), sella veredictos (commit 7531e7c) y solo entonces abre el desenlace. Atlas
no adapta el diseño de sus experimentos a la guía de CAPAS; un fallo de CAPAS se comunica en una línea y el arreglo es de CAPAS.
Generador: `phase2c/build_claims_e4b.py` (determinista; aborta si un input trae palabra de veredicto). Claims sha256 `58b74c2b…`.

| métrica | codificado como | veredicto v6 = HEAD | desenlace sellado de Atlas | acierto |
|---|---|---|---|---|
| P1 deriva del layout | statistical_confidence (p 7,63e-6, α 0,05 nominal, 18 pares, sign-flip pareado) + snapshot 15:28 con layout rep12 | ACCEPT | DERIVA DE F EN EL LAYOUT (media +0,0466) | sí (bueno ≠ REJECT) |
| P2 persistencia | exact_model_solution con theta, IC95 [1,259, 1,550], reference_value 0,5 — **sin** abs_error/tolerance (no se inventan) | HOLD | RECUPERA | vacuo (HOLD = no-ACCEPT; no hay tipo de claim para "IC dentro de una banda pre-registrada") |
| P3 decisión (control simultáneo, gap 6,1 s) | statistical_confidence (p 7,63e-6, media −0,128 sobre F cruda, misma lectura corregida) | ACCEPT | EL LAYOUT VIEJO SIGUE MEJOR (más CZ en el control) | sí (bueno ≠ REJECT) |

Lectura honesta: los tres desenlaces coincidieron con la hipótesis pre-registrada, así que este lote solo mide
**bueno-no-REJECT** (2/2 + 1 vacuo); no hay "malo" en E4b. Cuenta limpia acumulada de Atlas: malo-no-ACCEPT **1/1** (E4),
bueno-no-REJECT **2/2** (E4b), 1 HOLD vacuo. n sigue siendo anécdota.

Hallazgo contra CAPAS (una línea, como pide el modo nuevo): **no existe tipo de claim para un intervalo contra una banda
pre-registrada** (P2; misma familia que la deuda S6 del umbral unilateral). Diseño pendiente: `interval_band_claim`
{estimate, ci, ci_level, band_rule pre-registrada} → ACCEPT solo si el IC entero cae en la banda declarada.
`field_dates` llegaron por primera vez en el snapshot de las 15:28 (t1 medido 12-oct 23:28, readout 13-oct 12:36, sx 00:23,
cz 04:08): la ley aún no las lee (regla v2 pre-especificada, sin código); sobre el layout rep12 dio PASS.

### Cierre de C-9 y C-11 (2026-10-13 ~19:30, tag `atlas-ciego-v7`) y su coste post-hoc

Implementado tal como se pre-especificó (v2, cuatro puntos de Atlas): `field_dates` manda; sin ellas, inferencia por
identidad con `previous_snapshot` (elemento a elemento en continuos, campo entero en cuantizados, edad = cota mínima);
sin ninguna, aviso `field_freshness.status = "not evaluable"`. Y el tipo `interval_band_claim` (estimate, ci_low, ci_high,
ci_level, band{low,high}, band_pre_registered): intervalo entero dentro → ACCEPT; fuera → REJECT; a caballo → REWRITE
(se licencia el intervalo, no la banda); banda no pre-registrada → REWRITE. Tests: `benchmarks/test_interval_band_claim.py`,
`benchmarks/test_calibration_snapshot.py` (incluye la calibración real de E4b con `field_dates`).

**Coste post-hoc medido (abierto, no ciego):** sobre E4b, **P1 pasa de ACCEPT a REJECT** en v7: `field_dates` revela que
el T1 del qubit 65 (en el layout rep12) se midió el 2026-10-11 21:33, 2 días calendario antes del job → `stale_field`
→ FLAG → el invariante anula el ACCEPT. P2 con el tipo nuevo daría ACCEPT (RECUPERA; no se recodifica: el sellado de
E4b no cambia). P3 sin cambio. E4 sin cambio (REJECT). Es decir: la regla v2, sobre el único lote limpio que la tiene,
convierte un claim bueno en REJECT. **Pregunta pre-registrada para Atlas, a decidir ANTES del siguiente claim limpio:**
¿un campo rancio en el layout debe ser FLAG (violación → REJECT, como se pre-especificó) o HOLD (la ley no puede juzgar
el contexto → no-ACCEPT sin REJECT)? No se cambia a posteriori con estos datos; se decide por escrito y se aplica al
siguiente.

**Decisión (2026-10-13 ~20:00, tag `atlas-ciego-v8`):** campo rancio en el layout = **HOLD**, no FLAG. Recomendación de
Atlas, adoptada por CAPAS conociendo E4b y antes del siguiente claim limpio (se declara: no es ciega): un T1 viejo no
contradice el claim, deja sin verificar el contexto de calibración; REJECT queda para evidencia que contradice. Efecto
post-hoc: E4b P1 pasa de REJECT (v7) a HOLD (v8) — vacuo, no error. Se aplica a partir del siguiente claim.

**Corrección (2026-10-13 ~20:30, tag `atlas-ciego-v9`): el "coste post-hoc" de v7 era en parte un artefacto de zona
horaria.** Al verificar v8 en vivo, el servidor (UTC) daba ACCEPT a P1 y mi máquina (-06:00) HOLD: la política de días
calendario usaba la zona de la máquina. El T1 del qubit 65 está fechado 2026-10-11T21:33-06:00 = 2026-10-12 03:33 UTC;
frente a un `job_date` 2026-10-13 son 2 días calendario en -06:00 y 1 en UTC. Un veredicto no puede depender de dónde
corre el motor: ahora los timestamps sin zona se leen en UTC (la zona de los `running` de vuestros jobs) salvo que el
snapshot declare `timezone` ("UTC", "±HH:MM" o nombre IANA), y los días calendario se cuentan en esa zona. Test:
mismo veredicto con TZ=UTC, America/Mexico_City y Asia/Tokyo. Con la regla determinista, **E4b P1 sigue ACCEPT** en
todos los motores (v6, v8, v9); con `timezone: "-06:00"` declarado sería HOLD (T1 del qubit 65 rancio), nunca REJECT.
Lección: toda aritmética de calendario del motor lleva zona explícita; `verify_determinism.py` no cubría la zona.
