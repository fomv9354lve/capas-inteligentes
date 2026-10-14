#!/usr/bin/env python3
"""capas_check.py: engine-independent checker for CAPAS verdict certificates.

Written on 2026-10-14 from CERTIFICATE_SPEC.md (v2) only, without reading,
importing or running the CAPAS engine (GOVERNANCE §6: constructor != verifier).
Standard library only, Python 3.11+.

API
    check(record, table_bytes) -> (accepted, failed_check_numbers, messages)

    `record` is a sealed record {certificate, seal, seal_hash[, payload]} or a
    bare certificate object. Check numbers follow spec §7. The checker is
    fail-closed: any unexpected condition is a failure, never an acceptance,
    and it never repairs a certificate.

CLI
    python3 capas_check.py --table docs/rule_table.json FILE.jsonl
    Exit 0 if every record is accepted, 1 if any is rejected, 2 on unreadable input.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys

VERDICTS = ("ACCEPT", "REWRITE", "REJECT", "HOLD")
STAGES = ("base", "downgrade", "annotate")
SEP = "; "
SEAL_FIELDS = ("engine_tag", "engine_commit", "sealed_at", "sealed_by", "run_by")


# ---------------------------------------------------------------- §2 hashing
def canon(x) -> str:
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def H(x) -> str:
    return "sha256:" + hashlib.sha256(canon(x).encode("utf-8")).hexdigest()


def table_sha(table_bytes: bytes) -> str:
    return "sha256:" + hashlib.sha256(table_bytes).hexdigest()


# ---------------------------------------------------------------- rule table
class TableError(Exception):
    pass


def load_table(table_bytes: bytes) -> dict:
    """Parse the rule table into {id: rule}; strict about shape (fail-closed)."""
    try:
        doc = json.loads(table_bytes.decode("utf-8"))
    except Exception as e:  # noqa: BLE001
        raise TableError(f"rule table is not valid JSON: {e}")
    if not isinstance(doc, dict) or not isinstance(doc.get("rules"), list):
        raise TableError("rule table has no 'rules' array")
    rules: dict = {}
    for i, r in enumerate(doc["rules"]):
        if not isinstance(r, dict) or not isinstance(r.get("id"), str):
            raise TableError(f"rule #{i} has no string id")
        rid = r["id"]
        if rid in rules:
            raise TableError(f"duplicate rule id {rid}")
        if r.get("stage") not in STAGES:
            raise TableError(f"rule {rid}: bad stage {r.get('stage')!r}")
        if not isinstance(r.get("version"), int) or isinstance(r.get("version"), bool):
            raise TableError(f"rule {rid}: version is not an integer")
        ct = r.get("claim_type")
        if ct is not None and not isinstance(ct, str):
            raise TableError(f"rule {rid}: claim_type is neither null nor a string")
        if not isinstance(r.get("pattern"), str):
            raise TableError(f"rule {rid}: pattern is not a string")
        try:
            compiled = re.compile(r["pattern"], re.S)
        except re.error as e:
            raise TableError(f"rule {rid}: pattern does not compile: {e}")
        if r["stage"] == "base":
            if r.get("verdict") not in VERDICTS:
                raise TableError(f"base rule {rid}: bad verdict {r.get('verdict')!r}")
        elif r["stage"] == "downgrade":
            frm = r.get("from")
            if not isinstance(frm, list) or not all(v in VERDICTS for v in frm):
                raise TableError(f"downgrade rule {rid}: bad 'from'")
            if r.get("to") not in VERDICTS:
                raise TableError(f"downgrade rule {rid}: bad 'to'")
        rules[rid] = dict(r, _re=compiled)
    return rules


# ---------------------------------------------------------------- §5 reason
def decompose(reason: str, regexes: list) -> list | None:
    """Find split points so that segment i full-matches regexes[i] and the
    segments joined with '; ' equal `reason`. Backtracks over every candidate
    end position, since '; ' may also occur inside a segment. Returns the
    segments, or None if no assignment works."""
    n = len(regexes)
    memo: dict = {}

    def solve(i: int, pos: int):
        key = (i, pos)
        if key in memo:
            return memo[key]
        result = None
        if i == n - 1:
            seg = reason[pos:]
            if regexes[i].fullmatch(seg):
                result = [seg]
        else:
            end = reason.find(SEP, pos)
            while end != -1:
                seg = reason[pos:end]
                if regexes[i].fullmatch(seg):
                    rest = solve(i + 1, end + len(SEP))
                    if rest is not None:
                        result = [seg] + rest
                        break
                end = reason.find(SEP, end + 1)
        memo[key] = result
        return result

    if n == 0:
        return None
    return solve(0, 0)


# ---------------------------------------------------------------- §3 / §4
def audit_body(c: dict) -> dict:
    ia = c.get("invariant_audit")
    rf = c.get("required_fields")
    no = c.get("notices")
    return {
        "schema_version": c["schema_version"],
        "input_claim": c["input_claim"],
        "verdict": c["verdict"],
        "reason": c["reason"],
        "required_fields": [] if rf is None else rf,
        "invariant_audit": ia["verdict"] if isinstance(ia, dict) else None,
        "audit_hash_recipe": "v2",
        "engine_version": c["engine_version"],
        "rule_table_sha256": c["rule_table_sha256"],
        "rules_fired": c["rules_fired"],
        "evidence_sha256": c["evidence_sha256"],
        "notices": [] if no is None else no,
    }


def evidence_hash(payload: dict) -> str:
    """§3 (clarified 2026-10-14): E = payload.evidence when it is an object,
    {} otherwise (absent or any non-object value); M = payload.meta as given
    (any JSON value), or null if absent."""
    if not isinstance(payload, dict):
        raise ValueError("payload is not an object")
    ev = payload.get("evidence")
    ev = ev if isinstance(ev, dict) else {}
    meta = payload["meta"] if "meta" in payload else None
    return H({"evidence": ev, "meta": meta})


# ---------------------------------------------------------------- check
def _is_str_list(x) -> bool:
    return isinstance(x, list) and all(isinstance(s, str) for s in x)


def check(record: dict, table_bytes: bytes) -> tuple[bool, list[int], list[str]]:
    failed: set[int] = set()
    msgs: list[str] = []

    def fail(n: int, m: str) -> None:
        failed.add(n)
        msgs.append(f"check {n}: {m}")

    try:
        _check(record, table_bytes, fail)
    except Exception as e:  # noqa: BLE001  fail-closed
        failed.add(0)
        msgs.append(f"checker error (fail-closed): {type(e).__name__}: {e}")
    nums = sorted(failed)
    return (not nums, nums, msgs)


def _check(record, table_bytes, fail) -> None:
    if not isinstance(record, dict):
        raise ValueError("record is not a JSON object")
    sealed = "certificate" in record
    if sealed:
        cert = record["certificate"]
        payload = record.get("payload")
        has_payload = "payload" in record
    else:
        cert, payload, has_payload = record, None, False
    if not isinstance(cert, dict):
        raise ValueError("certificate is not a JSON object")

    # Field shapes the spec types in §1 (a malformed certificate fails closed).
    for f in ("schema_version", "reason", "engine_version", "rule_table_sha256",
              "evidence_sha256", "audit_hash", "audit_hash_recipe"):
        if not isinstance(cert.get(f), str):
            raise ValueError(f"certificate.{f} is missing or not a string")
    ic = cert.get("input_claim")
    if not isinstance(ic, dict) or not isinstance(ic.get("type"), str) or "id" not in ic:
        raise ValueError("certificate.input_claim is not an object with id and type")
    if "text" not in ic and "text_sha256" not in ic:
        raise ValueError("certificate.input_claim has neither text nor text_sha256")
    if cert.get("verdict") not in VERDICTS:
        raise ValueError(f"certificate.verdict {cert.get('verdict')!r} is not one of {VERDICTS}")
    if not _is_str_list(cert.get("rules_fired")):
        raise ValueError("certificate.rules_fired is not an array of strings")
    for f in ("required_fields", "notices"):
        if cert.get(f) is not None and not _is_str_list(cert[f]):
            raise ValueError(f"certificate.{f} is not an array of strings")
    ia = cert.get("invariant_audit")
    if ia is not None and not (isinstance(ia, dict) and isinstance(ia.get("verdict"), str)):
        raise ValueError("certificate.invariant_audit is neither null nor an object with a verdict string")

    # 1. recipe
    if cert["audit_hash_recipe"] != "v2":
        fail(1, f"audit_hash_recipe is {cert['audit_hash_recipe']!r}, not 'v2'")

    # 2. table hash
    got = table_sha(table_bytes)
    if got != cert["rule_table_sha256"]:
        fail(2, f"rule table sha256 {got} != certificate {cert['rule_table_sha256']}")

    # 3. rules exist, non-empty, first is base
    try:
        rules = load_table(table_bytes)
    except TableError as e:
        fail(3, f"rule table unusable: {e}")
        rules = None
    fired = cert["rules_fired"]
    chain = None
    if rules is not None:
        missing = [r for r in fired if r not in rules]
        if not fired:
            fail(3, "rules_fired is empty")
        elif missing:
            fail(3, f"rules_fired ids not in table: {missing}")
        elif rules[fired[0]]["stage"] != "base":
            fail(3, f"first rule {fired[0]} is a {rules[fired[0]]['stage']} rule, not base")
        else:
            chain = [rules[r] for r in fired]
    if chain is None:
        for n, why in ((4, "reason"), (5, "replay"), (6, "first rule claim_type"),
                       (7, "tail rule claim_type")):
            fail(n, f"{why} cannot be checked without a valid rules_fired chain")
    else:
        # 4. reason decomposition
        if decompose(cert["reason"], [r["_re"] for r in chain]) is None:
            fail(4, f"reason does not decompose over rules_fired {fired}: {cert['reason']!r}")

        # 5. replay
        v = chain[0]["verdict"]
        replay_ok = True
        for r in chain[1:]:
            if r["stage"] == "base":
                fail(5, f"second base rule {r['id']} in rules_fired")
                replay_ok = False
                break
            if r["stage"] == "downgrade":
                if v not in r["from"]:
                    fail(5, f"downgrade {r['id']} acted on {v}, outside its domain {r['from']}")
                    replay_ok = False
                    break
                v = r["to"]
        if replay_ok and v != cert["verdict"]:
            fail(5, f"replayed verdict {v} != certificate verdict {cert['verdict']}")

        # 6. first rule claim type
        ctype = ic["type"]
        ct0 = chain[0].get("claim_type")
        if ct0 is not None and ct0 != ctype:
            fail(6, f"base rule {chain[0]['id']} is for {ct0!r}, claim type is {ctype!r}")

        # 7. tail rule claim types
        bad = [r["id"] for r in chain[1:] if r.get("claim_type") is not None and r["claim_type"] != ctype]
        if bad:
            fail(7, f"tail rules {bad} do not apply to claim type {ctype!r}")

    # 8. audit hash
    ah = H(audit_body(cert))
    if ah != cert["audit_hash"]:
        fail(8, f"recomputed audit_hash {ah} != {cert['audit_hash']}")

    # 9. evidence hash (payload supplied)
    if has_payload:
        try:
            eh = evidence_hash(payload)
        except ValueError as e:
            fail(9, str(e))
        else:
            if eh != cert["evidence_sha256"]:
                fail(9, f"recomputed evidence_sha256 {eh} != {cert['evidence_sha256']}")

    # 10. seal (sealed record)
    if sealed:
        seal = record.get("seal")
        sh = record.get("seal_hash")
        if not isinstance(seal, dict):
            fail(10, "sealed record has no seal object")
        elif not isinstance(sh, str):
            fail(10, "sealed record has no seal_hash string")
        else:
            empty = [f for f in SEAL_FIELDS if not (isinstance(seal.get(f), str) and seal[f])]
            if empty:
                fail(10, f"seal fields missing or empty: {empty}")
            extra = sorted(set(seal) - set(SEAL_FIELDS))
            if extra:
                fail(10, f"seal has fields outside the spec: {extra}")
            got = H({"audit_hash": cert["audit_hash"], "seal": seal})
            if got != sh:
                fail(10, f"recomputed seal_hash {got} != {sh}")


# ---------------------------------------------------------------- CLI
def _claim_id(rec) -> str:
    try:
        c = rec["certificate"] if isinstance(rec, dict) and "certificate" in rec else rec
        cid = str(c["input_claim"]["id"])
        return cid if cid else "<empty id>"
    except Exception:  # noqa: BLE001
        return "<unknown>"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Check CAPAS certificates against CERTIFICATE_SPEC.md v2.")
    ap.add_argument("--table", required=True, help="rule table JSON file")
    ap.add_argument("file", help="JSONL file, one record per line")
    a = ap.parse_args(argv)
    try:
        with open(a.table, "rb") as fh:
            table_bytes = fh.read()
        with open(a.file, "r", encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError as e:
        print(f"error: cannot read input: {e}", file=sys.stderr)
        return 2
    except UnicodeDecodeError as e:
        print(f"error: input is not UTF-8: {e}", file=sys.stderr)
        return 2

    n = acc = 0
    for lineno, line in enumerate(lines, 1):
        if not line.strip():
            continue
        n += 1
        try:
            rec = json.loads(line)
        except json.JSONDecodeError as e:
            print(f"REJECTED <line {lineno}> checks=[0] not valid JSON: {e}")
            continue
        ok, nums, msgs = check(rec, table_bytes)
        cid = _claim_id(rec)
        if ok:
            acc += 1
            print(f"ACCEPTED {cid}")
        else:
            print(f"REJECTED {cid} checks={nums} {msgs[0] if msgs else ''}")
    print(f"checked {n}: {acc} accepted, {n - acc} rejected")
    if n == 0:
        return 2
    return 0 if acc == n else 1


if __name__ == "__main__":
    sys.exit(main())
