#!/usr/bin/env python3
"""Pasa papers retractados por fabricacion y controles no retractados por capas_invariants.
Salida: por paper, items extraidos, items FLAG, leyes que dispararon. Luego tasas fab vs ctl."""
import glob, json, sys, collections
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
sys.path.insert(0, ".")
import capas_invariants as ci
from extract import text_of, items, table_items

def to_evidence(it):
    if it["kind"] == "pct":
        return {"reported_percent": {"k": it["k"], "N": it["N"], "pct": it["pct"], "decimals": it["decimals"]}}
    if it["kind"] == "pval":
        return {"pvalue_test": {"stat": it["stat"], "df1": it["df1"], "df2": it["df2"],
                                "value": it["value"], "op": it["op"], "p": it["p"],
                                "decimals": it["decimals"], "value_decimals": it["value_decimals"]}}
    if it["kind"] == "grim":
        return {"grim": {"mean": it["mean"], "n": it["n"], "decimals": it["decimals"]}}
    return None

def run(folder, label):
    rows = []
    for f in sorted(glob.glob(f"{folder}/*.xml")):
        its = items(text_of(f)) + table_items(f); flags = []; checked = 0
        for it in its:
            ev = to_evidence(it)
            if not ev: continue
            a = ci.audit(ev)
            if a["applicable"]:
                checked += 1
                if a["verdict"] == "FLAG":
                    flags.append({"kind": it["kind"], "src": it.get("src","prose"), "why": a["summary"][:140]})
        rows.append({"group": label, "file": f.split("/")[-1], "items": len(its),
                     "checked": checked, "flags": len(flags), "detail": flags})
    return rows

if __name__ == "__main__":
    rows = run("xml", "FAB") + run("xml_ctl", "CTL")
    json.dump(rows, open("audit_results.json", "w"), indent=1)
    for g in ("FAB", "CTL"):
        R = [r for r in rows if r["group"] == g]
        withitems = [r for r in R if r["checked"] > 0]
        flagged = [r for r in withitems if r["flags"] > 0]
        tot_items = sum(r["checked"] for r in R); tot_flags = sum(r["flags"] for r in R)
        print(f"\n{g}: {len(R)} papers | con items chequeables: {len(withitems)} | "
              f"papers con >=1 FLAG: {len(flagged)} ({100*len(flagged)/max(len(withitems),1):.0f}% de los chequeables)")
        print(f"     items chequeados {tot_items}, FLAGs {tot_flags} ({100*tot_flags/max(tot_items,1):.1f}% de items)")
        kinds = collections.Counter(d["kind"] for r in R for d in r["detail"])
        print(f"     flags por ley: {dict(kinds)}")
