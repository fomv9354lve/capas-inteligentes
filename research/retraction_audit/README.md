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

## Segunda pasada: severidad y puerta de columnas (2026-10-12, mismo día)

Dos cambios. (1) La puerta de autoconsistencia se saltaba columnas con <3 celdas y aceptaba
`k > N`: un solo control (`PMC8216857`) aportaba 9 de 14 flags severos por un N mal leído.
Corregido para ambos grupos. (2) Cada flag se gradúa: `decision_error` (p recalculado cruza .05),
`impossible` (k > N, 100% con 80/81, 0/40 = 1.9%), `numeric_mismatch`, y los no severos
`rounding` / `truncation`.

| grupo | items | FLAGs | % | severos | % severos |
|---|---|---|---|---|---|
| fabricados (11 papers chequeables) | 150 | 11 | 7,3% | 8 | **5,3%** |
| control (17 chequeables) | 804 | 14 | 1,7% | 6 | **0,7%** |

Fisher severos por ítem: **OR 7,5, p = 0,0004**. Por paper: sin separación (3/11 vs 5/17).

La separación es por ítem, no por paper: un paper fabricado chequeable concentra más
inconsistencias severas, pero "tener al menos una" no distingue. **Sigue sobre 11 papers.**
La tanda 2 (clínica/psicología, razones de datos, 7.934 candidatos) está descargando; su etiqueta
es más débil ("Unreliable Results" domina) y hay que estratificar por razón antes de sumar.

## Tercera pasada: corpus completo estratificado por razón (2026-10-13)

Tanda 2: 7.934 retractaciones en clínica/psicología con razones de datos; 6.185 con texto. Control
sin cambios (116). Estratificación por la **primera razón que casa, por orden de fuerza** (un paper
puede llevar varias). Severo = error de decisión, cuenta imposible o desajuste numérico.

| razón | papers | chequeables | items | severos | % sev | OR vs ctl | p |
|---|---|---|---|---|---|---|---|
| Falsification/Fabrication of Data | 175 | 11 | 150 | 8 | 5,3 | 7,49 | 0,0004 |
| Unreliable Data | 345 | 9 | 195 | 1 | 0,5 | 0,69 | 1 |
| Error in Data | 151 | 18 | 499 | 7 | 1,4 | 1,89 | 0,26 |
| Error in Results and/or Conclusions | 67 | 15 | 521 | 5 | 1,0 | 1,29 | 0,76 |
| Unreliable Results | 5.569 | 616 | 16.725 | 265 | 1,6 | 2,14 | 0,057 |
| **control** | 116 | 17 | 804 | 6 | 0,7 | — | — |

Agregados: fuertes (fab + unreliable/error in data) 1,9% vs 0,7%, OR 2,56, p 0,053. Todos: 1,6% vs
0,7%, OR 2,14, p 0,058. **Por paper no hay separación en ningún estrato** (119/670 = 18% vs 5/17 =
29%).

**Lectura.** La señal fuerte (OR 7,5) vive sólo en "Fabrication of Data" y sobre 11 papers. Al
bajar a etiquetas más débiles la razón de probabilidades cae a ~2 y deja de ser significativa. El
cuello de botella es ahora **el control: 17 papers chequeables y 6 ítems severos no anclan nada**. Se
está descargando un control de ~800 papers de las mismas 60 revistas. Hasta entonces, ninguna de
las razones por encima de la primera fila es un hallazgo.

Dos bugs míos corregidos en esta pasada, ambos del lado del experimento: truncaba la razón de
retractación a 120 caracteres (4.541 papers caían en "?"), y la lista de control se construía con
una query sin codificar. Ninguno toca el motor.

## Resultado externo relacionado: corpus ciego de Ginibre (2026-10-13)

No es parte de este experimento, pero es la primera tasa ciega del motor y conviene tenerla al
lado. 176 claims de un proyecto real (110 malos / 66 buenos), evidencia codificada por dos agentes
sin ver el desenlace, motor congelado (`ginibre-ciego-v1` = a78cadf). Sin contaminar: detección
53/82 = 0,65 [0,54–0,74]; buenos no rechazados 52/63 = 0,83 (0,94 como cota al corregir una
traducción). Reproducido 176/176 entre las dos sesiones. Ficheros, hashes e informe en el repo de
Ginibre, `CAPAS_CORPUS_2026-10-12/`. Límites literales de Ginibre: un proyecto, números del
codificador en ~20 claims, "bueno" = ausencia de corrección posterior.

## Cuarta pasada: control grande. Veredicto final: REFUTADO como vía de detección (2026-10-13)

Control de 888 papers OA no retractados, mismas 60 revistas, 2012–2022; 86 chequeables, 3.988 ítems.

| grupo | papers | chequeables | items | severos | % sev | OR vs ctl | p |
|---|---|---|---|---|---|---|---|
| Falsification/Fabrication of Data | 175 | 11 | 150 | 8 | 5,3 | 2,59 | 0,019 |
| Unreliable Results | 5.569 | 616 | 16.725 | 265 | 1,6 | 0,74 | 0,020 |
| todos los retractados por datos/resultados | 6.308 | 670 | 18.093 | 286 | **1,58** | 0,74 | 0,017 |
| **control** | 888 | 86 | 3.988 | 85 | **2,13** | — | — |

Por paper: 17,8% de retractados chequeables con ≥1 severo vs 19,8% de controles. OR 0,88, p 0,66.

**Lo que esto dice.** El control de 17 papers de las pasadas anteriores era bajo por azar. Con 86, la
tasa base de inconsistencias numéricas severas en literatura limpia es ~2%, en línea con lo que
statcheck lleva una década midiendo. Los papers retractados por razones de datos **no tienen más**:
en el agregado tienen ligeramente menos. La única franja que conserva señal es "Falsification/
Fabrication of Data" (5,3% vs 2,1%), sobre 11 papers; sin más n no es un hallazgo.

**Conclusión.** Las inconsistencias numéricas recomputables desde el texto **no separan** papers
retractados de limpios en este corpus. Como vía de detección de fraude a escala, refutada. El
motor no falló: midió bien, y lo que midió es que la señal no está donde se buscaba. Queda en pie
el hallazgo estructural (94% del fraude por fabricación no tiene nada recomputable en texto) y
las siete leyes que el experimento dejó en el motor.
