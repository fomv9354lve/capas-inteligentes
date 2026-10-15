#!/usr/bin/env python3
"""Builds cases/C001..C100.json, oracle/labels.json and oracle/checks.json.

Run logs are produced by executing each snippet (python3; for version-mismatch cases the
real /opt/homebrew/bin/python3.13 or /usr/bin/python3). Ledger figures are computed with
the oracle's own metric code. Shuffled with SEED so the case id carries no category.
"""
import calendar
import json
import os
import random
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import oracle as O  # noqa: E402

SEED = 20261015
CASES = os.path.join(os.path.dirname(HERE), "cases")
PY_OTHER = {"3.13": "/opt/homebrew/bin/python3.13", "3.9": "/usr/bin/python3"}

# ============================================================== python_behavior

def P(key, cat, snippet, claim, pred, scope="run", why="", supported="", claimed_version=None,
      marker=None, counter_code=None, counter_pred=None, log="real", alt_snippet=None,
      other_py=None, notes=""):
    return dict(key=key, cat=cat, snippet=snippet, claim=claim, pred=pred, scope=scope, why=why,
                supported=supported, claimed_version=claimed_version, marker=marker,
                counter_code=counter_code, counter_pred=counter_pred, log=log,
                alt_snippet=alt_snippet, other_py=other_py, notes=notes)


PY = [
    # ---------------- valid
    P("pv_sort_stable", "valid",
      'records = [("b", 2), ("a", 1), ("c", 2), ("d", 1)]\nprint(sorted(records, key=lambda r: r[1]))\n',
      "In this snippet, sorting by the second field keeps tied records in their original relative order: ('a', 1) before ('d', 1) and ('b', 2) before ('c', 2).",
      "lines == [\"[('a', 1), ('d', 1), ('b', 2), ('c', 2)]\"]",
      why="log output matches the claimed order exactly"),
    P("pv_round_half_even", "valid", "print(round(2.5), round(3.5), round(-2.5))\n",
      "On the interpreter in the log, round(2.5) returns 2, round(3.5) returns 4 and round(-2.5) returns -2.",
      "lines == ['2 4 -2']", why="log prints '2 4 -2'"),
    P("pv_float_sum", "valid", "total = 0.1 + 0.2\nprint(total == 0.3)\nprint(total)\n",
      "The snippet shows that 0.1 + 0.2 does not compare equal to 0.3; the sum prints as 0.30000000000000004.",
      "lines == ['False', '0.30000000000000004']", why="log prints False and 0.30000000000000004"),
    P("pv_floordiv", "valid", "print(-7 // 2, int(-7 / 2), -7 % 2)\n",
      "Here -7 // 2 evaluates to -4 while int(-7 / 2) evaluates to -3, and -7 % 2 is 1.",
      "lines == ['-4 -3 1']", why="log prints '-4 -3 1'"),
    P("pv_split_empty", "valid", 'parts = "a,b,,c,".split(",")\nprint(len(parts), parts)\n',
      "Splitting 'a,b,,c,' on commas in this snippet returns five elements, two of which are empty strings.",
      "lines == [\"5 ['a', 'b', '', 'c', '']\"]", why="log shows 5 elements with two ''"),
    P("pv_mutable_default", "valid",
      "def add(item, bucket=[]):\n    bucket.append(item)\n    return bucket\n\nprint(add(1))\nprint(add(2))\n",
      "In this snippet the second call to add() returns [1, 2], because both calls append to the same default list.",
      "lines == ['[1]', '[1, 2]']", why="log prints [1] then [1, 2]"),
    P("pv_generator_twice", "valid", "squares = (n * n for n in range(4))\nprint(sum(squares))\nprint(sum(squares))\n",
      "Summing the same generator expression twice in this snippet gives 14 the first time and 0 the second time.",
      "lines == ['14', '0']", why="log prints 14 then 0"),
    P("pv_dict_order_314", "valid", 'd = {}\nd["z"] = 1\nd["a"] = 2\nd["m"] = 3\nprint(list(d))\n',
      "On Python 3.14.5, the interpreter in the log, list(d) returns the keys in insertion order: ['z', 'a', 'm'].",
      "lines == [\"['z', 'a', 'm']\"]", claimed_version="3.14.5",
      why="log is from 3.14.5 and prints ['z', 'a', 'm']"),
    P("pv_leap_day", "valid",
      "from datetime import date, timedelta\n\nprint(date(2024, 2, 28) + timedelta(days=1))\nprint((date(2025, 3, 1) - date(2025, 2, 1)).days)\n",
      "The snippet shows that one day after 2024-02-28 is 2024-02-29, and that February 2025 has 28 days.",
      "lines == ['2024-02-29', '28']", why="log prints 2024-02-29 and 28"),
    P("pv_regex_greedy", "valid",
      'import re\n\ntext = "<a><b>"\nprint(re.findall(r"<.+?>", text))\nprint(re.findall(r"<.+>", text))\n',
      "In this run the non-greedy pattern returns two tags, ['<a>', '<b>'], while the greedy pattern returns one match, ['<a><b>'].",
      "lines == [\"['<a>', '<b>']\", \"['<a><b>']\"]", why="log shows both results as claimed"),
    P("pv_keyerror", "valid", 'd = {"a": 1}\nprint(d.get("b"))\nprint(d["b"])\n',
      "The snippet prints None for d.get('b') and then stops with KeyError: 'b' on d['b'].",
      "lines[0] == 'None' and lines[-1] == \"KeyError: 'b'\"", why="log prints None then a KeyError: 'b' traceback"),
    P("pv_strip_chain", "valid", 'print("  Hello World  ".strip().lower().replace("o", "0"))\n',
      "The snippet prints 'hell0 w0rld' with no surrounding spaces.",
      "lines == ['hell0 w0rld']", why="log prints hell0 w0rld"),
    P("pv_aliasing", "valid", "grid = [[0] * 2] * 2\ngrid[0][0] = 9\nprint(grid)\n",
      "In this snippet, setting grid[0][0] = 9 also changes grid[1][0], so it prints [[9, 0], [9, 0]].",
      "lines == ['[[9, 0], [9, 0]]']", why="log prints [[9, 0], [9, 0]]"),
    # ---------------- false
    P("pf_round_2675", "false", "print(round(2.675, 2))\n",
      "The snippet prints 2.68 for round(2.675, 2).", "lines == ['2.68']",
      why="log prints 2.67", supported="The snippet prints 2.67 for round(2.675, 2)."),
    P("pf_sort_case", "false", 'print(sorted(["banana", "apple", "Cherry"]))\n',
      "The snippet's output lists the fruits alphabetically ignoring case: ['apple', 'banana', 'Cherry'].",
      "lines == [\"['apple', 'banana', 'Cherry']\"]",
      why="log prints ['Cherry', 'apple', 'banana'] (uppercase sorts first)",
      supported="The snippet prints ['Cherry', 'apple', 'banana']."),
    P("pf_true_div", "false", "print(7 / 2, 7 // 2, type(7 / 2).__name__)\n",
      "In this run 7 / 2 evaluates to the integer 3, the same as 7 // 2.",
      "lines[0].split()[0] == '3'", why="log prints 3.5 3 float",
      supported="7 / 2 evaluates to the float 3.5; 7 // 2 evaluates to 3."),
    P("pf_sort_none", "false", "nums = [3, 1, 2]\nresult = nums.sort()\nprint(result, nums)\n",
      "The snippet prints [1, 2, 3] for result, because nums.sort() returns the sorted list.",
      "lines[0].startswith('[1, 2, 3]')", why="log prints 'None [1, 2, 3]'",
      supported="result is None; nums is sorted in place to [1, 2, 3]."),
    P("pf_replace_count", "false", 'print("banana".replace("a", "o", 2))\n',
      "The log shows 'bonono': the count argument of 2 still lets replace() change every 'a'.",
      "lines == ['bonono']", why="log prints bonona (only two replacements)",
      supported="The snippet prints 'bonona'; only the first two 'a' are replaced."),
    P("pf_int_float_str", "false", 'print(int("3.0"))\n',
      "int('3.0') returns 3 in this snippet.", "lines == ['3']",
      why="log shows ValueError: invalid literal for int() with base 10: '3.0'",
      supported="int('3.0') raises ValueError in this snippet."),
    P("pf_gen_return", "false", "def gen():\n    yield 1\n    return 2\n\ng = gen()\nprint(list(g))\n",
      "list(gen()) in this snippet produces [1, 2], including the value given in the return statement.",
      "lines == ['[1, 2]']", why="log prints [1]",
      supported="list(gen()) produces [1]; the return value is not yielded."),
    P("pf_replace_month", "false", "from datetime import datetime\n\nprint(datetime(2026, 1, 31).replace(month=2))\n",
      "In this snippet replace(month=2) on 2026-01-31 clamps the date to 2026-02-28.",
      "'2026-02-28' in out", why="log shows ValueError: day is out of range for month",
      supported="replace(month=2) on 2026-01-31 raises ValueError in this snippet."),
    P("pf_re_match", "false", 'import re\n\nm = re.match(r"\\d+", "abc123")\nprint(m)\n',
      "re.match finds '123' in 'abc123' in this run.", "\"'123'\" in out",
      why="log prints None (match anchors at the start)", supported="re.match returns None for 'abc123' here."),
    P("pf_tuple_iadd", "false",
      't = ([1], 2)\ntry:\n    t[0] += [3]\nexcept TypeError as e:\n    print("TypeError:", e)\nprint(t)\n',
      "Because the augmented assignment raises TypeError, the tuple in this snippet is left unchanged and prints as ([1], 2).",
      "lines[-1] == '([1], 2)'", why="log prints the TypeError and then ([1, 3], 2): the list was mutated",
      supported="The TypeError is raised, but the inner list is still extended: t prints as ([1, 3], 2)."),
    P("pf_dict_merge", "false", 'a = {"x": 1, "y": 2}\nb = {"y": 3}\nprint(a | b)\nprint({**b, **a})\n',
      "Both merge expressions in the snippet end with y equal to 3.",
      "eval(lines[0])['y'] == 3 and eval(lines[1])['y'] == 3",
      why="log shows y=3 for a | b but y=2 for {**b, **a}",
      supported="a | b gives y = 3; {**b, **a} gives y = 2."),
    P("pf_format_half", "false", 'print(f"{0.5:.0f}", f"{1.5:.0f}", f"{2.5:.0f}")\n',
      "In this run f'{0.5:.0f}' renders as 1 and f'{2.5:.0f}' renders as 3, i.e. halves round up.",
      "lines == ['1 2 3']", why="log prints '0 2 2' (round half to even)",
      supported="The three values render as 0, 2 and 2."),
    # ---------------- exaggerated
    P("pe_dict_order_all", "exaggerated", 'd = {"z": 1, "a": 2, "m": 3}\nprint(list(d))\n',
      "Dictionaries preserve insertion order in every Python version, as this run shows.",
      "lines == [\"['z', 'a', 'm']\"]", scope="universal", marker=r"every Python version",
      why="one run on 3.14.5 cannot establish behaviour in every version (CPython <3.6 did not guarantee it)",
      supported="On Python 3.14.5 this dict lists its keys in insertion order."),
    P("pe_round_down", "exaggerated", "print(round(2.5), round(4.5))\n",
      "Python's round() always rounds .5 down, as round(2.5) and round(4.5) show here.",
      "lines == ['2 4']", scope="universal", marker=r"always",
      counter_code="print(round(3.5))\n", counter_pred="lines == ['4']",
      why="two inputs do not support 'always'; round(3.5) gives 4",
      supported="In this run round(2.5) is 2 and round(4.5) is 4."),
    P("pe_float_never_exact", "exaggerated", "print(0.1 + 0.2 == 0.3)\n",
      "Float addition in Python never gives an exact decimal result; this comparison proves it.",
      "lines == ['False']", scope="universal", marker=r"never",
      counter_code="print(0.5 + 0.25 == 0.75)\n", counter_pred="lines == ['True']",
      why="one comparison does not support 'never'; 0.5 + 0.25 == 0.75 is True",
      supported="0.1 + 0.2 does not compare equal to 0.3 in this run."),
    P("pe_floordiv_lower", "exaggerated", "print(-7 // 2, -7 / 2)\n",
      "// always returns a value strictly lower than true division, as -7 // 2 = -4 against -3.5 shows.",
      "lines == ['-4 -3.5']", scope="universal", marker=r"always",
      counter_code="print(6 // 2 < 6 / 2)\n", counter_pred="lines == ['False']",
      why="one input; for exact divisions (6 // 2 vs 6 / 2) the result is not strictly lower",
      supported="-7 // 2 is -4, below -7 / 2 = -3.5."),
    P("pe_split_never_empty", "exaggerated", 'print("a  b ".split())\n',
      "str.split() never returns empty strings, whatever separator is passed; see the output here.",
      "lines == [\"['a', 'b']\"]", scope="universal", marker=r"never .*whatever separator",
      counter_code='print("" in "a,,b".split(","))\n', counter_pred="lines == ['True']",
      why="the run uses no separator; with ',' empty strings appear",
      supported="split() with no argument drops the empty fields of 'a  b '."),
    P("pe_iter_twice", "exaggerated", "g = (x for x in [1, 2])\nprint(list(g), list(g))\n",
      "Any Python iterable yields nothing when it is iterated a second time, as this run shows.",
      "lines == ['[1, 2] []']", scope="universal", marker=r"Any Python iterable",
      counter_code="xs = [1, 2]\nprint(list(xs), list(xs))\n", counter_pred="lines == ['[1, 2] [1, 2]']",
      why="shown for a generator only; a list re-iterates fully",
      supported="This generator yields nothing on the second pass."),
    P("pe_defaults_leak", "exaggerated",
      'def tag(t, seen=[]):\n    seen.append(t)\n    return len(seen)\n\nprint(tag("a"), tag("b"))\n',
      "Every Python function with a default argument carries state between calls, just like tag() does here.",
      "lines == ['1 2']", scope="universal", marker=r"Every Python function",
      counter_code="def f(x=0):\n    x += 1\n    return x\n\nprint(f(), f())\n", counter_pred="lines == ['1 1']",
      why="only a mutable default that is mutated carries state; an int default does not",
      supported="tag()'s mutable default list carries state between calls."),
    P("pe_feb29", "exaggerated", "from datetime import date, timedelta\n\nprint(date(2028, 2, 28) + timedelta(days=1))\n",
      "Adding timedelta(days=1) to February 28 always lands on February 29, as this run shows.",
      "lines == ['2028-02-29']", scope="universal", marker=r"always",
      counter_code="from datetime import date, timedelta\n\nprint(date(2027, 2, 28) + timedelta(days=1))\n",
      counter_pred="lines == ['2027-03-01']",
      why="true only in leap years; 2027-02-28 + 1 day is 2027-03-01",
      supported="One day after 2028-02-28 is 2028-02-29."),
    P("pe_findall_strings", "exaggerated", 'import re\n\nprint(re.findall(r"\\d+", "a1b22c333"))\n',
      "re.findall returns a list of strings whatever the pattern, which this run confirms.",
      "lines == [\"['1', '22', '333']\"]", scope="universal", marker=r"whatever the pattern",
      counter_code='import re\n\nprint(type(re.findall(r"(a)(b)", "ab")[0]).__name__)\n', counter_pred="lines == ['tuple']",
      why="one group-free pattern; with two groups findall returns tuples",
      supported="For r'\\d+' on 'a1b22c333' findall returns ['1', '22', '333']."),
    P("pe_int_any_digits", "exaggerated", 'print(int(" 42 "), int("+7"), int("0010"))\n',
      "int() accepts any string that contains digits, as these three conversions show.",
      "lines == ['42 7 10']", scope="universal", marker=r"any string",
      counter_code='try:\n    int("4 2")\nexcept ValueError:\n    print("ValueError")\n', counter_pred="lines == ['ValueError']",
      why="three inputs; int('4 2') raises ValueError",
      supported="int() accepts ' 42 ', '+7' and '0010'."),
    P("pe_sorted_any", "exaggerated", 'print(sorted([3, 1, 2]), sorted(["b", "a"]))\n',
      "sorted() can order any Python list; both calls in this run succeed.",
      "lines == [\"[1, 2, 3] ['a', 'b']\"]", scope="universal", marker=r"any Python list",
      counter_code='try:\n    sorted([1, "a"])\nexcept TypeError:\n    print("TypeError")\n', counter_pred="lines == ['TypeError']",
      why="two homogeneous lists; a mixed int/str list raises TypeError",
      supported="sorted() orders these two homogeneous lists."),
    P("pe_removeprefix_all", "exaggerated", 'print("v1.2".removeprefix("v"))\n',
      "str.removeprefix works on every Python 3 release; the log confirms it.",
      "lines == ['1.2']", scope="universal", marker=r"every Python 3 release",
      why="one run on 3.14.5; removeprefix was added in 3.9",
      supported="On Python 3.14.5 'v1.2'.removeprefix('v') returns '1.2'."),
    # ---------------- incomplete
    P("pi_nolog_sorted_items", "incomplete", 'prices = {"b": 2, "a": 1}\nprint(sorted(prices.items(), key=lambda kv: kv[1]))\n',
      "This snippet prints [('a', 1), ('b', 2)].", "True", log="none",
      notes="Snippet pasted from the code review thread.", why="no run_log in the bundle"),
    P("pi_nolog_round1005", "incomplete", "print(round(1.005, 2))\n",
      "The snippet prints 1.01.", "True", log="none",
      notes="Helper used in the invoice rounding module.", why="no run_log in the bundle"),
    P("pi_nolog_median", "incomplete", "import statistics\n\nprint(statistics.median([1, 3, 2, 4]))\n",
      "The snippet prints 2.5, the mean of the two middle values.", "True", log="none",
      why="no run_log in the bundle"),
    P("pi_nolog_strptime", "incomplete", 'from datetime import datetime\n\nprint(datetime.strptime("2026-13-01", "%Y-%m-%d"))\n',
      "The snippet raises ValueError because month 13 does not exist.", "True", log="none",
      notes="Input validation check for the import job.", why="no run_log in the bundle"),
    P("pi_nolog_upper", "incomplete", 'print("straße".upper())\n',
      "The snippet prints 'STRASSE'.", "True", log="none", why="no run_log in the bundle"),
    P("pi_other_sortlen", "incomplete", 'words = ["pear", "fig", "apple", "kiwi"]\nprint(sorted(words, key=len))\n',
      "This snippet prints ['fig', 'kiwi', 'pear', 'apple'].", "True", log="other_snippet",
      alt_snippet='words = ["pear", "fig", "apple", "kiwi"]\nprint(sorted(sorted(words), key=len))\n',
      why="the run_log's cat shows different code (pre-sorted list) than the snippet"),
    P("pi_other_join", "incomplete", 'print(" ".join(reversed("abc")))\n',
      "The snippet prints 'c b a'.", "True", log="other_snippet",
      alt_snippet='print(" ".join(reversed(list("abc"))))\n',
      why="the run_log's cat shows different code than the snippet"),
    P("pi_other_fromkeys", "incomplete", 'tags = ["a", "b", "a", "c", "b"]\nprint(list(dict.fromkeys(tags)))\n',
      "The snippet removes the duplicates while keeping first-seen order and prints ['a', 'b', 'c'].", "True",
      log="other_snippet", alt_snippet='tags = ["a", "b", "c"]\nprint(list(dict.fromkeys(tags)))\n',
      why="the run_log's cat shows a list without duplicates, not the snippet"),
    P("pi_other_index", "incomplete", "items = [1, 2, 3]\nprint(items[3])\n",
      "The snippet fails with IndexError: list index out of range.", "True", log="other_snippet",
      alt_snippet="items = [1, 2, 3]\nprint(items[5])\n",
      why="the run_log's cat shows items[5], not items[3]"),
    P("pi_ver_313_format", "incomplete", 'print(f"{1234567:,}")\n',
      "On Python 3.14, which production runs, this snippet prints 1,234,567.", "True",
      log="other_version", other_py="3.13", claimed_version="3.14",
      why="claim is about 3.14; the only log is from Python 3.13"),
    P("pi_ver_39_bigint", "incomplete", 'print(len(str(int("1" * 5000))))\n',
      "On Python 3.14 this snippet prints 5000.", "True",
      log="other_version", other_py="3.9", claimed_version="3.14",
      why="claim is about 3.14; the only log is from Python 3.9 (3.11+ limits int/str conversion digits)"),
    P("pi_ver_39_utc", "incomplete", "from datetime import datetime, UTC\n\nprint(datetime(2026, 1, 1, tzinfo=UTC))\n",
      "On Python 3.14 the snippet prints 2026-01-01 00:00:00+00:00.", "True",
      log="other_version", other_py="3.9", claimed_version="3.14",
      why="claim is about 3.14; the only log is from Python 3.9, where the import fails"),
    P("pi_ver_313_sortkeys", "incomplete", 'import json\n\nprint(json.dumps({"b": 1, "a": 2}, sort_keys=True))\n',
      'Under Python 3.14.5 this snippet prints {"a": 2, "b": 1}.', "True",
      log="other_version", other_py="3.13", claimed_version="3.14.5",
      why="claim is about 3.14.5; the only log is from Python 3.13"),
]


def build_python(spec, cur_version_line):
    snip = spec["snippet"]
    if spec["log"] == "none":
        log = None
    elif spec["log"] == "real":
        log = O.format_log(cur_version_line, snip, O.run_snippet("python3", snip))
    elif spec["log"] == "other_snippet":
        alt = spec["alt_snippet"]
        log = O.format_log(cur_version_line, alt, O.run_snippet("python3", alt))
    elif spec["log"] == "other_version":
        py = PY_OTHER[spec["other_py"]]
        log = O.format_log(O.interp_version(py), snip, O.run_snippet(py, snip))
    bundle = {"snippet": snip, "run_log": log, "notes": spec["notes"]}
    check = {"pred": spec["pred"], "scope": spec["scope"]}
    if spec["claimed_version"]:
        check["claimed_version"] = spec["claimed_version"]
    if spec["scope"] == "universal":
        check["universal_marker"] = spec["marker"]
    if spec["counter_code"]:
        check["counter_code"] = spec["counter_code"]
        check["counter_pred"] = spec["counter_pred"]
    sup = spec["supported"]
    return dict(family="python_behavior", claim=spec["claim"], bundle=bundle, check=check,
                cat=spec["cat"], why=spec["why"], supported=sup)


# ============================================================== ledger_metric

DEF_REV = "revenue = sum(amount) over rows with account = 'revenue' dated within the period"
DEF_NET = ("net_revenue = sum(amount) over rows with account in ('revenue', 'refund') dated within the period "
           "(refund amounts are negative)")
DEF_MARGIN = ("gross_margin = (revenue - cogs) / revenue, where revenue = sum(amount) for account 'revenue' and "
              "cogs = sum(amount) for account 'cogs', rows dated within the period")
DEF_TICKET = ("average_ticket = sum(amount) / count(rows) over rows with account = 'revenue' dated within the period "
              "(one row = one order)")
DEF_OPEX = "opex = sum(amount) over rows with account = 'opex' dated within the period"
DEF_REFUND_RATE = ("refund_rate = -sum(amount where account = 'refund') / sum(amount where account = 'revenue'), "
                   "rows dated within the period")


def DEF_GROWTH(f, t):
    return (f"mom_growth = revenue({t}) / revenue({f}) - 1, where revenue(m) = sum(amount) for account 'revenue' "
            f"dated in month m")


def DEF_CHURN(f, last):
    return (f"logo_churn = (customers with a 'subscription' row in {f} and no 'subscription' row in {last}) / "
            f"(customers with a 'subscription' row in {f})")


def DEF_DSO(end, days):
    return (f"DSO = accounts_receivable balance / revenue x {days} days, where the balance is the "
            f"'accounts_receivable' row dated {end} and revenue = sum(amount) for account 'revenue' within the period")


MONTH_NAMES = {f"{i:02d}": calendar.month_name[i] for i in range(1, 13)}


def mname(m):
    y, mm = m.split("-")
    return f"{MONTH_NAMES[mm]} {y}"


def money(v):
    return f"${v:,.2f}"


def pct(v, d=1):
    return f"{v * 100:.{d}f}%"


class Gen:
    def __init__(self, key):
        self.r = random.Random(f"{SEED}-{key}")
        self.rows = []
        self.pool = [f"C-{n}" for n in self.r.sample(range(100, 999), 14)]

    def day(self, m, lo=1, hi=None):
        y, mm = map(int, m.split("-"))
        hi = hi or calendar.monthrange(y, mm)[1]
        return f"{m}-{self.r.randint(lo, hi):02d}"

    def add(self, d, acc, cust, amt):
        self.rows.append({"date": d, "account": acc, "customer": cust, "amount": round(amt, 2)})
        return round(amt, 2)

    def revenue(self, m, n, lo=800, hi=6000, dlo=1, dhi=None):
        out = []
        for _ in range(n):
            out.append(self.add(self.day(m, dlo, dhi), "revenue", self.r.choice(self.pool), self.r.uniform(lo, hi)))
        return out

    def cogs(self, m, ratio, dlo=1, dhi=None):
        rev = sum(r["amount"] for r in self.rows if r["account"] == "revenue" and r["date"].startswith(m))
        tot = rev * ratio
        a = round(tot * self.r.uniform(0.35, 0.65), 2)
        self.add(self.day(m, dlo, dhi), "cogs", "", a)
        self.add(self.day(m, dlo, dhi), "cogs", "", tot - a)

    def refunds(self, m, n, lo=60, hi=500):
        for _ in range(n):
            self.add(self.day(m), "refund", self.r.choice(self.pool), -self.r.uniform(lo, hi))

    def opex(self, m, n=2, lo=1500, hi=9000, dlo=1, dhi=None):
        for _ in range(n):
            self.add(self.day(m, dlo, dhi), "opex", "", self.r.uniform(lo, hi))

    def csv(self):
        rows = sorted(self.rows, key=lambda r: (r["date"], r["account"], r["customer"]))
        lines = ["date,account,customer,amount"]
        lines += [f"{r['date']},{r['account']},{r['customer']},{r['amount']:.2f}" for r in rows]
        return "\n".join(lines) + "\n"


def compute(spec, g, period):
    rows = O.parse_rows(g.csv())
    return O.compute_metric(spec, rows, O.period_months(period))


def export_note(a, z=None, extra=""):
    if isinstance(a, list):
        rng = "; ".join(f"{x} to {y}" for x, y in a)
    else:
        rng = f"{a} to {z}"
    return (f"Export range: {rng}. General-ledger export from the ERP." + (" " + extra if extra else "")).strip()


def full_range(period):
    p0, p1 = O.period_bounds(O.period_months(period))
    return str(p0), str(p1)


def L(key, cat, claim, period, definition, g, reported, tol, spec, claim_chk, scope, notes, why, supported=""):
    bundle = {"rows_csv": g.csv(), "metric_definition": definition, "period": period,
              "reported_value": reported, "tolerance": tol, "notes": notes}
    check = {"spec": spec, "claim": claim_chk, "scope": scope}
    return dict(key=key, family="ledger_metric", claim=claim, bundle=bundle, check=check, cat=cat,
                why=why, supported=supported)


PERIOD = {"kind": "period"}
Q1 = ["2026-01", "2026-02", "2026-03"]
Q2 = ["2026-04", "2026-05", "2026-06"]
Q3 = ["2026-07", "2026-08", "2026-09"]
ALL2026 = [f"2026-{i:02d}" for i in range(1, 13)]


def ledger_cases():
    out = []
    SUM_REV = {"metric": "sum", "accounts": ["revenue"]}
    SUM_NET = {"metric": "sum", "accounts": ["revenue", "refund"]}
    SUM_OPEX = {"metric": "sum", "accounts": ["opex"]}
    MARGIN = {"metric": "margin"}
    TICKET = {"metric": "avg_ticket", "accounts": ["revenue"]}

    def approx(v, tol):
        return {"op": "approx", "value": v, "tol": tol}

    # ------------------------------------------------ valid
    g = Gen("lv_rev_q1")
    for m in Q1:
        g.revenue(m, g.r.randint(5, 7)); g.cogs(m, 0.55); g.opex(m)
    v = compute(SUM_REV, g, "2026-Q1")
    out.append(L("lv_rev_q1", "valid", f"Revenue for 2026-Q1 was {money(v)}.", "2026-Q1", DEF_REV, g, v, 0.01,
                 SUM_REV, approx(v, 0.01), PERIOD, export_note(*full_range("2026-Q1")),
                 "recomputed Q1 revenue equals the claim; all three months present"))

    g = Gen("lv_net_feb")
    g.revenue("2026-02", 7); g.refunds("2026-02", 3); g.opex("2026-02")
    v = compute(SUM_NET, g, "2026-02")
    out.append(L("lv_net_feb", "valid", f"Net revenue for February 2026, after refunds, was {money(v)}.", "2026-02",
                 DEF_NET, g, v, 0.01, SUM_NET, approx(v, 0.01), PERIOD, export_note(*full_range("2026-02")),
                 "revenue plus negative refunds equals the claim"))

    g = Gen("lv_margin_q2")
    for m in Q2:
        g.revenue(m, 5); g.cogs(m, 0.58)
    v = compute(MARGIN, g, "2026-Q2")
    out.append(L("lv_margin_q2", "valid", f"Gross margin for 2026-Q2 was {pct(v)}.", "2026-Q2", DEF_MARGIN, g,
                 round(v, 4), 0.0005, MARGIN, approx(round(v, 3), 0.0005), PERIOD,
                 export_note(*full_range("2026-Q2")), "recomputed margin rounds to the claimed percentage"))

    g = Gen("lv_growth")
    g.revenue("2026-02", 5, 1000, 4000); g.revenue("2026-03", 7, 1000, 4000)
    sp = {"metric": "growth", "from": "2026-02", "to": "2026-03"}
    v = compute(sp, g, "2026-02..2026-03"); assert v > 0.01
    out.append(L("lv_growth", "valid", f"Revenue grew {pct(v)} from February to March 2026.", "2026-02..2026-03",
                 DEF_GROWTH("2026-02", "2026-03"), g, round(v, 4), 0.0005, sp, approx(round(v, 3), 0.0005), PERIOD,
                 export_note(*full_range("2026-02..2026-03")), "recomputed Feb->Mar growth matches"))

    g = Gen("lv_ticket_jan")
    g.revenue("2026-01", 8, 200, 2400); g.opex("2026-01")
    v = compute(TICKET, g, "2026-01")
    out.append(L("lv_ticket_jan", "valid", f"The average ticket in January 2026 was {money(v)}.", "2026-01",
                 DEF_TICKET, g, round(v, 2), 0.01, TICKET, approx(round(v, 2), 0.01), PERIOD,
                 export_note(*full_range("2026-01")), "sum/count of January revenue rows matches"))

    def churn_gen(key, n_cust, churned, new=2, last_hi=None):
        g = Gen(key)
        cust = g.pool[:n_cust]
        gone = sorted(g.r.sample(cust, churned))
        late = g.pool[n_cust:n_cust + new]
        for i, m in enumerate(Q1):
            if i == 0:
                active = list(cust)
            elif i == 1:  # half of the leavers still billed in February
                active = [c for c in cust if c not in gone] + gone[: len(gone) // 2] + late
            else:
                active = [c for c in cust if c not in gone] + late
            for c in active:
                g.add(g.day(m, 1, 28), "subscription", c, g.r.choice([49.0, 99.0, 149.0]))
        return g

    CH = {"metric": "churn"}
    g = churn_gen("lv_churn_q1", 10, 2)
    v = compute(CH, g, "2026-Q1")
    out.append(L("lv_churn_q1", "valid", f"Logo churn for 2026-Q1 was {pct(v)}.", "2026-Q1",
                 DEF_CHURN("2026-01", "2026-03"), g, round(v, 4), 0.0005, CH, approx(round(v, 3), 0.0005), PERIOD,
                 export_note(*full_range("2026-Q1")), "January cohort minus March subscribers gives the claimed rate"))

    g = Gen("lv_dso_q1")
    for m in Q1:
        g.revenue(m, 5, 2000, 9000)
    rev = sum(r["amount"] for r in g.rows)
    g.add("2026-03-31", "accounts_receivable", "", rev * 47.3 / 90)
    DSO = {"metric": "dso"}
    v = compute(DSO, g, "2026-Q1")
    out.append(L("lv_dso_q1", "valid", f"DSO for 2026-Q1 was {v:.1f} days.", "2026-Q1", DEF_DSO("2026-03-31", 90),
                 g, round(v, 1), 0.05, DSO, approx(round(v, 1), 0.05), PERIOD, export_note(*full_range("2026-Q1")),
                 "AR / revenue x 90 matches the claim"))

    g = Gen("lv_rev_q1_with_april")
    for m in Q1:
        g.revenue(m, 5); g.opex(m)
    g.revenue("2026-04", 2, dhi=5)
    v = compute(SUM_REV, g, "2026-Q1")
    out.append(L("lv_rev_q1_with_april", "valid", f"Revenue for 2026-Q1 was {money(v)}.", "2026-Q1", DEF_REV, g, v,
                 0.01, SUM_REV, approx(v, 0.01), PERIOD, export_note("2026-01-01", "2026-04-05"),
                 "reported Q1 revenue correctly excludes the April rows present in the export"))

    g = Gen("lv_margin_gt35_mar")
    g.revenue("2026-03", 6); g.cogs("2026-03", 0.6)
    v = compute(MARGIN, g, "2026-03"); assert v > 0.36
    out.append(L("lv_margin_gt35_mar", "valid", "Gross margin in March 2026 was above 35%.", "2026-03", DEF_MARGIN,
                 g, round(v, 4), None, MARGIN, {"op": "gt", "value": 0.35}, PERIOD,
                 export_note(*full_range("2026-03")), f"recomputed margin {v:.4f} > 0.35"))

    g = Gen("lv_opex_q3")
    for m in Q3:
        g.opex(m, 3); g.revenue(m, 3)
    v = compute(SUM_OPEX, g, "2026-Q3")
    out.append(L("lv_opex_q3", "valid", f"Operating expenses for 2026-Q3 totalled {money(v)}.", "2026-Q3", DEF_OPEX,
                 g, v, 0.01, SUM_OPEX, approx(v, 0.01), PERIOD, export_note(*full_range("2026-Q3")),
                 "sum of Q3 opex rows matches"))

    g = Gen("lv_growth_fall")
    g.revenue("2026-04", 7, 1000, 4000); g.revenue("2026-05", 5, 1000, 4000)
    sp = {"metric": "growth", "from": "2026-04", "to": "2026-05"}
    v = compute(sp, g, "2026-04..2026-05"); assert v < -0.01
    out.append(L("lv_growth_fall", "valid", f"Revenue fell {pct(-v)} from April to May 2026.", "2026-04..2026-05",
                 DEF_GROWTH("2026-04", "2026-05"), g, round(v, 4), 0.0005, sp, approx(round(v, 3), 0.0005), PERIOD,
                 export_note(*full_range("2026-04..2026-05")), "recomputed Apr->May change matches the claimed fall"))

    g = Gen("lv_ticket_refunds")
    g.revenue("2026-06", 7, 300, 2500); g.refunds("2026-06", 2)
    v = compute(TICKET, g, "2026-06")
    out.append(L("lv_ticket_refunds", "valid", f"The average ticket in June 2026 was {money(v)}.", "2026-06",
                 DEF_TICKET, g, round(v, 2), 0.01, TICKET, approx(round(v, 2), 0.01), PERIOD,
                 export_note(*full_range("2026-06")), "ticket over revenue rows only (refund rows correctly excluded)"))

    # ------------------------------------------------ false
    g = Gen("lf_rev_q1_april")
    for m in Q1:
        g.revenue(m, 5); g.opex(m)
    g.revenue("2026-04", 2, dhi=4)
    v = compute(SUM_REV, g, "2026-Q1")
    wrong = round(sum(r["amount"] for r in g.rows if r["account"] == "revenue"), 2)
    out.append(L("lf_rev_q1_april", "false", f"Revenue for 2026-Q1 was {money(wrong)}.", "2026-Q1", DEF_REV, g,
                 wrong, 0.01, SUM_REV, approx(wrong, 0.01), PERIOD, export_note("2026-01-01", "2026-04-04"),
                 "reported figure includes April rows outside the period",
                 f"Revenue for 2026-Q1 was {money(v)}."))

    g = Gen("lf_net_ignores_refunds")
    g.revenue("2026-04", 7); g.refunds("2026-04", 3)
    v = compute(SUM_NET, g, "2026-04")
    wrong = compute(SUM_REV, g, "2026-04")
    out.append(L("lf_net_ignores_refunds", "false", f"Net revenue for April 2026, after refunds, was {money(wrong)}.",
                 "2026-04", DEF_NET, g, wrong, 0.01, SUM_NET, approx(wrong, 0.01), PERIOD,
                 export_note(*full_range("2026-04")), "reported figure is gross revenue; refunds not netted",
                 f"Net revenue for April 2026 was {money(v)}."))

    g = Gen("lf_margin_markup")
    for m in Q1:
        g.revenue(m, 5); g.cogs(m, 0.62)
    v = compute(MARGIN, g, "2026-Q1")
    rows = O.parse_rows(g.csv())
    R = sum(r["amount"] for r in rows if r["account"] == "revenue"); C = sum(r["amount"] for r in rows if r["account"] == "cogs")
    wrong = (R - C) / C
    out.append(L("lf_margin_markup", "false", f"Gross margin for 2026-Q1 was {pct(wrong)}.", "2026-Q1", DEF_MARGIN, g,
                 round(wrong, 4), 0.0005, MARGIN, approx(round(wrong, 3), 0.0005), PERIOD,
                 export_note(*full_range("2026-Q1")), "reported value divides by cogs (markup), not revenue",
                 f"Gross margin for 2026-Q1 was {pct(v)}."))

    g = Gen("lf_growth_sign")
    g.revenue("2026-05", 7, 1000, 4000); g.revenue("2026-06", 5, 1000, 4000)
    sp = {"metric": "growth", "from": "2026-05", "to": "2026-06"}
    v = compute(sp, g, "2026-05..2026-06"); assert v < -0.01
    out.append(L("lf_growth_sign", "false", f"Revenue grew {pct(-v)} from May to June 2026.", "2026-05..2026-06",
                 DEF_GROWTH("2026-05", "2026-06"), g, round(-v, 4), 0.0005, sp, approx(round(-v, 3), 0.0005), PERIOD,
                 export_note(*full_range("2026-05..2026-06")), "revenue fell; the claim reports the change as growth",
                 f"Revenue fell {pct(-v)} from May to June 2026."))

    g = Gen("lf_ticket_customers")
    g.pool = g.pool[:4]
    g.revenue("2026-02", 9, 200, 2000)
    v = compute(TICKET, g, "2026-02")
    rows = [r for r in O.parse_rows(g.csv()) if r["account"] == "revenue"]
    wrong = sum(r["amount"] for r in rows) / len({r["customer"] for r in rows})
    out.append(L("lf_ticket_customers", "false", f"The average ticket in February 2026 was {money(wrong)}.", "2026-02",
                 DEF_TICKET, g, round(wrong, 2), 0.01, TICKET, approx(round(wrong, 2), 0.01), PERIOD,
                 export_note(*full_range("2026-02")), "reported figure divides by distinct customers, not orders",
                 f"The average ticket in February 2026 was {money(v)}."))

    g = churn_gen("lf_churn_enddenom", 12, 3, new=3)
    v = compute(CH, g, "2026-Q1")
    rows = O.parse_rows(g.csv())
    first = {r["customer"] for r in rows if O.ym(r["date"]) == "2026-01"}
    last = {r["customer"] for r in rows if O.ym(r["date"]) == "2026-03"}
    wrong = len(first - last) / len(last)
    assert abs(wrong - v) > 0.002
    out.append(L("lf_churn_enddenom", "false", f"Logo churn for 2026-Q1 was {pct(wrong)}.", "2026-Q1",
                 DEF_CHURN("2026-01", "2026-03"), g, round(wrong, 4), 0.0005, CH, approx(round(wrong, 3), 0.0005),
                 PERIOD, export_note(*full_range("2026-Q1")), "reported rate uses March customers as denominator",
                 f"Logo churn for 2026-Q1 was {pct(v)}."))

    g = Gen("lf_dso_365")
    for m in Q1:
        g.revenue(m, 5, 2000, 9000)
    rev = sum(r["amount"] for r in g.rows)
    g.add("2026-03-31", "accounts_receivable", "", rev * 12.0 / 90)
    v = compute(DSO, g, "2026-Q1")
    wrong = v / 90 * 365
    out.append(L("lf_dso_365", "false", f"DSO for 2026-Q1 was {wrong:.1f} days.", "2026-Q1", DEF_DSO("2026-03-31", 90),
                 g, round(wrong, 1), 0.05, DSO, approx(round(wrong, 1), 0.05), PERIOD,
                 export_note(*full_range("2026-Q1")), "reported DSO uses 365 days instead of the defined 90",
                 f"DSO for 2026-Q1 was {v:.1f} days."))

    g = Gen("lf_rev_transposed")
    for m in Q2:
        g.revenue(m, 6, 3000, 12000); g.opex(m)
    v = compute(SUM_REV, g, "2026-Q2")
    s = f"{v:.2f}"; ip, dp = s.split(".")
    i = next(k for k in range(1, len(ip) - 1) if ip[k] != ip[k + 1])
    ip2 = ip[:i] + ip[i + 1] + ip[i] + ip[i + 2:]
    wrong = float(ip2 + "." + dp)
    out.append(L("lf_rev_transposed", "false", f"Revenue for 2026-Q2 was {money(wrong)}.", "2026-Q2", DEF_REV, g,
                 wrong, 0.01, SUM_REV, approx(wrong, 0.01), PERIOD, export_note(*full_range("2026-Q2")),
                 "reported total has two digits transposed", f"Revenue for 2026-Q2 was {money(v)}."))

    g = Gen("lf_margin_threshold")
    for m in Q1:
        g.revenue(m, 5)
    rev = sum(r["amount"] for r in g.rows)
    g.add("2026-02-14", "cogs", "", rev * 0.604 * 0.5); g.add("2026-03-20", "cogs", "", rev * 0.604 * 0.5)
    g.add("2026-01-20", "opex", "", 4000)
    v = compute(MARGIN, g, "2026-Q1"); assert 0.39 < v < 0.40
    out.append(L("lf_margin_threshold", "false", "Gross margin for 2026-Q1 was above 40%.", "2026-Q1", DEF_MARGIN, g,
                 0.40, None, MARGIN, {"op": "gt", "value": 0.40}, PERIOD, export_note(*full_range("2026-Q1")),
                 f"recomputed margin is {v:.4f}, below 40%", f"Gross margin for 2026-Q1 was {pct(v)}."))

    g = Gen("lf_rev_deferred")
    g.revenue("2026-03", 6)
    for _ in range(2):
        g.add(g.day("2026-03"), "deferred_revenue", g.r.choice(g.pool), g.r.uniform(1500, 5000))
    v = compute(SUM_REV, g, "2026-03")
    wrong = compute({"metric": "sum", "accounts": ["revenue", "deferred_revenue"]}, g, "2026-03")
    out.append(L("lf_rev_deferred", "false", f"Revenue for March 2026 was {money(wrong)}.", "2026-03", DEF_REV, g,
                 wrong, 0.01, SUM_REV, approx(wrong, 0.01), PERIOD, export_note(*full_range("2026-03")),
                 "reported figure adds deferred_revenue rows the definition excludes",
                 f"Revenue for March 2026 was {money(v)}."))

    g = Gen("lf_opex_missing_row")
    for m in Q2:
        g.opex(m, 3); g.revenue(m, 2)
    v = compute(SUM_OPEX, g, "2026-Q2")
    dropped = [r for r in g.rows if r["account"] == "opex"][4]["amount"]
    wrong = round(v - dropped, 2)
    out.append(L("lf_opex_missing_row", "false", f"Operating expenses for 2026-Q2 totalled {money(wrong)}.", "2026-Q2",
                 DEF_OPEX, g, wrong, 0.01, SUM_OPEX, approx(wrong, 0.01), PERIOD, export_note(*full_range("2026-Q2")),
                 "reported total omits one opex row", f"Operating expenses for 2026-Q2 totalled {money(v)}."))

    g = Gen("lf_ticket_with_refunds")
    g.revenue("2026-05", 6, 300, 2500); g.refunds("2026-05", 3)
    v = compute(TICKET, g, "2026-05")
    rows = [r for r in O.parse_rows(g.csv()) if r["account"] in ("revenue", "refund")]
    wrong = sum(r["amount"] for r in rows) / len(rows)
    out.append(L("lf_ticket_with_refunds", "false", f"The average ticket in May 2026 was {money(wrong)}.", "2026-05",
                 DEF_TICKET, g, round(wrong, 2), 0.01, TICKET, approx(round(wrong, 2), 0.01), PERIOD,
                 export_note(*full_range("2026-05")), "reported figure counts refund rows as orders",
                 f"The average ticket in May 2026 was {money(v)}."))

    g = Gen("lf_growth_wrong_base")
    g.revenue("2026-01", 4, 1000, 3000); g.revenue("2026-02", 6, 1000, 3000); g.revenue("2026-03", 7, 1000, 3000)
    sp = {"metric": "growth", "from": "2026-02", "to": "2026-03"}
    v = compute(sp, g, "2026-02..2026-03")
    wrong = compute({"metric": "growth", "from": "2026-01", "to": "2026-03"}, g, "2026-01..2026-03")
    assert wrong > 0 and abs(wrong - v) > 0.01
    out.append(L("lf_growth_wrong_base", "false", f"Revenue grew {pct(wrong)} from February to March 2026.",
                 "2026-02..2026-03", DEF_GROWTH("2026-02", "2026-03"), g, round(wrong, 4), 0.0005, sp,
                 approx(round(wrong, 3), 0.0005), PERIOD, export_note("2026-01-01", "2026-03-31"),
                 "reported growth is measured against January, not February",
                 f"Revenue changed {pct(v)} from February to March 2026."))

    # ------------------------------------------------ exaggerated
    g = Gen("le_growth_since_launch")
    g.revenue("2026-02", 5, 1000, 4000); g.revenue("2026-03", 7, 1000, 4000)
    sp = {"metric": "growth", "from": "2026-02", "to": "2026-03"}
    v = compute(sp, g, "2026-02..2026-03"); assert v > 0.01
    out.append(L("le_growth_since_launch", "exaggerated",
                 f"Revenue has grown every month since launch, including {pct(v)} from February to March 2026.",
                 "2026-02..2026-03", DEF_GROWTH("2026-02", "2026-03"), g, round(v, 4), 0.0005, sp,
                 approx(round(v, 3), 0.0005), {"kind": "unbounded", "marker": "every month since launch"},
                 export_note(*full_range("2026-02..2026-03")), "rows support one month-over-month change only",
                 f"Revenue grew {pct(v)} from February to March 2026."))

    g = Gen("le_margin_will_stay")
    for m in Q1:
        g.revenue(m, 5); g.cogs(m, 0.575)
    v = compute(MARGIN, g, "2026-Q1"); assert v > 0.40
    out.append(L("le_margin_will_stay", "exaggerated",
                 f"Gross margin is structurally above 40%: it was {pct(v)} in 2026-Q1 and will stay above 40%.",
                 "2026-Q1", DEF_MARGIN, g, round(v, 4), 0.0005, MARGIN, approx(round(v, 3), 0.0005),
                 {"kind": "future", "marker": "will stay"}, export_note(*full_range("2026-Q1")),
                 "one quarter supports the Q1 figure, not a forecast", f"Gross margin was {pct(v)} in 2026-Q1."))

    g = Gen("le_rev_every_quarter")
    for m in Q1:
        g.revenue(m, 6, 3000, 9000)
    v = compute(SUM_REV, g, "2026-Q1")
    T = int(v // 10000) * 10000
    out.append(L("le_rev_every_quarter", "exaggerated", f"Revenue exceeded {money(T)} in every quarter of 2026.",
                 "2026-Q1", DEF_REV, g, v, 0.01, SUM_REV, {"op": "gt", "value": T},
                 {"kind": "months", "months": ALL2026, "marker": "every quarter of 2026"},
                 export_note(*full_range("2026-Q1")), "only Q1 rows are in the bundle",
                 f"Revenue exceeded {money(T)} in 2026-Q1 ({money(v)})."))

    g = Gen("le_ticket_consistent")
    g.revenue("2026-01", 8, 400, 1800)
    v = compute(TICKET, g, "2026-01")
    out.append(L("le_ticket_consistent", "exaggerated",
                 f"The average ticket is consistently {money(v)} in every month of 2026.", "2026-01", DEF_TICKET, g,
                 round(v, 2), 0.01, TICKET, approx(round(v, 2), 0.01),
                 {"kind": "months", "months": ALL2026, "marker": "every month of 2026"},
                 export_note(*full_range("2026-01")), "only January rows are in the bundle",
                 f"The average ticket in January 2026 was {money(v)}."))

    g = churn_gen("le_churn_never", 12, 1)
    v = compute(CH, g, "2026-Q1"); assert v < 0.10
    out.append(L("le_churn_never", "exaggerated",
                 f"Logo churn never exceeds 10% in a quarter; 2026-Q1 came in at {pct(v)}.", "2026-Q1",
                 DEF_CHURN("2026-01", "2026-03"), g, round(v, 4), 0.0005, CH, approx(round(v, 3), 0.0005),
                 {"kind": "unbounded", "marker": "never exceeds"}, export_note(*full_range("2026-Q1")),
                 "one quarter of data cannot support 'never'", f"Logo churn for 2026-Q1 was {pct(v)}."))

    g = Gen("le_dso_every_qend")
    for m in Q1:
        g.revenue(m, 5, 2000, 9000)
    rev = sum(r["amount"] for r in g.rows)
    g.add("2026-03-31", "accounts_receivable", "", rev * 38.4 / 90)
    v = compute(DSO, g, "2026-Q1"); assert v < 45
    out.append(L("le_dso_every_qend", "exaggerated", f"DSO stays below 45 days at every quarter end; it was {v:.1f} days for 2026-Q1.",
                 "2026-Q1", DEF_DSO("2026-03-31", 90), g, round(v, 1), 0.05, DSO, approx(round(v, 1), 0.05),
                 {"kind": "unbounded", "marker": "every quarter end"}, export_note(*full_range("2026-Q1")),
                 "one quarter end in the bundle", f"DSO for 2026-Q1 was {v:.1f} days."))

    g = Gen("le_net_positive_2026")
    g.revenue("2026-03", 6); g.refunds("2026-03", 2)
    v = compute(SUM_NET, g, "2026-03"); assert v > 0
    out.append(L("le_net_positive_2026", "exaggerated",
                 "Net revenue after refunds was positive in every month of 2026, March included.", "2026-03", DEF_NET, g,
                 v, 0.01, SUM_NET, {"op": "gt", "value": 0}, {"kind": "months", "months": ALL2026, "marker": "every month of 2026"},
                 export_note(*full_range("2026-03")), "only March rows are in the bundle",
                 f"Net revenue after refunds was positive in March 2026 ({money(v)})."))

    g = Gen("le_refunds_always")
    g.revenue("2026-02", 8, 1500, 5000); g.refunds("2026-02", 3, 100, 400)
    RR = {"metric": "refund_rate"}
    v = compute(RR, g, "2026-02"); assert v < 0.05
    out.append(L("le_refunds_always", "exaggerated",
                 f"Refunds are always below 5% of revenue; in February 2026 they were {pct(v)}.", "2026-02",
                 DEF_REFUND_RATE, g, round(v, 4), 0.0005, RR, approx(round(v, 3), 0.0005),
                 {"kind": "unbounded", "marker": "always"}, export_note(*full_range("2026-02")),
                 "one month of data cannot support 'always'", f"Refunds were {pct(v)} of revenue in February 2026."))

    g = Gen("le_opex_rest_of_year")
    for m in Q3:
        g.opex(m, 3); g.revenue(m, 2)
    v = compute(SUM_OPEX, g, "2026-Q3")
    Y = (int(v // 5000) + 2) * 5000
    out.append(L("le_opex_rest_of_year", "exaggerated",
                 f"Operating expenses were {money(v)} in 2026-Q3 and will remain below {money(Y)} per quarter for the rest of the year.",
                 "2026-Q3", DEF_OPEX, g, v, 0.01, SUM_OPEX, approx(v, 0.01), {"kind": "future", "marker": "will remain"},
                 export_note(*full_range("2026-Q3")), "Q3 actuals do not establish Q4 spending",
                 f"Operating expenses for 2026-Q3 totalled {money(v)}."))

    g = Gen("le_q2_guarantees")
    for m in Q2:
        g.revenue(m, 6, 2000, 8000)
    v = compute(SUM_REV, g, "2026-Q2")
    F = int(v * 3.6 // 10000) * 10000
    out.append(L("le_q2_guarantees", "exaggerated",
                 f"2026-Q2 revenue of {money(v)} guarantees that full-year 2026 revenue will exceed {money(F)}.",
                 "2026-Q2", DEF_REV, g, v, 0.01, SUM_REV, approx(v, 0.01), {"kind": "future", "marker": "guarantees"},
                 export_note(*full_range("2026-Q2")), "one quarter cannot guarantee a full-year total",
                 f"Revenue for 2026-Q2 was {money(v)}."))

    g = Gen("le_margin_h1_months")
    g.revenue("2026-03", 6); g.cogs("2026-03", 0.6)
    v = compute(MARGIN, g, "2026-03"); assert v > 0.36
    out.append(L("le_margin_h1_months", "exaggerated", "Gross margin was above 35% in every month of 2026-H1.", "2026-03",
                 DEF_MARGIN, g, round(v, 4), None, MARGIN, {"op": "gt", "value": 0.35},
                 {"kind": "months", "months": [f"2026-{i:02d}" for i in range(1, 7)], "marker": "every month of 2026-H1"},
                 export_note(*full_range("2026-03")), "only March rows are in the bundle",
                 f"Gross margin in March 2026 was above 35% ({pct(v)})."))

    g = Gen("le_ticket_since_2025")
    g.revenue("2026-01", 7, 900, 2600)
    v = compute(TICKET, g, "2026-01"); assert v > 1000
    out.append(L("le_ticket_since_2025", "exaggerated",
                 f"The average ticket has been above $1,000 in every month since January 2025, including {money(v)} in January 2026.",
                 "2026-01", DEF_TICKET, g, round(v, 2), 0.01, TICKET, approx(round(v, 2), 0.01),
                 {"kind": "months", "months": O.month_list("2025-01", "2026-01"), "marker": "every month since January 2025"},
                 export_note(*full_range("2026-01")), "only January 2026 rows are in the bundle",
                 f"The average ticket in January 2026 was {money(v)}."))

    g = Gen("le_growth_every_month")
    g.revenue("2026-02", 5, 1000, 3000); g.revenue("2026-03", 7, 1000, 3000)
    sp = {"metric": "growth", "from": "2026-02", "to": "2026-03"}
    v = compute(sp, g, "2026-02..2026-03"); assert v > 0.05
    out.append(L("le_growth_every_month", "exaggerated",
                 f"Monthly revenue grows by at least 5% every month, as the {pct(v)} increase from February to March 2026 shows.",
                 "2026-02..2026-03", DEF_GROWTH("2026-02", "2026-03"), g, round(v, 4), 0.0005, sp,
                 {"op": "gt", "value": 0.05}, {"kind": "unbounded", "marker": "every month"},
                 export_note(*full_range("2026-02..2026-03")), "one month-over-month change only",
                 f"Revenue grew {pct(v)} from February to March 2026."))

    # ------------------------------------------------ incomplete
    g = Gen("li_rev_q1_febonly")
    for m in Q1[:2]:
        g.revenue(m, 6); g.opex(m)
    v = compute(SUM_REV, g, "2026-Q1")
    out.append(L("li_rev_q1_febonly", "incomplete", f"Revenue for 2026-Q1 was {money(v)}.", "2026-Q1", DEF_REV, g, v,
                 0.01, SUM_REV, approx(v, 0.01), PERIOD, export_note("2026-01-01", "2026-02-28"),
                 "export and rows stop at 2026-02-28; March missing"))

    g = Gen("li_margin_q2_nojune")
    for m in Q2[:2]:
        g.revenue(m, 5); g.cogs(m, 0.57)
    v = compute(MARGIN, g, "2026-Q2")
    out.append(L("li_margin_q2_nojune", "incomplete", f"Gross margin for 2026-Q2 was {pct(v)}.", "2026-Q2", DEF_MARGIN, g,
                 round(v, 4), 0.0005, MARGIN, approx(round(v, 3), 0.0005), PERIOD,
                 export_note("2026-04-01", "2026-05-31"), "June is outside the export; no June rows"))

    g = Gen("li_margin_no_cogs")
    for m in Q1:
        g.revenue(m, 5); g.opex(m)
    out.append(L("li_margin_no_cogs", "incomplete", "Gross margin for 2026-Q1 was 41.2%.", "2026-Q1", DEF_MARGIN, g,
                 0.412, 0.0005, MARGIN, approx(0.412, 0.0005), PERIOD,
                 export_note(*full_range("2026-Q1"), "COGS is posted in the inventory sub-ledger, which is not part of this export."),
                 "definition needs cogs rows; none in the bundle"))

    g = Gen("li_dso_no_ar")
    for m in Q1:
        g.revenue(m, 5, 2000, 9000)
    out.append(L("li_dso_no_ar", "incomplete", "DSO for 2026-Q1 was 44.0 days.", "2026-Q1", DEF_DSO("2026-03-31", 90), g,
                 44.0, 0.05, DSO, approx(44.0, 0.05), PERIOD,
                 export_note(*full_range("2026-Q1"), "The AR aging report is exported separately."),
                 "no accounts_receivable row; DSO cannot be computed"))

    g = Gen("li_churn_partial_mar")
    cust = g.pool[:12]
    gone = set(g.r.sample(cust, 1))
    for i, m in enumerate(Q1):
        for c in cust:
            if i == 2 and c in gone:
                continue
            d = g.day(m, 1, 28)
            if i == 2 and int(d[-2:]) > 15:
                continue  # billed after the export cut-off
            g.add(d, "subscription", c, g.r.choice([49.0, 99.0]))
    v = compute(CH, g, "2026-Q1")
    out.append(L("li_churn_partial_mar", "incomplete", f"Logo churn for 2026-Q1 was {pct(v)}.", "2026-Q1",
                 DEF_CHURN("2026-01", "2026-03"), g, round(v, 4), 0.0005, CH, approx(round(v, 3), 0.0005), PERIOD,
                 export_note("2026-01-01", "2026-03-15"), "export stops at 2026-03-15; later March billings absent"))

    g = Gen("li_growth_partial")
    g.revenue("2026-02", 6, 1000, 4000); g.revenue("2026-03", 6, 1000, 4000, dhi=20)
    sp = {"metric": "growth", "from": "2026-02", "to": "2026-03"}
    v = compute(sp, g, "2026-02..2026-03")
    word = "grew" if v > 0 else "fell"
    out.append(L("li_growth_partial", "incomplete", f"Revenue {word} {pct(abs(v))} from February to March 2026.",
                 "2026-02..2026-03", DEF_GROWTH("2026-02", "2026-03"), g, round(v, 4), 0.0005, sp,
                 approx(round(v, 3), 0.0005), PERIOD, export_note("2026-02-01", "2026-03-20"),
                 "export ends 2026-03-20; March incomplete"))

    g = Gen("li_ticket_q3_noaug")
    g.revenue("2026-07", 5, 300, 2200); g.revenue("2026-09", 5, 300, 2200)
    v = compute(TICKET, g, "2026-Q3")
    out.append(L("li_ticket_q3_noaug", "incomplete", f"The average ticket for 2026-Q3 was {money(v)}.", "2026-Q3",
                 DEF_TICKET, g, round(v, 2), 0.01, TICKET, approx(round(v, 2), 0.01), PERIOD,
                 export_note([("2026-07-01", "2026-07-31"), ("2026-09-01", "2026-09-30")]),
                 "export ranges skip August; no August rows"))

    g = Gen("li_net_no_refunds")
    g.revenue("2026-05", 7); g.opex("2026-05")
    v = compute(SUM_REV, g, "2026-05")
    out.append(L("li_net_no_refunds", "incomplete", f"Net revenue for May 2026, after refunds, was {money(v)}.", "2026-05",
                 DEF_NET, g, v, 0.01, SUM_NET, approx(v, 0.01), PERIOD,
                 export_note(*full_range("2026-05"), "Refunds are processed in the payments platform and are not in this export."),
                 "definition needs refund rows; none in the bundle"))

    g = Gen("li_opex_q3_late_start")
    g.opex("2026-07", 2, dlo=15); g.opex("2026-08", 3); g.opex("2026-09", 3)
    v = compute(SUM_OPEX, g, "2026-Q3")
    out.append(L("li_opex_q3_late_start", "incomplete", f"Operating expenses for 2026-Q3 totalled {money(v)}.", "2026-Q3",
                 DEF_OPEX, g, v, 0.01, SUM_OPEX, approx(v, 0.01), PERIOD, export_note("2026-07-15", "2026-09-30"),
                 "export starts 2026-07-15; first half of July missing"))

    g = Gen("li_rev_h1_q1only")
    for m in Q1:
        g.revenue(m, 5); g.opex(m)
    v = compute(SUM_REV, g, "2026-H1")
    out.append(L("li_rev_h1_q1only", "incomplete", f"Revenue for 2026-H1 was {money(v)}.", "2026-H1", DEF_REV, g, v, 0.01,
                 SUM_REV, approx(v, 0.01), PERIOD, export_note("2026-01-01", "2026-03-31"),
                 "period is H1 but export and rows cover Q1 only"))

    g = Gen("li_margin_gt_nojune")
    for m in Q2[:2]:
        g.revenue(m, 5); g.cogs(m, 0.55)
    v = compute(MARGIN, g, "2026-Q2"); assert v > 0.38
    out.append(L("li_margin_gt_nojune", "incomplete", "Gross margin stayed above 38% for 2026-Q2.", "2026-Q2", DEF_MARGIN,
                 g, round(v, 4), None, MARGIN, {"op": "gt", "value": 0.38}, PERIOD,
                 export_note("2026-04-01", "2026-05-31"), "June missing from export and rows"))

    g = Gen("li_rev_may_partial")
    g.revenue("2026-05", 6, dhi=24)
    v = compute(SUM_REV, g, "2026-05")
    out.append(L("li_rev_may_partial", "incomplete", f"Revenue for May 2026 was {money(v)}.", "2026-05", DEF_REV, g, v,
                 0.01, SUM_REV, approx(v, 0.01), PERIOD, export_note("2026-05-01", "2026-05-24"),
                 "export ends 2026-05-24; last week of May missing"))
    return out


ACTION = {"valid": "state_as_written", "false": "withhold", "exaggerated": "narrow_or_withhold",
          "incomplete": "withhold"}


def main():
    cur_line = O.interp_version("python3")
    items = [build_python(s, cur_line) for s in PY] + ledger_cases()
    assert len(items) == 100, len(items)
    rnd = random.Random(SEED)
    rnd.shuffle(items)
    if os.path.isdir(CASES):
        for f in os.listdir(CASES):
            if f.endswith(".json"):
                os.remove(os.path.join(CASES, f))
    os.makedirs(CASES, exist_ok=True)
    labels, checks = {}, {}
    for i, it in enumerate(items, 1):
        cid = f"C{i:03d}"
        case = {"case_id": cid, "family": it["family"], "claim": it["claim"], "bundle": it["bundle"]}
        with open(os.path.join(CASES, cid + ".json"), "w") as f:
            json.dump(case, f, indent=2, ensure_ascii=False)
            f.write("\n")
        lab = {"category": it["cat"], "correct_action": ACTION[it["cat"]], "why": it["why"]}
        if it["cat"] in ("false", "exaggerated"):
            lab["supported_statement"] = it["supported"]
        labels[cid] = lab
        checks[cid] = it["check"]
    with open(os.path.join(HERE, "labels.json"), "w") as f:
        json.dump(labels, f, indent=2, ensure_ascii=False); f.write("\n")
    with open(os.path.join(HERE, "checks.json"), "w") as f:
        json.dump(checks, f, indent=2, ensure_ascii=False); f.write("\n")
    from collections import Counter
    print(Counter((it["family"], it["cat"]) for it in items))


if __name__ == "__main__":
    main()
