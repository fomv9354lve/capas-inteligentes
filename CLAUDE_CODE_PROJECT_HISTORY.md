# CAPAS Claim Gate — Project History and Context for Claude Code

Fecha: 2026-06-19

## Reanudar desde esta carpeta

```bash
cd "/Users/kreniq/Desktop/KRENIQ/AI Projects/01. Investigacion/CAPAS INTELIGENTES"
```

Archivo web principal:

```bash
docs/index.html
```

Handoff operativo corto:

```bash
HANDOFF_CAPAS_CODEX.md
```

Demo pública:

```text
https://fomv9354lve.github.io/capas-inteligentes/
```

## Resumen en una frase

CAPAS Claim Gate pasó de ser un prototipo client-side de validación determinística de claims científicos a una demo web avanzada de governance para claims de training data, con schema v3, 11 tipos de claim, batch mode, guided builder, paper/text ingestion, provenance gates, fine-tune readiness y UI accesible. La deuda actual ya no es lógica del gate: es arquitectura de información, navegación, storytelling de producto y ergonomía enterprise.

## Qué es CAPAS exactamente

CAPAS no debe describirse como:

- Fact-checker general.
- Detector de hallucinations.
- LLM judge.
- Motor de verdad automática.

Descripción correcta:

```text
CAPAS is a deterministic schema-gated evidence classifier for AI training-data claims.
```

Explicación:

CAPAS toma un claim estructurado y evidencia estructurada en JSON. Luego decide, con reglas determinísticas y auditables, si esa evidencia licencia el claim para ciertos usos, incluyendo entrada a pipelines de fine-tuning. El output no dice "esto es verdad" en abstracto. Dice: "dado este payload y estos campos de evidencia suministrados, el claim pasa o no pasa la gate definida por el schema".

Línea clave del producto:

```json
"non_claim": "This decision is rule-based over supplied evidence fields, not an LLM judgment."
```

Esa línea es central para el posicionamiento: no-LLM es una ventaja regulatoria y de auditabilidad, no una limitación.

## Evolución histórica resumida

### 1. Auditoría inicial

El usuario pidió:

```text
Quiero auditoria profunda, valor de mercado, debugging, mejora de UI/UX mejora grado lab competidores y State of Art
```

Se auditó el sitio vivo:

```text
https://fomv9354lve.github.io/capas-inteligentes/
```

Hallazgos iniciales:

- UI útil pero parecía prototipo.
- Falta de persistencia robusta del historial.
- Accesibilidad incompleta.
- Copy JSON activo sin contenido.
- Mensajes de error técnicos.
- Light mode parcial.
- Output JSON sin highlighting.
- Fine-tune readiness todavía débil.
- Sin API/SDK/CI integration clara.

Resultado: se inició una secuencia de hardening técnico y UI/UX.

### 2. UI/UX hardening v6

Se cerraron:

- ARIA labels.
- Focus-visible.
- Mensaje amigable si textarea vacío.
- Copy JSON disabled hasta tener output.
- Historial localStorage con cap 50.
- Restore desde historial.
- Contador N/50.
- Grid responsive.
- Output horizontal scroll.
- Light mode.
- Microestado processing.

Se verificó en producción y CI/Pages estaban verdes.

### 3. Rediseño visual enterprise

El usuario dijo que la UI parecía juguete y no estaba al nivel de competidores grandes.

Se propuso y luego se fue consolidando un diseño tipo:

- Vercel.
- Linear.
- Supabase.
- IBM Carbon.
- Raycast.

Cambios conceptuales:

- Topbar sticky.
- Design tokens CSS.
- Paleta semántica.
- Badges de verdict.
- Botón primario claro.
- Mejor jerarquía.
- Dark/light/system theme.
- Syntax highlighting.

### 4. Guided intake y schema evolution

Se añadió:

- Build Draft.
- Guided intake.
- Schema version.
- Help modal.
- Batch mode.
- Shared payload/permalink.
- Fine-tune blockers.
- Non-claim marker.

Varios commits fueron auditados: v8, v9, v10, v11, v12, v13.

### 5. Batch pipelines

Se cerraron:

- Batch mode con array, `{items: []}`, `{claims: []}` y single auto-wrap.
- Batch output con `results: [{ index, result }]`.
- Summary por veredicto.
- UI con filas expandibles por item.
- Batch fine-tune readiness agregado.
- Progress label.

### 6. Historial como audit log

Se cerraron:

- Persistencia localStorage.
- FIFO 50.
- Timestamp visible.
- Delete individual.
- Restore con teclado.
- Filtros por texto.
- Filtro por veredicto.
- Export CSV.
- Clear history.

### 7. Schema v2/v3 y nuevos tipos

Tipos activos al final:

1. `universal_anchor_claim`
2. `exact_model_solution`
3. `physical_accuracy`
4. `claim_transition`
5. `statistical_confidence`
6. `reproducibility_check`
7. `financial_metric_claim`
8. `causal_mechanism_claim`
9. `systematic_review_claim`
10. `evidence_conflict_claim`
11. `multimodal_evidence_claim`

Schema actual esperado:

```text
capas-claim-payload-v3
```

Se decidió que payloads sin versión o con versiones anteriores deben bloquearse con HOLD/schema error.

### 8. Fine-tune readiness

Primero `fine_tune_ready` era siempre false. Luego el usuario pidió criterios positivos reales:

1. Revisión externa/provenance.
2. Source-backed evidence.
3. Semantic alignment.
4. Witness independence.
5. Training evidence explícito.

Luego pidió endurecerlo con:

1. Firma o hash de review externo.
2. Source URLs recuperables y hashables.
3. Witness ID resoluble.
4. RO-Crate/provenance packet validado.
5. Reviewer identity/attestation verificable.

Resultado:

- 14 criterios de readiness.
- 9 criterios declarativos evaluables en browser.
- 5 provenance gates requieren CLI/API, no pueden completarse en static browser.
- UI debe explicar que el browser es preview y la verificación activa vive en `capas.py` CLI/API.

Idea importante:

```text
fine_tune_ready: true should not be reachable from static browser if active external provenance I/O is required.
```

Eso es postura de seguridad, no bug.

### 9. Paper/text ingestion

Se añadió ingestion:

- Texto libre.
- Metadata adapters tipo Semantic Scholar/PubMed local.
- Extraction preview.
- Evidence spans.
- Human confirmation.
- Numeric parser para `p_value`, `alpha`, etc.
- Candidatos por claim type.

Se cerró el bug de parser numérico:

- `p_value: 0.03` ahora parsea como number.
- `alpha: 0.05` ahora parsea como number.

Límite documentado:

```text
CAPAS does not perform general theorem proving or general paper understanding.
```

### 10. Guided builder

Se arregló el builder para que adapte campos al tipo:

- `systematic_review_claim` genera sus campos.
- `evidence_conflict_claim` genera sus campos.
- `multimodal_evidence_claim` genera sus campos.
- `causal_mechanism_claim` genera sus campos.

Último estado auditado: `40f33e3 · Fix guided builder type redraw`, score 10/10 en las 11 dimensiones funcionales.

## Estado técnico actual según auditorías

Última tabla consolidada:

| Dimensión | Score |
|---|---:|
| Lógica de decisión | 10/10 |
| Schema & validación | 10/10 |
| Fine-tune readiness | 10/10 |
| Build Draft | 10/10 |
| Batch mode | 10/10 |
| Historial | 10/10 |
| UX/UI funcional | 10/10 |
| Accesibilidad | 10/10 |
| Ayuda in-app | 10/10 |
| Seguridad / aislamiento | 10/10 |
| Paper ingestion | 10/10 |

Importante: ese 10/10 es para la superficie funcional browser auditada empíricamente, no significa que el producto enterprise completo esté terminado. Todavía faltan distribución, API/CLI pública, backend multiusuario y mejor arquitectura de información.

## State of the Art y posicionamiento

CAPAS no compite directamente con:

- FEVER.
- SciFact.
- AVeriTeC.
- FActScore.
- Factcheck-GPT.
- DeepSciVerify.
- Elicit.
- OpenAI Evals.
- RAGAS.
- TruLens.
- DeepEval.
- Vectara HHEM.
- Patronus Lynx.
- Label Studio.
- Argilla.
- MLflow.
- DVC.
- W&B Artifacts.
- DataComp.
- LAION filters.

Comparación correcta:

- Fact-checkers verifican texto libre contra corpus.
- Hallucination detectors evalúan outputs de LLM post-inference.
- Dataset curation limpia corpus masivos.
- Lineage tools rastrean archivos/datasets.
- CAPAS gatea claims estructurados antes de entrar a training/fine-tuning.

Moat conceptual:

1. Determinismo rule-based.
2. Schema versioning estricto.
3. 11 tipos de claim con lógica epistémica distinta.
4. Fine-tune readiness con blockers granulares.
5. Provenance/witness/RO-Crate.
6. Human-in-the-loop confirmation.
7. Browser static preview + CLI/API verification surface.
8. Non-LLM marker en cada output.

Riesgo estratégico:

El producto resuelve un problema real pero adelantado al mercado. Muchos usuarios aún no saben que necesitan gates de claims antes de fine-tuning. La historia de negocio debe educar.

## Business case / "so what"

El usuario quiere una historia tipo consultoría estratégica pero sin mencionar explícitamente Big 3.

Narrativa recomendada:

```text
CAPAS reduces the review burden for training-data governance by turning vague claim review into a deterministic evidence contract.
```

Traducción de valor:

- Menos revisión manual repetitiva.
- Menos claims no verificables entrando a datasets.
- Mejor trazabilidad para auditorías.
- Menos riesgo de usar claims sin provenance.
- Mejor handoff entre investigadores, data teams y compliance.
- Exportable a CSV/JSON para auditoría.

Evitar claims no demostrados:

- No decir "ahorra 80%" salvo que haya benchmark real.
- No decir "enterprise validated" si no hay cliente.
- No decir "production deployment" si es simulación.

Wording más fuerte pero honesto para métricas:

```text
Stress-tested across a 1,000-claim governance simulation.
```

o:

```text
Validated on a 1,000-claim simulated audit run with deterministic decision traces.
```

Siempre footnote:

```text
Pilot metrics are simulated unless explicitly marked as customer-validated production data.
```

## Disclaimers y footnotes necesarios

Agregar al sitio, idealmente en Pilot Packet/Product Story/footer:

1. CAPAS gates structured evidence supplied by users; it does not independently certify truth.
2. Browser decisions are deterministic previews; active provenance verification requires CLI/API.
3. Share URLs may embed payload data; do not share sensitive or proprietary claims.
4. Users are responsible for rights, permissions and licenses for paper text, PDFs, source URLs and evidence.
5. Paper ingestion is extraction assistance, not general paper understanding or theorem proving.
6. Training-data readiness is a governance signal, not legal advice or regulatory certification.
7. Pilot metrics are simulated unless explicitly marked as customer-validated.
8. External source availability and hash verification may change over time.

## Warning upstream de Node 20

El usuario preguntó por el warning upstream.

Explicación acordada:

- Es un warning de GitHub Actions/Pages o de una action de terceros sobre runtime Node 20.
- No es fallo de CAPAS.
- No rompe CI ni Pages si los checks finales están verdes.
- Se puede documentar y sostener explícitamente que se monitoreará.
- No conviene gastar tiempo tratándolo como bug del producto si el estado remoto final es verde.

## Automatización diaria SOTA / literatura

El usuario preguntó cómo mantener SOTA/literatura actualizados automáticamente.

Ya existen docs relevantes:

- `docs/DAILY_SOTA_UPDATE.md`
- `docs/SOTA_DAILY_WATCH.md`

Dirección recomendada:

- Crear/usar un workflow de GitHub Actions programado (`schedule:` cron diario).
- O correr local en Mac con `launchd`/cron.
- El flujo diario debería:
  1. Consultar fuentes permitidas/API: arXiv, Semantic Scholar, PubMed, Google Scholar si manual/no scraping agresivo.
  2. Guardar resultados en `docs/SOTA_DAILY_WATCH.md` o `outputs/sota/YYYY-MM-DD.md`.
  3. Clasificar por relevancia: claim verification, provenance, RO-Crate, AI governance, training-data quality.
  4. Generar diff/PR o commit automático si hay cambios.
  5. No inventar citas. Toda cita debe tener URL/DOI/arXiv ID.

Si se implementa, usar fuentes oficiales/APIs y evitar scraping frágil.

## Deuda UX actual más importante

Aunque la funcionalidad llegó a 10/10, la UX de producto aún tiene problemas:

1. La web se siente como una sola hoja larga.
2. Home/App/Pilot/Product Story no están claramente separados.
3. CTAs se mueven y cambian el contexto.
4. El usuario no sabe cómo volver de app a landing o viceversa.
5. "Return to gate" es ambiguo.
6. Customer brief / pilot packet / product story se sienten como `.md` sin diseño.
7. Raw JSON puede aparecer demasiado pronto para usuario nuevo.
8. Guided Form debe ser default para nuevos usuarios.
9. Audit Log no debe contaminar el workspace principal si no se necesita.
10. Topbar necesita navegación estable.

## Última petición concreta del usuario

El usuario mostró una captura con tres botones:

- Run the gate
- Pilot packet
- Product story

Y dijo, en esencia:

- Esa sección se mueve al navegar y confunde.
- Quiere Home y secciones estáticas.
- Quiere moverse entre ellas con navegación clara.
- Incluir Home.
- Nombres claros.
- "Return to gate" no debe llevar a Home si dice gate.
- Desde Home, Customer Package y Product History deben abrir su sección correcta.
- Ahora es un lío; quiere un index navegable.

Luego añadió análisis de UX:

- Para usuario nuevo es 5.5/10.
- Para usuario objetivo es 8/10.
- Falta onboarding activo.
- JSON raw no debe ser lo primero.
- Terms técnicos necesitan tooltips/contexto.
- Audit Log puede cortarse/desbordar.
- Guided Evidence Constructor es una buena idea pero debe ser punto de entrada.

## Próxima implementación recomendada

### Opción segura: SPA con secciones ancladas

Mantener `docs/index.html`, pero reorganizar:

```html
<nav class="topbar">
  <a href="#home">Home</a>
  <a href="#gate">Run the gate</a>
  <a href="#ingest">Ingest paper</a>
  <a href="#audit-log">Audit log</a>
  <a href="#pilot-packet">Pilot packet</a>
  <a href="#product-story">Product story</a>
  <button id="help-btn">Help</button>
</nav>

<main>
  <section id="home">...</section>
  <section id="gate">...</section>
  <section id="ingest">...</section>
  <section id="audit-log">...</section>
  <section id="pilot-packet">...</section>
  <section id="product-story">...</section>
</main>
```

Add active section highlighting only if simple and reliable.

### Opción más limpia: Multi-page

Crear:

- `docs/index.html` = Home / landing.
- `docs/app.html` = Gate app.
- `docs/pilot-packet.html` = designed customer/pilot packet.
- `docs/product-story.html` = designed story.

Riesgo: mover JS/IDs puede romper el gate. Si se hace, primero extraer o duplicar scripts con cuidado.

Recomendación práctica: empezar con SPA anclada.

## Wording recomendado para nav/CTAs

Top nav:

- Home
- Run the gate
- Ingest paper
- Audit log
- Pilot packet
- Product story
- Help

Hero:

```text
CAPAS Claim Gate
Deterministic evidence gates for AI training-data claims.
```

Subcopy:

```text
Validate structured scientific and governance claims before they enter fine-tuning pipelines. CAPAS uses versioned schemas, explicit evidence fields and auditable provenance blockers, not an LLM judge.
```

CTAs:

- Primary: `Run the gate`
- Secondary: `View pilot packet`
- Tertiary: `Read product story`

Avoid:

- Customer brief and pilot packet as separate labels if they point to similar content.
- Product history if the real content is product story.
- Return to gate unless it truly scrolls/links to `#gate`.

## Guided builder improvement direction

Make builder feel richer:

- Default tab should be Guided Form.
- Raw JSON tab should be labeled `Raw JSON · Advanced`.
- Add evidence contract progress:
  - `3/4 required fields complete`.
  - "Ready to run" state.
- Add claim type descriptions inline.
- Add field-level helper text.
- Add `Build and run gate` primary button.
- Keep `Build JSON` secondary.
- Evidence contract should show required, optional, present/missing states.

## App/landing separation recommendation

User should always know where they are:

- Home = product explanation.
- Gate = working tool.
- Pilot Packet = business case and adoption plan.
- Product Story = why CAPAS exists, SOTA, positioning.
- Help = modal/reference.

If staying in one page, use section titles and nav active state.

## Files to inspect first

```bash
rg -n "product-hero|hero-actions|workflow-strip|gate-section|guided-panel|ingest-panel|history-section|Pilot|Product story|Customer brief|Run the gate|Return to gate" docs/index.html
```

Then open relevant regions:

```bash
nl -ba docs/index.html | sed -n '1,260p'
nl -ba docs/index.html | sed -n '260,620p'
nl -ba docs/index.html | sed -n '620,1040p'
```

Use `apply_patch` for edits.

## Validation commands

```bash
python3 capas.py validate
python3 -m py_compile capas.py benchmarks/verify_claim_gate_ui.py
git diff --check
```

If browser automation exists in repo:

```bash
python3 benchmarks/verify_claim_gate_ui.py
```

## Caution

- Do not break existing IDs used by JS.
- Do not remove ARIA attributes.
- Do not remove schema v3 enforcement.
- Do not remove fine-tune CLI-only note.
- Do not remove share URL privacy warning.
- Avoid adding external dependencies.
- Avoid turning the app back into a marketing-only landing page.
- Keep the gate reachable in one click from Home.

