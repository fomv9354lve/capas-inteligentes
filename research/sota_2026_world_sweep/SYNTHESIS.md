# Barrido mundial 2026 — síntesis comparativa y novedad epistemológica de CAPAS

Fecha: 2026-10-14. Cobertura: 197 países (193 ONU + Vaticano, Palestina, Taiwán, Kosovo), siete olas alfabéticas,
informes por país en `wave_1_A-B.md` … `wave_7_T-Z.md` (4,113 líneas, 197 entradas con plantilla fija). Brief común en
`BRIEF.md`. Todo lo citado lleva URL en el informe de su ola; lo que no se encontró se dice.

## 0. Cómo leer esto (método y límites, primero)

- **Presupuesto de búsqueda.** La sesión tenía un tope de 200 búsquedas web compartido por las siete olas; se agotó en
  la primera pasada. La segunda pasada se hizo con fetch directo a fuentes primarias y sus catálogos (arXiv, Europe PMC,
  OpenAlex, Zenodo, sitios de agencias y normas), sin rodear el tope por buscadores (el aviso de la herramienta lo
  prohíbe y los agentes lo respetaron). Consecuencia honesta: en las potencias científicas la cobertura es profunda;
  en unos 60 países pequeños es bibliográfica (lo que está en catálogos), no de prensa local. Cuatro países quedaron
  **inalcanzables** (Nauru, Nepal, Níger, Corea del Norte): ni búsqueda ni fetch; no se cuentan como "nada".
- **Tercera pasada (búsqueda real, presupuesto repuesto):** México con sus 8 búsquedas (sigue sin trabajo doméstico de
  verificación; único nodo de reproducibilidad: INSP con BITSS/CEGA; 47 % de las revistas de las principales instituciones
  sin política de IA generativa; Rosaura Ruiz, ago-2026: «la responsabilidad no puede delegarse en un modelo»); Corea,
  España, Suecia, Singapur profundizados; los cuatro inalcanzables resueltos (Nauru, Níger, Corea del Norte: nada;
  Nepal: adyacente). Ningún ranking cambió.
- **Qué significa "nada".** NOTHING FOUND = se consultó y no apareció nada relevante, ni directo ni adyacente. Son
  del orden de 95 países. Otros ~75 tienen solo trabajo adyacente (integridad, ciencia abierta, regulación). Unos 25
  tienen trabajo **directo**: sistemas o papers que verifican o gatean claims.
- **Lo que no puede encontrar este método:** actores que no publican en catálogos (laboratorios internos de empresas,
  reguladores sin web legible, trabajo en idiomas que no se consultaron). Las entradas lo declaran país por país.

## 1. ¿Alguien hace lo mismo? No. Hay piezas, no la composición.

Ningún país tiene un gate de admisibilidad de claims **determinista, fail-closed, sin modelo en el veredicto, con
tasas ciegas selladas y ledger público**. Lo más cercano, por distancia creciente:

| Sistema (país, fecha) | Comparte con CAPAS | No comparte |
|---|---|---|
| **metacheck** (NL, TU/e+VU+Glasgow, beta jun-2026) | reglas primero (statcheck, RegCheck paper-vs-prereg, cruces con Retraction Watch/PubPeer), LLM opcional y declarado | es un **informe asesor**, se niega a puntuar o dictaminar; sin tasas ciegas; sin fail-closed |
| **Triage-PiEvo** (CN, Westlake/Kuaishou, oct-2026) | admisión de evidencia por reglas, fail-closed (0 % evidencia no fiable admitida vs 100 % sin gate) | es un filtro de evidencia para un agente, no un veredicto sobre claims; sin sellado ni ledger |
| **SOCpilot / AutoPyVerifier** (US, 2026) | eligen verificador determinista sobre juez LLM por auditabilidad; traza tipada por corrida | el LLM **construye** el verificador; sin tasas ciegas; sin disciplina de fuga |
| **Kirsch, "Untrusted Authors, Trusted Answers"** (CZ, CTU, jul-2026) | plano LLM no confiable + verificador verificado (Lean 4) + grados de fidelidad | matemáticas/lógica, no evidencia empírica; sin corpus ciego |
| **LeanProbe / LeanFlow** (CH, EPFL, jun-2026) | el núcleo de Lean es un veredicto sin modelo; feedback verificable a agentes vía MCP | solo matemáticas; no hay noción de admisibilidad de evidencia |
| **YouRA** (KR, ETRI, 2026) | gates MUST_WORK, validador independiente, detector de datos simulados, números solo desde estado registrado | juzgado por LLM de punta a punta; sin ventaja medida contra alucinación |
| **ETH "Read the paper, write the code"** (CH, abr-2026) | el agente reproductor está **aislado** de código, resultados y paper (disciplina de ciego) | el juez es comparación celda a celda, no un gate; sin sellado por hash |
| **SciTrue** (NZ, Auckland, EACL 2026) | seis etiquetas de veredicto incl. "overstated" | **modelo en el veredicto**, sin evaluación sellada: es el contraejemplo limpio |
| **SCI-Verifier** (CN, Shanghai AI Lab, ICLR 2026) | taxonomía de equivalencias reutilizable para REWRITE | rechaza explícitamente el diseño por reglas: el **antipolo** |
| **MBZUAI "claim-calibrated evidence ladder"** (AE, 2026) | el principio ACCEPT/REWRITE/HOLD por nivel de evidencia | principio, no mecanismo; y su auditoría cruzada (F1 0,70 → 0,31 fuera del benchmark) es la cita de por qué un verificador LLM no puede ser la capa de veredicto |

Lectura: el campo ya **nombró el problema** en 2026 (taller NeurIPS "AI for Science: Verification in the Age of AI
Scientists", 12-dic-2026; survey "AI Scientists and the Verification Gap": 26 sistemas, 38 % con artefactos de
reproducibilidad, **ninguno con oráculo externo validado en el bucle**). CAPAS+Atlas es, en lo encontrado, el único
par oráculo-gate con tasas ciegas publicadas y límites medidos.

## 2. ¿Alguien sella como nosotros? Parcialmente, y nadie congela el motor.

- **Brasil, Iniciativa de Reproducibilidad (eLife, jul-2026):** criterios declarados antes de abrir, comités de
  validación ciegos al resultado, 143 → 53 invalidadas → 90 válidas, 20–44 % según criterio. Es el mejor modelo de
  **reporte** de lote sellado (publicar el conteo de invalidaciones).
- **Hungría, Transparent Psi / AMP (ELTE):** datos "nacidos abiertos", informes en tiempo real, diseño de consenso
  adversarial, auditores externos. Es el protocolo humano que CAPAS mecaniza.
- **Suiza, ETH (abr-2026):** aislamiento del evaluador respecto de la respuesta.
- **Nadie** congela el **motor** en un tag antes de codificar y sella los veredictos por hash antes de abrir el
  desenlace. Esa es la diferencia operativa: en CAPAS el instrumento de medición está prerregistrado, no solo el análisis.

## 3. ¿Alguien publica un ledger de sus propios números? No en esta forma.

- **Dissernet (RU):** ledger ciudadano a escala nacional (14,054 tesis, 1,801 grados revocados) sobre terceros.
- **Survey del verification gap (US, 2026):** propone una lista de verificación para revisores; 83 % publica código,
  38 % artefactos reproducibles.
- **Ningún proyecto** encontrado etiqueta cada número propio como CLOSED/BACKED/SCOPED con el release bloqueado si un
  número queda huérfano, ni verifica que la página pública coincida con el ledger. El vocabulario más cercano son los
  "grados de fidelidad / clases de aseguramiento" de Kirsch (CZ), que CAPAS puede adoptar.

## 4. ¿Alguien hace contra-firma adversarial con otra familia de modelos? No como mecanismo.

- **UK AISI, "LLM judges on trial" (jul-2025):** marco bayesiano para medir el sesgo de un autograder por tarea; la
  conclusión es "verifica la fiabilidad del juez antes de usarlo", no "no uses juez".
- **IBM Research JuStRank (IL, 2025):** 1,5 M juicios; el sesgo y la decisividad del juez distorsionan rankings.
- **Brodeur et al., PNAS (AU/BE/CO, jun-2026):** 288 investigadores, 103 equipos: reproducción 94 % solo humanos,
  91 % asistida, **37 % dirigida por IA**. Es la cifra externa del costo de poner un modelo al mando del veredicto.
- Nadie encontrado hace que un modelo de **otra empresa** ataque los claims propios con comandos ejecutados y publique
  las refutaciones como tests. Eso sigue siendo propio de CAPAS.

## 5. ¿Alguien ingiere contexto de máquina con hash? El campo converge ahí, sin veredicto.

- **Alemania, PTB DCC + D-SI:** certificados de calibración digitales **firmados**, legibles por máquina, con
  distribución de incertidumbre y fecha por parámetro; conferencia feb-2026; despliegue industrial 2027. Es el objetivo
  natural del adaptador de calibración más allá de Qiskit.
- **China, GB/T 47468-2026** (métodos de prueba de desempeño de sistemas cuánticos; vigente 1-nov-2026): dice **cómo
  medir**, no si un número reportado es admisible contra una foto congelada. Eso sigue siendo terreno de CAPAS/Atlas.
- **Rumania/Polonia, REWIRE (Horizon 2026–29):** planes de reproducibilidad, entornos reconstruibles (Guix) y paquetes
  RO-Crate: artefactos accionables por máquina listos para ingerir como evidencia declarada.
- **Japón, JST–G-Search (mar-2026):** una agencia nacional reposiciona sus datos bibliográficos estructurados como
  capa de grounding a prueba de alucinación. **Países Bajos, Open Science NL (35,5 M €):** ReproRun, Hippocampus
  (trazado completo de experimentos "para que resultados de IA puedan verificarse"). **ReAgent (2026):** auditoría
  estática+dinámica de que los números del paper salen del repositorio.
- Ninguno conecta la ingesta con un veredicto fail-closed. CAPAS lo hace desde el 14-oct-2026 (adaptadores 1–3).

## 6. Cómo enmarca cada bloque lo que sabe y lo que no

| Bloque / país | Marco epistémico dominante | Valor por defecto |
|---|---|---|
| Estados Unidos | "verification gap", auditabilidad a nivel de claim, honestidad epistémica (abstención, "do LLMs know what they don't know"), **Predictive Value of Pass**: con presupuesto de verificación fijo, rodear falsedades de verdades sube la probabilidad de pasar y baja la informatividad | mixto; la frontera es el **presupuesto** de verificación |
| Reino Unido | "ciencia de las evaluaciones": el juez es un instrumento de medición con sesgo medible; MHRA autoriza por etapas contra umbrales prefijados | fail-open con medición del juez |
| Países Bajos | **severidad** (Mayo/Lakens): el prerregistro vale porque permite a otros saber qué habría refutado | asesor, nunca puntúa |
| Alemania | **metrología**: la incertidumbre es ciudadana de primera clase, firmada y fechada | determinista, no declarado fail-closed |
| Israel | **prueba que un tercero re-verifica** (PICID: el verificador emite pruebas comprobables "para no depender de la salida del verificador") | fail-closed por construcción |
| Hungría | consenso adversarial, datos nacidos abiertos, auditores externos | protocolo humano |
| Austria | **ley**: "para la formación del juicio no se admiten aplicaciones de IA" (ÖAWI 2026 §3.5a) | fail-closed normativo |
| México | "**si una decisión no puede explicarse, no debe automatizarse**" (Chapultepec P3, ene-2026) + verificar resultados, reproducir procesos, declarar IA | principio sin mecanismo |
| China | procedencia y sanciones (etiquetado, retiro de papers con IA); en los laboratorios, **recompensas por reglas** porque el modelo-juez sufre hackeo (DeepSeek-R1 §2.2.2; Tencent "un token engaña al juez") y, al mismo tiempo, verificadores-modelo (SCI-Verifier) | dividido: el mapa de posicionamiento |
| Japón | procedencia de los **insumos** (grounding bibliográfico, Lean para "alucinación semántica") | asistido por LLM en el bucle |
| Brasil / Perú / Turquía / Ucrania / India | sanción como fail-closed institucional: salida de IA como autoría humana prohibida (CNPq), compra de autoría expulsada (Perú), referencias fabricadas sancionadas (TÜBİTAK), "violación institucional" (Ucrania, ley 4742-IX), retracciones penalizan rankings (NIRF) | fail-closed por castigo, no por mecanismo |
| Lituania | verificación **previa** y auditoría regular de toda herramienta de IA usada en investigación (directrices 2024) | requisito nacional sin herramienta |
| Vaticano | "reproducibilidad, procedencia, transparencia y revisión por pares" como respuesta a la ciencia generada por IA (PAS 2026) | normativo |
| Microestados y la mitad de África/Asia central/Pacífico | sin marco propio | — |

Patrón: donde hay instituciones fuertes, la respuesta es **o medir al juez o castigar al autor**; donde hay metrología,
**firmar la incertidumbre**; donde hay formalistas, **pruebas re-verificables**. Ningún bloque junta las tres cosas
con una regla de silencio (lo no declarado no se acepta) aplicada a sí mismo.

## 7. Mapa de gaps

**Lo que el campo pide y CAPAS ya tiene**
- Un oráculo externo validado en el bucle (survey 2608.05179): Atlas sobre hardware real con desenlaces sellados.
- Verificación determinista como frontera de aplicación, juez solo para el residuo semántico (consenso práctico US).
- Cumplimiento mecánico de normas que hoy son texto: ÖAWI 2026 §3.5a, Chapultepec P3, Lituania §30–32, CNPq 2.664.
- Los tres deberes de Chapultepec (verificar, reproducir, declarar) como campos exigidos, no como principios.

**Lo que el campo tiene y CAPAS no**
- Certificados de calibración firmados con incertidumbre (PTB DCC/D-SI). → adaptador.
- Pruebas re-verificables por terceros con un verificador mínimo (PICID). → el hash de auditoría debe volverse certificado reproducible.
- Medición formal del sesgo de un juez (AISI) para comparar CAPAS contra un LLM-juez en el mismo lote sellado.
- RegCheck (diferencia paper vs prerregistro) y cruce con Retraction Watch (metacheck; Labenbacher 2026: ningún GenAI detecta fiablemente literatura retractada). → reglas estructurales baratas.
- Vocabulario de grados de fidelidad (Kirsch) y taxonomía de equivalencias (SCI-VerifyBench) para REWRITE.
- Canal de distribución: la Federación Global de Redes de Reproducibilidad (23 redes, oficina en SwissRN).
- Un argumento formal del presupuesto de verificación (PVP): cuánto hay que verificar por lote para que "pasó" informe.

**Lo que no tiene nadie**
- Motor congelado y prerregistrado como instrumento, veredictos sellados antes del desenlace, tasas ciegas publicadas
  **con la fuga declarada** (los claims sellados son datos de entrenamiento una vez escritas reglas a partir de ellos).
- Un ledger de números propios con bloqueo de release y verificación página-contra-ledger.
- Contra-firma por otra familia de modelos con comandos ejecutados y refutaciones congeladas como tests.
- Ingesta de contexto de máquina **atada** a un veredicto fail-closed.

## 8. La novedad epistemológica defendible (una página)

**Tesis.** CAPAS no verifica verdad. Licencia la reutilización de un claim bajo una **regla de silencio**: lo que no
está declarado en campos no se acepta; lo que contradice se rechaza; lo que no se puede juzgar se detiene. Y aplica
esa misma regla a sí mismo: sus números viven en un ledger con estatus, sus claims son atacados por otra empresa, y
su desempeño ciego pertenece al motor congelado, no al motor de hoy.

**Por qué es nuevo, dicho sin exagerar.** Cada pieza existe en algún país: el veredicto sin modelo (núcleo de Lean en
Suiza, metrología en Alemania), el aislamiento del evaluador (ETH, Brasil, Hungría), la medición del juez (UK), la
regla normativa (Austria, México), la ingesta estructurada (PTB, JST, REWIRE). Lo que no existe es la **composición
con autoaplicación**: un instrumento de medición prerregistrado que publica su tasa de error ciega, declara su fuga y
somete sus propias afirmaciones al mismo gate. Ese es el objeto epistemológico: **un verificador que es, él mismo, un
claim sellado**.

**Lo que la tesis admite, porque está medido.** No detecta fraude (888 limpios vs 6,348 retractados: sin separación).
No lee prosa. Una fabricación consistente pasa (techo GIGO). Deja pasar uno de cada tres malos a ciegas en el corpus
agrupado. El motor actual no tiene tasa ciega hasta el siguiente lote sellado. El PVP (US/PL 2026) da la forma
matemática de ese techo: con presupuesto de verificación fijo, la informatividad de "pasó" cae cuando el emisor rodea
falsedades de verdades; la respuesta de CAPAS, HOLD ante silencio, es exactamente el mecanismo que esa teoría pide.

**Frase para la portada, si se quiere:** "El campo mide a los jueces o castiga a los autores. CAPAS prerregistra al
instrumento y publica cuándo se equivoca."

## 9. Plan: cinco acciones, cada una con su origen y el test que la cierra

1. **Presupuesto de verificación por lote (PVP).** Declarar en cada lote sellado cuántos campos se verificaron contra
   artefacto y cuántos solo se leyeron; publicar la cobertura. Origen: arXiv 2610.05547 (US/PL, oct-2026). Test: entrada
   de ledger `verification_budget` por lote y fallo de release si la cobertura no está declarada.
2. **Adaptadores 5 y 6: DCC/D-SI (PTB) y RO-Crate/Guix (REWIRE).** Certificado de calibración firmado → snapshot con
   incertidumbre por parámetro; paquete RO-Crate → artefacto de reproducibilidad declarado. Test: fixtures de ambos
   formatos; firma inválida o hash que no cuadra → HOLD (esto cierra también el adaptador 4, procedencia en el motor).
3. **Hash de auditoría → certificado re-verificable (PICID).** El veredicto emite la traza de reglas aplicadas y un
   verificador mínimo independiente la re-ejecuta sin el motor. Test: script de replay de terceros en CI sobre los
   veredictos sellados; cualquier divergencia rompe el build.
4. **CAPAS vs LLM-juez en el mismo lote sellado (AISI + Brodeur).** Prerregistrar X6 (de Atlas) con dos jueces: CAPAS y
   un LLM de otra familia; medir sesgo del juez con el marco bayesiano de AISI; usar el 37 % vs 94 % de PNAS como prior
   declarado. Test: prerregistro sellado antes de codificar; publicación de ambas tasas con intervalos.
5. **Dos reglas estructurales baratas (metacheck, Labenbacher).** `cited_doi ∈ Retraction Watch → HOLD`; diferencia
   paper-vs-prerregistro → REWRITE. Test: tests de regresión + costo post-hoc sobre X1–X5 declarado dentro de muestra.

**Posicionamiento, sin costo de ingeniería:** enviar el protocolo sellado al taller NeurIPS 2026 "Verification in the
Age of AI Scientists" (12-dic-2026); citar Chapultepec P3 y ÖAWI §3.5a en la portada como normas que CAPAS cumple
mecánicamente; pedir asiento en la Federación Global de Redes de Reproducibilidad (SwissRN) como canal; mapear los
invariantes de Atlas contra GB/T 47468-2026 y el coeficiente de anomalía axial (Hayata & Yamamoto, PRR sep-2026) como
invariante nuevo.

## Apéndice A. Países con trabajo directo (sistemas o papers que verifican/gatean claims)

Estados Unidos, Reino Unido, Suiza, Países Bajos, Alemania, Israel, Francia, China, Japón, Corea del Sur, Chequia,
Canadá, Nueva Zelanda, España, Emiratos Árabes Unidos, Taiwán, Brasil, Australia, Austria, Rusia (nivel texto), Suecia,
Singapur, Hungría (protocolo), Polonia (PoVisLE), Uruguay (PhotoHolmes, forense determinista). México: ninguno; solo
política (Chapultepec, SNPCyH, UNAM) y capacidad (Coatlicue).

## Apéndice B. Conteos de "nada encontrado" por ola

Ola 1 (A–B): 25 de 28 sin trabajo directo; 4 sin nada en absoluto (Afganistán, Andorra, Bielorrusia, Benín). Ola 2 (C–E):
16. Ola 3 (F–I): 11. Ola 4 (J–M): 16. Ola 5 (N–R): 9, más 4 inalcanzables. Ola 6 (S): 16. Ola 7 (T–Z): 13. Los
nombres están en cada `## Wave summary`.
