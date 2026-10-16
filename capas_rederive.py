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
  "sum(revenue) / sum(revenue, prev) - 1", "sum(revenue) / distinct(customer, revenue)",
  "sum(revenue, source=MX)". It checks that every month of the period has rows IN EVERY SOURCE the metric uses
  (2026-10-15, experiment v2: two entities merged into one CSV hid one entity's missing month).
- load_ref(): reads an original source file by {path, sha256} under CAPAS_SOURCE_ROOT, so the engine checks the
  material itself and not an AI's transcription of it (experiment v2). No root, a path outside it, a missing file or
  a hash mismatch -> an error, never a guess.
- assertion_segments(): the separate assertions in a claim text, so a compound claim needs one check per assertion.
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


_ENTITY_COLUMNS = ("source", "entity", "company", "country", "subsidiary", "business_unit")


def _rows(rows_csv: str, source: str | None = None) -> list[dict[str, str]]:
    rd = csv.DictReader(io.StringIO(str(rows_csv).strip()))
    if not rd.fieldnames or not {"date", "account", "amount"} <= {f.strip() for f in rd.fieldnames}:
        raise ValueError("rows_csv needs the columns date, account, amount")
    out = []
    for r in rd:
        row = {k.strip(): (v or "").strip() for k, v in r.items() if k}
        # the source of a row: the declared source name, else an entity-like column, else one source
        row["__source"] = source or next((row[c] for c in _ENTITY_COLUMNS if row.get(c)), "") or "main"
        out.append(row)
    return out


def source_rows(sources: list[tuple[str, str]]) -> list[dict[str, str]]:
    """[(name, rows_csv)] -> all rows tagged with their source (a single unnamed CSV may carry an entity column)."""
    rows: list[dict[str, str]] = []
    for name, text in sources:
        rows.extend(_rows(text, name or None))
    return rows


def load_ref(ref: Any) -> tuple[str | None, str | None]:
    """{path, sha256} under CAPAS_SOURCE_ROOT -> (text, None) or (None, error)."""
    import hashlib
    import capas_plan3
    if not isinstance(ref, dict) or not isinstance(ref.get("path"), str) or not isinstance(ref.get("sha256"), str):
        return None, "a source reference needs path and sha256"
    root = capas_plan3._root()
    if root is None:
        return None, "this engine has no CAPAS_SOURCE_ROOT, so it cannot read the original file"
    full = capas_plan3._safe(root, ref["path"])
    if full is None or not full.is_file():
        return None, f"source file not found under CAPAS_SOURCE_ROOT: {ref['path']}"
    data = full.read_bytes()
    if hashlib.sha256(data).hexdigest() != ref["sha256"].lower().removeprefix("sha256:"):
        return None, f"sha256 of {ref['path']} does not match the reference"
    return data.decode("utf-8"), None


def ledger_metric(rows_csv: Any, expression: str, period: str) -> dict[str, Any]:
    """Evaluate `expression` over the rows dated in `period` (and `prev`, the previous period, when it is referenced).
    rows_csv is a CSV string or a list of already-tagged rows (source_rows). Returns {value, coverage_ok,
    missing_months (as "source:YYYY-MM" when there are several sources), periods_used, sources_used}."""
    rows = rows_csv if isinstance(rows_csv, list) else _rows(rows_csv)
    tree = ast.parse(str(expression), mode="eval")
    used = {period}
    touched: dict[str, set[str]] = {}          # source ("*" = every source) -> periods it was read for

    def months_of(p):
        return set(period_months(p))

    def select(account, p, src=None):
        ms = months_of(p)
        touched.setdefault(src or "*", set()).add(p)
        return [r for r in rows if r.get("account") == account and r.get("date", "")[:7] in ms
                and (src is None or r.get("__source") == src)]

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
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in _FUNCS and \
                all(k.arg == "source" for k in n.keywords):
            names = [a.id if isinstance(a, ast.Name) else a.value if isinstance(a, ast.Constant) and isinstance(a.value, str) else None
                     for a in n.args]
            if None in names:
                raise ValueError("aggregate arguments must be names")
            src = None
            for k in n.keywords:
                v = k.value
                src = v.id if isinstance(v, ast.Name) else v.value if isinstance(v, ast.Constant) and isinstance(v.value, str) else None
                if src is None:
                    raise ValueError("source= must be a name")
            p = period
            if names and names[-1] == "prev":
                p = previous_period(period); names = names[:-1]; used.add(p)
            if n.func.id == "distinct":
                if len(names) != 2:
                    raise ValueError("distinct(column, account[, prev])")
                col, acct = names
                return float(len({r.get(col, "") for r in select(acct, p, src) if r.get(col, "")}))
            if len(names) != 1:
                raise ValueError(f"{n.func.id}(account[, prev][, source=NAME])")
            sel = select(names[0], p, src)
            if n.func.id == "count":
                return float(len(sel))
            try:
                return sum(float(r["amount"]) for r in sel)
            except ValueError as e:
                raise ValueError(f"non-numeric amount: {e}") from None
        raise ValueError(f"unsupported element in the metric: {ast.dump(n)[:60]}")

    value = ev(tree)
    all_sources = sorted({r.get("__source", "main") for r in rows}) or ["main"]
    many = len(all_sources) > 1
    missing: list[str] = []
    for src, periods in touched.items():
        for s_name in (all_sources if src == "*" else [src]):
            have = {r.get("date", "")[:7] for r in rows if r.get("__source", "main") == s_name}
            for p in periods:
                missing += [f"{s_name}:{m}" if many else m for m in period_months(p) if m not in have]
    missing = sorted(set(missing))
    return {"value": value, "coverage_ok": not missing, "missing_months": missing, "periods_used": sorted(used),
            "sources_used": all_sources}


_OPS = {"==", "<", "<=", ">", ">="}


def ledger_check(rows: list[dict[str, str]], check: dict[str, Any], default_period: str) -> dict[str, Any]:
    """One extra assertion of a compound claim: {metric, op, value, tolerance?, period?}."""
    op = check.get("op", "==")
    if op not in _OPS or not isinstance(check.get("value"), (int, float)) or isinstance(check.get("value"), bool):
        raise ValueError("a ledger check needs metric, op (==, <, <=, >, >=) and a numeric value")
    m = ledger_metric(rows, str(check.get("metric", "")), str(check.get("period") or default_period))
    v, target, tol = m["value"], float(check["value"]), float(check.get("tolerance") or 0.0)
    ok = {"==": abs(v - target) <= tol, "<": v < target, "<=": v <= target, ">": v > target, ">=": v >= target}[op]
    return {**m, "op": op, "target": target, "passed": ok}


_VERB = re.compile(r"\b(grew|grow|grows|rose|rise|rises|fell|fall|falls|declined|declines|increased|increases|decreased|"
                   r"decreases|dropped|drops|was|were|is|are|reached|exceeded|exceeds|stayed|stays|remained|remains|beat|"
                   r"missed|totall?ed|averaged|came in|creci\w*|cay\w+|subi\w+|baj\w+|fue|fueron|es|son|alcanz\w+|super\w+)\b",
                   re.I)


def assertion_segments(text: str) -> list[str]:
    """The separate assertions of a claim: clauses joined by and/while/but/whereas/; that each carry a verb."""
    # one alternation, no adjacent quantified whitespace (CodeQL polynomial-redos); pieces are stripped afterwards
    parts = re.split(r";|\b(?:and|while|whereas|but|y|mientras|pero)\b", str(text or "")[:4000], flags=re.I)
    return [p.strip(" ,") for p in parts if _VERB.search(p)]
