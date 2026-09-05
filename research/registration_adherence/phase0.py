#!/usr/bin/env python3
"""Fase 0 — ¿qué fracción del switching de outcomes es decidible sin LLM?

Dos llamadas por ensayo, ambas a endpoints estructurados:
  /api/v2/studies/{nct}        -> fecha de inicio + outcomes actuales
  /api/int/studies/{nct}/history -> outcomes originales + versiones que los cambiaron

Nada de scrapear, nada de LLM. Si un ensayo no se puede clasificar, cuenta como
NO decidible: fail-closed, igual que el motor.
"""
import json, subprocess, sys, time

def get(url, tries=3):
    """urllib recibe 403 de clinicaltrials.gov; curl pasa. Usamos curl."""
    for i in range(tries):
        r = subprocess.run(["curl", "-sg", "--max-time", "45", url],
                           capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            try:
                return json.loads(r.stdout)
            except json.JSONDecodeError:
                pass
        if i == tries - 1: return None
        time.sleep(1.5 * (i + 1))
    return None

def sample(n):
    """Ensayos intervencionales, completados, CON resultados publicados."""
    ncts, token = [], None
    while len(ncts) < n:
        u = ("https://clinicaltrials.gov/api/v2/studies?"
             "filter.overallStatus=COMPLETED&query.term=AREA[StudyType]INTERVENTIONAL"
             "&aggFilters=results:with&pageSize=100&fields=NCTId")
        if token: u += f"&pageToken={token}"
        d = get(u)
        if not d: break
        for s in d.get("studies", []):
            ncts.append(s["protocolSection"]["identificationModule"]["nctId"])
        token = d.get("nextPageToken")
        if not token: break
    return ncts[:n]

def _titles(outcomes):
    """Conjunto normalizado de titulos de outcome. None si no es interpretable."""
    if not isinstance(outcomes, list):
        return None
    out = set()
    for o in outcomes:
        if not isinstance(o, dict):
            return None
        t = o.get("measure") or o.get("title")
        if not t:
            return None
        out.add(" ".join(str(t).lower().split()))
    return out


def classify(nct):
    cur = get(f"https://clinicaltrials.gov/api/v2/studies/{nct}")
    hist = get(f"https://clinicaltrials.gov/api/int/studies/{nct}/history")
    if not cur or not hist:
        return {"nct": nct, "bucket": "NO_DECIDIBLE", "reason": "sin datos"}

    ps = cur.get("protocolSection", {})
    start = (ps.get("statusModule", {}).get("startDateStruct") or {}).get("date")
    cur_primary = _titles((ps.get("outcomesModule") or {}).get("primaryOutcomes"))
    orig_primary = _titles(hist.get("originalData", {}).get("primaryOutcomes"))
    changes = hist.get("changes", [])

    if orig_primary is None or cur_primary is None:
        return {"nct": nct, "bucket": "NO_DECIDIBLE",
                "reason": "outcomes primarios no estructurados"}
    if not changes:
        return {"nct": nct, "bucket": "NO_DECIDIBLE", "reason": "sin historial"}

    # Comparacion de CONTENIDO, no de "se toco el modulo".
    added   = sorted(cur_primary - orig_primary)
    removed = sorted(orig_primary - cur_primary)

    # Solo cuentan ediciones del PROTOCOLO tras el inicio; publicar resultados
    # toca "Outcome Measures (Results)", que es otra cosa y no es switching.
    edits_after_start = [
        (c["version"], c["date"]) for c in changes
        if c["version"] != 0
        and "Outcome Measures" in (c.get("moduleLabels") or [])
        and start and c["date"] >= start
    ]

    return {
        "nct": nct, "bucket": "DECIDIBLE_ESTRUCTURADO", "start": start,
        "versions": len(changes),
        "n_orig_primary": len(orig_primary), "n_cur_primary": len(cur_primary),
        "added_primary": added, "removed_primary": removed,
        "content_changed": bool(added or removed),
        "protocol_outcome_edits_after_start": len(edits_after_start),
        # switching = el CONTENIDO del outcome primario cambio, y hubo una
        # edicion de protocolo despues de que el estudio arrancara.
        "switched": bool((added or removed) and edits_after_start),
    }


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    ncts = sample(n)
    print(f"muestra: {len(ncts)} ensayos completados con resultados", flush=True)
    out = []
    for i, nct in enumerate(ncts, 1):
        out.append(classify(nct))
        if i % 25 == 0: print(f"  {i}/{len(ncts)}", flush=True)
        time.sleep(0.25)
    json.dump(out, open(sys.argv[2] if len(sys.argv) > 2 else "phase0_results.json", "w"), indent=1)
    dec = [r for r in out if r["bucket"] == "DECIDIBLE_ESTRUCTURADO"]
    sw = [r for r in dec if r.get("switched")]
    ch = [r for r in dec if r.get("content_changed")]
    ed = [r for r in dec if r.get("protocol_outcome_edits_after_start")]
    n = max(len(dec), 1)
    print(f"\n  decidible sin LLM:                       {len(dec)}/{len(out)} = {100*len(dec)/max(len(out),1):.1f}%")
    print(f"  contenido del primario cambio:           {len(ch)}/{len(dec)} = {100*len(ch)/n:.1f}%")
    print(f"  edicion de protocolo tras inicio:        {len(ed)}/{len(dec)} = {100*len(ed)/n:.1f}%")
    print(f"  SWITCHING (ambas):                       {len(sw)}/{len(dec)} = {100*len(sw)/n:.1f}%")
