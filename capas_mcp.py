"""CAPAS MCP server — the deterministic claim-admissibility gate as a tool for ANY LLM agent.

The LLM PROPOSES evidence; CAPAS DISPOSES the verdict (fail-closed, no LLM in the decision).
Wire it into Claude Code / Claude Desktop / Cursor / any MCP client:

    {
      "mcpServers": {
        "capas": { "command": "python3", "args": ["/abs/path/to/capas_mcp.py"] }
      }
    }

Dependency-free: speaks MCP over stdio as newline-delimited JSON-RPC 2.0, using only the stdlib
(matching the rest of the engine). Tools: capas_gate, capas_invariants, capas_gate_quantum,
capas_reward, capas_certificate. Every tool is a thin wrapper over capas_sdk — the verdict is
always the deterministic engine's, never a language model's.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import capas_sdk

PROTOCOL_VERSION = "2024-11-05"
SERVER_INFO = {"name": "capas", "version": "0.1.0"}

# --- tool registry: name -> (handler, inputSchema, description) ---------------------------------

_EVIDENCE = {"type": "object", "description": "declared evidence fields for the claim type",
             "additionalProperties": True}


def _gate(a):
    return capas_sdk.gate(a["claim_type"], a.get("evidence", {}), a.get("claim_text", ""),
                          a.get("claim_id", "claim"))


def _invariants(a):
    return capas_sdk.invariants(a.get("block", {}))


def _gate_quantum(a):
    return capas_sdk.gate_quantum(a.get("row", {}))


def _reward(a):
    return {"reward": capas_sdk.reward(a["claim_type"], a.get("evidence", {}),
                                       a.get("claim_text", ""), a.get("claim_id", "claim"))}


def _certificate(a):
    return capas_sdk.certificate(a["claim_type"], a.get("evidence", {}),
                                 a.get("claim_text", ""), a.get("claim_id", "claim"))


TOOLS = {
    "capas_gate": {
        "handler": _gate,
        "description": ("Deterministically gate a structured claim: ACCEPT / REWRITE / REJECT / HOLD. "
                        "The LLM proposes the evidence; CAPAS decides fail-closed (no LLM in the verdict). "
                        "Unsupported/missing evidence HOLDs; it never false-ACCEPTs."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "claim_type": {"type": "string", "description": "registered claim type, e.g. financial_metric_claim"},
                "evidence": _EVIDENCE,
                "claim_text": {"type": "string"},
                "claim_id": {"type": "string"},
            },
            "required": ["claim_type", "evidence"],
        },
    },
    "capas_invariants": {
        "handler": _invariants,
        "description": ("Check declared quantities against domain LAWS (cross-domain, deterministic, no "
                        "oracle): accounting{assets,liabilities,equity}, quantum{t1_us,t2_us,...}, "
                        "grim{mean,n}, probabilities[]/distribution{}, parts[]+total. PASS only if every "
                        "applicable law holds (fail-closed). Catches finance/psychology/quantum fabrication."),
        "inputSchema": {
            "type": "object",
            "properties": {"block": {"type": "object", "additionalProperties": True,
                                     "description": "one or more invariant blocks"}},
            "required": ["block"],
        },
    },
    "capas_gate_quantum": {
        "handler": _gate_quantum,
        "description": ("Gate a reported quantum calibration/result row against textbook physical "
                        "invariants, no device: T2<=2T1, P01>=P10, CZ~RZZ, Gamma_phi>=0, gate-error "
                        "coherence floor, residual ZZ. The GRIM/statcheck analog for quantum claims."),
        "inputSchema": {
            "type": "object",
            "properties": {"row": {"type": "object", "additionalProperties": True,
                                   "description": "t1_us,t2_us,t2_method,p01,p10,cz_error,rzz_error,"
                                                  "gate_error,gate_time_ns,zz_residual_hz"}},
            "required": ["row"],
        },
    },
    "capas_reward": {
        "handler": _reward,
        "description": ("Dense verifiable reward in [0,1] ALIGNED with the gate (the RLVR signal a model "
                        "cannot game by being plausible): ACCEPT->1.0, REWRITE->0.5, HOLD->0.25, REJECT->0.0."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "claim_type": {"type": "string"}, "evidence": _EVIDENCE,
                "claim_text": {"type": "string"}, "claim_id": {"type": "string"},
            },
            "required": ["claim_type", "evidence"],
        },
    },
    "capas_certificate": {
        "handler": _certificate,
        "description": ("A re-derivable admissibility certificate: stratifies the claim into grounded / "
                        "generated / unknowable and names the boundary it cannot enter (the audit artifact)."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "claim_type": {"type": "string"}, "evidence": _EVIDENCE,
                "claim_text": {"type": "string"}, "claim_id": {"type": "string"},
            },
            "required": ["claim_type", "evidence"],
        },
    },
}


def _tools_list():
    return [{"name": n, "description": t["description"], "inputSchema": t["inputSchema"]}
            for n, t in TOOLS.items()]


def handle(msg: dict) -> dict | None:
    """Dispatch one JSON-RPC request. Returns a response dict, or None for notifications."""
    method = msg.get("method")
    mid = msg.get("id")

    if method == "initialize":
        return {"jsonrpc": "2.0", "id": mid, "result": {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": SERVER_INFO,
            "instructions": "CAPAS gates claims fail-closed. The LLM proposes evidence; CAPAS disposes "
                            "the verdict. No language model is ever in the decision.",
        }}
    if method in ("notifications/initialized", "initialized"):
        return None
    if method == "ping":
        return {"jsonrpc": "2.0", "id": mid, "result": {}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": mid, "result": {"tools": _tools_list()}}
    if method == "tools/call":
        params = msg.get("params") or {}
        name = params.get("name")
        args = params.get("arguments") or {}
        tool = TOOLS.get(name)
        if tool is None:
            return {"jsonrpc": "2.0", "id": mid,
                    "error": {"code": -32602, "message": f"unknown tool {name!r}"}}
        try:
            result = tool["handler"](args)
            text = json.dumps(result, indent=2, default=str)
            return {"jsonrpc": "2.0", "id": mid,
                    "result": {"content": [{"type": "text", "text": text}],
                               "structuredContent": result, "isError": False}}
        except Exception as exc:  # tool error -> fail-closed, surfaced as isError (not a crash)
            return {"jsonrpc": "2.0", "id": mid,
                    "result": {"content": [{"type": "text",
                                            "text": f"CAPAS tool error (fail-closed): {exc}"}],
                               "isError": True}}
    if mid is not None:
        return {"jsonrpc": "2.0", "id": mid,
                "error": {"code": -32601, "message": f"method not found: {method}"}}
    return None


def serve(stdin=None, stdout=None) -> None:
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = handle(msg)
        if resp is not None:
            stdout.write(json.dumps(resp) + "\n")
            stdout.flush()


if __name__ == "__main__":
    serve()
