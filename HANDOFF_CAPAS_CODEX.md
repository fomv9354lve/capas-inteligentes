# CAPAS Claim Gate — Codex Handoff

Fecha: 2026-06-19

## Actualización crítica — 2026-06-19 23:58 CST

Carpeta activa:

```bash
cd "/Users/kreniq/Desktop/KRENIQ/AI Projects/01. Investigacion/CAPAS INTELIGENTES"
```

Estado inmediato antes de continuar:

- El usuario aprobó el render exacto del logo 3D de `/Users/kreniq/Downloads/red_de_transiciones_3d (2).html`.
- Ese logo ya fue integrado en `docs/index.html` como escena Three.js real, no como SVG aproximado.
- La escena usa Three.js r128 + OrbitControls desde CDN, conserva 36 nodos, tubos cian/magenta, shell wireframe, fog, auto-rotación y oscilación.
- El SVG `docs/capas-transition-network-logo.svg` todavía existe y se usa en la app/header pequeño, pero en la Home el logo importante debe ser el render Three.js exacto.
- El usuario pidió corregir la colocación: el logo 3D debe quedar en desktop del lado derecho, arriba, alineado al techo del hero según mockup. La línea amarilla del mockup marca el espacio del logo.
- El cambio anterior lo movió a la izquierda por una instrucción posterior, pero ahora el usuario pidió revertir esa colocación: “ESTÁ BIEN A LA DERECHA”.
- No tocar la escena Three.js ni volver a recrearla como SVG. Solo ajustar layout/orden/alineación del hero.

Archivos relevantes:

- `docs/index.html`: Home pública y hero con `#capas-3d-logo`.
- `benchmarks/verify_customer_product_assets.py`: verifica que la Home contenga `id="capas-3d-logo"`, `initTransitionLogo`, `THREE.OrbitControls`, `TOTAL_NODES = 36`, `THREE.TubeGeometry`, etc.
- `docs/app.html`, `outputs/capas_claim_gate_ui.html`, `capas.py`: contienen topbar/logo pequeño de la app; no son el problema actual salvo si el usuario vuelve a mencionar navbar.

Últimos checks que pasaron antes de esta corrección:

```bash
python3 capas.py validate
python3 benchmarks/verify_customer_product_assets.py
python3 benchmarks/verify_claim_gate_ui.py
git diff --check
```

Pendiente exacto:

1. En `docs/index.html`, volver a hero desktop con texto a la izquierda y `.hero-visual` a la derecha.
2. Mantener `.hero { align-items: start; }`.
3. Mantener `.hero-visual { justify-items: end; align-self: start; }`.
4. Mantener `.hero-logo-card { width: min(100%, 420px); aspect-ratio: 1 / 1; min-height: 300px; }`.
5. En DOM, el bloque de texto debe ir primero y el bloque `.hero-visual` después.
6. En mobile, puede apilarse a una columna; no importa si el logo queda arriba o abajo, pero desktop debe respetar mockup: logo arriba/derecha.

Resultado aplicado después de esta nota:

- `docs/index.html` ya volvió a texto izquierda + logo 3D exacto derecha en desktop.
- El App (`docs/app.html` y `outputs/capas_claim_gate_ui.html`) ya no debe cargar `capas-transition-network-logo.svg` en el topbar. Ese SVG fue el logo descartado que el usuario no quiere ver al entrar a Gate App.
- La causa del App renderizado como texto plano fue CSP desincronizado: `docs/app.html` actúa como plantilla para `_render_ui()` si existe, y si se toca CSS/HTML hay que regenerar con:

```bash
python3 capas.py ui --output docs/app.html
python3 capas.py ui
```

- Verificaciones posteriores que pasaron:

```bash
python3 benchmarks/verify_claim_gate_ui.py
python3 benchmarks/verify_claim_gate_ui_browser.py
python3 benchmarks/verify_customer_product_assets.py
git diff --check
```

## Carpeta exacta para reanudar

```bash
cd "/Users/kreniq/Desktop/KRENIQ/AI Projects/01. Investigacion/CAPAS INTELIGENTES"
```

Rama actual:

```bash
main...origin/main
```

Archivo principal de la web:

```bash
docs/index.html
```

Demo pública:

```text
https://fomv9354lve.github.io/capas-inteligentes/
```

## Estado del producto

CAPAS Claim Gate está en estado funcional avanzado. La última auditoría empírica validó score 10/10 sobre la superficie browser para:

- Lógica determinística de decisión.
- Schema v3 con enforcement estricto.
- Fine-tune readiness con 14 criterios.
- Build Draft.
- Batch mode.
- Historial con búsqueda/filtros/delete/timestamps.
- UX/UI funcional.
- Accesibilidad ARIA.
- Ayuda in-app.
- Seguridad/aislamiento.
- Paper/text ingestion.

Versión observada recientemente:

```text
v13 · end-to-end gaps | schema v3 | shared payload
```

Commit funcional mencionado por el usuario:

```text
40f33e3 · Fix guided builder type redraw
```

## Contexto importante de conversación

El usuario pidió inicialmente:

- Auditoría profunda.
- Valor de mercado.
- Debugging.
- Mejora UI/UX.
- Comparación con competidores.
- State of the Art.
- Elevar a nivel de producto enterprise.

Se cerraron muchas rondas de auditoría:

- UI/UX hardening.
- Batch mode.
- Schema/version indicator.
- Shortcut help modal.
- API/GitHub Action concept.
- Standalone ingestion/retrieval/PDF/parser direction.
- Fine-tune readiness real.
- Provenance gates: review hash, source URLs hashables, witness registry, RO-Crate, reviewer attestation.
- Mobile responsive.
- Guided builder dynamic fields.
- Paper ingestion numeric parser/evidence spans.

El warning de Node 20 en GitHub Pages fue tratado como upstream/no bloqueante. Mensaje conceptual: no es un fallo de CAPAS, sino una advertencia de GitHub Actions/Pages sobre runtime upstream. Mantenerlo documentado, no perseguirlo como bug del producto.

## Última dirección del usuario

El usuario quiere atacar la deuda de UX/arquitectura de información, no la lógica del gate.

Problemas señalados:

1. La web se siente como una sola hoja larga.
2. No hay navegación clara entre Home, App/Gate, Customer/Pilot Packet y Product Story.
3. Los CTAs se mueven/confunden según scroll.
4. "Return to gate" no comunica bien si vuelve al app o al home.
5. Customer brief, pilot packet, product story y MDs se sienten sin diseño.
6. Quiere una página navegable, con secciones estáticas claras, incluyendo Home.
7. Quiere wording profesional sin mencionar explícitamente "Big 3".
8. Quiere reemplazar wording flojo como "1,000 candidate training claims in simulated pilot" por algo más fuerte, honesto y demostrable.
9. Quiere footnotes/disclaimers sobre PI, licencias, uso de datos y límites.
10. Quiere que el constructor guiado se sienta más rico, tipo IBM-grade, sin copiar IBM.

## Recomendación de arquitectura UX siguiente

No seguir pegando CSS encima. Conviene hacer una reorganización explícita del `docs/index.html`:

### Navegación propuesta

Top nav fija y estable:

- Home
- Gate
- Ingest
- Audit Log
- Pilot Packet
- Product Story
- Help

Regla: la nav no cambia de contenido por sección. Siempre lleva a anclas o vistas claras.

### Estructura propuesta en la misma página

Mantener como single-page app, pero con anclas limpias:

```html
<section id="home">...</section>
<section id="gate">...</section>
<section id="ingest">...</section>
<section id="audit-log">...</section>
<section id="pilot-packet">...</section>
<section id="product-story">...</section>
```

Alternativa más limpia si el archivo crece demasiado:

- `docs/index.html` = Home + navegación.
- `docs/app.html` = Gate app.
- `docs/customer-brief.html` = customer/pilot packet con diseño.
- `docs/product-story.html` = historia de producto con diseño.

Pero antes de partir archivos, revisar el JS actual: probablemente está acoplado a IDs dentro de `docs/index.html`. La vía más segura es anclas en una sola página.

## Cambios de wording recomendados

Evitar:

```text
1,000 candidate training claims in simulated pilot
```

Opciones mejores:

```text
Validated on a 1,000-claim governance simulation
```

```text
1,000-claim pilot simulation with deterministic audit trails
```

```text
Stress-tested across 1,000 structured training-data claims
```

Si no existe evidencia real en repo para los 1,000 claims, usar lenguaje de simulación explícito:

```text
Simulated 1,000-claim governance run; not a production customer deployment.
```

## Footnotes/disclaimers necesarios

Agregar una sección pequeña de notas, no legalista pero profesional:

- CAPAS gates structured evidence supplied by users; it does not independently certify truth.
- Share URLs may embed payload data; do not share sensitive claims or proprietary provenance.
- Paper ingestion is a deterministic preview and requires human confirmation.
- Source URLs, review hashes, witness IDs and RO-Crate validation require CLI/API verification, not static browser preview.
- Users are responsible for rights, licenses and permissions for uploaded/processed paper text and evidence.
- Pilot metrics are simulations unless explicitly marked as production/customer validated.

## UI/UX deuda activa

### 1. Navegación

Crear una nav estable con Home incluido. El usuario debe poder pasar de app a landing y de landing a app sin depender de botones ambiguos.

Wording sugerido:

- "Home" = landing/product overview.
- "Run the gate" = app/gate.
- "Pilot packet" = business case/customer package.
- "Product story" = narrative/product positioning.

Evitar "Return to gate" si no está claro el origen. Usar:

- "Open gate"
- "Back to home"
- "View pilot packet"
- "Read product story"

### 2. Home

Debe ser una pantalla estable, no mezclada con tool state.

Hero recomendado:

```text
CAPAS Claim Gate
Deterministic evidence gates for AI training-data claims.
```

Subcopy:

```text
Validate structured scientific and governance claims before they enter fine-tuning pipelines. No LLM judge, no hidden inference, just versioned schemas, explicit evidence fields and auditable provenance blockers.
```

Primary CTA:

```text
Run the gate
```

Secondary:

```text
View pilot packet
```

### 3. Gate/App

El gate debe sentirse como workspace, no landing.

Mantener tabs:

- Guided Form
- Raw JSON
- Ingestion

Pero entrada default para usuario nuevo debe ser Guided Form, no Raw JSON.

### 4. Guided builder

Elevar riqueza:

- Campo por campo con descripción corta.
- Evidence contract lateral con progreso.
- Estado "ready to run" cuando todos los campos requeridos están completos.
- Tooltips para claim types.
- Botón principal "Build and run gate" además de "Build JSON".
- Raw JSON como modo avanzado, no primera experiencia.

### 5. Pilot packet / Product story

No dejar como Markdown plano. Integrar visualmente en la web:

- Hero corto.
- Problem / Gate / Output / Business case.
- ROI calculator o ROI cards.
- Footnotes.
- Link visible a fuentes/docs.

## Competidores / referencias UX discutidas

Se comparó contra:

- Linear.
- IBM Carbon.
- Raycast.
- Label Studio.
- DeepEval.
- Braintrust.
- Galileo.
- W&B.
- Snorkel.
- Retool.
- Postman.
- Stripe.

Conclusión de UX:

- CAPAS tiene lógica y design tokens fuertes.
- El problema no es la estética base sino la arquitectura de información.
- Antes el gate quedaba enterrado bajo marketing.
- Luego se movió hacia app-shell, pero ahora la navegación entre Home/App/brief/story quedó confusa.
- Siguiente paso: navegación estable y separación mental de "landing" vs "workspace".

## Comandos útiles

Ver estado:

```bash
git status --short --branch
```

Buscar estructura:

```bash
rg -n "product-hero|gate-section|guided-panel|ingest-panel|history-section|Pilot|Product story|Customer brief|Run the gate" docs/index.html
```

Validar Python:

```bash
python3 capas.py validate
python3 -m py_compile capas.py benchmarks/verify_claim_gate_ui.py
```

Buscar CSS duplicado/manual:

```bash
rg -n "CAPAS PROFESSIONAL REDESIGN|product-hero|topbar|samples-bar|gate-section" docs/index.html
```

## Próximo bloque de implementación recomendado

1. Leer `docs/index.html` completo por secciones relevantes.
2. Identificar topbar actual, hero actual, CTA row, gate section, guided panel, ingest panel, history, business/customer/product sections.
3. Implementar navegación estable:
   - Home
   - Gate
   - Ingest
   - Audit Log
   - Pilot Packet
   - Product Story
   - Help
4. Renombrar CTAs ambiguos.
5. Añadir footnotes/disclaimers.
6. Reemplazar wording "candidate training claims" por wording más fuerte y trazable.
7. Mejorar customer/pilot/product sections para que no se sientan como Markdown plano.
8. Verificar con screenshot/Playwright si hay herramienta disponible o con browser manual.
9. Ejecutar validaciones existentes.

## Nota sobre imágenes en Codex

El usuario no pudo pegar imágenes en Codex. Recomendación dada:

```bash
mkdir -p screenshots
screencapture -i screenshots/captura.png
```

Luego indicar la ruta:

```text
screenshots/captura.png
```

El asistente puede inspeccionarla con `view_image`.
