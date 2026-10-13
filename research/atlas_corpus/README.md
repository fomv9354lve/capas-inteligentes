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
