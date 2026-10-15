#!/usr/bin/env python3
"""Ground-truth oracle for research/exp_capas_v2.

Re-derives the category of every claim from cases/ alone:
  * Python materials: the snippet is executed with python3 (isolated mode, temp dir); its
    "label -> value" output lines are compared with what the claim asserts; when a run log
    is present, the log is checked byte-for-byte against a fresh run.
  * Ledger materials: metrics are recomputed from rows_csv with the definitions stated in
    the material (revenue = sales - refunds, etc.); a period counts as covered only if every
    month of it has at least one row in the ledger(s) used.
  * Generalisations: the narrower statement must hold AND an explicit counterexample (an
    executed expression, a syntax check with ast feature_version, or a period that fails or
    is not covered) must exist.
  * Incomplete: the materials lack what is needed (named code absent from every material,
    account absent, period not covered, interpreter version not in any log).
The per-claim checks are in SPECS below. labels.json is read only at the end, to compare.
Exit status 0 iff every label is re-derived and every integrity check passes.
"""
import ast
import contextlib
import csv
import functools
import io
import json
import math
import operator
import os
import platform
import re
import subprocess
import sys
import tempfile
from decimal import Decimal, ROUND_HALF_UP

HERE = os.path.dirname(os.path.abspath(__file__))
CASES = os.path.join(HERE, "..", "cases")
LABELS = os.path.join(HERE, "labels.json")
PY = "python3"
LOCAL_VERSION = subprocess.run([PY, "--version"], capture_output=True, text=True).stdout.strip()  # "Python 3.x.y"


class OracleError(Exception):
    pass


# ----------------------------------------------------------------------------- loading
def load_reports():
    reps = {}
    for fn in sorted(os.listdir(CASES)):
        if fn.endswith(".json"):
            with open(os.path.join(CASES, fn), encoding="utf-8") as fh:
                r = json.load(fh)
            reps[r["report_id"]] = r
    return reps


# ----------------------------------------------------------------------------- python
_RUN = {}


def run_snippet(src):
    if src in _RUN:
        return _RUN[src]
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "snippet.py")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(src)
        cp = subprocess.run([PY, "-I", "snippet.py"], cwd=td, capture_output=True, text=True, timeout=60)
    if cp.returncode != 0:
        raise OracleError("snippet failed: " + cp.stderr[-400:])
    _RUN[src] = cp.stdout
    return cp.stdout


def parse_out(stdout):
    out = {}
    for line in stdout.splitlines():
        if " -> " in line:
            k, v = line.split(" -> ", 1)
            if k in out:
                raise OracleError("duplicate output label " + k)
            out[k] = v
    return out


def namespace(src):
    ns = {"__name__": "snippet_ns"}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(src, "snippet.py", "exec"), ns)
    return ns


def raises(fn, *a, **k):
    try:
        fn(*a, **k)
    except Exception:
        return True
    return False


def syntax_fails(src, ver):
    try:
        ast.parse(src, feature_version=tuple(ver))
    except SyntaxError:
        return True
    return False


def log_version(log):
    m = re.search(r"^\$ python3 --version\n(Python [0-9.]+)\n", log, re.M)
    return m.group(1) if m else None


def check_run_log(mat):
    log = mat.get("run_log")
    if not log:
        return
    src = mat["snippet"]
    expected = ("$ python3 --version\n" + LOCAL_VERSION + "\n$ cat snippet.py\n" + src
                + ("" if src.endswith("\n") else "\n") + "$ python3 snippet.py\n" + run_snippet(src))
    if log != expected:
        raise OracleError("run_log does not match a fresh run")


# ----------------------------------------------------------------------------- ledger
def ledger_rows(mats):
    rows = []
    for src_i, mat in enumerate(mats):
        rd = csv.DictReader(io.StringIO(mat["rows_csv"]))
        if rd.fieldnames != ["date", "account", "customer", "amount"]:
            raise OracleError("bad ledger header")
        for r in rd:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", r["date"]):
                raise OracleError("bad date " + r["date"])
            rows.append((r["date"], r["account"], r["customer"], Decimal(r["amount"]), src_i))
    return rows


def months_of(period):
    if re.fullmatch(r"\d{4}-Q[1-4]", period):
        y, q = period.split("-Q")
        return [f"{y}-{m:02d}" for m in range(3 * int(q) - 2, 3 * int(q) + 1)]
    if re.fullmatch(r"\d{4}-\d{2}", period):
        return [period]
    if re.fullmatch(r"\d{4}", period):
        return [f"{period}-{m:02d}" for m in range(1, 13)]
    raise OracleError("bad period " + period)


def prev_period(period, yoy=False):
    if re.fullmatch(r"\d{4}-Q[1-4]", period):
        y, q = int(period[:4]), int(period[-1])
        if yoy:
            return f"{y - 1}-Q{q}"
        return f"{y - 1}-Q4" if q == 1 else f"{y}-Q{q - 1}"
    if re.fullmatch(r"\d{4}-\d{2}", period):
        y, m = int(period[:4]), int(period[5:])
        if yoy:
            return f"{y - 1}-{m:02d}"
        return f"{y - 1}-12" if m == 1 else f"{y}-{m - 1:02d}"
    return str(int(period) - 1)


def covered(rows, period):
    """A month is covered iff some ledger has rows in it and no ledger has a gap there (a month inside that
    ledger's own first..last month span with no rows at all). Ledgers that are consecutive exports of one series
    (R2, R6) do not overlap; ledgers of parallel entities (R5) do, and each must cover the month."""
    by_src = {}
    for r in rows:
        by_src.setdefault(r[4], set()).add(r[0][:7])
    for m in months_of(period):
        if not any(m in ms for ms in by_src.values()):
            return False
        if any(min(ms) <= m <= max(ms) and m not in ms for ms in by_src.values()):
            return False
    return True


def _sum(rows, period, account):
    ms = set(months_of(period))
    return sum((r[3] for r in rows if r[0][:7] in ms and r[1] == account), Decimal(0))


def metric(rows, name, period, account=None):
    """Return the metric as Decimal, or None if the materials cannot settle it."""
    accounts = {r[1] for r in rows}
    if name in ("growth", "yoy"):
        other = prev_period(period, yoy=(name == "yoy"))
        a, b = metric(rows, "revenue", period), metric(rows, "revenue", other)
        if a is None or b is None:
            return None
        return (a / b - 1) * 100
    if not covered(rows, period):
        return None
    if name == "account_total":
        if account not in accounts:
            return None
        return _sum(rows, period, account)
    need = {"revenue": ["sales"], "sales": ["sales"], "gm": ["sales", "cogs"], "avg_ticket": ["sales"],
            "customers": ["sales"], "refund_rate": ["sales"], "gross_profit": ["sales", "cogs"]}[name]
    if any(a not in accounts for a in need):
        return None
    sales = _sum(rows, period, "sales")
    refunds = _sum(rows, period, "refunds")
    rev = sales - refunds
    ms = set(months_of(period))
    custs = {r[2] for r in rows if r[0][:7] in ms and r[1] == "sales" and r[2]}
    if name == "revenue":
        return rev
    if name == "sales":
        return sales
    if name == "gm":
        return (rev - _sum(rows, period, "cogs")) / rev * 100
    if name == "gross_profit":
        return rev - _sum(rows, period, "cogs")
    if name == "avg_ticket":
        return rev / len(custs)
    if name == "customers":
        return Decimal(len(custs))
    if name == "refund_rate":
        return refunds / sales * 100
    raise OracleError("unknown metric " + name)


def rounded(x, scale, dp):
    q = Decimal(1).scaleb(-dp)
    return (x / Decimal(scale)).quantize(q, rounding=ROUND_HALF_UP)


OPS = {">": operator.gt, ">=": operator.ge, "<": operator.lt, "<=": operator.le}


# ----------------------------------------------------------------------------- claim checks
def materials_text(rep):
    parts = []
    for m in rep["materials"].values():
        parts += [str(v) for v in m.values() if v]
    return "\n".join(parts).lower()


def snippet_ns(rep, mat_id):
    ns = namespace(rep["materials"][mat_id]["snippet"])
    ns.update(raises=raises, math=math, functools=functools, operator=operator, Decimal=Decimal)
    return ns


def expect_holds(rep, spec):
    """Every 'label -> value' pair must match the fresh run; every assert must be True in the snippet's namespace."""
    out = parse_out(run_snippet(rep["materials"][spec["mat"]]["snippet"]))
    ok = True
    for k, v in spec.get("expect", []):
        if k not in out:
            raise OracleError(f"label {k!r} not in output of {spec['mat']}")
        ok = ok and out[k] == v
    if spec.get("asserts"):
        ns = snippet_ns(rep, spec["mat"])
        for a in spec["asserts"]:
            ok = ok and (eval(a, ns) is True)
    if not spec.get("expect") and not spec.get("asserts"):
        raise OracleError("empty expectation")
    return ok


def rows_of(rep, mats):
    return ledger_rows([rep["materials"][m] for m in mats])


def derive(rep, claim, spec, top=True):
    t = spec["t"]
    text = claim["text"]
    if top:
        for g in spec.get("guard", []):  # asserted values must literally appear in the claim text
            if g not in text:
                raise OracleError(f"guard {g!r} not in claim text")
        for w in spec.get("scope_words", []):
            if w.lower() not in text.lower():
                raise OracleError(f"scope word {w!r} not in claim text")

    if t == "out":
        return "valid" if expect_holds(rep, spec) else "false"

    if t == "out_general":
        if not expect_holds(rep, spec):
            return "false"
        if eval(spec["counter"], snippet_ns(rep, spec["mat"])) is not True:
            raise OracleError("counterexample does not hold")
        return "exaggerated"

    if t == "version_scope":
        if not expect_holds(rep, spec):
            return "false"
        if not syntax_fails(rep["materials"][spec["mat"]]["snippet"], spec["older"]):
            raise OracleError("older grammar parses the snippet")
        return "exaggerated"

    if t == "other_version":
        want = "Python " + spec["version"]
        logs = [log_version(m.get("run_log") or "") for m in rep["materials"].values() if m.get("kind") == "python"]
        if spec["version"] not in text:
            raise OracleError("version not in text")
        if any(l and (l == want or l.startswith(want + ".")) for l in logs):
            return "settleable"
        if LOCAL_VERSION == want or LOCAL_VERSION.startswith(want + "."):
            return "settleable"
        return "incomplete"

    if t == "absent":
        mt = materials_text(rep)
        if not any(tok.lower() in text.lower() for tok in spec["tokens"]):
            raise OracleError("absent-token not in claim")
        if any(tok.lower() in mt for tok in spec["tokens"]):
            return "present"
        return "incomplete"

    if t == "metric":
        rows = rows_of(rep, spec["mats"])
        v = metric(rows, spec["metric"], spec["period"], spec.get("account"))
        if v is None:
            return "incomplete"
        return "valid" if rounded(v, spec.get("scale", 1), spec["dp"]) == Decimal(spec["claimed"]) else "false"

    if t == "metric_cmp":
        rows = rows_of(rep, spec["mats"])
        a = metric(rows, spec["metric"], spec["a"])
        b = metric(rows, spec["metric"], spec["b"])
        if a is None or b is None:
            return "incomplete"
        return "valid" if OPS[spec["op"]](a, b) else "false"

    if t == "threshold":
        v = metric(rows_of(rep, spec["mats"]), spec["metric"], spec["period"])
        if v is None:
            return "incomplete"
        return "valid" if OPS[spec["op"]](v, Decimal(spec["threshold"])) else "false"

    if t == "metric_general":
        for it in spec["narrow"]:
            c = derive(rep, claim, it, top=False)
            if c != "valid":
                return c
        bad = []
        for u in spec["universe"]:
            mats, p = (u if isinstance(u, list) else [spec["mats"], u])
            v = metric(rows_of(rep, mats), spec["metric"], p)
            if v is None or not OPS[spec["op"]](v, Decimal(spec["threshold"])):
                bad.append(p)
        if not bad:
            raise OracleError("generalisation has no counterexample or uncovered period")
        return "exaggerated"

    if t == "metric_all":  # a universal over an explicitly finite set of periods, all inside the materials
        vals = [metric(rows_of(rep, spec["mats"]), spec["metric"], p, spec.get("account")) for p in spec["universe"]]
        if any(v is None for v in vals):
            return "incomplete"
        return "valid" if all(OPS[spec["op"]](v, Decimal(spec["threshold"])) for v in vals) else "false"

    if t == "compose":  # narrower parts must all hold; at least one part of the generalisation must fail
        for it in spec["narrow"]:
            c = derive(rep, claim, it, top=False)
            if c != "valid":
                return c
        if not any(derive(rep, claim, it, top=False) in ("false", "incomplete") for it in spec["counter"]):
            raise OracleError("no counterexample among the generalisation's parts")
        return "exaggerated"

    if t == "out_vs_metric":
        out = parse_out(run_snippet(rep["materials"][spec["mat"]]["snippet"]))
        v = metric(rows_of(rep, spec["mats"]), spec["metric"], spec["period"])
        if v is None:
            return "incomplete"
        q = Decimal(1).scaleb(-spec["dp"])
        same = Decimal(out[spec["key"]]).quantize(q, rounding=ROUND_HALF_UP) == rounded(v, 1, spec["dp"])
        return "valid" if same == spec["match"] else "false"

    if t == "dataset_equal":  # the snippet embeds the ledger material's rows verbatim
        needle = rep["materials"][spec["ledger"]]["rows_csv"]
        return "valid" if needle in rep["materials"][spec["mat"]]["snippet"] else "false"

    raise OracleError("unknown spec type " + t)


SPECS = {'R1#1': {'t': 'absent', 'tokens': ['format_invoice_total']},
 'R1#2': {'t': 'out',
          'mat': 'S4',
          'expect': [['split_instalments(1000, 3)', '[334, 333, 333]'], ['sum(split_instalments(1000, 3))', '1000']],
          'asserts': []},
 'R1#3': {'t': 'absent', 'tokens': ['apply_vat']},
 'R1#4': {'t': 'out_general',
          'mat': 'S6',
          'expect': [],
          'asserts': ["by_amount[0][0] == 'INV-1'"],
          'counter': "[r[0] for r in by_amount if r[1] == 200] == ['INV-3', 'INV-2']",
          'scope_words': ['always']},
 'R1#5': {'t': 'version_scope',
          'mat': 'S7',
          'expect': [["classify({'code': 200})", "'ok'"], ["classify({'code': 503})", "'retry'"]],
          'older': [3, 8],
          'scope_words': ['3.8']},
 'R1#6': {'t': 'out', 'mat': 'S1', 'expect': [['round(2.5)', '3']], 'asserts': []},
 'R1#7': {'t': 'out', 'mat': 'S5', 'expect': [['b', "['A', 'B']"], ['a is b', 'True']], 'asserts': []},
 'R1#8': {'t': 'out', 'mat': 'S3', 'expect': [['dedupe([1, True, 1.0])', '[1, True, 1.0]']], 'asserts': []},
 'R1#9': {'t': 'out', 'mat': 'S2', 'expect': [['sum(items) == 1.0', 'True']], 'asserts': []},
 'R1#10': {'t': 'out', 'mat': 'S1', 'expect': [['round_money(0.125)', '0.13']], 'asserts': []},
 'R1#11': {'t': 'out',
           'mat': 'S3',
           'expect': [['dedupe_fast(data)', '[3, 1, 2]'], ['dedupe(data)', '[3, 1, 2]']],
           'asserts': []},
 'R1#12': {'t': 'out_general',
           'mat': 'S4',
           'expect': [['-7 % 2', '1']],
           'asserts': [],
           'counter': '7 % -2 < 0',
           'scope_words': ['never']},
 'R1#13': {'t': 'out', 'mat': 'S4', 'expect': [['-7 // 2', '-3']], 'asserts': []},
 'R1#14': {'t': 'absent', 'tokens': ['benchmark', 'timeit', 'perf_counter']},
 'R1#15': {'t': 'out_general',
           'mat': 'S2',
           'expect': [['math.fsum(items)', '1.0']],
           'asserts': [],
           'counter': 'math.fsum([0.1, 0.2]) != 0.3',
           'scope_words': ['any list']},
 'R1#16': {'t': 'out',
           'mat': 'S4',
           'expect': [['split_instalments(1000, 3)', '[334, 333, 333]'], ['split_instalments(10, 4)', '[3, 3, 2, 2]']],
           'asserts': ['all(max(p) - min(p) <= 1 for p in [split_instalments(1000, 3), split_instalments(10, 4)])']},
 'R1#17': {'t': 'out_general',
           'mat': 'S4',
           'expect': [['split_instalments(1000, 3)', '[334, 333, 333]'],
                      ['sum(split_instalments(1000, 3))', '1000'],
                      ['split_instalments(10, 4)', '[3, 3, 2, 2]']],
           'asserts': [],
           'counter': 'raises(split_instalments, 100, 0)',
           'scope_words': ['any n']},
 'R1#18': {'t': 'out', 'mat': 'S5', 'expect': [['a is b', 'False']], 'asserts': []},
 'R1#19': {'t': 'out', 'mat': 'S6', 'expect': [['max(invoices, key=amount)', "('INV-2', 200)"]], 'asserts': []},
 'R1#20': {'t': 'out_general',
           'mat': 'S3',
           'expect': [['dedupe(data)', '[3, 1, 2]']],
           'asserts': [],
           'counter': 'raises(dedupe, [[1], [1]])',
           'scope_words': ['any list']},
 'R1#21': {'t': 'absent', 'tokens': ['retry queue', 'max_retries']},
 'R1#22': {'t': 'out_general',
           'mat': 'S2',
           'expect': [['math.isclose(0.1 + 0.2, 0.3)', 'True']],
           'asserts': [],
           'counter': 'not math.isclose(0.0, 0.1 + 0.2 - 0.3)',
           'scope_words': ['any two']},
 'R1#23': {'t': 'other_version', 'mat': 'S2', 'version': '3.11'},
 'R1#24': {'t': 'out', 'mat': 'S1', 'expect': [['round_money_dec(1.005)', "Decimal('1.01')"]], 'asserts': []},
 'R1#25': {'t': 'out', 'mat': 'S1', 'expect': [['round_money(2.675)', '2.67']], 'asserts': []},
 'R1#26': {'t': 'out_general',
           'mat': 'S1',
           'expect': [['round_money_dec(2.675)', "Decimal('2.68')"],
                      ['round_money_dec(1.005)', "Decimal('1.01')"],
                      ['round_money_dec(0.125)', "Decimal('0.13')"],
                      ['round_money_dec(0.375)', "Decimal('0.38')"],
                      ['round_money_dec(10.0)', "Decimal('10.00')"]],
           'asserts': [],
           'counter': "raises(round_money_dec, float('inf'))",
           'scope_words': ['every float']},
 'R1#27': {'t': 'out', 'mat': 'S7', 'expect': [["classify({'code': 503})", "'fail'"]], 'asserts': []},
 'R1#28': {'t': 'absent', 'tokens': ['csv exporter', 'csv']},
 'R1#29': {'t': 'out',
           'mat': 'S6',
           'expect': [['desc', "[('INV-3', 200), ('INV-2', 200), ('INV-1', 100), ('INV-4', 100)]"]],
           'asserts': []},
 'R1#30': {'t': 'other_version', 'mat': 'S6', 'version': '3.10'},
 'R2#1': {'t': 'metric_general',
          'mats': ['L1'],
          'narrow': [{'t': 'metric',
                      'mats': ['L1'],
                      'metric': 'gm',
                      'period': '2025-Q3',
                      'claimed': '35.8',
                      'dp': 1,
                      'guard': [],
                      'scale': 1}],
          'metric': 'gm',
          'universe': ['2025-01',
                       '2025-02',
                       '2025-03',
                       '2025-04',
                       '2025-05',
                       '2025-06',
                       '2025-07',
                       '2025-08',
                       '2025-09'],
          'op': '>',
          'threshold': '30',
          'scope_words': ['every month']},
 'R2#2': {'t': 'metric',
          'mats': ['L1'],
          'metric': 'gm',
          'period': '2025-Q3',
          'claimed': '35.8',
          'dp': 1,
          'guard': ['35.8%'],
          'scale': 1},
 'R2#3': {'t': 'metric_general',
          'mats': ['L1'],
          'narrow': [{'t': 'metric',
                      'mats': ['L1'],
                      'metric': 'avg_ticket',
                      'period': '2025-Q3',
                      'claimed': '6284.97',
                      'dp': 2,
                      'guard': [],
                      'scale': 1}],
          'metric': 'avg_ticket',
          'universe': ['2025-07', '2025-08', '2025-09'],
          'op': '>',
          'threshold': '3500',
          'scope_words': ['each month']},
 'R2#4': {'t': 'metric_cmp', 'mats': ['L1'], 'metric': 'revenue', 'a': '2025-Q3', 'op': '<', 'b': '2025-Q2'},
 'R2#5': {'t': 'metric_general',
          'mats': ['L1'],
          'narrow': [{'t': 'metric',
                      'mats': ['L1'],
                      'metric': 'refund_rate',
                      'period': '2025-Q3',
                      'claimed': '6.8',
                      'dp': 1,
                      'guard': [],
                      'scale': 1}],
          'metric': 'refund_rate',
          'universe': ['2025-01',
                       '2025-02',
                       '2025-03',
                       '2025-04',
                       '2025-05',
                       '2025-06',
                       '2025-07',
                       '2025-08',
                       '2025-09'],
          'op': '<',
          'threshold': '10',
          'scope_words': ['every month']},
 'R2#6': {'t': 'absent', 'tokens': ['days sales outstanding', 'receivable']},
 'R2#7': {'t': 'metric',
          'mats': ['L1'],
          'metric': 'account_total',
          'period': '2025-Q3',
          'claimed': '0',
          'dp': 0,
          'guard': [],
          'scale': 1,
          'account': 'marketing'},
 'R2#8': {'t': 'metric',
          'mats': ['L2'],
          'metric': 'revenue',
          'period': '2024-Q4',
          'claimed': '31728.51',
          'dp': 2,
          'guard': [],
          'scale': 1},
 'R2#9': {'t': 'metric',
          'mats': ['L1'],
          'metric': 'account_total',
          'period': '2025-Q3',
          'claimed': '21400',
          'dp': 0,
          'guard': [],
          'scale': 1,
          'account': 'opex'},
 'R2#10': {'t': 'metric_general',
           'mats': ['L1'],
           'narrow': [{'t': 'threshold',
                       'mats': ['L1'],
                       'metric': 'revenue',
                       'period': '2025-08',
                       'op': '>',
                       'threshold': '20000'},
                      {'t': 'threshold',
                       'mats': ['L1'],
                       'metric': 'revenue',
                       'period': '2025-09',
                       'op': '>',
                       'threshold': '20000'}],
           'metric': 'revenue',
           'universe': ['2025-01',
                        '2025-02',
                        '2025-03',
                        '2025-04',
                        '2025-05',
                        '2025-06',
                        '2025-07',
                        '2025-08',
                        '2025-09'],
           'op': '>',
           'threshold': '20000',
           'scope_words': ['every month']},
 'R2#11': {'t': 'metric',
           'mats': ['L1'],
           'metric': 'refund_rate',
           'period': '2025-Q2',
           'claimed': '7.4',
           'dp': 1,
           'guard': ['7.4%'],
           'scale': 1},
 'R2#12': {'t': 'metric',
           'mats': ['L1'],
           'metric': 'growth',
           'period': '2025-Q2',
           'claimed': '33.0',
           'dp': 1,
           'guard': ['33.0%'],
           'scale': 1},
 'R2#13': {'t': 'metric',
           'mats': ['L2'],
           'metric': 'revenue',
           'period': '2024-Q3',
           'claimed': '58643.12',
           'dp': 2,
           'guard': ['58,643.12'],
           'scale': 1},
 'R2#14': {'t': 'metric',
           'mats': ['L1'],
           'metric': 'growth',
           'period': '2025-Q3',
           'claimed': '-3.4',
           'dp': 1,
           'guard': ['3.4%', 'below'],
           'scale': 1},
 'R2#15': {'t': 'metric',
           'mats': ['L1'],
           'metric': 'revenue',
           'period': '2025-Q3',
           'claimed': '75419.64',
           'dp': 2,
           'guard': ['75,419.64'],
           'scale': 1},
 'R2#16': {'t': 'metric',
           'mats': ['L1'],
           'metric': 'gm',
           'period': '2025-Q3',
           'claimed': '35.7',
           'dp': 1,
           'guard': ['35.7%'],
           'scale': 1},
 'R2#17': {'t': 'metric',
           'mats': ['L1'],
           'metric': 'revenue',
           'period': '2025-Q3',
           'claimed': '80913.69',
           'dp': 2,
           'guard': ['80,913.69'],
           'scale': 1},
 'R2#18': {'t': 'metric',
           'mats': ['L2'],
           'metric': 'gm',
           'period': '2024-Q4',
           'claimed': '36.4',
           'dp': 1,
           'guard': [],
           'scale': 1},
 'R2#19': {'t': 'metric',
           'mats': ['L1', 'L2'],
           'metric': 'yoy',
           'period': '2025-Q3',
           'claimed': '45.1',
           'dp': 1,
           'guard': ['45.1%'],
           'scale': 1},
 'R2#20': {'t': 'metric_all',
           'mats': ['L1'],
           'metric': 'revenue',
           'universe': ['2025-01',
                        '2025-02',
                        '2025-03',
                        '2025-04',
                        '2025-05',
                        '2025-06',
                        '2025-07',
                        '2025-08',
                        '2025-09'],
           'op': '>',
           'threshold': '17000',
           'scope_words': ['every month']},
 'R2#21': {'t': 'metric',
           'mats': ['L1'],
           'metric': 'revenue',
           'period': '2025-09',
           'claimed': '26410.79',
           'dp': 2,
           'guard': ['26,410.79'],
           'scale': 1},
 'R2#22': {'t': 'metric',
           'mats': ['L1'],
           'metric': 'avg_ticket',
           'period': '2025-Q2',
           'claimed': '8457.43',
           'dp': 2,
           'guard': ['8,457.43'],
           'scale': 1},
 'R2#23': {'t': 'metric',
           'mats': ['L1', 'L2'],
           'metric': 'revenue',
           'period': '2024',
           'claimed': '147000',
           'dp': 0,
           'guard': [],
           'scale': 1},
 'R2#24': {'t': 'metric',
           'mats': ['L1'],
           'metric': 'customers',
           'period': '2025-Q1',
           'claimed': '12',
           'dp': 0,
           'guard': ['12'],
           'scale': 1},
 'R2#25': {'t': 'metric',
           'mats': ['L1'],
           'metric': 'revenue',
           'period': '2025-10',
           'claimed': '24000',
           'dp': 0,
           'guard': [],
           'scale': 1},
 'R2#26': {'t': 'metric_general',
           'mats': ['L1', 'L2'],
           'narrow': [{'t': 'metric',
                       'mats': ['L1', 'L2'],
                       'metric': 'gm',
                       'period': '2024-Q3',
                       'claimed': '36.3',
                       'dp': 1,
                       'guard': [],
                       'scale': 1}],
           'metric': 'gm',
           'universe': ['2024-Q4', '2025-Q1', '2025-Q2', '2025-Q3'],
           'op': '>',
           'threshold': '35',
           'scope_words': ['every quarter']},
 'R2#27': {'t': 'metric_general',
           'mats': ['L1'],
           'narrow': [{'t': 'metric',
                       'mats': ['L1'],
                       'metric': 'growth',
                       'period': '2025-Q2',
                       'claimed': '33.2',
                       'dp': 1,
                       'guard': [],
                       'scale': 1}],
           'metric': 'growth',
           'universe': ['2025-Q1', '2025-Q2', '2025-Q3'],
           'op': '>',
           'threshold': '0',
           'scope_words': ['throughout']},
 'R2#28': {'t': 'metric_general',
           'mats': ['L1', 'L2'],
           'narrow': [{'t': 'metric',
                       'mats': ['L1', 'L2'],
                       'metric': 'yoy',
                       'period': '2025-Q3',
                       'claimed': '45.1',
                       'dp': 1,
                       'guard': [],
                       'scale': 1}],
           'metric': 'yoy',
           'universe': ['2025-07', '2025-08', '2025-09'],
           'op': '>',
           'threshold': '40',
           'scope_words': ['each month']},
 'R2#29': {'t': 'metric',
           'mats': ['L1', 'L2'],
           'metric': 'growth',
           'period': '2025-Q1',
           'claimed': '84.8',
           'dp': 1,
           'guard': [],
           'scale': 1},
 'R2#30': {'t': 'metric',
           'mats': ['L1'],
           'metric': 'avg_ticket',
           'period': '2025-Q3',
           'claimed': '6284.97',
           'dp': 2,
           'guard': ['6,284.97'],
           'scale': 1},
 'R3#1': {'t': 'out', 'mat': 'S2', 'expect': [["quarter_of('2025-12-31')", "'2025-Q3'"]], 'asserts': []},
 'R3#2': {'t': 'other_version', 'mat': 'S1', 'version': '3.11'},
 'R3#3': {'t': 'out', 'mat': 'S2', 'expect': [["quarter_of('2025-03-01')", "'2025-Q1'"]], 'asserts': []},
 'R3#4': {'t': 'metric',
          'mats': ['L1'],
          'metric': 'revenue',
          'period': '2024-Q4',
          'claimed': '817.83',
          'dp': 2,
          'guard': [],
          'scale': 1},
 'R3#5': {'t': 'metric_general',
          'mats': ['L1'],
          'narrow': [{'t': 'metric',
                      'mats': ['L1'],
                      'metric': 'avg_ticket',
                      'period': '2025-Q2',
                      'claimed': '382.26',
                      'dp': 2,
                      'guard': [],
                      'scale': 1}],
          'metric': 'avg_ticket',
          'universe': ['2025-01', '2025-02', '2025-03', '2025-04', '2025-05', '2025-06'],
          'op': '>',
          'threshold': '300',
          'scope_words': ['every month']},
 'R3#6': {'t': 'metric_all',
          'mats': ['L1'],
          'metric': 'account_total',
          'universe': ['2024-12', '2025-01', '2025-02', '2025-03', '2025-04', '2025-05', '2025-06'],
          'op': '>',
          'threshold': '0',
          'scope_words': ['every month'],
          'account': 'cogs'},
 'R3#7': {'t': 'compose',
          'narrow': [{'t': 'out_vs_metric',
                      'mat': 'S1',
                      'key': 'revenue 2025-Q1',
                      'mats': ['L1'],
                      'metric': 'revenue',
                      'period': '2025-Q1',
                      'dp': 2,
                      'match': True},
                     {'t': 'out_vs_metric',
                      'mat': 'S1',
                      'key': 'revenue 2025-Q2',
                      'mats': ['L1'],
                      'metric': 'revenue',
                      'period': '2025-Q2',
                      'dp': 2,
                      'match': True}],
          'counter': [{'t': 'out_vs_metric',
                       'mat': 'S1',
                       'key': 'avg_ticket 2025-Q1',
                       'mats': ['L1'],
                       'metric': 'avg_ticket',
                       'period': '2025-Q1',
                       'dp': 2,
                       'match': True},
                      {'t': 'out_vs_metric',
                       'mat': 'S1',
                       'key': 'avg_ticket 2025-Q2',
                       'mats': ['L1'],
                       'metric': 'avg_ticket',
                       'period': '2025-Q2',
                       'dp': 2,
                       'match': True}],
          'scope_words': ['every figure']},
 'R3#8': {'t': 'out', 'mat': 'S3', 'expect': [['parsed[0].date()', "'2025-04-01'"]], 'asserts': []},
 'R3#9': {'t': 'out_vs_metric',
          'mat': 'S1',
          'key': 'gross_margin_pct 2025-Q1',
          'mats': ['L1'],
          'metric': 'gm',
          'period': '2025-Q1',
          'dp': 1,
          'match': True},
 'R3#10': {'t': 'out_vs_metric',
           'mat': 'S1',
           'key': 'revenue 2025-Q2',
           'mats': ['L1'],
           'metric': 'revenue',
           'period': '2025-Q2',
           'dp': 2,
           'match': True},
 'R3#11': {'t': 'metric',
           'mats': ['L1'],
           'metric': 'avg_ticket',
           'period': '2025-Q2',
           'claimed': '152.90',
           'dp': 2,
           'guard': ['152.90'],
           'scale': 1},
 'R3#12': {'t': 'metric',
           'mats': ['L1'],
           'metric': 'gm',
           'period': '2025-Q2',
           'claimed': '56.1',
           'dp': 1,
           'guard': ['56.1%'],
           'scale': 1},
 'R3#13': {'t': 'metric',
           'mats': ['L1'],
           'metric': 'refund_rate',
           'period': '2025-Q2',
           'claimed': '7.1',
           'dp': 1,
           'guard': ['7.1%'],
           'scale': 1},
 'R3#14': {'t': 'absent', 'tokens': ['campaign', 'new subscribers']},
 'R3#15': {'t': 'metric',
           'mats': ['L1'],
           'metric': 'account_total',
           'period': '2025-Q2',
           'claimed': '0',
           'dp': 0,
           'guard': [],
           'scale': 1,
           'account': 'shipping'},
 'R3#16': {'t': 'metric',
           'mats': ['L1'],
           'metric': 'growth',
           'period': '2025-Q1',
           'claimed': '139.1',
           'dp': 1,
           'guard': [],
           'scale': 1},
 'R3#17': {'t': 'absent', 'tokens': ['churn']},
 'R3#18': {'t': 'metric',
           'mats': ['L1'],
           'metric': 'revenue',
           'period': '2025-Q1',
           'claimed': '2076.81',
           'dp': 2,
           'guard': ['2,076.81'],
           'scale': 1},
 'R3#19': {'t': 'out_general',
           'mat': 'S3',
           'expect': [['parsed[0] == parsed[1]', 'True']],
           'asserts': [],
           'counter': "raises(lambda: datetime.fromisoformat('2025-04-01T05:30:00') < parsed[0])",
           'scope_words': ['any two']},
 'R3#20': {'t': 'metric_general',
           'mats': ['L1'],
           'narrow': [{'t': 'metric',
                       'mats': ['L1'],
                       'metric': 'growth',
                       'period': '2025-Q2',
                       'claimed': '17.3',
                       'dp': 1,
                       'guard': [],
                       'scale': 1}],
           'metric': 'growth',
           'universe': ['2025-04', '2025-05', '2025-06'],
           'op': '>',
           'threshold': '0',
           'scope_words': ['every month']},
 'R3#21': {'t': 'metric',
           'mats': ['L1'],
           'metric': 'revenue',
           'period': '2025-07',
           'claimed': '760',
           'dp': 0,
           'guard': [],
           'scale': 1},
 'R3#22': {'t': 'out_general',
           'mat': 'S2',
           'expect': [["quarter_of('2025-04-01')", "'2025-Q2'"]],
           'asserts': [],
           'counter': "raises(quarter_of, '20250401')",
           'scope_words': ['any ISO 8601']},
 'R3#23': {'t': 'metric_general',
           'mats': ['L1'],
           'narrow': [{'t': 'metric',
                       'mats': ['L1'],
                       'metric': 'gm',
                       'period': '2025-Q2',
                       'claimed': '56.0',
                       'dp': 1,
                       'guard': [],
                       'scale': 1}],
           'metric': 'gm',
           'universe': ['2025-01', '2025-02', '2025-03', '2025-04', '2025-05', '2025-06'],
           'op': '>',
           'threshold': '50',
           'scope_words': ['every month']},
 'R3#24': {'t': 'metric_general',
           'mats': ['L1'],
           'narrow': [{'t': 'metric',
                       'mats': ['L1'],
                       'metric': 'customers',
                       'period': '2025-Q2',
                       'claimed': '6',
                       'dp': 0,
                       'guard': [],
                       'scale': 1}],
           'metric': 'customers',
           'universe': ['2025-01', '2025-02', '2025-03', '2025-04', '2025-05', '2025-06'],
           'op': '>=',
           'threshold': '3',
           'scope_words': ['every month']},
 'R3#25': {'t': 'metric',
           'mats': ['L1'],
           'metric': 'growth',
           'period': '2025-Q2',
           'claimed': '17.3',
           'dp': 1,
           'guard': ['17.3%'],
           'scale': 1},
 'R3#26': {'t': 'metric_general',
           'mats': ['L1'],
           'narrow': [{'t': 'metric',
                       'mats': ['L1'],
                       'metric': 'refund_rate',
                       'period': '2025-Q2',
                       'claimed': '7.1',
                       'dp': 1,
                       'guard': [],
                       'scale': 1}],
           'metric': 'refund_rate',
           'universe': ['2024-12', '2025-01', '2025-02', '2025-03', '2025-04', '2025-05', '2025-06'],
           'op': '<',
           'threshold': '12',
           'scope_words': ['every month']},
 'R3#27': {'t': 'out', 'mat': 'S3', 'expect': [['parsed[0] == parsed[1]', 'True']], 'asserts': []},
 'R3#28': {'t': 'metric',
           'mats': ['L1'],
           'metric': 'revenue',
           'period': '2025-06',
           'claimed': '650.07',
           'dp': 2,
           'guard': ['650.07'],
           'scale': 1},
 'R3#29': {'t': 'dataset_equal', 'mat': 'S1', 'ledger': 'L1'},
 'R3#30': {'t': 'out_vs_metric',
           'mat': 'S1',
           'key': 'avg_ticket 2025-Q2',
           'mats': ['L1'],
           'metric': 'avg_ticket',
           'period': '2025-Q2',
           'dp': 2,
           'match': True},
 'R4#1': {'t': 'absent', 'tokens': ['rows per minute', 'throughput', 'timeit', 'perf_counter']},
 'R4#2': {'t': 'other_version', 'mat': 'S5', 'version': '3.12'},
 'R4#3': {'t': 'out', 'mat': 'S3', 'expect': [["int(' 7 ')", "'ValueError'"]], 'asserts': []},
 'R4#4': {'t': 'out_general',
          'mat': 'S2',
          'expect': [["'MX-USD-02'.removeprefix('MX-')", "'USD-02'"], ["'MX-USD-02'.lstrip('MX-')", "'USD-02'"]],
          'asserts': [],
          'counter': "'MX-MXN-01'.lstrip('MX-') != 'MX-MXN-01'.removeprefix('MX-')",
          'scope_words': ['any code']},
 'R4#5': {'t': 'absent', 'tokens': ['parse_import_date']},
 'R4#6': {'t': 'out_general',
          'mat': 'S6',
          'expect': [["parse('ABC-123 x4')", "('ABC-123', 4)"]],
          'asserts': [],
          'counter': "parse('abc-123 x4') is None",
          'scope_words': ['regardless']},
 'R4#7': {'t': 'out',
          'mat': 'S5',
          'expect': [['a.casefold() == b.casefold()', 'True'], ['a.lower() == b.lower()', 'False']],
          'asserts': []},
 'R4#8': {'t': 'out', 'mat': 'S5', 'expect': [["len('e\\u0301')", '1']], 'asserts': []},
 'R4#9': {'t': 'version_scope',
          'mat': 'S8',
          'expect': [['first(rows)', "('SKU-001', 4)"], ['first([])', 'None']],
          'older': [3, 10],
          'scope_words': ['3.10']},
 'R4#10': {'t': 'absent', 'tokens': ['iso_week_start']},
 'R4#11': {'t': 'out_general',
           'mat': 'S4',
           'expect': [['(date(2025, 3, 1) - date(2025, 2, 1)).days', '28']],
           'asserts': [],
           'counter': '(date(2025, 1, 1) + timedelta(days=28)).month == 1',
           'scope_words': ['any date']},
 'R4#12': {'t': 'out', 'mat': 'S1', 'expect': [['cleaned', "['SKU-001', 'SKU-002', 'SKU-003']"]], 'asserts': []},
 'R4#13': {'t': 'out', 'mat': 'S6', 'expect': [["parse('ABC-123  x10 extra')", 'None']], 'asserts': []},
 'R4#14': {'t': 'absent', 'tokens': ['parse_csv_line']},
 'R4#15': {'t': 'out',
           'mat': 'S4',
           'expect': [['date(2024, 2, 29).replace(year=2025)', 'datetime.date(2025, 2, 28)']],
           'asserts': []},
 'R4#16': {'t': 'out',
           'mat': 'S7',
           'expect': [["json.dumps({'amount': Decimal('1.10')})", "'TypeError'"],
                      ["json.dumps({'amount': Decimal('1.10')}, default=str)", '\'{"amount": "1.10"}\'']],
           'asserts': []},
 'R4#17': {'t': 'out_general',
           'mat': 'S7',
           'expect': [["json.dumps({'b': 1, 'a': 2}, sort_keys=True)", '\'{"a": 2, "b": 1}\'']],
           'asserts': [],
           'counter': "json.dumps({'b': 1, 'a': 2}) != json.dumps({'a': 2, 'b': 1})",
           'scope_words': ['any two equal']},
 'R4#18': {'t': 'out', 'mat': 'S1', 'expect': [["'SKU-KUS'.strip('SKU')", "'-KUS'"]], 'asserts': []},
 'R4#19': {'t': 'out',
           'mat': 'S2',
           'expect': [["'MX-MXN-01'.lstrip('MX-')", "'N-01'"], ["'MX-MXN-01'.removeprefix('MX-')", "'MXN-01'"]],
           'asserts': []},
 'R4#20': {'t': 'out', 'mat': 'S1', 'expect': [["'a  b'.split(' ')", "['a', 'b']"]], 'asserts': []},
 'R4#21': {'t': 'out', 'mat': 'S4', 'expect': [['date(2024, 12, 30).isocalendar()', '(2025, 1, 1)']], 'asserts': []},
 'R4#22': {'t': 'version_scope',
           'mat': 'S6',
           'expect': [["parse('ABC-123 x4')", "('ABC-123', 4)"]],
           'older': [3, 7],
           'scope_words': ['3.7']},
 'R4#23': {'t': 'out_general',
           'mat': 'S3',
           'expect': [["'42'.isdigit()", 'True'], ["'٤٢'.isdigit()", 'True'], ["int('42')", '42'], ["int('٤٢')", '42']],
           'asserts': [],
           'counter': "raises(int, '\\u00b2')",
           'scope_words': ['whenever']},
 'R4#24': {'t': 'out', 'mat': 'S7', 'expect': [['json.loads(\'{"a": 1, "a": 2}\')', "{'a': 1}"]], 'asserts': []},
 'R4#25': {'t': 'out', 'mat': 'S3', 'expect': [["int('٤٢')", '42']], 'asserts': []},
 'R4#26': {'t': 'other_version', 'mat': 'S7', 'version': '3.10'},
 'R4#27': {'t': 'out',
           'mat': 'S4',
           'expect': [['date(2024, 1, 31) + timedelta(days=30)', 'datetime.date(2024, 3, 2)']],
           'asserts': []},
 'R4#28': {'t': 'out',
           'mat': 'S2',
           'expect': [["'MX-MXN-01'.removeprefix('MX-')", "'MXN-01'"],
                      ["'MX-USD-02'.removeprefix('MX-')", "'USD-02'"],
                      ["'MXN-03'.removeprefix('MX-')", "'MXN-03'"]],
           'asserts': []},
 'R4#29': {'t': 'absent', 'tokens': ['normalise_phone']},
 'R4#30': {'t': 'absent', 'tokens': ['cp1252', 'encoding']},
 'R5#1': {'t': 'metric_cmp', 'mats': ['L2'], 'metric': 'revenue', 'a': '2025-Q1', 'op': '>', 'b': '2025-Q2'},
 'R5#2': {'t': 'metric',
          'mats': ['L1'],
          'metric': 'gm',
          'period': '2025-Q3',
          'claimed': '42.7',
          'dp': 1,
          'guard': ['42.7%'],
          'scale': 1},
 'R5#3': {'t': 'metric_general',
          'mats': ['L1'],
          'narrow': [{'t': 'threshold',
                      'mats': ['L1'],
                      'metric': 'revenue',
                      'period': '2025-06',
                      'op': '>',
                      'threshold': '15000'},
                     {'t': 'threshold',
                      'mats': ['L1'],
                      'metric': 'revenue',
                      'period': '2025-09',
                      'op': '>',
                      'threshold': '15000'}],
          'metric': 'revenue',
          'universe': ['2025-07', '2025-08', '2025-09'],
          'op': '>',
          'threshold': '15000',
          'scope_words': ['every month']},
 'R5#4': {'t': 'metric',
          'mats': ['L2'],
          'metric': 'revenue',
          'period': '2025-Q2',
          'claimed': '25903.52',
          'dp': 2,
          'guard': ['25,903.52'],
          'scale': 1},
 'R5#5': {'t': 'metric',
          'mats': ['L1'],
          'metric': 'yoy',
          'period': '2025-Q3',
          'claimed': '18',
          'dp': 0,
          'guard': [],
          'scale': 1},
 'R5#6': {'t': 'metric',
          'mats': ['L1'],
          'metric': 'revenue',
          'period': '2025-10',
          'claimed': '16210.00',
          'dp': 2,
          'guard': [],
          'scale': 1},
 'R5#7': {'t': 'metric_general',
          'mats': ['L1'],
          'narrow': [{'t': 'metric',
                      'mats': ['L1'],
                      'metric': 'growth',
                      'period': '2025-Q3',
                      'claimed': '22.5',
                      'dp': 1,
                      'guard': [],
                      'scale': 1}],
          'metric': 'growth',
          'universe': [[['L1'], '2025-Q3'], [['L2'], '2025-Q3']],
          'op': '>',
          'threshold': '0',
          'scope_words': ['both entities']},
 'R5#8': {'t': 'metric',
          'mats': ['L1', 'L2'],
          'metric': 'customers',
          'period': '2025-Q2',
          'claimed': '18',
          'dp': 0,
          'guard': ['18'],
          'scale': 1},
 'R5#9': {'t': 'metric',
          'mats': ['L2'],
          'metric': 'avg_ticket',
          'period': '2025-Q3',
          'claimed': '2113.98',
          'dp': 2,
          'guard': [],
          'scale': 1},
 'R5#10': {'t': 'metric',
           'mats': ['L2'],
           'metric': 'gm',
           'period': '2025-Q3',
           'claimed': '35.9',
           'dp': 1,
           'guard': [],
           'scale': 1},
 'R5#11': {'t': 'metric',
           'mats': ['L1'],
           'metric': 'growth',
           'period': '2025-Q3',
           'claimed': '22.5',
           'dp': 1,
           'guard': ['22.5%'],
           'scale': 1},
 'R5#12': {'t': 'metric',
           'mats': ['L1', 'L2'],
           'metric': 'gm',
           'period': '2025-Q1',
           'claimed': '41.0',
           'dp': 1,
           'guard': ['41.0%'],
           'scale': 1},
 'R5#13': {'t': 'metric_general',
           'mats': ['L1'],
           'narrow': [{'t': 'metric',
                       'mats': ['L1'],
                       'metric': 'customers',
                       'period': '2025-Q3',
                       'claimed': '15',
                       'dp': 0,
                       'guard': [],
                       'scale': 1}],
           'metric': 'customers',
           'universe': ['2025-07', '2025-08', '2025-09'],
           'op': '>=',
           'threshold': '10',
           'scope_words': ['every month']},
 'R5#14': {'t': 'absent', 'tokens': ['fx rate', 'exchange rate', 'depreciat']},
 'R5#15': {'t': 'metric',
           'mats': ['L1'],
           'metric': 'account_total',
           'period': '2025-Q3',
           'claimed': '0',
           'dp': 0,
           'guard': [],
           'scale': 1,
           'account': 'payroll'},
 'R5#16': {'t': 'metric',
           'mats': ['L1'],
           'metric': 'revenue',
           'period': '2025-06',
           'claimed': '15593.77',
           'dp': 2,
           'guard': ['15,593.77'],
           'scale': 1},
 'R5#17': {'t': 'metric',
           'mats': ['L1', 'L2'],
           'metric': 'revenue',
           'period': '2025-Q3',
           'claimed': '66100.83',
           'dp': 2,
           'guard': [],
           'scale': 1},
 'R5#18': {'t': 'metric_general',
           'mats': ['L1', 'L2'],
           'narrow': [{'t': 'metric',
                       'mats': ['L1', 'L2'],
                       'metric': 'gm',
                       'period': '2025-Q1',
                       'claimed': '41.0',
                       'dp': 1,
                       'guard': [],
                       'scale': 1}],
           'metric': 'gm',
           'universe': ['2025-Q1', '2025-Q2', '2025-Q3'],
           'op': '>',
           'threshold': '38',
           'scope_words': ['every quarter']},
 'R5#19': {'t': 'metric',
           'mats': ['L2'],
           'metric': 'refund_rate',
           'period': '2025-Q2',
           'claimed': '9.1',
           'dp': 1,
           'guard': ['9.1%'],
           'scale': 1},
 'R5#20': {'t': 'metric',
           'mats': ['L1'],
           'metric': 'gm',
           'period': '2025-Q1',
           'claimed': '44.2',
           'dp': 1,
           'guard': ['44.2%'],
           'scale': 1},
 'R5#21': {'t': 'metric',
           'mats': ['L1'],
           'metric': 'revenue',
           'period': '2025-Q3',
           'claimed': '45787.68',
           'dp': 2,
           'guard': ['45,787.68'],
           'scale': 1},
 'R5#22': {'t': 'metric',
           'mats': ['L1'],
           'metric': 'revenue',
           'period': '2025-Q2',
           'claimed': '37707.40',
           'dp': 2,
           'guard': ['37,707.40'],
           'scale': 1},
 'R5#23': {'t': 'metric',
           'mats': ['L1', 'L2'],
           'metric': 'growth',
           'period': '2025-Q2',
           'claimed': '-15.4',
           'dp': 1,
           'guard': ['15.4%', 'fell'],
           'scale': 1},
 'R5#24': {'t': 'metric_general',
           'mats': ['L1'],
           'narrow': [{'t': 'metric',
                       'mats': ['L1'],
                       'metric': 'refund_rate',
                       'period': '2025-Q3',
                       'claimed': '0.4',
                       'dp': 1,
                       'guard': [],
                       'scale': 1}],
           'metric': 'refund_rate',
           'universe': ['2025-01',
                        '2025-02',
                        '2025-03',
                        '2025-04',
                        '2025-05',
                        '2025-06',
                        '2025-07',
                        '2025-08',
                        '2025-09'],
           'op': '<',
           'threshold': '1',
           'scope_words': ['every month']},
 'R5#25': {'t': 'metric_general',
           'mats': ['L1'],
           'narrow': [{'t': 'metric',
                       'mats': ['L1'],
                       'metric': 'gm',
                       'period': '2025-Q3',
                       'claimed': '42.7',
                       'dp': 1,
                       'guard': [],
                       'scale': 1}],
           'metric': 'gm',
           'universe': ['2025-01',
                        '2025-02',
                        '2025-03',
                        '2025-04',
                        '2025-05',
                        '2025-06',
                        '2025-07',
                        '2025-08',
                        '2025-09'],
           'op': '>',
           'threshold': '40',
           'scope_words': ['every month']},
 'R5#26': {'t': 'metric_all',
           'mats': ['L1'],
           'metric': 'gm',
           'universe': ['2025-01',
                        '2025-02',
                        '2025-03',
                        '2025-04',
                        '2025-05',
                        '2025-06',
                        '2025-07',
                        '2025-08',
                        '2025-09'],
           'op': '>',
           'threshold': '38',
           'scope_words': ['every month']},
 'R5#27': {'t': 'metric',
           'mats': ['L1', 'L2'],
           'metric': 'revenue',
           'period': '2025-Q2',
           'claimed': '57055.32',
           'dp': 2,
           'guard': ['57,055.32'],
           'scale': 1},
 'R5#28': {'t': 'metric',
           'mats': ['L1', 'L2'],
           'metric': 'growth',
           'period': '2025-Q3',
           'claimed': '15.9',
           'dp': 1,
           'guard': [],
           'scale': 1},
 'R5#29': {'t': 'metric',
           'mats': ['L2'],
           'metric': 'avg_ticket',
           'period': '2025-Q1',
           'claimed': '3912.96',
           'dp': 2,
           'guard': ['3,912.96'],
           'scale': 1},
 'R5#30': {'t': 'metric_general',
           'mats': ['L2'],
           'narrow': [{'t': 'metric',
                       'mats': ['L2'],
                       'metric': 'avg_ticket',
                       'period': '2025-Q1',
                       'claimed': '3700.50',
                       'dp': 2,
                       'guard': [],
                       'scale': 1}],
           'metric': 'avg_ticket',
           'universe': ['2025-01',
                        '2025-02',
                        '2025-03',
                        '2025-04',
                        '2025-05',
                        '2025-06',
                        '2025-07',
                        '2025-08',
                        '2025-09'],
           'op': '>',
           'threshold': '2500',
           'scope_words': ['every month']},
 'R6#1': {'t': 'metric_general',
          'mats': ['L1', 'L2'],
          'narrow': [{'t': 'metric',
                      'mats': ['L1', 'L2'],
                      'metric': 'yoy',
                      'period': '2024-Q3',
                      'claimed': '71.3',
                      'dp': 1,
                      'guard': [],
                      'scale': 1}],
          'metric': 'yoy',
          'universe': ['2024-07', '2024-08', '2024-09'],
          'op': '>',
          'threshold': '50',
          'scope_words': ['each month']},
 'R6#2': {'t': 'out',
          'mat': 'S1',
          'expect': [["Decimal('0.125').quantize(CENT, ROUND_HALF_EVEN)", '0.13']],
          'asserts': []},
 'R6#3': {'t': 'metric_general',
          'mats': ['L1', 'L2'],
          'narrow': [{'t': 'metric',
                      'mats': ['L1', 'L2'],
                      'metric': 'growth',
                      'period': '2024-Q4',
                      'claimed': '-14.4',
                      'dp': 1,
                      'guard': [],
                      'scale': 1}],
          'metric': 'growth',
          'universe': ['2024-Q1', '2024-Q2', '2024-Q3', '2024-Q4'],
          'op': '<',
          'threshold': '0',
          'scope_words': ['every quarter']},
 'R6#4': {'t': 'metric',
          'mats': ['L1'],
          'metric': 'growth',
          'period': '2024-Q4',
          'claimed': '14.4',
          'dp': 1,
          'guard': ['14.4%', 'grew'],
          'scale': 1},
 'R6#5': {'t': 'metric',
          'mats': ['L1'],
          'metric': 'gm',
          'period': '2024',
          'claimed': '48.1',
          'dp': 1,
          'guard': ['48.1%'],
          'scale': 1},
 'R6#6': {'t': 'out',
          'mat': 'S1',
          'expect': [['vat_on_total(basket)', '0.25'], ['vat_per_line(basket)', '0.24']],
          'asserts': []},
 'R6#7': {'t': 'metric',
          'mats': ['L1'],
          'metric': 'gm',
          'period': '2024-Q4',
          'claimed': '48.3',
          'dp': 1,
          'guard': ['48.3%'],
          'scale': 1},
 'R6#8': {'t': 'out', 'mat': 'S2', 'expect': [['additive(p, ds)', '72.00']], 'asserts': []},
 'R6#9': {'t': 'out_general',
          'mat': 'S3',
          'expect': [['tier(4999.99)', "'silver'"]],
          'asserts': [],
          'counter': "tier(999) == 'list'",
          'scope_words': ['any spend']},
 'R6#10': {'t': 'out', 'mat': 'S4', 'expect': [['round(Fraction(5, 2))', '3']], 'asserts': []},
 'R6#11': {'t': 'out', 'mat': 'S3', 'expect': [['tier(5000)', "'silver'"]], 'asserts': []},
 'R6#12': {'t': 'other_version', 'mat': 'S3', 'version': '3.10'},
 'R6#13': {'t': 'out_general',
           'mat': 'S4',
           'expect': [['sum([1/3] * 3) == 1', 'True']],
           'asserts': [],
           'counter': 'sum([1/49] * 49) != 1',
           'scope_words': ['any n']},
 'R6#14': {'t': 'metric',
           'mats': ['L1'],
           'metric': 'revenue',
           'period': '2024',
           'claimed': '202056.60',
           'dp': 2,
           'guard': ['202,056.60'],
           'scale': 1},
 'R6#15': {'t': 'version_scope',
           'mat': 'S5',
           'expect': [["parse_rule('pct:10')", "('pct', 10.0)"]],
           'older': [3, 9],
           'scope_words': ['3.9']},
 'R6#16': {'t': 'absent', 'tokens': ['P07']},
 'R6#17': {'t': 'metric',
           'mats': ['L1', 'L2'],
           'metric': 'revenue',
           'period': '2025-01',
           'claimed': '18400',
           'dp': 0,
           'guard': [],
           'scale': 1},
 'R6#18': {'t': 'metric_general',
           'mats': ['L1'],
           'narrow': [{'t': 'metric',
                       'mats': ['L1'],
                       'metric': 'refund_rate',
                       'period': '2024-Q4',
                       'claimed': '13.5',
                       'dp': 1,
                       'guard': [],
                       'scale': 1}],
           'metric': 'refund_rate',
           'universe': ['2024-01',
                        '2024-02',
                        '2024-03',
                        '2024-04',
                        '2024-05',
                        '2024-06',
                        '2024-07',
                        '2024-08',
                        '2024-09',
                        '2024-10',
                        '2024-11',
                        '2024-12'],
           'op': '<',
           'threshold': '15',
           'scope_words': ['every month']},
 'R6#19': {'t': 'metric',
           'mats': ['L1', 'L2'],
           'metric': 'yoy',
           'period': '2024-Q3',
           'claimed': '71.3',
           'dp': 1,
           'guard': ['71.3%'],
           'scale': 1},
 'R6#20': {'t': 'out',
           'mat': 'S2',
           'expect': [['stacked(p, ds)', '72.0000'], ['stacked(p, ds[::-1])', '72.0000']],
           'asserts': []},
 'R6#21': {'t': 'absent', 'tokens': ['twice as fast', 'timeit', 'perf_counter', 'benchmark']},
 'R6#22': {'t': 'absent', 'tokens': ['discount_cap']},
 'R6#23': {'t': 'out',
           'mat': 'S3',
           'expect': [['tier(20000)', "'platinum'"], ['tier(250000)', "'platinum'"]],
           'asserts': []},
 'R6#24': {'t': 'out_general',
           'mat': 'S1',
           'expect': [['vat_on_total(basket)', '0.25'], ['vat_per_line(basket)', '0.24']],
           'asserts': [],
           'counter': "vat_on_total([Decimal('0.53')] * 10) - vat_per_line([Decimal('0.53')] * 10) > Decimal('0.01')",
           'scope_words': ['never']},
 'R6#25': {'t': 'out', 'mat': 'S4', 'expect': [['sum(shares) == 1', 'True']], 'asserts': []},
 'R6#26': {'t': 'metric',
           'mats': ['L1'],
           'metric': 'revenue',
           'period': '2024',
           'claimed': '213533.03',
           'dp': 2,
           'guard': ['213,533.03'],
           'scale': 1},
 'R6#27': {'t': 'metric_general',
           'mats': ['L1'],
           'narrow': [{'t': 'metric',
                       'mats': ['L1'],
                       'metric': 'gm',
                       'period': '2024',
                       'claimed': '48.1',
                       'dp': 1,
                       'guard': [],
                       'scale': 1}],
           'metric': 'gm',
           'universe': ['2024-01',
                        '2024-02',
                        '2024-03',
                        '2024-04',
                        '2024-05',
                        '2024-06',
                        '2024-07',
                        '2024-08',
                        '2024-09',
                        '2024-10',
                        '2024-11',
                        '2024-12'],
           'op': '>',
           'threshold': '40',
           'scope_words': ['every month']},
 'R6#28': {'t': 'metric',
           'mats': ['L1', 'L2'],
           'metric': 'growth',
           'period': '2024',
           'claimed': '39',
           'dp': 0,
           'guard': [],
           'scale': 1},
 'R6#29': {'t': 'metric',
           'mats': ['L1'],
           'metric': 'avg_ticket',
           'period': '2024',
           'claimed': '35588.84',
           'dp': 2,
           'guard': ['35,588.84'],
           'scale': 1},
 'R6#30': {'t': 'metric',
           'mats': ['L1', 'L2'],
           'metric': 'gm',
           'period': '2023',
           'claimed': '45.9',
           'dp': 1,
           'guard': [],
           'scale': 1}}


def main():
    reps = load_reports()
    with open(LABELS, encoding="utf-8") as fh:
        labels = json.load(fh)
    problems = []
    derived = {}
    for rid, rep in sorted(reps.items()):
        for mid, mat in rep["materials"].items():
            try:
                if mat["kind"] == "python":
                    check_run_log(mat)
                    first = run_snippet(mat["snippet"])
                    _RUN.pop(mat["snippet"])
                    if run_snippet(mat["snippet"]) != first:
                        raise OracleError("nondeterministic output")
                elif mat["kind"] == "ledger":
                    ledger_rows([mat])
                else:
                    raise OracleError("unknown kind")
            except Exception as e:
                problems.append(f"{rid}/{mid}: integrity: {e}")
        if [c["n"] for c in rep["claims"]] != list(range(1, 31)):
            problems.append(f"{rid}: claims are not numbered 1..30")
    claim_ids = set()
    for rid, rep in sorted(reps.items()):
        for c in rep["claims"]:
            cid = f"{rid}#{c['n']}"
            claim_ids.add(cid)
            for ref in c.get("refs", []):
                if ref not in rep["materials"]:
                    problems.append(f"{cid}: ref {ref} missing")
            if cid not in SPECS:
                problems.append(f"{cid}: no spec")
                continue
            try:
                got = derive(rep, c, SPECS[cid])
            except Exception as e:
                problems.append(f"{cid}: {type(e).__name__}: {e}")
                continue
            derived[cid] = got
            lab = labels.get(cid, {})
            if got != lab.get("category"):
                problems.append(f"{cid}: oracle={got} label={lab.get('category')}")
            want_action = {"valid": "state_as_written", "false": "withhold", "exaggerated": "narrow_or_withhold",
                           "incomplete": "withhold"}.get(lab.get("category"))
            if lab.get("correct_action") != want_action:
                problems.append(f"{cid}: correct_action inconsistent with category")
    if set(labels) != claim_ids:
        problems.append(f"label ids differ from claim ids: {sorted(set(labels) ^ claim_ids)[:10]}")
    if set(SPECS) != claim_ids:
        problems.append(f"spec ids differ from claim ids: {sorted(set(SPECS) ^ claim_ids)[:10]}")
    counts = {}
    for cat in derived.values():
        counts[cat] = counts.get(cat, 0) + 1
    print(f"interpreter: {LOCAL_VERSION} ({platform.platform()})")
    print(f"reports: {len(reps)}  claims re-derived: {len(derived)}  counts: {dict(sorted(counts.items()))}")
    for rid in sorted(reps):
        per = {}
        for cid, cat in derived.items():
            if cid.split("#")[0] == rid:
                per[cat] = per.get(cat, 0) + 1
        print(f"  {rid}: {dict(sorted(per.items()))}")
    if problems:
        print(f"FAIL: {len(problems)} problem(s)")
        for p in problems:
            print("  " + p)
        return 1
    print("OK: every label re-derived (" + str(len(derived)) + "/" + str(len(claim_ids)) + ")")
    return 0


if __name__ == "__main__":
    sys.exit(main())
