# KRENIQ — coordinación de infraestructura (LÉEME antes de editar o desplegar)

**Todo vive bajo KRENIQ.** `krenniq.com` es el dominio paraguas (front door). CAPAS y Atlas son
las dos herramientas. Esta app (`capas`) **además hospeda el landing oficial de krenniq.com** —
por eso tus edits/deploys aquí pueden tumbar el dominio si no sigues estas reglas.

## 1. krenniq.com vive DENTRO de esta app (`capas`)
- `krenniq.com` está bindeado a la Azure Container App **`capas`** (RG `capas-rg`, env `capas-env`).
- **Routing por Host** en `capas_api.py` (bloque `if p in ("/", ""):`):
  - `Host: krenniq.com` → sirve `docs/krenniq.html` (landing KRENIQ: las 2 herramientas + sección "El nombre"/Karenin).
  - cualquier otro Host (`capas.lemonground…azurecontainerapps.io`) → `docs/index.html` (CAPAS "Full Mock", la herramienta).
  - **NO rompas ese bloque.** Si lo tocas, krenniq.com deja de servir el landing.

### Subdominios (vivos desde 2026-06-23)
La app `capas` sirve DOS hostnames: **`krenniq.com`** (landing) y **`capas.krenniq.com`** (la herramienta CAPAS). `atlas.krenniq.com` lo sirve la app `atlas` (otro repo). Routing por Host en `capas_api.py`: `krenniq.com`/`www` → landing; cualquier otro (incl. `capas.krenniq.com` y el FQDN azure) → `index.html`.

## 2. ⚠️ GOTCHA CRÍTICO — cada deploy de `capas` tumba el TLS de SUS dos dominios
Hacer `az containerapp update -n capas …` **rompe el binding SNI** de `krenniq.com` Y `capas.krenniq.com` en el edge (queda `http 000` / `no peer certificate`), aunque la config diga `SniEnabled`. **DESPUÉS DE CADA DEPLOY de capas, RE-BINDEA LOS DOS:**
```bash
az containerapp hostname bind --hostname krenniq.com -n capas -g capas-rg \
  --environment capas-env --certificate mc-capas-env-krenniq-com-3031
az containerapp hostname bind --hostname capas.krenniq.com -n capas -g capas-rg \
  --environment capas-env --certificate mc-capas-env-capas-krenniq-co-5290
# espera ~2–5 min; verifica AMBOS:
curl -sI https://krenniq.com && curl -sI https://capas.krenniq.com   # HTTP/2 200
```
(Atlas: igual, al desplegar `atlas` re-bindea `atlas.krenniq.com` con cert `mc-capas-env-atlas-krenniq-co-8796`.)
- Certs administrados (DigiCert, vencen Dic 2026): `mc-capas-env-krenniq-com-3031`, `mc-capas-env-capas-krenniq-co-5290`, `mc-capas-env-atlas-krenniq-co-8796`. **No los borres.**
- DNS (Cloudflare): A `@` → `20.232.76.107` gris; CNAME `capas`/`atlas` → FQDNs azure gris; TXT `asuid.*`. **No toques** o la validación se cae. (Token de DNS scoped fue usado y debe revocarse.)

## 2b. Idioma (toggle ES/EN persistente entre los 3 sitios) — **default INGLÉS**
`docs/lang.js` (DEFAULT='en') + cookie `kq_lang` a nivel `.krenniq.com` (compartida apex+subdominios). Cada texto traducible lleva `data-en` y/o `data-es`; el contenido tal cual es la base. Toggle en la nav: `<button class="nav-lang" data-lang-btn onclick="KQLang.toggle()">`. Landing 100% bilingüe; Atlas usa su i18n conectado a la misma cookie. **CAPAS está en inglés (base) y le faltan los `data-es` — esa traducción al español la lleva la SESIÓN DE CAPAS (lead de CAPAS), no la sesión de Atlas.** Patrón: a cada elemento traducible de las páginas `docs/*.html` agrégale `data-es="<español>"`; `lang.js` ya hace el swap.

## 2c. El nombre / about
El landing dice que el nombre "viene de una idea, no de una persona" (despeja confusión con el científico **Krenn** citado en benchmarks). El origen literario (Karenin / Kundera, *La insoportable levedad del ser*, fidelidad a lo real) vive SOLO en comentario de código / material de about — **no se expone en el landing**.

## 3. Deploy de `capas` (flujo completo)
```bash
TAG="capas:<lo-que-sea>-$(date +%Y%m%d%H%M%S)"
az acr build --registry caf7ef600384acr --image "$TAG" .
az containerapp update -n capas -g capas-rg --image "caf7ef600384acr.azurecr.io/$TAG"
# >>> RE-BIND krenniq.com (paso 2) <<<  ← SIEMPRE, o el dominio queda muerto
```
`.dockerignore` excluye `designlab/`, `outputs/`, `audits/`, `__pycache__`, `*.png/jpeg` — mantén el contexto liviano (~50 MB).

## 4. Shell de marca = fuente única, no forkear
- `docs/kreniq-shell.css` es la **fuente única** del shell (nav, bg-logo flotante canónico, cards, tokens de layout: --col 1200px, --gutter 48px, --nav-h 60px, --radius 14px, --pink #e8185d). `../corporate-platform/design-system/` lo espeja para apps nuevas. **No dupliques/forkees estilos por página.**
- **Nav canónico** (idéntico en las 7 páginas `docs/*.html`):
  `Home`(→ `https://krenniq.com/`) · `Intro+`(→ `index.html`, el intro de CAPAS, activo) · Gate App · Methodology · Pilot · Audit · Benchmark · Security · `Atlas`(→ app de Atlas) · CTA `Test a Claim`.
  **No** renombres "Intro+" de vuelta a "Home", **no** quites el link `Atlas`, **no** apuntes "Home" a `index.html`.

## 5. Mapa de superficies (qué es qué)
| URL | Sirve | Repo/archivo |
|-----|-------|--------------|
| `krenniq.com/` | Landing KRENIQ (front door) | esta app · `docs/krenniq.html` |
| `capas.lemonground…azure/` | CAPAS (la herramienta) | esta app · `docs/index.html` |
| `atlas.lemonground…azure/` | Atlas (la otra herramienta) | **otro repo**: `../ATLAS/` (hermano de este, bajo `01. Investigacion/`) |

Atlas es app/repo aparte — no se despliega desde aquí. Su nav ya apunta Home→landing y CAPAS→capas.
