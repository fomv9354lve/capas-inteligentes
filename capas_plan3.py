#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""CAPAS — PLAN_v3 rules (council ratified 8/8, 2026-10-14; owner: "implementa las 9").

Downgrade-only stages that run inside decide_external_claim() after the claim-type rule and the invariant filter.
None of them can raise a verdict. Each rule is declared here AS DATA (id, from-verdicts, to-verdict, reason pattern)
and docs/rule_table.json carries the same entries, so an engine-independent checker can replay them.

  A3a  provenance      payload.meta.sources [{path, sha256}] re-hashed under CAPAS_SOURCE_ROOT (the ingestion
                       adapter's format). Missing root, missing file or hash mismatch -> HOLD.
  A6   ai_use_declared {tool, purpose, phase} (CNPq 2.664/2026 shape) or the string "none". Absent -> notice only
                       (required from the X6 freeze; required now would HOLD every existing payload).
  A3   guard band      <field>_u + coverage_factor (declared-only, D-SI/IMEKO): a comparison whose margin is within
                       k*u is HOLD "not decidable". No *_u declared -> notice "uncertainty: not declared".
  A5   retraction      cited_dois requires retraction_snapshot {source, date, sha256} and cited_doi_retracted. Absent
                       or unreadable -> HOLD; a cited DOI in the snapshot -> HOLD. Never a live lookup (metacheck).
  A5   prereg fields   prereg {field: pre-registered value}: a reported field that differs, or a pre-registered field
                       that is not reported -> REWRITE (field-level adherence, not text diff).
"""
from __future__ import annotations

import hashlib
import math
import os
from pathlib import Path
from typing import Any

# Rule entries in the same shape as docs/rule_table.json (see scripts/gen_rule_table.py). `pattern` is a regex over
# one "; "-separated reason segment. `from` = verdicts the rule may act on; `to` = verdict after (None = unchanged).
RULES: list[dict[str, Any]] = [
    {"key": "prov_no_root", "stage": "downgrade", "from": ["ACCEPT", "REWRITE"], "to": "HOLD", "hold_class": "engine_gap",
     "pattern": r"payload\.meta\.sources declares \d+ source file\(s\) but this engine has no CAPAS_SOURCE_ROOT: the files cannot be re-hashed",
     "label": "declared source files cannot be checked on this engine", "giant": "REWIRE RO-Crate / PLAN_v3 A3a"},
    {"key": "prov_mismatch", "stage": "downgrade", "from": ["ACCEPT", "REWRITE"], "to": "HOLD", "hold_class": "field_absent",
     "pattern": r"source file\(s\) do not match their declared sha256 or are absent: .+",
     "label": "a declared source file is absent or its hash differs", "giant": "PLAN_v3 A3a"},
    {"key": "prov_ok", "stage": "annotate", "from": None, "to": None,
     "pattern": r"\d+ source file\(s\) re-hashed under CAPAS_SOURCE_ROOT and match",
     "label": "declared source files match their hashes", "giant": "PLAN_v3 A3a"},
    {"key": "guard_band", "stage": "downgrade", "from": ["ACCEPT", "REWRITE"], "to": "HOLD", "hold_class": "field_absent",
     "pattern": r"\w+ = \S+ lies within the guard band of \w+ = \S+ \(k = \S+, U = \S+\): not decidable at the declared uncertainty",
     "label": "a compared value lies inside its declared guard band", "giant": "D-SI (IMEKO TC6 2025), JCGM 106"},
    {"key": "retraction_missing", "stage": "downgrade", "from": ["ACCEPT", "REWRITE"], "to": "HOLD", "hold_class": "field_absent",
     "pattern": r"cited_dois declared without a readable retraction_snapshot \{source, date, sha256\} and cited_doi_retracted: retraction status cannot be judged",
     "label": "retraction status of the cited works is not declared", "giant": "metacheck (Retraction Watch cross-check)"},
    {"key": "retraction_hit", "stage": "downgrade", "from": ["ACCEPT", "REWRITE"], "to": "HOLD", "hold_class": "field_absent",
     "pattern": r"a cited work is retracted in the declared snapshot \(.+\): its support is withdrawn",
     "label": "a cited work is retracted", "giant": "metacheck (Retraction Watch cross-check)"},
    {"key": "prereg_deviation", "stage": "downgrade", "from": ["ACCEPT"], "to": "REWRITE",
     "pattern": r"deviates from the pre-registration on fields? \[.+\]: the claim is licensed only as a deviation",
     "label": "a reported field differs from, or omits, its pre-registered value", "giant": "COMPare / field-level adherence"},
]
RULE_BY_KEY = {r["key"]: r for r in RULES}
AI_USE_KEYS = ("tool", "purpose", "phase")
_UNCERTAIN_PAIRS = [("abs_error", "tolerance")]


def _num(x: Any) -> float | None:
    return float(x) if isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(float(x)) else None


def validate(payload: dict[str, Any], evidence: dict[str, Any]) -> list[str]:
    """Shape errors for the PLAN_v3 fields (added to the schema errors, so a malformed field is HOLD)."""
    errs: list[str] = []
    meta = payload.get("meta")
    if meta is not None:
        if not isinstance(meta, dict) or set(meta) - {"sources"}:
            errs.append("payload.meta must be an object with only 'sources'")
        else:
            src = meta.get("sources")
            if not isinstance(src, list) or not all(isinstance(s, dict) and isinstance(s.get("path"), str) and isinstance(s.get("sha256"), str)
                                                   for s in src):
                errs.append("payload.meta.sources must be an array of {path, sha256} objects")
    ai = evidence.get("ai_use_declared")
    if ai is not None and ai != "none":
        items = ai if isinstance(ai, list) else [ai]
        if not items or not all(isinstance(i, dict) and all(isinstance(i.get(k), str) and i.get(k).strip() for k in AI_USE_KEYS) for i in items):
            errs.append("evidence.ai_use_declared must be \"none\" or {tool, purpose, phase} (non-empty strings), or a list of them")
    for k, v in evidence.items():
        if k.endswith("_u") and _num(v) is None:
            errs.append(f"evidence.{k} must be a finite number (standard uncertainty)")
        if k.endswith("_u") and _num(v) is not None and float(v) < 0:
            errs.append(f"evidence.{k} must be >= 0")
    if "coverage_factor" in evidence and (_num(evidence["coverage_factor"]) is None or float(evidence["coverage_factor"]) <= 0):
        errs.append("evidence.coverage_factor must be a positive number")
    if "method_standard" in evidence and not isinstance(evidence["method_standard"], str):
        errs.append("evidence.method_standard must be a string")
    if "cited_dois" in evidence and not (isinstance(evidence["cited_dois"], list) and all(isinstance(d, str) for d in evidence["cited_dois"])):
        errs.append("evidence.cited_dois must be an array of strings")
    rs = evidence.get("retraction_snapshot")
    if rs is not None and not (isinstance(rs, dict) and all(isinstance(rs.get(k), str) for k in ("source", "date", "sha256"))):
        errs.append("evidence.retraction_snapshot must be {source, date, sha256} strings (optional path)")
    if "cited_doi_retracted" in evidence and not isinstance(evidence["cited_doi_retracted"], bool):
        errs.append("evidence.cited_doi_retracted must be a boolean")
    if "prereg" in evidence and not isinstance(evidence["prereg"], dict):
        errs.append("evidence.prereg must be an object {field: pre-registered value}")
    return errs


def _root() -> Path | None:
    r = os.environ.get("CAPAS_SOURCE_ROOT")
    return Path(r).resolve() if r else None


def _safe(root: Path, rel: str) -> Path | None:
    p = Path(rel)
    if p.is_absolute() or ".." in p.parts:
        return None
    full = (root / p).resolve()
    return full if str(full).startswith(str(root)) else None


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _norm_doi(d: str) -> str:
    d = d.strip().lower()
    for pre in ("https://doi.org/", "http://doi.org/", "doi:"):
        if d.startswith(pre):
            d = d[len(pre):]
    return d


def _seg(key: str, text: str) -> tuple[str, str]:
    return key, text


def apply(payload: dict[str, Any], evidence: dict[str, Any], verdict: str) -> dict[str, Any]:
    """Return {verdict, segments [(key, text)], notices [str], checks {..}}. Downgrade-only by construction: each
    rule acts only when the current verdict is in its `from` set, and `to` is never stronger."""
    segs: list[tuple[str, str]] = []
    notices: list[str] = []
    checks: dict[str, Any] = {}

    def fire(key: str, text: str) -> None:
        nonlocal verdict
        r = RULE_BY_KEY[key]
        if r["from"] is None or verdict in r["from"]:
            segs.append((key, text))
            if r["to"]:
                verdict = r["to"]

    # A3a provenance inside decide()
    sources = ((payload.get("meta") or {}).get("sources") or []) if isinstance(payload.get("meta"), dict) else []
    if sources:
        root = _root()
        if root is None:
            fire("prov_no_root", f"payload.meta.sources declares {len(sources)} source file(s) but this engine has no "
                                 "CAPAS_SOURCE_ROOT: the files cannot be re-hashed")
            checks["provenance"] = {"declared": len(sources), "verified": 0, "status": "no source root"}
        else:
            bad = []
            for s in sources:
                p = _safe(root, s["path"])
                if p is None or not p.is_file():
                    bad.append(f"{s['path']} (absent)")
                elif _sha(p) != s["sha256"].removeprefix("sha256:"):
                    bad.append(f"{s['path']} (hash differs)")
            checks["provenance"] = {"declared": len(sources), "verified": len(sources) - len(bad), "problems": bad}
            if bad:
                fire("prov_mismatch", "source file(s) do not match their declared sha256 or are absent: " + ", ".join(bad[:5]))
            else:
                fire("prov_ok", f"{len(sources)} source file(s) re-hashed under CAPAS_SOURCE_ROOT and match")
    else:
        checks["provenance"] = {"declared": 0, "verified": 0}

    # A6 AI-use declaration
    ai = evidence.get("ai_use_declared")
    checks["ai_use_declared"] = ai if ai is not None else "not declared"
    if ai is None:
        notices.append("ai_use_declared: not declared (tool, purpose, phase); required from the X6 freeze")

    # A3 guard band (declared-only)
    k = _num(evidence.get("coverage_factor")) or 2.0
    declared_u = [f for f in evidence if f.endswith("_u")]
    checks["uncertainty"] = {f: evidence[f] for f in declared_u} or "not declared"
    for val, lim in _UNCERTAIN_PAIRS:
        x, L = _num(evidence.get(val)), _num(evidence.get(lim))
        if x is None or L is None:
            continue
        ux, uL = _num(evidence.get(val + "_u")) or 0.0, _num(evidence.get(lim + "_u")) or 0.0
        if not ux and not uL:
            continue
        U = k * math.sqrt(ux * ux + uL * uL)
        if abs(x - L) <= U:
            fire("guard_band", f"{val} = {x:g} lies within the guard band of {lim} = {L:g} (k = {k:g}, U = {U:.3g}): "
                               "not decidable at the declared uncertainty")
    if not declared_u and any(_num(evidence.get(v)) is not None for v, _ in _UNCERTAIN_PAIRS):
        notices.append("uncertainty: not declared (no *_u field); the comparison is made at face value")

    # A5 retraction snapshot
    if evidence.get("cited_dois"):
        rs = evidence.get("retraction_snapshot")
        flag = evidence.get("cited_doi_retracted")
        hit = None
        readable = isinstance(rs, dict) and all(isinstance(rs.get(x), str) and rs.get(x) for x in ("source", "date", "sha256"))
        if readable and isinstance(rs.get("path"), str) and _root() is not None:
            p = _safe(_root(), rs["path"])
            if p is None or not p.is_file() or _sha(p) != rs["sha256"].removeprefix("sha256:"):
                readable = False
            else:
                listed = {_norm_doi(line.split(",")[0]) for line in p.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip()}
                hits = sorted(_norm_doi(d) for d in evidence["cited_dois"] if _norm_doi(d) in listed)
                hit = hits or None
                flag = bool(hits)
        checks["retraction"] = {"snapshot": rs if readable else "absent or unreadable", "cited": len(evidence["cited_dois"]),
                                "retracted_flag": flag}
        if not readable or not isinstance(flag, bool):
            fire("retraction_missing", "cited_dois declared without a readable retraction_snapshot {source, date, sha256} "
                                       "and cited_doi_retracted: retraction status cannot be judged")
        elif flag:
            fire("retraction_hit", f"a cited work is retracted in the declared snapshot ({rs['source']}, {rs['date']}"
                                   + (f": {', '.join(hit[:3])}" if hit else "") + "): its support is withdrawn")

    # A5 field-level pre-registration adherence
    pre = evidence.get("prereg")
    if isinstance(pre, dict) and pre:
        diff = sorted(f for f, v in pre.items() if f in evidence and evidence[f] != v)
        omitted = sorted(f for f in pre if f not in evidence)
        checks["prereg_adherence"] = {"fields": len(pre), "deviating": diff, "omitted": omitted}
        if diff or omitted:
            names = diff + [f"{f} (not reported)" for f in omitted]
            fire("prereg_deviation", f"deviates from the pre-registration on field{'s' if len(names) > 1 else ''} "
                                     f"[{', '.join(names)}]: the claim is licensed only as a deviation")
    return {"verdict": verdict, "segments": segs, "notices": notices, "checks": checks}
