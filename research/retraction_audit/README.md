# Retraction audit — ¿qué fracción del fraude retractado cae CAPAS sin leer el texto?

**Estado (2026-10-12): en curso. Sin resultado reportable todavía.**

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
