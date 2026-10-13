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
