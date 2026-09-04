# Plan 1 — Desacople de repo: CAPAS exclusivo + captura de estado + repo de marca

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dejar el repo CAPAS sirviendo solo a CAPAS, con el trabajo de julio a salvo en `origin`, el estado de Azure capturado en disco, y el design system de marca extraído a su propio repo con un candado de deriva verificable.

**Architecture:** Cuatro bloques secuenciales. Primero se salva lo que solo existe en este disco (seis commits + `proof_admissibility`). Después se captura la configuración completa de Azure a JSON versionado, porque los planes 2 y 3 se escriben *desde* ese volcado y no desde suposiciones. Luego se borran los forks de páginas de Atlas y el redirect 301 que los tapaba, con un verificador nuevo que impide que reaparezcan. Por último el design system compartido (`kreniq-shell.css`, `lang.js`, logo) se extrae al repo de marca y CAPAS pasa a consumirlo bajo un lock de hash que rompe el build si diverge.

**Tech Stack:** Python 3.14, pytest 9.1, `az` CLI, git. Sin dependencias nuevas.

**Spec:** `docs/superpowers/specs/2026-09-04-kreniq-topology-design.md`

## Global Constraints

- **Los comandos `az` los ejecuta Osvaldo.** El asistente prepara, verifica y valida salidas. Aplica a toda la Task 3.
- **Nada destructivo antes de la Task 3.** La captura de estado precede a cualquier borrado de infraestructura (que ocurre en los planes 2 y 3, no aquí).
- **No se toca DNS en este plan.** Ningún paso de aquí modifica Cloudflare.
- **`docs/krenniq.html` y `docs/legal.html` NO se borran de CAPAS en este plan.** Se copian al repo de marca; su borrado es la pieza 3b del spec y vive en el Plan 2, porque hasta que el Static Web App esté vivo, la app `capas` es lo único que sirve el landing.
- **El link `Atlas` del nav se conserva**, igual que `NAV_ITEMS` en `deploy_site.py:38` y `designlab/render_check.py:56`. CAPAS y Atlas son hermanos bajo una marca y se enlazan a propósito.
- **Toda salida `OK:`/`FAIL:` sigue el patrón de `benchmarks/verify_*.py`:** `def main() -> int`, `raise SystemExit(main())`, cabecera SPDX `Apache-2.0` y copyright `Fco. Osvaldo Morales Vilchis`.
- **Rama de trabajo:** `feat/capas-fisica`. No se hace merge a `main` en este plan.

---

### Task 1: Salvar el trabajo que solo existe en este disco

Seis commits locales no están en `origin`, y `proof_admissibility` (motor + test + contratos + UI) no está ni commiteado. Esta tarea no cambia comportamiento: elimina el riesgo de pérdida total.

**Files:**
- Modify: `capas.py`, `capas_api.py`, `docs/app.html`, `docs/capas-contracts.js`, `docs/capas-contracts.json`, `docs/index.html`, `docs/krenniq.html`, `.gitignore`
- Add: `CLAUDE.md`, `FREEZE_RUNBOOK.md`, `benchmarks/verify_proof_admissibility.py`, `docs/BRAND_KRENNIQ.md`, `docs/PROBE_MISSES.md`, `docs/tokens.css`, `examples/quantum_showcase.py`

**Interfaces:**
- Consumes: nada
- Produces: `origin/feat/capas-fisica` y `origin/main` al día. Ningún artefacto de código nuevo.

- [ ] **Step 1: Verificar que la suite está verde antes de commitear nada**

```bash
python3 -m pytest benchmarks/ -q --no-header -p no:cacheprovider
python3 benchmarks/conformance.py
python3 benchmarks/verify_proof_admissibility.py
```

Esperado: `310 passed`, `CAPAS-CONFORMANT`, y `OK: proof_admissibility gates the word 'theorem'...`. Si algo falla, **detente y repórtalo** — no commitees sobre rojo.

- [ ] **Step 2: Commitear el claim-type `proof_admissibility`**

```bash
git add capas.py benchmarks/verify_proof_admissibility.py \
        docs/capas-contracts.json docs/capas-contracts.js docs/app.html
git commit -m "Add proof_admissibility: gate the word 'theorem' on quantifier scope

A universally-quantified claim ('for all', 'all orders') is licensed only by a
bound uniform over the quantified index. Finite or leading-order checks license
the checked scope and nothing beyond it, so they downgrade to 'leading-order
result + conjectured remainder' rather than being accepted as a theorem. An
unidentified load-bearing step, or a step that does not re-derive, REJECTs.

Locked by benchmarks/verify_proof_admissibility.py."
```

- [ ] **Step 3: Commitear la barrera de secretos y la documentación operativa**

La entrada `.claude/` del `.gitignore` es la barrera que impide publicar `settings.local.json`, que contiene claves en texto plano. Hoy la protección misma está sin commitear.

```bash
git add .gitignore CLAUDE.md FREEZE_RUNBOOK.md docs/BRAND_KRENNIQ.md \
        docs/PROBE_MISSES.md docs/tokens.css examples/quantum_showcase.py
git commit -m "Commit the secrets barrier and the operational docs

.gitignore gains .claude/, which is what keeps settings.local.json (API keys in
plaintext) out of the repo — the barrier itself was untracked. Adds the project
CLAUDE.md, the freeze runbook, and the brand/probe notes that were living only
on disk."
```

- [ ] **Step 4: Commitear el trabajo de contenido de julio**

`docs/index.html` y `docs/krenniq.html` están modificados y **ya en producción**, pero sin
commitear. Van en su propio commit: no son limpieza de Atlas y no deben acabar barridos por el
`git add -A docs` de la Task 3.

`capas_api.py` **se deja fuera a propósito.** Su único diff son las 10 líneas del redirect 301
que la Task 3 elimina; al quitarlas, el archivo vuelve a su estado en HEAD y no queda nada que
commitear.

```bash
git add docs/index.html docs/krenniq.html
git commit -m "Commit the July landing work that was live but untracked

index.html gained the 'Proof on a real paper' section: 13 of 13 closed-form
claims re-derived straight from a PDF, one tabulated row flagged at 2.6% off the
paper's own formula, zero numbers typed by a model. krenniq.html dropped the
three pricing tiers for a single open-access block.

Both have been serving on capas.krenniq.com since 2026-07-02; only the source
was missing."
```

- [ ] **Step 5: Verificar que no queda nada sensible sin trackear ni trackeado por error**

```bash
git check-ignore -v .claude/settings.local.json
git ls-files | xargs grep -lIE "(sk-ant|AKIA|-----BEGIN (RSA|OPENSSH|PRIVATE))" 2>/dev/null || echo "sin secretos trackeados"
```

Esperado: la primera línea confirma que `.gitignore:25` lo ignora; la segunda imprime `sin secretos trackeados`.

- [ ] **Step 6: Empujar ambas ramas a `origin`** — ⚠️ **NO lo ejecuta un subagente**

Publicar en un remoto compartido es un efecto fuera del árbol de trabajo. Este paso lo confirma
Osvaldo explícitamente y lo ejecuta el controlador, nunca un implementador.

```bash
git push origin main
git push origin feat/capas-fisica
```

- [ ] **Step 7: Verificar que `origin` ya tiene todo**

```bash
git fetch origin
git log --oneline origin/main -1
git status -sb | head -1
```

Esperado: `origin/main` en `4e189e9` o posterior, y la línea de status **sin** `ahead`. Si aparece `ahead`, el push no llegó.

---

### Task 2: Verificador de aislamiento de superficie

TDD real: este verificador falla hoy, porque los forks y el redirect existen. La Task 3 lo pone en verde.

**Files:**
- Create: `benchmarks/verify_capas_surface_isolation.py`

**Interfaces:**
- Consumes: nada
- Produces: `benchmarks/verify_capas_surface_isolation.py`, ejecutable con `python3`, exit `0` si la superficie es solo-CAPAS y `1` si no. La Task 4 lo registra en `conformance.py` bajo el nombre de suite `surface_isolation`.

- [ ] **Step 1: Escribir el verificador que falla**

Crear `benchmarks/verify_capas_surface_isolation.py`:

```python
#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""CAPAS serves CAPAS: no forked sibling pages, and no redirect standing in for them.

docs/ carried frozen copies of a sibling product's pages, and capas_api.py grew a
301 to paper over the fact that they had gone stale. Both are gone; this asserts
they stay gone. A vendored fork drifts from its source in silence — the redirect
was the tell, not the fix.

The nav link to the sibling is deliberate and is asserted PRESENT: CAPAS and Atlas
are siblings under one brand and cross-link on purpose. Isolation here means CAPAS
stops *hosting* another product, not that it stops *pointing* at it.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
API = ROOT / "capas_api.py"

FORBIDDEN_GLOBS = ("atlas-*.html", "atlas_*.svg")
FORBIDDEN_FILES = ("evidence.html",)
FORBIDDEN_DIRS = ("atlas_data",)
SIBLING_NAV_HREF = 'href="https://atlas.krenniq.com/"'


def main() -> int:
    fails: list[str] = []

    for pat in FORBIDDEN_GLOBS:
        for f in sorted(DOCS.glob(pat)):
            fails.append(f"forked sibling page still present: docs/{f.name}")
    for name in FORBIDDEN_FILES:
        if (DOCS / name).exists():
            fails.append(f"forked sibling page still present: docs/{name}")
    for d in FORBIDDEN_DIRS:
        if (DOCS / d).is_dir():
            fails.append(f"forked sibling assets still present: docs/{d}/")

    api = API.read_text(encoding="utf-8")
    if "atlas.krenniq.com" in api:
        fails.append("capas_api.py still redirects to the sibling product (the 301 fork-patch)")

    index = (DOCS / "index.html").read_text(encoding="utf-8")
    if SIBLING_NAV_HREF not in index:
        fails.append("docs/index.html lost the sibling nav link to Atlas — that link is intended")

    if fails:
        print("FAIL:")
        for x in fails:
            print("  -", x)
        return 1
    print("OK: CAPAS's surface is CAPAS only — no forked sibling pages, no assets, and no "
          "redirect standing in for them; the intended sibling nav link is intact.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Ejecutarlo para confirmar que FALLA**

```bash
python3 benchmarks/verify_capas_surface_isolation.py; echo "exit=$?"
```

Esperado: `exit=1`, con unas 12 líneas listando `atlas-*.html`, `atlas_*.svg`, `evidence.html`, `atlas_data/` y el redirect de `capas_api.py`. **Si sale `exit=0`, el verificador está mal escrito** — no detecta nada y hay que arreglarlo antes de seguir.

- [ ] **Step 3: Commitear el verificador en rojo**

```bash
git add benchmarks/verify_capas_surface_isolation.py
git commit -m "Add surface-isolation check (red): CAPAS must not host sibling pages

Fails today by design: docs/ still carries the forked Atlas pages and
capas_api.py still redirects around them. The next commit makes it pass."
```

---

### Task 3: Borrar los forks y el redirect

**Files:**
- Delete: `docs/atlas-audit.html`, `docs/atlas-benchmark.html`, `docs/atlas-intro.html`, `docs/atlas-methodology.html`, `docs/atlas-pilot.html`, `docs/atlas-pricing.html`, `docs/atlas-security.html`, `docs/evidence.html`, `docs/atlas_ad.svg`, `docs/atlas_channel.svg`, `docs/atlas_proofreading.svg`, `docs/atlas_reliability.svg`, `docs/atlas_data/`
- Modify: `capas_api.py` (quitar el bloque 301, líneas ~266-274)

**Interfaces:**
- Consumes: `benchmarks/verify_capas_surface_isolation.py` de la Task 2
- Produces: ese verificador en verde

- [ ] **Step 1: Confirmar que ninguno de esos archivos está trackeado**

```bash
git ls-files docs/atlas-*.html docs/atlas_*.svg docs/evidence.html docs/atlas_data 2>/dev/null || true
```

Esperado: **salida vacía**. Los 13 son untracked, así que se borran del disco y no del índice. Si alguno aparece aquí, usa `git rm` para ese en el paso siguiente.

- [ ] **Step 2: Borrar los forks**

```bash
rm -f docs/atlas-audit.html docs/atlas-benchmark.html docs/atlas-intro.html \
      docs/atlas-methodology.html docs/atlas-pilot.html docs/atlas-pricing.html \
      docs/atlas-security.html docs/evidence.html \
      docs/atlas_ad.svg docs/atlas_channel.svg docs/atlas_proofreading.svg \
      docs/atlas_reliability.svg
rm -rf docs/atlas_data
```

- [ ] **Step 3: Quitar el redirect 301 de `capas_api.py`**

Borrar este bloque completo (está justo después de la asignación de `p` en el handler, alrededor de la línea 266):

```python
        # Atlas-page forks: docs/ guarda copias VIEJAS de páginas de Atlas (evidence.html,
        # atlas-*.html, congeladas pre-audit — p.ej. "Route accuracy", TVD cherry-picked).
        # Una sola fuente de verdad: 301 al sitio canónico. Nunca más se desincronizan.
        _fork = p.lstrip("/")
        if _fork == "evidence.html" or _fork.startswith("atlas-"):
            self.send_response(301)
            self.send_header("Location", "https://atlas.krenniq.com/" + _fork)
            self.send_header("Cache-Control", "no-cache")
            self._cors(); self.end_headers()
            return
```

La línea siguiente (`f = (DOCS / p.lstrip("/")).resolve()`) queda intacta. **No toques el bloque de routing por `Host`** — ese se elimina en el Plan 2, cuando el Static Web App ya sirva el landing.

- [ ] **Step 4: Ejecutar el verificador y confirmar que PASA**

```bash
python3 benchmarks/verify_capas_surface_isolation.py; echo "exit=$?"
```

Esperado: `exit=0` y `OK: CAPAS's surface is CAPAS only ...`

- [ ] **Step 5: Confirmar que no se rompió nada más**

```bash
python3 -m pytest benchmarks/ -q --no-header -p no:cacheprovider
python3 benchmarks/conformance.py
```

Esperado: `310 passed` y `CAPAS-CONFORMANT`.

Para el lint, ojo con el criterio:

`designlab/layout_lint.py` **no está en verde y nunca lo ha estado**: hace glob de `docs/*.html`
y lintea como página de marca archivos que estructuralmente no lo son — `logo_kreniq_volum_trico.html`
es el contenido del iframe del logo (no puede contener un iframe de sí mismo ni un `<nav>`), y
`live.html`, `product.html` y `gemini-code-*.html` no tienen nav. Otros fallan por ancho de columna.

El criterio no es "verde", es **"sin regresión"**: los mismos 9 fallos preexistentes, ninguno nuevo.
La baseline está congelada en
`.superpowers/sdd/2026-09-04-kreniq-repo-decoupling/lint-baseline.txt`:

```
app.html  gate-app-mock.html  gate-app-mock2.html  gemini-code-1781935819867.html
krenniq.html  legal.html  live.html  logo_kreniq_volum_trico.html  product.html
```

```bash
python3 designlab/layout_lint.py 2>&1 | grep "^✗" | sed 's/^✗ //' | sort \
  > /tmp/lint-now.txt
diff .superpowers/sdd/2026-09-04-kreniq-repo-decoupling/lint-baseline.txt /tmp/lint-now.txt \
  && echo "LINT OK — sin regresión contra la baseline"
```

Esperado: `LINT OK — sin regresión contra la baseline`. El lint pasa de evaluar 23 páginas a 15,
porque se borraron 8 archivos HTML.

- [ ] **Step 6: Corregir la ruta caduca del repo de Atlas en el `CLAUDE.md`**

`CLAUDE.md:57` apunta el repo de Atlas a `OPORTUNIDADES/codex_subrepo/atlas-codex`, ruta que
ya no existe. El repo real está en `01. Investigacion/ATLAS/`, hermano de este.

```bash
python3 - <<'EOF'
import pathlib
p = pathlib.Path("CLAUDE.md")
s = p.read_text(encoding="utf-8")
old = "**otro repo**: `OPORTUNIDADES/codex_subrepo/atlas-codex`"
new = "**otro repo**: `../ATLAS/` (hermano de este, bajo `01. Investigacion/`)"
assert old in s, "la ruta caduca ya no está en CLAUDE.md — revisa antes de seguir"
p.write_text(s.replace(old, new), encoding="utf-8")
print("CLAUDE.md:57 corregido")
EOF
```

**No toques `CLAUDE.md:15`** (la descripción del routing por Host): esa línea deja de aplicar
en el Plan 2 y se reescribe allí, junto con el cambio de código que la vuelve falsa.

- [ ] **Step 7: Commitear**

Tras la Task 1, `docs/index.html` y `docs/krenniq.html` ya están commiteados y `capas_api.py`
ha vuelto a su estado en HEAD, así que este `add` recoge solo los borrados y el `CLAUDE.md`.
Confirma que es así antes de commitear:

```bash
git add -A docs capas_api.py CLAUDE.md
git status --porcelain --cached   # esperado: solo líneas 'D ' de docs/ + 'M  CLAUDE.md'
git commit -m "Remove the vendored sibling pages and the redirect that covered them

docs/ carried 12 frozen copies of Atlas pages plus its data directory (~800 KB),
and capas_api.py 301'd around them because they had gone stale. Deleting the
forks removes the reason the redirect existed. CAPAS keeps the nav link to
Atlas: siblings under one brand cross-link on purpose.

verify_capas_surface_isolation.py goes green. CLAUDE.md's pointer to the Atlas
repo is corrected: it named a path that no longer exists."
```

---

### Task 4: Registrar el verificador en el conformance

**Files:**
- Modify: `benchmarks/conformance.py:29-36` (tupla `SUITES`)

**Interfaces:**
- Consumes: `benchmarks/verify_capas_surface_isolation.py`
- Produces: la suite `surface_isolation` corriendo en cada `conformance.py`, y por tanto en CI firmado por Sigstore

- [ ] **Step 1: Añadir la entrada a `SUITES`**

Insertar después de la línea de `audit_hash_reproduces`, respetando el formato de tres campos `(nombre, ruta, descripción)`:

```python
    ("surface_isolation", "benchmarks/verify_capas_surface_isolation.py", "CAPAS's surface hosts CAPAS only; no vendored sibling pages"),
```

- [ ] **Step 2: Ejecutar el conformance y verificar que la suite aparece**

```bash
python3 benchmarks/conformance.py | grep -E "surface_isolation|CAPAS-CONFORMANT"
```

Esperado: una línea `OK surface_isolation ...` y la línea final `CAPAS-CONFORMANT`.

- [ ] **Step 3: Anotar el cambio de hash**

El `result hash` del conformance cambia al añadir una suite: antes era `sha256:3d3b5cf39aaffef23fa8562b`. Es esperado — el hash cubre el perfil de suites, y el perfil cambió. Anota el nuevo valor en el mensaje de commit.

- [ ] **Step 4: Commitear**

```bash
git add benchmarks/conformance.py
git commit -m "Register surface_isolation in the conformance suite

The check now runs on neutral CI and is Sigstore-signed with the rest, so a
re-vendored sibling page fails the badge rather than sitting unnoticed in docs/.
Result hash moves (the suite profile changed), which is expected."
```

---

### Task 5: Captura del estado de Azure

Los planes 2 y 3 recrean apps. Recrear sin conocer la configuración es adivinar. Esta tarea produce el volcado del que se escribirán esos planes, y un validador que asegura que el volcado está completo antes de que nadie borre nada.

**Files:**
- Create: `ops/capture_azure_state.sh`, `ops/verify_capture.py`, `benchmarks/test_verify_capture.py`
- Create (generado, versionado): `ops/azure_state/*.json`

**Interfaces:**
- Consumes: nada
- Produces: `ops/verify_capture.py` con `validate(state_dir: Path) -> list[str]` que devuelve una lista de fallos vacía si la captura está completa; `main() -> int` la envuelve con el patrón `OK:`/`FAIL:`

- [ ] **Step 1: Escribir el test del validador con fixtures**

Crear `benchmarks/test_verify_capture.py`:

```python
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""The capture validator must reject an incomplete dump before anything is deleted."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ops"))
from verify_capture import REQUIRED_APPS, validate  # noqa: E402


def _app(name: str) -> dict:
    return {
        "name": name,
        "identity": {"type": "SystemAssigned", "principalId": "p-" + name},
        "properties": {
            "configuration": {"ingress": {"targetPort": 8000, "external": True}},
            "template": {
                "containers": [{"image": "acr/x:1", "resources": {"cpu": 0.5, "memory": "1Gi"}}],
                "scale": {"minReplicas": 1, "maxReplicas": 1},
            },
        },
    }


def _complete(tmp: Path) -> Path:
    d = tmp / "azure_state"
    d.mkdir()
    for a in REQUIRED_APPS:
        (d / f"app-{a}.json").write_text(json.dumps(_app(a)))
        (d / f"secrets-{a}.json").write_text("[]")
        (d / f"roles-{a}.json").write_text("[]")
    (d / "env-capas-env.json").write_text(json.dumps(
        {"properties": {"staticIp": "20.232.76.107", "defaultDomain": "x.eastus.azurecontainerapps.io"}}))
    (d / "certs-capas-env.json").write_text(json.dumps([{"name": "c1"}, {"name": "c2"}, {"name": "c3"}]))
    (d / "resources.json").write_text("[]")
    return d


def test_complete_capture_passes(tmp_path):
    assert validate(_complete(tmp_path)) == []


def test_missing_app_is_caught(tmp_path):
    d = _complete(tmp_path)
    (d / "app-teoria.json").unlink()
    fails = validate(d)
    assert any("teoria" in f for f in fails)


def test_missing_role_inventory_is_caught(tmp_path):
    d = _complete(tmp_path)
    (d / "roles-capas.json").unlink()
    fails = validate(d)
    assert any("roles" in f and "capas" in f for f in fails)


def test_app_without_ingress_port_is_caught(tmp_path):
    d = _complete(tmp_path)
    bad = json.loads((d / "app-atlas.json").read_text())
    bad["properties"]["configuration"]["ingress"] = None
    (d / "app-atlas.json").write_text(json.dumps(bad))
    fails = validate(d)
    assert any("atlas" in f and "ingress" in f for f in fails)


def test_env_without_static_ip_is_caught(tmp_path):
    d = _complete(tmp_path)
    (d / "env-capas-env.json").write_text(json.dumps({"properties": {"defaultDomain": "x"}}))
    fails = validate(d)
    assert any("staticIp" in f for f in fails)
```

- [ ] **Step 2: Ejecutar el test y confirmar que falla por import**

```bash
python3 -m pytest benchmarks/test_verify_capture.py -q --no-header
```

Esperado: `ModuleNotFoundError: No module named 'verify_capture'`.

- [ ] **Step 3: Escribir el validador**

Crear `ops/verify_capture.py`:

```python
#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Gate the Azure capture before anything gets recreated.

Recreating a container app requires its full configuration, and Container Apps
secrets are write-only: what is not captured here is not recoverable later. This
refuses to call a dump complete unless every app carries its ingress, resources,
scale, secret names and role inventory, and the environment carries the static IP
and default domain that the DNS cutover is measured against.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED_APPS = ("capas", "atlas", "client-app-1", "client-app-2", "teoria")
ENV_NAME = "capas-env"
EXPECTED_CERTS = 3


def _load(path: Path):
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def validate(state_dir: Path) -> list[str]:
    fails: list[str] = []

    for app in REQUIRED_APPS:
        doc = _load(state_dir / f"app-{app}.json")
        if doc is None:
            fails.append(f"missing or unreadable app config: app-{app}.json")
        else:
            props = doc.get("properties", {})
            ingress = (props.get("configuration") or {}).get("ingress")
            if not ingress or ingress.get("targetPort") is None:
                fails.append(f"{app}: ingress/targetPort not captured — cannot recreate")
            containers = (props.get("template") or {}).get("containers") or []
            if not containers or not containers[0].get("resources"):
                fails.append(f"{app}: container resources not captured — cannot recreate")
            if (props.get("template") or {}).get("scale") is None:
                fails.append(f"{app}: scale not captured — cannot recreate")

        if _load(state_dir / f"secrets-{app}.json") is None:
            fails.append(f"{app}: secret names not captured (secrets-{app}.json)")
        if _load(state_dir / f"roles-{app}.json") is None:
            fails.append(f"{app}: roles inventory not captured (roles-{app}.json) — "
                         "a recreated identity loses every assignment")

    env = _load(state_dir / f"env-{ENV_NAME}.json")
    if env is None:
        fails.append(f"missing environment config: env-{ENV_NAME}.json")
    else:
        p = env.get("properties", {})
        if not p.get("staticIp"):
            fails.append("environment staticIp not captured — DNS cutover has no baseline")
        if not p.get("defaultDomain"):
            fails.append("environment defaultDomain not captured — CNAME target unknown")

    certs = _load(state_dir / f"certs-{ENV_NAME}.json")
    if certs is None:
        fails.append(f"missing certificate list: certs-{ENV_NAME}.json")
    elif len(certs) != EXPECTED_CERTS:
        fails.append(f"expected {EXPECTED_CERTS} managed certificates, captured {len(certs)}")

    if _load(state_dir / "resources.json") is None:
        fails.append("missing resource inventory: resources.json")

    return fails


def main() -> int:
    state_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "azure_state"
    fails = validate(state_dir)
    if fails:
        print("FAIL:")
        for x in fails:
            print("  -", x)
        return 1
    print(f"OK: capture at {state_dir} is complete — every app carries ingress, resources, scale, "
          "secret names and role inventory; the environment carries staticIp and defaultDomain. "
          "Safe to plan recreation against it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Ejecutar los tests y confirmar que pasan**

```bash
python3 -m pytest benchmarks/test_verify_capture.py -q --no-header
```

Esperado: `5 passed`.

- [ ] **Step 5: Escribir el script de captura**

Crear `ops/capture_azure_state.sh` y hacerlo ejecutable:

```bash
#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
#
# Vuelca el estado completo de un resource group antes de recrear nada.
# Los secretos de Container Apps son de solo escritura: esto captura sus NOMBRES,
# no sus valores. Reponer los valores es trabajo manual — ver §7 del spec.
set -euo pipefail

RG="${1:-capas-rg}"
ENV_NAME="${2:-capas-env}"
OUT="$(cd "$(dirname "$0")" && pwd)/azure_state"
mkdir -p "$OUT"

echo "capturando $RG -> $OUT"

az containerapp list -g "$RG" --query "[].name" -o tsv > "$OUT/apps.txt"

while read -r a; do
  [ -z "$a" ] && continue
  echo "  app: $a"
  az containerapp show -n "$a" -g "$RG" -o json          > "$OUT/app-$a.json"
  az containerapp secret list -n "$a" -g "$RG" -o json    > "$OUT/secrets-$a.json"
  pid=$(az containerapp show -n "$a" -g "$RG" --query "identity.principalId" -o tsv)
  if [ -n "$pid" ] && [ "$pid" != "None" ]; then
    az role assignment list --assignee "$pid" --all -o json > "$OUT/roles-$a.json"
  else
    echo "[]" > "$OUT/roles-$a.json"
  fi
done < "$OUT/apps.txt"

az containerapp env show -n "$ENV_NAME" -g "$RG" -o json             > "$OUT/env-$ENV_NAME.json"
az containerapp env certificate list -n "$ENV_NAME" -g "$RG" -o json > "$OUT/certs-$ENV_NAME.json"
az resource list -g "$RG" -o json                                    > "$OUT/resources.json"

echo "listo. valida con: python3 ops/verify_capture.py"
```

```bash
chmod +x ops/capture_azure_state.sh
```

- [ ] **Step 6: Osvaldo ejecuta la captura**

Este paso lo corre Osvaldo, no el asistente:

```bash
./ops/capture_azure_state.sh capas-rg capas-env
python3 ops/verify_capture.py
```

Esperado: `OK: capture at .../ops/azure_state is complete ...`. Si sale `FAIL:`, **no continúes con los planes 2 o 3** — la captura incompleta es exactamente lo que este validador existe para bloquear.

- [ ] **Step 7: Confirmar que el volcado no contiene valores de secretos**

```bash
grep -ril "value" ops/azure_state/secrets-*.json
python3 -c "
import json,glob
for f in glob.glob('ops/azure_state/secrets-*.json'):
    for s in json.load(open(f)):
        assert 'value' not in s or not s['value'], f'{f} trae un valor de secreto en claro'
print('sin valores de secretos en el volcado')"
```

Esperado: `sin valores de secretos en el volcado`. Si algún secreto trajera valor, **no commitees** y repórtalo.

- [ ] **Step 8: Commitear captura, validador y tests**

```bash
git add ops/capture_azure_state.sh ops/verify_capture.py \
        benchmarks/test_verify_capture.py ops/azure_state
git commit -m "Capture Azure state before anything is recreated

Container Apps secrets are write-only and a recreated managed identity loses
every role assignment, so what is not captured now is not recoverable later.
verify_capture.py refuses to call a dump complete unless each app carries its
ingress, resources, scale, secret names and role inventory, and the environment
carries the static IP and default domain the DNS cutover is measured against.

Secret NAMES only; no values are dumped."
```

---

### Task 6: Repo de marca `kreniq-brand`

El design system (`kreniq-shell.css`, `lang.js`, el logo) lo comparten las 8 páginas de CAPAS, el landing y Atlas. Hoy vive dentro de CAPAS, que es uno de sus consumidores. Se extrae al nivel de la marca.

**Files:**
- Create (repo nuevo, fuera de este árbol): `../kreniq-brand/` con `krenniq.html`, `legal.html`, `kreniq-shell.css`, `lang.js`, `krenniq-logo.png`, `logo_kreniq_volum_trico.html`, `shell.lock.json`, `README.md`, `.gitignore`
- **No modifica** `docs/krenniq.html` ni `docs/legal.html` en CAPAS: se copian, no se mueven (ver Global Constraints)

**Interfaces:**
- Consumes: los archivos de `docs/` listados arriba
- Produces: `../kreniq-brand/shell.lock.json`, un objeto `{"kreniq-shell.css": "<sha256>", "lang.js": "<sha256>"}` que la Task 7 consume como fuente de verdad del lock

- [ ] **Step 1: Crear el repo e inicializarlo**

```bash
BRAND="$(cd .. && pwd)/kreniq-brand"
mkdir -p "$BRAND"
cd "$BRAND" && git init -q && cd -
```

- [ ] **Step 2: Copiar el landing y el design system**

```bash
BRAND="$(cd .. && pwd)/kreniq-brand"
cp docs/krenniq.html docs/legal.html "$BRAND/"
cp docs/kreniq-shell.css docs/lang.js docs/krenniq-logo.png "$BRAND/"
cp docs/logo_kreniq_volum_trico.html "$BRAND/"
ls -la "$BRAND"
```

Esperado: siete archivos. Los cuatro del shell están verificados presentes en `docs/`:
`kreniq-shell.css` (7.8 K), `lang.js` (2.9 K), `krenniq-logo.png` (11 K) y
`logo_kreniq_volum_trico.html` (7.3 K), este último referenciado por `layout_lint.py` como
logo canónico de fondo.

- [ ] **Step 3: Corregir el contenido del landing**

Dos arreglos que el spec §2 y §6 exigen, ahora que el landing vive en la marca.

**(a) El descriptor de marca.** `Krenn·IQ — Inteligencia Cuántica` describe solo a Atlas; la
decisión 3 acotó KRENIQ a infraestructura de investigación verificable, que cubre a las dos
herramientas. Cuatro ocurrencias en `krenniq.html`: línea 4 (`<title>`), 25 (`.nav-logo-sub`),
38 (`.hero-eyebrow`) y 125 (footer).

**(b) El copy caduco.** Línea 65 dice `Gratis este mes de lanzamiento` / `Free this launch
month`. Se escribió el 2026-07-02 y lleva dos meses en vivo: es un claim temporal falso en la
puerta de entrada de una marca cuya tesis es que los claims portan su licencia. Se sustituye
por uno sin fecha.

```bash
BRAND="$(cd .. && pwd)/kreniq-brand"
python3 - "$BRAND" <<'EOF'
import pathlib, sys
p = pathlib.Path(sys.argv[1]) / "krenniq.html"
s = p.read_text(encoding="utf-8")
subs = [
    ("<title>Krenn·IQ — Inteligencia Cuántica</title>",
     "<title>Krenn·IQ — Infraestructura de verificación</title>"),
    ('data-en="Quantum Intelligence"', 'data-en="Verification Infrastructure"'),
    ('data-en="Krenn&middot;IQ — Quantum Intelligence">Krenn&middot;IQ — Inteligencia Cuántica</div>',
     'data-en="Krenn&middot;IQ — Verification Infrastructure">Krenn&middot;IQ — Infraestructura de verificación</div>'),
    ('data-en="Quantum Intelligence &middot; verdicts from evidence, not noise">Inteligencia Cuántica &middot; veredictos con evidencia, no humo</span>',
     'data-en="Verification infrastructure &middot; verdicts from evidence, not noise">Infraestructura de verificación &middot; veredictos con evidencia, no humo</span>'),
    ('data-en="Free this launch month. Open engine.">Gratis este mes de lanzamiento. Motor abierto.</h2>',
     'data-en="Open and free. Apache-2.0 engine.">Abierto y gratis. Motor Apache-2.0.</h2>'),
]
missed = [a for a, _ in subs if a not in s]
if missed:
    print("NO ENCONTRADO (revisa antes de seguir):")
    for m in missed:
        print("  -", m[:90])
    raise SystemExit(1)
for a, b in subs:
    s = s.replace(a, b)
p.write_text(s, encoding="utf-8")
print("landing corregido: descriptor de marca + copy caduco")
EOF
```

- [ ] **Step 4: Confirmar que no queda rastro de lo viejo**

```bash
BRAND="$(cd .. && pwd)/kreniq-brand"
grep -c "Inteligencia Cuántica\|Quantum Intelligence\|launch month\|mes de lanzamiento" "$BRAND/krenniq.html" || echo "0 — limpio"
```

Esperado: `0 — limpio`.

> **Requiere tu visto bueno:** el descriptor nuevo (`Infraestructura de verificación` /
> `Verification Infrastructure`) es una propuesta, no una decisión tomada. Cubre a CAPAS
> (admisibilidad de claims) y a Atlas (si un claim cuántico necesita QPU) sin encerrar la
> marca en lo cuántico. Si prefieres otro, cámbialo aquí antes de ejecutar.

- [ ] **Step 5: Generar el lock de hashes**

```bash
BRAND="$(cd .. && pwd)/kreniq-brand"
python3 -c "
import hashlib, json, pathlib, sys
brand = pathlib.Path(sys.argv[1])
lock = {n: hashlib.sha256((brand/n).read_bytes()).hexdigest() for n in ('kreniq-shell.css','lang.js')}
(brand/'shell.lock.json').write_text(json.dumps(lock, indent=2, sort_keys=True) + '\n')
print(json.dumps(lock, indent=2))
" "$BRAND"
```

- [ ] **Step 6: Escribir el README del repo de marca**

Crear `../kreniq-brand/README.md`:

```markdown
# kreniq-brand

La marca KRENIQ: el landing de `krenniq.com`, sus términos, y el design system que
comparten los sub-proyectos.

KRENIQ es el paraguas. CAPAS y Atlas son sub-proyectos hermanos debajo de ella y
consumen este shell; no lo forkean. `shell.lock.json` fija el sha256 de
`kreniq-shell.css` y `lang.js`, y cada consumidor rompe su build si su copia
diverge de esos hashes.

## Contenido

| Archivo | Qué es |
|---|---|
| `krenniq.html` | Landing de `krenniq.com` |
| `legal.html` | Términos, privacidad y datos |
| `kreniq-shell.css` | Fuente única del shell: nav, cards, tokens de layout |
| `lang.js` | Toggle ES/EN, cookie `kq_lang` a nivel `.krenniq.com` |
| `krenniq-logo.png`, `logo_kreniq_volum_trico.html` | Logos canónicos |
| `shell.lock.json` | sha256 del shell; lo consumen CAPAS y Atlas |

## Al cambiar el shell

1. Edita `kreniq-shell.css` o `lang.js` aquí.
2. Regenera el lock.
3. En cada consumidor: `python3 scripts/sync_shell.py` y commitea la copia nueva.

Un consumidor que no sincronice falla su lint. Es deliberado: la deriva silenciosa
del shell es lo que este lock existe para impedir.
```

- [ ] **Step 7: Commitear el repo de marca**

```bash
BRAND="$(cd .. && pwd)/kreniq-brand"
cd "$BRAND"
printf '.DS_Store\n' > .gitignore
git add -A
git commit -m "Seed the KRENIQ brand repo: landing, terms and the shared shell

The brand landing and the design system that CAPAS and Atlas both consume lived
inside CAPAS, which is one of their consumers. They move up to the brand, which
is where they belong. shell.lock.json pins the shell's sha256 so a consumer that
drifts fails its own build."
cd -
```

---

### Task 7: Lock de deriva del shell en CAPAS

**Files:**
- Create: `scripts/sync_shell.py`, `docs/shell.lock.json`, `benchmarks/test_shell_lock.py`
- Modify: `designlab/layout_lint.py` (añadir la comprobación de lock a `main()`)

**Interfaces:**
- Consumes: `../kreniq-brand/shell.lock.json` de la Task 6
- Produces: `shell_lock_drift(docs_dir: Path, lock_path: Path) -> list[str]` en `designlab/layout_lint.py`, invocada desde `main()`

- [ ] **Step 1: Escribir el test del detector de deriva**

Crear `benchmarks/test_shell_lock.py`:

```python
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""The shell lock must catch a consumer whose copy drifted from the brand's."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "designlab"))
from layout_lint import shell_lock_drift  # noqa: E402

LOCKED = ("kreniq-shell.css", "lang.js")


def _setup(tmp: Path, css: bytes = b"a{}", js: bytes = b"var a;") -> tuple[Path, Path]:
    docs = tmp / "docs"
    docs.mkdir()
    (docs / "kreniq-shell.css").write_bytes(css)
    (docs / "lang.js").write_bytes(js)
    lock = tmp / "shell.lock.json"
    lock.write_text(json.dumps({
        "kreniq-shell.css": hashlib.sha256(css).hexdigest(),
        "lang.js": hashlib.sha256(js).hexdigest(),
    }))
    return docs, lock


def test_in_sync_reports_no_drift(tmp_path):
    docs, lock = _setup(tmp_path)
    assert shell_lock_drift(docs, lock) == []


def test_edited_css_is_caught(tmp_path):
    docs, lock = _setup(tmp_path)
    (docs / "kreniq-shell.css").write_bytes(b"a{color:red}")
    drift = shell_lock_drift(docs, lock)
    assert any("kreniq-shell.css" in d for d in drift)


def test_missing_consumer_file_is_caught(tmp_path):
    docs, lock = _setup(tmp_path)
    (docs / "lang.js").unlink()
    drift = shell_lock_drift(docs, lock)
    assert any("lang.js" in d for d in drift)


def test_missing_lock_is_caught(tmp_path):
    docs, lock = _setup(tmp_path)
    lock.unlink()
    drift = shell_lock_drift(docs, lock)
    assert any("lock" in d.lower() for d in drift)
```

- [ ] **Step 2: Ejecutar y confirmar que falla por import**

```bash
python3 -m pytest benchmarks/test_shell_lock.py -q --no-header
```

Esperado: `ImportError: cannot import name 'shell_lock_drift'`.

- [ ] **Step 3: Añadir `shell_lock_drift` a `designlab/layout_lint.py`**

Insertar tras `_nav_signature` (alrededor de la línea 46), antes de `lint_page`:

```python
LOCKED_SHELL_FILES = ("kreniq-shell.css", "lang.js")


def shell_lock_drift(docs_dir: Path, lock_path: Path) -> list[str]:
    """El shell de marca es fuente única: una copia local que difiere del lock es deriva.

    El lock lo publica el repo kreniq-brand. Un consumidor que edita su copia en vez de
    editar la fuente rompe la consistencia entre los tres sitios en silencio; esto la
    convierte en un fallo de build.
    """
    import hashlib
    import json

    if not lock_path.is_file():
        return [f"shell lock missing: {lock_path} — run scripts/sync_shell.py"]
    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return [f"shell lock unreadable: {lock_path}"]

    drift = []
    for name in LOCKED_SHELL_FILES:
        local = docs_dir / name
        if not local.is_file():
            drift.append(f"{name}: missing locally but pinned in the lock")
            continue
        expected = lock.get(name)
        if expected is None:
            drift.append(f"{name}: not pinned in the lock — regenerate it in kreniq-brand")
            continue
        actual = hashlib.sha256(local.read_bytes()).hexdigest()
        if actual != expected:
            drift.append(f"{name}: drifted from the brand shell "
                         f"(local {actual[:12]} != locked {expected[:12]}) — "
                         "edit kreniq-brand and re-sync, do not edit the copy")
    return drift
```

- [ ] **Step 4: Ejecutar los tests y confirmar que pasan**

```bash
python3 -m pytest benchmarks/test_shell_lock.py -q --no-header
```

Esperado: `4 passed`.

- [ ] **Step 5: Escribir `scripts/sync_shell.py`**

```python
#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Sincroniza el shell de marca hacia este consumidor.

La fuente es el repo kreniq-brand. Este script copia el shell y su lock; nunca al
revés. Si editaste la copia local en vez de la fuente, esto la sobrescribe — que es
justo lo que debe pasar.

Uso:  python3 scripts/sync_shell.py [ruta-a-kreniq-brand]
Por defecto busca ../kreniq-brand, o el valor de $KRENIQ_BRAND.
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
FILES = ("kreniq-shell.css", "lang.js", "krenniq-logo.png", "logo_kreniq_volum_trico.html")


def main() -> int:
    if len(sys.argv) > 1:
        brand = Path(sys.argv[1])
    else:
        brand = Path(os.environ.get("KRENIQ_BRAND", ROOT.parent / "kreniq-brand"))
    brand = brand.expanduser().resolve()

    if not brand.is_dir():
        print(f"FAIL: brand repo not found at {brand}")
        print("      pass its path, or set KRENIQ_BRAND")
        return 1
    lock = brand / "shell.lock.json"
    if not lock.is_file():
        print(f"FAIL: {lock} missing — regenerate the lock in the brand repo")
        return 1

    for name in FILES:
        src = brand / name
        if not src.is_file():
            print(f"FAIL: {src} missing in the brand repo")
            return 1
        shutil.copy2(src, DOCS / name)
    shutil.copy2(lock, DOCS / "shell.lock.json")

    print(f"OK: synced {len(FILES)} shell files + shell.lock.json from {brand}")
    print("    run `python3 designlab/layout_lint.py` to confirm no drift remains.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 6: Sincronizar y verificar que no hay deriva**

```bash
python3 scripts/sync_shell.py
python3 -c "
import sys, pathlib
sys.path.insert(0, 'designlab')
from layout_lint import shell_lock_drift
d = shell_lock_drift(pathlib.Path('docs'), pathlib.Path('docs/shell.lock.json'))
print('drift:', d or 'ninguna')
"
```

Esperado: `OK: synced 4 shell files ...` y `drift: ninguna`.

- [ ] **Step 7: Conectar la comprobación a `main()` de `layout_lint.py`**

`fail` en `main()` es un **contador de páginas** (`fail = 0`, `fail += 1`), y la línea de
resumen imprime `len(files) - fail`. No sumes la deriva a ese contador o el resumen mentirá:
llévala aparte y súmala solo al código de salida.

Sustituir las dos últimas líneas de `main()` (línea 82-83):

```python
    print("\n%s — %d/%d páginas OK" % ("FALLO" if fail else "TODO OK", len(files) - fail, len(files)))
    sys.exit(1 if fail else 0)
```

por:

```python
    print("\n%s — %d/%d páginas OK" % ("FALLO" if fail else "TODO OK", len(files) - fail, len(files)))

    drift = shell_lock_drift(ROOT / "docs", ROOT / "docs" / "shell.lock.json")
    if drift:
        print("\n✗ deriva del shell de marca (fuente única: repo kreniq-brand):")
        for d in drift:
            print("    - %s" % d)

    sys.exit(1 if (fail or drift) else 0)
```

- [ ] **Step 8: Ejecutar el lint completo y la suite**

```bash
python3 -m pytest benchmarks/ -q --no-header -p no:cacheprovider
```

Esperado: `319 passed` (310 previos + 5 de captura + 4 de lock).

El lint sigue el criterio de no-regresión (ver Task 3, Step 5): la baseline tiene 9 páginas
fallando por causas estructurales previas a este plan. Lo que esta tarea SÍ debe conseguir es
que no aparezca ninguna línea `SHELL-DRIFT`:

```bash
python3 designlab/layout_lint.py 2>&1 | grep "^✗" | sed 's/^✗ //' | sort \
  > /tmp/lint-now.txt
diff .superpowers/sdd/2026-09-04-kreniq-repo-decoupling/lint-baseline.txt /tmp/lint-now.txt \
  && echo "LINT OK — sin regresión contra la baseline"
```

```bash
python3 designlab/layout_lint.py 2>&1 | grep -c "SHELL-DRIFT" | xargs echo "líneas de deriva:"
```

Esperado: `LINT OK — sin regresión contra la baseline` y `líneas de deriva: 0`.

- [ ] **Step 9: Commitear**

```bash
git add scripts/sync_shell.py docs/shell.lock.json docs/kreniq-shell.css docs/lang.js \
        designlab/layout_lint.py benchmarks/test_shell_lock.py
git commit -m "Pin the brand shell: drift fails the build instead of passing quietly

kreniq-shell.css and lang.js are the brand's, shared by CAPAS, Atlas and the
landing. CAPAS now consumes them under a sha256 lock published by kreniq-brand:
editing the local copy instead of the source is caught by layout_lint rather
than diverging the three sites in silence. sync_shell.py pulls from the brand,
never the other way."
```

---

## Verificación final del plan

Al terminar las 7 tareas, todo lo siguiente debe ser cierto:

```bash
python3 -m pytest benchmarks/ -q --no-header -p no:cacheprovider   # 319 passed
python3 benchmarks/conformance.py | tail -3                        # CAPAS-CONFORMANT
python3 benchmarks/verify_capas_surface_isolation.py               # OK
python3 ops/verify_capture.py                                      # OK
python3 designlab/layout_lint.py 2>&1 | grep "^✗" | sed 's/^✗ //' | sort | \
  diff .superpowers/sdd/2026-09-04-kreniq-repo-decoupling/lint-baseline.txt -   # sin regresión
git status -sb | head -1                                           # sin 'ahead'
ls docs/atlas-*.html docs/evidence.html 2>/dev/null || echo "forks borrados"
```

## Lo que este plan NO hace

- No borra `docs/krenniq.html` ni `docs/legal.html` de CAPAS (Plan 2, pieza 3b)
- No toca el bloque de routing por `Host` de `capas_api.py` (Plan 2, pieza 3b)
- No crea ni modifica nada en Azure (Planes 2 y 3)
- No toca DNS
- No hace merge a `main`
