#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Author-side: writes the PUBLIC, redacted copy of the sealed blind corpus (owner decision 2026-10-14: publish the
verdict files and the outcome labels, claim text as hash only) to research/ginibre_corpus/public/.

What is published, per set (X1-3 v1, X1-3 v2, X4, X5):
  claims_<set>.jsonl    claim_id, contaminado, claim type, sha256 of the claim text, and the evidence fields the engine
                        read. Free-text evidence values (anything that is not a short enum token) are replaced by
                        "sha256:<hex>" of the exact string; numbers, booleans and enum tokens are kept.
  verdicts_<set>.jsonl  the sealed header (unchanged) and per claim: verdict, ceiling, reason (redacted strings
                        replaced by their hash), sha256 of licensed_claim.
  outcomes_<set>.jsonl  claim_id, outcome label (bueno/malo), outcome_type. The outcome note is withheld.
  MANIFEST.json         sha256 of every original sealed file and of every public file.
The claim texts and outcome notes quote results of an unpublished paper; their hashes let anyone check them the
day the paper is public. Run: python3 research/ginibre_corpus/publish_redacted.py"""
import hashlib, json, os, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
G = Path(os.environ.get("CAPAS_GINIBRE_CORPUS") or
         "/Users/kreniq/Desktop/KRENIQ/AI Projects/01. Investigacion/Paper - Inverse Ginibre Overlap/CAPAS_CORPUS_2026-10-12")
OUT = ROOT / "research" / "ginibre_corpus" / "public"
SETS = [("X1-3_v1", "PARA_CAPAS_claims.jsonl", "PARA_CAPAS_desenlaces.jsonl", "DE_CAPAS_veredictos.jsonl"),
        ("X1-3_v2", "PARA_CAPAS_claims.jsonl", "PARA_CAPAS_desenlaces.jsonl", "DE_CAPAS_veredictos_v2.jsonl"),
        ("X4", "PARA_CAPAS_claims_X4.jsonl", "PARA_CAPAS_desenlaces_X4.jsonl", "DE_CAPAS_veredictos_X4.jsonl"),
        ("X5", "PARA_CAPAS_claims_X5.jsonl", "PARA_CAPAS_desenlaces_X5.jsonl", "DE_CAPAS_veredictos_X5.jsonl")]
TOKEN = re.compile(r"^[A-Za-z_]{1,24}$")  # enum tokens (bounded, MEDIDO, se, z, max) are kept verbatim
H = lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest()
L = lambda p: [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def redact(o, seen):
    if isinstance(o, dict):
        return {k: redact(v, seen) for k, v in o.items()}
    if isinstance(o, list):
        return [redact(v, seen) for v in o]
    if isinstance(o, str) and not TOKEN.match(o):
        seen.add(o); return "sha256:" + H(o)
    return o


def scrub(reason, seen):
    for s in sorted(seen, key=len, reverse=True):
        reason = reason.replace(s, "sha256:" + H(s)[:16])
    return reason


def dump(path, rows):
    path.write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows), encoding="utf-8")


def main() -> int:
    if not G.exists():
        print(f"SKIP: corpus dir not present ({G})"); return 2
    OUT.mkdir(parents=True, exist_ok=True)
    man = {"published": "2026-10-14", "decision": "owner, 2026-10-14: verdicts and outcome labels public, claim text as hash only",
           "hash": "sha256 of the exact UTF-8 string", "originals": {}, "public": {}, "sets": {}}
    for name, cf, of, vf in SETS:
        for f in (cf, of, vf):
            man["originals"][f] = hashlib.sha256((G / f).read_bytes()).hexdigest()
        claims, seen = [], set()
        for r in L(G / cf):
            c = r["payload"]["claim"]; seen.add(c["text"])
            claims.append({"claim_id": r["claim_id"], "contaminado": r["contaminado"], "schema_version": r["payload"]["schema_version"],
                           "claim": {"id": c["id"], "type": c["type"], "text_sha256": H(c["text"])},
                           "evidence": redact(r["payload"]["evidence"], seen)})
        rows = L(G / vf); hdr = rows[0]; verdicts = [hdr]
        for v in rows[1:]:
            lc = v.get("licensed_claim")
            verdicts.append({"claim_id": v["claim_id"], "contaminado": v["contaminado"], "claim_type": v["claim_type"],
                             "verdict": v["verdict"], "ceiling_s2": v.get("ceiling_s2"), "reason": scrub(v.get("reason") or "", seen),
                             "licensed_claim_sha256": H(lc) if isinstance(lc, str) else None})
        outcomes = [{"claim_id": o["claim_id"], "outcome": o["outcome"], "outcome_type": o.get("outcome_type")} for o in L(G / of)]
        for kind, rows_ in (("claims", claims), ("verdicts", verdicts), ("outcomes", outcomes)):
            p = OUT / f"{kind}_{name}.jsonl"; dump(p, rows_)
            man["public"][p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
        man["sets"][name] = {"claims_file": cf, "outcomes_file": of, "verdicts_file": vf, "engine_tag": hdr.get("engine_tag"),
                             "engine_commit": hdr.get("engine_commit"), "n": len(claims), "redacted_strings": len(seen)}
        print(f"{name}: {len(claims)} claims, {len(seen)} strings hashed, tag {hdr.get('engine_tag')}")
    (OUT / "MANIFEST.json").write_text(json.dumps(man, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
