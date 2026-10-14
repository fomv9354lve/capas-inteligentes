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

### 3b. Lecciones de deploy del 2026-10-13 (léelas antes de tocar `deploy_site.py`)
- `python3 deploy_site.py` **sin flags DESPLIEGA** (`az containerapp up --source`). `--verify` es solo lectura (live == local).
  Cualquier otro flag (incl. `--help`) ahora imprime uso y sale sin desplegar — antes desplegaba (incidente 03:15).
- Los `az` mutantes los corre Osvaldo. La sesión prepara y verifica; no despliega salvo instrucción explícita.
- Tras un deploy: comprueba **los tres** hostnames (krenniq.com, capas.krenniq.com, atlas.krenniq.com) con GET
  (`curl -s -o /dev/null -w '%{http_code}' https://…/`): hasta el deploy que lleve `do_HEAD` (commit del 2026-10-13 ~17:00)
  el servidor de capas respondía **501 a HEAD**, así que `curl -sI` daba 501 aunque el sitio estuviera bien; el `up --source`
  de hoy no tumbó el SNI, pero la regla de re-bind del §2 sigue vigente.
- La Gate App decide con el motor Python vía `/api/decide` (individual Y lote); la réplica JS `rule()` no es el motor
  (paridad 130/233) y sin backend la página da HOLD. `python3 benchmarks/replica_parity.py` mide la deriva.
- `python3 -m pytest` verde no implica la puerta de producto verde: corre `capas validate` tras cambiar reglas del motor.

## 4. Shell de marca = fuente única, no forkear
- `docs/kreniq-shell.css` es la **fuente única** del shell (nav, bg-logo flotante canónico, cards, tokens de layout: --col 1200px, --gutter 48px, --nav-h 60px, --radius 14px, --pink #e8185d). `../corporate-platform/design-system/` lo espeja para apps nuevas. **No dupliques/forkees estilos por página.**
- **Nav canónico por tarea** (decisión de Osvaldo 2026-10-14, «3 si», auditoría CAP-19). Fuente única: `scripts/apply_nav.py`
  (escribe el nav y la barra secundaria en las 9 páginas; CI corre `--check`). No edites el nav a mano en una página.
  Nivel 1: `Product`(→ index.html) · `Application`(→ app.html) · `Evidence`(→ benchmark.html) · `Pilot`(→ pilot-packet.html) ·
  `Documentation`(→ security.html) + CTA `Test a Claim`. Barra secundaria: las páginas del grupo (Overview/In depth;
  Gate App/Decision log; Benchmark/Proof ledger/Audit and governance; Pilot packet/Decision brief; Security/Library and
  API/Threat model/Legal) y, a la derecha, el ecosistema `Krenn·IQ`(→ krenniq.com) y `Atlas`. El logo sigue llevando a krenniq.com.

## 5. Mapa de superficies (qué es qué)
| URL | Sirve | Repo/archivo |
|-----|-------|--------------|
| `krenniq.com/` | Landing KRENIQ (front door) | esta app · `docs/krenniq.html` |
| `capas.lemonground…azure/` | CAPAS (la herramienta) | esta app · `docs/index.html` |
| `https://capas.krenniq.com/in-depth.html` | CAPAS a fondo: las 18 secciones largas que salieron del home el 2026-10-13 (ledger de pruebas en `#ledger`, paralelo IBM, casos de uso…). El home quedó en ~1,100 palabras por instrucción de Osvaldo; **no vuelvas a engordarlo**: lo largo va aquí | esta app · `docs/in-depth.html` |
| `atlas.lemonground…azure/` | Atlas (la otra herramienta) | **otro repo**: `../ATLAS/` (hermano de este, bajo `01. Investigacion/`) |

Atlas es app/repo aparte — no se despliega desde aquí. Su nav ya apunta Home→landing y CAPAS→capas.
