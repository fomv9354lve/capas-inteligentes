"""Collect execution metadata and JSONL structure without scoring decisions."""
from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    summary = {"generated_at": datetime.now().astimezone().isoformat(timespec="seconds"), "runs": {}}
    selection_path = HERE / "SCORING_SELECTION.json"
    selection = json.loads(selection_path.read_text()) if selection_path.exists() else {}
    summary["scoring_selection"] = selection
    call_ids = {"CB1": [], "CB2": []}
    call_errors = []
    calls_path = HERE / "arm_B" / "calls.jsonl"
    if calls_path.exists():
        for number, line in enumerate(calls_path.read_text().splitlines(), 1):
            try:
                obj = json.loads(line)
                if obj.get("agent") in call_ids:
                    call_ids[obj["agent"]].append(obj.get("case"))
            except json.JSONDecodeError:
                call_errors.append(number)
    summary["calls_json_invalid_lines"] = call_errors
    for arm in ("CA1", "CA2", "CB1", "CB2"):
        attempts = sorted((json.loads(p.read_text()) for p in HERE.glob(f"metadata_{arm}_attempt*.json")),
                          key=lambda x: x["attempt"])
        selected_number = selection.get("selected_attempts", {}).get(arm, attempts[-1]["attempt"])
        latest = next(a for a in attempts if a["attempt"] == selected_number)
        log = (HERE / latest["log"]).read_text()
        header = log.split("\nuser\n", 1)[0]
        record = {"attempts": attempts, "selected_attempt": selected_number,
                  "selected_attempt_metadata": latest,
                  "header": dict(re.findall(r"(?m)^([\w ]+): (.*)$", header))}
        tokens = re.findall(r"(?m)^tokens used\n([\d,]+)", log)
        record["cli_tokens_used"] = int(tokens[-1].replace(",", "")) if tokens else None
        record["shell_exec_calls"] = len(re.findall(r"(?m)^exec$", log))
        record["mcp_started"] = dict(Counter(re.findall(r"(?m)^mcp: (.+) started$", log)))
        record["shell_nonzero_statuses"] = re.findall(r"(?m)^.*exited [1-9][0-9]* in .*?$", log)
        record["mcp_failed_statuses"] = re.findall(r"(?m)^mcp: .*\(failed\).*?$", log)
        sid = record["header"].get("session id")
        trace_day = latest["start"][:10].split("-")
        paths = list((Path.home() / ".codex" / "sessions" / Path(*trace_day)).glob(f"*{sid}.jsonl"))
        record["session_trace"] = str(paths[0]) if paths else None
        counts, nested = Counter(), Counter()
        flagged, reads, patches, output_warnings, warning_details = [], [], [], [], []
        sources_by_call = {}
        usage = None
        if paths:
            for line in paths[0].read_text().splitlines():
                event = json.loads(line)
                payload = event.get("payload", {})
                if event.get("type") == "event_msg" and payload.get("type") == "token_count":
                    info = payload.get("info") or {}
                    usage = info.get("total_token_usage", usage)
                if event.get("type") == "response_item" and payload.get("type") == "custom_tool_call_output":
                    output = payload.get("output", "")
                    if isinstance(output, list):
                        output = "\n".join(item.get("text", "") for item in output if isinstance(item, dict))
                    warnings = re.findall(r"Warning: truncated output[^\n]*", str(output))
                    output_warnings.extend(warnings)
                    for warning in warnings:
                        warning_details.append({"warning": warning, "call_id": payload.get("call_id"),
                                                "tool_discovery": "ALL_TOOLS" in sources_by_call.get(payload.get("call_id"), "")})
                if event.get("type") != "response_item" or payload.get("type") not in ("function_call", "custom_tool_call"):
                    continue
                counts[payload.get("name")] += 1
                source = payload.get("input", payload.get("arguments", ""))
                sources_by_call[payload.get("call_id")] = source
                nested.update(re.findall(r"\btools\.([\w]+)\(", source))
                for match in re.finditer(r"(?:readFile(?:Sync)?|readdir|read_text|read_bytes)\s*\(", source):
                    reads.append(source[match.start():match.start()+220].split(");")[0].split("\\n")[0])
                patches.extend(re.findall(r"\*\*\* (?:Add|Update|Delete) File: ([^\n\\]+)", source))
                hits = re.findall(r"RESULTS\.md|result_sealed_scorer|CODEX_TASK\.md|oracle/|MEMORY\.md|git (?:show|log)", source)
                if hits:
                    flagged.append({"call_id": payload.get("call_id"), "matches": sorted(set(hits))})
        record.update(top_level_tool_calls=dict(counts), nested_tool_mentions=dict(nested),
                      cumulative_token_usage=usage, restricted_source_matches=flagged,
                      read_operation_arguments=reads, patch_targets=sorted(set(patches)),
                      tool_output_warnings=output_warnings, tool_output_warning_details=warning_details)
        path = HERE / ("arm_A" if arm[1] == "A" else "arm_B") / f"decisions_{arm}.jsonl"
        lines = path.read_text().splitlines() if path.exists() else []
        ids, invalid, invalid_details, id_position_errors = [], [], [], []
        first = 1 if arm.endswith("1") else 51
        expected = [f"C{i:03d}" for i in range(first, first+50)]
        for number, line in enumerate(lines, 1):
            try:
                obj = json.loads(line)
                if not isinstance(obj, dict):
                    raise ValueError("not an object")
                ids.append(obj.get("case_id"))
                if number > len(expected) or obj.get("case_id") != expected[number-1]:
                    id_position_errors.append(number)
            except (json.JSONDecodeError, ValueError) as error:
                invalid.append(number)
                invalid_details.append({"line": number, "message": str(error),
                                        "column": getattr(error, "colno", None)})
        record["validation"] = {"path": str(path.relative_to(HERE)), "lines": len(lines),
                                "invalid_json_lines": invalid, "case_ids_exact_order": ids == expected,
                                "invalid_json_details": invalid_details,
                                "valid_json_objects": len(ids),
                                "parsed_ids_match_line_positions": not id_position_errors,
                                "id_position_errors": id_position_errors,
                                "missing_parsed_ids": sorted(set(expected)-set(ids)),
                                "sha256": sha(path) if path.exists() else None}
        if arm in call_ids:
            counts_by_case = Counter(call_ids[arm])
            record["capas_calls"] = {"total": len(call_ids[arm]), "unique_cases": len(counts_by_case),
                                     "missing_expected_ids": sorted(set(expected)-set(counts_by_case)),
                                     "extra_ids": sorted(set(counts_by_case)-set(expected)),
                                     "repeated_ids": {k: v for k,v in counts_by_case.items() if v > 1}}
        summary["runs"][arm] = record
    before = json.loads((HERE / "preflight.json").read_text())
    summary["file_hashes"] = {name: {"before": digest, "after": sha(ROOT/name),
                                      "unchanged": digest == sha(ROOT/name)}
                              for name, digest in before["sha256"].items()}
    summary["all_complete"] = all(r["selected_attempt_metadata"]["exit_code"] == 0
                                  and r["validation"]["lines"] == 50
                                  and not r["validation"]["invalid_json_lines"]
                                  and r["validation"]["case_ids_exact_order"]
                                  for r in summary["runs"].values())
    summary["all_structurally_valid"] = summary["all_complete"]
    summary["all_runs_finished"] = all(r["selected_attempt_metadata"]["end"] is not None
                                       for r in summary["runs"].values())
    summary["scoring_packet_ready"] = all(
        r["selected_attempt_metadata"]["exit_code"] == 0
        and r["validation"]["lines"] == 50
        and r["validation"]["parsed_ids_match_line_positions"]
        and r["validation"]["invalid_json_lines"] == selection.get("declared_malformed_lines", {}).get(arm, [])
        for arm, r in summary["runs"].items())
    (HERE / "run_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({"all_structurally_valid": summary["all_structurally_valid"],
        "scoring_packet_ready": summary["scoring_packet_ready"], "runs": {
        k: {"cli_tokens_used": v["cli_tokens_used"], "top_level_tool_calls": v["top_level_tool_calls"],
            "validation": v["validation"], "restricted_source_matches": v["restricted_source_matches"]}
        for k, v in summary["runs"].items()}}, indent=2))


if __name__ == "__main__":
    main()
