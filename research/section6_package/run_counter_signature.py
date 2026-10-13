#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Contra-firma §6 con un modelo de OTRA familia, que DIRIGE la verificación.

El modelo remoto no puede ejecutar; este script es sus manos: le entrega INSTRUCCION.md + claims.json
+ un mapa del repo, y en cada turno ejecuta los comandos que pida (bloques ```run), con lista blanca,
y le devuelve la salida CRUDA. El constructor (Claude) no interviene en el juicio: no edita salidas,
no resume, no responde preguntas. Transcripción completa (comandos + salidas + veredictos) a
section6_<proveedor>_<fecha>.md.

Uso: python3 research/section6_package/run_counter_signature.py deepseek|groq [--model M] [--rounds N]
Llaves: ~/.config/estandar/<proveedor>.key (mismo mecanismo que integropoly). Nunca se imprimen.
"""
import argparse, datetime, json, os, re, subprocess, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKG = Path(__file__).resolve().parent
PROVIDERS = {
    "deepseek": {"url": "https://api.deepseek.com/chat/completions", "key": "deepseek.key", "model": "deepseek-reasoner"},
    "groq": {"url": "https://api.groq.com/openai/v1/chat/completions", "key": "groq.key", "model": "openai/gpt-oss-120b"},
    "xai": {"url": "https://api.x.ai/v1/chat/completions", "key": "xai.key", "model": "grok-4.7"},
    "gemini": {"url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions", "key": "gemini.key", "model": "gemini-3.8-flash"},
}
ALLOW = re.compile(r"^(python3?|pytest|cat|head|tail|sed|grep|rg|ls|wc|shasum|sha256sum|jq|git|find|diff|sort|uniq|cut|tr|awk|echo|printf|stat|file)\b")
DENY = re.compile(r"(\brm\b|\bmv\b|\bcp\b|\bsudo\b|\bcurl\b|\bwget\b|\bssh\b|\baz\b|\bpip\b|\bnpm\b|>\s*[^&]|\btee\b|\bchmod\b|\bchown\b|\bkill\b|git\s+(commit|push|reset|checkout|switch|restore|rebase|merge|tag\s+-d|branch\s+-[dD]|clean|stash|rm|mv)|\bopen\b|\bosascript\b|\bexec\b|\beval\b|\bsource\b|\bexport\b|\$\(|`)")
MAX_OUT = 12000


def key_for(prov):
    return (Path.home() / ".config/estandar" / PROVIDERS[prov]["key"]).read_text().strip()


TOOLS = [{"type": "function", "function": {"name": "run",
          "description": "Ejecuta un comando shell de SOLO LECTURA/ejecucion en la raiz del repo CAPAS INTELIGENTES (python3, pytest, cat, grep, git log/show/diff, ls, head, sed -n...). Sin red, sin escritura. Devuelve la salida cruda.",
          "parameters": {"type": "object", "properties": {"cmd": {"type": "string", "description": "comando shell"}}, "required": ["cmd"]}}}]


def chat(prov, model, messages):
    body = {"model": model, "messages": messages, "temperature": 0.2, "max_tokens": 8000, "tools": TOOLS, "tool_choice": "auto"}
    req = urllib.request.Request(PROVIDERS[prov]["url"], data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "Authorization": f"Bearer {key_for(prov)}",
                                          "User-Agent": "capas-section6/1.0"})  # Cloudflare 1010 bloquea Python-urllib
    try:
        with urllib.request.urlopen(req, timeout=900) as r:
            d = json.load(r)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"{prov} HTTP {e.code}: {e.read()[:300]!r}")
    m = d["choices"][0]["message"]
    return m, d.get("usage", {}), d.get("model", model)


def _segments(line):
    """Split a shell line on | ; && || that are OUTSIDE quotes (so `python3 -c "a; b"` is one segment)."""
    segs, cur, q = [], "", None
    i = 0
    while i < len(line):
        ch = line[i]
        if q:
            cur += ch
            if ch == q: q = None
        elif ch in ("'", '"'):
            q = ch; cur += ch
        elif ch in "|;&":
            if cur.strip(): segs.append(cur.strip())
            cur = ""
        else:
            cur += ch
        i += 1
    if cur.strip(): segs.append(cur.strip())
    return segs


PY_WRITE = re.compile(r"(open\([^)]*['\"][wax]|write_text|write_bytes|os\.(remove|unlink|rename|system|makedirs|mkdir|symlink|link|chmod|chdir|popen|exec\w*|spawn\w*)|"
                      r"shutil\.|subprocess|\bsocket\b|urllib|requests|\bimportlib\b|__import__|\bctypes\b|\bsignal\b|"
                      r"pathlib[^\n]*\.(unlink|rmdir|touch|symlink_to|hardlink_to|write_\w+|mkdir))")


def run_cmd(cmd):
    for line in cmd.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        for seg in _segments(line):
            if not ALLOW.match(seg):
                return f"[DENEGADO: segmento no permitido: {seg[:80]!r}]"
            if seg.startswith(("python", "pytest")) and PY_WRITE.search(seg):
                return f"[DENEGADO: escritura/red desde python: {seg[:80]!r}]"
        if DENY.search(line):
            return f"[DENEGADO: patrón prohibido en: {line[:80]!r}]"
    try:
        r = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True, timeout=600,
                           env={"PATH": os.environ["PATH"], "HOME": os.environ["HOME"], "LANG": "C.UTF-8", "PYTHONDONTWRITEBYTECODE": "1"})
        out = (r.stdout + ("\n[stderr]\n" + r.stderr if r.stderr.strip() else "")).strip()
    except subprocess.TimeoutExpired:
        out = "[TIMEOUT 600s]"
    dirty = "\n".join(l for l in subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout.splitlines()
                      if " outputs/" not in l and ".coverage" not in l)  # artefactos generados por los propios verificadores
    if dirty != run_cmd.baseline:
        out += "\n[ALERTA: el comando modificó el árbol de trabajo]\n" + dirty
    if len(out) > MAX_OUT:
        out = out[:MAX_OUT // 2] + f"\n…[{len(out) - MAX_OUT} chars omitidos]…\n" + out[-MAX_OUT // 2:]
    return out or "[sin salida]"


def repo_map():
    g = lambda *a: subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    return (f"HEAD: {g('rev-parse', 'HEAD')}\nrama: {g('rev-parse', '--abbrev-ref', 'HEAD')}\n"
            f"tags: {g('tag', '-l', 'ginibre-ciego-*')}\n"
            f"raíz: {', '.join(sorted(p.name for p in ROOT.iterdir() if not p.name.startswith('.')))}\n"
            f"benchmarks/: {', '.join(sorted(p.name for p in (ROOT / 'benchmarks').iterdir()))}\n"
            f"research/: {', '.join(sorted(p.name for p in (ROOT / 'research').iterdir()))}\n"
            "Repo de Ginibre (solo lectura): /Users/kreniq/Desktop/KRENIQ/AI Projects/01. Investigacion/Paper - Inverse Ginibre Overlap/\n"
            "Rutas citadas en claims.json que NO existen con ese nombre: verify_cara_decoupling.py, verify_audit_hash_reproduces.py, "
            "INFORME_CORPUS.md (está en el repo de Ginibre), audit_results.json, phase0_n500.json (buscar bajo research/).")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("provider", choices=PROVIDERS)
    ap.add_argument("--model")
    ap.add_argument("--rounds", type=int, default=14)
    ap.add_argument("--focus", default="", help="instrucción adicional (p.ej. qué claims priorizar)")
    ap.add_argument("--suffix", default="", help="sufijo del archivo de salida")
    a = ap.parse_args()
    model = a.model or PROVIDERS[a.provider]["model"]
    date = datetime.date.today().isoformat()
    out = PKG / f"section6_{a.provider}_{date}{a.suffix}.md"
    instr = (PKG / "INSTRUCCION.md").read_text()
    claims = (PKG / "claims.json").read_text()
    system = (instr + "\n\n## Protocolo de ejecución\nNo puedes ejecutar directamente. Pide comandos en bloques\n"
              "```run\n<comando shell>\n```\n(uno o varios por turno; cwd = raíz del repo CAPAS INTELIGENTES; solo lectura y "
              "ejecución: python3/pytest/cat/grep/git log|show|diff…; sin red, sin escritura). Recibirás la salida CRUDA, sin "
              "edición. Nadie responderá preguntas: solo salidas de comandos. Cuando termines, escribe tu informe final "
              "empezando con la línea `## VEREDICTOS` y sin bloques run. Usa como máximo ~" + str(a.rounds) + " turnos."
              + (f"\n\n## Foco de esta corrida\n{a.focus}" if a.focus else ""))
    run_cmd.baseline = "\n".join(l for l in subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout.splitlines()
                                 if " outputs/" not in l and ".coverage" not in l)
    messages = [{"role": "system", "content": system},
                {"role": "user", "content": f"## claims.json\n```json\n{claims}\n```\n\n## Mapa del repo\n{repo_map()}\n\nEmpieza."}]
    log = [f"# Contra-firma §6 — {a.provider} / {model} — {date}\n", f"HEAD: {repo_map().splitlines()[0]}\n",
           "Transcripción literal: cada comando pedido por el modelo y su salida cruda. El constructor no editó nada.\n"]
    usage_tot = {}
    executed_cmds = []
    for rnd in range(1, a.rounds + 2):
        m, usage, served = chat(a.provider, model, messages)
        content = m.get("content") or ""
        reasoning = m.get("reasoning") or ""
        for k, v in usage.items():
            if isinstance(v, (int, float)): usage_tot[k] = usage_tot.get(k, 0) + v
        tool_calls = m.get("tool_calls") or []
        messages.append({"role": "assistant", "content": content, **({"tool_calls": tool_calls} if tool_calls else {})})
        log.append(f"\n## Turno {rnd} — modelo ({served})\n\n{content}\n" + (f"\n<details><summary>razonamiento</summary>\n\n{reasoning}\n</details>\n" if reasoning else ""))
        print(f"[turno {rnd}] {len(content)} chars, {len(tool_calls)} tool calls", file=sys.stderr)
        blocks = re.findall(r"```run\s*\n(.*?)```", content, re.S)
        if "## VEREDICTOS" in content:
            break
        if not blocks and not tool_calls:
            if rnd >= a.rounds:
                break
            messages.append({"role": "user", "content": "[Sin comandos ni informe. Usa la herramienta `run` para verificar, o emite el informe final con `## VEREDICTOS`.]"})
            continue
        for tc in tool_calls:
            try:
                cmd = json.loads(tc["function"]["arguments"]).get("cmd", "")
            except Exception:
                cmd = tc["function"].get("arguments", "")
            o = run_cmd(cmd); executed_cmds.append(cmd)
            log.append(f"\n### ejecutado (tool)\n```\n$ {cmd.strip()}\n{o}\n```\n")
            messages.append({"role": "tool", "tool_call_id": tc["id"], "content": f"$ {cmd.strip()}\n{o}"})
        reply = []
        for b in blocks:
            o = run_cmd(b); executed_cmds.append(b)
            reply.append(f"$ {b.strip()}\n{o}")
            log.append(f"\n### ejecutado\n```\n$ {b.strip()}\n{o}\n```\n")
        if rnd >= a.rounds:
            reply.append("[Último turno disponible: emite ahora el informe final con `## VEREDICTOS`.]")
        if reply:
            messages.append({"role": "user", "content": "\n\n".join(reply)})
    # --- Gate sobre el informe (run 4 del 13-oct: el auditor cito `ls` que nunca ejecuto). Cada comando que el
    # informe final presenta como ejecutado debe aparecer entre los realmente ejecutados; si no, se marca.
    executed = {c.strip() for c in executed_cmds}
    final = messages[-1]["content"] if messages and messages[-1]["role"] == "assistant" else ""
    report = final.split("## VEREDICTOS", 1)[1] if "## VEREDICTOS" in final else final
    quoted = []
    for blk in re.findall(r"```[a-z]*\s*\n(.*?)```", report, re.S):
        for ln in blk.splitlines():
            ln = ln.strip()
            if ln.startswith("$ "):
                quoted.append(ln[2:].strip())
            elif ln and not ln.startswith(("→", "->", "#", "[")) and re.match(r"^(python3?|pytest|cat|head|tail|sed|grep|rg|ls|wc|shasum|jq|git|find|diff|sort|uniq|cut|tr|awk)\b", ln):
                quoted.append(ln)
    def _norm(c): return re.sub(r"\s+", " ", c).strip()
    ex_norm = {_norm(c) for c in executed}
    unexecuted = [q for q in quoted if _norm(q) not in ex_norm and not any(_norm(q) in e or e in _norm(q) for e in ex_norm)]
    gate = (f"\n## GATE sobre el informe\ncomandos citados en VEREDICTOS: {len(quoted)}; ejecutados de verdad: {len(quoted) - len(unexecuted)}; "
            f"**NO EJECUTADOS: {len(unexecuted)}**\n" + "".join(f"- `{q[:160]}`\n" for q in unexecuted) +
            ("\nTodo veredicto apoyado en un comando NO EJECUTADO carece de valor; verificar contra los bloques `### ejecutado`.\n" if unexecuted else "\nTodos los comandos citados fueron ejecutados.\n"))
    log.append(gate)
    print(gate, file=sys.stderr)
    log.append(f"\n---\nuso de tokens: {json.dumps(usage_tot)}\n")
    out.write_text("\n".join(log))
    print(out)


if __name__ == "__main__":
    main()
