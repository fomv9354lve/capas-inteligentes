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
