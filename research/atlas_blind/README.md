# Lote ciego de Atlas (corridas GHZ de junio 2026) — ley `calibration_snapshot`

Ley congelada en `atlas-ciego-v1` (bd50eff) antes de leer el lote. Lote: 4 casos A–D, snapshot completo de
ibm_kingston (155 qubits / 176 aristas) medido 2026-06-22, job 2026-06-23, con `layout`. Desenlace sellado
por Atlas (sha256 c2a1abc0…), regla declarada antes: GOOD = TVD(ideal, QPU) < 0,15; DEGRADED ≥ 0,15;
acierto = PASS↔GOOD, FLAG↔DEGRADED.

Dos archivos sellados ANTES de abrir desenlaces (`outcomes_file_opened: false`):
- `DE_CAPAS_veredictos_atlas_2026-06.json` — política completa (fijada por Osvaldo 2026-10-13: absoluta +
  relativa, frescura mismo día): A FLAG (sólo stale) · B FLAG · C FLAG (sólo stale) · D FLAG.
- `DE_CAPAS_veredictos_atlas_2026-06_physics_only.json` — misma ley sin `job_date`: A PASS · B FLAG · C PASS · D FLAG.

El suplementario existe porque las 4 corridas usaron snapshot del día anterior: la regla de frescura a 1 día
marca A y C por sí sola y taparía si los filtros físicos discriminan. Se reportan las dos filas; el doble
conteo (Atlas y CAPAS, sobre los mismos archivos sellados) se añade abajo cuando Atlas revele.

## Doble conteo (revelado por Atlas 2026-10-13; sello verificado c2a1abc0…; batch 19cae306… coincide)

| caso | corrida | TVD | desenlace | política completa | filtros físicos |
|---|---|---|---|---|---|
| A | ghz4_embed_GOOD | 0,064 | GOOD | FLAG (solo stale) ✗ | PASS ✓ |
| B | ghz4_embed_TLS | 0,465 | DEGRADED | FLAG ✓ | FLAG ✓ (120_121 0,201; 121_122; q121 T1 11 µs) |
| C | ghz6_GOOD | 0,081 | GOOD | FLAG (solo stale) ✗ | PASS ✓ |
| D | ghz6_TLS | 0,782 | DEGRADED | FLAG ✓ | FLAG ✓ (111_112 0,142; 112_113 1,0; 113_114) |

**Política completa 2/4 · filtros físicos 4/4.** Conteo de Atlas y de CAPAS idénticos sobre los mismos archivos
sellados. Lectura pre-declarada (en el mensaje a Atlas, antes de la revelación) confirmada tal cual: los filtros
físicos discriminan; «mismo día» es política, no física, y marcó dos corridas buenas con snapshot de 1 día.
Atlas propone `max_age_days: 1` (IBM recalibra ~a diario); decisión de Osvaldo. **n = 4 (2 por clase), GHZ
pequeños: es un control, no validación estadística.** Registro de Atlas: `benchmarks/capas_blind/DOUBLE_COUNT_2026-06.md`.
