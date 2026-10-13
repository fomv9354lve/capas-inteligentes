# Retraction audit — ¿qué fracción del fraude retractado cae CAPAS sin leer el texto?

**Estado (2026-10-12): primera pasada completa. Resultado: HOLD — señal sugerente, no tasa.**

Ground truth: Retraction Watch vía Crossref Labs (`https://api.labs.crossref.org/data/retractionwatch`,
73.145 retractaciones). Filtro: `Reason` contiene "Falsification/Fabrication of Data", con PMID,
tipo Research Article → **1.269 papers** (`data/fab.json`). Control: papers Open Access de las
mismas revistas, 2012–2022, no presentes en Retraction Watch (`data/ctl_ft.json`, 116 con texto).

Texto completo vía Europe PMC `fullTextXML` (la ruta NCBI BioC rechazó artículos CC-BY conocidos
y falló su propio control; no usar). Disponibilidad medida: ~18% de los fabricados.

## Pipeline
```
dl_all.py      -> xml/           texto de los fabricados (Europe PMC, reanudable)
extract.py     -> items          prosa: "k/N (p%)", "stat(df)=v, p=…"; tablas: celdas "k (p%)"
                                 bajo columna con "n = N" en cabecera, con puerta de
                                 autoconsistencia (si N no explica >=70% de su columna,
                                 se leyó mal: NO se chequea)
run_audit.py   -> audit_results  cada item -> capas_invariants.audit -> PASS/FLAG
```

## Lo aprendido hasta ahora
- El set de fabricación es 43% biología de laboratorio: el fraude está en **imágenes**, no en
  números. Para esos papers no hay nada recomputable. La señal, si existe, vive en clínica y
  psicología. Estratificar antes de reportar.
- Tres bugs de extracción produjeron 101 falsos positivos en controles limpios (decimales
  inferidos del float, p-valor puntual en vez de intervalo statcheck, colspan ignorado en
  tablas). Corregidos; quedan ~27, que al inspeccionarlos son errores de reporte reales.
- GRIM no se aplica a medias de tabla: la mayoría son variables continuas. Desactivado.
- Dos leyes nuevas en el motor salieron de esto: `pvalue_test` (statcheck) y `reported_percent`.

## Qué NO se puede afirmar
Ninguna tasa de detección. n chequeable es de un dígito en fabricados. Un FLAG es "inconsistente",
no "fraude": statcheck encuentra inconsistencias en ~50% de la literatura limpia.

## Resultado de la primera pasada (2026-10-12)

Descargados 175/1.269 fabricados con texto (13,8%). Control: 116.

| grupo | papers | con algo chequeable | papers con ≥1 FLAG | items | FLAGs | % items |
|---|---|---|---|---|---|---|
| fabricados | 175 | **11 (6%)** | 5 (45% de los chequeables) | 150 | 11 | **7,3%** |
| control | 116 | 17 (15%) | 7 (41%) | 875 | 29 | **3,3%** |

Fisher exacto por ítem: OR ≈ 2.3, p ≈ 0.03. Por paper (entre chequeables): OR ≈ 1.2, p ≈ 1.

**Lo que esto dice y lo que no.**
- A nivel de paper no hay separación: 45% vs 41%. Un FLAG es "inconsistencia", y la literatura
  limpia las tiene (statcheck: ~50% de los papers de psicología).
- A nivel de ítem los fabricados fallan 2,2× más, con p ≈ 0.03 — sugerente, sobre **11 papers**.
  No es una tasa de detección. Es una hipótesis para un n mayor.
- El hallazgo estructural es el 6%: **94% de los papers retractados por fabricación no tienen
  nada recomputable en el texto.** El fraude de este corpus vive en imágenes de biología.
  La detección numérica solo puede hablar del 6% restante.
- Cualitativamente, los flags en fabricados son de otra especie que los de control: tres
  F-tests en un mismo paper (J. Neuroinflammation, retractado) con p reportado 0.17–0.21 que
  recomputan a p < .05; un `80/81 (100%)`; un `0/40 (1.9%)`. Los de control son redondeos y
  erratas. **Graduar severidad** (error de decisión, cuenta imposible vs. redondeo) es la
  siguiente hipótesis a probar, no un resultado.
- Tres flags en fabricados (28.6→28, 68.9→68) son truncamiento, no error. La ley de porcentajes
  debería aceptar truncamiento como convención alternativa; afecta a ambos grupos.

**Lo que salió del experimento para el motor:** dos leyes nuevas (`pvalue_test` statcheck con
método de intervalo, `reported_percent`), `check_sum` con errores estándar, y el estado HOLD.
