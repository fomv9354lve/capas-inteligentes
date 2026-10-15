"""Print process and structural progress only, never decision contents or scores."""
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent


def main():
    selection_path = HERE / "SCORING_SELECTION.json"
    selection = json.loads(selection_path.read_text()) if selection_path.exists() else {}
    calls = {"CB1": [], "CB2": []}
    calls_path = HERE / "arm_B" / "calls.jsonl"
    if calls_path.exists():
        for line in calls_path.read_text().splitlines():
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("agent") in calls:
                calls[obj["agent"]].append(obj.get("case"))
    for arm in ("CA1", "CA2", "CB1", "CB2"):
        paths = sorted(HERE.glob(f"metadata_{arm}_attempt*.json"))
        if not paths:
            print(json.dumps({"arm": arm, "status": "not started"}))
            continue
        attempts = [json.loads(p.read_text()) for p in paths]
        selected = selection.get("selected_attempts", {}).get(arm)
        m = (next(a for a in attempts if a["attempt"] == selected) if selected is not None
             else max(attempts, key=lambda x: x["attempt"]))
        log = (HERE / m["log"]).read_text()
        directory = HERE / ("arm_A" if arm[1] == "A" else "arm_B")
        path = directory / f"decisions_{arm}.jsonl"
        lines = path.read_text().splitlines() if path.exists() else []
        ids, invalid_lines = [], []
        for n, line in enumerate(lines, 1):
            try:
                obj = json.loads(line)
                if not isinstance(obj, dict):
                    raise ValueError("not an object")
                ids.append(obj.get("case_id"))
            except (json.JSONDecodeError, ValueError):
                invalid_lines.append(n)
        first = 1 if arm.endswith("1") else 51
        expected = [f"C{i:03d}" for i in range(first, first+50)]
        tokens = re.findall(r"(?m)^tokens used\n([\d,]+)", log)
        status = {"arm": arm, "attempt": m["attempt"], "exit_code": m["exit_code"],
                  "wall_seconds": m["wall_seconds"], "log_bytes": len(log.encode()),
                  "lines": len(lines), "invalid_json_lines": invalid_lines,
                  "case_ids_exact_order": ids == expected,
                  "exec_calls_visible": len(re.findall(r"(?m)^exec$", log)),
                  "tokens_reported": tokens[-1] if tokens else None}
        if arm.startswith("CB"):
            status.update(capas_calls=len(calls[arm]), capas_unique_cases=len(set(calls[arm])))
        print(json.dumps(status))


if __name__ == "__main__":
    main()
