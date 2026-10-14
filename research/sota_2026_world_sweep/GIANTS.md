# Sobre hombros de gigantes — lo que CAPAS hereda, de quién, y qué exactamente

Compilado el 2026-10-14 de las ocho perspectivas del consejo (`council/round1_*.md`), que a su vez citan los informes
por país del barrido mundial. Cada línea dice qué regla, formato, protocolo o número toma CAPAS de ese trabajo.
Lo que aquí se nombra se acredita en la página pública "In depth" y en el README del repositorio.

## Metrología (Alemania, China)
- **PTB, Digital Calibration Certificate (DCC)** — https://www.ptb.de/news/dcc. Hereda el objeto: un resultado de
  calibración es un documento firmado, fechado, legible por máquina, con una fecha por parámetro. `field_dates` ya es
  esa disciplina; falta el resto del registro.
- **D-SI (IMEKO TC6 2025)** — https://imeko.org/publications/tc6-2025/IMEKO-TC6-2025-003.pdf. Hereda la cuádrupla
  valor · unidad · incertidumbre (con distribución) · fecha. Hoy el snapshot lleva valor y fecha; la incertidumbre
  (`*_u`, `coverage_factor`) y la banda de guarda entran en el plan.
- **PTB AI-Met / AI.Cert (2025)** — https://www.dmet.ptb.de/. Hereda la postura: la IA apoya la evaluación de
  conformidad; la decisión queda en el procedimiento determinista. Arte previo de "sin modelo en el veredicto".
- **Fraunhofer IAIS, AI Assessment Catalog** — https://www.iais.fraunhofer.de/en/publications/studies/2023/ai-assessment-catalog.html.
  Hereda una frase para cada certificado: "complementa, no sustituye, el cumplimiento formal".
- **GB/T 47468-2026, métodos de prueba de sistemas cuánticos** — https://openstd.samr.gov.cn/bzgk/gb/std_list?p.p2=GB%2FT+47468.
  Hereda la disciplina del mensurando: un número solo es comparable con su método de prueba declarado (`method_standard`).
  Texto no leído: solo el slot, nunca una afirmación de conformidad.

## Metaciencia (Países Bajos, Brasil, Hungría, Australia, Bélgica, Colombia)
- **statcheck** (Nuijten, Tilburg) — https://statcheck.io. Hereda su única regla: recomputar p desde el estadístico y
  los grados de libertad declarados. Pendiente: la guía aún dice "p se toma como declarado".
- **metacheck** (Lakens, Mesquida, Bekkers; beta jun-2026) — https://www.scienceverse.org/metacheck/. Hereda el cruce
  con Retraction Watch y PubPeer, la fórmula "LLM opcional, declarado, solo clasificación" y la negativa a puntuar o
  rankear.
- **Severidad (Mayo, Lakens)** — https://www.tandfonline.com/doi/full/10.1080/2833373X.2024.2376046. Hereda: un
  prerregistro vale lo que habría refutado. De ahí `would_have_failed_if` en cada ACCEPT.
- **Iniciativa Brasileña de Reproducibilidad** (Amaral; eLife, jul-2026) — https://elifesciences.org/reviewed-preprints/111001.
  Hereda la plantilla de reporte de lote sellado: criterios declarados antes de abrir, invalidaciones con causa (53/143),
  rango por criterio (20–44 %), resumen "≥ mitad" (27 %).
- **Transparent Psi / AMP** (Kekecs, ELTE) — DOI 10.1098/rsos.191375, 10.1371/journal.pone.0335330. Hereda datos
  nacidos abiertos (hash al crear, no al sellar) y el orden húngaro: el oponente cofirma el protocolo antes de los datos.
- **Brodeur et al., PNAS jun-2026** — https://doi.org/10.1073/pnas.2524747123. Hereda una cita, no un prior: equipos
  dirigidos por IA reproducen 37 % frente a 94 % de humanos. Mide reproducción, no juicio.
- **repliCATS / IDEA** (Melbourne) — https://replicats.research.unimelb.edu.au/. Hereda la elicitación estructurada
  como campo humano declarado y sellable.

## Métodos formales (Israel, Suiza, Chequia, Francia, Austria)
- **PICID** (Katz Lab, HUJI; FMCAD 2026) — https://arxiv.org/abs/2503.12083. Hereda la regla: el verificador emite una
  prueba que un verificador independiente valida "para no depender solo de la salida del verificador". De ahí el
  certificado re-verificable y `capas_check.py` sin importar el motor.
- **Kirsch, "Untrusted Authors, Trusted Answers"** (CTU, jul-2026) — https://arxiv.org/abs/2607.14137. Hereda el replay
  en la fuente, los grados de fidelidad y el par "autor no confiable, verificador verificado".
- **LeanProbe / AI for Math @ EPFL** — https://aiformath.epfl.ch. Hereda: el núcleo es el único veredicto; los agentes
  reciben feedback verificable por MCP. El servidor MCP de CAPAS es diseño convergente.
- **Inria, "Leaning and Rocq'ing"** — https://www.renaissancephilanthropy.org/leaning-and-rocqing. Hereda el hueco:
  un núcleo certifica "prueba ⊢ enunciado", nunca "enunciado ⊨ intención". El techo GIGO es ese hueco.
- **ISTA, Henzinger, Alignment Monitoring** — https://arxiv.org/abs/2508.00021. Hereda: las garantías valen mientras el
  modelo coincide con la realidad; vigilar la brecha. `max_age_days` y la regla de fuga son ese principio.
- **ÖAWI, Richtlinie 2026 §3.5(a)** — https://oeawi.at/wp-content/uploads/2026/07/OAWI-Richtlinie-2026.pdf. Hereda el
  número cero: "para la formación del juicio no se admiten aplicaciones de IA".

## Evaluación de IA (Reino Unido, Estados Unidos, Emiratos)
- **UK AISI, "LLM judges on trial"** — https://www.aisi.gov.uk/blog/llm-judges-on-trial-a-new-statistical-framework-to-assess-autograders.
  Hereda: un juez es un instrumento de medición cuyo sesgo se estima por tarea antes de usarlo.
- **"Reliability without Validity"** — https://arxiv.org/html/2606.19544v1. Hereda la distinción: el determinismo es
  fiabilidad; la validez necesita una etiqueta externa.
- **Bańka & Chudziak, "Predictive Value of Pass"** — https://arxiv.org/abs/2610.05547. Hereda el número: presupuesto
  mínimo de verificación para un valor predictivo objetivo. De ahí `verification_budget` por lote.
- **Ding et al., "AI Scientists and the Verification Gap"** — https://arxiv.org/abs/2608.05179. Hereda las dimensiones
  de la lista (semillas, trazas, oráculo en el bucle) y la base: 38 % con artefactos.
- **SOCpilot / AutoPyVerifier** — https://arxiv.org/pdf/2605.05501, https://www.emergentmind.com/papers/2604.22937.
  Hereda la traza tipada de violación por corrida.
- **JuStRank (IBM Research)** — https://arxiv.org/abs/2412.09569. Hereda la razón medida: el sesgo y la decisividad del
  juez distorsionan rankings.
- **MBZUAI, "claim-calibrated evidence ladder" y auditoría cruzada de verificadores** — https://arxiv.org/abs/2607.00368,
  https://arxiv.org/abs/2608.25934. Hereda el principio de la escalera y la cita: F1 0,70 → 0,31 fuera del benchmark.
- **"Epistemological Fault Lines" / "Do LLMs Know What They Don't Know II"** — https://arxiv.org/pdf/2512.19466,
  https://arxiv.org/pdf/2609.07879. Hereda la regla: la abstención se puntúa como correcta o no, nunca como gratis.
  De ahí `hold_share` e `informative_rate` junto a cada tasa.

## Verificación por reglas (China)
- **DeepSeek-R1 §2.2.2** — https://arxiv.org/html/2501.12948v1. Hereda la justificación escrita de "sin modelo en el
  veredicto": "el modelo de recompensa neuronal puede sufrir reward hacking".
- **Tencent AI Lab, "One Token to Fool LLM-as-a-Judge"** — https://arxiv.org/abs/2507.08794. Hereda un protocolo de
  prueba: negativos "llave maestra" para cualquier brazo con juez.
- **DeepSeek-Prover-V2 / Kimina-Prover** — https://arxiv.org/abs/2504.21801, https://arxiv.org/abs/2504.11354. Hereda
  el estándar que CAPAS aún no cumple: el núcleo es pequeño e independientemente verificable.
- **Triage-PiEvo** (Westlake/Kuaishou, oct-2026) — https://arxiv.org/abs/2610.14683. Hereda los niveles de admisión
  (mismo canal · canal independiente · evaluador independiente) y la propagación de retracciones.
- **SCI-Verifier / SCI-VerifyBench** (Shanghai AI Lab, ICLR 2026) — https://arxiv.org/abs/2509.24285. La contraposición,
  nombrada con justicia; hereda su taxonomía de equivalencias como normalizadores deterministas, nunca como modelo.

## Benchmarking cuántico (Japón, China, CERN)
- **Hayata & Yamamoto, PRR sep-2026** — https://journals.aps.org/prresearch/abstract/10.1103/l8w6-pk4m. Hereda un tipo
  de claim con valor de referencia exacto y el estado de mitigación como campo declarado.
- **VERaiPHY / PHYSTAT, arXiv 2607.10039** — https://arxiv.org/abs/2607.10039. Hereda tres campos: calibración con datos
  independientes, chequeo de cobertura, corrección look-elsewhere; y "los datos se tocan solo en la prueba final".
- **CMS, dos equipos firman antes de abrir** — https://cms.cern/node/1378. Hereda: GOVERNANCE §6 es la regla de CMS
  mecanizada.
- **IBM, estrategias estándar de benchmark** — https://research.ibm.com/publications/defining-standard-strategies-for-quantum-benchmarks.
  Hereda la separación benchmark ≠ diagnóstico que `capas_quantum_physics.py` debe conservar.

## Regulación (Estados Unidos, Reino Unido, Canadá, Australia, Nueva Zelanda, Arabia Saudita, Corea)
- **FDA, criterios de rechazo técnico y Validator Rules / Pinnacle 21** — https://www.pharmasug.org/download/sde/rtp2022/PharmaSUG-NCSDE_2022-08.pdf.
  Hereda: el rechazo precede a la revisión; forma antes que estadística.
- **MHRA, autorización por etapas contra umbrales prefijados (2026)** — https://www.raps.org/resource/euro-roundup-mhra-commission-makes-recommendations-on-ai-regulatory-framework-in-the-uk.html.
  Hereda: umbrales fijados antes de los datos; licencia solo hasta la etapa alcanzada.
- **Health Canada, Predetermined Change Control Plans** — https://www.blg.com/en/insights/2025/02/health-canadas-evolving-regulatory-framework-for-machine-learning-enabled-medical-devices.
  Hereda: un sobre de cambios escrito; un cambio fuera de él reabre la validación.
- **TGA, guía AI-SaMD feb-2026** — https://www.tga.gov.au/node/514668. Hereda: los datos sintéticos cuentan solo como
  complemento.
- **NZ Medsafe Verification Pathway / COFEPRIS reliance** — https://www.medsafe.govt.nz/consultations/verification-pathway-rules-outcome.pdf.
  Hereda una regla negativa: el reliance transfiere veredictos, no evidencia; un veredicto ajeno es un campo declarado,
  nunca un ACCEPT.

## Política y redes (México, Brasil, Perú, Lituania, Federación)
- **Principios de Chapultepec, P3** (SECIHTI+ATDT, ene-2026) — https://secihti.mx/wp-content/uploads/2026/02/Principios_Chapultepec_F.pdf.
  Hereda los tres deberes como campos: verificar resultados, reproducir procesos, declarar el uso de IA. CAPAS
  "satisface mecánicamente la cláusula de investigación de P3"; nunca "cumple" ni "avalado por".
- **SNPCyH, criterios de admisibilidad (DOF may-2026)** — https://secihti.mx/snpcyh/criterios-de-admisibilidad/.
  Hereda la palabra admisibilidad a nivel revista y el hueco (sin criterio de datos, IA o retracciones) como canal.
- **CNPq, Portaria 2.664/2026** — https://www.gov.br/cnpq/pt-br/assuntos/noticias/cnpq-em-acao/cnpq-publica-portaria-que-institui-politica-de-integridade-na-atividade-cientifica.
  Hereda la forma de la declaración de IA: herramienta + propósito + fase (`ai_use_declared`).
- **Perú, DS 062-2024-PCM** — contraejemplo: "IA para detectar fraude" prometida sin evaluación. CAPAS lo midió y lo declinó.
- **Lituania, directrices de IA en investigación (2024) §30–32** — https://etikostarnyba.lt/wp-content/uploads/2024/08/Guidelines-on-the-ethical-use-of-artificial-intelligence-in-education-and-research.pdf.
  Hereda el requisito: verificación previa y auditoría regular de toda herramienta de IA.
- **Rede Brasileira de Reprodutibilidade y la Federación Global** — https://www.reprodutibilidade.org/,
  https://crsuzh.pages.uzh.ch/swissrn/contents/news/posts/2026-04-22b/GFRN.html. Hereda la forma institucional:
  dirigida por pares, con directorio, embajadores y guías; la herramienta es una entrada de catálogo, nunca la dueña.
