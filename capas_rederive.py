# SPDX-License-Identifier: Apache-2.0
"""Engine-side re-derivation (2026-10-15, after the AI vs AI+CAPAS experiment): CAPAS checks the evidence itself instead
of comparing fields an AI transcribed.

- python_run(): runs a Python snippet in a child interpreter and returns what it printed. ARBITRARY CODE EXECUTION:
  it runs only when the caller opts in (decide_external_claim(..., rederive=True) or CAPAS_REDERIVE_EXEC=1 in a local
  process). The hosted API never enables it. Limits: isolated mode (-I), empty temp working directory, minimal
  environment, no stdin, CPU/memory/file-size limits, wall timeout. This is a guard for honest inputs on the
  caller's own machine, not a sandbox for hostile code.
- ledger_metric(): recomputes a financial metric from raw rows (no code execution; safe on the hosted API). The metric
  is an arithmetic expression over aggregates of the rows, e.g. "(sum(revenue) - sum(cogs)) / sum(revenue)",
  "sum(revenue) / sum(revenue, prev) - 1", "sum(revenue) / distinct(customer, revenue)". It also checks that every
  month of the period has rows.
"""
from __future__ import annotations

import ast, csv, io, os, re, subprocess, sys, tempfile
from typing import Any

EXEC_ENV = "CAPAS_REDERIVE_EXEC"
TIMEOUT_S = 5


def exec_enabled(flag: bool | None = None) -> bool:
    return bool(flag) if flag is not None else os.environ.get(EXEC_ENV) == "1"


def runtime_version() -> str:
    return "%d.%d.%d" % sys.version_info[:3]


def version_matches(declared: str, actual: str | None = None) -> bool:
    """'3.14' matches 3.14.x; '3.14.5' must match exactly; '3' matches any 3.x. Empty never matches."""
    actual = actual or runtime_version()
    d = [p for p in re.findall(r"\d+", str(declared or ""))][:3]
    return bool(d) and actual.split(".")[:len(d)] == d


def _limits() -> None:   # runs in the child before exec (POSIX only)
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_CPU, (TIMEOUT_S, TIMEOUT_S))
        resource.setrlimit(resource.RLIMIT_FSIZE, (1 << 20, 1 << 20))
        try:
            resource.setrlimit(resource.RLIMIT_AS, (1 << 30, 1 << 30))
        except (ValueError, OSError):
            pass
    except Exception:
        pass


def normalize_output(text: str) -> str:
    lines = [ln.rstrip() for ln in str(text).replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines).strip("\n")


def python_run(snippet: str) -> dict[str, Any]:
    """Run the snippet; `observed` is stdout, plus the exception line (e.g. "KeyError: 'b'") when it raised."""
    with tempfile.TemporaryDirectory(prefix="capas_rederive_") as d:
        path = os.path.join(d, "snippet.py")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(snippet)
        env = {"PATH": "/usr/bin:/bin", "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1", "LC_ALL": "C.UTF-8"}
        try:
            p = subprocess.run([sys.executable, "-I", "snippet.py"], cwd=d, env=env, stdin=subprocess.DEVNULL,
                               capture_output=True, text=True, timeout=TIMEOUT_S,
                               preexec_fn=_limits if os.name == "posix" else None)
        except subprocess.TimeoutExpired:
            return {"ran": False, "timed_out": True, "runtime_version": runtime_version()}
    out = normalize_output(p.stdout)
    exc = ""
    if p.returncode != 0:
        tail = [ln for ln in p.stderr.strip().splitlines() if ln.strip()]
        exc = tail[-1].strip() if tail else f"exit status {p.returncode}"
    observed = "\n".join(x for x in (out, exc) if x)
    return {"ran": True, "timed_out": False, "runtime_version": runtime_version(), "returncode": p.returncode,
            "stdout": out, "exception": exc, "observed": observed}


def outputs_match(expected: str, observed: str) -> bool:
    return normalize_output(expected) == normalize_output(observed)


# ------------------------------------------------------------------ ledger

_FUNCS = {"sum", "count", "distinct"}
_PERIOD = re.compile(r"^(\d{4})(?:-(Q[1-4]|\d{2}))?$")


def period_months(period: str) -> list[str]:
    m = _PERIOD.match(str(period or "").strip())
    if not m:
        raise ValueError(f"period {period!r} is not YYYY, YYYY-Qn or YYYY-MM")
    y, part = int(m.group(1)), m.group(2)
    if part is None:
        months = range(1, 13)
    elif part.startswith("Q"):
        q = int(part[1]); months = range(3 * q - 2, 3 * q + 1)
    else:
        months = [int(part)]
        if not 1 <= months[0] <= 12:
            raise ValueError(f"month out of range in {period!r}")
    return [f"{y:04d}-{mm:02d}" for mm in months]


def previous_period(period: str) -> str:
    m = _PERIOD.match(period.strip()); y, part = int(m.group(1)), m.group(2)
    if part is None:
        return f"{y - 1}"
    if part.startswith("Q"):
        q = int(part[1]); return f"{y - 1}-Q4" if q == 1 else f"{y}-Q{q - 1}"
    mm = int(part); return f"{y - 1}-12" if mm == 1 else f"{y}-{mm - 1:02d}"


def _rows(rows_csv: str) -> list[dict[str, str]]:
    rd = csv.DictReader(io.StringIO(str(rows_csv).strip()))
    if not rd.fieldnames or not {"date", "account", "amount"} <= {f.strip() for f in rd.fieldnames}:
        raise ValueError("rows_csv needs the columns date, account, amount")
    return [{k.strip(): (v or "").strip() for k, v in r.items() if k} for r in rd]


def ledger_metric(rows_csv: str, expression: str, period: str) -> dict[str, Any]:
    """Evaluate `expression` over the rows dated in `period` (and `prev`, the previous period, when it is referenced).
    Returns {value, coverage_ok, missing_months, periods_used}; raises ValueError on a malformed spec."""
    rows = _rows(rows_csv)
    tree = ast.parse(str(expression), mode="eval")
    used = {period}

    def months_of(p):
        return set(period_months(p))

    def select(account, p):
        ms = months_of(p)
        return [r for r in rows if r.get("account") == account and r.get("date", "")[:7] in ms]

    def ev(n):
        if isinstance(n, ast.Expression):
            return ev(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool):
            return float(n.value)
        if isinstance(n, ast.BinOp) and isinstance(n.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
            a, b = ev(n.left), ev(n.right)
            if isinstance(n.op, ast.Div):
                if b == 0:
                    raise ValueError("division by zero in the metric")
                return a / b
            return a + b if isinstance(n.op, ast.Add) else a - b if isinstance(n.op, ast.Sub) else a * b
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub):
            return -ev(n.operand)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in _FUNCS and not n.keywords:
            names = [a.id if isinstance(a, ast.Name) else a.value if isinstance(a, ast.Constant) and isinstance(a.value, str) else None
                     for a in n.args]
            if None in names:
                raise ValueError("aggregate arguments must be names")
            p = period
            if names and names[-1] == "prev":
                p = previous_period(period); names = names[:-1]; used.add(p)
            if n.func.id == "distinct":
                if len(names) != 2:
                    raise ValueError("distinct(column, account[, prev])")
                col, acct = names
                return float(len({r.get(col, "") for r in select(acct, p) if r.get(col, "")}))
            if len(names) != 1:
                raise ValueError(f"{n.func.id}(account[, prev])")
            sel = select(names[0], p)
            if n.func.id == "count":
                return float(len(sel))
            try:
                return sum(float(r["amount"]) for r in sel)
            except ValueError as e:
                raise ValueError(f"non-numeric amount: {e}") from None
        raise ValueError(f"unsupported element in the metric: {ast.dump(n)[:60]}")

    value = ev(tree)
    have = {r.get("date", "")[:7] for r in rows}
    missing = sorted(m for p in used for m in period_months(p) if m not in have)
    return {"value": value, "coverage_ok": not missing, "missing_months": missing, "periods_used": sorted(used)}
