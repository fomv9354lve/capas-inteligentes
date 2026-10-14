#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""CAPAS — machine-context ingestion (adapters), so evidence fields come from the artifact a machine produced,
with its hash, and not from a model's or a person's hand.

Decision 2026-10-13 (Osvaldo): "lo mejor que puede hacer el motor es ingerir contexto" — but only context that the
SOURCE produces mechanically. A model may still choose which artifact goes where; it never types a number.

Adapters (each deterministic, invents nothing, records the source sha256):

  backend_properties(props)  Qiskit `BackendProperties` (object, `.to_dict()` or its JSON) -> calibration_snapshot in
                             the shape the invariant law already reads (Atlas schema: t1_us/t2_us/readout/sx/cz tables,
                             edges, field_dates per parameter, declared timezone). A qubit without T1 stays absent.
  prereg(doc)                atlas_prereg/v1 pre-registration -> one claim SKELETON per metric_definition (id, verbatim
                             definition, prereg id/time/sha, supersedes chain). No claim type, no evidence: those are
                             declared by the coder in a mapping that names the prereg metric it serves.
  results(source, spec)      a results file (JSON, or CSV loaded as {rows, n_rows}) + a declarative spec
                             {evidence_field: "dotted.path" | {"const": v} | {"path": ..., "as": "str"}} -> evidence
                             fields COPIED from the file (numbers, booleans, lists of numbers; strings only when the
                             spec says so), with provenance that separates what was read (field -> path) from what was
                             declared (field -> value). The adapter never computes a statistic: that is the analysis
                             script's job, pinned by the pre-registration.
  verify_sources(payload)    every entry in meta.sources {path, sha256} is re-hashed; a mismatch is reported, never
                             silently accepted. The sealed runner refuses to seal a payload whose sources do not match.

CLI:
  python3 capas_ingest.py backend-properties <props.json | fake:FakeKingston> [--layout 1,2,3] [--job-date YYYY-MM-DD] -o snap.json
  python3 capas_ingest.py prereg <prereg.json> -o skeletons.jsonl
  python3 capas_ingest.py verify-sources <claims.jsonl> [--root DIR]
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ADAPTER_VERSION = "1"
VERDICT_WORDS = re.compile(r"\b(CONFIRMADO|FALSADO|CADUCO|RECUPERA|PERSISTE|EMPEORA|INDETERMINADO|SIGUE MEJOR|SIN DIFERENCIA|"
                           r"ACCEPT|REJECT|REWRITE|HOLD)\b")
_TWO_Q = ("cz", "ecr", "cx")   # the invariant law's normalizer knows these table names


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=_json_default)


def _json_default(o: Any) -> Any:
    if isinstance(o, (_dt.datetime, _dt.date)):
        return o.isoformat()
    raise TypeError(f"not serializable: {type(o).__name__}")


def _iso(d: Any) -> str | None:
    if d is None:
        return None
    if isinstance(d, _dt.datetime):
        return d.isoformat()
    return str(d)


def _offset_of(d: Any) -> str | None:
    """'+HH:MM' / '-HH:MM' / 'UTC' of a tz-aware datetime or ISO string; None if naive/unknown."""
    if isinstance(d, str):
        m = re.search(r"(Z|[+-]\d{2}:\d{2})$", d.strip())
        if not m:
            return None
        return "UTC" if m.group(1) == "Z" else m.group(1)
    if isinstance(d, _dt.datetime) and d.tzinfo is not None:
        off = d.utcoffset() or _dt.timedelta(0)
        if off == _dt.timedelta(0):
            return "UTC"
        sign = "+" if off >= _dt.timedelta(0) else "-"
        off = abs(off)
        return f"{sign}{off.seconds // 3600:02d}:{(off.seconds // 60) % 60:02d}"
    return None


# ----------------------------------------------------------------------------------------------- backend properties
def _props_to_dict(props: Any) -> dict[str, Any]:
    if isinstance(props, (str, Path)):
        return json.loads(Path(props).read_text(encoding="utf-8"))
    if isinstance(props, dict):
        return props
    if hasattr(props, "to_dict"):
        return props.to_dict()
    raise TypeError("backend_properties: expected a BackendProperties, its to_dict() or a JSON path")


def backend_properties(props: Any, *, layout: list[int] | None = None, job_date: str | None = None,
                       source_label: str | None = None) -> dict[str, Any]:
    """Qiskit BackendProperties -> calibration_snapshot. Field by field, same names, same numbers, dated per parameter."""
    d = _props_to_dict(props)
    raw_sha = sha256_bytes(canonical_json(d).encode("utf-8"))
    qubits = d.get("qubits") or []
    gates = d.get("gates") or []
    t1, t2, ro, fd_t1, fd_t2, fd_ro = {}, {}, {}, {}, {}, {}
    for q, plist in enumerate(qubits):
        for p in plist or []:
            name, val, date = p.get("name"), p.get("value"), p.get("date")
            if val is None:
                continue
            if name == "T1":
                t1[str(q)] = float(val) * (1e6 if p.get("unit") in ("s", "sec") else 1.0)  # IBM reports us; be explicit
                fd_t1[str(q)] = _iso(date)
            elif name == "T2":
                t2[str(q)] = float(val) * (1e6 if p.get("unit") in ("s", "sec") else 1.0)
                fd_t2[str(q)] = _iso(date)
            elif name == "readout_error":
                ro[str(q)] = float(val)
                fd_ro[str(q)] = _iso(date)
    sx, fd_sx = {}, {}
    two_q: dict[str, dict[str, float]] = {}
    fd_two_q: dict[str, dict[str, str | None]] = {}
    for g in gates:
        gname, gq = g.get("gate"), list(g.get("qubits") or [])
        err = next((p for p in (g.get("parameters") or []) if p.get("name") == "gate_error" and p.get("value") is not None), None)
        if err is None:
            continue
        if gname == "sx" and len(gq) == 1:
            sx[str(gq[0])] = float(err["value"])
            fd_sx[str(gq[0])] = _iso(err.get("date"))
        elif len(gq) == 2 and gname in _TWO_Q:
            a, b = sorted(int(x) for x in gq)
            key = f"{a}_{b}"
            # a directed pair reported twice: keep the first seen (deterministic over the file order), never average
            two_q.setdefault(gname, {}).setdefault(key, float(err["value"]))
            fd_two_q.setdefault(gname, {}).setdefault(key, _iso(err.get("date")))
    gate_name = next((g for g in _TWO_Q if g in two_q), None)
    last = d.get("last_update_date")
    snap: dict[str, Any] = {
        "backend": d.get("backend_name"),
        "backend_version": d.get("backend_version"),
        "measured": _iso(last),
        "measured_note": "measured = BackendProperties.last_update_date; each parameter's own date is in field_dates",
        "n": len(qubits),
        "t1_us": t1, "t2_us": t2, "readout": ro, "sx": sx,
        "field_dates": {"t1_us": fd_t1, "t2_us": fd_t2, "readout": fd_ro, "sx": fd_sx},
        "source": {"adapter": "capas_ingest.backend_properties", "adapter_version": ADAPTER_VERSION,
                   "input_sha256": raw_sha, "input": source_label or "BackendProperties.to_dict()"},
    }
    if gate_name:
        snap[gate_name] = two_q[gate_name]
        snap["edges"] = [[int(x) for x in k.split("_")] for k in sorted(two_q[gate_name], key=lambda k: tuple(map(int, k.split("_"))))]
        snap["field_dates"]["cz" if gate_name == "cz" else gate_name] = fd_two_q[gate_name]
    tz = _offset_of(last) or next((_offset_of(v) for v in fd_t1.values() if v), None)
    if tz:
        snap["timezone"] = tz
    if layout:
        snap["layout"] = [int(q) for q in layout]
    if job_date:
        snap["job_date"] = job_date
    return snap


# ------------------------------------------------------------------------------------------------- pre-registration
def prereg(doc: Any, *, source_label: str | None = None) -> list[dict[str, Any]]:
    """atlas_prereg/v1 -> claim skeletons, one per metric_definition. The prereg must not carry results or verdicts."""
    if isinstance(doc, (str, Path)):
        raw = Path(doc).read_bytes()
        d = json.loads(raw.decode("utf-8"))
        src_sha = sha256_bytes(raw)
        label = source_label or str(Path(doc).resolve())   # absolute: pre-registrations usually live outside this repo
    else:
        d = doc
        src_sha = sha256_bytes(canonical_json(d).encode("utf-8"))
        label = source_label or "prereg dict"
    if d.get("schema") != "atlas_prereg/v1":
        raise ValueError(f"prereg: unsupported schema {d.get('schema')!r}")
    # verdict words inside a metric DEFINITION are legitimate (they name the bands); results are what must be absent
    for forbidden in ("results", "outcome", "outcomes", "verdict", "verdicts"):
        if forbidden in d:
            raise ValueError(f"prereg: carries '{forbidden}' — a pre-registration must not contain results")
    out = []
    for m in d.get("metric_definitions") or []:
        name = m.get("name")
        if not name:
            continue
        out.append({
            "claim": {"id": f"atlas:{d['id']}:{name}", "type": None, "text": f"{name}: {m.get('definition', '')}".strip()},
            "evidence": {},
            "meta": {"prereg": {"id": d.get("id"), "registered_utc": d.get("registered_utc"), "schema": d.get("schema"),
                                "supersedes": d.get("supersedes") or [], "pinned_files": len(d.get("pinned_sha256") or {}),
                                "metric": name, "definition_verbatim": m.get("definition")},
                     "sources": [{"path": label, "sha256": src_sha, "adapter": "capas_ingest.prereg", "adapter_version": ADAPTER_VERSION}],
                     "band_words_in_definition": bool(VERDICT_WORDS.search(str(m.get("definition", ""))))},
        })
    return out


# ----------------------------------------------------------------------------------------------------- results
class SpecError(ValueError):
    pass


def _load_results(source: Any) -> tuple[dict[str, Any], str, str]:
    """-> (data, sha256, label). CSV becomes {"rows": [ {col: value} ], "n_rows": N}; numeric-looking cells stay strings
    (no coercion: the spec must say what it expects and CSV has no types)."""
    if isinstance(source, dict):
        return source, sha256_bytes(canonical_json(source).encode("utf-8")), "results dict"
    p = Path(source); raw = p.read_bytes(); sha = sha256_bytes(raw)
    if p.suffix.lower() == ".csv":
        import csv, io
        rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8"))))
        return {"rows": rows, "n_rows": len(rows)}, sha, str(p)
    return json.loads(raw.decode("utf-8")), sha, str(p)


def _walk(data: Any, path: str) -> Any:
    cur = data
    for part in path.split("."):
        if isinstance(cur, list):
            try:
                cur = cur[int(part)]
            except (ValueError, IndexError):
                raise SpecError(f"path {path!r}: no list index {part!r}")
        elif isinstance(cur, dict):
            if part not in cur:
                raise SpecError(f"path {path!r}: no key {part!r}")
            cur = cur[part]
        else:
            raise SpecError(f"path {path!r}: cannot descend into {type(cur).__name__} at {part!r}")
    return cur


def _is_copyable(v: Any) -> bool:
    if isinstance(v, bool) or v is None or (isinstance(v, (int, float)) and not isinstance(v, bool)):
        return True
    if isinstance(v, list):
        return all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v)
    return False


def results(source: Any, spec: dict[str, Any], *, source_label: str | None = None) -> dict[str, Any]:
    """Copy evidence fields out of a results file by declared paths. Returns
    {"evidence": {...}, "provenance": {"source": {...}, "read": {field: path}, "declared": {field: value}}}.
    A string value is refused unless the spec entry says {"path": ..., "as": "str"}: a number that arrives as text
    (CSV, or a quoted JSON value) is a coding error, not something to coerce silently."""
    data, sha, label = _load_results(source)
    ev, read, declared = {}, {}, {}
    for field, how in spec.items():
        if isinstance(how, dict) and "const" in how:
            ev[field] = how["const"]; declared[field] = how["const"]; continue
        path, as_ = (how, None) if isinstance(how, str) else (how.get("path"), how.get("as"))
        if not isinstance(path, str):
            raise SpecError(f"{field}: spec entry must be a path string, {{'const': v}} or {{'path': ..., 'as': 'str'}}")
        v = _walk(data, path)
        if as_ == "str":
            if not isinstance(v, str):
                raise SpecError(f"{field}: {path!r} is {type(v).__name__}, spec expects a string")
        elif as_ == "float":
            try:
                v = float(v)
            except (TypeError, ValueError):
                raise SpecError(f"{field}: {path!r} = {v!r} is not a number (CSV cells need 'as': 'float' and must parse)")
        elif not _is_copyable(v):
            raise SpecError(f"{field}: {path!r} is {type(v).__name__} ({str(v)[:40]!r}); only numbers, booleans and lists of numbers are copied")
        ev[field] = v; read[field] = path
    return {"evidence": ev,
            "provenance": {"source": {"path": source_label or label, "sha256": sha, "adapter": "capas_ingest.results", "adapter_version": ADAPTER_VERSION},
                           "read": read, "declared": declared}}


def derived(provenance: dict[str, Any], field: str, rule: str, value: Any) -> Any:
    """Record a field the CODER derived from read values by a stated rule (e.g. a pre-registered direction rule). The
    adapter does not evaluate rules; it only makes the derivation visible next to what was read and what was declared."""
    provenance.setdefault("derived", {})[field] = rule
    return value


# --------------------------------------------------------------------------------------------------- provenance
def attach_source(payload: dict[str, Any], path: str | Path, *, adapter: str, root: Path | None = None) -> dict[str, Any]:
    p = Path(path)
    b = (root / p if root and not p.is_absolute() else p).read_bytes()
    payload.setdefault("meta", {}).setdefault("sources", []).append(
        {"path": str(path), "sha256": sha256_bytes(b), "adapter": adapter, "adapter_version": ADAPTER_VERSION})
    return payload


def verify_sources(payload: dict[str, Any], root: Path | None = None) -> list[str]:
    """Re-hash every declared source. Returns the list of problems (empty = all match). Missing file is a problem."""
    problems = []
    for s in (payload.get("meta") or {}).get("sources") or []:
        p = Path(s.get("path", ""))
        fp = root / p if root and not p.is_absolute() else p
        if not fp.is_file():
            problems.append(f"source missing: {s.get('path')}")
            continue
        got = sha256_bytes(fp.read_bytes())
        if got != s.get("sha256"):
            problems.append(f"source hash mismatch: {s.get('path')} declared {str(s.get('sha256'))[:12]} got {got[:12]}")
    return problems


# ---------------------------------------------------------------------------------------------------------- CLI
def _load_props(arg: str) -> tuple[Any, str]:
    if arg.startswith("fake:"):
        from qiskit_ibm_runtime import fake_provider as fp
        b = getattr(fp, arg[5:])()
        return b.properties(), arg
    return arg, arg


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__); return 2
    cmd, args = argv[1], argv[2:]
    out = args[args.index("-o") + 1] if "-o" in args else None
    if cmd == "backend-properties":
        props, label = _load_props(args[0])
        layout = [int(x) for x in args[args.index("--layout") + 1].split(",")] if "--layout" in args else None
        job_date = args[args.index("--job-date") + 1] if "--job-date" in args else None
        snap = backend_properties(props, layout=layout, job_date=job_date, source_label=label)
        text = json.dumps(snap, indent=1, ensure_ascii=False)
        (Path(out).write_text(text, encoding="utf-8") if out else print(text))
        print(f"snapshot: backend={snap.get('backend')} n={snap.get('n')} t1={len(snap['t1_us'])} edges={len(snap.get('edges') or [])} "
              f"tz={snap.get('timezone')} input_sha256={snap['source']['input_sha256'][:16]}", file=sys.stderr)
        return 0
    if cmd == "prereg":
        rows = prereg(args[0])
        text = "\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows) + "\n"
        (Path(out).write_text(text, encoding="utf-8") if out else print(text))
        print(f"skeletons: {len(rows)} from {args[0]}", file=sys.stderr)
        return 0
    if cmd == "verify-sources":
        root = Path(args[args.index("--root") + 1]) if "--root" in args else None
        bad = 0
        for line in Path(args[0]).read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            # sources live in the ROW's meta (schema v3 allows no `meta` inside the payload); fall back to the payload
            holder = row if (row.get("meta") or {}).get("sources") else row.get("payload", row)
            for pr in verify_sources(holder, root):
                bad += 1
                print(f"{row.get('claim_id') or row.get('payload', row).get('claim', {}).get('id')}: {pr}")
        print("sources:", "OK" if not bad else f"{bad} problem(s)")
        return 0 if not bad else 1
    print(__doc__); return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
