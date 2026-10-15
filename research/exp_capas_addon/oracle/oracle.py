#!/usr/bin/env python3
"""Ground-truth oracle for research/exp_capas_addon.

Re-derives the category of every case in ../cases/ from the bundles alone, by
  * execution: re-running each Python snippet with python3 and comparing to the run_log
    and to the claim's encoded predicate;
  * arithmetic: recomputing each ledger metric from rows_csv and checking period coverage;
  * explicit per-case scope checks encoded in checks.json (claim predicate, claimed
    version, whether the claim generalises beyond the run/period, counterexamples).

checks.json never stores the category. The derived category is compared with
labels.json; any disagreement (or any unverifiable log) makes the script exit 1.
Never consults CAPAS.
"""
import calendar
import csv
import io
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
CASES = os.path.join(os.path.dirname(HERE), "cases")

# Interpreters we can use to re-verify logs from other versions (optional).
KNOWN_INTERPRETERS = ["python3", "/opt/homebrew/bin/python3.13", "/usr/bin/python3"]

# ---------------------------------------------------------------- python helpers

def interp_version(py):
    r = subprocess.run([py, "--version"], capture_output=True, text=True)
    return (r.stdout or r.stderr).strip()


def run_snippet(py, code):
    """Run code as snippet.py in a temp dir; stdout+stderr merged; tmp path -> /work."""
    d = tempfile.mkdtemp(prefix="excase_")
    path = os.path.join(d, "snippet.py")
    with open(path, "w") as f:
        f.write(code)
    env = dict(os.environ, PYTHON_COLORS="0", NO_COLOR="1", PYTHONUNBUFFERED="1")
    env.pop("PYTHONSTARTUP", None)
    r = subprocess.run([py, "snippet.py"], cwd=d, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, text=True, env=env, timeout=30)
    out = r.stdout
    for p in sorted({d, os.path.realpath(d)}, key=len, reverse=True):
        out = out.replace(p, "/work")
    return out


def format_log(version_line, code, out):
    return ("$ python3 --version\n" + version_line + "\n"
            "$ cat snippet.py\n" + code.rstrip("\n") + "\n"
            "$ python3 snippet.py\n" + out)


def parse_log(log):
    """Return (version, code, output) from a log made by format_log."""
    m = re.match(r"\$ python3 --version\n(Python \S+)\n\$ cat snippet\.py\n(.*?)\n"
                 r"\$ python3 snippet\.py\n(.*)\Z", log, re.S)
    if not m:
        raise ValueError("unparseable run_log")
    return m.group(1).split()[1], m.group(2), m.group(3)


def eval_pred(expr, out):
    lines = out.splitlines()
    return bool(eval(expr, {"__builtins__": __builtins__}, {"out": out, "lines": lines}))


def derive_python(case, chk, cur_version):
    b = case["bundle"]
    log = b.get("run_log")
    if log is None:
        return "incomplete", "no run_log in bundle"
    ver, code, logged_out = parse_log(log)
    if code.strip() != b["snippet"].strip():
        return "incomplete", "run_log executed different code than the snippet"
    cv = chk.get("claimed_version")
    if cv and not (ver == cv or ver.startswith(cv + ".")):
        # optional: confirm the foreign log is itself genuine
        for py in KNOWN_INTERPRETERS:
            if interp_version(py) == "Python " + ver:
                if run_snippet(py, b["snippet"]) != logged_out:
                    return "ERROR", f"foreign log ({ver}) not reproducible"
        return "incomplete", f"claim is about Python {cv}, log is from {ver}"
    if ver != cur_version:
        return "ERROR", f"cannot re-execute: log {ver}, oracle has {cur_version}"
    out = run_snippet("python3", b["snippet"])
    if out != logged_out:
        return "ERROR", "re-execution does not reproduce run_log"
    if not eval_pred(chk["pred"], out):
        return "false", "claim predicate fails on the logged/re-executed output"
    if chk["scope"] == "universal":
        if not re.search(chk["universal_marker"], case["claim"], re.I):
            return "ERROR", "universal scope encoded but marker not in claim"
        note = "claim generalises beyond one run on one version"
        if chk.get("counter_code"):
            cout = run_snippet("python3", chk["counter_code"])
            if not eval_pred(chk["counter_pred"], cout):
                return "ERROR", "counterexample did not refute the generalisation"
            note += "; counterexample executed refutes it"
        return "exaggerated", note
    return "valid", "log reproduces and claim predicate holds, scope = this run"


# ---------------------------------------------------------------- ledger helpers

def parse_rows(rows_csv):
    rows = []
    for r in csv.DictReader(io.StringIO(rows_csv)):
        rows.append({"date": date.fromisoformat(r["date"]), "account": r["account"],
                     "customer": r["customer"], "amount": float(r["amount"])})
    return rows


def ym(d):
    return f"{d.year:04d}-{d.month:02d}"


def month_list(start, end):
    y, m = map(int, start.split("-"))
    ey, em = map(int, end.split("-"))
    out = []
    while (y, m) <= (ey, em):
        out.append(f"{y:04d}-{m:02d}")
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def period_months(period):
    m = re.fullmatch(r"(\d{4})-Q([1-4])", period)
    if m:
        y, q = int(m.group(1)), int(m.group(2))
        return month_list(f"{y}-{3*q-2:02d}", f"{y}-{3*q:02d}")
    m = re.fullmatch(r"(\d{4})-H([12])", period)
    if m:
        y, h = int(m.group(1)), int(m.group(2))
        return month_list(f"{y}-{6*h-5:02d}", f"{y}-{6*h:02d}")
    m = re.fullmatch(r"(\d{4}-\d{2})\.\.(\d{4}-\d{2})", period)
    if m:
        return month_list(m.group(1), m.group(2))
    if re.fullmatch(r"\d{4}-\d{2}", period):
        return [period]
    raise ValueError(period)


def period_bounds(months):
    y, m = map(int, months[0].split("-"))
    ey, em = map(int, months[-1].split("-"))
    return date(y, m, 1), date(ey, em, calendar.monthrange(ey, em)[1])


def required_accounts(spec):
    k = spec["metric"]
    if k in ("sum", "avg_ticket"):
        return list(spec["accounts"])
    if k == "margin":
        return ["revenue", "cogs"]
    if k == "growth":
        return ["revenue"]
    if k == "churn":
        return ["subscription"]
    if k == "dso":
        return ["revenue", "accounts_receivable"]
    if k == "refund_rate":
        return ["revenue", "refund"]
    raise ValueError(k)


def compute_metric(spec, rows, months):
    inp = [r for r in rows if ym(r["date"]) in months]
    S = lambda accs, ms=months: sum(r["amount"] for r in rows
                                    if r["account"] in accs and ym(r["date"]) in ms)
    k = spec["metric"]
    if k == "sum":
        return round(S(spec["accounts"]), 2)
    if k == "margin":
        rev, cogs = S(["revenue"]), S(["cogs"])
        return (rev - cogs) / rev
    if k == "growth":
        return S(["revenue"], [spec["to"]]) / S(["revenue"], [spec["from"]]) - 1
    if k == "avg_ticket":
        sel = [r["amount"] for r in inp if r["account"] in spec["accounts"]]
        return sum(sel) / len(sel)
    if k == "churn":
        first = {r["customer"] for r in rows if r["account"] == "subscription" and ym(r["date"]) == months[0]}
        last = {r["customer"] for r in rows if r["account"] == "subscription" and ym(r["date"]) == months[-1]}
        return len(first - last) / len(first)
    if k == "dso":
        _, end = period_bounds(months)
        ar = sum(r["amount"] for r in rows if r["account"] == "accounts_receivable" and r["date"] == end)
        days = (end - period_bounds(months)[0]).days + 1
        return ar / S(["revenue"]) * days
    if k == "refund_rate":
        return -S(["refund"]) / S(["revenue"])
    raise ValueError(k)


def derive_ledger(case, chk):
    b = case["bundle"]
    rows = parse_rows(b["rows_csv"])
    months = period_months(b["period"])
    p0, p1 = period_bounds(months)
    notes = b.get("notes") or ""
    if "Export range:" not in notes:
        return "ERROR", "notes lack export range"
    seg = notes.split("Export range:", 1)[1].split(".", 1)[0]
    ranges = sorted((date.fromisoformat(a), date.fromisoformat(z)) for a, z in
                    re.findall(r"(\d{4}-\d{2}-\d{2}) to (\d{4}-\d{2}-\d{2})", seg))
    cur = p0  # walk the sorted ranges forward from the period start
    for a, z in ranges:
        if a <= cur and z >= cur:
            cur = date.fromordinal(z.toordinal() + 1)
    if cur <= p1:
        return "incomplete", f"export range(s) {[(str(a), str(z)) for a, z in ranges]} leave {cur} onward (to {p1}) uncovered"
    have = {ym(r["date"]) for r in rows}
    missing = [x for x in months if x not in have]
    if missing:
        return "incomplete", f"no rows for {missing}"
    accs = {r["account"] for r in rows if p0 <= r["date"] <= p1}
    miss_acc = [a for a in required_accounts(chk["spec"]) if a not in accs]
    if miss_acc:
        return "incomplete", f"definition needs account(s) {miss_acc} absent from rows"
    val = compute_metric(chk["spec"], rows, months)
    c = chk["claim"]
    if c["op"] == "approx":
        ok = abs(val - c["value"]) <= c["tol"] + 1e-9
    elif c["op"] == "gt":
        ok = val > c["value"]
    elif c["op"] == "lt":
        ok = val < c["value"]
    else:
        raise ValueError(c["op"])
    if not ok:
        return "false", f"recomputed {val:.6g} vs claim {c['op']} {c['value']}"
    sc = chk["scope"]
    if sc["kind"] == "period":
        return "valid", f"recomputed {val:.6g} supports claim; full coverage"
    if not re.search(sc["marker"], case["claim"], re.I):
        return "ERROR", "beyond-period scope encoded but marker not in claim"
    if sc["kind"] in ("future", "unbounded"):
        return "exaggerated", f"true for {b['period']} ({val:.6g}); claim is {sc['kind']}"
    if sc["kind"] == "months":
        outside = [x for x in sc["months"] if x not in months]
        if not outside:
            return "ERROR", "claimed months are inside the bundle period"
        return "exaggerated", f"true for {b['period']}; claim covers {len(outside)} months without rows"
    raise ValueError(sc)


# ---------------------------------------------------------------- main

def main():
    labels = json.load(open(os.path.join(HERE, "labels.json")))
    checks = json.load(open(os.path.join(HERE, "checks.json")))
    cur = interp_version("python3").split()[1]
    files = sorted(f for f in os.listdir(CASES) if f.endswith(".json"))
    bad = 0
    print(f"oracle: python3 = {cur}; {len(files)} cases")
    print(f"{'case':6} {'family':16} {'label':12} {'derived':12} ok  reason")
    for fn in files:
        case = json.load(open(os.path.join(CASES, fn)))
        cid = case["case_id"]
        chk = checks[cid]
        try:
            if case["family"] == "python_behavior":
                got, why = derive_python(case, chk, cur)
            else:
                got, why = derive_ledger(case, chk)
        except Exception as e:  # noqa: BLE001
            got, why = "ERROR", repr(e)
        lab = labels[cid]["category"]
        ok = got == lab
        bad += not ok
        print(f"{cid:6} {case['family']:16} {lab:12} {got:12} {'Y' if ok else 'N':3} {why}")
    if set(labels) != {f[:-5] for f in files}:
        print("label set != case set"); bad += 1
    print(f"\n{len(files) - bad}/{len(files)} labels re-derived")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
