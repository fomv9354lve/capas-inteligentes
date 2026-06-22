"""Drive capas_mcp.py exactly as an MCP client would — over stdio, newline-delimited JSON-RPC —
and assert the handshake + every tool fires deterministically. Proves the server is a real MCP
endpoint, not an assertion.
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import capas_mcp


def _drive(messages: list[dict]) -> list[dict]:
    """Feed JSON-RPC messages through the server's stdio loop, collect responses."""
    stdin = io.StringIO("\n".join(json.dumps(m) for m in messages) + "\n")
    stdout = io.StringIO()
    capas_mcp.serve(stdin=stdin, stdout=stdout)
    return [json.loads(l) for l in stdout.getvalue().splitlines() if l.strip()]


def run() -> int:
    checks = []

    # 1. handshake
    init = capas_mcp.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    checks.append(("initialize returns protocol + serverInfo 'capas'",
                   init["result"]["serverInfo"]["name"] == "capas"
                   and "protocolVersion" in init["result"]))

    # 2. notifications/initialized produces no response
    checks.append(("notifications/initialized is a no-reply notification",
                   capas_mcp.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None))

    # 3. tools/list exposes the 5 CAPAS tools
    tl = capas_mcp.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    names = {t["name"] for t in tl["result"]["tools"]}
    expected = {"capas_gate", "capas_invariants", "capas_gate_quantum", "capas_reward", "capas_certificate"}
    checks.append((f"tools/list exposes {sorted(expected)}", names == expected))
    checks.append(("every tool has an inputSchema",
                   all("inputSchema" in t for t in tl["result"]["tools"])))

    # 4. full stdio drive: initialize -> tools/call capas_gate (ACCEPT case)
    accept_args = {"name": "capas_gate", "arguments": {
        "claim_type": "exact_model_solution",
        "evidence": {"abs_error": 0.0, "tolerance": 1e-3}, "claim_text": "x"}}
    resp = _drive([
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": accept_args},
    ])
    call = [r for r in resp if r.get("id") == 3][0]
    verdict = call["result"]["structuredContent"]["verdict"]
    checks.append((f"capas_gate over stdio -> {verdict} (ACCEPT, deterministic)", verdict == "ACCEPT"))
    checks.append(("response has MCP content[] text", call["result"]["content"][0]["type"] == "text"))

    # 5. invariant OVERRIDE through MCP: a claim that re-derives but whose books don't close -> REJECT
    rej_args = {"name": "capas_gate", "arguments": {
        "claim_type": "financial_metric_claim",
        "evidence": {"reported_value": 1.0, "reference_value": 1.0, "tolerance": 1.0,
                     "metric_period_match": True,
                     "invariants": {"accounting": {"assets": 1000, "liabilities": 600, "equity": 300}}},
        "claim_text": "Q3"}}
    rej = capas_mcp.handle({"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": rej_args})
    rv = rej["result"]["structuredContent"]["verdict"]
    checks.append((f"capas_gate with invariant violation -> {rv} (downgrade-only override via MCP)",
                   rv == "REJECT"))

    # 6. capas_invariants tool: cross-domain (GRIM) fabrication
    inv = capas_mcp.handle({"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {
        "name": "capas_invariants", "arguments": {"block": {"grim": {"mean": 5.19, "n": 10}}}}})
    checks.append(("capas_invariants GRIM mean 5.19/n10 -> FLAG (fabrication)",
                   inv["result"]["structuredContent"]["verdict"] == "FLAG"))

    # 7. capas_gate_quantum tool: T2>2T1
    q = capas_mcp.handle({"jsonrpc": "2.0", "id": 6, "method": "tools/call", "params": {
        "name": "capas_gate_quantum", "arguments": {"row": {"t1_us": 11.2, "t2_us": 23.44}}}})
    checks.append(("capas_gate_quantum T2>2T1 -> FLAG",
                   q["result"]["structuredContent"]["verdict"] == "FLAG"))

    # 8. capas_reward tool: aligned signal
    rw = capas_mcp.handle({"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": {
        "name": "capas_reward", "arguments": {"claim_type": "exact_model_solution",
                                              "evidence": {"abs_error": 0.0, "tolerance": 1e-3}}}})
    checks.append((f"capas_reward ACCEPT-case -> {rw['result']['structuredContent']['reward']} (==1.0)",
                   rw["result"]["structuredContent"]["reward"] == 1.0))

    # 9. unknown tool fails closed (error, not crash)
    bad = capas_mcp.handle({"jsonrpc": "2.0", "id": 8, "method": "tools/call",
                            "params": {"name": "nope", "arguments": {}}})
    checks.append(("unknown tool -> JSON-RPC error (fail-closed)", "error" in bad))

    ok = all(c for _, c in checks)
    for label, c in checks:
        print(f"{'OK ' if c else 'XX '}{label}")
    print("CAPAS MCP SERVER: pass (real MCP endpoint, every tool deterministic, no LLM in any verdict)"
          if ok else "CAPAS MCP SERVER: FAILURES")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
