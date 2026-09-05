#!/usr/bin/env python3
"""Valida el detector determinista contra el ground truth humano de COMPare.

COMPare evaluó a mano 68 ensayos de 5 revistas top. Para cada uno registró
cuántos outcomes primarios preespecificados había y cuántos se reportaron
correctamente. Esa es la etiqueta; nosotros no la tocamos.
"""
import csv, json, re, subprocess, sys, time

sys.path.insert(0, "/private/tmp/claude-501/-Users-kreniq-Desktop-KRENIQ-AI-Projects-01--Investigacion-CAPAS-INTELIGENTES/e4b49b25-3ce8-4c75-9a5b-05446b2e11c5/scratchpad")
from phase0 import classify

CSV = "/private/tmp/claude-501/-Users-kreniq-Desktop-KRENIQ-AI-Projects-01--Investigacion-CAPAS-INTELIGENTES/e4b49b25-3ce8-4c75-9a5b-05446b2e11c5/scratchpad/compare_gt.csv"

def num(x):
    x = (x or "").strip()
    return int(x) if re.fullmatch(r"\d+", x) else None

rows = list(csv.reader(open(CSV, encoding="utf-8", errors="replace")))[1:]
gold = []
for r in rows:
    m = re.search(r"(NCT\d{8})", " ".join(r))
    if not m: continue
    tot, ok = num(r[17] if len(r) > 17 else ""), num(r[19] if len(r) > 19 else "")
    if tot is None or ok is None: continue
    gold.append({"nct": m.group(1), "journal": r[2], "total_primary": tot,
                 "correct_primary": ok, "label_problem": ok < tot})

print(f"ground truth utilizable: {len(gold)} ensayos con etiqueta humana", flush=True)
print(f"  con problema en primarios (etiqueta): {sum(g['label_problem'] for g in gold)}", flush=True)

out = []
for i, g in enumerate(gold, 1):
    c = classify(g["nct"])
    out.append({**g, **{k: v for k, v in c.items() if k != "nct"}})
    if i % 10 == 0: print(f"  {i}/{len(gold)}", flush=True)
    time.sleep(0.25)

json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else "validate.json", "w"), indent=1)

dec = [r for r in out if r["bucket"] == "DECIDIBLE_ESTRUCTURADO"]
print(f"\n  decidible: {len(dec)}/{len(out)}")
tp = sum(1 for r in dec if r["switched"] and r["label_problem"])
fp = sum(1 for r in dec if r["switched"] and not r["label_problem"])
fn = sum(1 for r in dec if not r["switched"] and r["label_problem"])
tn = sum(1 for r in dec if not r["switched"] and not r["label_problem"])
print(f"  TP={tp} FP={fp} FN={fn} TN={tn}")
if tp + fn: print(f"  sensibilidad: {tp/(tp+fn):.2f}")
if tp + fp: print(f"  VPP:          {tp/(tp+fp):.2f}")
