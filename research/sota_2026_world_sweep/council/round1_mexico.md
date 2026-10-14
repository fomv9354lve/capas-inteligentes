# Ronda 1 — México / redes latinoamericanas de reproducibilidad

Fuentes: `wave_4_J-M.md`, `wave_1_A-B.md`, `wave_5_N-R.md`, `wave_6_S.md` (GFRN), repo.

## 1. Gigantes que traigo

1. **Principios de Chapultepec, P3** (SECIHTI+ATDT, 29-ene-2026; https://secihti.mx/wp-content/uploads/2026/02/Principios_Chapultepec_F.pdf). CAPAS hereda los **tres deberes** de la cláusula de investigación como campos: *verificar resultados* → `independent_reproduction_pass`; *reproducir procesos* → `artifact_available`; *declarar el uso de IA* → campo que **hoy no existe** (§2, faltante A). P2 ("mecanismos de corrección") → `hold_has_resolution` (CLOSED).
2. **SNPCyH, Lineamientos DOF 27-may-2026 + criterios de admisibilidad** (https://secihti.mx/snpcyh/criterios-de-admisibilidad/). Hereda la palabra *admisibilidad* a nivel revista y el **hueco**: ningún criterio sobre datos, IA o retracciones en 513 revistas evaluadas por >300 SNII. El hueco es el canal.
3. **Iniciativa Brasileña de Reproducibilidad** (eLife RP, 10-jul-2026; https://elifesciences.org/reviewed-preprints/111001). Hereda la **plantilla de reporte de lote sellado**: criterios declarados antes de abrir, invalidaciones públicas con causa (53/143), rango por criterio (20–44 %), resumen "≥ mitad de criterios" (27 %).
4. **Portaria CNPq 2.664/2026** (https://www.in.gov.br/web/dou/-/portaria-cnpq-n-2.664-de-6-de-marco-de-2026-691779232). Hereda la forma de la declaración de IA: **herramienta + propósito + fase**; y "beca obtenida con afirmaciones infundadas → revocación" como ancla del beachhead regulado.
5. **Perú, DS 062-2024-PCM** (https://gestion.pe/peru/concytec-investigadores-que-compren-autorias-seran-expulsados-y-multados-por-el-sinacti-noticia/). Hereda el contraejemplo: Concytec prometió "IA para detectar fraude" sin evaluación; CAPAS midió eso (888 vs 6 348, sin separación) y lo declinó.
6. **Rede Brasileira de Reprodutibilidade** (https://www.reprodutibilidade.org/) y la **Federación Global de Redes de Reproducibilidad** (23 redes, oficina en SwissRN; https://crsuzh.pages.uzh.ch/swissrn/contents/news/posts/2026-04-22b/GFRN.html). Hereda la **forma institucional**: peer-led, directorio, embajadores, guías prácticas. Admite redes, no herramientas. México no está en la lista de UKRN (https://www.ukrn.org/international-networks/).

## 2. Crítica del plan

1. **PVP — KEEP, cambiando la forma.** Cobertura publicada en plantilla BRI: declarada antes de abrir, campos *leídos* vs *verificados contra artefacto*. Test: entrada `verification_budget` por lote; release falla si falta; `verify_page_matches_ledger.py` la compara.
2. **Adaptadores DCC y RO-Crate — CHANGE el orden.** Ningún laboratorio mexicano emite DCC; COFEPRIS importa por *reliance*. RO-Crate primero (deber 2 de Chapultepec); DCC cuando haya socio que los produzca. Test: RO-Crate con hash que no cuadra → HOLD vía `verify_sources`.
3. **Certificado re-verificable — KEEP, va primero.** Vuelve literal a P3: la decisión *se explica* porque un tercero la re-ejecuta sin el motor. Test: replay en CI sin importar `capas.py`; divergencia rompe el build; un evaluador SNII lo corre con `python3` y nada más.
4. **CAPAS vs LLM-juez en X6 — CHANGE.** Prerregistrar y sellar, sí. Desacuerdo: el 37 %/94 % de Brodeur mide *reproducción dirigida por IA*, no *juicio*; como prior cruza tareas. Entra SCOPED, nunca como prior. El reporte trae las invalidaciones de ambos jueces (BRI). Test: prerregistro sellado, dos tasas con intervalos, invalidaciones publicadas.
5. **Retraction Watch + diferencia paper/prerregistro — KEEP.** El cruce de DOI exige base viva: sin conexión → HOLD explícito, nunca silencio. La desviación de protocolo es lo que invalidó 53 réplicas en BRI. Test: regresión + costo post-hoc en X1–X5 declarado dentro de muestra.

**Faltantes:**
- **A. Campo `ai_use_declared` {tool, purpose, phase}** (Chapultepec deber 3 + CNPq 2.664). El corpus Ginibre fue escrito por sesiones de IA (commit 4ec4c45) y el motor no lo exige. Test: payload de origen IA sin el campo → REWRITE "declara el uso de IA"; `false` con procedencia IA → REJECT.
- **B. Reporte de lote en plantilla BRI**, retroactivo a X1–X5 como dentro-de-muestra. Test: generador determinista + verificador página-contra-ledger extendido.

## 3. Orden (90 días)

Días 1–15: acción 3 + entrada de ledger. 15–30: acción 5 + campo A. 30–60: acción 1 + reporte B retroactivo. 60–90: prerregistro X6 y RO-Crate; DCC pospuesto. Cada paso = código + test + entrada con estatus.

## 4. Adelante / atrás

**CAPAS adelante:** en México no hay herramienta, programa ni política con mecanismo; P3 es principio sin motor, SNPCyH opera a nivel revista, nunca a nivel claim. Nada determinista, nada sellado, ningún ledger. CAPAS está solo en casa.

**Mi tradición adelante:** BRI replicó 56 experimentos con 56 laboratorios en 7 años con comités humanos ciegos; CNPq y Perú sancionan con dientes; SNPCyH tiene 513 revistas y >300 evaluadores. Legitimidad institucional: CAPAS tiene cero, y la Federación admite redes, no herramientas.

## 5. Líneas rojas

1. No firmo "CAPAS cumple/implementa Chapultepec" ni nada que suene a aval de SECIHTI. P3 es orientador; solo "satisface mecánicamente la cláusula de investigación de P3".
2. No firmo una red fundada, hospedada o condicionada por la herramienta. La red es de personas e instituciones; CAPAS es una entrada en su catálogo.
3. No firmo "detector de fraude" en ninguna superficie, ni priors de otra tarea sin etiqueta SCOPED.

## 6. Posicionamiento como referente

Los líderes se posicionan por **redes nacionales peer-led** (RBR, lista UKRN, GFRN), preprints revisados (eLife, MetaArXiv) y normas de agencia (CNPq). México no tiene red.

**Fundar la Red Mexicana de Reproducibilidad:** convocatoria desde personas, no desde Krenn·IQ. Comité promotor de ≥5 instituciones: UNAM (CCOIA: Pruneda Gross; Investigación Científica: Funes), CIMAT, Cinvestav, IPN-CIC, REMERI/CUDI como nodo de infraestructura; estatutos calcados de RBR; solicitud a la lista UKRN y luego a la GFRN. Primer producto: criterios de datos/IA/retracciones para la convocatoria SNPCyH 2027.

**CAPAS sin capturar la red:** Osvaldo entra como investigador fundador, no como proveedor; el grupo "verificación de claims" lo preside otro; CAPAS figura en las guías prácticas junto a statcheck y GRIM, Apache-2.0 para que la red lo bifurque; y la regla decisiva: **la red corre el siguiente lote sellado, no Krenn·IQ** (GOVERNANCE §6, constructor ≠ verificador). La red es el verificador de CAPAS, no su cliente.

**Paso concreto:** llegar a la reunión fundacional con el certificado re-verificable (acción 3) y el primer reporte de lote en plantilla BRI.
