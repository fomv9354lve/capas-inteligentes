# KRENIQ — reordenamiento de topología (marca sobre sub-proyectos)

**Fecha:** 2026-09-04
**Estado:** diseño aprobado, pendiente de plan de implementación
**Decisor:** Osvaldo
**Alcance:** infraestructura Azure + repo CAPAS + repo de marca (nuevo)

---

## 1. Problema

`krenniq.com` es la marca paraguas. CAPAS y Atlas son sub-proyectos hermanos debajo de
ella. La infraestructura actual invierte esa jerarquía en tres niveles a la vez:

1. **El landing de la marca lo sirve la app `capas`**, vía routing por cabecera `Host` en
   `capas_api.py`. La marca depende del ciclo de deploy de uno de sus sub-proyectos.
2. **El environment y el resource group se llaman `capas-*`** pero hospedan CAPAS, Atlas y
   tres proyectos de otros tracks. Un contenedor compartido nombrado como uno de sus inquilinos.
3. **Cuatro tracks conviven en un resource group**: R (capas, atlas), M (dos apps cliente +
   storage + PostgreSQL), F (teoria).

Consecuencia directa y documentada: cada `az containerapp update -n capas` tumba el binding
SNI de `krenniq.com`. El `CLAUDE.md` de CAPAS lo documenta como gotcha permanente con un
runbook de re-bind. **No es un gotcha: es el síntoma del acoplamiento.** Al deshacerlo, la
clase de bug desaparece en lugar de documentarse.

Hallazgo de gobernanza asociado: `client-pg`, un servidor PostgreSQL con datos de
trabajo de cliente (Track M), vive dentro del resource group de un proyecto de investigación
(Track R).

---

## 2. Decisiones tomadas

| # | Decisión | Elegida |
|---|---|---|
| 1 | Topología objetivo | Un RG de marca KRENIQ; cliente y teoria evacuados a los suyos |
| 2 | Hosting del landing | Azure Static Web Apps (es estático: 60 KB, cero llamadas a API) |
| 3 | Alcance de la marca | Solo Track R: CAPAS + Atlas y futuros de esa naturaleza |
| 4 | Corte con Atlas dentro de CAPAS | Dejar de hospedarlo; conservar el link de nav como hermano |
| 5 | Recrear vs. mover | **Recrear todo**, nombres correctos desde el inicio |

**Sobre la decisión 3:** el `CLAUDE.md` del workspace prohíbe cross-output M↔X, M↔F y M↔P.
Un landing que listara todos los proyectos rompería esas reglas en una superficie pública que
ve un cliente. Se acotó a Track R, que las respeta todas.

**Sobre la decisión 5:** se advirtió que recrear el environment obliga a re-validar los tres
dominios, y que diferirlo a la renovación de certificados (diciembre 2026) fusionaría el costo
con trabajo inevitable. Osvaldo reafirmó la recreación completa. Se procede con ella.

**Consecuencia de la decisión 3 sobre el contenido:** el descriptor de marca actual
"Krenn·IQ — Inteligencia Cuántica" describe solo a Atlas y se retira. La tesis del hero
("Una disciplina: decidir con número, no con humo") sí cubre a ambas herramientas y se conserva.

---

## 3. Topología

### Antes

```
capas-rg / capas-env  (IP 20.232.76.107 · lemonground-e6ebae60.eastus)
├── capas ──┬── krenniq.com          ← LA MARCA, dentro de un sub-proyecto
│           └── capas.krenniq.com
├── atlas   ─── atlas.krenniq.com
├── client-app-1                ← Track M
├── client-app-2                ← Track M
├── client-storage      (storage)   ← Track M
├── client-pg   (postgres)  ← Track M · datos de cliente
├── teoria                           ← Track F
├── caf7ef600384acr      (registry compartido por las 5 apps)
└── workspace-capasrgxIaN (log analytics)
```

### Después

```
kreniq-swa  (Static Web App)  →  krenniq.com + www.krenniq.com

kreniq-rg / kreniq-env
├── capas   0.5 cpu · 1Gi · :7860 · min0/max5  →  capas.krenniq.com
├── atlas   2.0 cpu · 4Gi · :7860 · min1/max5  →  atlas.krenniq.com
├── kreniqacr
└── kreniq-logs

client-rg / client-env
├── client-app-1  0.5 cpu · 1Gi · :8000 · min1/max1   (RECREADA)
├── client-app-2  1.0 cpu · 2Gi · :8000 · min1/max1   (RECREADA)
├── client-storage     storage                             (MOVIDO)
├── client-pg  postgres                            (MOVIDO)
└── client-acr

teoria-rg / teoria-env
└── teoria  0.25 cpu · 0.5Gi · :80 · min0/max1

capas-rg  →  eliminado al final, ya vacío
```

---

## 4. Inventario verificado

Todo lo siguiente se comprobó contra Azure el 2026-09-04, no se asume.

**Dominios custom.** Solo `capas` (`capas.krenniq.com`, `krenniq.com`) y `atlas`
(`atlas.krenniq.com`) tienen dominios bindeados. **cliente y teoria no tienen ninguno**, así que
su evacuación no toca DNS.

**Certificados administrados**, los tres en `capas-env`, vencen diciembre 2026:
`mc-capas-env-krenniq-com-3031`, `mc-capas-env-capas-krenniq-co-5290`,
`mc-capas-env-atlas-krenniq-co-8796`.

**Secretos por app** (Container Apps no permite leer sus valores):

| App | Secretos | Coste de recrear |
|---|---|---|
| `capas` | ninguno | trivial |
| `client-app-2` | ninguno | trivial |
| `teoria` | credencial de pull del ACR | trivial, se regenera |
| `atlas` | `anthropic-key` | bajo, se repone |
| `client-app-1` | `database-url`, `graph-secret`, `microsoft-provider-authentication-secret` | **alto — ver §7** |

**Identidades administradas.** `capas`, `atlas`, `client-app-1` y `client-app-2`
usan `SystemAssigned`. Recrear una app genera un principal ID nuevo: **toda asignación de rol
concedida a la identidad vieja debe re-concederse.**

**Estado del repo CAPAS.** Rama `feat/capas-fisica`. `main` local va 4 commits por delante de
`origin/main`; la rama actual suma 2 más. **Seis commits existen solo en este disco.** Además,
el claim-type `proof_admissibility` (motor + test + contratos + UI) está sin commitear y pasa
sus verificaciones. Suite: 310/310 pytest, conformance CAPAS-CONFORMANT, 7/7 verificadores
load-bearing.

---

## 5. Restricciones de Azure verificadas

| Pregunta | Respuesta | Cómo se verificó |
|---|---|---|
| ¿Se renombra un resource group? | **No.** Azure no tiene operación de rename. | conocido; sin API de rename |
| ¿Se renombra un managed environment? | **No.** Un recurso no se renombra. | idem |
| ¿`managedEnvironments` soporta move entre RGs? | **Sí** (`CrossResourceGroupResourceMove`) | `az provider show -n Microsoft.App` |
| ¿`containerApps` soporta move? | **Sí** | idem |
| ¿PostgreSQL `flexibleServers` soporta move? | **Sí** | `az provider show -n Microsoft.DBforPostgreSQL` |
| ¿`storageAccounts` soporta move? | **Sí** | `az provider show -n Microsoft.Storage` |
| ¿Una container app puede cambiar de environment? | **No.** `managedEnvironmentId` es inmutable. | restricción de la plataforma |

**Implicación clave:** como una app no puede cambiar de environment, dar a cliente su propio
environment **obliga a recrear sus apps** — de ahí el bloqueo por secretos del §7. Los datos
(Postgres, Storage) sí se mueven intactos y no pasan por recreación.

**Pendiente de verificar antes de ejecutar:** si una container app puede moverse a otro RG
dejando atrás su environment. No afecta al plan elegido (recreamos), pero determina si existe
una vía de rollback más barata para cliente. Comando de validación no destructivo:

```bash
SUB=$(az account show --query id -o tsv)
az rest --method post \
  --url "https://management.azure.com/subscriptions/$SUB/resourceGroups/capas-rg/validateMoveResources?api-version=2021-04-01" \
  --body "{\"resources\":[\"/subscriptions/$SUB/resourceGroups/capas-rg/providers/Microsoft.App/containerApps/client-app-1\"],\"targetResourceGroup\":\"/subscriptions/$SUB/resourceGroups/kreniq-rg\"}"
```

`204` = permitido. Cualquier otra cosa trae el motivo exacto.

---

## 6. Piezas de trabajo

### Pieza 0 · Salvar lo que solo existe en este disco
Commit del trabajo suelto sobre `feat/capas-fisica`: `proof_admissibility` (motor, test,
contratos, UI), la barrera de secretos del `.gitignore`, `CLAUDE.md`, `FREEZE_RUNBOOK.md`.
Después `push` de `feat/capas-fisica` **y** de `main` a `origin`, sin merge todavía — el objetivo
de esta pieza es que nada exista solo en este disco, no reordenar ramas. El merge a `main` se
decide al cerrar la pieza 3b.

Diez minutos, y elimina el único riesgo del plan que es puro downside.

### Pieza 1 · Captura de configuración
Volcar a JSON versionado, antes de cualquier acción destructiva:
- configuración completa de las 5 container apps
- configuración del environment y de los 3 certificados
- **inventario de asignaciones de rol de las 4 identidades administradas**
- registros DNS actuales de Cloudflare, tal como están hoy

Nada destructivo ocurre hasta que este volcado exista y esté commiteado. Sin él, recrear es
adivinar.

### Pieza 2 · Repo de marca `kreniq-brand`
Repo nuevo, hermano de CAPAS y ATLAS en `01. Investigacion/`. Contiene:
- `krenniq.html` (landing) y `legal.html`
- **el design system como fuente única**: `kreniq-shell.css`, `lang.js`, el logo

Hoy `kreniq-shell.css` y `lang.js` están duplicados en CAPAS y Atlas. Se resuelve de forma
verificable, no confiada: la marca es la fuente, un `sync_shell.py` copia a los consumidores, y
`designlab/layout_lint.py` se extiende para **fallar el deploy si el shell local diverge del
hash de la versión de marca**. No se cargan CSS/JS cross-origin desde `krenniq.com`: eso ataría
la disponibilidad de las herramientas a la del landing.

Contenido: se retira el descriptor "Inteligencia Cuántica", se elimina el copy caduco
"Gratis este mes de lanzamiento" (escrito el 2026-07-02, lleva dos meses en vivo), y se añade
`www` como hostname, que hoy no tiene registro DNS.

### Pieza 3a · CAPAS exclusivo de CAPAS (sin dependencias)
- Borrar los forks de Atlas: `docs/atlas-*.html` (7), `docs/evidence.html`, `docs/atlas_*.svg`
  (4), `docs/atlas_data/` — unos 800 KB
- Eliminar el redirect 301 de `capas_api.py`, que solo existía para taparlos
- `legal.html` se copia al repo de marca (se borra de CAPAS en la pieza 3b)
- Conservar el link `Atlas` en el nav y `NAV_ITEMS` intacto en `deploy_site.py` y
  `designlab/render_check.py`
- Corregir el `CLAUDE.md` de CAPAS: apunta el repo de Atlas a `OPORTUNIDADES/codex_subrepo/atlas-codex`,
  ruta que ya no existe. El repo real está en `01. Investigacion/ATLAS/`
### Pieza 3b · Cortar el cordón del landing (DEPENDE de que SWA esté vivo)

**No ejecutar hasta que `krenniq.com` sirva desde Static Web Apps y esté verificado.** Mientras
el dominio siga apuntando al environment viejo, la app `capas` es lo único que sirve el landing.

- Eliminar el bloque de routing por `Host` de `capas_api.py` — `capas` pasa a servir siempre
  `index.html`
- Borrar `docs/krenniq.html` y `docs/legal.html` de CAPAS (ya viven en el repo de marca)
- Desbindear `krenniq.com` de la app `capas`
- Actualizar el `CLAUDE.md` de CAPAS: retirar el runbook de re-bind de TLS y la sección de
  routing por Host, que dejan de aplicar

### Pieza 4 · `kreniq-rg` / `kreniq-env` y migración de las herramientas
1. Crear `kreniq-rg`, `kreniq-env`, `kreniqacr`, `kreniq-logs`
2. Importar imágenes server-side con `az acr import` (sin rebuild ni push local)
3. Desplegar `capas` y `atlas` con la configuración capturada en la pieza 1
4. Reponer `anthropic-key` en `atlas`
5. Re-conceder roles a las identidades administradas nuevas
6. Bindear hostnames y emitir certificados administrados nuevos
7. Verificar contra el FQDN de Azure **antes** de tocar DNS

### Pieza 5 · Landing a Static Web Apps
Publicar `kreniq-swa` desde el repo de marca, verificar sobre la URL por defecto de SWA, y
**solo entonces** re-apuntar `krenniq.com`.

### Pieza 6 · Evacuar `teoria`
`teoria-rg` / `teoria-env`, recrear la app (solo tiene una credencial de ACR, regenerable).
Sin dominios custom: **no toca DNS**.

### Pieza 7 · Evacuar cliente
Ventana propia y separada. `client-rg` / `client-env` / `client-acr`. Mover Postgres y Storage
(intactos, con datos). Recrear las dos apps. Requiere el prerrequisito del §7. Sin dominios
custom: **no toca DNS**.

### Pieza 8 · Eliminar `capas-rg`
Solo cuando esté vacío y todo lo demás verificado.

---

## 7. Prerrequisito bloqueante de la pieza 7

`client-app-1` es una herramienta de cliente, con base de datos, corriendo caliente
(min=1). Recrearla exige credenciales que no son legibles desde ningún sitio:

- `database-url` — reconstruible desde el servidor Postgres
- `graph-secret` y `microsoft-provider-authentication-secret` — **hay que emitir secretos
  nuevos en el registro de aplicación de Entra ID**; Azure AD tampoco permite leerlos
- re-concesión de permisos a la identidad administrada nueva

**Osvaldo debe confirmar que puede emitir esos secretos antes de que empiece la pieza 7.** Si
no puede, la pieza queda parada sin bloquear ninguna otra — pero entonces `capas-rg` no se
puede eliminar (pieza 8) y la separación de tracks queda incompleta.

---

## 8. Orden de ejecución

Cada paso reduce el riesgo del siguiente:

| # | Pieza | Toca DNS | Riesgo |
|---|---|---|---|
| 1 | 0 · Salvar el trabajo local | no | ninguno |
| 2 | 1 · Captura de configuración | no | ninguno |
| 3 | 3a · Limpiar CAPAS | no | bajo, reversible en git |
| 4 | 2 · Repo de marca | no | ninguno |
| 5 | 5 · Landing a SWA | **sí** (A `@`, `www`) | medio |
| 6 | 3b · Cortar el cordón del landing | desbind | bajo, ya hay SWA sirviendo |
| 7 | 4 · Migrar capas y atlas | **sí** (2 CNAME, 2 TXT) | **alto** |
| 8 | 6 · Evacuar teoria | no | bajo |
| 9 | 7 · Evacuar cliente | no | medio, datos de cliente |
| 10 | 8 · Eliminar capas-rg | no | ninguno si está vacío |

**Dependencia dura:** la pieza 3b elimina lo único que sirve el landing hoy. Va después de la
pieza 5 y nunca antes. Invertirlas deja `krenniq.com` sirviendo `index.html` de CAPAS.

**Regla de DNS:** un hostname a la vez, con `curl` de verificación entre cada uno. Nunca en
bloque. El environment viejo se mantiene vivo durante toda la migración: mientras exista,
revertir un registro DNS restaura el servicio.

---

## 9. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Seis commits existen solo en este disco | Pieza 0 primero, antes que nada |
| Recrear sin conocer la config | Pieza 1: volcado a JSON commiteado antes de tocar nada |
| Identidades nuevas pierden sus roles | Inventario de asignaciones en pieza 1; re-concesión explícita |
| Validación TLS falla y cae un dominio | Un hostname a la vez; environment viejo vivo como rollback |
| Secretos de cliente irrecuperables | Prerrequisito §7 confirmado antes de empezar la pieza 7 |
| Datos de cliente en riesgo | Postgres y Storage se **mueven**, nunca se recrean |
| Se borra `capas-rg` con algo dentro | Pieza 8 solo tras verificar que está vacío |
| Se corta el landing antes de tener reemplazo | Pieza 3b bloqueada tras verificar SWA en vivo |

---

## 10. Criterios de verificación

La migración está terminada cuando todo lo siguiente es cierto y comprobado:

1. `curl -sI https://krenniq.com` y `https://www.krenniq.com` → `200`, servidos por SWA
2. `curl -sI https://capas.krenniq.com` y `https://atlas.krenniq.com` → `200` desde `kreniq-env`
3. `GET https://capas.krenniq.com/api/requirements?claim_type=proof_admissibility` → responde
   el contrato, no `unknown claim_type` (confirma que lo desplegado incluye el trabajo de julio)
4. Un deploy de `capas` **no** tumba `krenniq.com` — la prueba de que el acoplamiento murió
5. `python3 benchmarks/conformance.py` → CAPAS-CONFORMANT; 310/310 pytest
6. `az resource list -g capas-rg` → vacío, y el RG eliminado
7. Ningún recurso de Track M o F en `kreniq-rg`
8. `origin/main` contiene los 6 commits que hoy solo existen en local

---

## 11. Fuera de alcance

- Deuda del `ROADMAP.md`: Gap-1 (estudio ciego n≥500), fix de backing verification, release
  0.4.0 a PyPI, segundo maintainer, trustee. Son trabajo de producto, no de topología.
- Los 3 flags abiertos en `docs/MOTOR_INGEST_LOG.md`.
- Rediseño de contenido del landing más allá de retirar el descriptor de marca y el copy caduco.
- Decidir si `atlas` debe seguir en `min=1` con 2 CPU: es decisión del proyecto Atlas.
- Los 25 documentos de `outputs/_workflow_review/` (~500 KB de estrategia sin commitear):
  el `FREEZE_RUNBOOK.md` los identifica como fuente de un paper de métodos. Se decide aparte.

---

## 12. Supuestos abiertos

Si alguno es incorrecto, el plan cambia:

1. **Registries separados** (`kreniqacr`, `client-acr`) en vez de uno compartido, porque imágenes
   de cliente y de investigación no deberían convivir si estamos separando por track. Copia
   server-side con `az acr import`: sin rebuild ni push local.
2. **`teoria` va a su propio RG** (Track F), sin mezclarse.
3. **Los comandos `az` los ejecuta Osvaldo.** El `FREEZE_RUNBOOK.md` los declara bloqueados
   para el asistente. Yo preparo, verifico y valido las salidas.
4. **Este spec vive en el repo CAPAS por ahora** y migra al repo de marca cuando exista. Es una
   incoherencia consciente: un documento de topología KRENIQ dentro de un sub-proyecto, que
   se resuelve en la pieza 2.
5. **El `FREEZE` queda levantado.** La decisión de revivir CAPAS lo deroga; `FREEZE_RUNBOOK.md`
   se conserva como procedimiento para volver a congelar, no como estado activo.
