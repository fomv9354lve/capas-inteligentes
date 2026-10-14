#!/usr/bin/env python3
"""Re-evalúa el corpus ciego de Ginibre contra el ÁRBOL ACTUAL y lo puntúa con los desenlaces.

POST-HOC: este script conoce los desenlaces. Sirve para medir el efecto de un cambio del motor
sobre el mismo corpus; NO sustituye la cifra ciega (tag ginibre-ciego-v2, 52/81 y 57/63).
Uso: python3 research/ginibre_corpus/rescore.py [etiqueta]
"""
import json, sys, subprocess, tempfile, os, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
G = os.environ.get("CAPAS_GINIBRE_CORPUS") or "/Users/kreniq/Desktop/KRENIQ/AI Projects/01. Investigacion/Paper - Inverse Ginibre Overlap/CAPAS_CORPUS_2026-10-12"  # corpus is private (unpublished paper)
label = sys.argv[1] if len(sys.argv) > 1 else "working-tree"
oc = {json.loads(l)["claim_id"]: json.loads(l) for l in open(f"{G}/PARA_CAPAS_desenlaces.jsonl", encoding="utf-8") if l.strip()}
rows = []
for l in open(f"{G}/PARA_CAPAS_claims.jsonl", encoding="utf-8"):
    if not l.strip(): continue
    rec = json.loads(l); payload = rec["payload"]
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f: json.dump(payload, f); fn = f.name
    r = subprocess.run([sys.executable, "capas.py", "decide", "--input", fn, "--json"], cwd=ROOT, capture_output=True, text=True, timeout=120)
    os.unlink(fn)
    try: d = json.loads(r.stdout); d = d.get("decision", d); v = d.get("verdict")
    except Exception: v = "ERROR"
    rows.append({"id": rec["claim_id"], "contaminado": rec.get("contaminado"), "type": payload["claim"]["type"],
                 "verdict": v, "outcome": oc[rec["claim_id"]]["outcome"], "otype": oc[rec["claim_id"]].get("outcome_type")})
def score(R):
    mal = [r for r in R if r["outcome"] == "malo"]; bue = [r for r in R if r["outcome"] == "bueno"]
    det = sum(1 for r in mal if r["verdict"] != "ACCEPT"); nr = sum(1 for r in bue if r["verdict"] != "REJECT")
    return det, len(mal), nr, len(bue)
U = [r for r in rows if not r["contaminado"]]
d, m, n, b = score(U)
print(f"[{label}] SIN CONTAMINAR: detección {d}/{m} = {d/m:.2f} | buenos no rechazados {n}/{b} = {n/b:.2f}")
d, m, n, b = score(rows)
print(f"[{label}] TODOS:          detección {d}/{m} = {d/m:.2f} | buenos no rechazados {n}/{b} = {n/b:.2f}")
bt = collections.defaultdict(list)
for r in U: bt[r["type"]].append(r)
print("  por tipo (sin contaminar):")
for t, R in sorted(bt.items(), key=lambda x: -len(x[1])):
    d, m, n, b = score(R); print(f"    {t:<30} malos {d}/{m}   buenos {n}/{b}")
json.dump(rows, open(f"{ROOT}/research/ginibre_corpus/rescore_{label}.json", "w"), indent=1)
